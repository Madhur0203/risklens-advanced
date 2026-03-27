from pydantic import BaseModel
from typing import Optional


class FeedbackIn(BaseModel):
    case_id: str
    analyst_label: str
    analyst_comment: Optional[str] = None
