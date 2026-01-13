from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Union

@dataclass(frozen=True, slots=True)
class SourceRef:
    authors: str
    title: str
    year: Optional[int] = None
    edition: Optional[str] = None
    publisher: Optional[str] = None
    location: Optional[str] = None   # e.g. "p. 27, Eq. 1-22" or "Sec. 2.3"
    notes: Optional[str] = None      # e.g. "simplified from ..."

    def compact(self) -> str:
        parts = [self.authors, self.title]
        if self.edition:
            parts.append(self.edition)
        if self.year:
            parts.append(str(self.year))
        s = " — ".join(parts)
        if self.location:
            s += f" ({self.location})"
        return s

    def full(self) -> str:
        s = self.compact()
        if self.publisher:
            s += f". {self.publisher}."
        if self.notes:
            s += f" Notes: {self.notes}"
        return s