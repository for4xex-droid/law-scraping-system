from typing import List, Optional

from pydantic import BaseModel
from datetime import datetime


class Law(BaseModel):
    law_id: str
    law_num: str
    law_full_name: str
    last_updated: datetime


class Article(BaseModel):
    law_id: str
    article_number: str
    hierarchy: str
    content: str
    raw_xml: Optional[str] = None
