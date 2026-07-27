"""Provider contract for narrative founder summaries."""

from typing import Protocol

from control_center.models.summaries import FounderSummary, OperationsSummary


class SummaryProvider(Protocol):
    """A provider may summarize deterministic data but cannot modify it."""

    provider_name: str

    def generate_summary(self, operations: OperationsSummary) -> FounderSummary:
        """Return a validated narrative summary."""

