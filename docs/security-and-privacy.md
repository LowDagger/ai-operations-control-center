# Security and privacy

## Data classification

This portfolio repository and its migration are intended for fictional
operational data only. Do not load real customer, payment, advertising-account,
or personally identifiable data under the included public anon-read policy.

## Supabase keys

`SUPABASE_ANON_KEY`

- Used by the dashboard's read client.
- Limited by PostgreSQL grants and Row Level Security.
- The migration grants anon SELECT only.

`SUPABASE_SERVICE_ROLE_KEY`

- Used only by trusted backend repository save methods.
- Can bypass Row Level Security and must never appear in browser code, frontend
  bundles, logs, screenshots, commits, or client-visible errors.
- Is optional for the read-only live dashboard.

Both keys are represented by Pydantic `SecretStr` values and excluded from model
representations. Repository errors log only operation and exception type.

## n8n trusted writer

The Milestone 5 n8n workflow is a trusted server-side ingestion process. Its
HTTP Request nodes read `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` from the
n8n server environment. The exported workflow contains only expressions that
reference those variable names; it contains no credential values.

The service-role key can bypass RLS. Limit it to the n8n server process, protect
access to workflow executions, and avoid saving request headers in screenshots
or logs. Never copy the key into a Code node, workflow note, browser field,
committed file, or client-visible application state.

No Shopify, Meta Ads, Klaviyo, or Google credentials are used. The sample
records are fixed fictional aggregates without customer names, email addresses,
payment details, advertising-account identifiers, or other real data.

## Row Level Security

The migration enables RLS on every table. It creates explicit anon SELECT
policies for the fictional portfolio dataset and creates no anon INSERT, UPDATE,
or DELETE policies. Service-role access is reserved for trusted backend writes.

Before using non-fictional or tenant-specific data, replace the public read
policies with authenticated, tenant-scoped policies and complete a dedicated
privacy review.

## Failure behavior

- Demo mode never creates a Supabase client.
- Live mode fails safely if URL or anon credentials are missing.
- Supabase connection or query failures produce generic safe errors.
- Live mode never writes to or reads from local demo fixtures as a fallback.
- Invalid database rows are rejected by Pydantic before rendering.
- Repeated n8n demo runs upsert fixed fictional UUIDs instead of creating
  unbounded duplicate records.
- The controlled n8n failure branch writes only workflow-run metadata and never
  writes alerts.

## AI boundary

Gemini receives only already-validated operational data and returns a strict
`FounderSummary`. It cannot create or modify alerts, calculate metrics, choose
retries, grant approvals, or make operational decisions. Provider failure uses
the deterministic narrative fallback and does not change persisted operations.

n8n has the same decision boundary: it may prepare raw inputs and record
execution observations, but Python alone calculates derived metrics and
evaluates deterministic alert rules.
