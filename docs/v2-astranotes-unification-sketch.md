# Sketch: Unifying with AstraNotes (v2.0, not yet planned in detail)

**Status: the monorepo move already happened (v1.0, deliberately rough).**
`campaign/` now lives inside this repo, alongside `src/astranotes`. What's
still a sketch, not done, is everything below "Entanglement options" —
shared citations, shared computation, unit extension, pipeline convergence.
Written after reading through the AstraNotes source to find real, concrete
overlap rather than guessing from the project name.

## Direction (per discussion, 2026)

- **Monorepo.** Done for v1.0 — one repo, not two. `campaign/` was copied in
  from the old `AnalogAstrogation` folder (kept around temporarily, outside
  git, as a fallback until the merge is confirmed good).
- **Three release artifacts, not two.** AstraNotes today ships a PDF cheat
  sheet and a Jupyter notebook. Analog Astrogation adds a third: the stack of
  campaign markdown files + their generated worksheet PDFs. v2.0 treats all
  three as siblings from one codebase, not as two projects that happen to
  share a topic.
- **Entangle further, not just adjacent.** Beyond shared citations —
  shared computation, where it makes sense, so the same tested equation
  code backs both the "fast modern scalpel" (AstraNotes) and the answer
  keys behind the "slow analog" campaign (Analog Astrogation).

## What AstraNotes actually is

- A Python/sympy library (`astranotes.cheatsheet.keplerian_equations`) of
  Keplerian orbital-mechanics equations, each tagged with a `SourceRef`
  (author/title/edition/page/equation number) and a `Dimension` (unit-aware,
  SI-native — meters, seconds, radians, kg).
- A **shared, UI-agnostic bibliography layer** already built for this
  exact purpose: `sources_index.py` groups every equation's `SourceRef` by
  source work, and `render_latex_sources.py` / `jupyter_sources_render.py`
  are just two renderers over that same data. This is the reusable piece —
  a markdown renderer for Analog Astrogation's "Authentic method + reference
  material" sections would be a third renderer over data that already
  exists, not a new system.
- Two consumers of the equation library today: a single-page LaTeX/PDF
  "cheat sheet" (hand-rolled Python LaTeX generation, not pandoc) and an
  interactive Jupyter notebook where you plug in orbital elements and see
  every equation evaluate live, unit-converted, with sourcing shown.
- Tested: `tests/cheatsheet/test_keplerian_equations_eval.py` checks things
  like sin²E+cos²E≈1 and atan2 quadrant correctness — actual numeric
  regression tests on the equations, not just "does it render."

The README's stated philosophy: "sometimes a simple calculator is all we
need... as much as STK or Monte are wonderful, sometimes a scalpel is the
better tool." AstraNotes is the fast modern scalpel; Analog Astrogation is
the slow analog one aimed at the same target.

## Concrete overlap already found

- **Same source texts.** AstraNotes cites Vallado 4e and Bate/Mueller/White;
  Analog Astrogation's handoff doc leans on BMW for the same material
  (ballistic missile trajectories, Lambert's problem, patched conics) and
  names Battin for later stages. Two independently-typed citation sets for
  the same handful of books is drift waiting to happen — `sources_index.py`
  already solves this, just not for a third consumer yet.
- **Same equations, different point in the pipeline.** AstraNotes already
  has, tested and unit-correct: vis-viva, mean motion, orbital period,
  circular/escape velocity, angular momentum, perifocal position/velocity
  vectors, the perifocal→inertial rotation, and — notably — **Kepler's
  equation itself** (`mean_anomaly_elliptical`: M = E − e·sin(E), exactly
  what Phase 0.2 solves by hand with a slide rule). Stage 2 (orbital
  insertion) onward needs essentially this exact equation set.
- **Every Analog Astrogation problem already has a "Verification step"**
  telling the reader to recompute their hand answer in STK or "a quick
  script." AstraNotes *is* that quick script, already built, for anything
  Keplerian.
- **Both generate PDFs from structured content via LaTeX**, independently.
  AstraNotes hand-rolls LaTeX strings in Python; Analog Astrogation (as of
  this session) goes markdown → pandoc → `.tex` → xelatex.

## The one guardrail worth keeping regardless of how tight the coupling gets

| | Analog Astrogation | AstraNotes |
|---|---|---|
| Units | Period-authentic — mixed SI and **English/imperial** (lbf, ft, ft/s, slugs) depending on era/stage | SI-native only; no imperial units in `unit_registry` yet |
| Computer's role | Explicitly minimized — the pedagogical point is *not* using one, except as a late verification/"punch card" step | The computer *is* the product |
| Audience posture | A group working problems by hand together, off a printed sheet | One person querying a live reference |

If a worksheet ever *required* AstraNotes to function, it would quietly
undercut the "no computer until the end" premise the campaign is built on.
Entangling the codebases is fine and good; entangling them so a reader
can't do Stage 2 with a slide rule and a printed sheet alone is the one
thing to actively avoid. Shared code behind the scenes, unchanged reader
experience on the page.

## Actual shape of the monorepo (as merged, v1.0)

```
/ (AstraNotes repo, kept its git history)
  src/astranotes/          <- unchanged, the equation library + notebook + cheatsheet builder
  campaign/                <- Analog Astrogation content + tools, copied in as-is
    00-index.md
    phase-0-tools/
    stage-1-suborbital/
    tools/                 <- make_worksheet_tex.py, compile_worksheets.py
  docs/
    v2-astranotes-unification-sketch.md   <- this file
  00-handoff-analog-astrogation.md        <- Analog Astrogation's own planning doc, renamed to avoid clashing with anything repo-root-level
  pyproject.toml           <- unchanged (AstraNotes' existing setuptools config);
                               campaign/tools' only dependency, matplotlib, was
                               already a core AstraNotes dependency, so no
                               separate environment was needed
```

Rough edges left as-is for v1.0, on purpose: `campaign/` isn't a Python
package and isn't referenced anywhere in `pyproject.toml` — it's just
sitting in the repo, sharing the venv by accident of matplotlib overlap
rather than by design. `src/astranotes` and `campaign/` don't import from
each other yet. That's exactly the boundary the entanglement options below
are about crossing, deliberately not crossed yet.

## Entanglement options, loosest to tightest (the actual menu for v2.0)

**1. Shared citation data.** Analog Astrogation's problem files start
sourcing their "Authentic method + reference material" citations from
AstraNotes' `SourceRef`/`sources_index` data (even just by convention, or
literally rendering a markdown view through `sources_index.py` the way the
LaTeX and Jupyter renderers already do). Lowest effort, fixes a real drift
risk, and is the natural first step since the reusable piece already exists.

**2. AstraNotes as the answer-key computation engine.** `campaign/tools/`
imports `astranotes.cheatsheet.keplerian_equations` and uses it to
*compute* the numbers that land in worksheet answer keys for anything
Keplerian, instead of hand-derivation. Directly addresses a real failure
mode from this session — the Stage 1.1 liftoff-weight error existed
because nothing checked the numbers until a human asked a probing
question. Doesn't touch the worksheet/reader experience — purely an
authoring-time tool, which keeps the guardrail above intact for free.

**3. Extend AstraNotes' unit system to imperial units.** Currently the
hard blocker for using AstraNotes as a compute backend for Stage 1-style
problems (lbf, ft/s, slugs). The `SimpleUnit`/`CompositeUnit`/`Dimension`
machinery already handles arbitrary conversion math — this is closer to
"fill in a table" than an architecture change, but it's real work and
touches AstraNotes' own scope, not just Analog Astrogation's.

**4. Converge the two PDF pipelines.** One shared PDF-building toolkit
(either AstraNotes' bespoke LaTeX-string generator, or Analog Astrogation's
pandoc-based one, or something new) instead of two independent ones. This
is the highest-effort, most architecturally-binding option, and the one
most worth deferring until 1–3 have created enough shared surface area to
make the right answer obvious rather than guessed at.

**5. Where the campaign would actually reference AstraNotes.** Not before
Stage 2 — Stage 1 is deliberately pre-orbital-mechanics, so a Keplerian
equation tool would be a non-sequitur there. Stage 2 is the first point
where the content and the equation set actually overlap, and where a
"Verification step" could name AstraNotes specifically instead of saying
"a quick script."

## Open question, not answered here

Whether "entangle" extends to a fourth thing — AstraNotes' notebook
gaining a mode that loads a specific Analog Astrogation problem's inputs and
lets a reader check their hand answer interactively, rather than writing a
one-off script each time. That would make the notebook a genuine fourth
touchpoint for the campaign (beyond citations + computation + eventual
"go check AstraNotes" callouts) but is speculative — flagged here so it's
not lost, not sized or committed.
