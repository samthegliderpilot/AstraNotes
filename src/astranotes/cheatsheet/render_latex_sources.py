# astranotes/cheatsheet/render_latex_sources.py
from __future__ import annotations

from typing import Iterable, List

from astranotes.cheatsheet.sources_index import build_sources_index, SourceSection


def _latex_escape(s: str) -> str:
    """
    Escape LaTeX special characters for safe insertion into text mode.
    (Not math mode.)
    """
    if s is None:
        return ""
    repl = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(repl.get(ch, ch) for ch in str(s))


def render_sources_latex(
    equation_groups,
    *,
    section_title: str = "Sources",
    include_group_name: bool = False,  # you said equation name only; group tag off by default
) -> List[str]:
    """
    Return LaTeX lines for a sources section grouped by SourceWork.

    The caller controls pagination (e.g., ending multicols and issuing \\clearpage).
    """
    sections: List[SourceSection] = build_sources_index(
        equation_groups,
        include_group_name=include_group_name,
        sort_sources=True,
        sort_entries=True,
    )

    lines: List[str] = []
    lines.append(rf"\section*{{{_latex_escape(section_title)}}}")
    lines.append(r"\setlength{\parskip}{0pt}")
    lines.append(r"\setlength{\parindent}{0pt}")
    lines.append(r"\setlength{\itemsep}{0pt}")
    lines.append(r"\setlength{\topsep}{2pt}")

    for sec in sections:
        w = sec.work

        # Work header (authors — title — edition — year — publisher)
        parts = []
        if w.authors:
            parts.append(_latex_escape(w.authors))
        if w.title:
            parts.append(rf"\textit{{{_latex_escape(w.title)}}}")
        if w.edition:
            parts.append(_latex_escape(w.edition))
        if w.year is not None:
            parts.append(str(w.year))
        if w.publisher:
            parts.append(_latex_escape(w.publisher))

        header = " --- ".join([p for p in parts if p])
        lines.append(r"\subsection*{" + header + r"}")

        lines.append(r"\begin{itemize}")
        for e in sec.entries:
            # left side: equation name (already what you want)
            left = _latex_escape(e.equation_name)

            tail_parts = []
            if e.location:
                tail_parts.append(_latex_escape(e.location))
            if e.notes:
                tail_parts.append(_latex_escape(e.notes))

            if tail_parts:
                tail = " --- " + " --- ".join(tail_parts)
            else:
                tail = ""

            lines.append(rf"\item \textbf{{{left}}}{tail}")

        lines.append(r"\end{itemize}")
        lines.append(r"\vspace{0.5em}")

    return lines
