import base64
from io import BytesIO
import json
from PIL import Image
from typing import Dict
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, Request, Query, Response
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, validator
from typing import List, Dict, Union
import logging
from pydantic import BaseModel
from typing import List
import pandas as pd
from reports import Reports
from models import GoogleFormsTranslationMap, QuestionnaireDataModel, DashboardDataModel
from fastapi.middleware.cors import CORSMiddleware
import os
from data_processor import DataProcessor
from pathlib import Path

app = FastAPI()

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost,http://localhost:80,http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASIC_USER = os.environ.get("BASIC_AUTH_USER")
BASIC_PASS = os.environ.get("BASIC_AUTH_PASS")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET")

base_path = Path("/data")

class RegisterFormInputs(BaseModel):
    email: str
    password: str
    isAdmin: bool
class LoginFormInputs(BaseModel):
    email: str
    password: str

class CourseResponse(BaseModel):
    courses: List[str]
    university: str
    
class DepartmentCoursesResponse(BaseModel):
    departments: Dict[str, List[str]]

class FilePath(BaseModel):
    path: str

@app.post("/api/submit/{university}")
async def submit_questionaire(university: str, data: QuestionnaireDataModel):
    try:
        # Save data to Excel
        if DataProcessor.save_and_evaluate(data, university):
            return {"status": "success", "message": "Survey submitted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to save survey data")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DashboardData(BaseModel):
    diet: str
    ethnic_group: str
    hours_per_week_university_work: float
    family_earning_class: str
    quality_of_life: str
    alcohol_consumption: str
    personality_type: str
    stress_in_general: str
    well_hydrated: str
    exercise_per_week: float
    known_disabilities: str
    work_hours_per_week: float
    financial_support: str
    form_of_employment: str
    financial_problems: str
    home_country: str
    age: float
    course_of_study: str
    stress_before_exams: str
    feel_afraid: str
    timetable_preference: str
    timetable_reasons: str
    timetable_impact: str
    total_device_hours: float
    hours_socialmedia: float
    level_of_study: str
    gender: str
    physical_activities: str
    hours_between_lectures: float
    hours_per_week_lectures: float
    hours_socialising: float
    actual: str
    student_type_time: str
    student_type_location: str
    cost_of_study: float
    sense_of_belonging: str
    mental_health_activities: str
    predictions: float
    captured_at: str

class ReportRequest(BaseModel):
    data: List[DashboardData]
    charts: Dict[str, str]

    @validator('charts')
    def validate_charts(cls, v):
        for key, value in v.items():
            if not value.startswith('data:image'):
                raise ValueError(f'Invalid image format for {key}')
        return v

@app.post("/api/reports")
async def generate_reports(request: ReportRequest):
    try:
        df = pd.DataFrame([item.dict() for item in request.data])
        reports = Reports(df)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        
        # Decode chart images
        chart_images = {}
        for key, chart in request.charts.items():
            if isinstance(chart, str) and chart.startswith("data:image/png;base64,"):
                chart_images[key] = chart
        
        # Generate PDF report and save it temporarily
        report_path = f"{base_path}/reports/Mental_Health_Report_{timestamp}.pdf"
        reports.generate_pdf_report(report_path, chart_images)
        
        return {"message": "Report generated", "report_url": f"/api/reports/view/{timestamp}"}
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/api/reports/view/{timestamp}")
async def view_report(timestamp: str):
    report_path = f"{base_path}/reports/Mental_Health_Report_{timestamp}.pdf"
    if os.path.exists(report_path):
        return FileResponse(report_path, media_type='application/pdf', filename=f"Mental_Health_Report_{timestamp}.pdf")
    else:
        raise HTTPException(status_code=404, detail="Report not found")

@app.delete("/api/reports/delete/{timestamp}")
async def delete_report(timestamp: str):
    report_path = f"{base_path}/reports/Mental_Health_Report_{timestamp}.pdf"
    if os.path.exists(report_path):
        os.remove(report_path)
        return {"message": "Report deleted"}
    else:
        raise HTTPException(status_code=404, detail="Report not found")



@app.middleware("http")
async def security_gate(request: Request, call_next):
    path = request.url.path

    public_prefixes = (
        "/api/login",
        "/api/register",
        "/api/courses",
        "/api/departments",
        "/api/dashboard",
        "/api/reports/view",
        "/api/submit",
    )
    if path.startswith(public_prefixes):
        return await call_next(request)

    if path.startswith("/webhook"):
        secret = request.headers.get("x-webhook-secret") or request.query_params.get("secret")
        if WEBHOOK_SECRET and secret == WEBHOOK_SECRET:
            return await call_next(request)
        return JSONResponse({"detail": "Unauthorized webhook"}, status_code=401)

    if ACCESS_TOKEN:
        token = request.headers.get("x-access-token") or request.headers.get("authorization", "").replace("Bearer ", "").strip()
        if token and token == ACCESS_TOKEN:
            return await call_next(request)

    if BASIC_USER and BASIC_PASS:
        auth = request.headers.get("authorization") or ""
        parts = auth.split(" ", 1)
        if len(parts) == 2 and parts[0] == "Basic":
            try:
                userpass = base64.b64decode(parts[1]).decode("utf-8")
                u, p = userpass.split(":", 1)
                if u == BASIC_USER and p == BASIC_PASS:
                    return await call_next(request)
            except Exception:
                pass
        return JSONResponse(
            {"detail": "Authentication required"},
            status_code=401,
            headers={"WWW-Authenticate": 'Basic realm="Protected"'}
        )

    return await call_next(request)

@app.get("/api/courses/{university}", response_model=CourseResponse)
async def get_courses(university: str):
    try:
        # Construct file path
        file_path = f"{base_path}/{university.lower()}/{university.lower()}_courses.xlsx"
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"Course file not found for {university}")
        
        # Read Excel file
        df = pd.read_excel(file_path)
        
        # Convert to list of unique courses
        courses = df['Courses'].dropna().unique().tolist()
        
        return {
            "courses": courses,
            "university": university
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/departments/{university}", response_model=DepartmentCoursesResponse)
async def get_departments(university: str):
    print(university )
    try:
        file_path = f"{base_path}/{university.lower()}/{university.lower()}_courses.xlsx"
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"Course file not found for {university}")
        
        df = pd.read_excel(file_path)
        department_course_map = {}
        
        for index, row in df.iterrows():
            department = str(row['Departments']).strip() if pd.notna(row['Departments']) else None
            course = str(row['Courses']).strip() if pd.notna(row['Courses']) else None
            
            if department and course:
                if department not in department_course_map:
                    department_course_map[department] = []
                department_course_map[department].append(course)
        
        return {
            "university": university,
            "departments": department_course_map
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_user_data():
    file_path = f"{base_path}/login/login_data.xlsx"
    if os.path.exists(file_path):
        df = pd.read_excel(file_path, header=0)
        return df
    else:
        return pd.DataFrame(columns=["email", "password", "isAdmin", "university"])

@app.post("/api/login")
async def login(data: LoginFormInputs):
    try:
        df = get_user_data()
        print("Input data:", data.email, data.password)
        print("DataFrame before comparison:", df)
        
        # Convert values to string and handle NaN
        df['email'] = df['email'].fillna('').astype(str)
        df['password'] = df['password'].fillna('').astype(str)
        df['university'] = df['university'].fillna('').astype(str)
        
        # Clean input data
        clean_email = str(data.email).strip()
        clean_password = str(data.password).strip()
        
        # Compare values
        user = df[
            (df['email'].str.strip() == clean_email) & 
            (df['password'].str.strip() == clean_password)
        ]
        
        # print("Matched user:", user)
        
        if not user.empty:
            return {
                "message": "Login successful",
                "isAdmin": bool(user.iloc[0]['isAdmin']),
                "university": user.iloc[0]['university']
            }
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
            
    except Exception as e:
        print(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Login error: {str(e)}")

def save_user_data(df):
    file_path = f"{base_path}/login/login_data.xlsx"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    df.to_excel(file_path, index=False)

@app.post("/api/register")
async def register(data: RegisterFormInputs):
    try:
        df = get_user_data()
        print("Registration attempt for:", data.email)
        
        if data.email in df['email'].values:
            raise HTTPException(status_code=400, detail="User already exists")
        
        new_user = pd.DataFrame([{
            'email': str(data.email).strip(),
            'password': str(data.password).strip(),
            'isAdmin': bool(data.isAdmin)
        }])
        
        df = pd.concat([df, new_user], ignore_index=True)
        save_user_data(df)
        
        return {"message": "User registered successfully"}
    except Exception as e:
        print(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Registration error: {str(e)}")

@app.delete("/api/deleteUser")
async def delete_user(email: str):
    try:
        df = get_user_data()
        print("Delete attempt for:", email)
        
        if email not in df['email'].values:
            raise HTTPException(status_code=404, detail="User not found")
        
        df = df[df['email'] != email]
        save_user_data(df)
        
        return {"message": "User deleted successfully"}
    except Exception as e:
        print(f"Delete error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Delete error: {str(e)}")

def process_excel_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    
    numeric_columns = {
        'hours_per_week_university_work': 0,
        'exercise_per_week': 0,
        'work_hours_per_week': 0,
        'age': 0,
        'total_device_hours': 0,
        'hours_socialmedia': 0,
        'hours_between_lectures': 0,
        'hours_per_week_lectures': 0,
        'hours_socialising': 0,
        'cost_of_study': 0
    }
    
    for col, default in numeric_columns.items():
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(default).astype(int)
        else:
            df[col] = default
    
    for col in df.columns:
        if col not in numeric_columns:
            df[col] = df[col].fillna('Not Provided')
    
    # print("Processed columns:", df.columns.tolist())
    # print("Data types:", df.dtypes)
    
    return df

@app.get("/api/dashboard")
async def get_dashboard_data(university: str = Query(None)):
    try:
        file_path = f"{base_path}/merged/merged_data.xlsx"
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Data file not found")
        
        df = pd.read_excel(file_path, header=None)
        print("Original columns:", df.columns.tolist())
        column_ids = df.iloc[1].copy()
        df_cleaned = df.iloc[2:] 
        df_cleaned.columns = column_ids
        
        df_processed = process_excel_data(df_cleaned)
        
        if university and university != 'All':
            df_processed = df_processed[df_processed['source'] == university]
        
        data = df_processed.to_dict('records')
        
        return {"data": data}
        
    except Exception as e:
        print(f"Dashboard error: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail={"error": "Failed to fetch dashboard data", "details": str(e)}
        )

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    university = data.get("university") or "UAL"
    form_answers = data.get("answers") or data.get("formData") or data.get("namedValues") or {}

    mapped_data = {}
    for key, value in form_answers.items():
        if key in GoogleFormsTranslationMap:
            mapped_field = GoogleFormsTranslationMap[key]
            mapped_data[mapped_field] = value
        else:
            print(f"Unmapped question: {key}")

    questionnaire_data = QuestionnaireDataModel(
        answers=[{"id": k, "answer": v} for k, v in mapped_data.items()],
        source= university
    )
    
    return await webhook_submit_questionnaire(university, questionnaire_data)

async def webhook_submit_questionnaire(university: str, data: QuestionnaireDataModel):
    try:
        if DataProcessor.save_and_evaluate(data, university):
            return {"status": "success", "message": "Survey submitted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to save survey data")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))