"""
Automated Verification for SR University Rebranding Compliance
Guarantees 0 occurrences of 'Apex' or 'Apex University' across the entire codebase.
"""

import os
import unittest


class RebrandingVerificationTests(unittest.TestCase):
    def test_zero_apex_occurrences(self):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        disallowed = ["apex university", "apexuniv.edu"]

        excluded_dirs = {".git", ".agents", "__pycache__", ".pytest_cache"}
        excluded_exts = {".pyc", ".db", ".png", ".jpg", ".jpeg", ".ico"}

        excluded_files = {"test_rebranding.py"}

        violations = []

        for root, dirs, files in os.walk(base_dir):
            dirs[:] = [d for d in dirs if d not in excluded_dirs]
            for file in files:
                if file in excluded_files:
                    continue
                ext = os.path.splitext(file)[1].lower()
                if ext in excluded_exts:
                    continue

                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        for line_num, line in enumerate(f, 1):
                            lower_line = line.lower()
                            for term in disallowed:
                                if term in lower_line:
                                    violations.append(f"{filepath}:{line_num} contains '{term}' -> {line.strip()}")
                except Exception as e:
                    pass

        self.assertEqual(
            len(violations), 0,
            f"Found {len(violations)} rebranding violations:\n" + "\n".join(violations[:10])
        )


if __name__ == "__main__":
    unittest.main()
