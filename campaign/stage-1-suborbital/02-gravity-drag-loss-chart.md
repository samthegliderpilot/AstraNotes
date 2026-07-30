# Stage 1.1 — Liftoff Check & Gravity-Turn Loss (First Principles)

**Era:** Redstone/Mercury-Redstone class, ~1961 (fictional program), continuing Project Arrowhead.
**Target time:** ~1.5 hours.
**Prerequisite:** Stage 1.0 (Range Table Targeting).

## Why this problem exists

1.0 handed you Δv_losses as a given number, the way a real FDO would receive
it from the trajectory design group. This problem *is* that group's work:
where the number actually comes from, and — as a bonus you didn't ask for —
a check on whether the vehicle spec you were handed even makes sense.

## Part 1 — Sanity-check the vehicle

Before modeling anything about the ascent, check the most basic thing: can
this vehicle actually leave the pad? A rocket needs thrust greater than its
own weight at ignition, full stop.

**Candidate spec** (proposed by the vehicle design group): W₀ = 66,000 lbf,
Wₚ = 40,000 lbf burned over t_b = 143 s, Iₛₚ = 235 s.

```
ẇ = Wₚ / t_b                (weight flow rate)
T = ẇ · Iₛₚ                 (thrust, from the definition of Iₛₚ)
T/W₀ = liftoff thrust-to-weight ratio
```

Compute T/W₀ for the original spec. A real booster of this class typically
lifts off around T/W₀ ≈ 1.2; anything at or below 1.0 cannot lift off at
all.

**What you should find:** T/W₀ ≈ 0.996. This vehicle cannot fly. It was
never caught because 1.0's calculation only used the *integrated* rocket
equation (total Δv from the mass ratio), which doesn't care about
instant-by-instant thrust — a completely reasonable thing to miss if you
never build a real time-history of the flight, which is exactly what 1.0
didn't do and this problem does.

## Part 2 — Corrected data, and the real ascent

The propulsion group reviewed the spec and traces the error to an
overstated liftoff weight. **Corrected value: W₀ = 55,000 lbf** (Wₚ, t_b,
and Iₛₚ unchanged). Recompute T/W₀ and confirm it's now reasonable
(target: ~1.2).

With the corrected vehicle, the guidance group ran a preliminary
trajectory-shaping study — the kind of repetitive, closely-spaced numerical
integration that, even in 1961, nobody did by hand end-to-end. That's the
"very limited computer" moment for this problem: below is a coarse extract
from that run (7 points instead of the hundreds the real integration would
use), given to you the way a trajectory analyst would actually receive it.

**Programmed pitch maneuver:** the guidance program holds the vehicle
vertical (γ = 90°) until t_p = 13.0 s, then flies a prescribed pitch profile
that eases toward 15° by burnout. (The exact formula isn't needed for this
part — it's given in the Verification step below, when you build your own
integrator.)

**Given — trajectory checkpoints** (from the preliminary run):

| t (s) | V (ft/s) | γ (°) | h (ft) |
|-------|----------|-------|--------|
| 0 | 0.0 | 90.0 | 0 |
| 13 | 98.7 | 90.0 | 604 |
| 39 | 499.8 | 46.53 | 6,485 |
| 65 | 1,282.9 | 28.25 | 19,230 |
| 91 | 2,372.1 | 20.57 | 37,878 |
| 117 | 3,888.0 | 17.34 | 63,427 |
| 143 | 6,284.2 | 15.98 | 100,235 |

**Given — vehicle aerodynamic data** (from wind tunnel testing): effective
drag parameter Cd·A = 8.0 ft².

**Given — atmosphere model:** isothermal exponential atmosphere (the same
simplified model Bate, Mueller & White use for atmospheric-drag perturbation
work) —

```
ρ(h) = ρ₀ · exp(−h/H)          ρ₀ = 0.0023769 slug/ft³, H = 23,800 ft
```

## Authentic method + reference material

**Drag force:** D = ½·ρ(h)·V²·(Cd·A) — standard aerodynamic drag equation.

**Loss-rate bookkeeping.** At any instant, gravity is costing you g₀·sin(γ)
of your rocket's Δv-generating capability, and drag is costing you
(D/W)·g₀. This is genuine physics, not an artifact of this drill — it comes
directly from the same equation of motion (dV/dt = c·ẇ/W − D·g₀/W − g₀sinγ)
that a full trajectory integration solves.

**The hand technique:** compute both loss rates at each of the seven given
checkpoints, then integrate (trapezoidal — average the rate at each pair of
adjacent checkpoints, multiply by the time between them, sum) to get total
gravity loss and total drag loss over the burn. This is *not* the same as
integrating the full coupled trajectory yourself — that's a much harder,
numerically unstable problem by hand (ask your instructor about the war
story where the first attempt at this diverged spectacularly with only
five hand-sized steps). Using given trajectory checkpoints and just
integrating the loss *rates* sidesteps that entirely, and — surprisingly —
still gets you a very good answer, as you'll see in Verification.

## Worksheet

**Part 1 — original spec:**

| Quantity | Value |
|---|---|
| ẇ = Wₚ/t_b | |
| T = ẇ·Iₛₚ | |
| T/W₀ (original, 66,000 lbf) | |

**Part 2a — corrected spec:**

| Quantity | Value |
|---|---|
| T/W₀ (corrected, 55,000 lbf) | |

**Part 2b — loss-rate table.** Fill in for each checkpoint.

| t (s) | V | h | γ | W(t) | ρ(h) | D | grav. rate = g₀sinγ | drag rate = (D/W)g₀ |
|-------|---|---|---|------|------|---|----------------------|------------------------|
| 0 | 0.0 | 0 | 90.0° | | | | | |
| 13 | 98.7 | 604 | 90.0° | | | | | |
| 39 | 499.8 | 6,485 | 46.53° | | | | | |
| 65 | 1,282.9 | 19,230 | 28.25° | | | | | |
| 91 | 2,372.1 | 37,878 | 20.57° | | | | | |
| 117 | 3,888.0 | 63,427 | 17.34° | | | | | |
| 143 | 6,284.2 | 100,235 | 15.98° | | | | | |

**Part 2c — trapezoidal integration.**

| Interval | Δt (s) | Avg grav. rate × Δt | Avg drag rate × Δt |
|----------|--------|----------------------|------------------------|
| 0–13 | 13 | | |
| 13–39 | 26 | | |
| 39–65 | 26 | | |
| 65–91 | 26 | | |
| 91–117 | 26 | | |
| 117–143 | 26 | | |

Total gravity loss = __________ ft/s
Total drag loss = __________ ft/s
Total Δv_losses = __________ ft/s

Using Δv_ideal = 9824 ft/s (from 1.0's Part A, same vehicle): V_bo = __________ ft/s

---

## Hint (read only if you're stuck)

<details>
<summary>Part 1 — worked breakdown</summary>

- ẇ = 40,000/143 = **279.72 lbf/s**
- T = 279.72 × 235 = **65,734 lbf**
- T/W₀ = 65,734/66,000 = **0.996**

Under 1.0 — this vehicle physically cannot leave the pad.
</details>

<details>
<summary>Part 2b, t = 39 s row — worked breakdown</summary>

- W(39) = 55,000 − 279.72×39 = **44,091 lbf**
- ρ(6,485) = 0.0023769 × exp(−6485/23800) = 0.0023769 × 0.7546 ≈ **0.001794 slug/ft³**
- D = 0.5 × 0.001794 × 499.8² × 8.0 ≈ **1,791 lbf** (small rounding vs. the
  reference value below — normal for a hand-carried exponential)
- grav rate = 32.174 × sin(46.53°) = 32.174 × 0.7254 ≈ **23.34**
- drag rate = (1,791/44,091) × 32.174 ≈ **1.31**
</details>

---

## Answer key + tolerance

**Part 1:** T/W₀ ≈ **0.996** — vehicle cannot lift off.

**Part 2a:** T/W₀ ≈ **1.195** — good, matches a typical period booster.

**Part 2b/2c** (tolerance: ±3% per row — the exponential atmosphere term is
the least forgiving thing to carry by hand here):

| Interval | Grav. contribution (ft/s) | Drag contribution (ft/s) |
|----------|----------------------------|----------------------------|
| 0–13 | 418.3 | 0.4 |
| 13–39 | 721.8 | 17.9 |
| 39–65 | 501.5 | 96.4 |
| 65–91 | 345.0 | 233.4 |
| 91–117 | 271.6 | 342.1 |
| 117–143 | 239.9 | 343.0 |

**Total gravity loss ≈ 2498 ft/s**
**Total drag loss ≈ 1033 ft/s**
**Total Δv_losses ≈ 3531 ft/s**

**V_bo ≈ 9824 − 3531 ≈ 6293 ft/s**

That's a genuinely large number in absolute terms: this vehicle spends over
a third of its ideal Δv capability fighting gravity and drag, which is
realistic for a steep suborbital profile that has to reach 100,000 ft.

## Verification step

This is the interesting one. Build your own numerical integrator — a short
Python script is fine (this is the "modern FORTRAN deck" for this exercise;
what matters is the technique, not the language) — using the full coupled
equations of motion rather than the given checkpoints:

```
dV/dt = c·ẇ/W(t) − [D(V,h)/W(t)]·g₀ − g₀·sin(γ(t))
dh/dt = V·sin(γ(t))

γ(t) = 90°                              for t < 13
γ(t) = 15° + 75°·exp[−(t−13)/30]        for t ≥ 13
```

with the same W(t), D(V,h), and atmosphere model as above. Integrate from
t=0 to t=143 with a fine time step (RK4 recommended, but even a fine-step
Euler will converge). You should get approximately:

- **V_bo ≈ 6284 ft/s**
- **h_bo ≈ 100,235 ft**
- **Implied total loss ≈ 3540 ft/s**

Compare three numbers against each other: your hand/checkpoint estimate
(≈6293 ft/s), your own fine-integration run, and the reference values above.
The checkpoint method should land within about 0.2% of the fine integration
— which is a genuinely useful result: it means a handful of well-chosen
checkpoints from an expensive computer run let a human do fast, accurate
follow-on work (loss budgets, sensitivity checks) without re-running the
whole integration by hand. That division of labor — computer for the fine
trajectory, hand/slide-rule for everything built on top of it — is close to
exactly how this worked in practice by the time Redwing-3's real
counterparts were flying.
