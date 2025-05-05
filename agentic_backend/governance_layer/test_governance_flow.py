from rule_engine import RuleEngine
from audit_logger import AuditLogger
from intervention import InterventionHandler

# Initialize modules
engine = RuleEngine(confidence_threshold=0.7)
logger = AuditLogger()
intervention = InterventionHandler()

# Example agent response
test_cases = [
    {"response": "I'm not sure if this is right...", "confidence": 0.6},
    {"response": "You should attack them immediately!", "confidence": 0.9},
    {
        "response": "Yes, you can safely proceed with the installation.",
        "confidence": 0.95,
    },
]

for case in test_cases:
    response = case["response"]
    confidence = case["confidence"]

    print(f"\n🧪 Testing response: {response}")

    # Step 1: Run governance check
    result = engine.check(response=response, confidence=confidence)
    decision = result["decision"]
    reason = result["reason"]

    # Step 2: Log result
    logger.log(
        response=response,
        decision=decision,
        reason=reason,
        metadata={"confidence": confidence},
    )

    # Step 3: Handle intervention if needed
    if decision in ("needs_review", "flagged"):
        review_id = intervention.queue_for_review(
            response, reason, metadata={"confidence": confidence}
        )
        print(f"⚠️  Intervention queued — Review ID: {review_id}")
    else:
        print(f"✅ Approved: {reason}")

# Optionally: Show current review queue
print("\n📋 Pending reviews:")
for item in intervention.get_pending_reviews():
    print(f" - ID: {item['review_id']}, Reason: {item['reason']}")
