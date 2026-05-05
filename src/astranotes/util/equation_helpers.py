from dataclasses import dataclass
from typing import List, Optional, Dict, Sequence
import ipywidgets as widgets
import sympy as sy
from IPython.display import display, Math
import math
from numbers import Real
from astranotes.util.units import Dimension, Unit
from astranotes.util.source_ref import SourceRef

def _format_number(value: float, sigfigs: int = 6) -> str:
    """
    Format a float in a compact, readable way:
    - normal numbers -> fixed significant digits
    - very large/small -> scientific notation using HTML superscripts
    """
    if value == 0 or not math.isfinite(value):
        return str(value)

    abs_v = abs(value)

    # Use scientific for extreme magnitudes
    if abs_v >= 1e6 or abs_v < 1e-4:
        exp = int(math.floor(math.log10(abs_v)))
        mant = value / (10 ** exp)
        mant_str = f"{mant:.{sigfigs-1}g}"
        return f"{mant_str} x 10<sup>{exp}</sup>"

    # Otherwise: significant digits without excessive noise
    return f"{value:.{sigfigs}g}"

@dataclass(frozen=True)
class EquationForm:
    expr: sy.Expr

class EquationDefinition:
    def __init__(self, expr: sy.Eq, name: str, explanation: str, source: SourceRef, dimension: Dimension, forms : Sequence[EquationForm] = None):
        self.expr = expr
        self.name = name
        self.explanation = explanation
        self.source = source
        self.dimension = dimension
        if forms == None:
            forms = ()
        self.forms = forms

    def source_text(self, full: bool = False) -> str:
        return self.source.full() if full else self.source.compact()

    def evaluate_expr(self, subsDict : Dict[sy.Basic, float])->float:
        return self.expr.rhs.subs(subsDict).evalf()


class EquationGroup:
    def __init__(self, name: str, equations: List[EquationDefinition]):
        self.name = name
        self.equations = equations


class EquationDefinitionHtmlRender:
    """
    UI + cached display unit for an equation.
    - equation math is rendered using Output()+Math to work reliably in VS Code.
    - current_unit caches how the displayed value should be interpreted.
    """
    def __init__(self, equation: EquationDefinition):
        self.equation = equation

        self.eq_out = widgets.Output()
        self.result = widgets.HTML(value="")  # display value (number + unit)
        self.current_unit: Optional[Unit] = None

        # Render equation math once
        self._render_equation_math()

    def _render_equation_math(self):
        # Base equation: Eq(lhs, rhs)
        lhs = self.equation.expr.lhs
        rhs = self.equation.expr.rhs

        parts = [sy.latex(lhs), sy.latex(rhs)]

        # Additional forms: just RHS expressions
        for f in self.equation.forms:
            parts.append(sy.latex(f.expr))

        latex_str = " = ".join(parts)

        self.eq_out.clear_output(wait=True)
        with self.eq_out:
            display(Math(latex_str))

    def set_display_unit(self, unit: Unit) -> None:
        """
        Update cached display unit.
        """
        self.current_unit = unit

    def convert_native_to_display(self, native_value: float) -> float:
        """
        Convert from native SI value to currently cached display unit value.
        """
        if self.current_unit is None:
            raise RuntimeError("EquationDefinitionHtmlRender.current_unit is not set.")
        return self.current_unit.from_native(native_value)


    def update_value(self, display_value) -> None:
        """
        Update the displayed numeric value using the cached unit.
        Handles undefined, non-real, or invalid values gracefully.
        """
        if self.current_unit is None:
            raise RuntimeError("EquationDefinitionHtmlRender.current_unit is not set.")

        # ---- Validate numeric value ----
        is_valid_real = (
            isinstance(display_value, Real)
            and not isinstance(display_value, bool)   # guard against True/False
            and math.isfinite(display_value)
        )

        if not is_valid_real:
            message_html = (
                "<div style='font-size: 1.05em; padding-top: 2px; color: #a33;'>"
                "Element not evaluated for this orbit type"
                "</div>"
            )
            self.result.value = message_html
            return

        # ---- Normal numeric display ----
        number_html = _format_number(display_value, sigfigs=6)

        unit_html = (
            self.current_unit.pretty_abbreviation()
            if hasattr(self.current_unit, "pretty_abbreviation")
            else self.current_unit.abbreviation
        )

        self.result.value = (
            f"<div style='font-size: 1.1em; padding-top: 2px;'>"
            f"<span>{number_html}</span>"
            f"<span style='padding-left: 6px; color: #444;'>{unit_html}</span>"
            f"</div>"
        )

    def render(self) -> widgets.Widget:
        tooltip_text = f"{self.equation.explanation} — Source: {self.equation.source}"

        label = widgets.HTML(
            value=f"<b>{self.equation.name}</b>",
            tooltip=tooltip_text
        )

        box = widgets.VBox([label, self.eq_out, self.result])
        box.layout = widgets.Layout(width="100%", overflow_x='auto')
        return box

class MatrixEquationRenderer(EquationDefinitionHtmlRender):

    def convert_native_to_display(self, native_value):
        # native_value is a sy.Matrix; convert each element
        if self.current_unit is None:
            raise RuntimeError("current_unit is not set.")
        return native_value.applyfunc(self.current_unit.from_native)

    def update_value(self, display_value) -> None:
        if not isinstance(display_value, sy.Matrix) and not isinstance(display_value, sy.ImmutableDenseMatrix):
            self.result.value = "<div style='color:#a33'>Not a matrix result</div>"
            return

        rows, cols = display_value.shape
        unit_html = self.current_unit.pretty_abbreviation() if hasattr(self.current_unit, "pretty_abbreviation") else self.current_unit.abbreviation
        cells = ""
        for r in range(rows):
            cells += "<tr>"
            for c in range(cols):
                val = float(display_value[r, c])
                cells += f"<td style='padding:2px 8px; text-align:right'>{_format_number(val)}</td>"
            cells += f"<td style='padding:2px 4px; color:#444; font-size:0.9em'>{unit_html}</td>"
            cells += "</tr>"

        self.result.value = f"<table style='font-size:1.0em; border-collapse:collapse'>{cells}</table>"


def create_equation_renderers(groups: List[EquationGroup]) -> List[EquationDefinitionHtmlRender]:
    renderers: List[EquationDefinitionHtmlRender] = []
    for group in groups:
        for eq in group.equations:
            if isinstance(eq.expr.rhs, sy.MatrixBase):
                renderers.append(MatrixEquationRenderer(eq))
            else:
                renderers.append(EquationDefinitionHtmlRender(eq))
    return renderers


def render_equation_groups(groups: List[EquationGroup], renderers: List[EquationDefinitionHtmlRender]) -> widgets.Widget:
    all_sections = []
    renderer_iter = iter(renderers)

    for group in groups:
        header = widgets.HTML(value=f"<h3 style='margin-top:10px'>{group.name}</h3>")

        group_renderers = [next(renderer_iter) for _ in group.equations]

        group_box = widgets.GridBox(
            [r.render() for r in group_renderers],
            layout=widgets.Layout(
                grid_template_columns="repeat(3, 1fr)",
                grid_gap="2px"
            )
        )

        section = widgets.VBox([header, group_box])
        all_sections.append(section)

    return widgets.VBox(all_sections)
