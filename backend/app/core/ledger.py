from __future__ import annotations
from datetime import datetime, timezone
from uuid import uuid4
from typing import Any, Dict, List
from .models import Event

class Ledger:
    def __init__(self, run_id: str | None = None):
        self.run_id = run_id or str(uuid4())
        self._seq = 0
        self.events: List[Event] = []

    def add(self, type: str, summary: str, *, round: int = 0, data: Dict[str, Any] | None = None):
        self._seq += 1
        ev = Event(
            run_id=self.run_id,
            seq=self._seq,
            type=type,  # validated by EventType literal
            ts=datetime.now(timezone.utc).isoformat(),
            round=round,
            summary=summary,
            data=data or {},
        )
        self.events.append(ev)
        return ev
