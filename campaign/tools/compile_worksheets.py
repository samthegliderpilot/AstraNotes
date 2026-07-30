#!/usr/bin/env python3
"""Compile worksheet .tex files (produced by make_worksheet_tex.py) to PDF.

Usage:
  python3 compile_worksheets.py <file1.tex> [file2.tex ...]
  python3 compile_worksheets.py --all          # find every *-worksheet.tex under campaign/

Compiles each .tex in an isolated temp copy of its directory (so xelatex's
aux/log/out droppings never land in the repo), then copies the resulting
PDF back next to the source .tex.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CAMPAIGN_ROOT = Path(__file__).resolve().parent.parent


def find_all_tex():
    return sorted(CAMPAIGN_ROOT.glob("**/*-worksheet.tex"))


def compile_one(tex_path: Path) -> bool:
    tex_path = tex_path.resolve()
    src_dir = tex_path.parent
    with tempfile.TemporaryDirectory() as td:
        workdir = Path(td)
        # copy the .tex and any images it references (same-stem PNGs)
        shutil.copy(tex_path, workdir / tex_path.name)
        for png in src_dir.glob(f"{tex_path.stem}-grid_*.png"):
            shutil.copy(png, workdir / png.name)

        cmd = ["xelatex", "-interaction=nonstopmode", "-halt-on-error", tex_path.name]
        result = subprocess.run(cmd, cwd=str(workdir), capture_output=True, text=True)
        out_pdf = workdir / (tex_path.stem + ".pdf")
        if result.returncode != 0 or not out_pdf.exists():
            print(f"FAILED: {tex_path.name}")
            print(result.stdout[-3000:])
            print(result.stderr[-2000:])
            return False

        dest_pdf = src_dir / (tex_path.stem + ".pdf")
        shutil.copy(out_pdf, dest_pdf)
        print(f"wrote {dest_pdf}")
        return True


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args == ["--all"]:
        tex_files = find_all_tex()
        if not tex_files:
            print("No *-worksheet.tex files found under", CAMPAIGN_ROOT)
            sys.exit(1)
    else:
        tex_files = [Path(a) for a in args]

    ok = True
    for tex in tex_files:
        ok = compile_one(tex) and ok
    sys.exit(0 if ok else 1)
