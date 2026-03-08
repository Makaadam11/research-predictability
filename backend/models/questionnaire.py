from pydantic import BaseModel
from typing import Optional, List

class QuestionnaireDataModel(BaseModel):
    answers: List[dict]
    source: str
    
class QuestionnaireColumnsModel(BaseModel):
    diet: str
    ethnic_group: str
    hours_per_week_university_work: int
    family_earning_class: str
    quality_of_life: str
    alcohol_consumption: str
    personality_type: str
    stress_in_general: List[str]
    well_hydrated: str
    exercise_per_week: int
    known_disabilities: str
    work_hours_per_week: int
    financial_support: str
    form_of_employment: str
    financial_problems: str
    home_country: str
    age: int
    course_of_study: str
    stress_before_exams: str
    feel_afraid: str
    timetable_preference: str
    timetable_reasons: str
    timetable_impact: str
    total_device_hours: int
    hours_socialmedia: int
    level_of_study: str
    gender: str
    physical_activities: str
    hours_between_lectures: int
    hours_per_week_lectures: int
    hours_socialising: int
    actual: str
    student_type_time: str
    student_type_location: str
    cost_of_study: int
    sense_of_belonging: str
    mental_health_activities: str
    source: Optional[str]
    predictions: Optional[int]
    captured_at: Optional[str]