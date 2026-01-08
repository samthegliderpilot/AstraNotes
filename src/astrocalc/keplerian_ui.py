from typing import Callable, List, Dict
from astrocalc.util.units import unit_registry, Length, Time, Angle, Mass, Dimensionless
import ipywidgets as widgets
from astrocalc.util.units import Unit, Dimension
from astrocalc.util.equation_helpers import EquationDefinitionHtmlRender
from IPython.display import display
import traceback
class OrbitalMechanicsWidget:
    def __init__(self, orbital_mechanics, equation_renderers):
        self.orbital = orbital_mechanics
        self.equation_renderers = equation_renderers

        # Use predefined Dimension instances
        self.length_dim = Length
        self.time_dim = Time
        self.angle_dim = Angle
        self.mass_dim = Mass

        km_unit = unit_registry.get_unit_by_abbreviation(Length, "km")
        kg_unit = unit_registry.get_unit_by_abbreviation(Mass, "kg")
        deg_unit = unit_registry.get_unit_by_abbreviation(Angle, "deg")
        sec_unit = unit_registry.get_unit_by_abbreviation(Time, "s")
        
        self.mu_dimension = Length*Length*Length/(Time*Time)  # L^3 / T^2

        # Create dropdowns using Dimension.get_dropdown_options()
        self.length_unit = widgets.Dropdown(
            options = [(unit.name, unit) for unit in unit_registry[Length]],
            value=km_unit,
            description='Length Unit:',
            style={'description_width': 'initial'}
        )

        self.time_unit = widgets.Dropdown(
            options = [(unit.name, unit) for unit in unit_registry[Time]],
            value=sec_unit ,
            description='Time Unit:',
            style={'description_width': 'initial'}
        )

        self.angle_unit = widgets.Dropdown(
            options = [(unit.name, unit) for unit in unit_registry[Angle]],
            value=deg_unit,
            description='Angle Unit:',
            style={'description_width': 'initial'}
        )

        self.mass_unit = widgets.Dropdown(
            options = [(unit.name, unit) for unit in unit_registry[Mass]],
            value=kg_unit,
            description='Mass Unit:',
            style={'description_width': 'initial'}
        )

        # Orbital element input widgets
        # Length widgets
        display_units = self.get_selected_units()
        self.a_float = widgets.FloatText(value=7000, description='a (semi-major axis):')
        self.a_widget, self.a_unit_label = self._make_labeled_widget(self.a_float, self.length_unit.value)
        
        self.mu_float = widgets.FloatText(value=398600, description='μ (GM):')
        mu_unit = unit_registry.get_unit_for_dimension(self.mu_dimension, self.get_selected_units())
        self.mu_widget, self.mu_unit_label = self._make_labeled_widget(self.mu_float, mu_unit) 

        # Angle widgets
        self.i_float = widgets.FloatText(value=0.1, description='i (inclination):')
        self.i_widget, self.i_unit_label = self._make_labeled_widget(self.i_float, self.angle_unit.value)
        
        self.raan_float = widgets.FloatText(value=1.0, description='RAAN:')
        self.raan_widget, self.raan_unit_label = self._make_labeled_widget(self.raan_float, self.angle_unit.value)
        
        self.arg_pe_float = widgets.FloatText(value=0.5, description='Arg of Periapsis:')
        self.arg_pe_widget, self.arg_pe_unit_label = self._make_labeled_widget(self.arg_pe_float, self.angle_unit.value)
        
        self.nu_float = widgets.FloatText(value=0.0, description='True Anomaly:')
        self.nu_widget, self.nu_unit_label = self._make_labeled_widget(self.nu_float, self.angle_unit.value)
        
        # Eccentricity doesn't need units
        self.e_float_widget = widgets.FloatText(value=0.001, description='e (eccentricity):')

        # Attach observers for unit changes
        self.length_unit.observe(self.on_length_unit_change, names='value')
        self.angle_unit.observe(self.on_angle_unit_change, names='value')
        self.time_unit.observe(self.on_time_unit_change, names='value')
        self.mass_unit.observe(self.on_mass_unit_change, names='value')

        # Evaluate button
        self.evaluate_button = widgets.Button(description="Evaluate Elements", button_style='primary')
        #self.evaluate_button.on_click(self.evaluate_and_display)

        # Store previous units for conversion tracking
        self.prev_length_unit = self.length_unit.value
        self.prev_angle_unit = self.angle_unit.value
        self.prev_time_unit = self.time_unit.value
        self.prev_mass_unit = self.mass_unit.value

        # Layout
        self.unit_selectors = widgets.HBox([self.length_unit, self.time_unit, self.angle_unit, self.mass_unit])

        for w in [self.a_float, self.mu_float, self.i_float, self.raan_float, self.arg_pe_float, self.nu_float, self.e_float_widget]:
            w.observe(self.on_input_change, names='value')
        
        # Initialize button and validation colors at start
        self.evaluate_button.disabled = not self.inputs_are_valid()

    def _make_labeled_widget(self, float_widget, unit: Unit):
        label = widgets.Label(value=unit.abbreviation, layout=widgets.Layout(width='80px'))
        container = widgets.HBox([float_widget, label])
        return container, label

    def _update_widgets_for_unit_change(self, old_unit: Unit, new_unit: Unit, widgets: List[widgets.FloatText], unit_labels: List[widgets.Label]):
        if old_unit != new_unit:
            for w in widgets:
                native_value = old_unit.to_native(w.value)
                w.value = new_unit.from_native(native_value)
            for label in unit_labels:
                label.value = new_unit.abbreviation
            
    def on_length_unit_change(self, change):
        if change['name'] == 'value':
            old_unit: Unit = self.prev_length_unit
            new_unit: Unit = change['new']
            self._update_widgets_for_unit_change(
                old_unit,
                new_unit,
                [self.a_float],
                [self.a_unit_label]
            )
            self._update_mu_for_unit_change(
                old_length_unit=old_unit,
                old_time_unit=self.prev_time_unit,
                new_length_unit=new_unit,
                new_time_unit=self.time_unit.value,
            )

            # Now update the "prev" tracking
            self.prev_length_unit = new_unit
            self.evaluate_and_display()
    
    def on_angle_unit_change(self, change):
        if change['name'] == 'value':
            old_unit: Unit = self.prev_angle_unit
            new_unit: Unit = change['new']
            self._update_widgets_for_unit_change(
                old_unit,
                new_unit,
                [self.i_float, self.raan_float, self.arg_pe_float, self.nu_float],
                [self.i_unit_label, self.raan_unit_label, self.arg_pe_unit_label, self.nu_unit_label]
            )
            self.prev_angle_unit = new_unit
            self.evaluate_and_display()
                
    def on_time_unit_change(self, change):
        if change['name'] == 'value':
            old_unit: Unit = self.prev_time_unit
            new_unit: Unit = change['new']
            if old_unit != new_unit:
                # Convert μ using old units -> new units
                self._update_mu_for_unit_change(
                    old_length_unit=self.prev_length_unit,
                    old_time_unit=old_unit,
                    new_length_unit=self.length_unit.value,
                    new_time_unit=new_unit,
                )

                # Now update the "prev" tracking
                self.prev_time_unit = new_unit
                self.evaluate_and_display()

    def on_mass_unit_change(self, change):
        if change['name'] == 'value':
            old_unit: Unit = self.prev_mass_unit
            new_unit: Unit = change['new']
            if old_unit != new_unit:
                # Add any widgets that depend on time units here if needed
                # Example placeholder; none currently in orbital elements needing conversion
                self.prev_mass_unit = new_unit
                self.evaluate_and_display()

    def _update_mu_for_unit_change(self, old_length_unit: Unit, old_time_unit: Unit,
                                new_length_unit: Unit, new_time_unit: Unit):
        """
        Convert μ value + label from the old composite unit to the new composite unit.
        """
        old_display_units = {
            unit_registry.LENGTH: old_length_unit,
            unit_registry.TIME: old_time_unit,
            unit_registry.ANGLE: self.prev_angle_unit,
            unit_registry.MASS: self.prev_mass_unit,
            unit_registry.DIMENSIONLESS: Dimensionless,
        }

        new_display_units = {
            unit_registry.LENGTH: new_length_unit,
            unit_registry.TIME: new_time_unit,
            unit_registry.ANGLE: self.angle_unit.value,
            unit_registry.MASS: self.mass_unit.value,
            unit_registry.DIMENSIONLESS: Dimensionless,
        }

        old_mu_unit = unit_registry.get_unit_for_dimension(self.mu_dimension, old_display_units)
        new_mu_unit = unit_registry.get_unit_for_dimension(self.mu_dimension, new_display_units)

        # Always convert (even if abbreviations are equal)
        native_value = old_mu_unit.to_native(self.mu_float.value)
        self.mu_float.value = new_mu_unit.from_native(native_value)
        self.mu_unit_label.value = new_mu_unit.abbreviation


    def get_values_dict(self):
        display_units = self.get_selected_units()
        mu_unit = unit_registry.get_unit_for_dimension(self.mu_dimension, display_units)
        # Convert all widget values to native units before returning
        values = {
            self.orbital.a: self.length_unit.value.to_native(self.a_float.value),
            self.orbital.e: self.e_float_widget.value,
            self.orbital.i: self.angle_unit.value.to_native(self.i_float.value),
            self.orbital.raan: self.angle_unit.value.to_native(self.raan_float.value),
            self.orbital.arg_pe: self.angle_unit.value.to_native(self.arg_pe_float.value),
            self.orbital.true_anomaly: self.angle_unit.value.to_native(self.nu_float.value),
            self.orbital.mu: mu_unit.to_native(self.mu_float.value), 
        }
        return values

    def get_selected_units(self) -> Dict[Dimension, Unit]:
        # Example: assuming you have unit selection widgets named like length_unit_selector, angle_unit_selector, time_unit_selector
        return {
            unit_registry.LENGTH: self.length_unit.value,
            unit_registry.TIME: self.time_unit.value,
            unit_registry.ANGLE: self.angle_unit.value,
            unit_registry.MASS : self.mass_unit.value,
            unit_registry.DIMENSIONLESS: unit_registry.get_unit_by_abbreviation(Dimensionless, "")
        }

    def evaluate_and_display(self):
        native_values = self.get_values_dict()

        display_units = self.get_selected_units()

        evaluated_results = {}

        for eq_def in self.equation_renderers:
            native_val = self.orbital.evaluate_orbital_equations(eq_def.equation.expr, native_values)
            evaluated_results[eq_def] = native_val


        display_values = {}
        for eq_def, native_val in evaluated_results.items():
            dim = eq_def.equation.dimension
            # Fallback to native unit if no selected unit found
            display_unit = unit_registry.get_unit_for_dimension(dim, display_units)
            display_val = display_unit.from_native(native_val)
            display_values[eq_def] = (display_val, display_unit)

        for eq_def, (val, unit) in display_values.items():
            eq_def.update_value(eq_def, val, unit)

    def display(self):
        display(self.unit_selectors)
        display(self.a_widget, self.e_float_widget, self.i_widget, self.raan_widget,
                self.arg_pe_widget, self.nu_widget, self.mu_widget,
                self.evaluate_button)

    def validate_widget(self, widget: widgets.FloatText, validate_func: Callable[[float], bool]) -> bool:
        val = widget.value
        if val is None:
            widget.layout.background_color = 'lightpink'
            return False
        try:
            if not validate_func(val):
                widget.layout.background_color = 'lightpink'
                return False
            else:
                widget.layout.background_color = ''
                return True
        except Exception:
            widget.layout.background_color = 'lightpink'
            return False

    def inputs_are_valid(self) -> bool:
        # Example validators for your widgets
        validators = {
            self.a_float: lambda v: v > 0,
            self.mu_float: lambda v: v > 0,
            self.i_float: lambda v: True,  # no special restriction, just numeric
            self.raan_float: lambda v: True,
            self.arg_pe_float: lambda v: True,
            self.nu_float: lambda v: True,
            self.e_float_widget: lambda v: 0 <= v < 1,
        }
    
        all_valid = True
        for widget, validator in validators.items():
            if not self.validate_widget(widget, validator):
                all_valid = False
    
        return all_valid

    def on_input_change(self, change):
        self.evaluate_button.disabled = not self.inputs_are_valid()