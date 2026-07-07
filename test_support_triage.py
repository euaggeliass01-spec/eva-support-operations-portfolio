import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class WorkflowTests(unittest.TestCase):
    def test_local_mode_generates_all_outputs(self):
        project = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory() as temp:
            out_json = Path(temp) / "results.json"
            out_html = Path(temp) / "report.html"
            subprocess.run(
                [
                    sys.executable,
                    str(project / "support_triage.py"),
                    "--mode", "local",
                    "--input", str(project / "sample_tickets.csv"),
                    "--output", str(out_json),
                    "--html", str(out_html),
                ],
                check=True,
            )
            data = json.loads(out_json.read_text(encoding="utf-8"))
            self.assertEqual(len(data), 8)
            self.assertTrue(out_html.exists())
            self.assertTrue(all(item["draft_reply"].strip() for item in data))
            self.assertTrue(all(item["mode"] == "local" for item in data))

    def test_redaction(self):
        project = Path(__file__).resolve().parent
        sys.path.insert(0, str(project))
        from support_triage import redact_pii
        text = redact_pii("Email me at person@example.com or +49 123 456 789.")
        self.assertIn("[REDACTED_EMAIL]", text)
        self.assertIn("[REDACTED_PHONE]", text)


if __name__ == "__main__":
    unittest.main()
