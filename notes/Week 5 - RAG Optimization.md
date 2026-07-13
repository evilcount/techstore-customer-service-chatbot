---
week: 5
status: completed
tags:
  - rag
  - mmr
  - reranking
  - evaluation
---

# Week 5 - RAG Optimization

## Objective

Improve retrieval relevance, diversity and ranking quality.

## Implemented

- Maximum Marginal Relevance retrieval
- MMR configuration with `fetch_k=20` and `k=6`
- Cross-encoder re-ranking
- Selection of the top three chunks
- Chunk size experiments
- Evaluation set with ten technical questions
- Precision@3, Precision@6 and MRR metrics

## Results

| Pipeline | Precision@3 | Precision@6 | MRR |
|---|---:|---:|---:|
| Similarity baseline | 0.33 | 0.20 | 0.93 |
| MMR + re-ranking | 0.37 | 0.18 | 1.00 |

## Conclusion

The optimized pipeline returned a relevant source in the first position for every evaluation query.

## Main files

- `Week5_RAG_Optimization.ipynb`
- `src/pipeline/reranker.py`
- `src/pipeline/metrics.py`
- `docs/chunk-experiment.md`
- `docs/retrieval-metrics.md`

## Related notes

- [[MMR and Reranking]]
- [[Retrieval Metrics]]
- [[Week 4 - RAG Fundamentals]]
- [[Week 6 - Production RAG]]