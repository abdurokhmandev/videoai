"""Yordamchi funksiyalar"""

import re
from bot.utils.messages import NSFW_WORDS


def check_nsfw(text: str) -> bool:
    """Check if text contains NSFW content. Returns True if blocked."""
    lower = text.lower()
    for word in NSFW_WORDS:
        if word in lower:
            return True
    return False


def truncate_text(text: str, max_len: int = 50) -> str:
    """Truncate text with ellipsis"""
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def format_number(n: int) -> str:
    """Format number with comma separator"""
    return f"{n:,}"


def make_progress_bar(percent: int, length: int = 10) -> str:
    """Create text progress bar"""
    filled = int(length * percent / 100)
    bar = "█" * filled + "░" * (length - filled)
    return bar


def status_emoji(status: str) -> str:
    mapping = {
        "pending": "⏳",
        "processing": "⏳",
        "done": "✅",
        "failed": "❌",
    }
    return mapping.get(status, "❓")


def model_emoji(provider: str) -> str:
    if provider == "atlascloud":
        return "🏆 Premium"
    return "⚡ Tez"
