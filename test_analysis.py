import unittest
from types import SimpleNamespace
from unittest.mock import patch

from pydantic import ValidationError

from analysis import analyze, markdown_report
from samples import client_preview


class AnalysisTests(unittest.TestCase):
    def run_pipeline(self, responses):
        with patch("analysis.genai.Client") as client:
            generate = client.return_value.__enter__.return_value.models.generate_content
            generate.side_effect = responses
            result = analyze("Test meeting", "Client Call", "test", "test", lambda label: None)
            return result, generate.call_count

    def test_bad_response_stops_pipeline(self):
        with self.assertRaises(ValidationError):
            self.run_pipeline([SimpleNamespace(text='{"error":"incomplete"}')])

    def test_unassigned_items_skip_emails(self):
        notes, _, quality = client_preview()
        notes.action_items[0].owner = "Unassigned"
        result, count = self.run_pipeline([
            SimpleNamespace(text=notes.model_dump_json()), SimpleNamespace(text=quality.model_dump_json()),
        ])
        self.assertEqual(count, 2)
        self.assertFalse(result[1].emails)

    def test_report_contains_reviewed_email(self):
        report = client_preview()
        result, count = self.run_pipeline([SimpleNamespace(text=part.model_dump_json()) for part in report])
        self.assertEqual(count, 3)
        result[1].emails[0].body = "Reviewed message"
        self.assertIn("Reviewed message", markdown_report(*result))
