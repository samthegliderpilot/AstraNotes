# Stage 1.0 — Range Table Targeting (Powered Ascent + Ballistic Arc)

**Era:** Redstone/Mercury-Redstone class, ~1961 (fictional program).
**Prerequisite:** Phase 0 (all four drills).
**Depends on:** 0.0, 0.1 (slide rule, table interpolation) directly; 0.3
(triangle solving) indirectly, for the same "expect more than one valid
answer" habit.

This version deliberately simplifies two things — a constant Isp and a
given, un-derived loss budget — to keep the first Stage 1 problem to about
half an hour. For the harder, more complete version of this same ascent
(where both of those are derived rather than assumed), see **1.1** (liftoff
sanity check + gravity-turn loss, first-principles) and **1.2**
(non-constant Isp, full afternoon).

## Narrative frame

You're the flight dynamics engineer for **Project Arrowhead**, a fictional
1961 suborbital test program flying the **Redwing-3** booster out of a
fictional coastal range. Range Safety has assigned tomorrow's flight an
impact zone centered **210.0 nautical miles** downrange of the pad, inside a
larger safety corridor. Your job: using the vehicle's known performance and
a burnout altitude fixed by the guidance program, build the range table for
this vehicle and tell the pad crew what burnout flight path angle(s) will
put the impact where Range Safety wants it — and confirm there's more than
one way to get there.

## Given data

**Vehicle performance (powered ascent):**
- Gross liftoff weight, W₀ = 55,000 lbf
- Propellant weight burned to cutoff, Wₚ = 40,000 lbf
- Effective specific impulse, Iₛₚ = 235 s (treated as constant — real
  engines vary Iₛₚ with altitude, but a single effective value is the
  period-standard simplification for a first-pass performance estimate;
  see 1.2 for the non-constant version)
- Burn time, t_b = 143 s
- Gravity + drag loss allowance, Δv_losses = 3540 ft/s (derived in 1.1 from
  a first-principles gravity-turn/drag integration — treat it as a given
  here, the way a real FDO would receive it from the trajectory design
  group, having not run that study themselves)

**Ballistic arc:**
- Burnout altitude, h_bo = 100,000 ft (fixed by the guidance program,
  independent of flight path angle — this matches the altitude 1.1's
  gravity-turn study actually converges to, which is not a coincidence:
  the pitch program in 1.1 was designed to hit it)
- Standard gravity, g = 32.174 ft/s² (treated as constant with altitude —
  valid at these altitudes to within a few percent, and consistent with the
  flat, non-rotating Earth model used throughout this problem)
- Assume impact at sea level (flat, non-rotating Earth — no curvature
  correction at this range; that correction is flagged as a natural
  extension for a later, longer-range stage)

**Target:** impact range = 210.0 nautical miles from the pad (1 nm = 6076.12 ft)

## Authentic method + reference material

**Powered ascent — Tsiolkovsky rocket equation** (Tsiolkovsky, 1903; in
active use by every rocket engineer of this era):

```
Δv_ideal = c · ln(W₀/W₁)          c = Iₛₚ · g₀
V_bo = Δv_ideal − Δv_losses
```

where W₁ = W₀ − Wₚ is burnout weight.

**Ballistic arc — flat-Earth, uniform-gravity vacuum trajectory.** This is
the same mathematics behind WWII- and V2-era artillery/rocket range tables,
which the Redstone program inherited directly through von Braun's team. It
is *not* the full spherical-Earth treatment (Bate, Mueller & White, Ch. 4,
"Ballistic Missile Trajectories," which treats the free-flight arc as a
conic with one focus at Earth's center) — that's intentionally saved for a
later, longer-range stage, since Stage 1 is scoped to stay out of orbital
mechanics. At suborbital ranges like this one, the flat-Earth form is an
accurate and period-appropriate simplification, not a shortcut that
sacrifices authenticity.

With burnout velocity V_bo at flight path angle γ (measured above local
horizontal) and altitude h_bo:

```
v_y0 = V_bo · sin(γ)        v_x0 = V_bo · cos(γ)

t_impact = [v_y0 + √(v_y0² + 2·g·h_bo)] / g

R = v_x0 · t_impact

h_apex = h_bo + v_y0² / (2g)
```

**The graphical range-table method:** rather than solving R(γ) = 210.0 nm
directly (it's not algebraically clean to invert), compute R for a spread of
γ values, sketch R vs. γ by hand, and read the answer(s) off the curve. This
is exactly how real range tables were built and used operationally — a
chart, not an equation to invert on demand. Expect the curve to be
non-monotonic near its peak, which means **two** valid flight path angles
can produce the same range: a flatter, faster-arriving trajectory and a more
lofted one. Same ambiguity in spirit as the SSA triangle case in 0.3 — don't
be surprised by it, and don't discard one root as "wrong."

## Worksheet

**Part A — Burnout velocity**

| Quantity | Value |
|---|---|
| W₁ = W₀ − Wₚ | |
| c = Iₛₚ · g₀ | |
| W₀/W₁ | |
| ln(W₀/W₁) | |
| Δv_ideal = c·ln(W₀/W₁) | |
| V_bo = Δv_ideal − Δv_losses | |

**Part B — Range table.** Fill in for each γ. Carry v_y0² through in full
(you'll reuse it for the apex altitude too — don't recompute).

| γ | sin γ | cos γ | v_y0 | v_x0 | v_y0² | t_impact (s) | R (ft) | R (nm) | h_apex (ft) |
|---|-------|-------|------|------|-------|---------------|--------|--------|-------------|
| 30° | | | | | | | | | |
| 35° | | | | | | | | | |
| 40° | | | | | | | | | |
| 45° | | | | | | | | | |
| 50° | | | | | | | | | |
| 55° | | | | | | | | | |

**Part C — Graphical solution.** Plot R (nm, vertical axis) vs. γ
(horizontal axis, 30°–55°) on the grid below using your six points from
Part B. Draw a horizontal line at R = 210.0 nm and read off both crossings.

<!-- printable-grid: title="R vs. gamma" xlabel="gamma (deg)" xmin=28 xmax=57
     xmajor=5 xminor=1 ylabel="R (nm)" ymin=195 ymax=220 ymajor=5 yminor=1 -->

Low-angle solution: γ = __________°
High-angle solution: γ = __________°

---

## Hint (read only if you're stuck)

<details>
<summary>Part A — worked breakdown</summary>

- W₁ = 55,000 − 40,000 = **15,000 lbf**
- c = 235 × 32.174 = **7560.9 ft/s**
- W₀/W₁ = 55,000/15,000 = **3.6667**
- ln(3.6667) ≈ **1.2993** — via log₁₀ on the L scale (or table) × 2.302585:
  log₁₀(3.6667) ≈ 0.56425, × 2.302585 ≈ 1.2993
- Δv_ideal = 7560.9 × 1.2993 ≈ **9824 ft/s**
- V_bo = 9824 − 3540 = **6284 ft/s**
</details>

<details>
<summary>Part B, γ = 45° row — worked breakdown</summary>

- sin 45° = cos 45° = 0.70711
- v_y0 = v_x0 = 6284 × 0.70711 ≈ **4443 ft/s**
- v_y0² ≈ **19,750,000** ft²/s²
- 2·g·h_bo = 2 × 32.174 × 100,000 = **6,434,800** ft²/s²
- v_y0² + 2·g·h_bo ≈ 26,184,800 → √ ≈ **5117** ft/s
- t_impact = (4443 + 5117)/32.174 ≈ **297.2 s**
- R = 4443 × 297.2 ≈ 1,320,300 ft → **≈ 217.3 nm**
- h_apex = 100,000 + 19,750,000/64.348 ≈ **406,900 ft**

Chain the multiply/divide/sqrt steps on the slide rule without resetting
where you can — this row has five slide-rule operations back to back, which
is exactly the kind of chaining 0.0 Drill 1, Problem 9 was building toward.
</details>

---

## Answer key + tolerance

**Part A:** V_bo ≈ 6284 ft/s (tolerance: ±60 ft/s, ~1%)

**Part B** (tolerance: ±0.5% on R, ±1% on h_apex)

| γ | R (nm) | h_apex (ft) |
|---|--------|-------------|
| 30° | 199.9 | 253,400 |
| 35° | 211.0 | 301,900 |
| 40° | 216.9 | 353,600 |
| 45° | 217.3 | 406,900 |
| 50° | 211.9 | 460,100 |
| 55° | 200.7 | 511,800 |

The curve peaks between 40° and 45° rather than exactly at 45° — that's the
real effect of burnout altitude being nonzero (launching from 100,000 ft
down to a sea-level impact isn't quite symmetric with the textbook
flat-ground case). Small effect here since h_bo is small compared to R, but
it's genuine, not noise.

**Part C** (tolerance: ±1.5°, consistent with reading a hand-drawn chart)
- Low-angle solution: γ ≈ **34.5°**
- High-angle solution: γ ≈ **51.1°**

Both are legitimate answers to "what flight path angle hits 210 nm" — tell
the pad crew there's a choice to make (faster/flatter vs. more lofted, with
a correspondingly lower or higher apex), not that there's one right number.

## Verification step

Recompute Part B in STK or your Astrogator clone as a simple flat, non-
rotating-Earth vacuum trajectory from the same burnout state, and confirm
your six hand-computed ranges land within tolerance. Then find both γ
solutions for R = 210.0 nm numerically (bisection or Newton's method against
R(γ) − 210.0 = 0) and compare against your graphically-read values — that
gap is your graphical-reading error budget, separate from your arithmetic
error budget from Part B.

As a bonus check worth doing once: rerun the 45° case in STK using a
spherical, rotating Earth instead of the flat-Earth model used here, and see
how far the actual impact point shifts. At ~200 nm this should be a modest
correction — worth having the number in hand before a later stage pushes
range far enough that the flat-Earth assumption stops being defensible.
