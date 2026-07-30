# Phase 0.2 — Kepler's Equation by Hand

**Type:** Tool drill, no mission narrative.
**Target time:** ~20 minutes per example once the iteration pattern clicks —
budget longer the first time through.
**Prerequisite:** 0.0 Slide rule basics, 0.1 Trig/log table interpolation.

This is the drill the handoff notes call out specifically: solving Kepler's
equation by hand, iteratively, with a slide rule and trig tables, is
something nobody in the group has actually done — even people with
graduate-level orbital mechanics training almost always learned it as code,
not as a hand procedure. This is where that changes.

## The equation

Kepler's equation relates mean anomaly (time-like, uniform) to eccentric
anomaly (geometric, on the auxiliary circle):

```
M = E − e·sin(E)          (radians)
```

Worked in **degrees** (the practical choice with a degree-based trig table),
this becomes:

```
M = E − k·e·sin(E)          where k = 180/π ≈ 57.29578
```

There's no closed-form solution for E — it's solved iteratively. Newton-Raphson
on this equation, in degrees:

```
g(E)  = E − k·e·sin(E) − M
g'(E) = 1 − e·cos(E)
E_new = E − g(E)/g'(E)
```

**Watch the units carefully here** — this is the single most common place to
introduce an error. `g'(E) = 1 − e·cos(E)` has **no** factor of k in it, even
though `g(E)` does. That's not a typo: differentiating `sin(E)` with respect
to E when E is expressed in degrees pulls in a factor of π/180 from the
chain rule, which exactly cancels the k in the sine term. If you find
yourself writing `1 − k·e·cos(E)`, stop — that's the mistake to check for
first.

A good starting guess: **E₀ = M**. For higher eccentricity, E₀ = M +
k·e·sin(M) converges faster (it's literally the first pass of simple
successive substitution) — worth trying on Example 2 below if you want to
compare iteration counts.

## Reference material

Trig table: use the 0.1 excerpt/technique (interpolate sin and cos to at
least 5 decimal places — errors here feed directly into g(E) and g'(E)).

Period-authentic note: purpose-built tables existed historically for solving
Kepler's equation directly by lookup rather than iteration (e.g. tables of E
as a function of M and e, in the tradition of Bauschinger's orbit-determination
tables). Sourcing and linking a genuine period edition of one of these is
flagged as a follow-up for `reference/tables.md` — not yet done, so this
drill uses direct Newton-Raphson iteration instead, which is itself a
legitimate period-appropriate method, just more laborious than a
purpose-built lookup table would have been.

## Example 1 — Low eccentricity

**Given:** e = 0.100, M = 30.000°

Iterate E_new = E − g(E)/g'(E) starting from E₀ = M, until |ΔE| is
comfortably below your target precision (aim for < 0.01°).

## Example 2 — Higher eccentricity

**Given:** e = 0.400, M = 45.000°

Same procedure. Expect more iterations and a bigger first correction — this
is exactly why higher-eccentricity orbits were the harder case for real
human computers, and why a smarter initial guess mattered more as e grew.

Once E converges for either example, get the true anomaly ν:

```
tan(ν/2) = √[(1+e)/(1−e)] · tan(E/2)
```

---

## Worksheet

Use one row per Newton-Raphson iteration. Add rows as needed.

**Example 1** (e = 0.100, M = 30.000°)

| n | E_n (°) | sin(E_n) | cos(E_n) | g(E_n) | g'(E_n) | ΔE |
|---|---------|----------|----------|--------|---------|-----|
| 0 | 30.000 | | | | | |
| 1 | | | | | | |
| 2 | | | | | | |

Converged E = __________°  →  ν = __________°

**Example 2** (e = 0.400, M = 45.000°)

| n | E_n (°) | sin(E_n) | cos(E_n) | g(E_n) | g'(E_n) | ΔE |
|---|---------|----------|----------|--------|---------|-----|
| 0 | 45.000 | | | | | |
| 1 | | | | | | |
| 2 | | | | | | |
| 3 | | | | | | |

Converged E = __________°  →  ν = __________°

---

## Hint (read only if you're stuck)

<details>
<summary>Example 1, iteration 0 — worked breakdown</summary>

E₀ = 30.000°. From the trig table (or Drill 2 in 0.1): sin(30°) = 0.50000,
cos(30°) = 0.86603.

- k·e·sin(E₀) = 57.29578 × 0.100 × 0.50000 = 2.86479 — do this as one
  chained slide-rule setting: 57.29578 × 0.1 on C/D first (= 5.72958), then
  × 0.5 without resetting (= 2.86479).
- g(E₀) = 30.000 − 2.86479 − 30.000 = **−2.86479**
- g'(E₀) = 1 − 0.100 × 0.86603 = 1 − 0.08660 = **0.91340**
- ΔE = −g(E₀)/g'(E₀) = −(−2.86479)/0.91340 = **+3.1367°**
- E₁ = 30.000 + 3.1367 = **33.1367°**

Continue the same pattern for iteration 1: look up sin/cos of 33.1367°
(interpolating in your trig table), recompute g and g′, and you should see
ΔE shrink to well under a tenth of a degree — that's the quadratic
convergence Newton-Raphson is known for.
</details>

<details>
<summary>Why Example 2 takes more iterations</summary>

The first correction in Example 2 is much bigger (roughly +22.6° on the
first step, versus +3.1° in Example 1) because both e and the initial
residual are larger. Newton-Raphson still converges — it just needs one or
two extra passes to settle below 0.01°. If your second iteration overshoots
past the converged value and swings back, that's normal behavior for this
equation at moderate eccentricity, not a sign you've made an arithmetic
error — check the *trend* (ΔE shrinking each pass) rather than expecting
smooth monotonic approach.
</details>

---

## Answer key + tolerance

Tolerance reflects realistic hand-computation precision compounding through
several trig lookups and a few iterations: ±0.05° on E, ±0.1° on ν (the
true-anomaly conversion has its own tangent-half-angle lookup, so it
carries a bit more accumulated error).

**Example 1** (e = 0.100, M = 30.000°)
- Converges in ~2 iterations
- E ≈ 33.13°
- ν ≈ 36.40°

**Example 2** (e = 0.400, M = 45.000°)
- Converges in ~3 iterations
- E ≈ 65.92°
- ν ≈ 89.49°

Notice how much farther ν pulls ahead of E (and E ahead of M) as
eccentricity increases — 36.4° vs 33.1° vs 30.0° in Example 1, but 89.5° vs
65.9° vs 45.0° in Example 2. That spread *is* the geometric meaning of
eccentric vs. true anomaly, and it's worth sitting with for a second rather
than just checking the number.

## Verification step

Recompute both examples with a calculator or a quick script carrying full
double-precision Newton-Raphson to convergence, and compare against your
hand-iterated E and ν. Note two things: how many iterations you needed by
hand versus how many the exact computation takes to reach the same
precision, and whether your hand answer's error is dominated by trig-table
interpolation error (from 0.1) or by stopping the iteration slightly early.
Distinguishing those two error sources is exactly the kind of judgment a
real tracking-station human computer had to develop.
