# Workflow failure SOP

## Purpose and ownership

This SOP describes the human-operated response to a detected workflow failure.
It does not authorize automatic retries, escalation, approvals, or operational
changes. Deterministic application code reports facts and severity; the named
human owner remains accountable for every action.

## 1. Detection

1. Confirm that the workflow table shows `FAILED`.
2. Open the corresponding deterministic workflow-failure alert.
3. Record the fixed snapshot time, workflow name, failure reason, retry status,
   cost anomaly, owner, and severity.
4. Check whether a missing-data or cost-spike alert is also active.
5. Do not use a Gemini summary as the source of record.

## 2. Severity check

Use the stored workflow severity and deterministic alerts exactly as displayed:

- `CRITICAL`: begin review immediately and notify the owner.
- `WARNING`: review during the current operating window.
- `INFO`: record and review through the normal queue.

If a cost anomaly is greater than 50%, the deterministic cost-spike rule is
critical. If it is greater than 25% but not greater than 50%, it is warning.
Do not manually downgrade a deterministic alert in the dashboard.

## 3. Owner assignment

1. Use the `owner` field on the workflow run as the primary assignee.
2. If that person or team is unavailable, a human operations lead assigns a
   substitute and records the change.
3. Gemini, n8n, and the Streamlit UI cannot assign ownership.

## 4. Retry decision

The assigned human owner decides whether to retry after answering:

- Is the failure reason understood?
- Are required inputs present and validated?
- Is the downstream destination available?
- Could a retry duplicate writes or customer-facing actions?
- Is the workflow designed to be idempotent?
- Does the retry need an approval from operations, finance, or security?

Record one decision: `do not retry`, `retry once`, or `escalate before retry`.
The system may display the stored retry status, but it never makes this choice.

For the fictional n8n demo, fixed UUID upserts make its two documented branches
predictable. This does not establish that an unrelated production workflow is
safe to retry.

## 5. Escalation

Escalation is executed by a human:

- Escalate every `CRITICAL` workflow failure to the named owner and operations
  lead immediately.
- Escalate a `WARNING` that remains unresolved at the end of the current
  operating window.
- Escalate any suspected credential exposure, unauthorized write, real customer
  data exposure, or repeated non-idempotent action to security before retrying.
- Escalate financial-impact uncertainty to finance operations.

## 6. Incident notes

Record:

```text
Incident ID:
Detected at:
Snapshot timestamp:
Workflow:
Deterministic severity:
Named owner:
Failure reason:
Related alerts:
Data affected:
Customer impact:
Retry decision and human approver:
Actions taken:
Recovery evidence:
Closed at:
Follow-up owner:
```

Never paste API keys, access tokens, service-role credentials, or real customer
records into incident notes.

## 7. Recovery validation

Before closing the incident:

1. Confirm the latest workflow observation is `SUCCEEDED`.
2. Validate source completeness and schema acceptance.
3. Confirm expected row counts or fixed identifiers at the destination.
4. Check that no duplicate writes or unintended actions occurred.
5. Re-run deterministic metric and alert evaluation.
6. Confirm the workflow-failure condition is no longer present in the new
   snapshot; do not delete historical evidence.
7. Record the evidence and the human who validated recovery.

## 8. Post-incident review

Within the next review cycle:

- document root cause and contributing conditions;
- assess whether validation or idempotency controls need improvement;
- identify any threshold or ownership change for separate human approval;
- add a deterministic regression test when appropriate; and
- record a named owner and due date for each follow-up.

Gemini may summarize already-recorded incident facts, but it cannot determine
root cause, approve corrective action, change thresholds, or close the incident.
