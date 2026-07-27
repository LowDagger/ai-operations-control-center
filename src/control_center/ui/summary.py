"""Founder-summary presentation using native Streamlit components."""

import streamlit as st

from control_center.models.summaries import (
    OverallStatus,
    SummaryGenerationResult,
    SummaryStatus,
)

STATUS_COLORS = {
    SummaryStatus.DEMO: "blue",
    SummaryStatus.LIVE: "green",
    SummaryStatus.FALLBACK: "orange",
}

OVERALL_STATUS_COLORS = {
    OverallStatus.HEALTHY: "green",
    OverallStatus.ATTENTION: "orange",
    OverallStatus.CRITICAL: "red",
}


def render_founder_summary(result: SummaryGenerationResult) -> None:
    """Render a compact narrative without chat or operational controls."""

    st.header("Founder summary")
    with st.container(horizontal=True):
        st.badge(
            f"Provider: {result.provider_used}",
            icon=":material/auto_awesome:",
            color="violet",
        )
        st.badge(
            result.status.value.upper(),
            icon=":material/check_circle:",
            color=STATUS_COLORS[result.status],
        )

    if result.status == SummaryStatus.FALLBACK:
        st.warning(
            f"{result.fallback_reason} Showing the deterministic demo summary.",
            icon=":material/warning:",
        )

    with st.container(border=True):
        st.badge(
            result.summary.overall_status.value.upper(),
            color=OVERALL_STATUS_COLORS[result.summary.overall_status],
        )
        st.write(result.summary.executive_summary)

        st.subheader("Key findings")
        for finding in result.summary.key_findings:
            st.markdown(f"- {finding}")

        st.subheader("Recommended actions")
        for action in result.summary.recommended_actions:
            st.markdown(f"- {action}")

        st.subheader("Risks")
        for risk in result.summary.risks:
            st.markdown(f"- {risk}")

    st.caption(
        "Narrative assistance only. Calculations, alerts, retries, approvals, "
        "and operational decisions remain deterministic and human-controlled."
    )

