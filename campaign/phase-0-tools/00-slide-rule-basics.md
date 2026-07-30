# Phase 0.0 — Slide Rule Basics

**Type:** Tool drill, no mission narrative.
**Target time:** ~30 min if the scales are already comfortable; up to an
afternoon if not.
**Prerequisite:** None. This is the dependency root for everything else in
the campaign.
**Assumes:** A generic linear slide rule with C, D, A, B, K, S, and T scales
(a standard 10" engineering rule — Pickett, K&E, Post, etc. all work). This
is the baseline for Phase 0; nothing stops a later stage from calling for a
specialized rule (vector rule, log-log duplex for exponentials, a period
Trig/Kepler-specific rule, etc.) if the era or problem genuinely warrants
it — just note the swap explicitly in that problem's file when it happens.

## A note before you start

You've got E6B experience, not linear-rule experience — treat that as a
**false friend**, not a head start. The E6B is a *circular* rule built around
wind-triangle and fuel-burn conventions (rotating compass rose, specialized
scales for TAS/groundspeed). A linear C/D/A/B rule shares the underlying
logarithmic-scale principle but none of the E6B's specialized layout. Two
habits from the E6B will actively work against you here:

- **No fixed "index" story.** On the E6B you're often reading off a wind
  triangle with a consistent visual frame. On a linear rule, the C and D
  scales slide relative to each other and there's no rotating dial to anchor
  your eye — you have to track which index (1 at the left end of C, or the
  10 at the right end) you're using on a given problem, and that choice
  changes every time.
- **Decimal placement is entirely on you.** The E6B's problems are
  bounded (airspeeds, fuel flows) so wrong-order-of-magnitude answers are
  obviously wrong at a glance. A slide rule reads the same for 2.35, 23.5,
  and 235 — the scale only gives you the *significant digits*. You have to
  track the decimal point yourself with a quick mental estimate before you
  trust the rule's answer. This is arguably the single most important habit
  in this whole drill, and it's the one place hand computation fails
  silently if you skip it.

## Scale reference

| Scale | What it is | Use |
|-------|-----------|-----|
| C, D | Identical logarithmic scales, 1–10 | Multiplication, division |
| A, B | Two decades (1–100) squeezed into the C/D length | Squares, square roots |
| K | Three decades (1–1000) | Cubes, cube roots |
| S | Sine scale, angle in degrees | sin(θ) read against C/D |
| T | Tangent scale, angle in degrees | tan(θ) read against C/D |

Standard technique, if it's been a while: to multiply *a × b*, set the left
(or right) index of C over *a* on D, slide the cursor to *b* on C, read the
result on D. Division reverses this. Squares: set cursor on D, read A. Cubes:
set cursor on D, read K. Sine/tangent: set cursor to the angle on S (or T),
read the corresponding value on C (aligned back to D for a combined
calculation).

## Drill 1 — Multiplication and division (C/D scale)

Work these on the C/D scale only. Estimate the decimal placement mentally
*before* you read the rule, then confirm.

1. 2.35 × 4.12
2. 7.68 × 1.94
3. 3.14 × 6.02
4. 56.3 ÷ 8.15
5. 128 ÷ 3.7
6. 9.81 × 2.71828
7. 0.0456 × 273
8. 84.2 ÷ 0.0692
9. (4.5 × 6.3) ÷ 2.1 — do this as one continuous setting, without resetting
   the rule between the multiply and the divide. That chaining is the actual
   skill; a real hand-computer never re-set the rule for an intermediate
   result if they could avoid it.

## Drill 2 — Squares, cubes, and roots (A/B, K scale)

1. 3.85²
2. 12.7²
3. 0.542²
4. 2.15³
5. √56.3
6. √842
7. ∛47.5

## Drill 3 — Trig scales (S, T)

1. sin(23.5°)
2. sin(67°)
3. tan(15°)
4. tan(52°)
5. 45.0 × sin(30.0°) — combined trig + multiply, one setting
6. 68.3 ÷ tan(41.0°) — combined trig + divide, one setting

---

## Worksheet

Fill in your slide rule reading and your decimal-placement estimate
*before* checking the answer key.

| Problem | Your estimate (order of magnitude) | Your slide rule reading |
|---------|-------------------------------------|--------------------------|
| 1.1 | | |
| 1.2 | | |
| 1.3 | | |
| 1.4 | | |
| 1.5 | | |
| 1.6 | | |
| 1.7 | | |
| 1.8 | | |
| 1.9 | | |
| 2.1 | | |
| 2.2 | | |
| 2.3 | | |
| 2.4 | | |
| 2.5 | | |
| 2.6 | | |
| 2.7 | | |
| 3.1 | | |
| 3.2 | | |
| 3.3 | | |
| 3.4 | | |
| 3.5 | | |
| 3.6 | | |

---

## Answer key + tolerance

A well-made 10" rule read carefully gets you roughly ±0.5% on C/D,
±1% on A/B/K (the scale is compressed, so precision is inherently coarser),
and ±1–2% on S/T (worse near the ends of the scale — very small angles on S,
angles approaching 90° on T). These aren't arbitrary — they're the same
order of error a real 1950s–60s hand computer lived with, and it's why
period procedures cross-checked results and worked to a *tolerance band*
rather than treating any single hand answer as exact.

**Drill 1**
1. 9.68 (band: 9.63–9.73)
2. 14.9 (14.83–14.97)
3. 18.9 (18.81–18.99)
4. 6.91 (6.87–6.94)
5. 34.6 (34.4–34.8)
6. 26.7 (26.6–26.8)
7. 12.4 (12.3–12.5)
8. 1220 (1210–1230)
9. 13.5 (13.4–13.6)

**Drill 2**
1. 14.8 (14.7–15.0)
2. 161 (159–163)
3. 0.294 (0.291–0.297)
4. 9.94 (9.84–10.04)
5. 7.50 (7.43–7.58)
6. 29.0 (28.7–29.3)
7. 3.62 (3.58–3.66)

**Drill 3**
1. 0.399 (0.391–0.407)
2. 0.921 (0.912–0.930)
3. 0.268 (0.263–0.273)
4. 1.28 (1.26–1.30)
5. 22.5 (22.3–22.7)
6. 78.6 (77.0–80.2 — tan is steep near 41–45°, so this one's naturally looser)

## Verification step

Recompute all three drills on a calculator (full precision) and log your
percent error against the band above for each problem. Two things to look
for, not just "did I land in the band":

- **Where your error is largest.** If it clusters in Drill 3 or at the small
  end of Drill 2 (0.542²), that's expected — scale compression, not you
  doing something wrong.
- **Whether your error is systematic.** A consistent one-direction bias
  (always reading slightly high, say) usually means a cursor-alignment habit
  to fix, not random reading noise. Worth knowing now, before it's buried
  inside a multi-step orbital problem in Stage 1+.
