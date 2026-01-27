import sympy as sy

from astranotes.cheatsheet.keplerian_equations import KeplerianEquations
from astranotes.util.equation_helpers import EquationGroup
from astranotes.cheatsheet.render_latex_sources import render_sources_latex


def _make_equation_groups():
    orb = KeplerianEquations()
    equation_groups = [
        EquationGroup("General Orbital Equations", [
            orb.vis_viva(),
            orb.mean_motion(),
            orb.orbital_period(),
            orb.semi_latus_rectum(),
            orb.velocity_elliptical(),
        ]),
        EquationGroup("Elliptical Orbit Equations", [
            orb.orbital_radius(),
            orb.sin_eccentric_anomaly_wrt_true_anomaly(),
            orb.cos_eccentric_anomaly_wrt_true_anomaly(),
            orb.eccentric_anomaly_wrt_true_anomaly(),
        ]),
        EquationGroup("Circular Orbit Equations", [
            orb.circular_velocity(),
        ]),
        EquationGroup("Parabolic Equations", [
            orb.escape_velocity(),
        ]),
    ]
    return equation_groups


def test_all_equations_render_to_latex_without_error():
    """
    Sanity test: sympy.latex() succeeds for every equation expression.
    (Doesn't assert exact strings; it's a tripwire for rendering regressions.)
    """
    groups = _make_equation_groups()

    for g in groups:
        for eqd in g.equations:
            s = sy.latex(eqd.expr)  # should not throw
            assert isinstance(s, str)
            assert len(s.strip()) > 0
            # common "oops" tripwires
            assert "None" not in s


def test_sources_latex_renderer_basic_structure():
    """
    Sanity test: Sources LaTeX renderer emits expected structure.
    """
    groups = _make_equation_groups()
    lines = render_sources_latex(groups)

    assert isinstance(lines, list)
    assert len(lines) > 0

    joined = "\n".join(lines)

    # expected top header
    assert r"\section*{Sources}" in joined

    # grouped-by-source blocks should include itemize
    assert r"\begin{itemize}" in joined
    assert r"\end{itemize}" in joined

    # basic "no placeholders" sanity
    assert "None" not in joined

    # should contain at least one known equation name (bolded)
    assert r"\textbf{Vis-Viva}" in joined


def test_sources_latex_renderer_escapes_problem_characters():
    """
    Regression-style sanity: if an equation name or source has characters like '_' or '%',
    renderer should escape them. This test is mild: it just ensures LaTeX doesn't contain
    raw unescaped underscores from known names (your current names include v_{circ} in text).
    """
    groups = _make_equation_groups()
    lines = render_sources_latex(groups)
    joined = "\n".join(lines)

    # Your equation name includes 'Circular Velocity ($v_{circ}$)'
    # Underscore should appear escaped in text mode if present.
    # (We don't assert exact formatting; just ensure no raw '_circ' leaks unescaped in text.)
    assert "_{circ}" not in joined  # would indicate raw text underscore usage
