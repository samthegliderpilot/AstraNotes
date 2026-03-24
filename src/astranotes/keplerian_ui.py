from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List
import math

import ipywidgets as widgets
from IPython.display import display

from astranotes.util.units import (
    unit_registry,
    Length, Time, Angle, Mass, Dimensionless,
    Unit, Dimension,
)

from astranotes.util.equation_helpers import EquationDefinitionHtmlRender
from astranotes.cheatsheet.keplerian_equations import KeplerianEquations
@dataclass
class DimField:
    name: str
    widget: widgets.FloatText
    unit_label: widgets.Label
    container: widgets.Widget
    dimension: Dimension
    current_unit: Unit


class OrbitalMechanicsWidget:
    def __init__(self, orbital_mechanics : KeplerianEquations, equation_renderers : List[EquationDefinitionHtmlRender]):
        self._suppress_live_eval = False

        self.orbital = orbital_mechanics
        self.equation_renderers = equation_renderers

        # ---- Defaults ----
        km_unit = unit_registry.get_unit_by_abbreviation(Length, "km")
        sec_unit = unit_registry.get_unit_by_abbreviation(Time, "s")
        deg_unit = unit_registry.get_unit_by_abbreviation(Angle, "deg")
        kg_unit = unit_registry.get_unit_by_abbreviation(Mass, "kg")

        # ---- Unit selectors ----
        self.length_unit = widgets.Dropdown(
            options=[(u.name, u) for u in unit_registry[Length]],
            value=km_unit,
            description="Length Unit:",
            style={"description_width": "initial"},
        )
        self.time_unit = widgets.Dropdown(
            options=[(u.name, u) for u in unit_registry[Time]],
            value=sec_unit,
            description="Time Unit:",
            style={"description_width": "initial"},
        )
        self.angle_unit = widgets.Dropdown(
            options=[(u.name, u) for u in unit_registry[Angle]],
            value=deg_unit,
            description="Angle Unit:",
            style={"description_width": "initial"},
        )
        self.mass_unit = widgets.Dropdown(
            options=[(u.name, u) for u in unit_registry[Mass]],
            value=kg_unit,
            description="Mass Unit:",
            style={"description_width": "initial"},
        )

        self.unit_selectors = widgets.HBox([self.length_unit, self.time_unit, self.angle_unit, self.mass_unit])

        # ---- Dimensions ----
        self.mu_dimension = Length * Length * Length / (Time * Time)

        # ---- Fields registry + order ----
        self.fields: Dict[str, DimField] = {}
        self.field_order: List[str] = []

        # ---- Inputs ----
        self._add_field(
            name="a",
            description="a (semi-major axis):",
            default_value=7000.0,
            dimension=Length,
        )

        self._add_field(
            name="e",
            description="e (eccentricity):",
            default_value=0.3,
            dimension=Dimensionless,   # ✅ now a normal dimension
        )

        self._add_field(
            name="i",
            description="i (inclination):",
            default_value=0.1,
            dimension=Angle,
        )

        self._add_field(
            name="raan",
            description="RAAN:",
            default_value=1.0,
            dimension=Angle,
        )

        self._add_field(
            name="arg_pe",
            description="Arg of Periapsis:",
            default_value=0.5,
            dimension=Angle,
        )

        self._add_field(
            name="true_anomaly",
            description="True Anomaly:",
            default_value=60.0,
            dimension=Angle,
        )

        self._add_field(
            name="mu",
            description="μ (GM):",
            default_value=398600.0,
            dimension=self.mu_dimension,
        )

        # ---- Evaluate button ----
        self.evaluate_button = widgets.Button(description="Reevaluate", button_style="primary")
        self.evaluate_button.disabled = not self.inputs_are_valid()

        self.orbit_diagram_out = widgets.Output()

        # ---- Hook unit changes (single handler) ----
        self.length_unit.observe(self._on_any_unit_change, names="value")
        self.time_unit.observe(self._on_any_unit_change, names="value")
        self.angle_unit.observe(self._on_any_unit_change, names="value")
        self.mass_unit.observe(self._on_any_unit_change, names="value")

        # ---- Hook input changes for validation ----
        for name in self.field_order:
            self.fields[name].widget.observe(self.on_input_change, names="value")

        # Initialize unit caches (inputs + equations)
        self.apply_units(convert_values=False)

    # ------------------------------------------------------------------
    # Field registration / layout
    # ------------------------------------------------------------------
    def _make_labeled_widget(self, float_widget: widgets.FloatText, unit_abbr: str = "") -> tuple[widgets.Label, widgets.Widget]:
        label = widgets.HTML(value=f"<span style='font-size:1.0em'>{unit_abbr}</span>",
                                layout=widgets.Layout(width="80px"))
        container = widgets.HBox([float_widget, label])
        return label, container

    def _add_field(
        self,
        name: str,
        description: str,
        default_value: float,
        dimension: Dimension,
    ) -> None:
        float_widget = widgets.FloatText(value=default_value, description=description)

        env = self.get_selected_units()
        unit = unit_registry.get_unit_for_dimension(dimension, env)

        label, container = self._make_labeled_widget(float_widget, unit.pretty_abbreviation())

        self.fields[name] = DimField(
            name=name,
            widget=float_widget,
            unit_label=label,
            container=container,
            dimension=dimension,
            current_unit=unit,
        )

        self.field_order.append(name)

    def get_field_container_list(self) -> List[widgets.Widget]:
        return [self.fields[name].container for name in self.field_order]

    # ------------------------------------------------------------------
    # Unit environment
    # ------------------------------------------------------------------
    def get_selected_units(self) -> Dict[Dimension, Unit]:
        return {
            unit_registry.LENGTH: self.length_unit.value,
            unit_registry.TIME: self.time_unit.value,
            unit_registry.ANGLE: self.angle_unit.value,
            unit_registry.MASS: self.mass_unit.value,
            unit_registry.DIMENSIONLESS: unit_registry.get_unit_by_abbreviation(Dimensionless, ""),
        }

    # ------------------------------------------------------------------
    # Central unit application: inputs + equations
    # ------------------------------------------------------------------
    def apply_units(self, convert_values: bool = True) -> None:
        self._suppress_live_eval = True
        try:
            env = self.get_selected_units()

            # Update input fields (including dimensionless)
            for name in self.field_order:
                field = self.fields[name]

                old_unit = field.current_unit
                new_unit = unit_registry.get_unit_for_dimension(field.dimension, env)

                if convert_values and old_unit != new_unit:
                    native_value = old_unit.to_native(field.widget.value)
                    field.widget.value = new_unit.from_native(native_value)

                field.unit_label.value = new_unit.pretty_abbreviation()
                field.current_unit = new_unit

            # Update equation renderer unit caches
            for renderer in self.equation_renderers:
                dim = renderer.equation.dimension
                unit = unit_registry.get_unit_for_dimension(dim, env)
                renderer.set_display_unit(unit)
        finally:
            self._suppress_live_eval = False

    def _on_any_unit_change(self, change) -> None:
        if change.get("name") != "value":
            return
        self.apply_units(convert_values=True)
        self.evaluate_and_display()

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------
    def get_values_dict(self) -> Dict:
        f = self.fields
        return {
            self.orbital.a: f["a"].current_unit.to_native(f["a"].widget.value),
            self.orbital.e: f["e"].current_unit.to_native(f["e"].widget.value),  # still unitless, noop
            self.orbital.i: f["i"].current_unit.to_native(f["i"].widget.value),
            self.orbital.raan: f["raan"].current_unit.to_native(f["raan"].widget.value),
            self.orbital.arg_pe: f["arg_pe"].current_unit.to_native(f["arg_pe"].widget.value),
            self.orbital.true_anomaly: f["true_anomaly"].current_unit.to_native(f["true_anomaly"].widget.value),
            self.orbital.mu: f["mu"].current_unit.to_native(f["mu"].widget.value),
        }

    def evaluate_and_display(self) -> None:
        native_values = self.get_values_dict()

        # Evaluate everything once
        evaluated = self.orbital.evaluate_my_equations(native_values)

        for renderer in self.equation_renderers:
            try:
                native_val = evaluated.get(renderer.equation, math.nan)
                display_val = renderer.convert_native_to_display(native_val)
                renderer.update_value(display_val)
            except Exception:
                renderer.update_value(math.nan)

        # Update diagram last
        self.update_orbit_diagram(native_values)


    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------
    def display(self) -> None:
        display(self.unit_selectors)
        for w in self.get_field_container_list():
            display(w)
        display(self.evaluate_button)

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    def validate_widget(self, widget: widgets.FloatText, validate_func: Callable[[float], bool]) -> bool:
        val = widget.value
        ok = True

        if val is None:
            ok = False
        else:
            try:
                ok = bool(validate_func(val))
            except Exception:
                ok = False

        if ok:
            widget.remove_class("astro-invalid")
        else:
            widget.add_class("astro-invalid")

        return ok


    def inputs_are_valid(self) -> bool:
        f = self.fields
        validators = {
            f["a"].widget: lambda v: True,
            f["mu"].widget: lambda v: v > 0,
            f["i"].widget: lambda v: True,
            f["raan"].widget: lambda v: True,
            f["arg_pe"].widget: lambda v: True,
            f["true_anomaly"].widget: lambda v: True,
            f["e"].widget: lambda v: 0 <= v,
        }

        all_valid = True
        for widget, validator in validators.items():
            if not self.validate_widget(widget, validator):
                all_valid = False
        return all_valid

    def on_input_change(self, change) -> None:
        valid = self.inputs_are_valid()
        self.evaluate_button.disabled = not valid

        if self._suppress_live_eval:
            return

        if valid:
            self.evaluate_and_display()

    def update_orbit_diagram(self, native_values: Dict) -> None:
        """
        Render the orbit diagram using native (SI) values.
        Expects:
        - a in native length units
        - e dimensionless
        - true_anomaly in radians
        """
        # Import here to avoid hard dependency at module import time
        from IPython.display import display, HTML

        a = float(native_values[self.orbital.a])
        e = float(native_values[self.orbital.e])
        nu = float(native_values[self.orbital.true_anomaly])  # radians

        self.orbit_diagram_out.clear_output(wait=True)
        with self.orbit_diagram_out:
            # orbit_diagram_svg is the drawsvg function we defined earlier
            dwg = orbit_diagram_svg(a=a, e=e, nu=nu)
            display(dwg)


def orbit_diagram_svg(
    a, e, nu=None, *,
    size=520, margin=0.15,
    show_axes=True, show_labels=True,
    show_nu_arc=True,
    nu_arc_mode="signed",        # "signed" or "minor"
    pixel_padding=32,
    stroke_width=2,
    show_satellite=True,
    satellite_size_px=10,
    rmax_factor=10.0,            # for open orbits: plot out to rmax_factor * rp
    N=600,
    e_tol=1e-10,
):
    """
    Conic-section orbit diagram (ellipse/parabola/hyperbola) in SVG via drawsvg.

    Convention:
      - Focus (central body) at (0,0)
      - Periapsis on +x axis at (+rp, 0)
      - True anomaly ν measured from +x toward +y (CCW, in standard math sense)

    Inputs:
      - For ellipse (e<1): 'a' is semi-major axis (a>0 recommended)
      - For hyperbola (e>1): 'a' is |semi-major axis| (can be negative too; magnitude is used)
      - For parabola (e==1): 'a' is interpreted as periapsis distance rp

    Open-orbit plotting:
      - Hyperbolic/parabolic orbits go to infinity, so we plot a finite branch out to r = rmax_factor*rp.
    """
    import math
    import drawsvg as draw

    if e < 0:
        raise ValueError("Eccentricity e must be >= 0.")
    if a == 0:
        raise ValueError("Parameter 'a' must be nonzero (for parabola, use a=rp > 0).")

    # --- Classify conic & compute p ---
    if abs(e - 1.0) <= e_tol:
        conic = "parabola"
        rp = float(a)
        if rp <= 0:
            raise ValueError("For parabolic case (e≈1), interpret a as periapsis distance rp; require a>0.")
        p = 2.0 * rp
    elif e < 1.0:
        conic = "ellipse"
        if a < 0:
            # allow but unusual; geometry still works using |a|
            a_use = abs(a)
        else:
            a_use = float(a)
        p = a_use * (1.0 - e * e)
        rp = p / (1.0 + e)
    else:
        conic = "hyperbola"
        a_use = abs(a)
        p = a_use * (e * e - 1.0)
        rp = p / (1.0 + e)

    # Utility: r(nu) for this conic
    def r_of(nu_val):
        denom = 1.0 + e * math.cos(nu_val)
        if denom <= 0:
            return float("inf")
        return p / denom

    # Validate current nu is on the physical branch
    denom_now = 1.0 + e * math.cos(nu)
    if denom_now <= 0:
        raise ValueError(
            "True anomaly v is outside the valid branch for this open orbit "
            "(1 + e cos(v) <= 0). Choose v closer to periapsis."
        )

    # Current position
    r_now = p / denom_now
    xnu = r_now * math.cos(nu)
    ynu = r_now * math.sin(nu)

    # --- Choose plotting anomaly range ---
    if conic == "ellipse":
        nu_min, nu_max = 0.0, 2.0 * math.pi
    else:
        # We plot until r reaches rmax = rmax_factor * rp
        rmax = max(rmax_factor * rp, 1.5 * rp)

        # Solve for nu where r = rmax:
        # r = p/(1+e cos nu) => 1+e cos nu = p/r => cos nu = (p/r - 1)/e
        if conic == "parabola":
            # e == 1
            cos_lim = (p / rmax) - 1.0
        else:
            cos_lim = (p / rmax - 1.0) / e

        # clamp due to numeric edge cases
        cos_lim = max(-1.0, min(1.0, cos_lim))
        nu_plot_lim = math.acos(cos_lim)

        # Also respect the asymptote limit (where denom=0) for hyperbola, and pi for parabola
        if conic == "hyperbola":
            nu_inf = math.acos(-1.0 / e)  # denom -> 0 at this |nu|
            nu_plot_lim = min(nu_plot_lim, nu_inf - 1e-4)
        else:
            # parabola tends to infinity at nu = pi
            nu_plot_lim = min(nu_plot_lim, math.pi - 1e-4)

        nu_min, nu_max = -nu_plot_lim, +nu_plot_lim

    # Sample points in polar form around the focus
    pts_xy = []
    for i in range(N + 1):
        t = nu_min + (nu_max - nu_min) * i / N
        denom = 1.0 + e * math.cos(t)
        if denom <= 0:
            continue
        r = p / denom
        x = r * math.cos(t)
        y = r * math.sin(t)
        pts_xy.append((x, y))

    if len(pts_xy) < 5:
        raise ValueError("Could not generate enough points to draw the orbit (range too small or invalid).")

    # --- Scaling to pixels based on plotted extents ---
    xs = [x for x, _ in pts_xy] + [0.0, xnu]
    ys = [y for _, y in pts_xy] + [0.0, ynu]
    max_extent = max(max(abs(x) for x in xs), max(abs(y) for y in ys))
    R = max_extent * (1.0 + margin)

    half = size / 2
    usable_half = max(half - pixel_padding, 10)
    scale = usable_half / R

    def tosvg(x, y):
        return (x * scale, -y * scale)  # invert y so +y is up

    dwg = draw.Drawing(size, size, origin='center')

    # --- Optional axes ---
    if show_axes:
        ax_len = R * scale
        dwg.append(draw.Line(-ax_len, 0, ax_len, 0, stroke='rgba(0,0,0,0.15)', stroke_width=1))
        dwg.append(draw.Line(0, -ax_len, 0, ax_len, stroke='rgba(0,0,0,0.15)', stroke_width=1))

    # --- Draw orbit path ---
    path = draw.Path(stroke='black', stroke_width=stroke_width, fill='none')
    X0, Y0 = tosvg(*pts_xy[0])
    path.M(X0, Y0)
    for (x, y) in pts_xy[1:]:
        X, Y = tosvg(x, y)
        path.L(X, Y)
    dwg.append(path)

    # --- Focus (central body) ---
    fx, fy = tosvg(0, 0)
    dwg.append(draw.Circle(fx, fy, 6, fill='black'))

    # --- Periapsis point ---
    px, py = tosvg(rp, 0)
    dwg.append(draw.Circle(px, py, 4, fill='black'))

    # --- Apoapsis point (ellipse only) ---
    if conic == "ellipse":
        ra = p / (1.0 - e)  # = a(1+e)
        ax, ay = tosvg(-ra, 0)
        dwg.append(draw.Circle(ax, ay, 4, fill='black'))

    # --- Radius vector to current ν ---
    x1, y1 = tosvg(xnu, ynu)
    dwg.append(draw.Line(fx, fy, x1, y1, stroke='black', stroke_width=stroke_width))

    # --- Satellite marker (star) ---
    if show_satellite:
        def star_points(cx, cy, r_outer, r_inner, n=5, rotation=-math.pi/2):
            pts = []
            for k in range(2 * n):
                ang = rotation + k * math.pi / n
                rr = r_outer if (k % 2 == 0) else r_inner
                pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
            return pts

        pts = star_points(x1, y1, satellite_size_px, satellite_size_px * 0.45)
        star = draw.Path(stroke='black', stroke_width=1.2, fill='white')
        sx0, sy0 = pts[0]
        star.M(sx0, sy0)
        for (xx, yy) in pts[1:]:
            star.L(xx, yy)
        star.Z()
        dwg.append(star)

    # --- ν arc (with correct direction) ---
    if show_nu_arc:
        nu_norm = nu % (2 * math.pi)

        if nu_arc_mode == "minor":
            nu_draw = nu_norm if nu_norm <= math.pi else (2 * math.pi - nu_norm)
            # With y inverted, SVG sweep is opposite of math CCW:
            sweep = 0 if nu_norm <= math.pi else 1
        elif nu_arc_mode == "signed":
            nu_draw = nu_norm
            sweep = 0  # <-- correct after y inversion
        else:
            raise ValueError('nu_arc_mode must be "signed" or "minor".')

        if nu_draw > 1e-6:
            arc_r = max(0.25 * rp, 0.10 * (rp + 1e-12))

            arx0, ary0 = tosvg(arc_r, 0)
            arx1, ary1 = tosvg(arc_r * math.cos(nu_draw), arc_r * math.sin(nu_draw))

            large_arc = 1 if nu_draw > math.pi else 0

            arc = draw.Path(stroke='black', stroke_width=stroke_width, fill='none')
            arc.M(arx0, ary0)
            arc.A(arc_r * scale, arc_r * scale, 0, large_arc, sweep, arx1, ary1)
            dwg.append(arc)

            if show_labels:
                mid = nu_draw / 2
                lx, ly = tosvg(arc_r * math.cos(mid), arc_r * math.sin(mid))
                dwg.append(draw.Text('ν', 16, lx, ly, text_anchor='middle', dominant_baseline='middle'))

    # --- Labels ---
    if show_labels:
        # Offsets in physics units so text moves sensibly with scaling
        label_off = 0.08 * max(rp, 1e-12)

        Lx, Ly = tosvg(0 + label_off, 0 + label_off)
        dwg.append(draw.Text('Focus', 12, Lx, Ly, text_anchor='start'))

        Lx, Ly = tosvg(rp + label_off, 0 + label_off)
        dwg.append(draw.Text('Periapsis', 12, Lx, Ly, text_anchor='start'))

        if conic == "ellipse":
            ra = p / (1.0 - e)
            Lx, Ly = tosvg(-ra - label_off, 0 + label_off)
            dwg.append(draw.Text('Apoapsis', 12, Lx, Ly, text_anchor='end'))
        else:
            # Optional: label the orbit type for open conics
            # Place near top-left of the drawing box
            tx, ty = tosvg(-0.9 * max_extent, 0.9 * max_extent)
            dwg.append(draw.Text(conic.capitalize(), 12, tx, ty, text_anchor='start'))

    return dwg
