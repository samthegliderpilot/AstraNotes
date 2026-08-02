#!/usr/bin/env python3
"""Build a spoiler-free, printable worksheet PDF for one campaign problem:
title through the Worksheet section only -- Hint/Answer key/Verification are
stripped. For the full-content combined campaign book, see
build_campaign_pdf.py instead.

Also expands "printable-grid" markers into pre-scaled, gridlined blank axes
(via matplotlib) so a reader can plot hand-computed points directly on the
printout and read answers off it with a ruler/straightedge, instead of
needing separate graph paper.

Marker syntax (put this as an HTML comment in the source .md, right where
the graph should appear -- invisible in normal markdown rendering):

  <!-- printable-grid: title="Fig 1" xlabel="gamma (deg)" xmin=30 xmax=55
       xmajor=5 xminor=1 ylabel="R (nm)" ymin=195 ymax=220 ymajor=5 yminor=1 -->

Usage:
  python3 build_worksheet_pdf.py <problem.md> [output.pdf]
  python3 build_worksheet_pdf.py --all          # every problem under campaign/

Everything (extracted markdown, grid images, .tex, xelatex droppings) is
built in an isolated temp directory; only the final PDF is written back,
next to the source .md by default. Output is not committed to git (see
.gitignore) -- regenerate it whenever you need it for live/print use.
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from _shared import PREAMBLE, expand_grids, compile_tex_to_pdf, iter_problem_files

CUT_MARKERS = ["\n## Hint", "\n## Answer key", "\n## Verification step"]


def extract_worksheet(md_text: str) -> str:
    cut_at = len(md_text)
    for marker in CUT_MARKERS:
        idx = md_text.find(marker)
        if idx != -1:
            cut_at = min(cut_at, idx)
    body = md_text[:cut_at]
    body = re.sub(r'\n-{3,}\s*$', '', body.rstrip())
    return body.rstrip() + "\n"


def make_tex(worksheet_md: str, out_tex: Path):
    tmp_md = out_tex.with_suffix(".worksheet_src.md")
    tmp_md.write_text(worksheet_md, encoding="utf-8")
    cmd = [
        "pandoc", str(tmp_md),
        "-o", str(out_tex),
        "-s",  # standalone: full compilable .tex, not a fragment
        "-V", "papersize=letter",
        "-V", "geometry:margin=0.6in",
        "-V", "geometry:landscape",
        "-V", "fontsize=10pt",
        "-V", "colorlinks=true",
        "-V", "mainfont=DejaVu Serif",
        "-V", "monofont=DejaVu Sans Mono",
        "--pdf-engine=xelatex",
        "-H", str(PREAMBLE),
    ]
    subprocess.run(cmd, check=True)
    try:
        tmp_md.unlink()
    except PermissionError:
        pass


def build_one(md_path: Path, out_pdf: Path) -> bool:
    text = md_path.read_text(encoding="utf-8")
    worksheet = extract_worksheet(text)
    with tempfile.TemporaryDirectory() as td:
        workdir = Path(td)
        worksheet = expand_grids(worksheet, workdir, md_path.stem)
        out_tex = workdir / "worksheet.tex"
        make_tex(worksheet, out_tex)
        grid_pngs = sorted(workdir.glob(f"{md_path.stem}-grid_*.png"))
        return compile_tex_to_pdf(out_tex, out_pdf, extra_assets=grid_pngs)


def default_output(md_path: Path) -> Path:
    return md_path.with_name(md_path.stem + "-worksheet.pdf")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args == ["--all"]:
        targets = [(md_path, default_output(md_path)) for _stage, md_path in iter_problem_files()]
        if not targets:
            print("No problem files found under campaign/")
            sys.exit(1)
    else:
        md_path = Path(args[0]).resolve()
        out_pdf = Path(args[1]).resolve() if len(args) > 1 else default_output(md_path)
        targets = [(md_path, out_pdf)]

    ok = True
    for md_path, out_pdf in targets:
        ok = build_one(md_path, out_pdf) and ok
    sys.exit(0 if ok else 1)
