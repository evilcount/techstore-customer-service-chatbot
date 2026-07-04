# Sarlacc Tender Compliance Assistant Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a two-week PoC that extracts cited tender requirements and catalog specifications, performs hybrid compliance matching, and presents an auditable human-review workflow whose go/no-go gate is at least 95% mandatory-requirement recall.

**Architecture:** Extend the existing FastAPI, SQLAlchemy, Next.js, pytest, and Vitest application. A typed domain layer owns evidence and decision contracts; deterministic extraction and rules handle measurable fields; a provider-neutral semantic-review port handles only unresolved narrative cases; an evidence merger enforces decision precedence before persistence and human review.

**Tech Stack:** Python 3.11+, FastAPI, Pydantic 2, SQLAlchemy 2, PyMuPDF, pdfplumber, Pint, OpenAI-compatible structured output adapter, PostgreSQL/SQLite for PoC, Next.js 15, React 19, pytest, Vitest.

---

## File Structure

Create a focused `backend/app/tender/` package. Do not place tender logic in the existing chat service.

```text
backend/app/tender/
├── __init__.py              # package marker
├── schemas.py               # Pydantic domain and API contracts
├── extraction.py            # native PDF text/table extraction and OCR routing
├── normalization.py         # canonical categories, operators, values, and units
├── rules.py                 # deterministic comparison engine
├── semantic.py              # provider-neutral semantic review interface and adapter
├── decisions.py             # precedence and evidence merger
├── models.py                # SQLAlchemy tender, document, requirement, result, review models
├── repository.py            # persistence operations
├── workflow.py              # explicit resumable analysis state machine
├── evaluation.py            # golden-set metrics and go/no-go decision
├── reporting.py             # CSV/JSON compliance report generation
└── api.py                   # FastAPI upload, run, review, and report endpoints

backend/tests/tender/
├── fixtures/epec_golden.json
├── test_schemas.py
├── test_extraction.py
├── test_normalization.py
├── test_rules.py
├── test_semantic.py
├── test_decisions.py
├── test_repository.py
├── test_workflow.py
├── test_evaluation.py
├── test_reporting.py
└── test_api.py

app/tenders/page.tsx         # human review page
components/tenders/
├── UploadPanel.tsx          # document upload and analysis trigger
├── RequirementTable.tsx     # status filters and requirement rows
└── EvidencePanel.tsx        # side-by-side evidence and reviewer action
lib/tenders-api.ts           # typed HTTP client
tests-frontend/tenders.test.tsx
```

## Task 1: Dependencies, Configuration, and Package Boundary

**Files:**
- Modify: `backend/requirements.txt`
- Modify: `backend/app/core/config.py`
- Create: `backend/app/tender/__init__.py`
- Test: `backend/tests/tender/test_schemas.py`

- [ ] **Step 1: Add dependency and configuration assertions**

```python
# backend/tests/tender/test_schemas.py
from backend.app.core.config import Settings


def test_tender_settings_have_safe_defaults():
    settings = Settings()
    assert settings.tender_storage_dir == "./tender_data"
    assert settings.semantic_review_enabled is False
    assert settings.semantic_review_model == "gpt-4.1-mini"
    assert settings.semantic_review_max_retries == 1
```

- [ ] **Step 2: Run the test and verify it fails**

Run: `.\.venv\Scripts\python.exe -m pytest backend/tests/tender/test_schemas.py -v`  
Expected: FAIL because the tender settings do not exist.

- [ ] **Step 3: Add the dependencies and settings**

Append to `backend/requirements.txt`:

```text
PyMuPDF
pdfplumber
pint
python-multipart
```

Add to `Settings` in `backend/app/core/config.py`:

```python
tender_storage_dir: str = "./tender_data"
semantic_review_enabled: bool = False
semantic_review_model: str = "gpt-4.1-mini"
semantic_review_max_retries: int = 1
```

Create `backend/app/tender/__init__.py` as an empty package marker.

- [ ] **Step 4: Install and verify**

Run: `.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt`  
Expected: exit code 0.

Run: `.\.venv\Scripts\python.exe -m pytest backend/tests/tender/test_schemas.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
git add backend/requirements.txt backend/app/core/config.py backend/app/tender/__init__.py backend/tests/tender/test_schemas.py
git commit -m "build: add tender compliance dependencies"
```

## Task 2: Typed Evidence and Compliance Contracts

**Files:**
- Create: `backend/app/tender/schemas.py`
- Modify: `backend/tests/tender/test_schemas.py`

- [ ] **Step 1: Write contract tests**

```python
from pydantic import ValidationError
import pytest

from backend.app.tender.schemas import (
    ComplianceStatus,
    Evidence,
    Operator,
    Requirement,
)


def test_requirement_requires_page_citation():
    requirement = Requirement(
        requirement_id="REQ-001",
        category="ambient_temperature",
        description="Operating temperature shall be -10 C to 45 C",
        operator=Operator.RANGE,
        required_value=[-10, 45],
        unit="degC",
        mandatory=True,
        evidence=Evidence(document_id="epec", page=11, text="Ambient temperature: -10°C to +45°C"),
    )
    assert requirement.evidence.page == 11
    assert ComplianceStatus.REVIEW_REQUIRED.value == "REVIEW_REQUIRED"


def test_evidence_rejects_blank_source_text():
    with pytest.raises(ValidationError):
        Evidence(document_id="epec", page=11, text=" ")
```

- [ ] **Step 2: Run and verify failure**

Run: `.\.venv\Scripts\python.exe -m pytest backend/tests/tender/test_schemas.py -v`  
Expected: FAIL with `ModuleNotFoundError: backend.app.tender.schemas`.

- [ ] **Step 3: Implement the contracts**

```python
# backend/app/tender/schemas.py
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints

NonBlank = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class Operator(StrEnum):
    EQ = "eq"
    MIN = "min"
    MAX = "max"
    RANGE = "range"
    IN = "in"
    SEMANTIC = "semantic"


class ComplianceStatus(StrEnum):
    COMPLIANT = "COMPLIANT"
    NON_COMPLIANT = "NON_COMPLIANT"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"


class Evidence(BaseModel):
    document_id: NonBlank
    page: int = Field(ge=1)
    text: NonBlank
    coordinates: tuple[float, float, float, float] | None = None
    extraction_confidence: float = Field(default=1.0, ge=0, le=1)


class Requirement(BaseModel):
    requirement_id: NonBlank
    category: NonBlank
    description: NonBlank
    operator: Operator
    required_value: float | str | list[float] | list[str] | None
    unit: str | None = None
    mandatory: bool
    conditions: list[str] = []
    evidence: Evidence


class ProductSpecification(BaseModel):
    specification_id: NonBlank
    product_family: NonBlank
    model: str | None = None
    category: NonBlank
    description: NonBlank
    offered_value: float | str | list[float] | list[str] | None
    unit: str | None = None
    conditions: list[str] = []
    evidence: Evidence


class Assessment(BaseModel):
    requirement_id: NonBlank
    specification_ids: list[str]
    status: ComplianceStatus
    decision_method: Literal["rule", "semantic", "merged", "human"]
    rationale: NonBlank
    tender_evidence: Evidence
    product_evidence: list[Evidence]
    confidence: float = Field(ge=0, le=1)
    review_reason: str | None = None
```

- [ ] **Step 4: Run contract tests**

Run: `.\.venv\Scripts\python.exe -m pytest backend/tests/tender/test_schemas.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
git add backend/app/tender/schemas.py backend/tests/tender/test_schemas.py
git commit -m "feat: define tender compliance contracts"
```

## Task 3: Cited PDF and Table Extraction

**Files:**
- Create: `backend/app/tender/extraction.py`
- Create: `backend/tests/tender/test_extraction.py`
- Create: `backend/tests/tender/fixtures/epec_page_11.pdf`

- [ ] **Step 1: Add a small generated fixture and failing test**

Create `epec_page_11.pdf` as a one-page test fixture containing `Ambient temperature: -10°C to +45°C` and a two-column table headed `Description | Required`.

```python
# backend/tests/tender/test_extraction.py
from pathlib import Path

from backend.app.tender.extraction import extract_pdf


def test_extract_pdf_preserves_page_and_table_evidence():
    path = Path("backend/tests/tender/fixtures/epec_page_11.pdf")
    result = extract_pdf(path, document_id="epec")
    assert result.pages[0].page == 1
    assert "Ambient temperature" in result.pages[0].text
    assert result.pages[0].blocks
    assert result.pages[0].tables[0].rows[0] == ["Description", "Required"]
```

- [ ] **Step 2: Run and verify failure**

Run: `.\.venv\Scripts\python.exe -m pytest backend/tests/tender/test_extraction.py -v`  
Expected: FAIL because `extract_pdf` is missing.

- [ ] **Step 3: Implement native extraction with confidence routing**

```python
# backend/app/tender/extraction.py
from pathlib import Path

import fitz
import pdfplumber
from pydantic import BaseModel


class TextBlock(BaseModel):
    text: str
    coordinates: tuple[float, float, float, float]


class ExtractedTable(BaseModel):
    rows: list[list[str]]


class ExtractedPage(BaseModel):
    page: int
    text: str
    blocks: list[TextBlock]
    tables: list[ExtractedTable]
    requires_ocr: bool


class ExtractedDocument(BaseModel):
    document_id: str
    pages: list[ExtractedPage]


def extract_pdf(path: Path, document_id: str) -> ExtractedDocument:
    native = fitz.open(path)
    pages: list[ExtractedPage] = []
    with pdfplumber.open(path) as tabular:
        for index, page in enumerate(native):
            blocks = [
                TextBlock(text=item[4].strip(), coordinates=tuple(item[:4]))
                for item in page.get_text("blocks")
                if item[4].strip()
            ]
            text = "\n".join(block.text for block in blocks)
            tables = [
                ExtractedTable(rows=[[cell or "" for cell in row] for row in table])
                for table in tabular.pages[index].extract_tables()
                if table
            ]
            pages.append(ExtractedPage(
                page=index + 1,
                text=text,
                blocks=blocks,
                tables=tables,
                requires_ocr=len(text.strip()) < 40,
            ))
    return ExtractedDocument(document_id=document_id, pages=pages)
```

- [ ] **Step 4: Run extraction tests**

Run: `.\.venv\Scripts\python.exe -m pytest backend/tests/tender/test_extraction.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
git add backend/app/tender/extraction.py backend/tests/tender/test_extraction.py backend/tests/tender/fixtures/epec_page_11.pdf
git commit -m "feat: extract cited PDF text and tables"
```

## Task 4: Normalization and Unit Safety

**Files:**
- Create: `backend/app/tender/normalization.py`
- Create: `backend/tests/tender/test_normalization.py`

- [ ] **Step 1: Write failing normalization tests**

```python
from backend.app.tender.normalization import normalize_measurement, normalize_category


def test_normalize_voltage_and_temperature():
    assert normalize_measurement(0.38, "kV", "V") == 380
    assert normalize_measurement(45, "degC", "degC") == 45


def test_normalize_known_synonym():
    assert normalize_category("maximum ripple voltage") == "output_ripple"
    assert normalize_category("grid voltage") == "input_voltage"
```

- [ ] **Step 2: Run and verify failure**

Run: `.\.venv\Scripts\python.exe -m pytest backend/tests/tender/test_normalization.py -v`  
Expected: FAIL because the normalization module is missing.

- [ ] **Step 3: Implement explicit synonyms and Pint conversion**

```python
# backend/app/tender/normalization.py
from pint import UnitRegistry

ureg = UnitRegistry(autoconvert_offset_to_baseunit=True)

CATEGORY_SYNONYMS = {
    "maximum ripple voltage": "output_ripple",
    "ripple": "output_ripple",
    "grid voltage": "input_voltage",
    "input nominal voltage": "input_voltage",
    "ambient temperature": "ambient_temperature",
    "operating temperature": "ambient_temperature",
}


def normalize_category(value: str) -> str:
    key = " ".join(value.lower().strip().split())
    return CATEGORY_SYNONYMS.get(key, key.replace(" ", "_"))


def normalize_measurement(value: float, source_unit: str, target_unit: str) -> float:
    converted = (value * ureg(source_unit)).to(target_unit).magnitude
    return round(float(converted), 9)
```

- [ ] **Step 4: Run tests**

Run: `.\.venv\Scripts\python.exe -m pytest backend/tests/tender/test_normalization.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
git add backend/app/tender/normalization.py backend/tests/tender/test_normalization.py
git commit -m "feat: normalize tender categories and units"
```

## Task 5: Deterministic Compliance Rules

**Files:**
- Create: `backend/app/tender/rules.py`
- Create: `backend/tests/tender/test_rules.py`

- [ ] **Step 1: Write the EPEC boundary cases**

```python
from backend.app.tender.rules import compare
from backend.app.tender.schemas import ComplianceStatus, Evidence, Operator, ProductSpecification, Requirement

E = Evidence(document_id="doc", page=1, text="source")


def requirement(category, operator, value, unit="degC"):
    return Requirement(requirement_id="R1", category=category, description=category,
                       operator=operator, required_value=value, unit=unit,
                       mandatory=True, evidence=E)


def specification(category, value, unit="degC"):
    return ProductSpecification(specification_id="S1", product_family="charger",
                                category=category, description=category,
                                offered_value=value, unit=unit, evidence=E)


def test_product_range_must_cover_tender_range():
    result = compare(requirement("ambient_temperature", Operator.RANGE, [-10, 45]),
                     specification("ambient_temperature", [0, 40]))
    assert result.status is ComplianceStatus.NON_COMPLIANT


def test_lower_maximum_is_compliant():
    result = compare(requirement("output_ripple", Operator.MAX, 3, "%"),
                     specification("output_ripple", 2, "%"))
    assert result.status is ComplianceStatus.COMPLIANT
```

- [ ] **Step 2: Run and verify failure**

Run: `.\.venv\Scripts\python.exe -m pytest backend/tests/tender/test_rules.py -v`  
Expected: FAIL because `compare` is missing.

- [ ] **Step 3: Implement comparison semantics**

```python
# backend/app/tender/rules.py
from backend.app.tender.normalization import normalize_measurement
from backend.app.tender.schemas import Assessment, ComplianceStatus, Operator, ProductSpecification, Requirement


def compare(req: Requirement, spec: ProductSpecification) -> Assessment:
    if req.category != spec.category or req.required_value is None or spec.offered_value is None:
        status = ComplianceStatus.REVIEW_REQUIRED
        rationale = "No deterministic comparison is available."
    else:
        offered = spec.offered_value
        required = req.required_value
        if req.unit and spec.unit and req.unit != spec.unit and isinstance(offered, (int, float)):
            offered = normalize_measurement(float(offered), spec.unit, req.unit)
        matches = {
            Operator.EQ: lambda: offered == required,
            Operator.MIN: lambda: float(offered) >= float(required),
            Operator.MAX: lambda: float(offered) <= float(required),
            Operator.RANGE: lambda: offered[0] <= required[0] and offered[1] >= required[1],
            Operator.IN: lambda: required in offered,
        }
        if req.operator not in matches:
            status = ComplianceStatus.REVIEW_REQUIRED
            rationale = "Requirement requires semantic review."
        else:
            status = ComplianceStatus.COMPLIANT if matches[req.operator]() else ComplianceStatus.NON_COMPLIANT
            rationale = f"Applied deterministic operator {req.operator.value}."
    return Assessment(requirement_id=req.requirement_id,
                      specification_ids=[spec.specification_id], status=status,
                      decision_method="rule", rationale=rationale,
                      tender_evidence=req.evidence, product_evidence=[spec.evidence],
                      confidence=1.0 if status is not ComplianceStatus.REVIEW_REQUIRED else 0.0,
                      review_reason=None if status is not ComplianceStatus.REVIEW_REQUIRED else rationale)
```

- [ ] **Step 4: Run rule tests**

Run: `.\.venv\Scripts\python.exe -m pytest backend/tests/tender/test_rules.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
git add backend/app/tender/rules.py backend/tests/tender/test_rules.py
git commit -m "feat: compare measurable tender requirements"
```

## Task 6: Constrained Semantic Review and Evidence Merger

**Files:**
- Create: `backend/app/tender/semantic.py`
- Create: `backend/app/tender/decisions.py`
- Create: `backend/tests/tender/test_semantic.py`
- Create: `backend/tests/tender/test_decisions.py`

- [ ] **Step 1: Test the provider-neutral port and precedence**

```python
# backend/tests/tender/test_decisions.py
from backend.app.tender.decisions import merge_assessments
from backend.app.tender.schemas import Assessment, ComplianceStatus, Evidence

E = Evidence(document_id="doc", page=1, text="source")


def assessment(status, method, confidence):
    return Assessment(requirement_id="R1", specification_ids=["S1"], status=status,
                      decision_method=method, rationale="evidence-based",
                      tender_evidence=E, product_evidence=[E], confidence=confidence)


def test_semantic_result_cannot_override_rule_contradiction():
    merged = merge_assessments([
        assessment(ComplianceStatus.NON_COMPLIANT, "rule", 1.0),
        assessment(ComplianceStatus.COMPLIANT, "semantic", 0.9),
    ])
    assert merged.status is ComplianceStatus.NON_COMPLIANT
    assert merged.decision_method == "merged"


def test_low_confidence_semantic_result_requires_review():
    merged = merge_assessments([assessment(ComplianceStatus.COMPLIANT, "semantic", 0.6)])
    assert merged.status is ComplianceStatus.REVIEW_REQUIRED
```

- [ ] **Step 2: Run and verify failure**

Run: `.\.venv\Scripts\python.exe -m pytest backend/tests/tender/test_semantic.py backend/tests/tender/test_decisions.py -v`  
Expected: FAIL because semantic and decision modules are missing.

- [ ] **Step 3: Implement the semantic interface and merger**

```python
# backend/app/tender/semantic.py
from typing import Protocol

from backend.app.tender.schemas import Assessment, ProductSpecification, Requirement


class SemanticReviewer(Protocol):
    def review(self, requirement: Requirement, specifications: list[ProductSpecification]) -> Assessment:
        raise NotImplementedError


class DisabledSemanticReviewer:
    def review(self, requirement: Requirement, specifications: list[ProductSpecification]) -> Assessment:
        return Assessment(
            requirement_id=requirement.requirement_id,
            specification_ids=[item.specification_id for item in specifications],
            status="REVIEW_REQUIRED",
            decision_method="semantic",
            rationale="Semantic review is disabled.",
            tender_evidence=requirement.evidence,
            product_evidence=[item.evidence for item in specifications],
            confidence=0,
            review_reason="Semantic review is disabled.",
        )
```

```python
# backend/app/tender/decisions.py
from backend.app.tender.schemas import Assessment, ComplianceStatus


def merge_assessments(items: list[Assessment], threshold: float = 0.8) -> Assessment:
    base = items[0]
    if any(item.decision_method == "rule" and item.status is ComplianceStatus.NON_COMPLIANT for item in items):
        status = ComplianceStatus.NON_COMPLIANT
        reason = "Deterministic contradiction takes precedence."
    elif any(item.confidence < threshold for item in items) or len({item.status for item in items}) > 1:
        status = ComplianceStatus.REVIEW_REQUIRED
        reason = "Low confidence or disagreement requires human review."
    else:
        status = items[0].status
        reason = "All available assessments agree."
    return base.model_copy(update={"status": status, "decision_method": "merged",
                                   "rationale": reason,
                                   "review_reason": reason if status is ComplianceStatus.REVIEW_REQUIRED else None,
                                   "confidence": min(item.confidence for item in items)})
```

- [ ] **Step 4: Run semantic and merger tests**

Run: `.\.venv\Scripts\python.exe -m pytest backend/tests/tender/test_semantic.py backend/tests/tender/test_decisions.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
git add backend/app/tender/semantic.py backend/app/tender/decisions.py backend/tests/tender/test_semantic.py backend/tests/tender/test_decisions.py
git commit -m "feat: constrain semantic tender review"
```

## Task 7: Persistence and Resumable Workflow

**Files:**
- Create: `backend/app/tender/models.py`
- Create: `backend/app/tender/repository.py`
- Create: `backend/app/tender/workflow.py`
- Modify: `backend/app/db/models.py`
- Create: `backend/tests/tender/test_repository.py`
- Create: `backend/tests/tender/test_workflow.py`

- [ ] **Step 1: Write persistence and resume tests**

```python
def test_workflow_resumes_after_completed_extraction(repository, fake_pipeline):
    analysis = repository.create_analysis("EPEC")
    repository.mark_stage_complete(analysis.id, "EXTRACTION")
    fake_pipeline.run(analysis.id)
    assert fake_pipeline.calls == ["NORMALIZATION", "MATCHING", "REVIEW_READY"]


def test_reviewer_decision_is_audited(repository):
    result = repository.save_human_decision("result-1", "COMPLIANT", "engineer@example.com")
    assert result.reviewer_email == "engineer@example.com"
    assert result.reviewed_at is not None
```

- [ ] **Step 2: Run and verify failure**

Run: `.\.venv\Scripts\python.exe -m pytest backend/tests/tender/test_repository.py backend/tests/tender/test_workflow.py -v`  
Expected: FAIL because persistence and workflow types are missing.

- [ ] **Step 3: Implement focused SQLAlchemy entities**

Define `TenderAnalysis`, `TenderDocument`, `StoredRequirement`, `StoredAssessment`, and `AnalysisEvent` in `backend/app/tender/models.py`, all inheriting `Base`. Store canonical records as JSON text for the PoC, plus indexed status, stage, timestamps, reviewer email, document SHA-256, model version, prompt version, and rule version. Import these models at the bottom of `backend/app/db/models.py` so `Base.metadata.create_all()` registers them.

Implement repository methods with these exact signatures:

```python
class TenderRepository:
    def create_analysis(self, title: str) -> TenderAnalysis:
        raise NotImplementedError
    def add_document(self, analysis_id: str, kind: str, filename: str, sha256: str, path: str) -> TenderDocument:
        raise NotImplementedError
    def current_stage(self, analysis_id: str) -> str:
        raise NotImplementedError
    def mark_stage_complete(self, analysis_id: str, stage: str) -> AnalysisEvent:
        raise NotImplementedError
    def save_requirements(self, analysis_id: str, requirements: list[Requirement]) -> None:
        raise NotImplementedError
    def save_assessments(self, analysis_id: str, assessments: list[Assessment]) -> None:
        raise NotImplementedError
    def save_human_decision(self, result_id: str, status: str, reviewer_email: str) -> StoredAssessment:
        raise NotImplementedError
```

Implement `AnalysisWorkflow.run(analysis_id)` with the ordered stages `INGESTION`, `EXTRACTION`, `NORMALIZATION`, `MATCHING`, `REVIEW_READY`; skip stages already recorded complete and stop on failure without recording completion.

- [ ] **Step 4: Run persistence tests**

Run: `.\.venv\Scripts\python.exe -m pytest backend/tests/tender/test_repository.py backend/tests/tender/test_workflow.py -v`  
Expected: PASS using SQLite and `StaticPool`.

- [ ] **Step 5: Commit**

```powershell
git add backend/app/tender/models.py backend/app/tender/repository.py backend/app/tender/workflow.py backend/app/db/models.py backend/tests/tender/test_repository.py backend/tests/tender/test_workflow.py
git commit -m "feat: persist resumable tender analyses"
```

## Task 8: Golden-Set Evaluation and Reports

**Files:**
- Create: `backend/app/tender/evaluation.py`
- Create: `backend/app/tender/reporting.py`
- Create: `backend/tests/tender/fixtures/epec_golden.json`
- Create: `backend/tests/tender/test_evaluation.py`
- Create: `backend/tests/tender/test_reporting.py`

- [ ] **Step 1: Write metric and report tests**

```python
from backend.app.tender.evaluation import evaluate


def test_go_requires_95_percent_mandatory_recall():
    expected = {f"R{i}": True for i in range(20)}
    predicted = {f"R{i}" for i in range(19)}
    result = evaluate(expected, predicted, correct_classifications=18, total_classifications=19)
    assert result.mandatory_recall == 0.95
    assert result.go is True


def test_below_threshold_is_no_go():
    result = evaluate({"R1": True, "R2": True}, {"R1"}, 1, 1)
    assert result.go is False
```

- [ ] **Step 2: Run and verify failure**

Run: `.\.venv\Scripts\python.exe -m pytest backend/tests/tender/test_evaluation.py backend/tests/tender/test_reporting.py -v`  
Expected: FAIL because evaluation and reporting modules are missing.

- [ ] **Step 3: Implement metrics and stable exports**

```python
# backend/app/tender/evaluation.py
from pydantic import BaseModel


class EvaluationResult(BaseModel):
    mandatory_recall: float
    classification_precision: float
    go: bool


def evaluate(expected: dict[str, bool], predicted: set[str],
             correct_classifications: int, total_classifications: int) -> EvaluationResult:
    mandatory = {key for key, value in expected.items() if value}
    recall = len(mandatory & predicted) / len(mandatory) if mandatory else 1.0
    precision = correct_classifications / total_classifications if total_classifications else 0.0
    return EvaluationResult(mandatory_recall=recall,
                            classification_precision=precision,
                            go=recall >= 0.95)
```

Implement `write_json_report(analysis, assessments) -> bytes` and `write_csv_report(assessments) -> bytes`. Each row must include requirement ID, status, rationale, confidence, tender page/text, product pages/text, decision method, reviewer, and reviewed timestamp. Sort by requirement ID for reproducible output.

Populate `epec_golden.json` with 50–100 engineer-approved records using this schema:

```json
{
  "requirement_id": "EPEC-4.1-D",
  "mandatory": true,
  "category": "ambient_temperature",
  "expected_status": "NON_COMPLIANT",
  "tender_page": 11,
  "catalog_page": 5
}
```

- [ ] **Step 4: Run metric and report tests**

Run: `.\.venv\Scripts\python.exe -m pytest backend/tests/tender/test_evaluation.py backend/tests/tender/test_reporting.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
git add backend/app/tender/evaluation.py backend/app/tender/reporting.py backend/tests/tender/fixtures/epec_golden.json backend/tests/tender/test_evaluation.py backend/tests/tender/test_reporting.py
git commit -m "feat: evaluate and report tender compliance"
```

## Task 9: FastAPI Review Workflow

**Files:**
- Create: `backend/app/tender/api.py`
- Modify: `backend/app/main.py`
- Create: `backend/tests/tender/test_api.py`

- [ ] **Step 1: Write API contract tests**

```python
def test_upload_rejects_non_pdf(client):
    response = client.post("/api/tenders/analyses/A1/documents",
                           files={"file": ("notes.txt", b"text", "text/plain")},
                           data={"kind": "tender"}, headers=AUTH)
    assert response.status_code == 415


def test_review_requires_reason_when_overriding(client):
    response = client.post("/api/tenders/results/R1/review",
                           json={"status": "COMPLIANT", "reason": ""}, headers=AUTH)
    assert response.status_code == 422
```

- [ ] **Step 2: Run and verify failure**

Run: `.\.venv\Scripts\python.exe -m pytest backend/tests/tender/test_api.py -v`  
Expected: FAIL with 404 routes.

- [ ] **Step 3: Implement endpoints and register router**

Create a router at `/api/tenders`, protected by `require_demo_password`, with:

```text
POST /analyses
POST /analyses/{analysis_id}/documents
POST /analyses/{analysis_id}/run
GET  /analyses/{analysis_id}
GET  /analyses/{analysis_id}/results
POST /results/{result_id}/review
GET  /analyses/{analysis_id}/reports/{format}
```

For uploads, require MIME type `application/pdf`, stream to a generated document ID under `tender_storage_dir`, calculate SHA-256 while writing, and never use the supplied filename as a filesystem path. Return `409` for a run already in progress, `422` for an invalid review, and `503` when optional semantic review is unavailable. Include the router in `backend/app/main.py`.

- [ ] **Step 4: Run API tests and backend suite**

Run: `.\.venv\Scripts\python.exe -m pytest backend/tests/tender/test_api.py -v`  
Expected: PASS.

Run: `.\.venv\Scripts\python.exe -m pytest backend/tests -q`  
Expected: all tests PASS.

- [ ] **Step 5: Commit**

```powershell
git add backend/app/tender/api.py backend/app/main.py backend/tests/tender/test_api.py
git commit -m "feat: expose tender review API"
```

## Task 10: Human Review Portal

**Files:**
- Create: `lib/tenders-api.ts`
- Create: `components/tenders/UploadPanel.tsx`
- Create: `components/tenders/RequirementTable.tsx`
- Create: `components/tenders/EvidencePanel.tsx`
- Create: `app/tenders/page.tsx`
- Modify: `app/globals.css`
- Create: `tests-frontend/tenders.test.tsx`

- [ ] **Step 1: Write the primary interaction test**

```tsx
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import TenderPage from "../app/tenders/page";

vi.mock("../lib/tenders-api", () => ({
  listResults: vi.fn().mockResolvedValue([{ requirement_id: "EPEC-4.1-D", status: "NON_COMPLIANT",
    description: "Ambient temperature", tender_evidence: { page: 11, text: "-10°C to +45°C" },
    product_evidence: [{ page: 5, text: "0°C to +40°C" }], confidence: 1 }]),
  reviewResult: vi.fn().mockResolvedValue({ ok: true }),
}));

describe("tender review", () => {
  it("shows side-by-side evidence before approval", async () => {
    render(<TenderPage />);
    fireEvent.click(await screen.findByText("Ambient temperature"));
    expect(screen.getByText("Tender · page 11")).toBeInTheDocument();
    expect(screen.getByText("Catalog · page 5")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Approve decision" })).toBeEnabled();
  });
});
```

- [ ] **Step 2: Run and verify failure**

Run: `npm test -- --run tests-frontend/tenders.test.tsx`  
Expected: FAIL because the tender page and components do not exist.

- [ ] **Step 3: Implement the typed client and review page**

Define TypeScript types matching the API contracts in `lib/tenders-api.ts`. Implement password-authenticated `createAnalysis`, `uploadDocument`, `runAnalysis`, `listResults`, `reviewResult`, and `reportUrl` functions.

The page must provide:

- separate tender and catalog upload controls;
- visible workflow stage and failure state;
- filters for all three statuses;
- a table showing mandatory flag, category, status, confidence, and review state;
- side-by-side tender and product citations;
- approve, override, and “needs clarification” actions;
- mandatory reason text for overrides;
- JSON and CSV export links only after review readiness.

Use semantic HTML and preserve keyboard focus when selecting rows. Add responsive CSS under `.tender-*` selectors without altering existing `.chat-*` behavior.

- [ ] **Step 4: Run frontend tests and build**

Run: `npm test -- --run tests-frontend/tenders.test.tsx`  
Expected: PASS.

Run: `npm run build`  
Expected: Next.js production build succeeds.

- [ ] **Step 5: Commit**

```powershell
git add lib/tenders-api.ts components/tenders app/tenders/page.tsx app/globals.css tests-frontend/tenders.test.tsx
git commit -m "feat: add tender compliance review portal"
```

## Task 11: End-to-End Evaluation and Operating Documentation

**Files:**
- Create: `backend/tests/tender/test_epec_end_to_end.py`
- Create: `docs/sarlacc-poc-runbook.md`
- Modify: `README.md`

- [ ] **Step 1: Add the blind evaluation test**

```python
def test_epec_golden_set_meets_mandatory_recall(epec_pipeline, golden_records):
    output = epec_pipeline.run_blind(golden_records)
    assert output.metrics.mandatory_recall >= 0.95
    assert output.metrics.citation_coverage == 1.0
    assert all(item.tender_evidence.text for item in output.assessments)
```

- [ ] **Step 2: Run the test and record the honest baseline**

Run: `.\.venv\Scripts\python.exe -m pytest backend/tests/tender/test_epec_end_to_end.py -v`  
Expected before tuning: the measured result is recorded; if recall is below 0.95, the PoC is explicitly `NO-GO` and the failing categories are listed. Do not weaken the assertion.

- [ ] **Step 3: Write the operating runbook**

Document exact commands for backend/frontend startup, required environment variables, document upload, golden-set evaluation, report export, data deletion, retrying a failed stage, disabling semantic review, and interpreting `GO` versus `NO-GO`. Include the fixed safety statement: “The assistant supplies evidence and warnings; the commercial engineer owns the final tender decision.”

Update `README.md` with a Sarlacc PoC section linking the design, plan, and runbook.

- [ ] **Step 4: Run complete verification**

Run: `.\.venv\Scripts\python.exe -m pytest backend/tests -q`  
Expected: all backend tests PASS, including the unchanged chat tests.

Run: `npm test`  
Expected: all frontend tests PASS.

Run: `npm run build`  
Expected: production build succeeds.

Run: `git diff --check`  
Expected: no whitespace errors.

- [ ] **Step 5: Commit**

```powershell
git add backend/tests/tender/test_epec_end_to_end.py docs/sarlacc-poc-runbook.md README.md
git commit -m "docs: add Sarlacc PoC validation runbook"
```

## Implementation Completion Criteria

The implementation is complete only when:

- every surfaced requirement and result has non-empty page-level evidence;
- deterministic contradictions cannot be overridden by semantic review;
- low-confidence, missing-evidence, and conflicting cases become `REVIEW_REQUIRED`;
- reviewer overrides require a reason and create an audit event;
- the workflow resumes safely after a failed stage;
- the backend suite, frontend suite, and production build pass;
- the blind EPEC evaluation reports measured precision, recall, time, tokens, and cost; and
- the PoC is labelled `GO` only when mandatory-requirement recall is at least 95%.
