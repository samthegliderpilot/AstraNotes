# Stage 1.2 — Non-Constant Isp Ascent (Hard Mode)

**Era:** Redstone/Mercury-Redstone class, ~1961 (fictional program), continuing Project Arrowhead.
**Target time:** a full afternoon.
**Prerequisite:** Stage 1.0 (Range Table Targeting), Stage 1.1 (Liftoff Check & Gravity-Turn Loss).

## Why this problem exists

1.0 treated specific impulse as a single constant, 235 s, for the whole
burn. Real engines don't work that way: thrust is F = ṁ·Ve + (Pe − Pamb)·Ae
— as the vehicle climbs and ambient pressure Pamb drops, the same engine
produces more thrust and a higher effective Isp, right up to a vacuum
ceiling. This is standard, period-authentic propulsion analysis (see Sutton,
*Rocket Propulsion Elements* — in print and in active engineering use well
before 1961) and it is **not** a small effect: most of the pressure drop
happens in the first ~100,000–150,000 ft, which is most of this vehicle's
burn. Treating Isp as constant, as 1.0 did, understates burnout velocity by
a meaningful margin — you'll see by how much below.

This is genuinely harder than 1.0, for a specific reason: Isp now depends on
altitude, altitude depends on the velocity history, and velocity depends on
Isp. That circular dependency is why this can't be solved in one closed-form
step — it has to be marched forward in time, a handful of steps at a time,
the same way early trajectory integrators (Gauss-Jackson and similar —
already flagged in the campaign's reference list as a harder future problem
in its own right) worked before continuous integration was practical by
hand. What you're doing here is a simplified version of that same idea.

## Given data

Same (corrected) vehicle as 1.0/1.1: W₀ = 55,000 lbf, Wₚ = 40,000 lbf burned
uniformly over t_b = 143 s (weight decreases linearly with time). Standard
gravity g₀ = 32.174 ft/s².

**Loss budget:** Δv_losses = 3540 ft/s, from Stage 1.1's first-principles
gravity-turn/drag study.

**Engine performance — Isp vs. altitude** (from separate propulsion
analysis; reflects the nozzle's altitude compensation as ambient pressure
drops):

| h (ft) | Isp (s) |
|--------|---------|
| 0 | 235 |
| 20,000 | 246 |
| 40,000 | 253 |
| 60,000 | 258 |
| 80,000 | 261 |
| 100,000 | 263 |
| 120,000 | 264 |
| ≥ 140,000 | 265 (vacuum plateau) |

**Ascent altitude profile:** reuse the same trajectory checkpoints from
Stage 1.1 (same vehicle, same preliminary shaping run) rather than a
separately-invented profile:

| t (s) | h (ft) |
|-------|--------|
| 0 | 0 |
| 13 | 604 |
| 39 | 6,485 |
| 65 | 19,230 |
| 91 | 37,878 |
| 117 | 63,427 |
| 143 | 100,235 |

**Explicit simplification, stated up front:** this problem does *not* solve
for the trajectory shape — the altitude profile above is a given input
(1.1's result), not something you derive from the velocity you're computing
here. That keeps the coupling one-directional (altitude → Isp → Δv) and
hand-tractable. The full version, where Isp-vs-altitude feeds back into the
trajectory shape itself, is real and harder — a natural candidate for a
future stage, not this one.

## Authentic method + reference material

Divide the burn into the six intervals defined by the checkpoints above
(note: unequal step sizes — the first is 13 s, the rest are 26 s each,
since they come from 1.1's checkpoint times, not an even split). For each
step:

```
1. Look up altitude at the START of the step (from the given profile).
2. Interpolate Isp at that altitude.
3. c = Isp · g₀
4. Δv_step = c · ln(W_start/W_end)     [W_end from the linear weight burn]
5. Accumulate: V_cumulative += Δv_step
```

**Note the numerical choice being made in step 1:** using the altitude at
the *start* of each step to look up Isp for that whole step is an explicit
(forward-lagged) scheme — it's simple and hand-tractable, but it means each
step's Isp is slightly stale (the vehicle is actually higher, and Isp
actually slightly better, by the step's end). A more accurate scheme would
use the midpoint or average altitude of the step. This is the same kind of
approximation-choice tradeoff numerical integrators always face — flagged
here so it's a visible decision, not a hidden one.

## Worksheet

| Step | t_start–t_end (s) | h_start (ft) | Isp (interp.) | c = Isp·g₀ | W_start | W_end | ln(W_start/W_end) | Δv_step (ft/s) | V_cumulative (ft/s) |
|------|--------------------|--------------|----------------|------------|---------|-------|--------------------|-----------------|----------------------|
| 1 | 0–13 | 0 | | | 55,000 | 51,364 | | | |
| 2 | 13–39 | 604 | | | 51,364 | 44,091 | | | |
| 3 | 39–65 | 6,485 | | | 44,091 | 36,818 | | | |
| 4 | 65–91 | 19,230 | | | 36,818 | 29,546 | | | |
| 5 | 91–117 | 37,878 | | | 29,546 | 22,273 | | | |
| 6 | 117–143 | 63,427 | | | 22,273 | 15,000 | | | |

Total ideal Δv (altitude-varying Isp) = __________ ft/s

V_bo = Total ideal Δv − 3540 ft/s = __________ ft/s

Compare to 1.0's constant-Isp result (V_bo ≈ 6284 ft/s): difference =
__________ ft/s ( ______ %)

---

## Hint (read only if you're stuck)

<details>
<summary>Step 1 — worked breakdown</summary>

- h_start = 0 → Isp = 235 s (table row, no interpolation needed)
- c = 235 × 32.174 = 7560.9 ft/s
- ln(55,000/51,364) = ln(1.0708) ≈ 0.0684
- Δv_step = 7560.9 × 0.0684 ≈ **517 ft/s**
- V_cumulative = 517 ft/s
</details>

<details>
<summary>Step 4 — worked breakdown (an interpolated Isp row)</summary>

- h_start = 19,230 ft, between table rows 0 (Isp=235) and 20,000 (Isp=246)
- Fraction = 19,230/20,000 = 0.9615
- Isp = 235 + 0.9615×(246−235) = 235 + 10.58 = **245.58 s**
- c = 245.58 × 32.174 ≈ 7901.2 ft/s
- ln(36,818/29,546) = ln(1.2461) ≈ 0.2201
- Δv_step ≈ 7901.2 × 0.2201 ≈ **1739 ft/s**
- V_cumulative = 3056.8 (through step 3) + 1739 ≈ **4796 ft/s**
</details>

---

## Answer key + tolerance

Tolerance: ±1.5% on the total (six chained slide-rule/log/interpolation
sequences compound more error than 1.0's single calculation).

| Step | h_start (ft) | Isp (s) | Δv_step (ft/s) | V_cumulative (ft/s) |
|------|--------------|---------|-----------------|----------------------|
| 1 | 0 | 235.00 | 517 | 517 |
| 2 | 604 | 235.33 | 1156 | 1673 |
| 3 | 6,485 | 238.57 | 1384 | 3057 |
| 4 | 19,230 | 245.58 | 1739 | 4796 |
| 5 | 37,878 | 252.26 | 2293 | 7089 |
| 6 | 63,427 | 258.51 | 3288 | 10,377 |

**Total ideal Δv ≈ 10,377 ft/s** (versus 9824 ft/s at constant 235 s Isp in
1.0 — about 5.6% more; less dramatic than a first guess might suggest,
because this vehicle spends its first ~65 s still fairly low and slow,
where Isp hasn't climbed much yet — most of the Isp benefit shows up in the
last two steps, which is also where most of the propellant burns).

**V_bo ≈ 10,377 − 3540 ≈ 6837 ft/s** (versus 6284 ft/s in 1.0 — about **553
ft/s, or ~8.8% higher**).

That's still not a rounding-level correction. (Optional extension, not
required for this problem: redo 1.0's Part B with this V_bo and see how
much farther the impact point moves for each flight path angle. Rough
expectation, since range scales close to V_bo² at fixed γ and h_bo: on the
order of 15–18% more range.)

## Verification step

Recompute the six-step integration with a calculator at full precision and
confirm your hand total is within tolerance. Then try the alternate
numerical scheme flagged above: instead of using each step's *starting*
altitude to look up Isp, use the *midpoint* altitude (average of the
step's start and end altitude) and recompute. Compare the two totals — the
gap between them is your estimate of the error introduced by the
explicit/lagged scheme, separate from ordinary arithmetic and interpolation
error.

If you built the numerical integrator from 1.1's verification step, this is
also a natural place to extend it: add the same Isp(h) lookup into that
integrator (replacing the constant c with c(h) = Isp(h)·g₀) and get a fully
self-consistent, altitude-varying-Isp *and* altitude-varying-loss burnout
state in one run, rather than the two separate hand studies here and in
1.1. That combined version is the real "what would the computer actually
have produced" answer — worth comparing against both hand results once you
have it.
