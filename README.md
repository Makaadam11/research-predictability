# Predictability - Student Mental Health Analytics Platform

A full-stack web application that collects student mental health survey data (via Qualtrics-style questionnaires), applies machine learning models to predict mental health proneness, and presents actionable insights through an interactive analytics dashboard and AI-generated reports.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Environment Variables](#environment-variables)
  - [Local Development](#local-development)
  - [Docker Deployment](#docker-deployment)
- [Machine Learning Pipeline](#machine-learning-pipeline)
- [API Reference](#api-reference)
- [Dashboard & Visualization](#dashboard--visualization)
- [Report Generation](#report-generation)
- [License](#license)

---

## Overview

**Predictability** is designed to help universities identify students who may be at risk of mental health issues. The system works in three stages:

1. **Data Collection** - Students complete a 37-question survey covering demographics, academic context, finances, lifestyle, psychological factors, and technology usage.
2. **ML Prediction** - Trained machine learning models (Random Forest, Neural Network) classify each respondent as prone or not prone to mental health issues.
3. **Analytics & Reporting** - Staff explore results via an interactive dashboard with filterable charts, geographic maps, and exportable data. AI-powered PDF reports provide narrative analysis and actionable recommendations.

The platform supports multiple universities (currently UAL and SOL) with independent data pipelines that merge into a unified dataset for cross-institutional analysis.

---

## Key Features

### Questionnaire System
- 37-question comprehensive mental health survey
- Categories: demographics, academics, finances, lifestyle, psychology, technology
- Multi-university support with dynamic question loading
- Multiple input types: single/multi-select, sliders, dropdowns, text fields
- Real-time validation and submission

### ML-Based Prediction Engine
- **Random Forest** and **Neural Network (MLP)** classifiers
- Models trained with and without **SMOTE** (Synthetic Minority Oversampling) for balanced classification
- 38+ engineered features across numeric and categorical variables
- Hyperparameter tuning via RandomizedSearchCV with 5-fold cross-validation
- Binary prediction output: prone (1) vs. not prone (0) to mental health issues

### Interactive Dashboard
- Real-time data visualization with filterable charts
- **Demographics**: age, gender, ethnicity, country heat map, student type
- **Academic Context**: course distribution, study hours, lecture frequency, timetable preferences
- **Financial Factors**: support methods, employment, financial stress, cost of study
- **Lifestyle & Behaviour**: exercise, diet, substance use, hydration, sleep
- **Psychological Factors**: stress levels, personality type, sense of belonging, quality of life
- **Technology Usage**: device hours, social media patterns
- Multi-select filtering by university, department, and all categorical variables
- Export filtered data as Excel/CSV

### AI-Powered Report Generation
- Automated PDF reports with narrative insights generated via Groq LLM (Llama 3.1)
- Sections: executive summary, demographic analysis, academic factors, financial analysis, lifestyle/behavioural analysis, psychological/social analysis, key findings, actionable recommendations
- Embedded statistics and correlation analysis
- Background async processing

### Authentication & Access Control
- Email/password login with user registration
- Role-based access (admin panel for user management)
- Multi-method authentication: Bearer token, Basic Auth, webhook secret
- Protected endpoints for report generation and administration

---

## Architecture

```
                    +-------------------+
                    |    Students /     |
                    |    Survey Takers  |
                    +--------+----------+
                             |
                    Questionnaire Submission
                             |
                    +--------v----------+
                    |     Frontend      |
                    |   (Next.js 15)    |
                    |                   |
                    |  - Survey Forms   |
                    |  - Dashboard      |
                    |  - Report Viewer  |
                    |  - Admin Panel    |
                    +--------+----------+
                             |
                         REST API
                             |
                    +--------v----------+
                    |     Backend       |
                    |    (FastAPI)      |
                    |                   |
                    |  - Data Pipeline  |
                    |  - ML Prediction  |
                    |  - Report Gen     |
                    |  - Auth           |
                    +--------+----------+
                             |
              +--------------+--------------+
              |              |              |
     +--------v---+  +------v------+  +----v-------+
     | Excel Data |  | ML Models   |  | Groq API   |
     | Storage    |  | (.sav)      |  | (LLM)      |
     +------------+  +-------------+  +------------+
```

---

## Tech Stack

| Layer        | Technology                                                        |
| ------------ | ----------------------------------------------------------------- |
| **Frontend** | Next.js 15, TypeScript, Tailwind CSS, Material-UI, Chart.js, Recharts, React Simple Maps |
| **Backend**  | Python 3.13, FastAPI, Uvicorn, Pandas, NumPy, Scikit-learn        |
| **ML**       | Random Forest, Neural Network (MLP), SMOTE, StandardScaler       |
| **AI/LLM**   | Groq API (Llama 3.1 8B Instant) for report narrative generation  |
| **PDF**      | FPDF2 with DejaVu fonts                                          |
| **Data**     | Excel files (openpyxl), merged cross-university datasets          |
| **DevOps**   | Docker, Docker Compose                                            |

---

## Project Structure

```
mentalhealth/
├── backend/
│   ├── main.py                  # Entry point (uvicorn server)
│   ├── api.py                   # FastAPI routes & endpoints
│   ├── data_processor.py        # Survey submission & data processing
│   ├── data_evaluation.py       # ML model training & prediction
│   ├── data_merger.py           # Cross-university dataset merging
│   ├── reports.py               # PDF report generation with AI insights
│   ├── models/                  # Pydantic schemas
│   │   ├── account.py           # Login/Register models
│   │   ├── questionnaire.py     # Survey data model
│   │   ├── dashboard.py         # Dashboard response model
│   │   ├── report.py            # Report request model
│   │   ├── groq.py              # Groq LLM client
│   │   ├── course.py            # Course response model
│   │   └── department.py        # Department response model
│   ├── structs/                 # Data structures & mappings
│   │   ├── columns.py           # Column definitions
│   │   ├── mappings.py          # Value standardization
│   │   └── other.py             # Misc structures
│   ├── ml/                      # Serialized ML models
│   │   ├── RandomForest_original_model.sav
│   │   ├── RandomForest_smote_model.sav
│   │   ├── NeuralNetwork_original_model.sav
│   │   └── NeuralNetwork_smote_model.sav
│   ├── fonts/                   # DejaVu fonts for PDF generation
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx                # Home / university selection
│   │   │   ├── [university]/page.tsx   # Dynamic questionnaire page
│   │   │   ├── dashboard/page.tsx      # Analytics dashboard
│   │   │   ├── report/page.tsx         # Report viewer
│   │   │   ├── login/page.tsx          # Authentication page
│   │   │   ├── admin/page.tsx          # Admin user management
│   │   │   └── layout.tsx              # Root layout
│   │   ├── components/
│   │   │   ├── Dashboard/              # Dashboard chart components
│   │   │   ├── Questionaire/           # Survey input components
│   │   │   ├── Login/                  # Auth components
│   │   │   ├── Admin/                  # Admin panel
│   │   │   └── ProtectedRoute/         # Route guards
│   │   ├── api/                        # API client functions
│   │   ├── types/                      # TypeScript type definitions
│   │   └── utils/                      # Utility functions
│   ├── public/
│   │   └── topo.json                   # Geographic map data
│   ├── package.json
│   ├── next.config.ts
│   ├── tailwind.config.ts
│   └── tsconfig.json
│
├── data/
│   ├── merged/                  # Merged cross-university dataset
│   ├── login/                   # User credentials
│   ├── reports/                 # Generated PDF reports
│   ├── universities/            # University list
│   ├── ual/                     # UAL-specific data
│   └── sol/                     # SOL-specific data
│
├── docker-compose.yaml
├── .env
└── README.md
```

---

## Getting Started

### Prerequisites

- **Node.js** >= 18 and **npm**
- **Python** >= 3.10 and **pip**
- **Docker** & **Docker Compose** (for containerized deployment)

### Environment Variables

Create a `.env` file in the project root:

```env
# Backend
GROQ_API_KEY=gsk_...              # Groq API key for LLM report generation
ACCESS_TOKEN=your_access_token     # Token for protected API endpoints
BASIC_AUTH_USER=admin              # Basic auth username (optional)
BASIC_AUTH_PASS=password           # Basic auth password (optional)
WEBHOOK_SECRET=your_secret         # Webhook validation secret
ALLOWED_ORIGINS=http://localhost:3000  # CORS allowed origins (comma-separated)
```

### Local Development

#### Backend

```bash
cd backend
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
uvicorn api:app --reload
```

The API server starts at `http://localhost:8000`.

#### Frontend

```bash
cd frontend
npm install --legacy-peer-deps
npm run dev
```

The frontend starts at `http://localhost:3000`.

### Docker Deployment

```bash
docker-compose up --build
```

This starts both services:
- **Backend** (FastAPI) on port `8000`
- **Frontend** (Next.js) mapped to port `80`

The data directory is mounted as a volume to persist survey data and reports.

---

## Machine Learning Pipeline

### Feature Engineering

The pipeline processes **38+ features** across two categories:

| Type        | Features                                                                                              |
| ----------- | ----------------------------------------------------------------------------------------------------- |
| **Numeric** | age, study hours/week, work hours/week, socialising hours, social media hours, device hours, cost of study, lecture hours, gap between lectures, exercise frequency |
| **Categorical** | gender, diet, ethnicity, country, personality type, stress levels, employment, financial support, disabilities, alcohol use, study level, timetable preference, sense of belonging, and more |

### Training Process

1. Load merged dataset from Excel (dual-header format: question text + column IDs)
2. Clean, encode, and standardize all variables
3. Impute missing values (median for numeric, mode for categorical)
4. Apply StandardScaler to numeric features
5. Apply SMOTE for class balance (optional variant)
6. Train via **RandomizedSearchCV** with 5-fold stratified cross-validation
7. Evaluate on 25% held-out test set
8. Serialize trained models with joblib

### Models

| Model                    | File                              | Description                              |
| ------------------------ | --------------------------------- | ---------------------------------------- |
| Random Forest            | `RandomForest_original_model.sav` | Trained on original class distribution   |
| Random Forest + SMOTE    | `RandomForest_smote_model.sav`    | Trained with synthetic oversampling      |
| Neural Network (MLP)     | `NeuralNetwork_original_model.sav`| MLP classifier on original distribution  |
| Neural Network + SMOTE   | `NeuralNetwork_smote_model.sav`   | MLP classifier with oversampling         |

### Prediction

- **Output**: Binary classification (0 = no predicted mental health issues, 1 = prone to issues)
- Students who select "Prefer not to say" on the target question receive ML-predicted classifications
- Predictions are written back to the dataset for dashboard visualization

---

## API Reference

### Public Endpoints

| Method | Endpoint                          | Description                           |
| ------ | --------------------------------- | ------------------------------------- |
| POST   | `/api/submit/{university}`        | Submit questionnaire responses        |
| POST   | `/api/login`                      | User authentication                   |
| POST   | `/api/register`                   | New user registration                 |
| GET    | `/api/universities`               | List available universities           |
| GET    | `/api/courses/{university}`       | Get courses for a university          |
| GET    | `/api/departments/{university}`   | Get departments and courses           |
| GET    | `/api/dashboard?university={uni}` | Get dashboard data (cached)           |
| GET    | `/api/reports/view/{timestamp}`   | Download a generated PDF report       |

### Protected Endpoints (require auth token)

| Method | Endpoint                          | Description                           |
| ------ | --------------------------------- | ------------------------------------- |
| POST   | `/api/reports`                    | Generate a new AI-powered PDF report  |
| DELETE | `/api/reports/delete/{timestamp}` | Delete a generated report             |
| DELETE | `/api/deleteUser?email={email}`   | Delete a user account (admin only)    |

---

## Dashboard & Visualization

The dashboard provides six analytical categories, each with multiple interactive chart types:

| Category            | Visualizations                                                          |
| ------------------- | ----------------------------------------------------------------------- |
| **Demographics**    | Age distribution, gender breakdown, ethnicity chart, country heat map   |
| **Academic**        | Course distribution, study hours, lecture frequency, timetable impact   |
| **Financial**       | Support methods, employment status, financial stress, cost distribution |
| **Lifestyle**       | Exercise, diet quality, substance use, hydration, sleep patterns        |
| **Psychological**   | Stress levels, personality type, sense of belonging, quality of life    |
| **Technology**      | Device hours, social media usage, screen time patterns                  |

**Filtering**: Multi-select filters for university, department, and all categorical variables with real-time chart updates and cached filter counts.

**Export**: Download filtered datasets as Excel or CSV files.

---

## Report Generation

Reports are generated asynchronously using the **Groq API** (Llama 3.1 8B Instant model) and output as formatted PDF documents.

### Report Sections
1. Executive Summary
2. Demographic Analysis
3. Academic Factors Analysis
4. Financial Analysis
5. Lifestyle and Behavioural Analysis
6. Psychological and Social Analysis
7. Key Findings and Correlations
8. Actionable Recommendations

Reports are stored in `data/reports/` and can be viewed or deleted via the frontend.

---

## License

This project is licensed under the MIT License.
