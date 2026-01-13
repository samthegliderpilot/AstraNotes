# astrocalc/cheatsheet/sources_index.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

from astrocalc.util.source_ref import SourceRef
from astrocalc.util.equation_helpers import EquationGroup, EquationDefinition


@dataclass(frozen=True, slots=True)
class SourceWork:
    """
    Identifies a 'work' (book/paper/etc.) independent of per-equation location.
    This is the grouping key for a sources index.
    """
    authors: str
    title: str
    edition: Optional[str] = None
    year: Optional[int] = None
    publisher: Optional[str] = None

    @staticmethod
    def from_source(src: SourceRef) -> "SourceWork":
        return SourceWork(
            authors=src.authors,
            title=src.title,
            edition=src.edition,
            year=src.year,
            publisher=src.publisher,
        )


@dataclass(frozen=True, slots=True)
class SourceEntry:
    """
    One per equation, but grouped under a SourceWork.
    """
    equation_name: str
    group_name: str
    location: Optional[str] = None
    notes: Optional[str] = None


@dataclass(frozen=True, slots=True)
class SourceSection:
    """
    A SourceWork plus all entries (equations) that cite it.
    """
    work: SourceWork
    entries: Tuple[SourceEntry, ...]


def build_sources_index(
    equation_groups: Iterable[EquationGroup],
    *,
    include_group_name: bool = True,
    sort_sources: bool = True,
    sort_entries: bool = True,
) -> List[SourceSection]:
    """
    Build a sources index grouped by 'work' (authors/title/edition/year/publisher)
    with per-equation bullet entries containing (equation name, location, notes).

    UI-agnostic: returns a data structure suitable for both Jupyter and LaTeX renderers.

    Parameters
    ----------
    equation_groups:
        Iterable of EquationGroup (each has .name and .equations).
    include_group_name:
        If True, SourceEntry includes the group name where the equation appears.
    sort_sources:
        If True, sorts SourceSections by authors/title/edition/year/publisher.
    sort_entries:
        If True, sorts entries within each source by group name then equation name.

    Returns
    -------
    List[SourceSection]
    """
    grouped: Dict[SourceWork, List[SourceEntry]] = {}

    for group in equation_groups:
        gname = group.name
        for eq in group.equations:
            if not isinstance(eq, EquationDefinition):
                # Defensive: if someone accidentally passed a callback or similar
                raise TypeError(f"Expected EquationDefinition, got {type(eq).__name__}")

            src = eq.source
            if not isinstance(src, SourceRef):
                # You said you're fully adopting SourceRef; fail loudly if something slips through.
                raise TypeError(
                    f"Equation '{eq.name}' has source type {type(src).__name__}, expected SourceRef"
                )

            work = SourceWork.from_source(src)

            entry = SourceEntry(
                equation_name=eq.name,
                group_name=gname if include_group_name else "",
                location=src.location,
                notes=src.notes,
            )

            grouped.setdefault(work, []).append(entry)

    # Sorting helpers
    def source_sort_key(w: SourceWork):
        return (
            (w.authors or "").lower(),
            (w.title or "").lower(),
            (w.edition or "").lower(),
            w.year if w.year is not None else 10**9,
            (w.publisher or "").lower(),
        )

    def entry_sort_key(e: SourceEntry):
        return (
            (e.group_name or "").lower(),
            (e.equation_name or "").lower(),
        )

    sections: List[SourceSection] = []
    works = list(grouped.keys())

    if sort_sources:
        works.sort(key=source_sort_key)

    for w in works:
        entries = grouped[w]
        if sort_entries:
            entries.sort(key=entry_sort_key)
        sections.append(SourceSection(work=w, entries=tuple(entries)))

    return sections


def format_work_compact(work: SourceWork) -> str:
    """
    Small helper you can reuse in renderers.
    Returns a compact one-line identification of the work.
    """
    parts: List[str] = [work.authors, work.title]
    if work.edition:
        parts.append(work.edition)
    if work.year is not None:
        parts.append(str(work.year))
    if work.publisher:
        parts.append(work.publisher)
    return " — ".join([p for p in parts if p])


def format_entry_compact(entry: SourceEntry, *, show_group: bool = True) -> str:
    """
    Small helper you can reuse in renderers.
    Returns a compact single-line representation of a SourceEntry.
    """
    left = entry.equation_name
    if show_group and entry.group_name:
        left += f" [{entry.group_name}]"

    tail_parts: List[str] = []
    if entry.location:
        tail_parts.append(entry.location)
    if entry.notes:
        tail_parts.append(entry.notes)

    if tail_parts:
        return left + " — " + " — ".join(tail_parts)
    return left
