from typing import Dict, List
from pydantic import BaseModel

class DepartmentCoursesResponse(BaseModel):
    departments: Dict[str, List[str]]