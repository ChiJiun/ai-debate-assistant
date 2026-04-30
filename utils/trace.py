from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TraceEvent:
    step: str
    status: str
    message: str
    timestamp: str


def make_trace(step: str, status: str, message: str) -> TraceEvent:
    return TraceEvent(
        step=step,
        status=status,
        message=message,
        timestamp=datetime.now().strftime("%H:%M:%S"),
    )
