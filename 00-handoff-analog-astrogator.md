# Analog Astrogator — Project Handoff

This document summarizes everything decided in the planning conversation that led up to
this repo. Read this first, then ask the user (a flight dynamics / mission design
professional — deep domain expert, not a beginner) if anything is unclear before
generating content. Do not silently assume; confirm anything ambiguous.

## The Core Idea

The user works professionally in flight dynamics / mission design (STK, Monte, Copernicus,
has written their own Astrogator clone — treat them as an expert in modern tools). As a side
project with like-minded colleagues, they want to recreate real orbital mechanics problems
using **pre-digital-computer methods**: slide rules, trig/log tables, hand iteration — the
way flight dynamics officers and "human computers" actually worked from the 1950s through
the early Shuttle era.

The inspiration is explicitly *Hidden Figures* / *October Sky* — the era where trajectory
work was done by hand or with analog aids, before digital computers took over as the
primary tool.

**Authenticity bar (important, explicitly specified by the user):** one step short of
recreating a literal historical mission (e.g. not "John Glenn's actual Friendship 7
tracking data"). The *methods, tables, and procedures* must be genuinely authentic —
real techniques like Gauss's method, real period-correct reference tables — but the
mission scenarios themselves are fictional. Do not use "solvable by hand" as a stand-in
for authenticity; the user explicitly rejected that as indistinguishable from mining
generic textbook problems.

## The Campaign Structure

The project is versioned/living, organized as a **campaign mirroring the real history of
spaceflight**, era by era, roughly 1950s–1980s (until digital computers became the
*primary* method — noted below, this happens earlier than the "human computer" mythology
suggests).

**Important nuance already discussed and agreed:** digital computers (IBM 7090/7094,
Apollo Guidance Computer) entered real trajectory work by Mercury (~1961-62) — earlier
than pop-culture framing suggests. So the honest narrative arc is NOT "hand computation
until computers arrive." It's:

1. Hand computation as the **primary** method (pre-Mercury / ballistics era)
2. Hand computation as the **trusted verification/backup** method (Mercury through
   Apollo — this is literally what human computers like Katherine Johnson were doing:
   checking the mainframe's work)
3. Hand computation becomes vestigial (Skylab/Shuttle era)

This 3-part shift is more interesting and more historically honest than a clean cutover,
and later stages (esp. the closing stage) should reflect it.

### Agreed stage list (skeleton, not yet fully fleshed out — build one at a time)

- **Phase 0 — Tools** (see below, this is the load-bearing foundation, build first)
- **Stage 1 — Suborbital ballistics** (Redstone/Mercury-Redstone era, ~1961). No orbital
  mechanics yet — powered ascent + ballistic reentry, range tables, graphical
  range-vs-elevation solutions. Low complexity, sets tone.
- **Stage 2 — Orbital insertion & retrofire targeting** (Mercury-Atlas, 1962). First real
  orbital mechanics. Insertion conditions, retrofire burn targeting to hit a landing
  footprint.
- **Stage 3 — Orbit determination from tracking** (parallel/adjacent to Stage 2). Gauss's
  method angles-only OD from a fictional tracking station.
- **Stage 4 — Rendezvous** (Gemini, 1965-66). Phasing orbit design, Hohmann catch-up,
  terminal rendezvous via Clohessy-Wiltshire relative motion equations.
- **Stage 5 — Translunar** (Apollo, 1966-72). Patched conic TLI targeting, midcourse
  correction via simplified Lambert solve, free-return check. **Flagged as
  disproportionately heavy** — likely 2-3x the effort of any other stage, probably
  its own multi-session arc rather than a single afternoon.
- **Stage 6 — The handoff** (Skylab/Shuttle, 1973+). Proposed as a closing exercise
  rather than new math: take an earlier hand solution and use it as a *verification
  check* against a fast digital computation, mirroring the real historical shift.
- **(Future, explicitly wanted but NOT yet scoped)** — a later stage going as
  interplanetary as possible. Vision only, not designed yet.

**Versioning philosophy (explicit user request):** if a good idea for an earlier era
occurs while working on a later stage (e.g. "this would've been perfect for
Sputnik-era" while deep in Apollo work), go back and insert it. Maintain a living
index/log (stage, problem name, what tool/method it drills, dependencies on earlier
problems) so insertions are easy to place correctly. This log should be a first-class
file, not an afterthought.

## Phase 0 — Tools (build this first, it's the dependency root)

The realization that triggered this phase: later stages assume fluency with tools
nobody currently has (slide rule, table interpolation, hand-iterating Kepler's
equation). Better to build that muscle memory in isolation, as short drills, before
it's needed mid-problem in front of a group.

**Note on background:** the user has slide rule experience but *only* with an aviation
E6B (circular slide rule for wind triangles/fuel burn) — this is a false friend for a
general-purpose linear C/D/A/B-scale slide rule and may need partial unlearning rather
than transfer. Don't assume slide rule fluency transfers from aviation experience.

Agreed drill list, in dependency order:

1. **Slide rule basics** — multiplication/division, squares/cubes, trig scales. Pure
   drill reps, not an orbital problem.
2. **Trig/log table interpolation** — linear interpolation between entries, and
   recognizing when linear interpolation isn't accurate enough.
3. **Mean anomaly → eccentric anomaly → true anomaly, by hand** — solving Kepler's
   equation iteratively with a slide rule + tables. Explicitly called out by the user
   as something nobody in the group has actually done by hand, even in a related
   master's-level education. ~20 minute exercise, not a full narrative problem.
4. **Basic vector/triangle-solving drills** — law of cosines/sines, since much of hand
   orbital mechanics reduces to careful triangle solving.

Phase 0 problems do **not** need mission narrative framing — just tool + reps.
Target length for a Phase 0 drill: ~30 min if the person is already good at it, up to
an afternoon if not.

## Problem Package Format (applies to every problem, all stages)

Every individual problem file should contain these six parts:

1. **Narrative frame** — short fictional mission briefing (who's flying, what's the
   objective, what data exists). Skip this for Phase 0 drills.
2. **Given data** — realistic period-appropriate inputs (tracking angles, burn times,
   vehicle performance numbers). Must be internally consistent — work the problem
   forward first to generate self-consistent inputs, then present only the inputs.
3. **Authentic method + reference material** — state the real period method being used
   (e.g. Gauss's method, universal-variable Kepler solve per Battin), and link to real
   period-correct reference tables where possible (see Tables section below).
4. **Worksheet** — a blank, fillable form, ideally mirroring real NASA/tracking-station
   worksheet layouts where such layouts are known to exist.
5. **Answer key + tolerance** — a target *range*, not a single number (hand computation
   accumulates rounding error), plus the answer you'd get doing it their way
   specifically — don't imply more precision than the period method supports.
6. **Verification step** — instructions to re-run the same scenario in STK / the user's
   own Astrogator clone and compare against the hand result. Comparing hand-method
   error against modern propagation is considered one of the more interesting parts.

## Real Reference Methods Discussed (for future stages)

Confirmed as genuinely authentic, period-appropriate techniques to draw from as
stages are built:

- **Gauss's method** — angles-only orbit determination (three observations → range via
  8th-degree polynomial → Lagrange coefficients). The canonical "no computer" OD method.
- **Laplace's method** — alternative angles-only OD, differentiates line-of-sight
  instead of Gauss's geometric approach. Good contrast problem on the same dataset.
- **Herrick-Gibbs / Gibbs method** — OD from three position vectors (e.g. simulated
  radar fixes) rather than angles.
- **Kepler's equation via Newton-Raphson**, or older graphical/tabular iteration.
- **Battin's universal variable formulation** — from Richard Battin's *An Introduction
  to the Mathematics and Methods of Astrodynamics* (AIAA), built explicitly to unify
  conic cases for hand/early-computer use.
- **Lambert's problem via p-iteration** — from Bate, Mueller & White, *Fundamentals of
  Astrodynamics* (Dover paperback, written with literal hand-computation flowcharts;
  user likely already owns this).
- **Patched conic lunar trajectory design** — also Bate/Mueller/White, ch. ~7.
- **J2 secular drift** (RAAN, argument of perigee, mean anomaly rates) — closed form,
  satisfying by hand, easy to verify against modern propagation afterward.
- **Gauss-Jackson special perturbation integrator** — the actual workhorse numerical
  integrator for hand/early-computer propagation before RK-based methods. A few steps
  by hand is brutal but authentic; treat as an advanced/optional problem.
- **Time/reference frame conversions** — Julian date, GMST/sidereal time, coordinate
  transforms via almanac-style tables (American Ephemeris and Nautical Almanac
  conventions). Unglamorous but was a huge fraction of real human-computer labor.
- **Clohessy-Wiltshire relative motion equations** — for Gemini-era rendezvous, hand
  solvable.

## Reference Tables

Preference: use **real, genuine period reference tables**, linked rather than
reconstructed, wherever they've been digitized. Confirmed available:

- Archive.org has full scans of essentially every edition of *CRC Standard
  Mathematical Tables* from the 1930s onward, individually dated. This lets us pick
  the era-correct edition per stage (e.g. 12th edition, 1959, for the Mercury-Redstone
  stage) rather than using a modern edition or reconstructing tables from scratch.
  Index of editions: https://en.wikipedia.org/wiki/CRC_Standard_Mathematical_Tables
  (links out to individual archive.org scans per edition).
- Trig tables, Kepler's-equation solution charts, and other specialized period
  references have not yet been sourced — do this per-stage as needed, not all
  upfront.

A `reference/tables.md` file should track which table/edition is used by which stage,
with direct links.

## Format & Tooling Decisions

- **Markdown files**, not PDF — chosen explicitly by the user for easy versioning/diffing
  (e.g. inserting a Sputnik-era problem later) over PDF's opacity to diff tools.
- **Digital answer keys included** inline in the same file (clearly headed so they're
  easy to avoid reading early, but not hidden in a separate file).
- Repo lives locally at `C:\src\AnalogAstrogator` on the user's Windows machine.
- The user is using **Cowork** (not Claude Code) specifically because they prefer this
  conversational disposition over Claude Code's more code-focused tuning — be mindful
  of that preference; don't drift into a terse "code-writing-robot" register.
- Git: Cowork has direct local filesystem read/write access, confirmed. Whether Cowork
  can run git commit/push itself is *unconfirmed* — treat as file-writer, and let the
  user handle `git add/commit/push` themselves unless proven otherwise.

## Proposed Repo Structure (not yet created on disk)

```
/campaign/
  00-index.md              <- living stage/problem log + dependency tracking
  phase-0-tools/
    00-slide-rule-basics.md
    01-trig-log-tables-interpolation.md
    02-kepler-equation-by-hand.md
    03-triangle-solving-drills.md
  stage-1-suborbital/
    01-<problem-name>.md
  stage-2-orbital-insertion/
    ...
  reference/
    tables.md               <- curated links to archive.org scans, keyed to stage
```

## Where We Left Off / Next Step

Nothing has been written to disk yet. The immediate next step, agreed but not yet
executed, was: draft `00-index.md` (the skeleton/versioning log) and
`phase-0-tools/00-slide-rule-basics.md` as the first real artifacts, so the user can
sanity-check the format before generating the rest of Phase 0.

## User Working Style Notes

- Deep domain expert — do not over-explain basic orbital mechanics concepts, but DO
  flag it clearly if a request seems to be heading somewhere non-standard or
  historically inaccurate rather than silently complying.
- Prefers direct, honest answers over hedged/softened ones.
- Wants to be asked clarifying questions rather than have significant assumptions made
  silently on their behalf — confirm scope/format choices before generating large
  amounts of content.
