from pydantic import BaseModel, HttpUrl, field_validator
from typing import Optional
from datetime import datetime

class Event(BaseModel):
    venue: str
    title: str
    link: HttpUrl
    start_time: datetime
    raw_date_str: Optional[str] = None

    @field_validator('start_time', mode='before')
    @classmethod
    def validate_start_time(cls, v):
        if isinstance(v, datetime):
            return v
        # 如果传入的是字符串，我们可以在这里写通用的解析，
        # 但更推荐在每个爬虫内部解析好再传进来，因为每个站格式差太多
        return v

