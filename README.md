# AstraNotes

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

## Features (v1.0)

### Printable PDF cheat sheet

### Interactive Jupyter notebook
- Enter orbital elements (with units)
- Automatically evaluates equations
- Unit-aware inputs and outputs

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

## Building the PDF cheat sheet

From an activated virtual environment:
```
python -m astrocalc.build_cheatsheet
```

This generates a LaTeX file and compiles it into a PDF.  LaTeX is required for PDF generation.

## Sources

AstraNotes draws primarily from:

Vallado, Fundamentals of Astrodynamics and Applications, 4th Edition

Bate, Mueller, White, Fundamentals of Astrodynamics

Exact page and equation numbers are included for each formula.

## Project status

AstraNotes is an evolving personal project. Version 1.0 focuses on:

- Keplerian orbits
- Clarity and correctness

Future versions may add:

- more equations of course!
- Time standard conversions
- Additional orbital element types

## License

GPL-3.0. See the LICENSE file for details.

## Analog Astrogator campaign

`campaign/` holds a related but separate project: a set of hand-computation
orbital mechanics problems (slide rule, tables, period methods — no
calculator until a late verification step), released as markdown files plus
generated print-ready PDFs. See `campaign/00-index.md` for the campaign
itself and `campaign/tools/README.md` for how the PDFs are built. It shares
this repo starting v1.0; deeper integration with the equation library above
(shared citations, using it as an answer-key computation engine, etc.) is
sketched in `docs/v2-astranotes-unification-sketch.md` but not yet done.

## Why this exists

This project grew out of my desire to better connect the math to the evaluation of these equations.  Sometimes a simple calculator is all we need.  As much as STK or Monte are wonderful, sometimes a scaple is the better tool.  And all in all, this has been a pretty easy project to build.

I hope you find it as useful as I do.
