"""
REST API Blueprint for SR University Academic Performance Portal
"""

import json
import csv
import io
import bleach
from flask import request, jsonify, Response
from flask_login import login_required
from app.blueprints.api import api_bp
from app.extensions import csrf
from app.db import get_db
from app.models.user import roles_required
from app.services.analyzer import analyze_student_performance


def sanitize_text(val, max_len=255):
    """Sanitizes untrusted free-text using Bleach to strip all HTML tags."""
    if not val:
        return ""
    cleaned = bleach.clean(str(val), tags=[], attributes={}, strip=True).strip()
    return cleaned[:max_len]


@api_bp.route("/submissions", methods=["GET"])
def get_submissions():
    """Returns list of student submissions with optional search, department, and risk filters."""
    search = request.args.get("search", "").strip()
    dept = request.args.get("department", "").strip()
    risk = request.args.get("risk_level", "").strip()

    conn = get_db()
    cursor = conn.cursor()

    query = """
    SELECT id, roll_no, full_name, email, department, degree_program,
           current_semester, academic_year, overall_attendance, cgpa,
           active_backlogs, risk_level, risk_score, standing, created_at
    FROM students WHERE 1=1
    """
    params = []

    if search:
        query += " AND (full_name LIKE ? OR roll_no LIKE ? OR email LIKE ?)"
        like_str = f"%{search}%"
        params.extend([like_str, like_str, like_str])

    if dept and dept != "All":
        query += " AND department = ?"
        params.append(dept)

    if risk and risk != "All":
        query += " AND risk_level LIKE ?"
        params.append(f"%{risk}%")

    query += " ORDER BY id DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    students = [dict(row) for row in rows]
    conn.close()

    return jsonify({"success": True, "students": students, "count": len(students)})


@api_bp.route("/submissions/<int:student_id>", methods=["GET"])
def get_submission_detail(student_id):
    """Returns complete details of a student including semesters, courses, and diagnostics."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
    student_row = cursor.fetchone()

    if not student_row:
        conn.close()
        return jsonify({"success": False, "error": "Student record not found"}), 404

    student = dict(student_row)
    if student.get("extracurricular_activities"):
        try:
            student["extracurricular_activities"] = json.loads(student["extracurricular_activities"])
        except Exception:
            student["extracurricular_activities"] = [student["extracurricular_activities"]]

    cursor.execute("""
    SELECT semester_number, sgpa, credits_registered, credits_cleared, backlogs_count
    FROM semester_records WHERE student_id = ? ORDER BY semester_number ASC
    """, (student_id,))
    semesters = [dict(r) for r in cursor.fetchall()]

    cursor.execute("""
    SELECT subject_code, subject_name, credits, internal_marks, max_internal_marks,
           attendance_pct, grade_expected
    FROM subject_records WHERE student_id = ? ORDER BY id ASC
    """, (student_id,))
    subjects = [dict(r) for r in cursor.fetchall()]

    conn.close()

    analysis = analyze_student_performance(student, semesters, subjects)

    return jsonify({
        "success": True,
        "student": student,
        "semesters": semesters,
        "subjects": subjects,
        "analysis": analysis
    })


@api_bp.route("/submissions", methods=["POST"])
@csrf.exempt
def submit_form():
    """
    Processes a student form submission, analyzes performance, and persists to SQLite.
    Includes Bleach-based input sanitization and strict range validation.
    """
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "Invalid request JSON payload"}), 400

    try:
        roll_no = sanitize_text(data.get("roll_no", ""), 30).upper()
        full_name = sanitize_text(data.get("full_name", ""), 100)
        email = sanitize_text(data.get("email", ""), 120).lower()
        department = sanitize_text(data.get("department", ""), 100)
        degree_program = sanitize_text(data.get("degree_program", "B.Tech"), 50)
        academic_year = sanitize_text(data.get("academic_year", "2024-2028"), 30)
        mentor_name = sanitize_text(data.get("mentor_name", ""), 100)
        weekly_study_hours = sanitize_text(data.get("weekly_study_hours", "10-15 hours"), 50)
        sleep_hours = sanitize_text(data.get("sleep_hours", "7 hours"), 50)
        stress_level = sanitize_text(data.get("stress_level", "Moderate"), 50)
        career_goal = sanitize_text(data.get("career_goal", "Campus Placements"), 100)

        raw_extra = data.get("extracurricular_activities", [])
        if isinstance(raw_extra, list):
            extracurricular = [sanitize_text(x, 80) for x in raw_extra if x]
        else:
            extracurricular = [sanitize_text(raw_extra, 80)] if raw_extra else []

        try:
            current_semester = max(1, min(12, int(data.get("current_semester", 1))))
            overall_attendance = max(0.0, min(100.0, float(data.get("overall_attendance", 80.0))))
            input_cgpa = max(0.0, min(10.0, float(data.get("cgpa", 7.0))))
            active_backlogs = max(0, min(50, int(data.get("active_backlogs", 0))))
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": "Invalid numerical parameters"}), 400

        semesters = data.get("semesters", [])
        subjects = data.get("subjects", [])

        if not roll_no or not full_name or not email:
            return jsonify({"success": False, "error": "Roll Number, Name, and Email are required"}), 400

        analysis = analyze_student_performance({
            "cgpa": input_cgpa,
            "overall_attendance": overall_attendance,
            "active_backlogs": active_backlogs,
            "stress_level": stress_level,
            "weekly_study_hours": weekly_study_hours,
            "career_goal": career_goal
        }, semesters, subjects)

        effective_cgpa = analysis["cgpa"]
        risk_level = analysis["risk_level"]
        risk_score = analysis["risk_score"]
        standing = analysis["standing"]

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM students WHERE roll_no = ?", (roll_no,))
        existing = cursor.fetchone()

        if existing:
            student_id = existing["id"]
            cursor.execute("""
            UPDATE students SET
                full_name = ?, email = ?, department = ?, degree_program = ?,
                current_semester = ?, academic_year = ?, mentor_name = ?,
                overall_attendance = ?, cgpa = ?, active_backlogs = ?,
                weekly_study_hours = ?, sleep_hours = ?, extracurricular_activities = ?,
                stress_level = ?, career_goal = ?, risk_level = ?, risk_score = ?, standing = ?
            WHERE id = ?
            """, (
                full_name, email, department, degree_program, current_semester,
                academic_year, mentor_name, overall_attendance, effective_cgpa,
                active_backlogs, weekly_study_hours, sleep_hours, json.dumps(extracurricular),
                stress_level, career_goal, risk_level, risk_score, standing, student_id
            ))
            cursor.execute("DELETE FROM semester_records WHERE student_id = ?", (student_id,))
            cursor.execute("DELETE FROM subject_records WHERE student_id = ?", (student_id,))
        else:
            cursor.execute("""
            INSERT INTO students (
                roll_no, full_name, email, department, degree_program,
                current_semester, academic_year, mentor_name, overall_attendance,
                cgpa, active_backlogs, weekly_study_hours, sleep_hours,
                extracurricular_activities, stress_level, career_goal,
                risk_level, risk_score, standing
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                roll_no, full_name, email, department, degree_program,
                current_semester, academic_year, mentor_name, overall_attendance,
                effective_cgpa, active_backlogs, weekly_study_hours, sleep_hours,
                json.dumps(extracurricular), stress_level, career_goal,
                risk_level, risk_score, standing
            ))
            student_id = cursor.lastrowid

        for sem in semesters:
            try:
                sem_num = max(1, min(12, int(sem.get("semester_number", 1))))
                sgpa_val = max(0.0, min(10.0, float(sem.get("sgpa", 0.0))))
                reg_cr = max(0, min(60, int(sem.get("credits_registered", 20))))
                clr_cr = max(0, min(60, int(sem.get("credits_cleared", 20))))
                bk_cnt = max(0, min(30, int(sem.get("backlogs_count", 0))))
                cursor.execute("""
                INSERT INTO semester_records (
                    student_id, semester_number, sgpa, credits_registered, credits_cleared, backlogs_count
                ) VALUES (?, ?, ?, ?, ?, ?)
                """, (student_id, sem_num, sgpa_val, reg_cr, clr_cr, bk_cnt))
            except (ValueError, TypeError):
                continue

        for subj in subjects:
            try:
                sub_code = sanitize_text(subj.get("subject_code", "SUB101"), 20).upper()
                sub_name = sanitize_text(subj.get("subject_name", "Subject"), 100)
                credits_val = max(1, min(12, int(subj.get("credits", 3))))
                int_marks = max(0.0, min(100.0, float(subj.get("internal_marks", 35.0))))
                max_marks = max(1.0, min(100.0, float(subj.get("max_internal_marks", 50.0))))
                att_pct = max(0.0, min(100.0, float(subj.get("attendance_pct", 85.0))))
                grade_exp = sanitize_text(subj.get("grade_expected", "A"), 5).upper()

                cursor.execute("""
                INSERT INTO subject_records (
                    student_id, subject_code, subject_name, credits, internal_marks,
                    max_internal_marks, attendance_pct, grade_expected
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    student_id, sub_code, sub_name, credits_val, int_marks,
                    max_marks, att_pct, grade_exp
                ))
            except (ValueError, TypeError):
                continue

        conn.commit()
        conn.close()

        return jsonify({
            "success": True,
            "message": "Student academic performance data successfully analyzed and recorded!",
            "student_id": student_id,
            "analysis": analysis
        }), 201

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/submissions/<int:student_id>/notes", methods=["POST"])
@csrf.exempt
@login_required
@roles_required("admin", "advisor")
def update_advisor_notes(student_id):
    """Updates advisor notes for a student record. Requires advisor/admin authorization."""
    data = request.get_json() or {}
    notes = sanitize_text(data.get("advisor_notes", ""), 1000)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE students SET advisor_notes = ? WHERE id = ?", (notes, student_id))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Advisor notes updated successfully"})


@api_bp.route("/analytics", methods=["GET"])
def get_cohort_analytics():
    """Cohort-wide analytics for university faculty and department heads."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total, AVG(cgpa) as avg_cgpa, AVG(overall_attendance) as avg_att FROM students")
    base_stats = cursor.fetchone()
    total_students = base_stats["total"] or 0
    avg_cgpa = round(base_stats["avg_cgpa"] or 0.0, 2)
    avg_att = round(base_stats["avg_att"] or 0.0, 1)

    cursor.execute("SELECT risk_level, COUNT(*) as count FROM students GROUP BY risk_level")
    risk_dist = {r["risk_level"]: r["count"] for r in cursor.fetchall()}

    cursor.execute("""
    SELECT department, COUNT(*) as count, ROUND(AVG(cgpa), 2) as avg_cgpa, ROUND(AVG(overall_attendance), 1) as avg_att
    FROM students GROUP BY department
    """)
    dept_stats = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT COUNT(*) as count FROM students WHERE risk_level IN ('High Risk', 'Critical Risk')")
    at_risk_count = cursor.fetchone()["count"] or 0

    cursor.execute("SELECT COUNT(*) as count FROM students WHERE overall_attendance < 75.0")
    attendance_alert_count = cursor.fetchone()["count"] or 0

    conn.close()

    return jsonify({
        "success": True,
        "analytics": {
            "total_students": total_students,
            "avg_cgpa": avg_cgpa,
            "avg_attendance": avg_att,
            "at_risk_count": at_risk_count,
            "attendance_alert_count": attendance_alert_count,
            "risk_distribution": risk_dist,
            "department_stats": dept_stats
        }
    })


@api_bp.route("/export/csv", methods=["GET"])
def export_csv():
    """Generates and streams a CSV of all student performance records."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT roll_no, full_name, email, department, degree_program, current_semester,
           academic_year, overall_attendance, cgpa, active_backlogs, standing, risk_level, risk_score
    FROM students ORDER BY id ASC
    """)
    rows = cursor.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Roll No", "Full Name", "Email", "Department", "Program", "Semester",
        "Academic Year", "Attendance (%)", "CGPA", "Active Backlogs", "Academic Standing", "Risk Level", "Risk Score"
    ])

    for r in rows:
        writer.writerow([
            r["roll_no"], r["full_name"], r["email"], r["department"], r["degree_program"],
            r["current_semester"], r["academic_year"], r["overall_attendance"], r["cgpa"],
            r["active_backlogs"], r["standing"], r["risk_level"], r["risk_score"]
        ])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=student_performance_records.csv"}
    )
