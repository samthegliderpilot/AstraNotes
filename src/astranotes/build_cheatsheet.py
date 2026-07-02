import os
import subprocess
from astranotes.cheatsheet.keplerian_equations import KeplerianEquations
from astranotes.cheatsheet.render_latex_sources import render_sources_latex
from astranotes.util.equation_helpers import EquationGroup
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


_WIDE_LATEX_THRESHOLD = 300  # chars; above this an equation auto-sizes to col_span=2


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
    if r"\begin{matrix}" in eq_latex:
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
    for old, new in [
        (r"{\bigl(", r"\bigl("),  (r"\bigr)}", r"\bigr)"),
        (r"{\bigl[", r"\bigl["),  (r"\bigr]}", r"\bigr]"),
        (r"{\bigl\{", r"\bigl\{"), (r"\bigr\}}", r"\bigr\}"),
    ]:
        safe = safe.replace(old, new)

    def _find_positions_top_level(s: str, token: str):
        """Find token positions at brace depth 0."""
        out, depth, i = [], 0, 0
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
        """Find commas inside a \\bigl...\\bigr group but not inside {...}."""
        out = []
        brace_depth, delim_depth, i = 0, 0, 0
        open_tokens  = [r"\bigl(", r"\bigl[", r"\bigl\{"]
        close_tokens = [r"\bigr)", r"\bigr]", r"\bigr\}"]

        while i < len(s):
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
        left, right = safe[:idx + 1], safe[idx + 1:].lstrip()
        return r"\begin{aligned}" + left + r" \\ " + right + r"\end{aligned}"

    # 4) Fallbacks: top-level + / -
    for token in [r" + ", r" - "]:
        positions = _find_positions_top_level(safe, token)
        if positions:
            idx = min(positions, key=lambda x: abs(x - center))
            left, right = safe[:idx], safe[idx:].lstrip()
            return r"\begin{aligned}" + left + r" \\ " + right + r"\end{aligned}"

    # 5) Split on equals only when there is a chain of equalities
    if safe.count(" = ") > 1:
        positions = _find_positions_top_level(safe, r" = ")
        if positions:
            idx = min(positions, key=lambda x: abs(x - center))
            left = safe[:idx]
            right = safe[idx + len(r" = "):].lstrip()
            return r"\begin{aligned}" + left + r" \\ = " + right + r"\end{aligned}"

    return safe


# ---------------------------------------------------------------------------
# Grid layout
# ---------------------------------------------------------------------------

GRID_COLS = 4
COL_UNIT = 0.995 / GRID_COLS   # fraction of \textwidth per column slot


class LayoutItem:
    def __init__(self, equation, col_span: int = None):
        self.equation = equation

        eq = equation.expr
        parts = [sy.latex(eq.lhs), sy.latex(eq.rhs)]
        for form in getattr(equation, "forms", ()):
            parts.append(sy.latex(form))
        raw = r" = ".join(parts)
        self.eq_latex = _split_long_equation_latex(raw, max_len=65)

        if col_span is None:
            self.col_span = 2 if len(self.eq_latex) > _WIDE_LATEX_THRESHOLD else 1
        else:
            self.col_span = col_span


def _pack_rows(items: list) -> list:
    rows, current, remaining = [], [], GRID_COLS
    for item in items:
        span = min(item.col_span, GRID_COLS)
        if span > remaining:
            if current:
                rows.append(current)
            current, remaining = [], GRID_COLS
        current.append(item)
        remaining -= span
    if current:
        rows.append(current)
    return rows


def _emit_row(row: list) -> list:
    lines = []
    for i, item in enumerate(row):
        is_last = i == len(row) - 1
        width = f"{item.col_span * COL_UNIT:.4f}"
        # \noindent and \begin{minipage} on the same line — a newline between
        # them would become a space token that widens the row past \textwidth.
        prefix = r"\noindent" if i == 0 else ""
        lines.append(prefix + rf"\begin{{minipage}}[t]{{{width}\textwidth}}")
        lines.append(r"\noindent{\footnotesize\textbf{\mbox{" + item.equation.name + r"}}}")
        if item.col_span > 1:
            lines.append(r"\[\resizebox{\linewidth}{!}{$" + item.eq_latex + r"$}\]")
        else:
            lines.append(r"\[" + item.eq_latex + r"\]")
        lines.append(r"\end{minipage}" + ("" if is_last else "%"))
    # \par ends the paragraph (forces a real line break); \smallskip adds row gap.
    # \smallskip alone uses \vadjust in hmode and never breaks the paragraph.
    lines.append(r"\par\smallskip")
    return lines


def generate_layout_latex(items: list) -> str:
    lines = [
        r"\setlength{\parskip}{0pt}",
        r"\setlength{\parindent}{0pt}",
        r"\setlength{\abovedisplayskip}{2pt}",
        r"\setlength{\belowdisplayskip}{2pt}",
    ]
    for row in _pack_rows(items):
        lines.extend(_emit_row(row))
    return "\n".join(lines)


def generate_latex():
    kepler = KeplerianEquations()

    version = md.version("astranotes")
    generated_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    footer_text = f"AstraNotes v{version} — Generated {generated_utc}"

    # Add equations here in the order you want them to appear.
    # col_span is auto-detected from LaTeX string length; override with col_span=N.
    # Each row sums to GRID_COLS=4 column slots; wide equations span multiple slots.
    items = [
        LayoutItem(kepler.orbital_radius),
        LayoutItem(kepler.semi_latus_rectum),
        LayoutItem(kepler.radius_of_periapsis),
        LayoutItem(kepler.radius_of_apoapsis),
        LayoutItem(kepler.velocity_magnitude),
        LayoutItem(kepler.vis_viva),
        LayoutItem(kepler.circular_velocity),
        LayoutItem(kepler.escape_velocity),
        LayoutItem(kepler.angular_momentum),
        LayoutItem(kepler.mean_anomaly_elliptical),
        LayoutItem(kepler.mean_motion),
        LayoutItem(kepler.orbital_period),
        LayoutItem(kepler.eccentric_anomaly_wrt_true_anomaly),
        LayoutItem(kepler.flight_path_angle_wrt_eccentric_anomaly),
        LayoutItem(kepler.semi_latus_rectum_parabolic),
        LayoutItem(kepler.parabolic_anomaly_wrt_true_anomaly),
        LayoutItem(kepler.flight_path_angle_parabolic),
        LayoutItem(kepler.hyperbolic_anomaly_wrt_true_anomaly),
        LayoutItem(kepler.mean_anomaly_hyperbolic),
        LayoutItem(kepler.perifocal_radius_vector),
        LayoutItem(kepler.perifocal_velocity_vector),
        LayoutItem(kepler.perifocal_to_inertial_rotation_matrix, col_span=2),
        LayoutItem(kepler.inertial_radius_vector),
        LayoutItem(kepler.inertial_velocity_vector),
        LayoutItem(kepler.two_body_differential_equation),
        LayoutItem(kepler.equinoctial_ecc_cos_term),
        LayoutItem(kepler.equinoctial_ecc_sin_term),
        LayoutItem(kepler.equinoctial_inc_cos_term),
        LayoutItem(kepler.equinoctial_inc_sin_term),
        LayoutItem(kepler.mean_longitude),

    ]

    latex_lines = [
        r"\documentclass[10pt]{article}",
        r"\usepackage[landscape, top=0.5in, bottom=0.6in, left=0.6in, right=0.6in]{geometry}",
        r"\usepackage{amsmath}",
        r"\usepackage{graphicx}",
        r"\usepackage{titlesec}",
        r"\usepackage{multicol}",
        r"\usepackage{enumitem}",
        r"\usepackage{fancyhdr}",
        r"\usepackage{lastpage}",
        r"\pagestyle{fancy}",
        r"\fancyhf{}",
        rf"\fancyfoot[C]{{\footnotesize {footer_text}}}",
        r"\renewcommand{\headrulewidth}{0pt}",
        r"\renewcommand{\footrulewidth}{0.4pt}",
        r"\titlespacing*{\section}{0pt}{*0}{*0}",
        r"\titlespacing*{\subsection}{0pt}{*0}{*0}",
        r"\setlength{\parskip}{0pt}",
        r"\setlength{\parindent}{0pt}",
        r"\setlength{\abovedisplayskip}{5pt}",
        r"\setlength{\belowdisplayskip}{5pt}",
        r"\begin{document}",
        r"\vspace*{-1.5em}",
        r"{\small",
        r"\noindent",
        r"\textbf{AstraNotes Cheat Sheet: Keplerian Orbits} \quad --- \quad \textsc{SamTheGliderPilot}",
        r"}",
        r"\vspace{1em}",
        r"\section*{Keplerian Orbital Equations}",
        generate_layout_latex(items),
        r"\clearpage",
    ]

    # Sources page
    latex_lines.extend(render_sources_latex([EquationGroup('', [item.equation for item in items])]))
    latex_lines.append(r"\vspace{0.75em}")
    latex_lines.append(
        r"\noindent{\footnotesize\textbf{Note on atan2:} "
        r"This sheet uses $\mathrm{atan2}(y, x)$ (sine term/$y$ first, cosine term/$x$ second) "
        r"to preserve quadrant.}"
    )
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
    print(f"[X] PDF built at {os.path.join(BUILD_DIR, PDF_FILENAME)}")


def clean_aux_files():
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
