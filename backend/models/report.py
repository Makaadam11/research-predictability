from typing import Dict, List

from models.dashboard import DashboardData
from pydantic import BaseModel, field_validator

class ReportRequest(BaseModel):
    data: List[DashboardData]
    charts: Dict[str, str]

    @field_validator('charts')
    def validate_charts(cls, v):
        for key, value in v.items():
            if not value.startswith('data:image'):
                raise ValueError(f'Invalid image format for {key}')
        return v