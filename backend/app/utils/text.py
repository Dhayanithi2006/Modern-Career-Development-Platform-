import json
import re
from typing import Any


def normalize_skill(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).lower()


def extract_json_object(text: str) -> dict[str, Any] | None:
    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        return None
    try:
        parsed = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def simple_token_set(text: str) -> set[str]:
    return {token.lower() for token in re.findall(r"[a-zA-Z][a-zA-Z+#.\-]{1,}", text)}
