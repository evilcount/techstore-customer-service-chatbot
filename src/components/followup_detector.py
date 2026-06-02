from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(frozen=True)
class FollowUpTask:
    task: str
    customer_email: str
    priority: str = "medium"
    status: str = "open"
    category: str = "general_information"
    due_date: date | None = None
    description: str = ""
    source: str = "memory_agent"


FOLLOWUP_PHRASES = (
    "crie um follow-up",
    "criar um follow-up",
    "follow-up",
    "follow up",
    "me lembre",
    "lembre-me",
    "acompanhe",
    "verifique amanhã",
    "check tomorrow",
    "remind me",
)

HIGH_PRIORITY_WORDS = ("urgente", "emergency", "asap", "imediato")

CATEGORY_KEYWORDS = (
    (
        "billing",
        (
            "refund",
            "invoice",
            "payment",
            "billing",
            "reembolso",
            "pagamento",
            "cobrança",
            "cobranca",
        ),
    ),
    ("returns", ("return", "returns", "devolução", "devolucao", "troca")),
    (
        "technical_support",
        ("technical", "support", "mac mini", "não liga", "nao liga", "power", "laptop", "router"),
    ),
    (
        "product_inquiry",
        ("product", "produto", "stock", "estoque", "recommendation", "recomendação", "recomendacao"),
    ),
)


def detect_followup_task(
    customer_email: str,
    user_text: str,
    assistant_reply: str,
) -> FollowUpTask | None:
    normalized = user_text.lower()
    if not any(phrase in normalized for phrase in FOLLOWUP_PHRASES):
        return None

    return FollowUpTask(
        task=_build_title(user_text),
        customer_email=customer_email,
        priority=_infer_priority(normalized),
        category=_infer_category(normalized),
        due_date=_infer_due_date(normalized),
        description=_build_description(user_text, assistant_reply),
    )


def _build_title(user_text: str) -> str:
    title = user_text.strip().rstrip(".?!")
    replacements = (
        "Pode criar um follow-up para ",
        "pode criar um follow-up para ",
        "Crie um follow-up para ",
        "crie um follow-up para ",
        "Crie um follow-up ",
        "crie um follow-up ",
        "Remind me to ",
        "remind me to ",
    )
    for prefix in replacements:
        if title.startswith(prefix):
            title = title[len(prefix):]
            break
    title = title[:1].upper() + title[1:]
    return title[:80]


def _infer_priority(normalized_text: str) -> str:
    if any(word in normalized_text for word in HIGH_PRIORITY_WORDS):
        return "high"
    return "medium"


def _infer_category(normalized_text: str) -> str:
    for category, keywords in CATEGORY_KEYWORDS:
        if any(keyword in normalized_text for keyword in keywords):
            return category
    return "general_information"


def _infer_due_date(normalized_text: str) -> date | None:
    if "amanhã" in normalized_text or "amanha" in normalized_text or "tomorrow" in normalized_text:
        return date.today() + timedelta(days=1)
    return None


def _build_description(user_text: str, assistant_reply: str) -> str:
    reply_excerpt = assistant_reply.strip()[:300]
    return f"Customer request: {user_text.strip()}\n\nAssistant reply: {reply_excerpt}"
