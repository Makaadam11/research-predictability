import asyncio
import base64
import hashlib
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Dict, List

import pandas as pd
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, field_validator

from backend.models.account import LoginFormInputs, RegisterFormInputs
from backend.models.dashboard import DashboardData
from backend.models.questionnaire import QuestionnaireDataModel
from backend.models.report import ReportRequest
from data_processor import DataProcessor
from reports import Reports

app = FastAPI()

# Initialize thread pool executor for background tasks
executor = ThreadPoolExecutor(max_workers=5)

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost,http://localhost:80,http://localhost:3000,http://127.0.0.1"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,  # Cache preflight responses for 1 hour
)

BASIC_USER = os.environ.get("BASIC_AUTH_USER")
BASIC_PASS = os.environ.get("BASIC_AUTH_PASS")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET")

base_path = Path("../data")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# class RateLimitMiddleware(BaseHTTPMiddleware):
#     def __init__(self, app, max_concurrent=5):
#         super().__init__(app)
#         self.semaphore = asyncio.Semaphore(max_concurrent)

#     async def dispatch(self, request: Request, call_next):
#         async with self.semaphore:
#             return await call_next(request)

# app.add_middleware(
#     RateLimitMiddleware,
#     max_concurrent=5
# )

@app.middleware("http")
async def security_gate(request: Request, call_next):
    path = request.url.path

    if request.method == "OPTIONS":
        response = await call_next(request)
        return response
    
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

@app.post("/api/submit/{university}")
async def submit_questionaire(university: str, data: QuestionnaireDataModel):
    try:
        processor = DataProcessor()
        if processor.save_and_evaluate(data, university):
            return {"status": "success", "message": "Survey submitted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to save survey data")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


    
@app.post("/api/reports")
async def generate_reports(request: ReportRequest):
    try:
        reports: Reports = Reports()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        async def generate_in_background():
            report_df = pd.DataFrame([data.model_dump() for data in request.data])
            output_path = f"{base_path}/reports/Mental_Health_Report_{timestamp}.pdf"

            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                executor,
                reports.generate_report_pdf,
                report_df,
                output_path,
                # request.charts
            )
        
        await generate_in_background()
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
    

@app.get("/api/universities", response_model=List[str])
async def get_universities():
    try:
        file_path = "../data/universities/universities.xlsx"
        
        if not os.path.exists(file_path):
            print(f"Universities file not found at {file_path}")
            raise HTTPException(status_code=404, detail="Universities file not found")
        
        # Read Excel file
        print(f"Reading universities from {file_path}")
        df = pd.read_excel(file_path)
        
        # Debug the dataframe
        print(f"DataFrame shape: {df.shape}")
        print(f"DataFrame columns: {df.columns.tolist()}")
        print(f"DataFrame first few rows: {df.head().to_string()}")
        
        # Extract universities as a list
        universities = df.iloc[:, 0].dropna().unique().tolist()
        
        print(f"Extracted universities: {universities}")
        
        # If UAL is missing, add it manually
        if 'UAL' not in universities:
            universities.append('UAL')
            print("Added UAL to universities list")
            
        return universities
    except Exception as e:
        print(f"Error in get_universities: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

class CourseResponse(BaseModel):
    courses: List[str]
    university: str
    
@app.get("/api/courses/{university}", response_model=CourseResponse)
async def get_courses(university: str):
    try:
        # Construct file path
        file_path = f"../data/{university.lower()}/{university.lower()}_courses.xlsx"
        
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

class DepartmentCoursesResponse(BaseModel):
    departments: Dict[str, List[str]]

@app.get("/api/departments/All", response_model=DepartmentCoursesResponse)
async def get_all_departments():
    try:
        # Get list of universities first
        file_path = "../data/universities/universities.xlsx"
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Universities file not found")
        
        df_unis = pd.read_excel(file_path)
        universities = df_unis.iloc[:, 0].dropna().unique().tolist()
        
        # Ensure both UAL and SOL are included
        if 'UAL' not in universities:
            universities.append('UAL')
        if 'SOL' not in universities:
            universities.append('SOL')
            
        print(f"Processing universities for departments: {universities}")
        
        all_departments = {}
        
        # Loop through each university to collect departments and courses
        for university in universities:
            try:
                print(f"Processing university: {university}")
                uni_file_path = f"../data/{university.lower()}/{university.lower()}_courses.xlsx"
                
                if os.path.exists(uni_file_path):
                    print(f"Found course file for {university}")
                    df = pd.read_excel(uni_file_path)
                    
                    for index, row in df.iterrows():
                        department = str(row['Departments']).strip() if pd.notna(row['Departments']) else None
                        course = str(row['Courses']).strip() if pd.notna(row['Courses']) else None
                        
                        if department and course:
                            # Add university prefix to department name for clarity
                            dept_key = f"{university} - {department}"
                            
                            if dept_key not in all_departments:
                                all_departments[dept_key] = []
                            
                            all_departments[dept_key].append(course)
                else:
                    print(f"Course file not found for {university}: {uni_file_path}")
            except Exception as e:
                print(f"Error processing university {university}: {str(e)}")
                continue
        
        print(f"All departments: {all_departments.keys()}")
        return {
            "university": "All",
            "departments": all_departments
        }
    except Exception as e:
        print(f"Error in get_all_departments: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/api/departments/{university}", response_model=DepartmentCoursesResponse)
async def get_departments(university: str):
    print(university )
    try:
        file_path = f"../data/{university.lower()}/{university.lower()}_courses.xlsx"
        
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
        
        df['email'] = df['email'].fillna('').astype(str)
        df['password'] = df['password'].fillna('').astype(str)
        df['university'] = df['university'].fillna('').astype(str)
        
        clean_email = str(data.email).strip()
        clean_password = str(data.password).strip()
        
        user = df[
            (df['email'].str.strip() == clean_email) & 
            (df['password'].str.strip() == clean_password)
        ]
        
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
    
    return df

@lru_cache(maxsize=10)
def get_cached_dashboard_data(university: str, file_hash: str):
    """Cache dashboard data by university and file modification time"""
    file_path = f"{base_path}/merged/merged_data.xlsx"
    df = pd.read_excel(file_path, header=None)
    column_ids = df.iloc[1].copy()
    df_cleaned = df.iloc[2:] 
    df_cleaned.columns = column_ids
    df_processed = process_excel_data(df_cleaned)
    
    if university != 'All':
        df_processed = df_processed[df_processed['source'] == university]
    
    return df_processed.to_dict('records')

@app.get("/api/dashboard")
async def get_dashboard_data(university: str = Query(None)):
    try:
        file_path = f"{base_path}/merged/merged_data.xlsx"
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Data file not found")
        
        file_mtime = os.path.getmtime(file_path)
        file_hash = hashlib.md5(f"{file_path}{file_mtime}".encode()).hexdigest()
        
        data = await asyncio.to_thread(
            get_cached_dashboard_data,
            university or 'All',
            file_hash
        )
        
        return {"data": data}
        
    except Exception as e:
        print(f"Dashboard error: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail={"error": "Failed to fetch dashboard data", "details": str(e)}
        )