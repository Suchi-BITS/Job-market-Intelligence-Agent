import unittest
from job_agent.experience import extract_experience_years

class ExperienceTests(unittest.TestCase):
    def test_plus_years(self):
        self.assertEqual(extract_experience_years("Requires 5+ years of experience"), 5)
    def test_at_least(self):
        self.assertEqual(extract_experience_years("At least 3 years in Python"), 3)
    def test_plain_experience(self):
        self.assertEqual(extract_experience_years("2 years of experience required"), 2)
    def test_unknown_is_none(self):
        self.assertIsNone(extract_experience_years("Senior engineer, great communication skills"))

if __name__ == "__main__":
    unittest.main()
