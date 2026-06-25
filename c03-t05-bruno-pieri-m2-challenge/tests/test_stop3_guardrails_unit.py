import pytest

from src.guardrails.verifier import citation_density, numeric_grounding_rate
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

def test_citation_density_counts_cited_sentences():
    answer = (
        "The Laptop Pro X1 has 16 GB RAM. [TB:laptop_specs.csv:row0] "
        "It is popular with creators."
    )

    assert citation_density(answer) == 0.5


def test_numeric_grounding_rate_requires_numbers_in_context():
    answer = "The Laptop Pro X1 has 16 GB RAM and costs 1299 dollars."
    context_text = "model=Laptop Pro X1, ram_gb=16, price_usd=1299"

    assert numeric_grounding_rate(answer, context_text) == 1.0
    assert numeric_grounding_rate("It has 32 GB RAM.", context_text) == 0.0
