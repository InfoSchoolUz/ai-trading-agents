from __future__ import annotations

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


class LLMService:
    """
    Optional Gemini wrapper for short AI explanations.

    Design goals:
    - Never crash the backend if AI is unavailable
    - Return safe structured responses
    - Work only when explicitly enabled
    """

    def __init__(self) -> None:
        self.api_key = os.getenv("GOOGLE_API_KEY", "").strip()
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
        self.enabled = os.getenv("ENABLE_LLM_EXPLANATIONS", "false").strip().lower() == "true"

    def is_available(self) -> bool:
        """
        Basic availability check.
        Real import/runtime issues are handled inside explain().
        """
        return self.enabled and bool(self.api_key)

    def explain(self, prompt: str) -> dict[str, Any]:
        """
        Generate a plain-text explanation using Gemini.

        Returns:
            {
                "enabled": bool,
                "success": bool,
                "model": str,        # when success
                "text": str,         # when success
                "message": str       # when failed
            }
        """
        if not self.enabled:
            return {
                "enabled": False,
                "success": False,
                "message": "LLM explanations are disabled.",
            }

        if not self.api_key:
            return {
                "enabled": True,
                "success": False,
                "message": "GOOGLE_API_KEY is missing.",
            }

        try:
            import google.generativeai as genai
        except Exception as exc:
            logger.warning("google-generativeai import failed: %s", exc)
            return {
                "enabled": True,
                "success": False,
                "message": "google-generativeai is not installed.",
            }

        try:
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(prompt)
            text = (getattr(response, "text", "") or "").strip()

            if not text:
                return {
                    "enabled": True,
                    "success": False,
                    "message": "LLM returned empty text.",
                }

            return {
                "enabled": True,
                "success": True,
                "model": self.model_name,
                "text": text,
            }

        except Exception as exc:
            logger.exception("LLM explanation failed")
            return {
                "enabled": True,
                "success": False,
                "message": f"LLM request failed: {exc}",
            }

    def explain_json(self, prompt: str, fallback: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Generate JSON output from the model.
        If parsing fails, returns fallback.
        """
        fallback = fallback or {}
        result = self.explain(prompt)

        if not result.get("success"):
            return fallback

        text = str(result.get("text", "")).strip()
        if not text:
            return fallback

        try:
            return json.loads(text)
        except Exception:
            logger.warning("LLM output was not valid JSON")
            return fallback