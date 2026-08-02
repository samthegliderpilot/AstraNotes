# Campaign build tools

This is the Analog Astrogation campaign, folded into the AstraNotes repo
(v1.0: same repo, mostly separate content; deeper entanglement is future
work — see `docs/v2-astranotes-unification-sketch.md`).

## Setup

No separate environment needed — these scripts only depend on
`matplotlib`, which is already a core dependency of the main repo. Run the
usual repo bootstrap from the repo root (`./create_venv.sh` or
`./create_venv.ps1`) and the venv it creates covers `campaign/tools/` too.

**System prerequisites (not pip-installable, install separately):**
- [pandoc](https://pandoc.org/)
- a LaTeX distribution that provides `xelatex` (e.g. TeX Live or MacTeX)
- the DejaVu fonts (DejaVu Serif, DejaVu Sans Mono) — used for Unicode
  coverage (Greek letters, subscripts) that the default LaTeX fonts lack.
  Usually already present on Linux; on macOS/Windows, install if missing.

## The combined campaign PDF (primary deliverable)

```
python campaign/tools/build_campaign_pdf.py
```

Builds `build/analog_astrogation_campaign.pdf` — every problem's full
content (narrative through verification), stage by stage, in campaign order,
with a title page and table of contents. This is the one file meant to be
handed to someone as "the campaign so far," and the only campaign build
output committed to git (alongside the equation cheat sheet, which lands in
the same `build/` directory).

It reads every problem `.md` directly (no separate source-of-truth `.tex` to
maintain) and does everything — markdown assembly, printable-grid chart
expansion, pandoc, xelatex — in an isolated temp directory, copying back only
the final PDF. Re-run it any time a problem file changes; there's nothing
else to regenerate.

Stage order is a short hardcoded list in `_shared.py` (`STAGE_ORDER`) — add
a line there when a new stage folder is built.

## Single-worksheet print pipeline (for live/print use)

Separate from the combined PDF: if you want one problem's **spoiler-free**
worksheet (narrative through the Worksheet section only — no hints, answer
key, or verification) as a standalone printable PDF for working a problem
live:

```
# (with the repo's venv activated)

# one problem
python campaign/tools/build_worksheet_pdf.py campaign/stage-1-suborbital/01-range-table-targeting.md

# every problem under campaign/
python campaign/tools/build_worksheet_pdf.py --all
```

Goes straight from `.md` to PDF (pandoc + xelatex, isolated temp dir) in one
step — there's no separate `.tex` to generate or hand-edit first. Output
lands next to the source `.md` as `<name>-worksheet.pdf` by default and is
**not** committed to git (see `.gitignore`) — regenerate it whenever you need
it.

### Printable grids

If a worksheet step asks the reader to plot points and read a value off a
chart graphically, add a marker where the chart should appear:

```
<!-- printable-grid: title="R vs. gamma" xlabel="gamma (deg)" xmin=28 xmax=57
     xmajor=5 xminor=1 ylabel="R (nm)" ymin=195 ymax=220 ymajor=5 yminor=1 -->
```

It's an HTML comment, so it's invisible in normal markdown rendering — it
only does something when `build_worksheet_pdf.py` or `build_campaign_pdf.py`
processes the file. The tool expands it into a pre-scaled, gridlined blank
chart (major and minor gridlines) so the reader can plot and read answers
with a ruler directly on the printout, without needing separate graph paper.
`xmajor`/`xminor`/`ymajor`/`yminor` are optional (default to sensible
fractions of the axis range).

## Shared helpers

`_shared.py` holds the printable-grid expansion (`expand_grids`), the
isolated-temp-dir xelatex compile step (`compile_tex_to_pdf`), and the
campaign-wide stage order (`STAGE_ORDER`, `iter_problem_files`) used by both
scripts above — not a script itself, just imported by the others.
