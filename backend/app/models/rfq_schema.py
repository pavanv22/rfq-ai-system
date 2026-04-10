from pydantic import BaseModel
from typing import List

class RFQ(BaseModel):
    project_name: str
    budget: float
    timeline_weeks: int
    requirements: List[str]