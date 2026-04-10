from typing import List, Optional
from pydantic import BaseModel

class VendorData(BaseModel):
    vendor_name: str
    total_cost: float
    currency: str = "USD"
    timeline_weeks: Optional[int]
    scope_coverage: List[str] = []
    compliance_score: Optional[float] = 0
    source_file: Optional[str] = None