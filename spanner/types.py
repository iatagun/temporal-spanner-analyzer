from __future__ import annotations
import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)

VertexID = Any  # int or str


@dataclass
class TemporalGraph:
    V: set[VertexID]
    label: dict[tuple[VertexID, VertexID], float]

    def __post_init__(self):
        self.V = {str(v) for v in self.V}
        self._canonicalize()

    def _canonicalize(self):
        normalized: dict[tuple[str, str], float] = {}
        for (u, v), t in self.label.items():
            a, b = str(u), str(v)
            key = (a, b) if a <= b else (b, a)
            if key in normalized:
                existing = normalized[key]
                if t < existing:
                    normalized[key] = t
                    logger.warning(
                        "Duplicate edge (%s, %s) in TemporalGraph: "
                        "keeping earlier label %.4f (discarding %.4f)",
                        a, b, t, existing,
                    )
            else:
                normalized[key] = t
        self.label = normalized

    def copy(self) -> TemporalGraph:
        return TemporalGraph(set(self.V), dict(self.label))


@dataclass
class TemporalBiClique:
    S: list[VertexID]
    T: list[VertexID]
    label: dict[tuple[VertexID, VertexID], float]

    def __post_init__(self):
        self.S = [str(v) for v in self.S]
        self.T = [str(v) for v in self.T]
        normalized: dict[tuple[str, str], float] = {}
        for (u, v), t in self.label.items():
            a, b = str(u), str(v)
            key = (a, b) if a <= b else (b, a)
            if key in normalized:
                existing = normalized[key]
                if t < existing:
                    normalized[key] = t
            else:
                normalized[key] = t
        self.label = normalized

    def copy(self) -> TemporalBiClique:
        return TemporalBiClique(list(self.S), list(self.T), dict(self.label))
