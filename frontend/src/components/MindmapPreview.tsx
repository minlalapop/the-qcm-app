import { Download } from "lucide-react";
import { useRef, useState } from "react";

import type { MindMap } from "../api/types";
import { downloadElementAsPng, downloadTextFile, safeDownloadName } from "../utils/capture";
import { classNames } from "../utils/format";

export function MindmapPreview({ mindmap, showExportActions = true }: { mindmap: MindMap; showExportActions?: boolean }) {
  const [view, setView] = useState<"diagram" | "code">("diagram");
  const diagramRef = useRef<HTMLDivElement | null>(null);
  const code = mindmap.mermaid_content || mindmapJsonToMermaid(mindmap);
  const tree = parseMermaidMindmap(code, mindmap.title);

  async function exportPng() {
    setView("diagram");
    await new Promise((resolve) => window.requestAnimationFrame(resolve));
    if (!diagramRef.current) return;
    await downloadElementAsPng(diagramRef.current, safeDownloadName(mindmap.title, "png"));
  }

  function exportMermaid() {
    downloadTextFile(code, safeDownloadName(mindmap.title, "mmd"), "text/vnd.mermaid;charset=utf-8");
  }

  return (
    <div className="mt-5">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
        <div className="flex flex-wrap gap-2">
          <button
            className={classNames(
              "rounded-full px-4 py-2 text-sm font-extrabold transition",
              view === "diagram" ? "bg-primary text-white" : "bg-white/70 text-on-surface-variant hover:text-primary",
            )}
            onClick={() => setView("diagram")}
          >
            Diagram
          </button>
          <button
            className={classNames(
              "rounded-full px-4 py-2 text-sm font-extrabold transition",
              view === "code" ? "bg-primary text-white" : "bg-white/70 text-on-surface-variant hover:text-primary",
            )}
            onClick={() => setView("code")}
          >
            Mermaid code
          </button>
        </div>
        {showExportActions && (
          <div className="flex flex-wrap gap-2">
            <button
              className="inline-flex items-center gap-2 rounded-full bg-white/70 px-4 py-2 text-sm font-extrabold text-primary transition hover:bg-white"
              onClick={() => void exportPng()}
            >
              <Download size={16} />
              PNG
            </button>
            <button
              className="rounded-full bg-white/70 px-4 py-2 text-sm font-extrabold text-on-surface-variant transition hover:bg-white hover:text-primary"
              onClick={exportMermaid}
            >
              Mermaid
            </button>
          </div>
        )}
      </div>

      {view === "diagram" ? (
        <div className="max-h-[620px] overflow-auto rounded-2xl bg-white/75 p-5">
          <div ref={diagramRef} className="w-max rounded-2xl bg-white/75 p-5">
            <MindmapCanvas tree={tree} />
          </div>
        </div>
      ) : (
        <pre className="max-h-[520px] max-w-full overflow-auto rounded-2xl bg-on-surface p-5 text-sm leading-6 text-white">
          {code}
        </pre>
      )}
    </div>
  );
}

type MindmapTreeNode = {
  label: string;
  children: MindmapTreeNode[];
};

function MindmapCanvas({ tree }: { tree: MindmapTreeNode }) {
  const children = tree.children;
  const midpoint = Math.ceil(children.length / 2);
  const leftNodes = children.slice(0, midpoint).reverse();
  const rightNodes = children.slice(midpoint);

  return (
    <div className="mx-auto w-max min-w-[980px] py-8">
      <div className="grid min-h-[420px] grid-cols-[minmax(340px,1fr)_240px_minmax(340px,1fr)] items-center gap-8">
        <BranchColumn nodes={leftNodes} side="left" />
        <div className="relative flex min-h-[220px] items-center justify-center">
          <span className="absolute left-[-2rem] right-[-2rem] top-1/2 h-px bg-primary/25" />
          <div className="relative z-10 max-w-[240px] rounded-[1.5rem] border border-primary bg-primary px-6 py-5 text-center font-display text-lg font-extrabold text-white shadow-soft">
            {tree.label}
          </div>
        </div>
        <BranchColumn nodes={rightNodes} side="right" />
      </div>
    </div>
  );
}

function BranchColumn({ nodes, side }: { nodes: MindmapTreeNode[]; side: "left" | "right" }) {
  return (
    <div className="flex flex-col justify-center gap-7">
      {nodes.map((node, index) => (
        <div key={`${node.label}-${index}`} className={classNames("relative flex items-center", side === "left" ? "justify-end" : "justify-start")}>
          <span
            className={classNames(
              "absolute top-1/2 h-px w-12 bg-primary/35",
              side === "left" ? "right-[-3rem]" : "left-[-3rem]",
            )}
          />
          <MindmapBranch node={node} side={side} />
        </div>
      ))}
    </div>
  );
}

function MindmapBranch({ node, side }: { node: MindmapTreeNode; side: "left" | "right" }) {
  return (
    <div className={classNames("flex max-w-[360px] flex-col", side === "left" ? "items-end text-right" : "items-start text-left")}>
      <div className="rounded-2xl border border-primary/25 bg-surface-container px-4 py-3 text-sm font-extrabold text-on-surface shadow-soft">
        {node.label}
      </div>
      {node.children.length > 0 && (
        <div className={classNames("mt-3 flex flex-col gap-2 border-primary/20", side === "left" ? "items-end border-r pr-4" : "items-start border-l pl-4")}>
          {node.children.map((child, index) => (
            <div
              key={`${child.label}-${index}`}
              className="max-w-[300px] rounded-xl bg-white/75 px-3 py-2 text-xs font-bold text-on-surface-variant shadow-[0_1px_0_rgba(29,163,125,0.12)]"
            >
              {child.label}
              {child.children.length > 0 && (
                <div className={classNames("mt-2 space-y-1", side === "left" ? "text-right" : "text-left")}>
                  {child.children.slice(0, 4).map((grandChild, childIndex) => (
                    <p key={`${grandChild.label}-${childIndex}`} className="text-[11px] font-semibold opacity-80">
                      {grandChild.label}
                    </p>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function parseMermaidMindmap(code: string, fallbackTitle: string): MindmapTreeNode {
  const root: MindmapTreeNode = { label: fallbackTitle || "Mindmap", children: [] };
  const stack: Array<{ indent: number; node: MindmapTreeNode }> = [{ indent: -1, node: root }];

  for (const rawLine of code.split("\n")) {
    if (!rawLine.trim() || rawLine.trim().toLowerCase() === "mindmap") continue;
    const indent = rawLine.match(/^\s*/)?.[0].length ?? 0;
    const label = cleanMermaidLabel(rawLine.trim());
    if (!label) continue;

    while (stack.length > 1 && indent <= stack[stack.length - 1].indent) {
      stack.pop();
    }

    const node = { label, children: [] };
    stack[stack.length - 1].node.children.push(node);
    stack.push({ indent, node });
  }

  if (root.children.length === 1 && root.children[0].children.length > 0) {
    return root.children[0];
  }
  return root.children.length ? root : { label: fallbackTitle || "Mindmap", children: [] };
}

function cleanMermaidLabel(value: string): string {
  return value
    .replace(/^root\s*/i, "")
    .replace(/^\(+|\)+$/g, "")
    .replace(/^\[+|\]+$/g, "")
    .replace(/^"+|"+$/g, "")
    .trim();
}

function mindmapJsonToMermaid(mindmap: MindMap): string {
  const payload = mindmap.json_content || {};
  const rootLabel = typeof payload.root === "string" ? payload.root : mindmap.title;
  const nodes = Array.isArray(payload.nodes) ? payload.nodes : [];
  const lines = ["mindmap", `  root((${rootLabel}))`];
  for (const node of nodes) {
    if (node && typeof node === "object" && "label" in node) {
      lines.push(`    ${String((node as { label: unknown }).label)}`);
    }
  }
  return lines.join("\n");
}
