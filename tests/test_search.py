import tempfile
import unittest
from pathlib import Path

from job_agent.agent import JobSearchAgent, SearchRequest
from job_agent.search import search_jobs

SAMPLE = [
    {"title":"AI Engineer","company":"Example AI","location":"India",
     "description":"Build RAG systems. Requires 4 years of experience.",
     "tags":"Python, RAG","remote":"true","experience_years_min":"4",
     "url":"https://example.test/ai"},
    {"title":"Data Analyst","company":"Example Data","location":"Germany",
     "description":"SQL and dashboards. 2 years of experience.",
     "tags":"SQL","remote":"false","experience_years_min":"2",
     "url":"https://example.test/analyst"},
    {"title":"Knowledge Graph Engineer","company":"Example Graph","location":"India",
     "description":"Ontology and graph databases.","tags":"Python, ontology",
     "remote":"true","experience_years_min":"","url":"https://example.test/graph"},
]

class SearchTests(unittest.TestCase):
    def test_keyword_search(self):
        result = search_jobs(SAMPLE, query="AI Engineer")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["title"], "AI Engineer")
    def test_or_search(self):
        self.assertEqual(len(search_jobs(SAMPLE, query="Python OR SQL")), 3)
    def test_location_filter(self):
        self.assertEqual(len(search_jobs(SAMPLE, location="India")), 2)
    def test_remote_filter(self):
        self.assertEqual(len(search_jobs(SAMPLE, remote_only=True)), 2)
    def test_experience_filter_excludes_unknown(self):
        result = search_jobs(SAMPLE, min_experience=3, max_experience=5)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["title"], "AI Engineer")
    def test_agent_validates_experience_range(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "jobs.csv"
            path.write_text("title\nPython Engineer\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                JobSearchAgent(path).run(SearchRequest(min_experience=5, max_experience=2))

if __name__ == "__main__":
    unittest.main()
