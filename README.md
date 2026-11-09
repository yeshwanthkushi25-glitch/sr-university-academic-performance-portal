# 🎓 SR University Academic Performance Analysis & Advising Portal
### Intelligent Student Diagnostic Engine, Multi-Factor Risk Scoring, and Cohort Advisory Platform

[![Python Version](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.15-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Flask Architecture](https://img.shields.io/badge/Framework-Flask%203.1%20(Factory%20Pattern)-black.svg?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Security Standards](https://img.shields.io/badge/Security-CSRF%20%7C%20Talisman%20CSP%20%7C%20Bleach-emerald.svg)](#-security-hardening--industrial-architecture)
[![Institution](https://img.shields.io/badge/Institution-SR%20University-orange.svg)](#-project-team--academic-credentials)
[![Test Suite](https://img.shields.io/badge/Tests-16%2F16%20Passed%20(100%25)-brightgreen.svg)](#-automated-testing--quality-assurance)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

---

## 📌 Executive Summary & Problem Statement

In higher education institutions, academic stagnation, student attrition, and credit accumulation deficits often go unnoticed until semester examinations are completed. Conventional academic management systems act as passive record repositories rather than active diagnostic systems.

The **SR University Academic Performance Analysis & Advising Portal** is a production-grade, full-stack predictive evaluation and faculty advising system. It bridges the gap between raw coursework scores and student interventions through:
- **Continuous Credit-Weighted CGPA Recalculation:** Validates multi-semester trajectory deltas ($\Delta \text{SGPA}$) to detect acceleration or sudden performance dips.
- **5-Axis Competency Radar Vector:** Evaluates Theory Mastery, Attendance Discipline, Academic Consistency, Study Habit Discipline, and Exam Readiness.
- **Composite Risk Scoring ($0 - 100$):** Multi-factor algorithmic classifier categorizing students into *Low*, *Moderate*, *High*, and *Critical Risk* tiers.
- **Personalized SWOT Diagnostic Generator:** Generates automated actionable strengths, weaknesses, and academic remediation pathways.
- **Cohort Faculty Analytics & CSV Intelligence:** Enables department heads and academic advisors to track attendance alerts ($<75\%$), analyze departmental grade distributions, and log recorded student counseling interventions.

---

## 🏛️ Institutional Grounding & Academic Standards

This project is built and maintained under the academic standards of:
1. **Institution:** **SR University**, Department of Computer Science & Engineering.
2. **Evaluation Framework:** Continuous Internal Evaluation (CIE) and Semester End Examination (SEE) credit distribution standards.
3. **Attendance Policy:** Automated enforcement of university mandatory attendance thresholds:
   - $\ge 85\%$ — Exemplary attendance benchmark.
   - $75\% - 80\%$ — Warning condonation tier.
   - $< 75\%$ — Mandatory advisory alert & examination condonation disqualification risk.

---

## 🏗️ System Architecture & Modular Design

The codebase is built on an **Industrial-Grade Flask Application Factory Architecture** (`create_app`), decoupling configuration environments, stateful database connections, security headers, and domain endpoints into modular Blueprints.

```
                              +---------------------------------------+
                              |         Client Web Browser            |
                              |  (Tailwind CSS + Chart.js Controller) |
                              +---------------------------------------+
                                        |                  ^
                                 HTTPS  |                  | JSON / HTML
                                 POST   v                  |
                   +-----------------------------------------------------+
                   |          Security Middleware & Headers Tier         |
                   |   Flask-Talisman (CSP/HSTS) | Flask-WTF (CSRF)      |
                   +-----------------------------------------------------+
                                             |
                                             v
                   +-----------------------------------------------------+
                   |           Flask Application Factory Pattern         |
                   |       (app/__init__.py -> create_app(config))       |
                   +-----------------------------------------------------+
                          /                  |                    \
                         /                   |                     \
                        v                    v                      v
             +------------------+  +--------------------+  +-------------------+
             |    auth_bp       |  |      main_bp       |  |      api_bp       |
             | /login, /logout, |  |   / (Main Student  |  | /api/submissions  |
             | /register        |  |    Portal Stepper) |  | /api/analytics    |
             +------------------+  +--------------------+  | /api/export/csv   |
                      |                      |             +-------------------+
                      | (Flask-Login Auth)   |                       |
                      v                      v                       v
             +------------------+  +--------------------+  +-------------------+
             | User / RBAC Model|  | Jinja2 Templates   |  | Diagnostic Engine |
             | (Student / Admin)|  |  & Error Handlers  |  | (analyzer.py)     |
             +------------------+  +--------------------+  +-------------------+
                                             \                       /
                                              \                     /
                                               v                   v
                                      +---------------------------------+
                                      |    Decoupled Database Layer     |
                                      |   (app/db.py -> SQLite3 + WAL)  |
                                      +---------------------------------+
                                      |  students | users | semesters   |
                                      |  subject_records                |
                                      +---------------------------------+
```

---

## 🛠️ Technology Stack & Industrial Architecture

| Category | Technology / Library | Version | Architectural Role |
| :--- | :--- | :--- | :--- |
| **Backend Runtime** | Python | `3.11+` | Core execution environment & numerical computations |
| **Web Framework** | Flask | `3.1.3` | Application factory, routing, request lifecycle & blueprints |
| **Authentication** | Flask-Login | `0.6.3` | Session tracking, cookie management & role authorization |
| **CSRF Defense** | Flask-WTF | `1.3.0` | Cryptographic token protection for form submissions |
| **Security Headers** | Flask-Talisman | `1.1.0` | Content Security Policy (CSP), X-Frame-Options, nosniff |
| **XSS Sanitization** | Bleach | `6.4.0` | Allowlist-based stripping of malicious script tags in free text |
| **Persistence Engine**| SQLite 3 | `3.53+` | Embedded relational engine with foreign keys & WAL journal |
| **Frontend Styling** | Tailwind CSS CDN | `3.4+` | Modern responsive component design and design system |
| **Visual Analytics** | Chart.js | `4.4+` | GPA progression, 5-axis radar chart, and department metrics |
| **Test Framework** | Python `unittest` | Built-in | Automated testing, client test fixtures, isolated test DBs |

---

## 🌟 Core Functional Modules & Intelligence Engine

### 1. 📝 Student Multi-Step Evaluation Wizard
- **Demographics & Profile:** Roll Number, Name, University Email, Department, Program, Semester, Mentor.
- **Academic Trajectory:** Semester-by-semester SGPA inputs, registered credits, cleared credits, and backlog counters.
- **Coursework Internals:** Subject codes, names, continuous internal marks ($/50$), attendance $\%$, and expected grades.
- **Holistic Habit Assessment:** Weekly self-study hours, sleep duration, stress level, and extracurricular involvement.

### 2. 📊 Performance Diagnostic Engine (`analyzer.py`)
- **Credit-Weighted CGPA Calculation:**
  $$\text{Effective CGPA} = \frac{\sum_{i=1}^{n} (\text{SGPA}_i \times \text{Credits}_i)}{\sum_{i=1}^{n} \text{Credits}_i}$$
- **Trajectory Status Classifier:** Compares $\Delta = \text{SGPA}_{t} - \text{SGPA}_{t-1}$:
  - $\Delta \ge +0.5$: *Rapid Acceleration*
  - $+0.1 \le \Delta < +0.5$: *Upward Progression*
  - $-0.1 \le \Delta < +0.1$: *Consistent / Stable*
  - $-0.5 \le \Delta < -0.1$: *Gradual Decline*
  - $\Delta < -0.5$: *Sharp Dip (Needs Immediate Attention)*
- **5-Axis Competency Radar Vector ($0 - 100$):**
  1. *Theory Mastery:* Coursework continuous internal percentage average.
  2. *Attendance Discipline:* Overall lecture presence percentage.
  3. *Academic Consistency:* Inverted variance score of historical semester performance.
  4. *Study Discipline:* Normalized score mapped from self-study commitment bands.
  5. *Exam Readiness:* Standardized CGPA performance normalized to a $100$-point scale.
- **Multi-Factor Risk Classifier:**
  Calculates cumulative penalties for attendance deficits ($<75\%$), low CGPA ($<6.0$), active backlogs ($\times 15$ pts), weak subject clusters, and high stress levels. Classifies into *Low Risk*, *Moderate Risk*, *High Risk*, or *Critical Risk*.

### 3. 🏛️ Advisor & Faculty Portal
- Real-time department comparison charts (Average CGPA vs. Attendance).
- Cohort risk distribution doughnut chart.
- Student record directory with real-time text search and filter by department/risk.
- One-click CSV export of all student performance data.
- Recorded advisor counseling remarks saved directly to student records.

---

## 📁 Repository Directory Structure

```text
academic_performance_portal/
├── app/
│   ├── __init__.py               # Flask application factory (create_app)
│   ├── config.py                 # Configuration classes (Dev, Test, Prod)
│   ├── db.py                     # SQLite schema, connection pool & seed manager
│   ├── extensions.py             # Extension instances (LoginManager, CSRF, Talisman)
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py               # User model, user_loader, and @roles_required
│   ├── services/
│   │   ├── __init__.py
│   │   └── analyzer.py           # Diagnostic SWOT, radar vector & risk scoring
│   ├── blueprints/
│   │   ├── auth/                 # Authentication blueprint (/login, /logout, /register)
│   │   │   ├── __init__.py
│   │   │   └── routes.py
│   │   ├── main/                 # Main portal blueprint (/)
│   │   │   ├── __init__.py
│   │   │   └── routes.py
│   │   └── api/                  # REST API blueprint (/api/*)
│   │       ├── __init__.py
│   │       └── routes.py
│   ├── templates/                # Jinja2 presentation templates
│   │   ├── index.html            # Main student form & analytics dashboard
│   │   ├── login.html            # Auth login template with SR University branding
│   │   ├── register.html         # User registration template
│   │   └── errors/               # Centralized HTTP error handlers
│   │       ├── 400.html
│   │       ├── 403.html
│   │       ├── 404.html
│   │       └── 500.html
│   └── static/                   # Static assets
│       ├── css/style.css         # Custom animations & theme styles
│       └── js/app.js             # Form stepper, Chart.js managers & REST clients
├── tests/                        # Comprehensive automated test suite
│   ├── __init__.py
│   ├── base.py                   # Base test case with isolated SQLite test DB
│   ├── test_analyzer.py          # Unit tests for performance diagnostics
│   ├── test_api.py               # Integration tests for REST API routes
│   ├── test_auth.py              # Unit tests for authentication & roles
│   └── test_rebranding.py        # Automated test guaranteeing 0 'Apex' occurrences
├── .gitignore                    # Production git ignore configuration
├── analyzer.py                   # Root backward-compatible shim
├── app.py                        # Root WSGI application entrypoint
├── config.py                     # Root configuration forwarder
├── db.py                         # Root database operations forwarder
├── requirements.txt              # Pinned Python package dependencies
├── run.py                        # Standalone development server runner
├── test_app.py                   # Compatibility verification runner
└── README.md                     # Comprehensive project documentation
```

---

## 👥 Project Team & Academic Credentials

* **University:** **SR University**
* **Department & Branch:** Department of Computer Science & Engineering
* **Specialization:** Full-Stack Web Development & Academic Analytics
* **Academic Year:** 2026–2027

| # | Student / Developer Name | Roll Number | Primary Responsibilities |
| :-: | :--- | :--- | :--- |
| **1** | **Yeshwanth** | `2503A53005` | System Architecture, Industrial Flask Refactoring, Analytics Engine & Security Hardening |

---

## 🚀 Quick Start Guide & Local Setup

### 1. Prerequisites
Ensure you have **Python 3.10+** and **Git** installed on your system.

```bash
python --version
git --version
```

### 2. Clone Repository
```bash
git clone https://github.com/yeshwanthkushi25-glitch/sr-university-academic-performance-portal.git
cd sr-university-academic-performance-portal
```

### 3. Set Up Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate on Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Activate on Linux / macOS:
source venv/bin/activate
```

### 4. Install Dependencies
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Run Database Initialization
```bash
# Initializes schema and populates SR University demo benchmarks
python -c "from app import create_app; from app.db import init_db, seed_sample_data_if_empty; a = create_app(); print('Database Ready!')"
```

### 6. Launch Application Server
```bash
python run.py
```

Open your browser at: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## ⚡ Default Demo Accounts

The portal comes pre-seeded with ready-to-test credentials:

| Role | Email Address | Password | Permissions |
| :--- | :--- | :--- | :--- |
| **Student** | `student@sruniv.edu` | `student123` | Submit evaluations, view personalized SWOT & trajectory reports |
| **Faculty / Advisor** | `advisor@sruniv.edu` | `advisor123` | Access cohort analytics, inspect student directory & record counseling notes |

*(Alternatively, create a new custom account anytime via the `/register` page).*

---

## 🧪 Automated Testing & Quality Assurance

The project includes an isolated automated test suite built with Python's standard `unittest` framework. Tests execute against isolated in-memory or temporary databases to prevent side effects on development data.

### Execute Test Suite
```bash
python -m unittest discover -s tests -v
```

### Test Case Execution Summary

| # | Test Case Identifier | Module / Feature Tested | Verification Scope | Result |
| :-: | :--- | :--- | :--- | :-: |
| **1** | `test_high_performer_analysis` | Performance Analytics | Distinction classification, SWOT generation, trajectory delta | `PASS ✅` |
| **2** | `test_at_risk_student_analysis` | Risk Classification Engine | Critical risk score ($>50$), probation alert, attendance warnings | `PASS ✅` |
| **3** | `test_radar_scores_generation` | 5-Axis Competency Vector | Boundary check ($0-100$) for all 5 competency radar axes | `PASS ✅` |
| **4** | `test_get_submissions` | REST API (`GET /api/submissions`) | Submission retrieval, row mapping, student count | `PASS ✅` |
| **5** | `test_get_submission_detail` | REST API (`GET /api/submissions/<id>`) | Deep diagnostic detail retrieval, course arrays, SWOT analysis | `PASS ✅` |
| **6** | `test_create_submission` | REST API (`POST /api/submissions`) | Full evaluation payload ingestion, SQLite persistence, risk rating | `PASS ✅` |
| **7** | `test_create_submission_sanitization`| Security Hardening | Bleach HTML tag stripping to defend against XSS attacks | `PASS ✅` |
| **8** | `test_get_cohort_analytics` | Faculty Analytics API | Department aggregates, average CGPA, attendance alert counts | `PASS ✅` |
| **9** | `test_export_csv` | CSV Export Pipeline | Structured CSV stream generation with complete student records | `PASS ✅` |
| **10**| `test_advisor_notes_requires_auth`| Access Control Middleware | Unauthenticated requests to advisor notes return HTTP 401 | `PASS ✅` |
| **11**| `test_login_page_renders` | Authentication Blueprint | Verification of login template, SR University branding, CSRF tokens | `PASS ✅` |
| **12**| `test_register_page_renders` | Registration Blueprint | Verification of registration form fields and CSRF tokens | `PASS ✅` |
| **13**| `test_successful_login` | Session Management | Valid credentials create authenticated session for student | `PASS ✅` |
| **14**| `test_invalid_login` | Session Management | Rejected credentials trigger flash error message | `PASS ✅` |
| **15**| `test_logout` | Session Invalidation | Secure session termination and redirect | `PASS ✅` |
| **16**| `test_zero_apex_occurrences` | Institutional Rebranding | Full-tree audit guaranteeing 0 occurrences of legacy university terms | `PASS ✅` |

---

## 📡 REST API Reference & Data Contracts

| Method | Endpoint | Authentication | Description | Request Payload | Response |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/` | Public | Main Student Form & Analytics Dashboard | None | HTML |
| `GET` | `/login` | Public | User Login Portal | None | HTML |
| `POST` | `/login` | Public | Authenticate user session | `email`, `password`, `csrf_token` | Redirect / HTML |
| `GET` | `/register` | Public | User Registration Portal | None | HTML |
| `POST` | `/register` | Public | Register new student or advisor | `email`, `password`, `role`, `csrf_token`| Redirect / HTML |
| `GET` | `/logout` | Logged In | Terminate user session | None | Redirect |
| `GET` | `/api/submissions` | Public | Retrieve filtered student list | Query params: `search`, `department`, `risk_level` | JSON List |
| `GET` | `/api/submissions/<id>` | Public | Retrieve individual diagnostic profile | None | JSON Object |
| `POST` | `/api/submissions` | Public | Submit coursework & generate SWOT | JSON Student + Semesters + Subjects payload | JSON `201 Created` |
| `POST` | `/api/submissions/<id>/notes` | Advisor / Admin | Record faculty counseling remarks | `{"advisor_notes": "..."}` | JSON `200 OK` |
| `GET` | `/api/analytics` | Public | Cohort-wide metrics & risk summary | None | JSON Analytics |
| `GET` | `/api/export/csv` | Public | Download all records as CSV | None | `text/csv` stream |

---

## 📜 Academic Standards & Submission Compliance

- [x] **SR University Institutional Rebranding:** 0 occurrences of legacy terms across all code, templates, scripts, configs, and database files.
- [x] **Industrial Application Factory Pattern:** Implemented via `create_app()` with decoupled configuration classes (`DevelopmentConfig`, `TestingConfig`, `ProductionConfig`).
- [x] **Modular Blueprint Routing:** Application partitioned into `auth_bp`, `main_bp`, and `api_bp`.
- [x] **Security Hardening:** CSRF protection enabled via Flask-WTF, CSP security headers configured via Flask-Talisman, and XSS sanitization enforced via Bleach.
- [x] **Role-Based Access Control:** `@roles_required('admin', 'advisor')` decorator protecting faculty-only interventions.
- [x] **Comprehensive Test Suite:** 16 automated tests covering all critical paths with 100% pass rate.
- [x] **Standard Documentation Style:** Modeled after institutional reference projects with Shields.io badges, ASCII system diagrams, academic team metadata, and API specifications.

---

## 📄 License & Attribution

This project is developed as part of academic coursework at **SR University**, Department of Computer Science & Engineering. Licensed under the [MIT License](LICENSE).
