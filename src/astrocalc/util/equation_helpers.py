from typing import List
import ipywidgets as widgets
import sympy as sy
from astrocalc.util.units import Dimension, Unit

# Define a container class for display + numeric result
class EquationDefinition:
    def __init__(self, expr : sy.Eq, name : str, explanation : str, source : str, dimension : Dimension):
        self.expr = expr
        self.name = name
        self.explanation = explanation
        self.source = source
        self.dimension = dimension

class EquationGroup:
    def __init__(self, name: str, equations: List[EquationDefinition]):
        self.name = name
        self.equations = equations
        



class EquationDefinitionHtmlRender:
    def __init__(self, equation : EquationDefinition):
        self.equation = equation
        self.result = widgets.HTML(value="")  # Empty initially
        self.eq_out = widgets.Output()

    def render(self):
        # Combine explanation and source for tooltip
        tooltip_text = f"{self.equation.explanation} — Source: {self.equation.source}"
    
        # Create a label widget with name and tooltip
        label = widgets.HTML(
            value=f"<b>{self.equation.name}</b>",
            tooltip=tooltip_text
        )
    
        latex_str = sy.latex(self.equation.expr)

        self.eq_out.clear_output(wait=True)
        with self.eq_out:
            from IPython.display import display, Math
            display(Math(latex_str))

        box = widgets.VBox([
            label,
            self.eq_out,
            self.result
        ])
        box.layout = widgets.Layout(width='100%')
        return box


        
    def update_value(self, eq_def: EquationDefinition, value: float, unit: Unit):
        # Format the value and unit abbreviation nicely for display
        html_content = f"{value:.5g} {unit.abbreviation}"
        self.result.value = html_content

def create_equation_renderers(groups: List[EquationGroup]) -> List[EquationDefinitionHtmlRender]:
    renderers = []
    for group in groups:
        for eq in group.equations:
            renderers.append(EquationDefinitionHtmlRender(eq))
    return renderers
    
def render_equation_groups(groups: List[EquationGroup], renderers: List[EquationDefinitionHtmlRender]) -> widgets.Widget:
    all_sections = []
    renderer_iter = iter(renderers)

    for group in groups:
        header = widgets.HTML(value=f"<h3 style='margin-top:10px'>{group.name}</h3>")

        # Pull the next N renderers for this group
        group_renderers = [next(renderer_iter) for _ in group.equations]

        group_box = widgets.GridBox(
            [r.render() for r in group_renderers],
            layout=widgets.Layout(
                grid_template_columns="repeat(3, 20%)",
                grid_gap="2px"
            )
        )

        section = widgets.VBox([header, group_box])
        all_sections.append(section)

    return widgets.VBox(all_sections)
