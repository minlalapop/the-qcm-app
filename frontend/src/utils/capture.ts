export async function downloadElementAsPng(element: HTMLElement, filename: string): Promise<void> {
  const clone = element.cloneNode(true) as HTMLElement;
  inlineComputedStyles(element, clone);

  const width = Math.ceil(Math.max(element.scrollWidth, element.getBoundingClientRect().width));
  const height = Math.ceil(Math.max(element.scrollHeight, element.getBoundingClientRect().height));

  clone.setAttribute("xmlns", "http://www.w3.org/1999/xhtml");
  clone.style.width = `${width}px`;
  clone.style.height = `${height}px`;
  clone.style.overflow = "visible";

  const serialized = new XMLSerializer().serializeToString(clone);
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">
      <foreignObject width="100%" height="100%">
        ${serialized}
      </foreignObject>
    </svg>
  `;

  const image = new Image();
  const svgBlob = new Blob([svg], { type: "image/svg+xml;charset=utf-8" });
  const url = URL.createObjectURL(svgBlob);

  await new Promise<void>((resolve, reject) => {
    image.onload = () => resolve();
    image.onerror = () => reject(new Error("Could not capture diagram"));
    image.src = url;
  });

  const canvas = document.createElement("canvas");
  canvas.width = width * 2;
  canvas.height = height * 2;
  const context = canvas.getContext("2d");
  if (!context) {
    URL.revokeObjectURL(url);
    throw new Error("Canvas is not available");
  }
  context.scale(2, 2);
  context.drawImage(image, 0, 0, width, height);
  URL.revokeObjectURL(url);

  const pngBlob = await new Promise<Blob>((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (blob) resolve(blob);
      else reject(new Error("Could not export PNG"));
    }, "image/png");
  });

  downloadBlob(pngBlob, filename);
}

export function downloadTextFile(content: string, filename: string, mimeType = "text/plain;charset=utf-8"): void {
  downloadBlob(new Blob([content], { type: mimeType }), filename);
}

export function safeDownloadName(value: string, extension: string): string {
  const cleaned = value
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9-_]+/gi, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 80);
  return `${cleaned || "evasym-export"}.${extension}`;
}

function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.append(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

function inlineComputedStyles(source: Element, target: Element): void {
  if (source instanceof HTMLElement && target instanceof HTMLElement) {
    const computed = window.getComputedStyle(source);
    for (const property of computed) {
      target.style.setProperty(property, computed.getPropertyValue(property), computed.getPropertyPriority(property));
    }
    target.style.transformOrigin = computed.transformOrigin;
  }

  const sourceChildren = Array.from(source.children);
  const targetChildren = Array.from(target.children);
  for (let index = 0; index < sourceChildren.length; index += 1) {
    if (targetChildren[index]) {
      inlineComputedStyles(sourceChildren[index], targetChildren[index]);
    }
  }
}
