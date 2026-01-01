from typing import List
from pydantic import BaseModel

class CourseResponse(BaseModel):
    courses: List[str]
    university: str