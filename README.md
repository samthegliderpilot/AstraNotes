# AstraNotes

[![Latest Release](https://img.shields.io/github/v/release/samthegliderpilot/AstraNotes)](https://github.com/samthegliderpilot/AstraNotes/releases/latest)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/samthegliderpilot/AstraNotes/main?labpath=notebooks)

AstraNotes is an orbital mechanics cheat sheet with two faces:
- a clean, printable PDF of commonly used Keplerian equations
- an interactive Jupyter notebook where you can enter orbital elements and see values evaluated immediately

It is designed as a reference and learning aid, not a full astrodynamics library or flight dynamics simulator.

## What is this for?

AstraNotes is useful if you:
- work with Keplerian orbits and want a quick, reliable reference
- are learning or reviewing astrodynamics and want equations tied to clear sources
- want to sanity-check orbital values interactively without writing a full script
- like having a living cheat sheet instead of static notes or screenshots

This project intentionally stays close to the math you’d see in standard textbooks.  But if you want high-fidelity propagation, perturbations, or mission analysis, you should look elsewhere. AstraNotes is about clarity and convenience.

## Features

### Printable PDF cheat sheet

[Download the latest PDF](https://github.com/samthegliderpilot/AstraNotes/releases/latest/download/keplerian_cheatsheet.pdf) — no build tools needed, always the most recent release.

### Interactive Jupyter notebook
- Enter orbital elements (with units)
- Automatically evaluates equations
- Unit-aware inputs and outputs
- Runs in your browser with no install — see [Try it without installing anything](#try-it-without-installing-anything) below

### Explicit sourcing

Each equation traces back to a textbook and page/equation number

## Getting started
Requirements

- Python 3.10+
- Git
- Setup (recommended)

Clone the repository and run the bootstrap script for your platform:

PowerShell (Windows):
```
./create_venv.ps1
```

Bash (Linux/macOS):
```
./create_venv.sh
```

This will:
- create a virtual environment
- install AstraNotes in editable mode with notebook + dev dependencies
- register a Jupyter kernel
- enable git hooks for notebook hygiene

When finished, select the kernel Python (AstraNotes) in Jupyter.

## Using the notebook

Open the main notebook and:
1 enter orbital elements
1 choose display units

The equations update automatically, and a Sources section shows where each equation comes from.

## Try it without installing anything

[Binder](https://mybinder.org) builds a temporary, fully-configured Jupyter environment in your browser from this repo — no Python install, no cloning, nothing to set up. Click a badge below and wait roughly a minute while it builds; you'll get a live notebook you can run and edit. It's a scratch copy — nothing you change gets saved back here, so it's safe to poke at.

- [![Launch cheat sheet in Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/samthegliderpilot/AstraNotes/main?labpath=notebooks%2FOrbital_Elements_Cheet_Sheet.ipynb) — the interactive equation cheat sheet above
- [![Launch Lesson 1 in Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/samthegliderpilot/AstraNotes/main?labpath=notebooks%2FLesson_1_STM_2BP_Fundamentals.ipynb) — Lesson 1: the State Transition Matrix in the two-body problem (`notebooks/Lesson_1_STM_2BP_Fundamentals.ipynb`), a from-scratch derivation and numerical implementation, sympy through scipy

## Building the PDF cheat sheet

From an activated virtual environment:
```
python src/astranotes/build_cheatsheet.py
```

This generates a LaTeX file and compiles it into a PDF.  LaTeX is required for PDF generation.

## Sources

AstraNotes draws primarily from:

Vallado, Fundamentals of Astrodynamics and Applications, 4th Edition

Bate, Mueller, White, Fundamentals of Astrodynamics

Exact page and equation numbers are included for each formula.

## Project status

AstraNotes is an evolving personal project. Right now it focuses on:

- Keplerian orbits
- Clarity and correctness

Future versions may add:

- more equations of course!
- Time standard conversions
- Additional orbital element types

## Releases

Pushing a `main` commit doesn't publish anything by itself. Pushing a tag
(`vYYYY.MM.DD`) does: [`.github/workflows/release.yml`](.github/workflows/release.yml)
rebuilds both PDFs fresh and attaches them to a new GitHub Release under
that tag. The download links above always point at the latest one.

## License

Code (`src/astranotes/`, `campaign/tools/`) is licensed under the Mozilla
Public License 2.0 — see the [LICENSE](LICENSE) file.

Content (the Analog Astrogation campaign problems, notebooks, and generated
PDFs) is licensed under Creative Commons Attribution-ShareAlike 4.0
International (CC-BY-SA 4.0) — see [campaign/LICENSE](campaign/LICENSE).

## Analog Astrogation campaign

`campaign/` holds a related but separate project: a set of hand-computation
orbital mechanics problems (slide rule, tables, period methods — no
calculator until a late verification step), released as markdown files plus
a generated print-ready PDF. The whole campaign so far — every problem,
narrative through verification, in order — is one combined PDF:
[download the latest campaign PDF](https://github.com/samthegliderpilot/AstraNotes/releases/latest/download/analog_astrogation_campaign.pdf)
(or rebuild it yourself with `python campaign/tools/build_campaign_pdf.py`,
which writes it to `build/analog_astrogation_campaign.pdf`). See `campaign/00-index.md`
for the campaign index and `campaign/tools/README.md` for how the PDFs are
built. It shares this repo starting v1.0; deeper integration with the
equation library above (shared citations, using it as an answer-key
computation engine, etc.) is sketched in
`docs/v2-astranotes-unification-sketch.md` but not yet done.

## Why this exists

This project grew out of my desire to better connect the math to the evaluation of these equations.  Sometimes a simple calculator is all we need.  As much as STK or Monte are wonderful, sometimes a scaple is the better tool.  And all in all, this has been a pretty easy project to build.

I hope you find it as useful as I do.
