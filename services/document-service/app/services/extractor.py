from pathlib import Path
from typing import Any

import fitz

from app.services.storage import document_images_dir


def extract_tables_from_page(page: fitz.Page) -> list[dict[str, Any]]:
    if not hasattr(page, "find_tables"):
        return []

    tables: list[dict[str, Any]] = []
    try:
        table_finder = page.find_tables()
        for table_index, table in enumerate(table_finder.tables):
            tables.append(
                {
                    "table_index": table_index,
                    "bbox": list(table.bbox),
                    "rows": table.extract(),
                }
            )
    except Exception:
        return []

    return tables


def extract_pdf_elements(pdf_path: Path, document_id: str) -> dict[str, Any]:
    image_dir = document_images_dir(document_id)
    image_dir.mkdir(parents=True, exist_ok=True)

    pages: list[dict[str, Any]] = []
    images: list[dict[str, Any]] = []
    tables: list[dict[str, Any]] = []

    with fitz.open(pdf_path) as pdf:
        raw_metadata = dict(pdf.metadata or {})
        metadata = {
            "title": raw_metadata.get("title") or None,
            "author": raw_metadata.get("author") or None,
            "subject": raw_metadata.get("subject") or None,
            "creator": raw_metadata.get("creator") or None,
            "producer": raw_metadata.get("producer") or None,
            "language": None,
            "page_count": pdf.page_count,
            "raw_metadata": raw_metadata,
        }

        for page_index, page in enumerate(pdf, start=1):
            text_content = page.get_text("text") or ""
            pages.append({"page_number": page_index, "text_content": text_content})

            page_tables = extract_tables_from_page(page)
            if page_tables:
                tables.append({"page_number": page_index, "tables": page_tables})

            for image_index, image_info in enumerate(page.get_images(full=True), start=1):
                xref = image_info[0]
                extracted_image = pdf.extract_image(xref)
                extension = extracted_image.get("ext", "png")
                image_bytes = extracted_image["image"]
                image_path = image_dir / f"page-{page_index}-image-{image_index}.{extension}"
                image_path.write_bytes(image_bytes)

                images.append(
                    {
                        "page_number": page_index,
                        "image_index": image_index,
                        "file_path": str(image_path),
                        "extension": extension,
                        "width": int(extracted_image.get("width") or 0),
                        "height": int(extracted_image.get("height") or 0),
                    }
                )

    return {
        "metadata": metadata,
        "pages": pages,
        "images": images,
        "tables": tables,
        "ocr": {"required": False, "status": "not_used"},
    }
