import pytest

from src.rag_agent import GuardrailedAnswer


def test_guardrailed_answer_accepts_stop3_decisions():
    for decision in ("ask_clarify", "refuse"):
        result = GuardrailedAnswer(
            answer="Please clarify the product model.",
            decision=decision,
            claim_support_rate=0.0,
            contradiction_rate=0.0,
        )

        assert result.decision == decision


def test_guardrailed_answer_still_rejects_unknown_decision():
    with pytest.raises(ValueError, match="decision must be one of"):
        GuardrailedAnswer(
            answer="test",
            decision="unsupported_decision",
            claim_support_rate=0.0,
            contradiction_rate=0.0,
        )
