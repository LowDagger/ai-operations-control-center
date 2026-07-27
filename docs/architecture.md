# Architecture

## Runtime flow

```text
Fictional source-shaped records -> n8n normalization and raw aggregation
                                -> Supabase raw metric/workflow rows

Environment -> AppSettings -> Repository factory
                              |-> demo: LocalJsonRepository
                              `-> live: SupabaseRepository

Repository data -> Pydantic validation -> deterministic metric service
                                      |-> persisted deterministic alerts
                                      `-> safe summary service
```

The Streamlit entry point depends on repository interfaces and contains no
Supabase SDK calls. Provider-specific operations stay in the repository layer.

## n8n ingestion boundary

`n8n/workflows/dtc-operations-ingestion.json` is a trusted server-side writer.
It loads fixed fictional source records, normalizes their differing shapes, and
aggregates only the eleven raw inputs accepted by `DTCInputData`.

The success path uses Supabase REST upserts for:

- one raw `metrics_snapshots` row with calculated columns omitted; and
- one `workflow_runs` observation.

The controlled failure path writes only a different `workflow_runs`
observation. Both paths use fixed UUIDs and timestamps so repeated executions
are predictable. n8n never writes the `alerts` table.

The readable source fixtures under `n8n/sample-data/` match the records embedded
in the portable export. Embedding avoids filesystem and third-party credential
requirements after import.

## Repository selection

- Demo mode constructs `LocalJsonRepository` and reads the committed fictional
  fixtures.
- Live mode requires `SUPABASE_URL` and `SUPABASE_ANON_KEY`. Missing or invalid
  configuration stops the dashboard with a safe error.
- Supabase failures never trigger a local-fixture fallback.

`SupabaseRepository` maintains two clients:

- the anon-key client performs ordered, limited reads;
- the optional service-role client performs trusted backend inserts.

Without the service-role client, save methods fail closed with a configuration
error. The Streamlit dashboard does not invoke save methods.

## Data mapping

`repositories/mappers.py` is the single conversion boundary between the domain
models and flat Supabase row dictionaries:

- `Decimal` values serialize as exact strings accepted by PostgreSQL numeric
  input rather than binary floats;
- timezone-aware datetimes serialize with ISO-8601 offsets;
- UUIDs and enums serialize to their canonical strings;
- database rows are reconstructed through Pydantic before use.

Metric snapshots embed `DTCInputData` and `CalculatedMetrics`.
Generated-summary records embed `SummaryGenerationResult`. Workflows and alerts
use their existing Pydantic models directly.

## Deterministic and AI boundaries

The live dashboard recalculates metrics through the existing metric service.
Persisted alerts are records of alerts previously produced by deterministic
rules. Gemini can only return `FounderSummary`; it cannot calculate metrics,
modify alerts, decide retries, or approve actions.

n8n can normalize and aggregate raw source inputs, but it cannot calculate
derived business metrics, evaluate alert rules, assign alert severity, decide
retries, approve actions, or invoke Gemini.

## Deferred work

Live commerce and marketing connectors, scheduled production automation, final
deployment, and presentation polish remain deferred.
