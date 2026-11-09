"""
Database Operations and Seed Management for SR University Academic Portal.
Uses SQLite with WAL mode, foreign keys, and dynamic configuration resolution.
"""

import sqlite3
import json
import os
from flask import current_app
from werkzeug.security import generate_password_hash


def get_db_path(app=None):
    """Resolves active database path from Flask application config or default."""
    if app:
        return app.config.get("DB_PATH")
    if current_app:
        return current_app.config.get("DB_PATH")
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_dir, "academic_portal.db")


def get_db(app=None):
    """Returns a new SQLite connection with Row factory and foreign keys enabled."""
    db_path = get_db_path(app)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(app=None):
    """Creates database schema tables if they do not exist."""
    conn = get_db(app)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        roll_no TEXT UNIQUE NOT NULL,
        full_name TEXT NOT NULL,
        email TEXT NOT NULL,
        department TEXT NOT NULL,
        degree_program TEXT NOT NULL,
        current_semester INTEGER NOT NULL,
        academic_year TEXT NOT NULL,
        mentor_name TEXT,
        overall_attendance REAL NOT NULL,
        cgpa REAL NOT NULL,
        active_backlogs INTEGER DEFAULT 0,
        weekly_study_hours TEXT,
        sleep_hours TEXT,
        extracurricular_activities TEXT,
        stress_level TEXT,
        career_goal TEXT,
        risk_level TEXT,
        risk_score INTEGER,
        standing TEXT,
        advisor_notes TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('student','advisor','admin')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS semester_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        semester_number INTEGER NOT NULL,
        sgpa REAL NOT NULL,
        credits_registered INTEGER NOT NULL,
        credits_cleared INTEGER NOT NULL,
        backlogs_count INTEGER DEFAULT 0,
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subject_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        subject_code TEXT NOT NULL,
        subject_name TEXT NOT NULL,
        credits INTEGER NOT NULL,
        internal_marks REAL NOT NULL,
        max_internal_marks REAL DEFAULT 50,
        attendance_pct REAL NOT NULL,
        grade_expected TEXT,
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
    );
    """)

    conn.commit()
    conn.close()


def seed_sample_data_if_empty(app=None):
    """Populates default SR University student benchmarks and demo accounts if empty."""
    conn = get_db(app)
    cursor = conn.cursor()

    # Seed demo users if users table is empty
    cursor.execute("SELECT COUNT(*) as count FROM users")
    user_count = cursor.fetchone()["count"]
    if user_count == 0:
        cursor.execute(
            "INSERT INTO users (email, password_hash, role) VALUES (?, ?, ?)",
            ("student@sruniv.edu", generate_password_hash("student123"), "student")
        )
        cursor.execute(
            "INSERT INTO users (email, password_hash, role) VALUES (?, ?, ?)",
            ("advisor@sruniv.edu", generate_password_hash("advisor123"), "admin")
        )
        conn.commit()

    # Seed students if students table is empty
    cursor.execute("SELECT COUNT(*) as count FROM students")
    student_count = cursor.fetchone()["count"]

    if student_count == 0:
        sample_students = [
            {
                "roll_no": "21CS042",
                "full_name": "Aarav Sharma",
                "email": "aarav.sharma@sruniv.edu",
                "department": "Computer Science & Engineering",
                "degree_program": "B.Tech",
                "current_semester": 6,
                "academic_year": "2023-2027",
                "mentor_name": "Dr. R. Ramanujan",
                "overall_attendance": 88.5,
                "cgpa": 8.74,
                "active_backlogs": 0,
                "weekly_study_hours": "15-20 hours",
                "sleep_hours": "7 hours",
                "extracurricular_activities": json.dumps(["Coding Club Lead", "Hackathon Winner"]),
                "stress_level": "Moderate",
                "career_goal": "Software Engineering / AI Research",
                "risk_level": "Low Risk",
                "risk_score": 12,
                "standing": "First Class with Distinction / Honors",
                "advisor_notes": "Exemplary student. Excellent problem-solving skills.",
                "semesters": [
                    {"sem": 1, "sgpa": 8.40, "reg": 22, "cleared": 22, "backlogs": 0},
                    {"sem": 2, "sgpa": 8.65, "reg": 24, "cleared": 24, "backlogs": 0},
                    {"sem": 3, "sgpa": 8.80, "reg": 23, "cleared": 23, "backlogs": 0},
                    {"sem": 4, "sgpa": 8.90, "reg": 24, "cleared": 24, "backlogs": 0},
                    {"sem": 5, "sgpa": 8.95, "reg": 22, "cleared": 22, "backlogs": 0}
                ],
                "subjects": [
                    {"code": "CS301", "name": "Design & Analysis of Algorithms", "credits": 4, "internal": 46, "max": 50, "att": 92.0, "grade": "A+"},
                    {"code": "CS302", "name": "Database Management Systems", "credits": 4, "internal": 44, "max": 50, "att": 88.0, "grade": "A"},
                    {"code": "CS303", "name": "Operating Systems Architecture", "credits": 4, "internal": 41, "max": 50, "att": 85.0, "grade": "A"},
                    {"code": "CS304", "name": "Computer Networks & Protocols", "credits": 3, "internal": 47, "max": 50, "att": 90.0, "grade": "A+"},
                    {"code": "CS305", "name": "Algorithms & Systems Lab", "credits": 2, "internal": 48, "max": 50, "att": 95.0, "grade": "O"}
                ]
            },
            {
                "roll_no": "22AI018",
                "full_name": "Priya Nair",
                "email": "priya.nair@sruniv.edu",
                "department": "Artificial Intelligence & Data Science",
                "degree_program": "B.Tech",
                "current_semester": 4,
                "academic_year": "2024-2028",
                "mentor_name": "Dr. Sunita Rao",
                "overall_attendance": 68.0,
                "cgpa": 5.42,
                "active_backlogs": 2,
                "weekly_study_hours": "5-10 hours",
                "sleep_hours": "5 hours",
                "extracurricular_activities": json.dumps(["Cultural Secretary"]),
                "stress_level": "High",
                "career_goal": "Product Management",
                "risk_level": "Critical Risk",
                "risk_score": 78,
                "standing": "Academic Probation / Critical Warning",
                "advisor_notes": "Needs attendance condonation monitoring and backlog tutoring.",
                "semesters": [
                    {"sem": 1, "sgpa": 6.80, "reg": 20, "cleared": 20, "backlogs": 0},
                    {"sem": 2, "sgpa": 5.10, "reg": 22, "cleared": 18, "backlogs": 1},
                    {"sem": 3, "sgpa": 4.90, "reg": 22, "cleared": 18, "backlogs": 1}
                ],
                "subjects": [
                    {"code": "AI201", "name": "Deep Learning Foundations", "credits": 4, "internal": 22, "max": 50, "att": 62.0, "grade": "C"},
                    {"code": "AI202", "name": "Probability & Applied Statistics", "credits": 4, "internal": 24, "max": 50, "att": 65.0, "grade": "C"},
                    {"code": "AI203", "name": "Big Data Systems & Hadoop", "credits": 4, "internal": 31, "max": 50, "att": 72.0, "grade": "B"},
                    {"code": "AI204", "name": "Computer Vision Fundamentals", "credits": 3, "internal": 35, "max": 50, "att": 75.0, "grade": "B+"},
                    {"code": "AI205", "name": "AI & Neural Networks Lab", "credits": 2, "internal": 42, "max": 50, "att": 80.0, "grade": "A"}
                ]
            },
            {
                "roll_no": "23EC077",
                "full_name": "Rohan Deshmukh",
                "email": "rohan.deshmukh@sruniv.edu",
                "department": "Electronics & Communication",
                "degree_program": "B.Tech",
                "current_semester": 4,
                "academic_year": "2024-2028",
                "mentor_name": "Dr. V. K. Murthy",
                "overall_attendance": 82.0,
                "cgpa": 7.65,
                "active_backlogs": 0,
                "weekly_study_hours": "10-15 hours",
                "sleep_hours": "6 hours",
                "extracurricular_activities": json.dumps(["Robotics Club"]),
                "stress_level": "Moderate",
                "career_goal": "Core Engineering / R&D",
                "risk_level": "Moderate Risk",
                "risk_score": 32,
                "standing": "First Class",
                "advisor_notes": "Steady progress. Encourage to participate in research projects.",
                "semesters": [
                    {"sem": 1, "sgpa": 7.50, "reg": 20, "cleared": 20, "backlogs": 0},
                    {"sem": 2, "sgpa": 7.65, "reg": 22, "cleared": 22, "backlogs": 0},
                    {"sem": 3, "sgpa": 7.80, "reg": 22, "cleared": 22, "backlogs": 0}
                ],
                "subjects": [
                    {"code": "EC301", "name": "Digital Signal Processing", "credits": 4, "internal": 36, "max": 50, "att": 82.0, "grade": "B+"},
                    {"code": "EC302", "name": "VLSI Circuit Design", "credits": 4, "internal": 40, "max": 50, "att": 86.0, "grade": "A"},
                    {"code": "EC303", "name": "Electromagnetic Waves & Antennas", "credits": 4, "internal": 34, "max": 50, "att": 78.0, "grade": "B"},
                    {"code": "EC304", "name": "Microcontrollers & Embedded Systems", "credits": 3, "internal": 43, "max": 50, "att": 90.0, "grade": "A+"},
                    {"code": "EC305", "name": "VLSI & Embedded Lab", "credits": 2, "internal": 45, "max": 50, "att": 92.0, "grade": "O"}
                ]
            }
        ]

        for s in sample_students:
            cursor.execute("""
            INSERT INTO students (
                roll_no, full_name, email, department, degree_program, current_semester,
                academic_year, mentor_name, overall_attendance, cgpa, active_backlogs,
                weekly_study_hours, sleep_hours, extracurricular_activities, stress_level,
                career_goal, risk_level, risk_score, standing, advisor_notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                s["roll_no"], s["full_name"], s["email"], s["department"], s["degree_program"],
                s["current_semester"], s["academic_year"], s["mentor_name"], s["overall_attendance"],
                s["cgpa"], s["active_backlogs"], s["weekly_study_hours"], s["sleep_hours"],
                s["extracurricular_activities"], s["stress_level"], s["career_goal"],
                s["risk_level"], s["risk_score"], s["standing"], s["advisor_notes"]
            ))
            student_id = cursor.lastrowid

            for sem in s["semesters"]:
                cursor.execute("""
                INSERT INTO semester_records (
                    student_id, semester_number, sgpa, credits_registered, credits_cleared, backlogs_count
                ) VALUES (?, ?, ?, ?, ?, ?)
                """, (student_id, sem["sem"], sem["sgpa"], sem["reg"], sem["cleared"], sem["backlogs"]))

            for subj in s["subjects"]:
                cursor.execute("""
                INSERT INTO subject_records (
                    student_id, subject_code, subject_name, credits, internal_marks,
                    max_internal_marks, attendance_pct, grade_expected
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (student_id, subj["code"], subj["name"], subj["credits"], subj["internal"],
                      subj["max"], subj["att"], subj["grade"]))

        conn.commit()

    conn.close()
