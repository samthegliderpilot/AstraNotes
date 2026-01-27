# astranotes/cheatsheet/jupyter_sources_render.py
from __future__ import annotations

import ipywidgets as widgets
from html import escape
from typing import Iterable, Optional

from astranotes.cheatsheet.sources_index import (
    SourceSection,
    build_sources_index,
)

def render_sources_jupyter(
    equation_groups,
    *,
    title: str = "Sources",
    include_group_name: bool = True,
    use_full_width: bool = True,
) -> widgets.VBox:
    """
    Render a sources "page" for Jupyter, grouped by SourceWork and listing
    per-equation entries (equation name + optional [group] + location/notes).

    Parameters
    ----------
    equation_groups:
        Iterable[EquationGroup]
    title:
        Header text for the section.
    include_group_name:
        Include the equation-group tag like [Elliptical Orbit Equations] in each bullet.
    use_full_width:
        Set VBox width to 100%.

    Returns
    -------
    widgets.VBox
    """
    sections = build_sources_index(
        equation_groups,
        include_group_name=include_group_name,
        sort_sources=True,
        sort_entries=True,
    )
    return render_sources_index_jupyter(
        sections,
        title=title,
        include_group_name=include_group_name,
        use_full_width=use_full_width,
    )


def render_sources_index_jupyter(
    sections: Iterable[SourceSection],
    *,
    title: str = "Sources",
    include_group_name: bool = True,
    use_full_width: bool = True,
) -> widgets.VBox:
    """
    Render a prebuilt sources index (output of build_sources_index) as a Jupyter widget.
    """
    blocks = []

    if title:
        blocks.append(widgets.HTML(f"<h3 style='margin-top:10px'>{escape(title)}</h3>"))

    for sec in sections:
        w = sec.work

        # Work header line
        header_parts = []
        if w.authors:
            header_parts.append(escape(w.authors))
        if w.title:
            header_parts.append(f"<i>{escape(w.title)}</i>")
        if w.edition:
            header_parts.append(escape(w.edition))
        if w.year is not None:
            header_parts.append(str(w.year))
        if w.publisher:
            header_parts.append(escape(w.publisher))

        header_html = " — ".join(header_parts)

        # Entries list
        li_parts = []
        for e in sec.entries:
            left = escape(e.equation_name)

            if include_group_name and e.group_name:
                left += f" <span style='color:#666'>[{escape(e.group_name)}]</span>"

            tail_parts = []
            if e.location:
                tail_parts.append(escape(e.location))
            if e.notes:
                tail_parts.append(escape(e.notes))

            tail = ""
            if tail_parts:
                tail = " — " + " — ".join(tail_parts)

            li_parts.append(f"<li style='margin: 2px 0;'><b>{left}</b>{tail}</li>")

        block_html = (
            "<div style='margin-bottom: 12px;'>"
            f"  <div style='font-weight: 600; margin-top: 10px;'>{header_html}</div>"
            "  <ul style='margin-top: 4px; margin-bottom: 0px; padding-left: 22px;'>"
            f"    {''.join(li_parts)}"
            "  </ul>"
            "</div>"
        )

        blocks.append(widgets.HTML(block_html))

    box = widgets.VBox(blocks)
    if use_full_width:
        box.layout = widgets.Layout(width="100%")
    return box
