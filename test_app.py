import unittest
from tests.base import BaseTestCase


class AcademicPortalTests(BaseTestCase):
    def test_homepage(self):
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"SR University", res.data)

    def test_get_submissions(self):
        res = self.client.get('/api/submissions')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertGreaterEqual(len(data['students']), 1)

    def test_get_submission_detail(self):
        res = self.client.get('/api/submissions/1')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertIn('analysis', data)
        self.assertIn('radar_scores', data['analysis'])
        self.assertIn('cgpa', data['analysis'])

    def test_analytics(self):
        res = self.client.get('/api/analytics')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertIn('total_students', data['analytics'])

    def test_create_submission(self):
        payload = {
            'roll_no': '23CS999',
            'full_name': 'Sneha Patel',
            'email': 'sneha.patel@sruniv.edu',
            'department': 'Computer Science & Engineering',
            'degree_program': 'B.Tech',
            'current_semester': 3,
            'academic_year': '2024-2028',
            'mentor_name': 'Dr. K. Sharma',
            'overall_attendance': 89.0,
            'cgpa': 8.5,
            'active_backlogs': 0,
            'weekly_study_hours': '15-20 hours',
            'sleep_hours': '7 hours',
            'stress_level': 'Low',
            'career_goal': 'Campus Placements / Software Engineer',
            'extracurricular_activities': ['Technical Clubs / Coding'],
            'semesters': [
                {'semester_number': 1, 'sgpa': 8.2, 'credits_registered': 22, 'credits_cleared': 22, 'backlogs_count': 0},
                {'semester_number': 2, 'sgpa': 8.6, 'credits_registered': 24, 'credits_cleared': 24, 'backlogs_count': 0}
            ],
            'subjects': [
                {'subject_code': 'CS201', 'subject_name': 'Data Structures', 'credits': 4, 'internal_marks': 44, 'max_internal_marks': 50, 'attendance_pct': 92, 'grade_expected': 'A+'},
                {'subject_code': 'CS202', 'subject_name': 'Discrete Math', 'credits': 4, 'internal_marks': 42, 'max_internal_marks': 50, 'attendance_pct': 88, 'grade_expected': 'A'}
            ]
        }
        res = self.client.post('/api/submissions', json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertIn('analysis', data)
        self.assertEqual(data['analysis']['risk_level'], 'Low Risk')

    def test_export_csv(self):
        res = self.client.get('/api/export/csv')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Roll No,Full Name,Email", res.data)


if __name__ == '__main__':
    unittest.main()
