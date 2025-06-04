import unittest
import os
import json
import tempfile
from governance_layer.audit_logger import AuditLogger


class TestAuditLogger(unittest.TestCase):
    def test_log_entry_written(self):
        # Create a temp directory for logs.
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = AuditLogger(log_dir=temp_dir)
            logger.log(
                response="This is a test response.",
                decision="flagged",
                reason="Test reason",
                metadata={"confidence": 0.5},
            )

            # Check if a file was created
            files = os.listdir(temp_dir)
            self.assertEqual(len(files), 1)

            log_path = os.path.join(temp_dir, files[0])
            with open(log_path, "r") as f:
                lines = f.readlines()

            # Check if one line of JSON was written
            self.assertEqual(len(lines), 1)
            entry = json.loads(lines[0])
            self.assertEqual(entry["decision"], "flagged")
            self.assertIn("timestamp", entry)
            self.assertEqual(entry["metadata"]["confidence"], 0.5)


if __name__ == "__main__":
    unittest.main()
