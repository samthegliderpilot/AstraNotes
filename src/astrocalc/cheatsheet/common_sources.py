from __future__ import annotations
from typing import Optional
from astrocalc.util.source_ref import SourceRef

def vallado_4e(location: str, notes: Optional[str] = None) -> SourceRef:
    return SourceRef(
        authors="Vallado",
        title="Fundamentals of Astrodynamics and Applications",
        edition="4th Edition",
        location=location,
        notes=notes,
    )

def bates_mueller_white(location: str, notes: Optional[str] = None) -> SourceRef:
    return SourceRef(
        authors="Bates, Mueller, White",
        title="Fundamentals of Astrodynamics",
        location=location,
        notes=notes,
    )
