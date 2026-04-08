from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


class ReceiptStore:
    """Append-only local receipt journal for transparent trading decisions."""

    @staticmethod
    def path() -> Path:
        raw = os.getenv("RECEIPT_LOG_PATH", "backend/data/decision_receipts.jsonl")
        return Path(raw)

    @classmethod
    def save(cls, payload: dict[str, Any]) -> str:
        path = cls.path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
        return str(path)
