"""Non-required placeholder for a possible future Claude provider."""

from control_center.models.summaries import FounderSummary, OperationsSummary


class ClaudeSummaryProviderStub:
    """Document the extension point without adding an Anthropic dependency."""

    provider_name = "Claude (not configured)"

    def generate_summary(self, operations: OperationsSummary) -> FounderSummary:
        del operations
        raise NotImplementedError("Claude is not required for the MVP.")

