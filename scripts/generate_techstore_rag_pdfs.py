from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "docs" / "knowledge_base" / "pdf_sources"
PDF_DIR = ROOT / "docs" / "knowledge_base" / "pdfs"


@dataclass(frozen=True)
class DocumentSpec:
    filename: str
    title: str
    subtitle: str
    chapters: list[str]
    target_pages: int
    audience: str


DOCUMENTS = [
    DocumentSpec(
        filename="01_techstore_customer_policies",
        title="TechStore Plus Customer Policies",
        subtitle="Returns, refunds, warranty support, damaged delivery, and customer remedies",
        target_pages=35,
        audience="customer-facing support and policy teams",
        chapters=[
            "Return Eligibility and Product Condition",
            "Refund Timelines and Payment Exceptions",
            "Warranty Coverage and Service Contracts",
            "Damaged Delivery and Missing Package Claims",
            "Policy Exceptions for Business-Critical Orders",
            "Customer Communication Templates",
        ],
    ),
    DocumentSpec(
        filename="02_techstore_product_catalog_guide",
        title="TechStore Plus Product Catalog Guide",
        subtitle="Buying guidance for laptops, smartphones, tablets, routers, monitors, and accessories",
        target_pages=35,
        audience="sales support and product inquiry agents",
        chapters=[
            "Laptop Families and Buyer Profiles",
            "Smartphone Selection and Compatibility",
            "Home Office Bundles and Peripherals",
            "Gaming Systems and Display Recommendations",
            "Router, Mesh, and Smart Home Recommendations",
            "Accessory Matching and Upgrade Paths",
        ],
    ),
    DocumentSpec(
        filename="03_techstore_troubleshooting_manual",
        title="TechStore Plus Troubleshooting Manual",
        subtitle="Diagnostic flows for common customer support scenarios",
        target_pages=40,
        audience="technical support agents",
        chapters=[
            "Laptop Power, Battery, and Thermal Issues",
            "Smartphone Charging, Display, and Sync Issues",
            "Router Connectivity and Wi-Fi Stability",
            "Monitor, Docking, and Peripheral Problems",
            "Audio, Camera, and Conferencing Troubleshooting",
            "When to Escalate to Repair or Replacement",
        ],
    ),
    DocumentSpec(
        filename="04_techstore_shipping_fulfillment",
        title="TechStore Plus Shipping and Fulfillment Guide",
        subtitle="Order lifecycle, carrier handoff, tracking, delays, and warehouse exceptions",
        target_pages=30,
        audience="fulfillment, customer support, and escalation teams",
        chapters=[
            "Order Lifecycle and Warehouse States",
            "Carrier Services and Delivery Windows",
            "Tracking Delays and Address Corrections",
            "Missing, Damaged, and Split Shipments",
            "High-Value Orders and Signature Requirements",
            "Holiday Capacity and Customer Updates",
        ],
    ),
    DocumentSpec(
        filename="05_techstore_agent_handbook",
        title="TechStore Plus Agent Handbook",
        subtitle="Conversation standards, routing, urgency, follow-up, and support quality",
        target_pages=35,
        audience="customer service agents and team leads",
        chapters=[
            "Conversation Flow and Customer Tone",
            "Intent Classification and Routing",
            "Urgency, Priority Support, and Escalation",
            "Follow-Up Tasks and Ownership",
            "Grounded Answers and Knowledge Base Use",
            "Quality Review, Coaching, and Examples",
        ],
    ),
    DocumentSpec(
        filename="06_techstore_account_security",
        title="TechStore Plus Account Security Guide",
        subtitle="Secure account access, fraud signals, privacy, phishing, and recovery",
        target_pages=25,
        audience="account support, security, and customer education teams",
        chapters=[
            "Account Access and Identity Verification",
            "Password, MFA, and Recovery Guidance",
            "Phishing, Social Engineering, and Suspicious Messages",
            "Payment Safety and Order Fraud Signals",
            "Privacy-Conscious Support Practices",
            "Customer Education Playbooks",
        ],
    ),
]


POLICY_TOPICS = [
    "eligibility",
    "documentation",
    "customer expectations",
    "agent next action",
    "escalation trigger",
    "exception handling",
    "source metadata",
    "quality audit note",
]

PRODUCTS = [
    "ultrabook laptop",
    "engineering workstation laptop",
    "gaming notebook",
    "smartphone",
    "tablet",
    "mesh router",
    "Wi-Fi 6 router",
    "4K monitor",
    "USB-C docking station",
    "noise-canceling headset",
    "mechanical keyboard",
    "smart home hub",
]

CUSTOMER_PROFILES = [
    "remote consultant",
    "engineering student",
    "small business owner",
    "competitive gamer",
    "family account manager",
    "hybrid office employee",
    "content creator",
    "field technician",
]

ISSUES = [
    "late delivery",
    "battery drains quickly",
    "router disconnects during video calls",
    "screen flickers after sleep mode",
    "customer cannot locate package",
    "order shows delivered but is missing",
    "device will not power on",
    "payment authorization failed",
    "warranty claim lacks serial number",
    "customer needs a replacement before travel",
]


def main() -> None:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    PDF_DIR.mkdir(parents=True, exist_ok=True)

    for spec in DOCUMENTS:
        sections = build_document_sections(spec)
        markdown = render_markdown(spec, sections)
        md_path = SOURCE_DIR / f"{spec.filename}.md"
        pdf_path = PDF_DIR / f"{spec.filename}.pdf"
        md_path.write_text(markdown, encoding="utf-8")
        build_pdf(spec, sections, pdf_path)

    print(f"Generated {len(DOCUMENTS)} Markdown sources in {SOURCE_DIR}")
    print(f"Generated {len(DOCUMENTS)} PDFs in {PDF_DIR}")


def build_document_sections(spec: DocumentSpec) -> list[tuple[str, list[str], list[list[str]]]]:
    sections: list[tuple[str, list[str], list[list[str]]]] = []
    pages_per_chapter = max(3, spec.target_pages // len(spec.chapters))
    for chapter_index, chapter in enumerate(spec.chapters, start=1):
        for section_index in range(1, pages_per_chapter + 1):
            section_title = f"{chapter_index}.{section_index} {chapter}: {section_theme(chapter, section_index)}"
            paragraphs = [
                build_paragraph(spec, chapter, section_index, variant)
                for variant in range(1, 5)
            ]
            table = build_table(spec, chapter, section_index)
            sections.append((section_title, paragraphs, table))

    while len(sections) < spec.target_pages:
        section_index = len(sections) + 1
        chapter = spec.chapters[(section_index - 1) % len(spec.chapters)]
        sections.append(
            (
                f"Appendix {section_index}: {chapter} Scenario Library",
                [
                    build_case_study(spec, chapter, section_index),
                    build_decision_note(spec, chapter, section_index),
                    build_agent_guidance(spec, chapter, section_index),
                    build_quality_note(spec, chapter, section_index),
                ],
                build_table(spec, chapter, section_index),
            )
        )
    return sections[: spec.target_pages]


def section_theme(chapter: str, index: int) -> str:
    themes = [
        "Baseline Standard",
        "Customer Evidence",
        "Agent Workflow",
        "Edge Case",
        "Escalation Rule",
        "Quality Check",
        "Example Dialogue",
        "Operational Metric",
    ]
    return themes[(len(chapter) + index) % len(themes)]


def build_paragraph(spec: DocumentSpec, chapter: str, section_index: int, variant: int) -> str:
    product = PRODUCTS[(section_index + variant + len(chapter)) % len(PRODUCTS)]
    profile = CUSTOMER_PROFILES[(section_index * variant + len(spec.title)) % len(CUSTOMER_PROFILES)]
    issue = ISSUES[(section_index + variant * 2) % len(ISSUES)]
    topic = POLICY_TOPICS[(section_index + variant) % len(POLICY_TOPICS)]
    return (
        f"For {spec.audience}, this section defines how TechStore Plus handles {topic} "
        f"when a {profile} contacts support about a {product} and reports {issue}. "
        f"The agent should collect the minimum useful facts, confirm the customer's goal, "
        f"and keep the answer grounded in the relevant policy or product record. "
        f"If the case includes urgency, safety risk, a high-value shipment, repeated failure, "
        f"or an unresolved warranty decision, the agent should identify the correct escalation "
        f"path before promising a remedy. Scenario marker {section_index}-{variant} is unique "
        f"for retrieval testing and helps confirm that ChromaDB can recover this passage."
    )


def build_case_study(spec: DocumentSpec, chapter: str, index: int) -> str:
    product = PRODUCTS[index % len(PRODUCTS)]
    issue = ISSUES[(index + 3) % len(ISSUES)]
    profile = CUSTOMER_PROFILES[(index + 5) % len(CUSTOMER_PROFILES)]
    return (
        f"Case study: A {profile} purchased a {product} and contacted TechStore Plus because "
        f"{issue}. The agent first verified the order context, then separated what was known "
        f"from what still needed evidence. The response avoided broad promises and explained "
        f"the next checkpoint in plain language. This pattern supports retrieval because the "
        f"case contains product, issue, evidence, and next-action signals in one passage."
    )


def build_decision_note(spec: DocumentSpec, chapter: str, index: int) -> str:
    return (
        f"Decision note for {chapter}: agents should choose the narrowest reliable answer. "
        f"When a document does not contain a final remedy, the correct answer is to state the "
        f"known policy boundary and request the missing evidence. This is especially important "
        f"for warranty exclusions, delivery disputes, account recovery, and payment-risk cases."
    )


def build_agent_guidance(spec: DocumentSpec, chapter: str, index: int) -> str:
    return (
        f"Agent guidance: acknowledge the customer concern, name the relevant TechStore process, "
        f"ask for the order number or serial number when needed, and summarize the next action. "
        f"Do not invent coverage, shipping dates, repair outcomes, discounts, or security status. "
        f"Use retrieved context as the source of truth and cite the source title when available."
    )


def build_quality_note(spec: DocumentSpec, chapter: str, index: int) -> str:
    return (
        f"Quality note: a strong answer for this topic is concise, specific, and verifiable. "
        f"It should contain the policy window, customer evidence, product category, ownership "
        f"team, and escalation threshold when those details are present. A weak answer repeats "
        f"generic reassurance without connecting the customer request to a documented rule."
    )


def build_table(spec: DocumentSpec, chapter: str, section_index: int) -> list[list[str]]:
    rows = [["Signal", "Support action", "RAG retrieval clue"]]
    for offset in range(1, 5):
        product = PRODUCTS[(section_index + offset) % len(PRODUCTS)]
        issue = ISSUES[(section_index + offset) % len(ISSUES)]
        rows.append(
            [
                f"{product}: {issue}",
                f"Verify order, collect evidence, route via {chapter.split()[0].lower()} workflow",
                f"{spec.filename}:{section_index}:{offset}",
            ]
        )
    return rows


def render_markdown(
    spec: DocumentSpec,
    sections: list[tuple[str, list[str], list[list[str]]]],
) -> str:
    lines = [
        f"# {spec.title}",
        "",
        spec.subtitle,
        "",
        f"Audience: {spec.audience}.",
        "",
        "This is original synthetic documentation generated for the TechStore Plus RAG project. "
        "It is inspired by common e-commerce support, warranty, fulfillment, and security concepts, "
        "but it is not copied from any external source and is not legal advice.",
        "",
    ]
    for title, paragraphs, table in sections:
        lines.extend([f"## {title}", ""])
        for paragraph in paragraphs:
            lines.extend([paragraph, ""])
        lines.extend(render_markdown_table(table))
        lines.append("")
    return "\n".join(lines)


def render_markdown_table(rows: list[list[str]]) -> list[str]:
    header = "| " + " | ".join(rows[0]) + " |"
    separator = "| " + " | ".join("---" for _ in rows[0]) + " |"
    body = ["| " + " | ".join(row) + " |" for row in rows[1:]]
    return [header, separator, *body]


def build_pdf(
    spec: DocumentSpec,
    sections: list[tuple[str, list[str], list[list[str]]]],
    path: Path,
) -> None:
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TechStoreTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=28,
        alignment=TA_CENTER,
        spaceAfter=14,
    )
    subtitle_style = ParagraphStyle(
        "TechStoreSubtitle",
        parent=styles["BodyText"],
        fontSize=11,
        leading=15,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#374151"),
        spaceAfter=20,
    )
    heading_style = ParagraphStyle(
        "TechStoreHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#0F3D5E"),
        spaceBefore=8,
        spaceAfter=8,
    )
    body_style = ParagraphStyle(
        "TechStoreBody",
        parent=styles["BodyText"],
        fontSize=9.6,
        leading=13.3,
        alignment=TA_LEFT,
        spaceAfter=7,
    )
    small_style = ParagraphStyle(
        "TechStoreSmall",
        parent=styles["BodyText"],
        fontSize=8,
        leading=10,
    )

    story = [
        Paragraph(escape(spec.title), title_style),
        Paragraph(escape(spec.subtitle), subtitle_style),
        Paragraph(
            escape(
                "Original synthetic documentation for the TechStore Plus RAG project. "
                "Use these pages to test PDF ingestion, chunking, metadata, retrieval, "
                "and grounded customer-support answers."
            ),
            body_style,
        ),
        PageBreak(),
    ]

    for title, paragraphs, table_rows in sections:
        story.append(Paragraph(escape(title), heading_style))
        for paragraph in paragraphs:
            story.append(Paragraph(escape(paragraph), body_style))
        story.append(build_reportlab_table(table_rows, small_style))
        story.append(PageBreak())

    doc = SimpleDocTemplate(
        str(path),
        pagesize=letter,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
        title=spec.title,
        author="TechStore Plus RAG Corpus Generator",
    )
    doc.build(story, onFirstPage=footer(spec), onLaterPages=footer(spec))


def build_reportlab_table(rows: list[list[str]], style: ParagraphStyle) -> Table:
    escaped_rows = [[Paragraph(escape(cell), style) for cell in row] for row in rows]
    table = Table(escaped_rows, colWidths=[1.55 * inch, 3.05 * inch, 1.65 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E5EEF5")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0F3D5E")),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CBD5E1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def footer(spec: DocumentSpec):
    def draw(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#64748B"))
        canvas.drawString(0.65 * inch, 0.35 * inch, spec.title)
        canvas.drawRightString(7.85 * inch, 0.35 * inch, f"Page {doc.page}")
        canvas.restoreState()

    return draw


def escape(value: str) -> str:
    return (
        re.sub(r"&", "&amp;", value)
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


if __name__ == "__main__":
    main()
