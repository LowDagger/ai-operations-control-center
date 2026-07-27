"""Google Gemini structured-output summary provider."""

import json
from typing import Any

from control_center.models.summaries import FounderSummary, OperationsSummary

DEFAULT_TIMEOUT_SECONDS = 10.0


class GeminiSummaryProvider:
    """Generate narrative summaries without changing deterministic data."""

    provider_name = "Gemini"

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        client: Any | None = None,
    ) -> None:
        if not api_key:
            raise ValueError("A Gemini API key is required for the live provider.")
        if not model:
            raise ValueError("A Gemini model is required for the live provider.")
        if timeout_seconds <= 0:
            raise ValueError("The Gemini timeout must be positive.")

        self._api_key = api_key
        self._model = model
        self._timeout_seconds = timeout_seconds
        self._client = client

    def generate_summary(self, operations: OperationsSummary) -> FounderSummary:
        """Request structured output and validate the returned JSON again."""

        response = self._get_client().models.generate_content(
            model=self._model,
            contents=self._build_prompt(operations),
            config={
                "response_mime_type": "application/json",
                "response_schema": FounderSummary,
                "temperature": 0.1,
            },
        )
        response_text = getattr(response, "text", None)
        if not response_text:
            raise ValueError("Gemini returned no structured summary.")
        return FounderSummary.model_validate_json(response_text)

    def _get_client(self) -> Any:
        if self._client is not None:
            return self._client

        from google import genai
        from google.genai import types

        self._client = genai.Client(
            api_key=self._api_key,
            http_options=types.HttpOptions(
                timeout=int(self._timeout_seconds * 1000)
            ),
        )
        return self._client

    @staticmethod
    def _build_prompt(operations: OperationsSummary) -> str:
        snapshot = json.dumps(
            operations.model_dump(mode="json"),
            sort_keys=True,
        )
        return (
            "Create a concise operational founder summary from the validated "
            "fictional snapshot below. Treat every supplied metric, workflow "
            "status, and alert as authoritative. Do not recalculate metrics, "
            "create or modify alerts, decide retries, make approvals, or invent "
            "facts. Recommended actions are advisory and require human review. "
            "Return only the requested structured output.\n\n"
            f"Validated snapshot:\n{snapshot}"
        )

