import unittest
from types import SimpleNamespace
from unittest.mock import patch

from pydantic import ValidationError

from analysis import Email, analyze, correct_action, markdown_report
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

    def test_only_verbatim_source_is_retained(self):
        for candidate, expected in [("Test meeting", "Test meeting"), ("invented", "")]:
            with self.subTest(candidate=candidate):
                notes, drafts, quality = client_preview()
                notes.action_items[0].source_quote = candidate
                results, _ = self.run_pipeline(
                    [SimpleNamespace(text=p.model_dump_json()) for p in (notes, drafts, quality)]
                )
                self.assertEqual(results[0].action_items[0].source_quote, expected)

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


class ActionReviewTests(unittest.TestCase):
    def test_reassign_updates_both_owners_and_preserves_unrelated_draft(self):
        notes, drafts, quality = client_preview()
        first = notes.action_items[0]
        notes.action_items.append(first.model_copy(update={"task": "Prepare slides"}))
        drafts.emails.append(Email(owner="Lee", subject="Custom", body="Manually edited"))
        correct_action(notes, drafts, 0, "Send release notes", "Maya", "Monday")
        bodies = {e.owner: e.body for e in drafts.emails}
        self.assertIn("Prepare slides", bodies["John"])
        self.assertNotIn("Send release notes", bodies["John"])
        self.assertIn("Send release notes (Due: Monday)", bodies["Maya"])
        self.assertEqual(bodies["Lee"], "Manually edited")
        self.assertIn("Send release notes — Maya · Monday", markdown_report(notes, drafts, quality))

    def test_blank_task_rejected_and_owner_can_be_cleared(self):
        notes, drafts, _ = client_preview()
        with self.assertRaises(ValueError):
            correct_action(notes, drafts, 0, " ", "Maya", "Friday")
        self.assertEqual(notes.action_items[0].owner, "John")
        correct_action(notes, drafts, 0, "Send release notes", "", "")
        self.assertEqual(notes.action_items[0].owner, "Unassigned")
        self.assertEqual(notes.action_items[0].deadline, "Unspecified")
        self.assertFalse(drafts.emails)
