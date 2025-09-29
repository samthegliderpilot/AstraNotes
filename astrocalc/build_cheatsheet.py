import os
import subprocess
import sys
sys.path.append(os.path.dirname((os.path.dirname(__file__))))
from equations.keplerian_equations import KeplerianEquations
from sympy import latex
import sympy as sy

# === CONFIG ===
BUILD_DIR = os.path.join(os.path.dirname(__file__), "build")
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
        lines.append(r"\noindent {\footnotesize \textbf{\mbox{" + name + r"}}}\\")
        lines.append(r"\[\small " + eq_latex + r"\]")
        lines.append(r"\vspace{0.25em}")
        # lines.append(r"\begin{center}\small")
        # lines.append(r"\[")
        # lines.append(eq_latex)
        # lines.append(r"\]")
        # lines.append(r"\end{center}")
        # lines.append(r"\vspace{0.5em}")

    return "\n".join(lines)

def build_full_equation_table(circular, elliptical, parabolic, hyperbolic):
    max_len = max(len(circular), len(elliptical), len(parabolic), len(hyperbolic))

    def pad_col(col):
        return col + [("", "")] * (max_len - len(col))

    # circular = pad_col(circular)
    # elliptical = pad_col(elliptical)
    # parabolic = pad_col(parabolic)
    # hyperbolic = pad_col(hyperbolic)

    def wrap_minipage(content):
        return r"\begin{minipage}[t]{\linewidth}" + "\n" + content + "\n" + r"\end{minipage}"

    col1 = wrap_minipage(generate_column_equation_table(circular))
    col2 = wrap_minipage(generate_column_equation_table(elliptical))
    col3 = wrap_minipage(generate_column_equation_table(parabolic))
    col4 = wrap_minipage(generate_column_equation_table(hyperbolic))

    latex_lines = [
        r"\begin{tabular}{p{0.6\linewidth}@{\hspace{5.5em}} p{0.6\linewidth}@{\hspace{5.5em}} p{0.6\linewidth}@{\hspace{5.5em}} p{0.6\linewidth}}",
    r"\multicolumn{1}{c}{\textbf{\small Circular}} & \multicolumn{1}{c}{\textbf{\small Elliptical}} & \multicolumn{1}{c}{\textbf{\small Parabolic}} & \multicolumn{1}{c}{\textbf{\small Hyperbolic}} \\[0.5em]",
                    col1 + r" & " + col2 + r" & " + col3 + r" & " + col4 + r" \\",
        r"\end{tabular}"
    ]

    return latex_lines

def generate_latex():
    kepler = KeplerianEquations()

    equation_methods = [
        kepler.vis_viva(),
        kepler.mean_motion(),
        kepler.orbital_period(),
        kepler.orbital_radius(),
        kepler.circular_velocity(),
        kepler.escape_velocity(),
    ]
    circularEquations = [equation_methods[0], equation_methods[1]]
    ellipticalEquations = [equation_methods[2]]
    parabolicEquations = [equation_methods[3], equation_methods[4]]
    hyperbolicEquations = [equation_methods[5]]
    latex_lines = [
r"\documentclass[10pt]{article}",
r"\usepackage[landscape, margin=1in]{geometry}",
r"\usepackage{amsmath}",
r"\usepackage{titlesec}",
r"\usepackage{multicol}",
# Remove spacing from section titles if desired
r"\titlespacing*{\section}{0pt}{*0}{*0}",
r"\titlespacing*{\subsection}{0pt}{*0}{*0}",

# Reduce paragraph spacing to pack more
r"\setlength{\parskip}{0pt}",
r"\setlength{\parindent}{0pt}",
r"\setlength{\abovedisplayskip}{5pt}",
r"\setlength{\belowdisplayskip}{5pt}",

r"\begin{document}",

# Custom title block - smaller font, top-left, one line
r"{\small",
r"\noindent",
r"\textbf{AstroCalc Cheat Sheet: Keplerian Orbits} \quad --- \quad \textit{SamTheGliderPilot}",
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
        circularEquations,
        ellipticalEquations,
        parabolicEquations,
        hyperbolicEquations
    )

    # Now latex_table is a list of lines; write it into your .tex file or
    # include in your document body.
    for line in latex_table:
        latex_lines.append(line)
    latex_lines.append(r"\end{multicols}")
    latex_lines.append(r"\end{document}")

    with open(TEX_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(latex_lines))

    print(f"[✓] LaTeX file written to {TEX_PATH}")

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
            print(f"[−] Removed {file_path}")

def main():
    ensure_build_dir()
    generate_latex()
    compile_pdf()
    clean_aux_files()

if __name__ == "__main__":
    main()
