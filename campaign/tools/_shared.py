"""Shared helpers for the campaign build tools.

Used by both build_worksheet_pdf.py (single problem, spoiler-free, for
live/print use) and build_campaign_pdf.py (the whole campaign, full content,
combined) so the printable-grid expansion, xelatex compile step, and stage
ordering exist in exactly one place.
"""
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
CAMPAIGN_ROOT = TOOLS_DIR.parent
REPO_ROOT = CAMPAIGN_ROOT.parent
PREAMBLE = TOOLS_DIR / "worksheet_preamble.tex"

# Explicit build order: (stage folder name, display title for a section
# heading). Add a line here as each new stage folder is built -- same
# hardcoded-order convention as the equation list in
# src/astranotes/build_cheatsheet.py's generate_latex().
STAGE_ORDER = [
    ("phase-0-tools", "Phase 0 — Tools"),
    ("stage-1-suborbital", "Stage 1 — Suborbital Ballistics (Redstone/Mercury-Redstone, ~1961)"),
]


def iter_problem_files():
    """Yield (stage_folder, md_path) for every problem markdown file, in
    campaign build order."""
    for stage_folder, _title in STAGE_ORDER:
        stage_dir = CAMPAIGN_ROOT / stage_folder
        for md_path in sorted(stage_dir.glob("*.md")):
            yield stage_folder, md_path


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


def expand_grids(md_text: str, image_dir: Path, stem: str) -> str:
    """Expand <!-- printable-grid: ... --> markers into gridlined chart images,
    saved next to (image_dir) as <stem>-grid_N.png, and referenced by relative
    markdown image links in the returned text."""
    count = 0

    def repl(m):
        nonlocal count
        count += 1
        attrs = parse_attrs(m.group(1))
        png_name = f"{stem}-grid_{count}.png"
        make_grid_image(attrs, image_dir / png_name)
        caption = attrs.get("title", "")
        return f"\n![{caption}]({png_name})\n"

    return GRID_RE.sub(repl, md_text)


def compile_tex_to_pdf(tex_path: Path, dest_pdf: Path, extra_assets=()) -> bool:
    """Compile a .tex file to PDF with xelatex, in an isolated temp copy of
    its directory (so aux/log droppings never land in the repo). Copies any
    same-stem grid PNGs alongside by default, plus any extra_assets paths.
    Copies the resulting PDF to dest_pdf. Returns True on success."""
    tex_path = tex_path.resolve()
    src_dir = tex_path.parent
    with tempfile.TemporaryDirectory() as td:
        workdir = Path(td)
        shutil.copy(tex_path, workdir / tex_path.name)
        for png in src_dir.glob(f"{tex_path.stem}-grid_*.png"):
            shutil.copy(png, workdir / png.name)
        for asset in extra_assets:
            asset = Path(asset)
            shutil.copy(asset, workdir / asset.name)

        cmd = ["xelatex", "-interaction=nonstopmode", "-halt-on-error", tex_path.name]
        result = subprocess.run(cmd, cwd=str(workdir), capture_output=True, text=True)
        out_pdf = workdir / (tex_path.stem + ".pdf")
        if result.returncode != 0 or not out_pdf.exists():
            print(f"FAILED: {tex_path.name}")
            print(result.stdout[-3000:])
            print(result.stderr[-2000:])
            return False

        dest_pdf.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(out_pdf, dest_pdf)
        print(f"wrote {dest_pdf}")
        return True
