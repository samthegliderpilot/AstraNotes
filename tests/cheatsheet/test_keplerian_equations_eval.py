import math
import pytest

from astranotes.cheatsheet.keplerian_equations import KeplerianEquations


def _native_inputs(orb: KeplerianEquations, *, a_m, e, nu_rad, mu_m3_s2):
    """
    Build a values_dict using the *symbols from the KeplerianEquations instance*,
    in native units:
      - a, r in meters
      - angles in radians
      - mu in m^3/s^2
    """
    return {
        orb.a: float(a_m),
        orb.e: float(e),
        orb.true_anomaly: float(nu_rad),
        orb.mu: float(mu_m3_s2),
        # r/p intentionally omitted: evaluate_orbital_equations fills them
    }


def test_all_core_equations_evaluate_to_finite():
    """
    Tripwire: for a representative elliptical orbit, all current 1.0 equations
    should evaluate without crashing and return finite results.
    """
    orb = KeplerianEquations()

    # Representative elliptical orbit (Earth-ish)
    # a = 7000 km, e = 0.1, nu = 60 deg, mu = 3.986004418e14 m^3/s^2
    vals = _native_inputs(
        orb,
        a_m=7000e3,
        e=0.1,
        nu_rad=math.radians(60.0),
        mu_m3_s2=3.986004418e14,
    )

    eq_defs = [
        orb.vis_viva(),
        orb.mean_motion(),
        orb.orbital_period(),
        orb.orbital_radius(),
        orb.circular_velocity(),
        orb.escape_velocity(),
        orb.semi_latus_rectum(),
        orb.velocity_elliptical(),
        orb.sin_eccentric_anomaly_wrt_true_anomaly(),
        orb.cos_eccentric_anomaly_wrt_true_anomaly(),
        orb.eccentric_anomaly_wrt_true_anomaly(),
    ]

    for eqd in eq_defs:
        # Important: evaluate_orbital_equations mutates values_dict; isolate each run.
        local_vals = dict(vals)
        out = orb.evaluate_orbital_equations(eqd, local_vals)

        # SymPy Float or Python float are both ok
        out_f = float(out)
        assert math.isfinite(out_f), f"{eqd.name} returned non-finite value: {out!r}"


def test_eccentric_anomaly_quadrant_matches_true_anomaly_for_small_e():
    """
    Quadrant/atan2 regression guard:
    For small eccentricity, E should be close to nu (same quadrant), and atan2
    should choose the correct branch.
    """
    orb = KeplerianEquations()
    eq_E = orb.eccentric_anomaly_wrt_true_anomaly()

    mu = 3.986004418e14
    a = 7000e3

    # Pick an eccentricity that's not tiny but still mild
    e = 0.2

    # Quadrant II and III cases
    for nu_deg in (120.0, 240.0):
        nu = math.radians(nu_deg)
        vals = _native_inputs(orb, a_m=a, e=e, nu_rad=nu, mu_m3_s2=mu)
        E = float(orb.evaluate_orbital_equations(eq_E, dict(vals)))

        # Compare quadrants by comparing signs of sin/cos.
        # This catches the classic "atan vs atan2" / argument-order bug.
        assert math.copysign(1.0, math.sin(E)) == math.copysign(1.0, math.sin(nu))
        assert math.copysign(1.0, math.cos(E)) == math.copysign(1.0, math.cos(nu))

        # Also: E should be within pi of nu for reasonable e (broad sanity).
        # Normalize difference to [-pi, pi]
        diff = (E - nu + math.pi) % (2 * math.pi) - math.pi
        assert abs(diff) < 1.0, f"E too far from nu for e={e}, nu={nu_deg}deg: diff={diff}"


def test_sin_cos_of_eccentric_anomaly_identity():
    """
    Algebraic identity tripwire:
    sin(E)^2 + cos(E)^2 should be ~1 for valid inputs.
    This will catch substitution/plumbing mistakes.
    """
    orb = KeplerianEquations()
    eq_sin = orb.sin_eccentric_anomaly_wrt_true_anomaly()
    eq_cos = orb.cos_eccentric_anomaly_wrt_true_anomaly()

    vals = _native_inputs(
        orb,
        a_m=10000e3,
        e=0.5,
        nu_rad=math.radians(200.0),
        mu_m3_s2=3.986004418e14,
    )

    sinE = float(orb.evaluate_orbital_equations(eq_sin, dict(vals)))
    cosE = float(orb.evaluate_orbital_equations(eq_cos, dict(vals)))

    assert (sinE * sinE + cosE * cosE) == pytest.approx(1.0, abs=1e-10, rel=0.0)

def test_mean_motion_units_assume_radians_per_second():
    """
    If someone later changes angle 'native' away from radians, this will likely fail.
    n = sqrt(mu / a^3) in 1/s, but you tag it Angle/Time for display (rad/s).
    Numerically, for mu in m^3/s^2 and a in m, n should be ~1/s magnitude.
    """
    orb = KeplerianEquations()

    # Example: a=7000 km, mu=Earth
    vals = {
        orb.a: 7000e3,
        orb.e: 0.0,
        orb.true_anomaly: 0.0,
        orb.mu: 3.986004418e14,
    }
    n = float(orb.evaluate_orbital_equations(orb.mean_motion(), dict(vals)))
    assert n > 0.0
    assert n < 0.01  # rad/s, broad sanity for LEO-ish
