from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class RunRequest(BaseModel):
    title: str
    acceptance_criteria: List[str]
    budget_usd: float = Field(gt=0)
    weights: Optional[Dict[str, float]] = None
    use_llm: bool = True
    model: str = "llama3.1:8b"
