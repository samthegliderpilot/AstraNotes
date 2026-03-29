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
import re

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

    for eqFull in equations:
        eq = eqFull.expr
        name = eqFull.name

        lhs = eq.lhs
        rhs = eq.rhs

        parts = [sy.latex(lhs), sy.latex(rhs)]
        for form in getattr(eqFull, "forms", ()):
            parts.append(sy.latex(form.expr))

        eq_latex = r" = ".join(parts)
        eq_latex = _split_long_equation_latex(eq_latex, max_len=65)

        lines.append(r"\noindent{\footnotesize\textbf{" + name + r"}}")
        #lines.append(r"\vspace{-0.4em}")
        lines.append(r"\[" + eq_latex + r"\]")

    return "\n".join(lines)

import re

def _split_long_equation_latex(eq_latex: str, max_len: int = 60) -> str:
    """
    Split long LaTeX equations at a sensible place.

    Strategy:
      1. Normalize \\left/\\right to \\bigl/\\bigr.
      2. Remove wrapper braces around \\bigl...\\bigr groups so line breaks
         can occur between rows of an aligned environment.
      3. Prefer splitting at a comma inside a \\bigl(...\\bigr)-style group.
      4. Fall back to top-level '=' / '+' / '-'.

    Returns either the original equation string or an aligned environment.
    """
    if len(eq_latex) <= max_len:
        return eq_latex

    safe = eq_latex

    # 1) Normalize stretchy delimiters
    safe = (
        safe
        .replace(r"\left(", r"\bigl(")
        .replace(r"\right)", r"\bigr)")
        .replace(r"\left[", r"\bigl[")
        .replace(r"\right]", r"\bigr]")
        .replace(r"\left\{", r"\bigl\{")
        .replace(r"\right\}", r"\bigr\}")
    )

    # 2) Remove outer braces around delimited groups:
    #    {...\bigl(...\bigr)...} -> ...\bigl(...\bigr)...
    # This is what makes multiline breaks legal for function arguments.
    replacements = [
        (r"{\bigl(", r"\bigl("),
        (r"\bigr)}", r"\bigr)"),
        (r"{\bigl[", r"\bigl["),
        (r"\bigr]}", r"\bigr]"),
        (r"{\bigl\{", r"\bigl\{"),
        (r"\bigr\}}", r"\bigr\}"),
    ]
    for old, new in replacements:
        safe = safe.replace(old, new)

    def _find_positions_top_level(s: str, token: str):
        """Find token positions at brace depth 0."""
        out = []
        depth = 0
        i = 0
        while i < len(s):
            ch = s[i]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth = max(0, depth - 1)

            if depth == 0 and s.startswith(token, i):
                out.append(i)
            i += 1
        return out

    def _find_comma_in_delimited_group(s: str):
        """
        Find commas that are inside a \\bigl...\\bigr group but not inside {...}.
        Returns list of indices.
        """
        out = []
        brace_depth = 0
        delim_depth = 0
        i = 0

        open_tokens = [r"\bigl(", r"\bigl[", r"\bigl\{"]
        close_tokens = [r"\bigr)", r"\bigr]", r"\bigr\}"]

        while i < len(s):
            # Delimiter tracking first
            matched = False
            for tok in open_tokens:
                if s.startswith(tok, i):
                    delim_depth += 1
                    i += len(tok)
                    matched = True
                    break
            if matched:
                continue

            for tok in close_tokens:
                if s.startswith(tok, i):
                    delim_depth = max(0, delim_depth - 1)
                    i += len(tok)
                    matched = True
                    break
            if matched:
                continue

            ch = s[i]
            if ch == "{":
                brace_depth += 1
            elif ch == "}":
                brace_depth = max(0, brace_depth - 1)
            elif ch == "," and brace_depth == 0 and delim_depth > 0:
                out.append(i)

            i += 1

        return out

    center = len(safe) / 2

    # 3) Best choice: comma in a delimited argument list
    comma_positions = _find_comma_in_delimited_group(safe)
    if comma_positions:
        idx = min(comma_positions, key=lambda x: abs(x - center))
        left = safe[:idx + 1]
        right = safe[idx + 1:].lstrip()
        return (
            r"\begin{aligned}"
            + left
            + r" \\ "
            #+ r"& "
            + right
            + r"\end{aligned}"
        )

    # 4) Fallbacks: top-level =, +, -
    for token in [r" = ", r" + ", r" - "]:
        positions = _find_positions_top_level(safe, token)
        if positions:
            idx = min(positions, key=lambda x: abs(x - center))
            if token == r" = ":
                left = safe[:idx]
                right = safe[idx + len(token):].lstrip()
                return (
                    r"\begin{aligned}"
                    + left
                    + r" \\ "
                    + r"&= "
                    + right
                    + r"\end{aligned}"
                )
            else:
                left = safe[:idx]
                right = safe[idx:].lstrip()
                return (
                    r"\begin{aligned}"
                    + left
                    + r" \\ "
                    + r"&\qquad "
                    + right
                    + r"\end{aligned}"
                )

    return safe

def build_full_equation_table(equation_columns):
    def wrap_minipage(content):
        return (
            r"\begin{minipage}[t]{\linewidth}"
            r"\setlength{\abovedisplayskip}{2pt}"
            r"\setlength{\belowdisplayskip}{2pt}"
            "\n" + content + "\n"
            r"\end{minipage}"
        )

    rendered_cols = [
        wrap_minipage(generate_column_equation_table(col))
        for col in equation_columns
    ]

    # Pad out to exactly 4 columns if needed
    while len(rendered_cols) < 4:
        rendered_cols.append(wrap_minipage(""))

    latex_lines = [
        r"\begin{tabular}{p{0.6\linewidth}@{\hspace{5.5em}} p{0.6\linewidth}@{\hspace{5.5em}} p{0.6\linewidth}@{\hspace{5.5em}} p{0.6\linewidth}}",
        r"\multicolumn{1}{c}{\textbf{\small Column 1}} & "
        r"\multicolumn{1}{c}{\textbf{\small Column 2}} & "
        r"\multicolumn{1}{c}{\textbf{\small Column 3}} & "
        r"\multicolumn{1}{c}{\textbf{\small Column 4}} \\[0.5em]",
        rendered_cols[0] + r" & " + rendered_cols[1] + r" & " + rendered_cols[2] + r" & " + rendered_cols[3] + r" \\",
        r"\end{tabular}"
    ]

    return latex_lines

def generate_latex():
    kepler = KeplerianEquations()

    version = md.version("astranotes")  # or whatever your [project].name is
    generated_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    footer_text = f"AstraNotes v{version} — Generated {generated_utc}"
    col1_equations = [
        kepler.orbital_radius,
        kepler.semi_latus_rectum,
        kepler.radius_of_periapsis,
        kepler.radius_of_apoapsis,
    ]

    col2_equations = [
        kepler.velocity_magnitude,
        kepler.vis_viva,
        kepler.circular_velocity,
        kepler.escape_velocity,
        kepler.angular_momentum,
    ]

    col3_equations = [
        kepler.mean_motion,
        kepler.orbital_period,
        kepler.eccentric_anomaly_wrt_true_anomaly,
        kepler.flight_path_angle_wrt_eccentric_anomaly,
    ]

    col4_equations = [
        kepler.parabolic_anomaly_wrt_true_anomaly,
        kepler.flight_path_angle_parabolic,
        kepler.hyperbolic_anomaly_wrt_true_anomaly,
    ]

    equation_columns = [
        col1_equations,
        col2_equations,
        col3_equations,
        col4_equations,
    ]
    latex_table = build_full_equation_table(equation_columns)

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

    # Now latex_table is a list of lines; write it into your .tex file or
    # include in your document body.
    for line in latex_table:
        latex_lines.append(line)
    latex_lines.append(r"\end{multicols}")
    latex_lines.append(r"\clearpage")  # separate final page

    # add sources content
    latex_lines.extend(render_sources_latex([EquationGroup('', [eq for col in equation_columns for eq in col])]))
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
