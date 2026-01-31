from __future__ import annotations
from typing import Protocol, Optional, Dict, Any

class LLM(Protocol):
    async def generate(self, prompt: str, *, system: Optional[str] = None) -> str: ...
