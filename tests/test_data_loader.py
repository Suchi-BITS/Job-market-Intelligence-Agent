import tempfile
import unittest
from pathlib import Path
from job_agent.data_loader import DataLoadError, load_jobs

class DataLoaderTests(unittest.TestCase):
    def test_loads_and_fills_optional_columns(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "jobs.csv"
            path.write_text("title,company\nPython Engineer,Example Co\n", encoding="utf-8")
            jobs = load_jobs(path)
            self.assertEqual(len(jobs), 1)
            self.assertEqual(jobs[0]["title"], "Python Engineer")
            self.assertEqual(jobs[0]["location"], "")
    def test_missing_file_has_clear_error(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(DataLoadError):
                load_jobs(Path(temp) / "missing.csv")
    def test_missing_required_column(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "jobs.csv"
            path.write_text("company\nExample Co\n", encoding="utf-8")
            with self.assertRaises(DataLoadError):
                load_jobs(path)

if __name__ == "__main__":
    unittest.main()
