"""
Unit and Integration Tests for User Authentication & Access Control
"""

import unittest
from tests.base import BaseTestCase


class AuthTests(BaseTestCase):
    def test_login_page_renders(self):
        res = self.client.get("/login")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"SR University", res.data)
        self.assertIn(b"Sign In", res.data)

    def test_register_page_renders(self):
        res = self.client.get("/register")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Create Account", res.data)

    def test_successful_login(self):
        # Default seeded student: student@sruniv.edu / student123
        res = self.client.post("/login", data={
            "email": "student@sruniv.edu",
            "password": "student123"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"student@sruniv.edu", res.data)

    def test_invalid_login(self):
        res = self.client.post("/login", data={
            "email": "student@sruniv.edu",
            "password": "wrongpassword"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Invalid credentials", res.data)

    def test_logout(self):
        # Login first
        self.client.post("/login", data={
            "email": "student@sruniv.edu",
            "password": "student123"
        })
        # Logout
        res = self.client.get("/logout", follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Sign In", res.data)


if __name__ == "__main__":
    unittest.main()
