# Phase 0.1 — Trig/Log Table Interpolation

**Type:** Tool drill, no mission narrative.
**Target time:** ~30 min if interpolation is already comfortable; longer if not.
**Prerequisite:** 0.0 Slide rule basics.
**Assumes:** You have a 4- or 5-place log table and a matching trig table
(sine/tangent, tenths of a degree). The excerpts below are representative of
real period tables in layout and precision — treat them as if torn from an
actual reference; a period-correct edition (CRC Standard Mathematical Tables
or similar) will be linked in `reference/tables.md` per stage as sourcing is
done.

## Why this matters

A table only gives you exact values at its tabulated points. Everything
between two entries has to be interpolated — and every hand-computation
procedure from this era (Gauss's method, Kepler's-equation solving, orbit
determination worksheets) leans on this constantly. Get sloppy here and the
error propagates into every later step of a multi-stage hand solution.

## Method: linear interpolation

Given a table with entries at x₀ and x₁ = x₀ + Δx, and a target value x
between them:

```
f(x) ≈ f(x₀) + [(x - x₀) / Δx] · [f(x₁) - f(x₀)]
```

In words: find how far across the interval your target sits (as a fraction),
then move that same fraction of the way between the two tabulated values.
This works well when the function is close to a straight line over the
interval — which is the whole design goal of a good table (fine enough
spacing that linear interpolation is trustworthy). It breaks down where the
function curves sharply within one interval — see Drill 3 below.

## Drill 1 — Log table interpolation

Table excerpt: log₁₀(x) for x = 1.00 to 1.10

| x | log₁₀(x) |
|---|----------|
| 1.00 | 0.00000 |
| 1.01 | 0.00432 |
| 1.02 | 0.00860 |
| 1.03 | 0.01284 |
| 1.04 | 0.01703 |
| 1.05 | 0.02119 |
| 1.06 | 0.02531 |
| 1.07 | 0.02938 |
| 1.08 | 0.03342 |
| 1.09 | 0.03743 |
| 1.10 | 0.04139 |

Interpolate:

1. log₁₀(1.034)
2. log₁₀(1.067)
3. log₁₀(1.023)
4. log₁₀(1.089)

## Drill 2 — Trig table interpolation

Table excerpt: sin(θ) for θ = 23.0° to 24.0°

| θ | sin(θ) |
|---|--------|
| 23.0° | 0.39073 |
| 23.1° | 0.39234 |
| 23.2° | 0.39394 |
| 23.3° | 0.39555 |
| 23.4° | 0.39715 |
| 23.5° | 0.39875 |
| 23.6° | 0.40035 |
| 23.7° | 0.40195 |
| 23.8° | 0.40354 |
| 23.9° | 0.40514 |
| 24.0° | 0.40674 |

Interpolate:

1. sin(23.34°)
2. sin(23.78°)
3. sin(23.06°)

## Drill 3 — When linear interpolation isn't good enough

Table excerpt: tan(θ) near a steep region

| θ | tan(θ) |
|---|--------|
| 80.0° | 5.67128 |
| 80.5° | 5.97576 |
| 81.0° | 6.31375 |

Notice the differences aren't constant (0.30448, then 0.33799) — the
function is curving noticeably even over half-degree steps. This is what
"linear interpolation isn't accurate enough" looks like in practice.

1. Interpolate tan(80.3°) two ways: (a) using only the 80.0° and 81.0°
   entries (coarse table, 1° spacing), and (b) using the 80.0° and 80.5°
   entries (finer table, 0.5° spacing). Record both.
2. Compare the two answers. The gap between them is the real cost of using
   too coarse a table near a steep region of the function — this is exactly
   why period trig tables near 80–90° were often tabulated at finer spacing
   (arcminutes, not tenths of a degree), or came with a second-difference
   correction column for exactly this situation.

---

## Hint (read only if you're stuck)

<details>
<summary>Drill 1, Problem 1 — worked breakdown</summary>

log₁₀(1.034) sits between the 1.03 and 1.04 rows.

- Fraction across the interval: (1.034 − 1.03) / (1.04 − 1.03) = 0.4
- Table values: log₁₀(1.03) = 0.01284, log₁₀(1.04) = 0.01703
- Difference: 0.01703 − 0.01284 = 0.00419
- Interpolated value: 0.01284 + 0.4 × 0.00419 = 0.01284 + 0.001676 ≈ **0.01452**

No slide rule needed for this one — the fraction (0.4) is clean enough to do
the multiply in your head or with a quick C/D scale check if you want to
confirm the 0.4 × 0.00419 step.
</details>

<details>
<summary>Drill 3, Problem 1 — worked breakdown</summary>

**(a) Coarse (80.0°/81.0°):** fraction = 0.3. Difference = 6.31375 − 5.67128
= 0.64247. Interpolated = 5.67128 + 0.3 × 0.64247 ≈ **5.864**.

**(b) Fine (80.0°/80.5°):** target 80.3° is 0.6 of the way across this
half-degree interval. Difference = 5.97576 − 5.67128 = 0.30448. Interpolated
= 5.67128 + 0.6 × 0.30448 ≈ **5.854**.

The two methods disagree by about 0.01 (roughly 0.17%) — small in isolation,
but exactly the kind of error a real tracking-station computer couldn't
afford to compound across a multi-step solution. This is why finer-spaced
tables (or correction columns) existed for exactly this region of the
tangent function.
</details>

---

## Answer key + tolerance

**Drill 1** (tolerance: ±0.00003 — log tables interpolate very cleanly)
1. log₁₀(1.034) ≈ 0.01452
2. log₁₀(1.067) ≈ 0.02816
3. log₁₀(1.023) ≈ 0.00987
4. log₁₀(1.089) ≈ 0.03703

**Drill 2** (tolerance: ±0.0001)
1. sin(23.34°) ≈ 0.39620
2. sin(23.78°) ≈ 0.40482
3. sin(23.06°) ≈ 0.39169

**Drill 3**
1a. tan(80.3°), coarse table ≈ 5.864
1b. tan(80.3°), fine table ≈ 5.854
(True value ≈ 5.850 — the fine-table answer is noticeably closer.)

## Verification step

Recompute Drill 1 and Drill 2 answers on a calculator at full precision and
confirm you're within tolerance. For Drill 3, calculate the true value of
tan(80.3°) and note which interpolation (coarse or fine) came closer, and by
how much — that gap is the number you'd carry forward as your error budget
if this table were all you had in the field.
