# Phase 0.3 — Triangle-Solving Drills

**Type:** Tool drill, no mission narrative.
**Target time:** ~30 min.
**Prerequisite:** 0.0 Slide rule basics, 0.1 Trig/log table interpolation.

Much of hand orbital mechanics — tracking geometry, Gauss's method, range-
and-bearing problems — reduces at some point to careful triangle solving.
This drill covers the three tools you'll lean on repeatedly: law of cosines,
law of sines, and the ambiguous SSA case (which trips up more people than
it should, and is worth meeting here rather than mid-problem later).

## Law of cosines

```
c² = a² + b² − 2ab·cos(C)          (SAS: two sides + included angle → third side)
cos(C) = (a² + b² − c²) / (2ab)    (SSS: three sides → any angle)
```

## Law of sines

```
a/sin(A) = b/sin(B) = c/sin(C)
```

## The ambiguous case (SSA)

Given two sides and a non-included angle, there can be **zero, one, or two**
valid triangles. If the given angle is acute and the side opposite it is
shorter than the other given side, check both the arcsine solution and its
supplement (180° − that angle) — both may produce a valid triangle. This is
a genuine geometric ambiguity, not a mistake to avoid; real tracking data
resolved it with a second observation or physical reasoning about which
solution made sense.

## Drill 1 — SAS

Sides a = 42.3, b = 57.8, included angle C = 63.5°. Find side c.

## Drill 2 — SSS

Sides a = 35.0, b = 48.0, c = 61.0. Find angle C (opposite the longest side).

## Drill 3 — ASA

Angle A = 41.0°, angle B = 67.0°, side a = 28.5 (opposite A). Find angle C,
side b, and side c.

## Drill 4 — SSA (ambiguous case)

Side a = 22.0, side b = 30.0, angle A = 25.0° (opposite side a). Find all
valid solutions for angle B, and complete each triangle (angle C and side c).

---

## Worksheet

| Drill | Given | Working | Answer |
|-------|-------|---------|--------|
| 1 | a=42.3, b=57.8, C=63.5° | | c = |
| 2 | a=35.0, b=48.0, c=61.0 | | C = |
| 3 | A=41.0°, B=67.0°, a=28.5 | | C=___ b=___ c=___ |
| 4a | a=22.0, b=30.0, A=25.0° | | B=___ C=___ c=___ |
| 4b | (second solution) | | B=___ C=___ c=___ |

---

## Hint (read only if you're stuck)

<details>
<summary>Drill 1 — worked breakdown</summary>

c² = a² + b² − 2ab·cos(C)

- a² = 42.3² = 1789.29 — square on the A/B scale (0.0 Drill 2 skill)
- b² = 57.8² = 3340.84
- Sum: 5130.13
- 2ab = 2 × 42.3 × 57.8 = 4889.88 — chain multiply on C/D without resetting
- cos(63.5°) = 0.44620 — trig table, interpolating between 63° and 64°
  entries
- 2ab·cos(C) = 4889.88 × 0.44620 ≈ 2181.9
- c² = 5130.13 − 2181.9 = 2948.2
- c = √2948.2 ≈ **54.3** — square root via A/B scale (reverse of the
  squaring operation)

Every step here is a tool you already drilled in 0.0 and 0.1 — this problem
is really just about chaining them in the right order without losing track
of intermediate values. Write down each intermediate result; don't try to
carry more than one running value in your head.
</details>

<details>
<summary>Drill 4 — why there are two answers</summary>

sin(B) = b·sin(A)/a = 30.0 × sin(25.0°) / 22.0 = 30.0 × 0.42262 / 22.0 ≈
0.5763

This gives B ≈ 35.2° **or** B ≈ 180° − 35.2° = 144.8°. Check both: does
A + B stay under 180° in each case?

- 25.0° + 35.2° = 60.2° — valid, leaves 119.8° for C
- 25.0° + 144.8° = 169.8° — also valid, leaves only 10.2° for C

Both triangles are geometrically real. This is the case to internalize now:
whenever a > (b·sin A) but a < b, expect two solutions, not one — later,
when this shows up buried inside a tracking-geometry problem, you want to
recognize it immediately rather than quietly picking one root and moving on.
</details>

---

## Answer key + tolerance

Tolerance: ±0.3% on lengths, ±0.2° on angles — consistent with chaining a
few slide-rule operations and one or two trig-table lookups per problem.

**Drill 1:** c ≈ 54.3

**Drill 2:** C ≈ 93.3°

**Drill 3:** C = 72.0° exact (180 − 41 − 67), b ≈ 40.0, c ≈ 41.3

**Drill 4:**
- Solution a: B ≈ 35.2°, C ≈ 119.8°, c ≈ 45.2
- Solution b: B ≈ 144.8°, C ≈ 10.2°, c ≈ 9.2

## Verification step

Recompute all four drills at calculator precision and confirm you're within
tolerance. For Drill 4 specifically, verify both solutions independently
using the law of cosines instead of the law of sines (c² = a² + b² −
2ab·cos(C) with your solved C) — if both cross-checks close, that's good
confirmation you found genuinely valid triangles and not an arithmetic
coincidence.
