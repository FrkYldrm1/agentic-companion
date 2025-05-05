# governance_layer/intervention.py

import uuid
import datetime
from typing import Optional
from memory_layer.db import get_db
from memory_layer.models import FlaggedResponse
from sqlalchemy.orm import Session


class InterventionHandler:
    def __init__(self):
        self.pending_reviews = {}  # review_id: dict
        self.review_log = []  # archive of handled interventions

    def queue_for_review(self, response, reason, metadata=None):
        review_id = str(uuid.uuid4())
        entry = {
            "review_id": review_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "response": response,
            "reason": reason,
            "metadata": metadata or {},
            "status": "pending",
        }
        self.pending_reviews[review_id] = entry
        return review_id

    def get_pending_reviews(self):
        return list(self.pending_reviews.values())

    def resolve_review(
        self, review_id: str, decision: str, reviewer_id: Optional[str] = None
    ):
        if review_id not in self.pending_reviews:
            raise ValueError(f"Review ID not found: {review_id}")

        entry = self.pending_reviews.pop(review_id)
        entry.update(
            {
                "status": "resolved",
                "final_decision": decision,
                "reviewed_by": reviewer_id,
                "reviewed_at": datetime.datetime.now().isoformat(),
            }
        )
        self.review_log.append(entry)
        return entry
