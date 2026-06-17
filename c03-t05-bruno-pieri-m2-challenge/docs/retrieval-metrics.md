# Retrieval Quality Metrics — Stop 2

## Instructions

Define a small evaluation set of 10 questions, each with known relevant documents
(by filename). Then measure Precision@k and MRR for both:
- **Baseline**: the simple similarity retriever from Stop 1 (k=4).
- **Optimized**: MMR (k=6, fetch_k=20) + cross-encoder re-ranking (top-3).

Implement the metric functions in your pipeline before filling this table. The
capstone brief provides reference implementations in Stop 2, Component 4.

## Evaluation Set

| # | Question | Relevant documents (filenames) |
|---|---|---|
| 1 | "What is the return window for a refund?" | policy_return_policy.txt |
| 2 | "How do I reset the Router NX300?" | product_manual_router_nx300.txt, support_router_wont_connect.txt |
| 3 | "What does the Premium Protection Plan cover?" | policy_warranty_terms.txt |
| 4 | "Steps to file a warranty claim online" | support_warranty_claim_process.txt |
| 5 | "Laptop Pro X1 specifications" | product_manual_laptop_pro_x1.txt, laptop_specs.csv |
| 6 | "How do I pair a Zigbee device with the Smart Hub?" | product_manual_smart_hub_home.txt |
| 7 | "Does TechStore Plus cover accidental damage?" | policy_warranty_terms.txt |
| 8 | "Laptop won't turn on — first troubleshooting step" | support_laptop_wont_power_on.txt |
| 9 | "What is the restocking fee for an opened product?" | policy_return_policy.txt |
| 10 | "Warranty period for networking equipment" | policy_warranty_terms.txt, product_manual_router_nx300.txt |

## Results

| Pipeline | Precision@3 | Precision@6 | MRR |
|---|---|---|---|
| Baseline (similarity, k=4) | 0.33 | 0.20 | 0.93 |
| Optimized (MMR k=6, lambda=0.85 + re-rank top-3) | 0.37 | 0.18 | 1.00 |

## Analysis

### Precision@k observations

Precision@3 improved slightly after optimization because MMR surfaced a more
diverse candidate set and the cross-encoder promoted the best passages into the
top-3 context window. Precision@6 is lower for the optimized pipeline because the
final retriever intentionally returns only the re-ranked top-3 chunks to the LLM;
the metric still uses a fixed denominator of 6, so missing ranks 4-6 count against
the score.

Cross-encoder re-ranking boosted source-level relevance on query 3 (Premium
Protection Plan coverage), where the baseline did not rank the current warranty
policy first. The optimized pipeline placed `policy_warranty_terms.txt` at rank 1.

The trade-off is latency from cross-encoder inference and a lower Precision@6
when evaluating a top-3 compressed context with a six-slot denominator.

### MRR observations

Re-ranking significantly boosted MRR on query 3. For "What does the Premium
Protection Plan cover?", the baseline similarity retriever placed support and
service documents above the current warranty policy. MMR plus cross-encoder
re-ranking promoted `policy_warranty_terms.txt` to rank 1.

The baseline MRR of 0.93 indicates that the first relevant document was already
ranked first for most queries. The optimized pipeline raises MRR to 1.00, meaning
the first returned chunk source is relevant for every evaluation query.

## Conclusion

The optimized pipeline (MMR k=6, lambda=0.85 + cross-encoder re-ranking top-3)
improves Precision@3 (+0.04) and MRR (+0.07) while lowering Precision@6 (-0.02)
because the final context is compressed to three chunks. The Stop 2 requirement
— "the optimized pipeline must match or exceed the baseline on MRR" — is
satisfied: optimized MRR is 1.00 versus the baseline MRR of 0.93.
