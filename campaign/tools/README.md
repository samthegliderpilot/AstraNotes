# Campaign build tools

This is the Analog Astrogator campaign, folded into the AstraNotes repo
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

## Two-step print pipeline

Print-ready worksheets are built in two stages, both committed to git:

1. **`make_worksheet_tex.py`** — extracts the spoiler-free part of a
   problem (title through the Worksheet section; Hint/Answer key/
   Verification are stripped) and converts it to a standalone `.tex` file
   via pandoc. This is the source of truth for the printout — diffable,
   reviewable, and the thing to hand-edit if a worksheet layout needs
   tweaking beyond what the source `.md` controls.
2. **`compile_worksheets.py`** — compiles `.tex` files to PDF with
   `xelatex`, in an isolated temp copy of each file's directory so aux/log
   droppings never land in the repo. Only the final PDF gets copied back.

```
# (with the repo's venv activated)

# regenerate one problem's .tex after editing the source .md
python campaign/tools/make_worksheet_tex.py campaign/stage-1-suborbital/01-range-table-targeting.md

# compile every *-worksheet.tex under campaign/
python campaign/tools/compile_worksheets.py --all

# or compile just one (or a few)
python campaign/tools/compile_worksheets.py campaign/stage-1-suborbital/01-range-table-targeting-worksheet.tex
```

Both scripts write next to the source file by default: `<name>-worksheet.tex`
and `<name>-worksheet.pdf`. If a worksheet embeds a printable grid (see
below), the generated image is `<name>-worksheet-grid_N.png`, also written
next to the source and also meant to be committed — the `.tex` references
it by relative path, so it needs to travel with it.

**After editing a problem's worksheet section, re-run both steps** —
`make_worksheet_tex.py` to regenerate the `.tex` (and any grid images) from
the current `.md`, then `compile_worksheets.py` to rebuild the PDF from the
new `.tex`. The `.tex`/`.png`/`.pdf` are generated artifacts; the `.md` is
the only one meant to be hand-edited.

### Printable grids

If a worksheet step asks the reader to plot points and read a value off a
chart graphically, add a marker where the chart should appear:

```
<!-- printable-grid: title="R vs. gamma" xlabel="gamma (deg)" xmin=28 xmax=57
     xmajor=5 xminor=1 ylabel="R (nm)" ymin=195 ymax=220 ymajor=5 yminor=1 -->
```

It's an HTML comment, so it's invisible in normal markdown rendering — it
only does something when `make_worksheet_tex.py` processes the file. The
tool expands it into a pre-scaled, gridlined blank chart (major and minor
gridlines) so the reader can plot and read answers with a ruler directly on
the printout, without needing separate graph paper. `xmajor`/`xminor`/
`ymajor`/`yminor` are optional (default to sensible fractions of the axis
range).

## Regenerating everything

There's no single "rebuild all `.tex` from `.md`" command yet — run
`make_worksheet_tex.py` once per changed problem, then
`compile_worksheets.py --all` (or just the changed ones) to recompile. If
re-running `make_worksheet_tex.py` across the whole campaign becomes
tedious, a `--all` flag mirroring `compile_worksheets.py`'s would be the
natural next addition.
