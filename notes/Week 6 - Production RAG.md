---
week: 6
status: completed
tags:
  - rag
  - graph-rag
  - guardrails
  - multimodal
---

# Week 6 - Production RAG

## Objective

Transform the optimized RAG pipeline into a guarded, observable and multimodal production agent.

## Implemented

- `TechStoreRAGAgent`
- Graph RAG
- Knowledge graph traversal
- CSV table retrieval
- Image metadata retrieval
- Answers with source citations
- Claim verification
- Off-topic question detection
- Guardrail decision gate
- Citation and numeric-grounding metrics
- Logging and optional-route failure handling

## Guardrail decisions

- `answer`
- `answer_with_disclaimer`
- `extractive`
- `no_answer`
- `ask_clarify`
- `refuse`

## Main files

- `Week6_Stop3_Production_RAG.ipynb`
- `src/rag_agent.py`
- `src/graph/knowledge_graph.py`
- `src/guardrails/writer.py`
- `src/guardrails/verifier.py`
- `src/multimodal/table_retriever.py`
- `src/multimodal/image_retriever.py`

## Validation

- 20 automated tests passed
- No-answer guardrail validated
- Graph traversal validated
- Table-grounded numeric answer validated

## Related notes

- [[Graph RAG]]
- [[Guardrails]]
- [[Multimodal Retrieval]]
- [[Mandatory Tests]]