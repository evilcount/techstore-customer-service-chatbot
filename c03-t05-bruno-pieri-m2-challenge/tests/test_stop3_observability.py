import logging

from src.rag_agent import GuardrailedAnswer, TechStoreRAGAgent


def test_log_query_includes_guardrail_metrics(caplog):
    agent = TechStoreRAGAgent()
    result = GuardrailedAnswer(
        answer="The model has 16 GB RAM. [TB:laptop_specs.csv:row0]",
        decision="answer",
        claim_support_rate=1.0,
        contradiction_rate=0.0,
        cited_sources=["[TB:laptop_specs.csv:row0]"],
    )

    with caplog.at_level(logging.INFO, logger="src.rag_agent"):
        agent._log_query(
            "How much RAM does the Laptop Pro X1 have?",
            ["vector", "table"],
            4,
            result,
        )

    message = caplog.records[0].getMessage()
    assert "citation_density" in message
    assert "numeric_grounding_rate" in message
    assert "[TB:laptop_specs.csv:row0]" in message
