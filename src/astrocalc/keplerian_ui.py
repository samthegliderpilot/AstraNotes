from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List

import ipywidgets as widgets
from IPython.display import display

from astrocalc.util.units import (
    unit_registry,
    Length, Time, Angle, Mass, Dimensionless,
    Unit, Dimension,
)

from astrocalc.util.equation_helpers import EquationDefinitionHtmlRender
from astrocalc.equations.keplerian_equations import KeplerianEquations
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
        self.evaluate_button = widgets.Button(description="Evaluate Elements", button_style="primary")
        self.evaluate_button.disabled = not self.inputs_are_valid()

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
        if val is None:
            widget.layout.background_color = "lightpink"
            return False
        try:
            if not validate_func(val):
                widget.layout.background_color = "lightpink"
                return False
            widget.layout.background_color = ""
            return True
        except Exception:
            widget.layout.background_color = "lightpink"
            return False

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
        self.evaluate_button.disabled = not self.inputs_are_valid()
