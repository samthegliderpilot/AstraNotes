import os
import subprocess
from astranotes.cheatsheet.keplerian_equations import KeplerianEquations
from astranotes.cheatsheet.render_latex_sources import render_sources_latex
from astranotes.util.equation_helpers import EquationGroup
from sympy import latex
import sympy as sy
from datetime import datetime, timezone
import importlib.metadata as md
from pathlib import Path

# === CONFIG ===
BUILD_DIR = Path(os.path.dirname(__file__)).parent.parent / "build"
TEX_FILENAME = "keplerian_cheatsheet.tex"
PDF_FILENAME = "keplerian_cheatsheet.pdf"
TEX_PATH = os.path.join(BUILD_DIR, TEX_FILENAME)

def ensure_build_dir():
    os.makedirs(BUILD_DIR, exist_ok=True)

def generate_column_equation_table(equations):
    """
    Generate LaTeX lines for one vertical column of equations.
    Returns a string (not list).
    """
    lines = []
    lines.append(r"\setlength{\parskip}{0pt}")
    lines.append(r"\setlength{\parindent}{0pt}")

    for eqCb in equations:
        eqFull = eqCb
        eq = eqFull.expr
        name = eqFull.name
        eq_latex = sy.latex(eq)
        lines.append(r"\noindent{\footnotesize\textbf{" + name + r"}}")
        lines.append(r"\vspace{-0.4em}")
        lines.append(r"\[\small " + eq_latex + r"\]")
    return "\n".join(lines)

def build_full_equation_table(circularAndElliptical, parabolic, hyperbolic):
    half_closed = round(len(circularAndElliptical)/2)
    max_len = max(half_closed, len(parabolic), len(hyperbolic))

    def pad_col(col):
        return col + [("", "")] * (max_len - len(col))

    def wrap_minipage(content):
        return (
            r"\begin{minipage}[t]{\linewidth}"
            r"\setlength{\abovedisplayskip}{2pt}"
            r"\setlength{\belowdisplayskip}{2pt}"
            "\n" + content + "\n"
            r"\end{minipage}"
        )


    col1 = wrap_minipage(generate_column_equation_table(circularAndElliptical[0:half_closed]))
    col2 = wrap_minipage(generate_column_equation_table(circularAndElliptical[half_closed:]))
    col3 = wrap_minipage(generate_column_equation_table(parabolic))
    col4 = wrap_minipage(generate_column_equation_table(hyperbolic))

    latex_lines = [
        r"\begin{tabular}{p{0.6\linewidth}@{\hspace{5.5em}} p{0.6\linewidth}@{\hspace{5.5em}} p{0.6\linewidth}@{\hspace{5.5em}} p{0.6\linewidth}}",
        r"\multicolumn{1}{c}{\textbf{\small Circular}} & \multicolumn{1}{c}{\textbf{\small and Elliptical}} & \multicolumn{1}{c}{\textbf{\small Parabolic}} & \multicolumn{1}{c}{\textbf{\small Hyperbolic}} \\[0.5em]",
                    col1 + r" & " + col2 + r" & " + col3 + r" & " + col4 + r" \\",
        r"\end{tabular}"
    ]

    return latex_lines

def generate_latex():
    kepler = KeplerianEquations()

    version = md.version("astranotes")  # or whatever your [project].name is
    generated_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    footer_text = f"AstraNotes v{version} — Generated {generated_utc}"

    equation_methods = [
        kepler.vis_viva(),
        kepler.mean_motion(),
        kepler.orbital_period(),
        kepler.orbital_radius(),
        kepler.circular_velocity(),
        kepler.escape_velocity(),
        kepler.semi_latus_rectum(),
        kepler.velocity_elliptical(),
        kepler.sin_eccentric_anomaly_wrt_true_anomaly(),
        kepler.cos_eccentric_anomaly_wrt_true_anomaly(),
        kepler.eccentric_anomaly_wrt_true_anomaly(),
        kepler.velocity_elliptical(),
    ]
    circularAndEllipticalEquations = [equation_methods[0], equation_methods[1], equation_methods[4], equation_methods[2], equation_methods[6], equation_methods[3], equation_methods[7], equation_methods[8], equation_methods[9], equation_methods[10], equation_methods[7]]
    parabolicEquations = [equation_methods[5]]
    hyperbolicEquations = []
    latex_lines = [
r"\documentclass[10pt]{article}",
r"\usepackage[landscape, margin=1in]{geometry}",
r"\usepackage{amsmath}",
r"\usepackage{titlesec}",
r"\usepackage{multicol}",
r"\usepackage{fancyhdr}",
r"\usepackage{lastpage}",  # optional, only if you want Page X of Y
r"\pagestyle{fancy}",
r"\fancyhf{}",  # clear header/footer
rf"\fancyfoot[C]{{\footnotesize {footer_text}}}",
r"\renewcommand{\headrulewidth}{0pt}",
r"\renewcommand{\footrulewidth}{0.4pt}",
# Remove spacing from section titles if desired
r"\titlespacing*{\section}{0pt}{*0}{*0}",
r"\titlespacing*{\subsection}{0pt}{*0}{*0}",

# Reduce paragraph spacing to pack more
r"\setlength{\parskip}{0pt}",
r"\setlength{\parindent}{0pt}",
r"\setlength{\abovedisplayskip}{5pt}",
r"\setlength{\belowdisplayskip}{5pt}",

r"\begin{document}",
r"\vspace*{-1.5em}",
# Custom title block - smaller font, top-left, one line
r"{\small",
r"\noindent",
r"\textbf{AstraNotes Cheat Sheet: Keplerian Orbits} \quad --- \quad \textit{SamTheGliderPilot}",
r"}",

r"\vspace{1em}  % small vertical space before the rest",

r"\section*{Keplerian Orbital Equations}",
r"\begin{multicols}{4}"

    ]



    # for method in equation_methods:
    #     eq_def = method()
    #     equation_latex = latex(eq_def.expr, mode='plain')
    #     print("Generated LaTeX:", repr(equation_latex))
    #     latex_lines.append(r"\subsection*{" + eq_def.name + r"}")
    #     latex_lines.append(r"\begin{align*}")
    #     latex_lines.append(equation_latex )
    #     latex_lines.append(r"\end{align*}")
    #     latex_lines.append("")
    latex_table = build_full_equation_table(
        circularAndEllipticalEquations,
        parabolicEquations,
        hyperbolicEquations
    )

    # Now latex_table is a list of lines; write it into your .tex file or
    # include in your document body.
    for line in latex_table:
        latex_lines.append(line)
    latex_lines.append(r"\end{multicols}")
    latex_lines.append(r"\clearpage")  # separate final page

    # add sources content
    latex_lines.extend(render_sources_latex([EquationGroup('', equation_methods)]))
    latex_lines.append(r"\vspace{0.75em}")
    latex_lines.append(r"\noindent{\footnotesize\textbf{Note on atan2:} "
                    r"This sheet uses $\mathrm{atan2}(y, x)$ (sine term/$y$ first, cosine term/$x$ second) "
                    r"to preserve quadrant.}")
    latex_lines.append(r"\end{document}")

    with open(TEX_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(latex_lines))

    print(f"+ LaTeX file written to {TEX_PATH}")

def compile_pdf():
    print("Compiling LaTeX to PDF...")
    subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", "-output-directory", BUILD_DIR, TEX_PATH],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print(f"[✓] PDF built at {os.path.join(BUILD_DIR, PDF_FILENAME)}")

def clean_aux_files():
    # Clean common aux files
    extensions = [".aux", ".log", ".out"]
    for ext in extensions:
        file_path = os.path.join(BUILD_DIR, TEX_FILENAME.replace(".tex", ext))
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"[-] Removed {file_path}")

def main():
    ensure_build_dir()
    generate_latex()
    compile_pdf()
    clean_aux_files()

if __name__ == "__main__":
    main()
