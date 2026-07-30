#!/usr/bin/env python3
"""Extract the spoiler-free worksheet portion of a campaign problem .md file
(everything before the Hint/Answer key/Verification sections) and convert it
to a standalone LaTeX (.tex) file via pandoc -- source, not compiled. Use
compile_worksheets.py to turn .tex files into PDFs.

Also expands "printable-grid" markers into pre-scaled, gridlined blank axes
(via matplotlib) so a reader can plot hand-computed points directly on the
printout and read answers off it with a ruler/straightedge, instead of
needing separate graph paper. The generated PNGs are saved persistently
next to the .tex file (named <tex-stem>-grid_N.png) since the .tex
references them by relative path and both are meant to be committed to git.

Marker syntax (put this as an HTML comment in the source .md, right where
the graph should appear -- invisible in normal markdown rendering):

  <!-- printable-grid: title="Fig 1" xlabel="gamma (deg)" xmin=30 xmax=55
       xmajor=5 xminor=1 ylabel="R (nm)" ymin=195 ymax=220 ymajor=5 yminor=1 -->

Usage: python3 make_worksheet_tex.py <problem.md> [output.tex]
"""
import re
import subprocess
import sys
from pathlib import Path

CUT_MARKERS = ["\n## Hint", "\n## Answer key", "\n## Verification step"]
TOOLS_DIR = Path(__file__).parent
PREAMBLE = TOOLS_DIR / "worksheet_preamble.tex"

GRID_RE = re.compile(r'<!--\s*printable-grid:\s*(.*?)-->', re.DOTALL)
ATTR_RE = re.compile(r'(\w+)=(".*?"|\S+)')


def parse_attrs(attr_str):
    attrs = {}
    for m in ATTR_RE.finditer(attr_str):
        key, val = m.group(1), m.group(2)
        if val.startswith('"'):
            val = val.strip('"')
        attrs[key] = val
    return attrs


def make_grid_image(attrs, out_png):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker

    xmin, xmax = float(attrs["xmin"]), float(attrs["xmax"])
    ymin, ymax = float(attrs["ymin"]), float(attrs["ymax"])
    xmajor = float(attrs.get("xmajor", (xmax - xmin) / 5))
    xminor = float(attrs.get("xminor", xmajor / 5))
    ymajor = float(attrs.get("ymajor", (ymax - ymin) / 5))
    yminor = float(attrs.get("yminor", ymajor / 5))

    fig, ax = plt.subplots(figsize=(7.5, 5.0), dpi=200)
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.xaxis.set_major_locator(mticker.MultipleLocator(xmajor))
    ax.xaxis.set_minor_locator(mticker.MultipleLocator(xminor))
    ax.yaxis.set_major_locator(mticker.MultipleLocator(ymajor))
    ax.yaxis.set_minor_locator(mticker.MultipleLocator(yminor))
    ax.grid(which="major", linewidth=0.8, color="0.4")
    ax.grid(which="minor", linewidth=0.3, color="0.75")
    ax.set_xlabel(attrs.get("xlabel", ""))
    ax.set_ylabel(attrs.get("ylabel", ""))
    if attrs.get("title"):
        ax.set_title(attrs["title"])
    for spine in ax.spines.values():
        spine.set_linewidth(1.0)
    fig.tight_layout()
    fig.savefig(out_png)
    plt.close(fig)


def expand_grids(worksheet_md: str, image_dir: Path, stem: str):
    count = 0

    def repl(m):
        nonlocal count
        count += 1
        attrs = parse_attrs(m.group(1))
        png_name = f"{stem}-grid_{count}.png"
        make_grid_image(attrs, image_dir / png_name)
        caption = attrs.get("title", "")
        return f"\n![{caption}]({png_name})\n"

    return GRID_RE.sub(repl, worksheet_md)


def extract_worksheet(md_text: str) -> str:
    cut_at = len(md_text)
    for marker in CUT_MARKERS:
        idx = md_text.find(marker)
        if idx != -1:
            cut_at = min(cut_at, idx)
    body = md_text[:cut_at]
    body = re.sub(r'\n-{3,}\s*$', '', body.rstrip())
    return body.rstrip() + "\n"


def make_tex(md_path: Path, out_tex: Path):
    text = md_path.read_text(encoding="utf-8")
    worksheet = extract_worksheet(text)
    worksheet = expand_grids(worksheet, out_tex.parent, out_tex.stem)

    tmp_md = out_tex.with_suffix(".worksheet_src.md")
    tmp_md.write_text(worksheet, encoding="utf-8")
    cmd = [
        "pandoc", str(tmp_md),
        "-o", str(out_tex),
        "-s",  # standalone: full compilable .tex, not a fragment
        "-V", "geometry:margin=0.6in",
        "-V", "geometry:landscape",
        "-V", "fontsize=10pt",
        "-V", "colorlinks=true",
        "-V", "mainfont=DejaVu Serif",
        "-V", "monofont=DejaVu Sans Mono",
        "--pdf-engine=xelatex",  # only affects which template pandoc emits
        "-H", str(PREAMBLE),
    ]
    subprocess.run(cmd, check=True)
    try:
        tmp_md.unlink()
    except PermissionError:
        pass


if __name__ == "__main__":
    md_path = Path(sys.argv[1]).resolve()
    out_tex = (Path(sys.argv[2]) if len(sys.argv) > 2 else md_path.with_name(
        md_path.stem + "-worksheet.tex")).resolve()
    make_tex(md_path, out_tex)
    print("wrote", out_tex)
