import json
import datetime
import os


class AuditLogger:
    def __init__(self, log_dir="logs"):
        os.makedirs(log_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(log_dir, f"governance_log_{timestamp}.jsonl")

    def log(self, response: str, decision: str, reason: str, metadata: dict = None):
        """
        Append a log entry to the audit log file.

        Args:
            response: The agent's textual output.
            decision: Governance decision (approved, needs_review, flagged).
            reason: Explanation for the decision.
            metadata: Optional info (confidence, agent_id, user_id, etc.).
        """
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "response": response,
            "decision": decision,
            "reason": reason,
            "metadata": metadata or {},
        }
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
