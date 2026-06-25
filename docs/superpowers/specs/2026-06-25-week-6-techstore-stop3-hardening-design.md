# Week 6 TechStore Stop 3 Hardening Design

## Goal

Harden the existing TechStore Stop 3 implementation before publishing it, without changing the project domain from TechStore to Odyssey. The scope is to close practical grading gaps while preserving the passing mandatory cases and the existing repository structure.

## Chosen Approach

Use the TechStore capstone template as the source of truth for implementation. The Week 6 PDF describes a broader Odyssey-oriented version of the assignment, but this repository and its mandatory tests are TechStore-specific. Rewriting the corpus would be high risk and would discard working Stop 1/2/3 work.

## Scope

In scope:

- Replace silent `except Exception: pass` blocks in Stop 3 paths with observable warnings and graceful fallbacks.
- Extend `GuardrailedAnswer` decisions with `ask_clarify` and `refuse`, while keeping existing decisions backward-compatible.
- Add deterministic guardrail helpers for citation density and numeric grounding.
- Add focused tests for image retrieval, decision validation, guardrail metrics, and table/image routing where possible without LLM calls.
- Update documentation/notebook language to state that the implementation is the TechStore adaptation of Stop 3.

Out of scope:

- Replacing TechStore with Odyssey/Greek Mythology data.
- Implementing Neo4j, VLM image region detection, audio retrieval, or true bounding boxes.
- Rewriting the full RAG agent or changing the working mandatory test behavior.

## Architecture

The existing modules remain:

- `src/rag_agent.py` is the public orchestrator.
- `src/graph/knowledge_graph.py` owns graph extraction and traversal.
- `src/guardrails/writer.py` owns citation-bound answer generation.
- `src/guardrails/verifier.py` owns claim verification and decision gating.
- `src/multimodal/table_retriever.py` and `src/multimodal/image_retriever.py` own non-text retrieval.

Changes should be additive and small. New helper functions for metrics should live in `src/guardrails/verifier.py` unless they become large enough to justify a separate module.

## Data Flow

The agent still routes every query through vector retrieval and conditionally adds graph, table, and image evidence. Errors in optional routes should be logged and should not crash the answer path. Guardrails receive the merged context and return a `GuardrailedAnswer` with decision, support rate, contradiction rate, and citations.

## Decision Handling

Allowed decisions should become:

- `answer`
- `answer_with_disclaimer`
- `extractive`
- `ask_clarify`
- `no_answer`
- `refuse`

The implementation should not force `ask_clarify` or `refuse` into normal TechStore answers unless deterministic signals exist:

- `refuse`: unsafe or policy-irrelevant requests such as credential theft or malware instructions.
- `ask_clarify`: ambiguous product/policy questions where the answer depends on purchase date or product model and the context contains conflicting policy versions.

## Observability

For each query, logs should include:

- routing paths used;
- number of context documents;
- final decision;
- claim support rate;
- contradiction rate;
- citation density;
- numeric grounding rate;
- cited sources.

The printed log can remain concise, but the structured logger should carry the richer fields.

## Testing Strategy

Use TDD for behavior changes:

- Add failing tests for the new allowed decisions.
- Add failing tests for citation density and numeric grounding helpers.
- Add failing tests ensuring optional retrieval failures are logged instead of silently swallowed.
- Add image retriever tests that do not require LLM or network.

Verification commands:

- `.\.venv\Scripts\python.exe -m pytest tests -q`
- `.\.venv\Scripts\python.exe -m pytest c03-t05-bruno-pieri-m2-challenge\tests\test_stop2_metrics.py c03-t05-bruno-pieri-m2-challenge\tests\test_stop2_vectorstore.py c03-t05-bruno-pieri-m2-challenge\tests\test_mandatory_cases.py::test_guardrailed_answer_valid_construction -q`
- Run mandatory A/B/C individually only after lightweight tests pass, because each one is slow and uses LLM calls.

## Risks

- The broad Week 6 PDF asks for Odyssey. This design explicitly chooses the TechStore path because it matches the repo and tests.
- Full image-region grounding is not implemented. The image modality remains caption/tag grounded.
- Mandatory tests are slow because graph extraction runs on cold start.

## Success Criteria

- Existing tests continue to pass.
- Mandatory A/B/C still pass individually.
- Week 6 implementation has fewer hidden failure modes.
- Documentation clearly frames the work as the TechStore Stop 3 implementation.
