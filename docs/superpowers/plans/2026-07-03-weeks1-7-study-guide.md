# Guia de Estudo das Weeks 1 a 7 - Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Gerar um guia didatico em portugues, com 90 a 120 paginas, que explique o desenvolvimento do TechStore Plus da Week 1 ate a Week 7 e ensine uma pessoa iniciante a executar e testar cada etapa.

**Architecture:** O conteudo sera pesquisado a partir dos repositorios M1, M2 e M3, dos PDFs dos desafios, dos notebooks e dos testes reais. A fonte principal sera um Markdown versionado; um gerador Python baseado em ReportLab convertera essa fonte e os diagramas em PDF A4, e testes com PyPDF verificarao estrutura, paginas, termos obrigatorios e ausencia de segredos.

**Tech Stack:** Markdown, Python 3.13, ReportLab, PyPDF, PyMuPDF, pytest, Git, PowerShell

---

## File Structure

- Create: `docs/study-guide/source-matrix.md` - matriz de fontes, requisitos, arquivos e testes por Week.
- Create: `docs/study-guide/weeks-1-7-guia-completo.md` - fonte editorial completa.
- Create: `docs/study-guide/validation-report.md` - comandos executados e resultados sanitizados.
- Create: `docs/study-guide/assets/` - diagramas PNG gerados pelo proprio projeto.
- Create: `docs/study-guide/weeks-1-7-guia-completo.pdf` - entrega final.
- Create: `scripts/generate_weeks_1_7_study_guide.py` - conversor Markdown/ativos para PDF.
- Create: `tests/test_study_guide_pdf.py` - verificacoes estruturais e de seguranca.
- Reference: `scripts/generate_code_explanation_pdf.py` - padrao visual ReportLab existente.

## Task 1: Criar um ambiente isolado e inventariar as fontes

**Files:**
- Create: `docs/study-guide/source-matrix.md`
- Reference: `docs/superpowers/specs/2026-07-03-weeks1-7-study-guide-design.md`

- [ ] **Step 1: Criar worktree da documentacao**

```powershell
git check-ignore .worktrees
git worktree add .worktrees/weeks-1-7-study-guide -b docs/weeks-1-7-study-guide
```

Expected: worktree criado a partir de `main`, sem incluir as alteracoes locais do BrunoAudioManager.

- [ ] **Step 2: Localizar os PDFs oficiais**

```powershell
Get-ChildItem "C:\Users\evilc\OneDrive\Documents\Cursos\Pluralit\Aulas" -Recurse -File -Filter *.pdf |
    Where-Object { $_.FullName -match 'Week [1-7]' } |
    Select-Object FullName, Length, LastWriteTime
```

Expected: lista das fontes disponiveis por Week. Ausencias devem ser registradas e supridas pelo README, codigo e historico Git, nunca por invencao.

- [ ] **Step 3: Registrar os repositorios publicados**

```powershell
git ls-remote https://github.com/pluralit-ai-solutions-genai-pathway/c03-t05-bruno-pieri-m1-challenge.git refs/heads/main
git ls-remote https://github.com/pluralit-ai-solutions-genai-pathway/c03-t05-bruno-pieri-m2-challenge.git refs/heads/main
git ls-remote https://github.com/pluralit-ai-solutions-genai-pathway/c03-t05-bruno-pieri-m3-challenge.git refs/heads/main
```

Record the verified commit hashes in `source-matrix.md`.

- [ ] **Step 4: Preencher a matriz de rastreabilidade**

Use this exact table structure:

```markdown
| Week | Desafio/PDF | Repositorio/commit | Principais arquivos | Testes | Conceitos | Lacunas |
|---|---|---|---|---|---|---|
| 1 | caminho ou indisponivel | M1/hash | arquivos reais | comandos reais | fundamentos | nenhuma ou descricao |
| 2 | caminho ou indisponivel | M1/hash | arquivos reais | comandos reais | tools | nenhuma ou descricao |
| 3 | caminho ou indisponivel | M1/hash | arquivos reais | comandos reais | memoria/agente | nenhuma ou descricao |
| 4 | m2u2...pdf | M2/hash | loader.py, vectorstore.py | pytest... | RAG | ... |
| 5 | m2u4...pdf | M2/hash | reranker.py, metrics.py | pytest... | MMR | ... |
| 6 | m2u6...pdf | M2/hash | rag_agent.py, graph/, guardrails/ | pytest... | producao | ... |
| 7 | m3u2...pdf | M3/hash | challenge.ipynb, langgraph_challenge_agent.py | pytest... | LangGraph | numeracao Week 7/8 explicada |
```

- [ ] **Step 5: Commit da matriz**

```powershell
git add docs/study-guide/source-matrix.md
git commit -m "docs: inventory weeks 1 to 7 sources"
```

## Task 2: Capturar evidencias de testes reais

**Files:**
- Create: `docs/study-guide/validation-report.md`
- Reference: repositories M1, M2, and M3

- [ ] **Step 1: Criar o cabecalho do relatorio**

```markdown
# Relatorio de validacao do guia Weeks 1 a 7

Data da execucao: YYYY-MM-DD
Sistema: Windows / PowerShell / Python 3.13

> Saidas foram resumidas e sanitizadas. Nenhuma variavel secreta foi registrada.
```

- [ ] **Step 2: Executar os testes M1**

Run the test commands documented by the M1 repository README. Record command, total passed, warnings, skipped tests and failures. Do not copy environment values.

- [ ] **Step 3: Executar os testes M2**

```powershell
.\.venv\Scripts\python.exe -m pytest .\c03-t05-bruno-pieri-m2-challenge\tests -q
```

Also run the three mandatory Week 6 cases individually and record their behavior in plain language.

- [ ] **Step 4: Executar os testes M3 Stop 1**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_langgraph_challenge_agent.py tests/test_scaffolding.py -q
```

Expected from the published Stop 1 baseline: 16 passing tests. If the current repository has evolved, record the fresh number instead of preserving an obsolete number.

- [ ] **Step 5: Registrar testes manuais de notebooks**

For every notebook used in the guide, record:

```markdown
| Notebook | Kernel | API required | Key outputs | Execution status |
|---|---|---:|---|---|
```

- [ ] **Step 6: Scan de segredos no relatorio**

```powershell
rg -n "sk-|lsv2_|ntn_|OPENAI_API_KEY=|LANGCHAIN_API_KEY=" docs/study-guide
```

Expected: no matches.

- [ ] **Step 7: Commit das evidencias**

```powershell
git add docs/study-guide/validation-report.md
git commit -m "docs: record weeks 1 to 7 verification evidence"
```

## Task 3: Criar o esqueleto editorial completo

**Files:**
- Create: `docs/study-guide/weeks-1-7-guia-completo.md`

- [ ] **Step 1: Criar front matter e sumario editorial**

The source must start with:

```markdown
---
title: TechStore Plus - Guia Completo das Weeks 1 a 7
language: pt-BR
audience: iniciante
version: 1.0
---

# TechStore Plus
## Guia completo de desenvolvimento, arquitetura e testes

## Como utilizar este guia
## Preparacao do ambiente
## Glossario inicial
## Week 1
## Week 2
## Week 3
## Week 4
## Week 5
## Week 6
## Week 7
## Arquitetura integrada
## Guia unificado de testes
## Solucao de problemas
## Glossario completo
## Referencias
```

- [ ] **Step 2: Adicionar o modelo padrao em cada Week**

Every weekly chapter must contain these exact second-level sections:

```markdown
### Objetivo
### O que ja existia
### Problema a resolver
### Conceitos essenciais
### Arquitetura
### Implementacao por arquivo
### Codigo explicado
### Por que esta abordagem
### Como executar
### Como testar
### Resultado esperado
### Problemas e correcoes
### Limitacoes
### Revisao da Week
```

- [ ] **Step 3: Adicionar marcadores de diagramas**

Use explicit, parseable markers:

```markdown
![Fluxo geral](assets/architecture-evolution.png)
![Pipeline RAG](assets/rag-pipeline.png)
![StateGraph](assets/langgraph-flow.png)
```

- [ ] **Step 4: Commit do esqueleto**

```powershell
git add docs/study-guide/weeks-1-7-guia-completo.md
git commit -m "docs: outline weeks 1 to 7 study guide"
```

## Task 4: Redigir fundamentos e Weeks 1 a 3

**Files:**
- Modify: `docs/study-guide/weeks-1-7-guia-completo.md`

- [ ] **Step 1: Redigir orientacao para iniciantes**

Cover Python, virtual environments, `.env`, APIs, Git, notebooks and pytest. Every command must be PowerShell-compatible and state the correct working directory.

- [ ] **Step 2: Redigir Week 1 from verified sources**

Explain the initial user problem, application flow, main files and first tests. Cite real file paths inline, for example `src/...`, and avoid claiming functionality absent from the source matrix.

- [ ] **Step 3: Redigir Week 2 from verified sources**

Explain tools as controlled functions the agent can invoke, argument validation, returned data and error handling. Include one short code excerpt and a numbered walkthrough.

- [ ] **Step 4: Redigir Week 3 from verified sources**

Explain agent memory, conversation persistence, identifiers and integrations. Contrast stateless and stateful conversations with a table.

- [ ] **Step 5: Add test procedures for Weeks 1-3**

Each procedure must use this template:

````markdown
#### Teste: nome descritivo
**Objetivo:** ...
**Pre-requisitos:** ...
**Diretorio:** `...`
**Comando:**
```powershell
comando real
```
**Resultado esperado:** ...
**Se falhar:** ...
````

- [ ] **Step 6: Commit do primeiro bloco**

```powershell
git add docs/study-guide/weeks-1-7-guia-completo.md
git commit -m "docs: explain foundations and weeks 1 to 3"
```

## Task 5: Redigir Weeks 4 e 5

**Files:**
- Modify: `docs/study-guide/weeks-1-7-guia-completo.md`

- [ ] **Step 1: Explain the Week 4 RAG pipeline**

Cover loaders, page/source metadata, RecursiveCharacterTextSplitter, 500/50 chunking, OpenAI embeddings, ChromaDB persistence, similarity search and the `requests` documentation mini-project.

- [ ] **Step 2: Explain key Week 4 code**

Use excerpts from:

```text
c03-t05-bruno-pieri-m2-challenge/src/pipeline/loader.py
c03-t05-bruno-pieri-m2-challenge/src/pipeline/vectorstore.py
Week4_RAG_TechStore.ipynb
Week4_RAG_Python_Library.ipynb
```

- [ ] **Step 3: Explain Week 5 optimization**

Cover similarity baseline, MMR (`fetch_k=20`, `k=6`), cross-encoder re-ranking, top-3 compression, chunk experiments, Precision@3, Precision@6 and MRR.

- [ ] **Step 4: Include the verified metrics table**

```markdown
| Pipeline | Precision@3 | Precision@6 | MRR |
|---|---:|---:|---:|
| Similarity baseline | 0.33 | 0.20 | 0.93 |
| MMR + re-ranking | 0.37 | 0.18 | 1.00 |
```

Before publication, compare these values with `docs/retrieval-metrics.md`; use the repository values if they differ.

- [ ] **Step 5: Add offline/API test separation**

Clearly label which tests call embeddings/LLM APIs and which test metric functions without network access.

- [ ] **Step 6: Commit do bloco RAG**

```powershell
git add docs/study-guide/weeks-1-7-guia-completo.md
git commit -m "docs: explain rag fundamentals and optimization"
```

## Task 6: Redigir Weeks 6 e 7

**Files:**
- Modify: `docs/study-guide/weeks-1-7-guia-completo.md`

- [ ] **Step 1: Explain Week 6 production RAG**

Cover `TechStoreRAGAgent`, MMR/re-ranking, Graph RAG BFS, table/image retrieval, cited writer, verifier, decision gate, citation density, numeric grounding and optional-route logging.

- [ ] **Step 2: Explain Week 6 mandatory cases**

Document no-answer guardrail, graph traversal and table-grounded numeric answer. Explain what each assertion protects.

- [ ] **Step 3: Explain Week 7 LangGraph architecture**

Cover TypedDict, reducers, Agent/ToolNode/inspect_tools, deterministic validation exit, five executed-call cap, atomic parallel-batch rejection, checkpoint/thread ID, interrupt/resume and streaming.

- [ ] **Step 4: Explain the Week 7 arithmetic discrepancy**

State that `(2.5 + 7) * 3 = 28.5`; preserve the original challenge expectation only as a documented typo.

- [ ] **Step 5: Explain validation edge cases**

Include boolean, NaN, Infinity, arithmetic overflow, framework ToolNode errors and malformed error sentinels. Explain why safe failure is preferable to another model guess.

- [ ] **Step 6: Commit do bloco de producao**

```powershell
git add docs/study-guide/weeks-1-7-guia-completo.md
git commit -m "docs: explain production rag and langgraph"
```

## Task 7: Redigir arquitetura integrada e guia de testes

**Files:**
- Modify: `docs/study-guide/weeks-1-7-guia-completo.md`

- [ ] **Step 1: Build the chronological architecture narrative**

Explain how the system evolves from chatbot to tools, memory, RAG, optimized retrieval, guarded multimodal RAG and explicit LangGraph control.

- [ ] **Step 2: Add a responsibility map**

```markdown
| Layer | Responsibility | Main files | Introduced in |
|---|---|---|---|
| Interface | Receives user requests | verified paths | Week ... |
| Agent | Chooses actions | verified paths | Week ... |
| Retrieval | Finds evidence | verified paths | Week 4 |
| Guardrails | Validates answers | verified paths | Week 6 |
| Graph control | Routes nodes safely | verified paths | Week 7 |
```

- [ ] **Step 3: Write the clean-machine setup guide**

Include clone, virtual environment, dependency installation, `.env.example` copy and safe key configuration. Never include a real key.

- [ ] **Step 4: Write the unified test sequence**

Order tests from cheapest/offline to API-dependent. Include expected pass counts only when confirmed by Task 2; otherwise say “all collected tests must pass”.

- [ ] **Step 5: Add troubleshooting**

Cover missing key, wrong working directory, missing Chroma collection, model/network failure, OneDrive locking, Jupyter kernel mismatch, LangGraph deprecation warnings and stale checkpoints.

- [ ] **Step 6: Add review questions and glossary**

Provide 3-5 questions per Week plus definitions for LLM, token, embedding, chunk, vector store, retriever, MMR, re-ranker, RAG, guardrail, graph, node, edge, reducer, checkpoint and thread ID.

- [ ] **Step 7: Commit integrated content**

```powershell
git add docs/study-guide/weeks-1-7-guia-completo.md
git commit -m "docs: add integrated architecture and test guide"
```

## Task 8: Generate original diagrams

**Files:**
- Create: `docs/study-guide/assets/architecture-evolution.png`
- Create: `docs/study-guide/assets/rag-pipeline.png`
- Create: `docs/study-guide/assets/langgraph-flow.png`
- Create: `docs/study-guide/assets/test-pyramid.png`
- Create: `scripts/generate_weeks_1_7_study_guide.py`

- [ ] **Step 1: Implement deterministic diagram helpers**

The generator must expose these functions:

```python
def draw_architecture_evolution(output_path: Path) -> None: ...
def draw_rag_pipeline(output_path: Path) -> None: ...
def draw_langgraph_flow(output_path: Path) -> None: ...
def draw_test_pyramid(output_path: Path) -> None: ...
```

Use ReportLab `Drawing`, `Rect`, `String`, `Line` and `renderPM.drawToFile`; do not depend on web-hosted images.

- [ ] **Step 2: Generate diagrams**

```powershell
.\.venv\Scripts\python.exe scripts/generate_weeks_1_7_study_guide.py --diagrams-only
```

Expected: four non-empty PNG files at least 1400 pixels wide.

- [ ] **Step 3: Inspect all diagrams**

Use the local image viewer on each PNG. Verify text fits, arrows do not cross labels, and the palette remains readable in print.

- [ ] **Step 4: Commit diagrams and generator scaffold**

```powershell
git add scripts/generate_weeks_1_7_study_guide.py docs/study-guide/assets
git commit -m "docs: add study guide diagrams"
```

## Task 9: Build the PDF generator with tests

**Files:**
- Modify: `scripts/generate_weeks_1_7_study_guide.py`
- Create: `tests/test_study_guide_pdf.py`
- Create: `docs/study-guide/weeks-1-7-guia-completo.pdf`

- [ ] **Step 1: Write the failing structural test**

```python
from pathlib import Path
from pypdf import PdfReader

PDF = Path("docs/study-guide/weeks-1-7-guia-completo.pdf")


def test_study_guide_pdf_has_expected_scope():
    assert PDF.exists()
    reader = PdfReader(PDF)
    assert 90 <= len(reader.pages) <= 120
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    for week in range(1, 8):
        assert f"Week {week}" in text
    assert "Como testar" in text
    assert "Por que" in text


def test_study_guide_pdf_does_not_expose_secrets():
    reader = PdfReader(PDF)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    forbidden = ("sk-proj-", "lsv2_", "ntn_", "OPENAI_API_KEY=")
    assert not any(token in text for token in forbidden)
```

- [ ] **Step 2: Run RED**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_study_guide_pdf.py -q
```

Expected: FAIL because the final PDF does not exist yet.

- [ ] **Step 3: Implement the generator interface**

```python
def parse_markdown(source: Path) -> list[dict]: ...
def build_styles() -> dict[str, ParagraphStyle]: ...
def build_story(blocks: list[dict], assets_dir: Path) -> list: ...
def add_page_number(canvas, doc) -> None: ...
def build_pdf(source: Path, output: Path, assets_dir: Path) -> None: ...
def main() -> int: ...
```

Requirements:

- A4 pages;
- title page without footer;
- generated table of contents;
- numbered headings;
- syntax-styled code blocks with wrapping;
- repeated table headers;
- page number and short title in footer;
- images scaled within page bounds;
- explicit page breaks before each Week;
- source and output paths configurable by CLI.

- [ ] **Step 4: Generate the PDF**

```powershell
.\.venv\Scripts\python.exe scripts/generate_weeks_1_7_study_guide.py `
  --source docs/study-guide/weeks-1-7-guia-completo.md `
  --output docs/study-guide/weeks-1-7-guia-completo.pdf
```

- [ ] **Step 5: Run GREEN**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_study_guide_pdf.py -q
```

Expected: all PDF tests pass.

- [ ] **Step 6: Commit generator, tests and PDF**

```powershell
git add scripts/generate_weeks_1_7_study_guide.py tests/test_study_guide_pdf.py docs/study-guide/weeks-1-7-guia-completo.pdf
git commit -m "docs: generate weeks 1 to 7 study guide pdf"
```

## Task 10: Perform editorial and visual quality assurance

**Files:**
- Modify: `docs/study-guide/weeks-1-7-guia-completo.md`
- Modify: `docs/study-guide/validation-report.md`
- Regenerate: `docs/study-guide/weeks-1-7-guia-completo.pdf`

- [ ] **Step 1: Run source-quality scans**

```powershell
rg -n "TODO|TBD|Lorem|preencher depois|inserir aqui" docs/study-guide
rg -n "sk-|lsv2_|ntn_|OPENAI_API_KEY=|LANGCHAIN_API_KEY=" docs/study-guide
```

Expected: no matches.

- [ ] **Step 2: Check weekly section completeness**

Create a small verification in `tests/test_study_guide_pdf.py` that reads the Markdown and asserts each Week contains all standard chapter headings.

- [ ] **Step 3: Render PDF pages to PNG**

```powershell
.\.venv\Scripts\python.exe -c "import fitz, pathlib; d=fitz.open('docs/study-guide/weeks-1-7-guia-completo.pdf'); out=pathlib.Path('docs/study-guide/rendered'); out.mkdir(exist_ok=True); [p.get_pixmap(matrix=fitz.Matrix(1.5,1.5), alpha=False).save(out/f'page-{i+1:03}.png') for i,p in enumerate(d)]"
```

- [ ] **Step 4: Inspect representative and risk pages**

Inspect at minimum:

- cover;
- table of contents;
- first and last page of every Week;
- every page containing a diagram;
- every page containing a large table;
- every page containing a code block longer than 20 lines;
- final references page.

Verify no clipping, overlap, blank body pages, orphan headings or unreadable code.

- [ ] **Step 5: Check PDF text and links**

Use PyPDF to confirm every Week and repository URL is extractable. Manually test the three repository links in the final PDF.

- [ ] **Step 6: Regenerate after corrections**

Never patch the PDF directly. Fix Markdown, generator or assets, then regenerate and rerun all PDF tests.

- [ ] **Step 7: Record final validation**

Append to `validation-report.md`:

```markdown
## Validacao final do PDF
- Paginas: N
- Weeks encontradas: 1, 2, 3, 4, 5, 6, 7
- Testes estruturais: PASS
- Scan de segredos: PASS
- Inspecao visual: PASS
- Links conferidos: PASS
```

- [ ] **Step 8: Final commit**

```powershell
git add docs/study-guide scripts/generate_weeks_1_7_study_guide.py tests/test_study_guide_pdf.py
git commit -m "docs: finalize weeks 1 to 7 study guide"
```

## Task 11: Final independent verification and handoff

**Files:**
- Verify: all study-guide artifacts

- [ ] **Step 1: Run all guide tests fresh**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_study_guide_pdf.py -q
```

- [ ] **Step 2: Run project regression tests**

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
```

Document pre-existing warnings separately from failures.

- [ ] **Step 3: Verify Git scope**

```powershell
git status --short
git diff --stat main...HEAD
git log --oneline main..HEAD
```

Expected: only study-guide source, assets, generator, tests, PDF and validation artifacts differ; no BrunoAudioManager files, `.env`, logs or backups.

- [ ] **Step 4: Report deliverables**

Provide clickable local paths to the PDF, Markdown source and validation report. Report page count, tests and any residual limitations. Do not publish remotely without explicit approval.
