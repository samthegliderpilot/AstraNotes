# Analog Astrogation — Campaign Index

Living index of every problem in the campaign, in build order. Update this file
whenever a new problem is added or an earlier-era problem gets inserted out of
sequence — that's expected and encouraged (see versioning philosophy in the
handoff doc).

Columns: **Stage** (era), **Problem**, **Method/Tool drilled**, **Depends on**,
**Status**.

## Phase 0 — Tools

Foundation drills. No mission narrative. Build once, reused by every later stage.

| # | Problem | Method/Tool | Depends on | Status |
|---|---------|-------------|------------|--------|
| 0.0 | Slide rule basics | C/D scale mult/div, A/B squares & cubes, S/T trig scales | — | **Drafted** |
| 0.1 | Trig/log table interpolation | Linear interpolation, error recognition | 0.0 | **Drafted** |
| 0.2 | Kepler's equation by hand | Mean → eccentric → true anomaly, Newton-Raphson iteration | 0.0, 0.1 | **Drafted** |
| 0.3 | Triangle-solving drills | Law of cosines/sines, ambiguous SSA case | 0.0, 0.1 | **Drafted** |

## Stage 1 — Suborbital ballistics (Redstone/Mercury-Redstone, ~1961)

No orbital mechanics — powered ascent + ballistic reentry, range tables,
graphical range-vs-elevation solutions. Low complexity, sets tone.

| # | Problem | Method/Tool | Depends on | Status |
|---|---------|-------------|------------|--------|
| 1.0 | Range table targeting (basic, ~30 min) | Tsiolkovsky rocket equation (constant Isp), flat-Earth vacuum ballistic trajectory, graphical range-vs-elevation solution | 0.0, 0.1, 0.3 | **Drafted** |
| 1.1 | Liftoff check & gravity-turn loss (first principles, ~1.5 hr) | Thrust-to-weight sanity check, checkpoint-based trapezoidal integration of gravity/drag loss rates, reader-built numerical integrator for verification | 1.0 | **Drafted** |
| 1.2 | Non-constant Isp ascent (hard mode, full afternoon) | Stepwise numerical integration of the rocket equation, altitude-dependent Isp, reuses 1.1's trajectory checkpoints | 1.0, 1.1 | **Drafted** |

## Stage 2 — Orbital insertion & retrofire targeting (Mercury-Atlas, 1962)

First real orbital mechanics. Insertion conditions, retrofire burn targeting
to hit a landing footprint.

| # | Problem | Method/Tool | Depends on | Status |
|---|---------|-------------|------------|--------|
| 2.x | TBD | TBD | Phase 0, Stage 1 | Not yet scoped |

## Stage 3 — Orbit determination from tracking (parallel to Stage 2)

Gauss's method angles-only OD from a fictional tracking station.

| # | Problem | Method/Tool | Depends on | Status |
|---|---------|-------------|------------|--------|
| 3.x | TBD | Gauss's method | Phase 0 | Not yet scoped |

## Stage 4 — Rendezvous (Gemini, 1965–66)

Phasing orbit design, Hohmann catch-up, terminal rendezvous via
Clohessy-Wiltshire relative motion equations.

| # | Problem | Method/Tool | Depends on | Status |
|---|---------|-------------|------------|--------|
| 4.x | TBD | Clohessy-Wiltshire | Stage 2 | Not yet scoped |

## Stage 5 — Translunar (Apollo, 1966–72)

Patched conic TLI targeting, midcourse correction via simplified Lambert
solve, free-return check. **Flagged heavy** — likely 2–3x the effort of any
other stage; probably its own multi-session arc.

| # | Problem | Method/Tool | Depends on | Status |
|---|---------|-------------|------------|--------|
| 5.x | TBD | Patched conics, Lambert p-iteration | Stage 2, Stage 4 | Not yet scoped |

## Stage 6 — The handoff (Skylab/Shuttle, 1973+)

Closing exercise, not new math: take an earlier hand solution and use it as a
verification check against a fast digital computation — mirrors the real
historical shift from primary method to backup/verification to vestigial.

| # | Problem | Method/Tool | Depends on | Status |
|---|---------|-------------|------------|--------|
| 6.x | TBD | Re-verification of an earlier stage's result | Any prior stage | Not yet scoped |

## Future — Interplanetary

Vision only, not yet scoped. Explicitly wanted as a later addition.

## Insertion Log

Track any problem inserted out of build order here, with the reason.

| Date | Problem inserted | Target stage | Reason |
|------|-------------------|---------------|--------|
| — | 1.1 rebuilt from chart-reading to first-principles derivation; 1.0/1.2 revised | Stage 1 | User wanted the loss budget actually studied, not read off a pre-built chart. Rebuild caught a real error in 1.0's original vehicle spec (W₀=66,000 lbf implies T/W₀<1 — can't lift off) and its loss placeholder (900 ft/s vs. a derived ~3540 ft/s). Corrected W₀=55,000 lbf and the derived loss value now propagate through 1.0 and 1.2. |

## Notes

- Authenticity bar: real methods/tables, fictional mission scenarios. Not
  "solvable by hand" as a proxy for authenticity — genuine period technique.
- Every problem file follows the six-part Problem Package Format (narrative
  frame, given data, authentic method + reference, worksheet, answer key +
  tolerance, verification step) — Phase 0 drills omit the narrative frame.
- **Combined campaign PDF:** `python campaign/tools/build_campaign_pdf.py`
  builds `build/analog_astrogation_campaign.pdf` — every problem's full
  content (narrative through verification), stage by stage, with a title
  page and table of contents. This is the primary shareable deliverable and
  the only campaign build output checked into git; re-run it after editing
  any problem file.
- **Printable worksheets (live/print use):**
  `python campaign/tools/build_worksheet_pdf.py <problem.md>` (or `--all`)
  builds one problem's spoiler-free `<name>-worksheet.pdf` directly —
  narrative through worksheet only, Hint/Answer key/Verification stripped.
  Generated on demand — **not** committed to git (see `tools/README.md`). If
  a worksheet step asks the reader to plot and read a value graphically, add
  a `<!-- printable-grid: ... -->` marker
  (see `tools/README.md` for the attributes) at that point in the source
  file — the tool expands it into a pre-scaled, gridlined blank chart so the
  reader can plot and read with a ruler directly on the printout, no
  separate graph paper needed.
