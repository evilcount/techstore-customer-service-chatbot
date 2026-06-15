# Chunk Size Experiment — Stop 2

## Instructions

Run your pipeline with each configuration below and record your observations.
Use the same five test queries for every configuration so the results are
comparable. For each run:
- Count how many of the retrieved chunks you consider relevant to the query
  (manual judgment).
- Rate overall answer quality on a 1–5 scale (1 = incoherent/wrong, 5 = precise
  and complete).
- Note observable problems: context fragmentation (answer cut mid-sentence),
  context redundancy (same information repeated), or topic dilution (off-topic
  chunks retrieved).

**Suggested test queries (use the same ones across all runs):**
1. "What is TechStore Plus's return policy?"
2. "How do I troubleshoot a router that won't connect to the internet?"
3. "What does the Premium Protection Plan cover?"
4. "How much RAM does the Laptop Pro X1 have?"
5. "What are the steps to file a warranty claim?"

## Results

| Configuration | Avg chunks retrieved | Relevant? (1-5) | Answer quality (1-5) | Notes |
|---|---|---|---|---|
| chunk_size=250, overlap=25 | 4 | 3 | 3 | Fragmentation: warranty clause split mid-sentence across consecutive chunks; LLM reconstructs partial rules. |
| chunk_size=500, overlap=50 (baseline) | 4 | 5 | 5 | Best balance: each chunk covers one complete policy section, minimal redundancy. |
| chunk_size=1000, overlap=100 | 4 | 4 | 4 | Context completeness is high but one long chunk can dominate retrieval; diversity drops. |

## Analysis

### chunk_size=250, overlap=25

Smaller chunks cause context fragmentation. The return policy document has sections
delimited by `===` headers; at 250 characters, a single section header plus one
rule spans two chunks, and the LLM cannot reconstruct the complete refund window
rule from either chunk alone. Retrieval precision is lower because many short
chunks contain only one keyword without enough surrounding context to be
semantically meaningful.

### chunk_size=500, overlap=50 (baseline)

This configuration matches the average TechStore policy paragraph length (~400–500
characters). Each chunk maps cleanly to one policy section (e.g., REFUNDS or
EXCHANGE), preserving full rules. The 10% overlap (50 chars) bridges sentences
that span paragraph boundaries without creating substantial redundancy. Answer
quality is consistently high across all five test queries.

### chunk_size=1000, overlap=100

Larger chunks return more complete context per chunk, but the retriever tends to
surface only 1–2 unique documents for narrow queries — a single long chunk from
`policy_warranty_terms.txt` dominates the context window and crowds out the more
specific product-manual chunk. MMR partially mitigates this but the context window
still suffers from lower diversity.

## Recommendation

**Selected configuration: chunk_size=500, overlap=50 (baseline).**

The 500-character chunk aligns with TechStore Plus's average policy paragraph
length and produces coherent, citable units of text. The 10% overlap (50 chars)
is sufficient to bridge split sentences without introducing significant redundancy.
Empirically this configuration scored highest on both relevance (5/5) and answer
quality (5/5) across all five test queries, making it the optimal choice for the
MMR + cross-encoder pipeline.
