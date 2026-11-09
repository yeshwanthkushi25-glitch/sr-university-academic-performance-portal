"""
SR University Academic Performance Analysis Engine
Computes comprehensive diagnostics, risk scores, performance trajectories,
subject mastery matrices, and personalized SWOT recommendations.
"""

def analyze_student_performance(student_data, semesters, subjects):
    """
    Analyzes student academic metrics and returns detailed diagnostics.
    """
    current_cgpa = float(student_data.get("cgpa", 0.0))
    overall_attendance = float(student_data.get("overall_attendance", 0.0))
    active_backlogs = int(student_data.get("active_backlogs", 0))
    stress_level = str(student_data.get("stress_level", "Moderate"))
    study_hours_text = str(student_data.get("weekly_study_hours", "10-15 hours"))
    career_goal = str(student_data.get("career_goal", "Campus Placements"))

    # 1. Total Credits and Recalculated Weighted CGPA
    total_reg_credits = 0
    total_cleared_credits = 0
    total_grade_points = 0.0

    sgpa_list = []
    for sem in sorted(semesters, key=lambda x: x.get("semester_number", 0)):
        sgpa = float(sem.get("sgpa", 0.0))
        reg = int(sem.get("credits_registered", 20))
        cleared = int(sem.get("credits_cleared", reg))
        sgpa_list.append(sgpa)
        total_reg_credits += reg
        total_cleared_credits += cleared
        total_grade_points += (sgpa * reg)

    computed_cgpa = round(total_grade_points / total_reg_credits, 2) if total_reg_credits > 0 else current_cgpa
    effective_cgpa = computed_cgpa if computed_cgpa > 0 else current_cgpa

    credit_completion_rate = round((total_cleared_credits / total_reg_credits * 100), 1) if total_reg_credits > 0 else 100.0

    # 2. Performance Trajectory
    trajectory_status = "Stable"
    trajectory_delta = 0.0
    if len(sgpa_list) >= 2:
        trajectory_delta = round(sgpa_list[-1] - sgpa_list[-2], 2)
        if trajectory_delta >= 0.5:
            trajectory_status = "Rapid Acceleration"
        elif trajectory_delta > 0.1:
            trajectory_status = "Upward Progression"
        elif trajectory_delta >= -0.1:
            trajectory_status = "Consistent / Stable"
        elif trajectory_delta >= -0.5:
            trajectory_status = "Gradual Decline"
        else:
            trajectory_status = "Sharp Dip (Needs Attention)"
    elif len(sgpa_list) == 1:
        trajectory_status = "Baseline Established"

    # 3. Academic Standing Classification
    if effective_cgpa >= 8.5:
        standing = "First Class with Distinction / Honors"
    elif effective_cgpa >= 7.5:
        standing = "First Class"
    elif effective_cgpa >= 6.5:
        standing = "Second Class (Upper Division)"
    elif effective_cgpa >= 5.5:
        standing = "Second Class (Lower Division)"
    else:
        standing = "Academic Probation / Critical Warning"

    # 4. Multi-factor Risk Score Calculation (0 - 100)
    risk_score = 0
    risk_factors = []

    # Attendance risk
    if overall_attendance < 65:
        risk_score += 40
        risk_factors.append("Attendance below critical threshold (65%) - severe exam disqualification risk")
    elif overall_attendance < 75:
        risk_score += 25
        risk_factors.append("Attendance below university mandatory minimum (75%)")
    elif overall_attendance < 80:
        risk_score += 10
        risk_factors.append("Attendance is in the warning band (75% - 80%)")

    # GPA risk
    if effective_cgpa < 5.0:
        risk_score += 35
        risk_factors.append("CGPA below 5.0 indicates high probability of graduation delay")
    elif effective_cgpa < 6.0:
        risk_score += 20
        risk_factors.append("CGPA below 6.0 restricts placement and higher education eligibility")
    elif effective_cgpa < 7.0:
        risk_score += 10

    # Backlog risk
    if active_backlogs >= 3:
        risk_score += 30
        risk_factors.append(f"{active_backlogs} active backlogs pose serious credit accumulation deficit")
    elif active_backlogs > 0:
        risk_score += (active_backlogs * 15)
        risk_factors.append(f"{active_backlogs} active backlog(s) require immediate remediation")

    # Subject performance checks
    weak_subjects = []
    strong_subjects = []
    for s in subjects:
        internal = float(s.get("internal_marks", 0))
        max_marks = float(s.get("max_internal_marks", 50)) or 50.0
        pct = (internal / max_marks) * 100.0
        att = float(s.get("attendance_pct", 100.0))
        sub_name = s.get("subject_name", s.get("subject_code", "Unknown"))

        if pct < 50.0 or att < 75.0:
            weak_subjects.append({
                "code": s.get("subject_code", ""),
                "name": sub_name,
                "percentage": round(pct, 1),
                "attendance": att,
                "reason": "Low internal score" if pct < 50 else "Low attendance"
            })
        elif pct >= 75.0 and att >= 80.0:
            strong_subjects.append({
                "code": s.get("subject_code", ""),
                "name": sub_name,
                "percentage": round(pct, 1),
                "attendance": att
            })

    if weak_subjects:
        risk_score += min(20, len(weak_subjects) * 7)
        risk_factors.append(f"{len(weak_subjects)} subject(s) flagged for substandard internal marks or attendance")

    # Stress and study habit risk
    if stress_level.lower() == "high" and ("< 5" in study_hours_text or "5-10" in study_hours_text):
        risk_score += 10
        risk_factors.append("High stress combined with constrained self-study hours")

    # Cap risk score at 100
    risk_score = min(100, max(0, risk_score))

    # Categorize risk level
    if risk_score <= 20:
        risk_level = "Low Risk"
        risk_color = "emerald"
    elif risk_score <= 45:
        risk_level = "Moderate Risk"
        risk_color = "amber"
    elif risk_score <= 70:
        risk_level = "High Risk"
        risk_color = "orange"
    else:
        risk_level = "Critical Risk"
        risk_color = "rose"

    # 5. Radar Dimension Scores (0 - 100)
    subject_pcts = [(float(s.get("internal_marks", 0)) / (float(s.get("max_internal_marks", 50)) or 50.0)) * 100.0 for s in subjects] if subjects else [75.0]
    theory_mastery = round(sum(subject_pcts) / len(subject_pcts), 1) if subject_pcts else 70.0
    attendance_discipline = round(overall_attendance, 1)

    if len(sgpa_list) >= 2:
        variance = sum((x - (sum(sgpa_list)/len(sgpa_list))) ** 2 for x in sgpa_list) / len(sgpa_list)
        consistency_score = max(40, round(100 - (variance * 40), 1))
    else:
        consistency_score = 80.0

    study_score_map = {
        "< 5": 45,
        "5-10": 65,
        "10-15": 82,
        "15-20": 92,
        "20+": 98
    }
    study_score = 75
    for key, val in study_score_map.items():
        if key in study_hours_text:
            study_score = val
            break

    exam_readiness = round(min(100, effective_cgpa * 10), 1)

    radar_scores = {
        "Theory Mastery": theory_mastery,
        "Attendance Discipline": attendance_discipline,
        "Academic Consistency": consistency_score,
        "Study Discipline": study_score,
        "Exam Readiness": exam_readiness
    }

    # 6. Actionable SWOT & Tailored Recommendations
    strengths = []
    weaknesses = []
    recommendations = []

    if effective_cgpa >= 8.0:
        strengths.append(f"Strong academic foundation with CGPA of {effective_cgpa:.2f}")
    if overall_attendance >= 85:
        strengths.append(f"Punctual attendance record of {overall_attendance:.1f}%")
    if active_backlogs == 0:
        strengths.append("Clean academic slate with zero active backlogs")
    if strong_subjects:
        strengths.append(f"Demonstrated excellence in {len(strong_subjects)} key course(s): " + ", ".join([s["code"] for s in strong_subjects[:3]]))

    if overall_attendance < 75:
        weaknesses.append(f"Attendance is {overall_attendance:.1f}%, which is below the mandatory 75% university policy")
    if active_backlogs > 0:
        weaknesses.append(f"Carrying {active_backlogs} pending backlog course(s) impacting credit velocity")
    if weak_subjects:
        weaknesses.append(f"Struggling in {len(weak_subjects)} subject(s) requiring academic remediation: " + ", ".join([s["name"] for s in weak_subjects]))
    if trajectory_status in ["Gradual Decline", "Sharp Dip (Needs Attention)"]:
        weaknesses.append(f"Recent semester downward trend ({trajectory_delta:+.2f} SGPA change)")

    # Recommendations
    if overall_attendance < 75:
        recommendations.append("Prioritize attending all remaining lectures to bridge the mandatory 75% condonation cutoff.")
    if active_backlogs > 0:
        recommendations.append("Register for supplementary / re-examination exams immediately and consult faculty for backlog clearance scheduling.")
    if weak_subjects:
        for ws in weak_subjects[:2]:
            recommendations.append(f"Schedule faculty consultation / remedial tutoring hours for '{ws['name']}'.")
    if study_score < 70:
        recommendations.append("Establish a structured daily 2-hour study routine to balance continuous assessment preparation.")
    if effective_cgpa >= 8.5:
        recommendations.append("Consider applying for research internships, undergraduate honors thesis, or competitive national fellowships.")
    elif effective_cgpa >= 7.0 and "Placement" in career_goal:
        recommendations.append("Maintain CGPA above 7.0 to remain eligible for 95%+ campus recruitment tier-1 software and corporate drives.")
    if stress_level.lower() == "high":
        recommendations.append("Connect with student wellness / counseling center for time management and exam anxiety mitigation strategies.")

    if len(recommendations) < 3:
        recommendations.append("Form collaborative peer study circles for joint assignment reviews and mock midterm tests.")
        recommendations.append("Review previous years' semester examination papers for pattern analysis.")

    return {
        "cgpa": effective_cgpa,
        "credit_completion_rate": credit_completion_rate,
        "total_credits_registered": total_reg_credits,
        "total_credits_cleared": total_cleared_credits,
        "standing": standing,
        "trajectory_status": trajectory_status,
        "trajectory_delta": trajectory_delta,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risk_color": risk_color,
        "risk_factors": risk_factors,
        "radar_scores": radar_scores,
        "strong_subjects": strong_subjects,
        "weak_subjects": weak_subjects,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "recommendations": recommendations
    }
