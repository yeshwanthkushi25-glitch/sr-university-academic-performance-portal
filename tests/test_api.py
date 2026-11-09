"""
Integration Tests for SR University REST API Endpoints
"""

import unittest
from tests.base import BaseTestCase


class ApiEndpointTests(BaseTestCase):
    def test_get_submissions(self):
        res = self.client.get("/api/submissions")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertGreaterEqual(len(data["students"]), 1)

    def test_get_submission_detail(self):
        res = self.client.get("/api/submissions/1")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("student", data)
        self.assertIn("analysis", data)
        self.assertIn("semesters", data)
        self.assertIn("subjects", data)

    def test_create_submission(self):
        payload = {
            "roll_no": "24CS888",
            "full_name": "Kavya Reddy",
            "email": "kavya.reddy@sruniv.edu",
            "department": "Computer Science & Engineering",
            "degree_program": "B.Tech",
            "current_semester": 2,
            "academic_year": "2024-2028",
            "mentor_name": "Dr. Ramanujan",
            "overall_attendance": 90.0,
            "cgpa": 8.7,
            "active_backlogs": 0,
            "weekly_study_hours": "15-20 hours",
            "sleep_hours": "7 hours",
            "stress_level": "Low",
            "career_goal": "Software Engineer",
            "extracurricular_activities": ["Coding Club"],
            "semesters": [
                {"semester_number": 1, "sgpa": 8.7, "credits_registered": 22, "credits_cleared": 22, "backlogs_count": 0}
            ],
            "subjects": [
                {"subject_code": "CS101", "subject_name": "Python Programming", "credits": 4, "internal_marks": 45, "max_internal_marks": 50, "attendance_pct": 92, "grade_expected": "A+"}
            ]
        }
        res = self.client.post("/api/submissions", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("student_id", data)
        self.assertEqual(data["analysis"]["risk_level"], "Low Risk")

    def test_create_submission_sanitization(self):
        # Test XSS script stripping with Bleach
        payload = {
            "roll_no": "24CS777",
            "full_name": "Malicious <script>alert('hack')</script>User",
            "email": "test.xss@sruniv.edu",
            "department": "Computer Science & Engineering",
            "degree_program": "B.Tech",
            "current_semester": 1,
            "academic_year": "2024-2028",
            "mentor_name": "Dr. Mentor",
            "overall_attendance": 80.0,
            "cgpa": 7.5,
            "active_backlogs": 0,
            "semesters": [],
            "subjects": []
        }
        res = self.client.post("/api/submissions", json=payload)
        self.assertEqual(res.status_code, 201)
        student_id = res.get_json()["student_id"]

        detail_res = self.client.get(f"/api/submissions/{student_id}")
        saved_name = detail_res.get_json()["student"]["full_name"]
        self.assertNotIn("<script>", saved_name)
        self.assertNotIn("</script>", saved_name)

    def test_get_cohort_analytics(self):
        res = self.client.get("/api/analytics")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        analytics = data["analytics"]
        self.assertIn("total_students", analytics)
        self.assertIn("avg_cgpa", analytics)
        self.assertIn("risk_distribution", analytics)

    def test_export_csv(self):
        res = self.client.get("/api/export/csv")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Roll No,Full Name,Email", res.data)
        self.assertIn(b"student_performance_records.csv", res.headers.get("Content-Disposition", "").encode())

    def test_advisor_notes_requires_auth(self):
        # Unauthenticated request must return 401
        res = self.client.post("/api/submissions/1/notes", json={"advisor_notes": "Test remark"})
        self.assertEqual(res.status_code, 401)


if __name__ == "__main__":
    unittest.main()
