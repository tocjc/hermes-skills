#!/usr/bin/env python3
"""
Generate a knowledge-graph SVG/PNG from Obsidian vault wikilinks.

Usage:
    python3 scripts/gen-knowledge-graph.py [--vault /path/to/vault]

Requirements: pip install graphviz, apt-get install graphviz (system).

Output: <vault>/assets/knowledge-graph.svg (and .png if rsvg-convert available)

Colour convention in the generated graph:
  - Blue tones: foundation/inputs (theory, acquisition)
  - Red tones: analysis/diagnostics (time-domain, fault diagnosis)
  - Green: feature engineering / ML
  - Purple: tools, references, tutorials
  - Gray: meta / landing pages
"""
import re
import os
import sys
import subprocess
from pathlib import Path

try:
    from graphviz import Digraph
except ImportError:
    print("ERROR: pip install graphviz")
    sys.exit(1)


VAULT = os.environ.get("OBSIDIAN_VAULT_PATH", os.path.expanduser("~/notes/obsidian-vault"))

# Override via CLI arg
if len(sys.argv) > 2 and sys.argv[1] == "--vault":
    VAULT = sys.argv[2]

OUTPUT = os.path.join(VAULT, "assets", "knowledge-graph")

# Extend this map for new notes — colours by note name
COLOR_MAP = {
    "README": "#2b6cb0",
    "基础理论": "#3182ce",
    "信号采集": "#2b6cb0",
    "时域分析": "#e53e3e",
    "频域分析": "#dd6b20",
    "时频分析": "#d69e2e",
    "特征工程": "#38a169",
    "故障诊断": "#e53e3e",
    "常用工具": "#805ad5",
    "案例研究": "#319795",
    "欢迎 👋": "#a0aec0",
}


def extract_wikilinks(content: str) -> set:
    """Extract [[NoteName]] targets, stripping section anchors and display text."""
    links = set()
    for m in re.finditer(r"(?<!`)\[\[([^\]]+)\]\](?!`)", content):
        target = m.group(1).split("#")[0].split("|")[0].strip()
        if "/" not in target and not target.startswith("http"):
            links.add(target)
    return links


def main():
    vault = Path(VAULT)
    if not vault.is_dir():
        print(f"ERROR: vault not found at {vault}")
        sys.exit(1)

    md_files = {}
    for fpath in sorted(vault.rglob("*.md")):
        md_files[fpath.stem] = fpath.read_text(encoding="utf-8")

    dot = Digraph("ObsidianKnowledgeGraph", format="svg", engine="neato")
    dot.attr(
        overlap="false",
        splines="curved",
        bgcolor="#1a1a2e",
        fontcolor="white",
        fontname="Arial",
        size="40,35",
        dpi="150",
        K="1.5",
        start="5",
    )

    for name in md_files:
        color = COLOR_MAP.get(name, "#718096")
        dot.node(name, label=name, shape="box", style="filled,rounded",
                 fillcolor=color, fontcolor="white", fontsize="13",
                 penwidth="0", margin="0.18,0.08")

    edges = 0
    for source, content in md_files.items():
        for target in extract_wikilinks(content):
            if target in md_files:
                dot.edge(source, target,
                         color=COLOR_MAP.get(target, "#4a5568"),
                         penwidth="0.6", arrowsize="0.4")
                edges += 1

    out_dir = vault / "assets"
    out_dir.mkdir(parents=True, exist_ok=True)
    svg_path = dot.render(filename=str(out_dir / "knowledge-graph"), cleanup=True)

    # Try to render PNG as well (rsvg-convert from librsvg2-bin)
    png_path = svg_path.replace(".svg", ".png")
    try:
        subprocess.run(
            ["rsvg-convert", svg_path, "-o", png_path],
            check=True, capture_output=True, timeout=15,
        )
        print(f"PNG also written: {png_path}")
    except Exception:
        pass  # PNG is nice-to-have

    print(f"✅ Graph: {svg_path}  ({len(md_files)} nodes, {edges} edges)")
    print(f"   Embed in any note via: ![[assets/knowledge-graph.svg]]")


if __name__ == "__main__":
    main()