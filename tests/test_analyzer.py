"""
Unit Tests for SR University Performance Analytics Engine
"""

import unittest
from app.services.analyzer import analyze_student_performance


class AnalyzerTests(unittest.TestCase):
    def test_high_performer_analysis(self):
        student_data = {
            "cgpa": 8.8,
            "overall_attendance": 92.0,
            "active_backlogs": 0,
            "stress_level": "Low",
            "weekly_study_hours": "15-20 hours",
            "career_goal": "Software Engineering"
        }
        semesters = [
            {"semester_number": 1, "sgpa": 8.5, "credits_registered": 22, "credits_cleared": 22, "backlogs_count": 0},
            {"semester_number": 2, "sgpa": 9.1, "credits_registered": 22, "credits_cleared": 22, "backlogs_count": 0}
        ]
        subjects = [
            {"subject_code": "CS301", "subject_name": "Algorithms", "credits": 4, "internal_marks": 46, "max_internal_marks": 50, "attendance_pct": 95, "grade_expected": "A+"}
        ]
        result = analyze_student_performance(student_data, semesters, subjects)

        self.assertEqual(result["risk_level"], "Low Risk")
        self.assertEqual(result["risk_score"], 0)
        self.assertIn("Distinction", result["standing"])
        self.assertEqual(result["credit_completion_rate"], 100.0)
        self.assertEqual(result["trajectory_status"], "Rapid Acceleration")
        self.assertGreater(len(result["strengths"]), 0)
        self.assertEqual(len(result["weaknesses"]), 0)

    def test_at_risk_student_analysis(self):
        student_data = {
            "cgpa": 5.2,
            "overall_attendance": 64.0,
            "active_backlogs": 3,
            "stress_level": "High",
            "weekly_study_hours": "5-10 hours",
            "career_goal": "Tech Startups"
        }
        semesters = [
            {"semester_number": 1, "sgpa": 6.0, "credits_registered": 20, "credits_cleared": 16, "backlogs_count": 1},
            {"semester_number": 2, "sgpa": 4.8, "credits_registered": 20, "credits_cleared": 14, "backlogs_count": 2}
        ]
        subjects = [
            {"subject_code": "AI201", "subject_name": "Deep Learning", "credits": 4, "internal_marks": 18, "max_internal_marks": 50, "attendance_pct": 60, "grade_expected": "C"}
        ]
        result = analyze_student_performance(student_data, semesters, subjects)

        self.assertIn("Risk", result["risk_level"])
        self.assertGreater(result["risk_score"], 50)
        self.assertIn("Probation", result["standing"])
        self.assertLess(result["credit_completion_rate"], 100.0)
        self.assertGreater(len(result["weaknesses"]), 0)
        self.assertGreater(len(result["recommendations"]), 0)

    def test_radar_scores_generation(self):
        student_data = {"cgpa": 7.5, "overall_attendance": 82.0, "active_backlogs": 0}
        result = analyze_student_performance(student_data, [], [])
        radar = result["radar_scores"]
        self.assertIn("Theory Mastery", radar)
        self.assertIn("Attendance Discipline", radar)
        self.assertIn("Academic Consistency", radar)
        self.assertIn("Study Discipline", radar)
        self.assertIn("Exam Readiness", radar)
        for val in radar.values():
            self.assertGreaterEqual(val, 0)
            self.assertLessEqual(val, 100)


if __name__ == "__main__":
    unittest.main()
