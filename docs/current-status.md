# Current status

## Final delivery milestone

The project is prepared for a public Streamlit demo and structured interview
walkthrough. The final milestone adds delivery configuration and operational
documentation without changing product behavior.

Implemented:

- `APP_MODE=demo` selects the existing fictional JSON fixtures without creating
  a Supabase client.
- `APP_MODE=live` requires a valid Supabase URL and anon key and never falls back
  to local fixtures.
- The live dashboard reads the latest persisted input snapshot, workflow runs,
  and deterministic alerts from Supabase.
- Metrics are recalculated by the existing deterministic metric service from
  the persisted source snapshot.
- Repository save/read methods cover metric snapshots, workflow runs, alerts,
  and generated summaries.
- Anon credentials are used for read-only access. Trusted writes require a
  separate service-role client.
- Decimal values use exact string serialization and datetimes use ISO-8601.
- All Supabase tests use fake clients and run offline.
- A portable n8n workflow loads fixed fictional Shopify, Meta Ads, Klaviyo, and
  Google Sheets-style data without source credentials or network reads.
- The workflow normalizes source records and aggregates only the eleven raw
  inputs accepted by `DTCInputData`.
- The success path upserts a fixed metric snapshot and successful workflow run.
- A controlled demo branch upserts a fixed failed workflow run without writing
  a metric snapshot or alert.
- Fixed UUIDs and timestamps keep repeated workflow demonstrations predictable.
- `app.py` is the root Streamlit Community Cloud entry point.
- `requirements.txt` installs the local `src/` package, whose four runtime
  dependencies remain authoritative in `pyproject.toml`.
- Public deployment defaults explicitly to `APP_MODE=demo` and needs no
  credentials.
- The repository includes a 3–5 minute demo script, workflow-failure SOP, and
  formula/alert-rule reference.

Current limitations:

- The local repository's explicit save methods are process-local so the
  committed demo fixtures remain immutable and deterministic.
- The Streamlit dashboard is a read-only live consumer. It does not automatically
  write on reruns.
- The n8n workflow is manually triggered and uses embedded fictional records;
  it has no live Shopify, Meta Ads, Klaviyo, or Google Sheets integrations.
- Supabase tables must contain fictional portfolio data only under the included
  public anon-read policy.
- Screenshots remain documented placeholders until a deployment URL is chosen.
- Deployment itself remains a manual owner action in Streamlit Community Cloud.

Operational references:

- `docs/demo-script.md`
- `docs/sop-workflow-failure.md`
- `docs/scoring-and-alert-rules.md`
- `docs/n8n-workflow.md`
- `docs/security-and-privacy.md`

Validation results are reported with the final delivery rather than hardcoded
in this status document.
