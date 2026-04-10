from pydantic import BaseModel
from typing import List

class RFQ(BaseModel):
    title: str
    scope: str
    timelines: str
    line_items: List[str]