from __future__ import annotations
import httpx
from typing import Optional

class OllamaLLM:
    def __init__(self, model: str = "llama3.1:8b", base_url: str = "http://127.0.0.1:11434/api"):
        self.model = model
        self.base_url = base_url.rstrip("/")

    async def generate(self, prompt: str, *, system: Optional[str] = None) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }
        if system:
            payload["system"] = system

        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(f"{self.base_url}/generate", json=payload)
            r.raise_for_status()
            data = r.json()
            return data.get("response", "").strip()
