from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List
import math

import ipywidgets as widgets
from IPython.display import display

from astrocalc.util.units import (
    unit_registry,
    Length, Time, Angle, Mass, Dimensionless,
    Unit, Dimension,
)

from astrocalc.util.equation_helpers import EquationDefinitionHtmlRender
from astrocalc.cheatsheet.keplerian_equations import KeplerianEquations
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
            default_value=0.001,
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
            default_value=0.0,
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
            self.orbital.e: f["e"].current_unit.to_native(f["e"].widget.value),  # ✅ still unitless, noop
            self.orbital.i: f["i"].current_unit.to_native(f["i"].widget.value),
            self.orbital.raan: f["raan"].current_unit.to_native(f["raan"].widget.value),
            self.orbital.arg_pe: f["arg_pe"].current_unit.to_native(f["arg_pe"].widget.value),
            self.orbital.true_anomaly: f["true_anomaly"].current_unit.to_native(f["true_anomaly"].widget.value),
            self.orbital.mu: f["mu"].current_unit.to_native(f["mu"].widget.value),
        }

    def evaluate_and_display(self) -> None:
        native_values = self.get_values_dict()

        for renderer in self.equation_renderers:
            native_val = self.orbital.evaluate_orbital_equations(renderer.equation, native_values)
            display_val = renderer.convert_native_to_display(native_val)
            renderer.update_value(display_val)

        # Update the diagram last, using the same native snapshot
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
            # Simple regime guard for the 2.0 diagram
            if not (0 <= e < 1):
                display(HTML("<div style='color:#666; font-style:italic;'>"
                            "Orbit diagram (2.0) currently supports only elliptical orbits (0 ≤ e &lt; 1)."
                            "</div>"))
                return

            # orbit_diagram_svg is the drawsvg function we defined earlier
            dwg = orbit_diagram_svg(a=a, e=e, nu=nu)
            display(dwg)


def orbit_diagram_svg(a, e, nu=None, *, nu_deg=None, size=520, margin=0.15,
                      show_axes=True, show_labels=True):
    """
    Draw a simple orbital-geometry diagram as a vector SVG using drawsvg.

    Parameters
    ----------
    a : float
        Semi-major axis (same units as you want for the geometry)
    e : float
        Eccentricity (0 <= e < 1 for ellipse)
    nu : float, optional
        True anomaly in radians (use either nu or nu_deg)
    nu_deg : float, optional
        True anomaly in degrees (use either nu or nu_deg)
    size : int
        Canvas size in pixels (square)
    margin : float
        Fractional margin around the apoapsis distance
    show_axes : bool
        Draw faint x/y axes
    show_labels : bool
        Add labels for focus, periapsis, apoapsis, and ν

    Returns
    -------
    drawsvg.Drawing
        A drawing you can display in Jupyter by just returning it.
    """
    try:
        import drawsvg as draw
    except ImportError as ex:
        raise ImportError(
            "drawsvg is not installed. Try: pip install drawsvg"
        ) from ex

    if nu is None:
        if nu_deg is None:
            nu = 0.0
        else:
            nu = math.radians(nu_deg)

    if not (0 <= e < 1):
        raise ValueError("This simple diagram function currently supports only elliptical orbits (0 <= e < 1).")

    # Basic ellipse geometry
    b = a * math.sqrt(1 - e*e)
    c = a * e  # focus distance from center

    # We'll place the *right* focus at the origin (0,0). Then the ellipse center is at (-c, 0).
    # Parametric ellipse with that shift:
    #   x(t) = a cos t - c
    #   y(t) = b sin t
    # This makes periapsis at +x.
    rp = a * (1 - e)
    ra = a * (1 + e)

    # True anomaly position (focus-origin polar form)
    r = a * (1 - e*e) / (1 + e * math.cos(nu))
    xnu = r * math.cos(nu)
    ynu = r * math.sin(nu)

    # Scaling to pixels
    R = ra * (1 + margin)
    scale = (size * 0.45) / R  # 0.45 leaves some breathing room

    def tosvg(x, y):
        # SVG y-axis goes down; invert so +y is up in our diagram.
        return (x * scale, -y * scale)

    dwg = draw.Drawing(size, size, origin='center')  # origin at canvas center (still SVG-y-down)

    # Optional axes
    if show_axes:
        ax_len = R * scale
        dwg.append(draw.Line(-ax_len, 0, ax_len, 0, stroke='rgba(0,0,0,0.15)', stroke_width=1))
        dwg.append(draw.Line(0, -ax_len, 0, ax_len, stroke='rgba(0,0,0,0.15)', stroke_width=1))

    # Draw ellipse (as a polyline for full control)
    pts = []
    N = 400
    for i in range(N + 1):
        t = 2 * math.pi * i / N
        x = a * math.cos(t) - c
        y = b * math.sin(t)
        pts.append(tosvg(x, y))

    # Build path from points
    p = draw.Path(stroke='black', stroke_width=2, fill='none')
    x0, y0 = pts[0]
    p.M(x0, y0)
    for (x, y) in pts[1:]:
        p.L(x, y)
    dwg.append(p)

    # Focus (central body) at origin
    fx, fy = tosvg(0, 0)
    dwg.append(draw.Circle(fx, fy, 6, fill='black'))

    # Periapsis and apoapsis points
    px, py = tosvg(rp, 0)
    ax, ay = tosvg(-ra, 0)

    dwg.append(draw.Circle(px, py, 4, fill='black'))
    dwg.append(draw.Circle(ax, ay, 4, fill='black'))

    # Radius vector to current true anomaly
    x1, y1 = tosvg(xnu, ynu)
    dwg.append(draw.Line(fx, fy, x1, y1, stroke='black', stroke_width=2))

    # A small arc to show ν (from +x axis to the radius vector)
    arc_r = max(0.18 * a, 0.2 * rp)  # in "physics units"
    arx0, ary0 = tosvg(arc_r, 0)
    arx1, ary1 = tosvg(arc_r * math.cos(nu), arc_r * math.sin(nu))

    # SVG arc flags: large_arc, sweep
    # In our coordinates, increasing nu should sweep CCW (upwards), but SVG y is inverted; we already inverted y,
    # so the geometry behaves like standard math.
    large_arc = 1 if (nu % (2*math.pi)) > math.pi else 0
    sweep = 1  # CCW in our inverted-y coordinate system tends to map correctly with sweep=1 here

    arc = draw.Path(stroke='black', stroke_width=2, fill='none')
    arc.M(arx0, ary0)
    # Use circular arc: rx=ry=arc_r*scale
    arc.A(arc_r * scale, arc_r * scale, 0, large_arc, sweep, arx1, ary1)
    dwg.append(arc)

    if show_labels:
        # Simple labels (kept minimal)
        dwg.append(draw.Text('Focus', 12, fx + 8, fy - 8))
        dwg.append(draw.Text('Periapsis', 12, px + 6, py - 6))
        dwg.append(draw.Text('Apoapsis', 12, ax - 60, ay - 6))

        # ν label near the arc midpoint
        mid = nu / 2
        lx, ly = tosvg(arc_r * math.cos(mid), arc_r * math.sin(mid))
        dwg.append(draw.Text('ν', 16, lx + 4, ly - 4))

    return dwg
