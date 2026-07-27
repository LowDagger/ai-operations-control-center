-- AI Operations Control Center Milestone 4
-- This schema is for fictional portfolio data only. Do not load real customer data.

create extension if not exists pgcrypto;

-- Stores DTC source inputs alongside their deterministic calculated metrics.
create table public.metrics_snapshots (
    id uuid primary key default gen_random_uuid(),
    created_at timestamptz not null default now(),
    revenue numeric(20, 2),
    ad_spend numeric(20, 2),
    new_customers bigint,
    orders bigint,
    sessions bigint,
    refunds bigint,
    refunded_revenue numeric(20, 2),
    impressions bigint,
    clicks bigint,
    creative_frequency numeric(20, 6),
    previous_period_ad_spend numeric(20, 2),
    roas numeric(20, 8),
    cac numeric(20, 8),
    aov numeric(20, 8),
    cvr numeric(20, 8),
    order_volume bigint,
    refund_rate numeric(20, 8),
    constraint metrics_revenue_nonnegative check (revenue >= 0),
    constraint metrics_ad_spend_nonnegative check (ad_spend >= 0),
    constraint metrics_new_customers_nonnegative check (new_customers >= 0),
    constraint metrics_orders_nonnegative check (orders >= 0),
    constraint metrics_sessions_nonnegative check (sessions >= 0),
    constraint metrics_refunds_nonnegative check (refunds >= 0),
    constraint metrics_refunded_revenue_nonnegative
        check (refunded_revenue >= 0),
    constraint metrics_impressions_nonnegative check (impressions >= 0),
    constraint metrics_clicks_nonnegative check (clicks >= 0),
    constraint metrics_frequency_nonnegative check (creative_frequency >= 0),
    constraint metrics_previous_spend_nonnegative
        check (previous_period_ad_spend >= 0),
    constraint metrics_roas_nonnegative check (roas >= 0),
    constraint metrics_cac_nonnegative check (cac >= 0),
    constraint metrics_aov_nonnegative check (aov >= 0),
    constraint metrics_cvr_nonnegative check (cvr >= 0),
    constraint metrics_order_volume_nonnegative check (order_volume >= 0),
    constraint metrics_refund_rate_valid
        check (refund_rate >= 0 and refund_rate <= 1)
);

comment on table public.metrics_snapshots is
    'Fictional DTC input snapshots and deterministic calculated metrics.';

-- Stores observed workflow execution state; retry decisions remain external.
create table public.workflow_runs (
    id uuid primary key default gen_random_uuid(),
    created_at timestamptz not null default now(),
    workflow_name text not null,
    status text not null,
    last_run timestamptz not null,
    failure_reason text,
    retry_status text not null,
    cost_anomaly numeric(20, 8),
    owner text not null,
    severity text not null,
    constraint workflow_name_not_blank
        check (length(btrim(workflow_name)) > 0),
    constraint workflow_owner_not_blank check (length(btrim(owner)) > 0),
    constraint workflow_status_valid
        check (status in ('succeeded', 'failed', 'running')),
    constraint workflow_retry_status_valid
        check (retry_status in ('not_needed', 'pending', 'exhausted', 'succeeded')),
    constraint workflow_severity_valid
        check (severity in ('info', 'warning', 'critical')),
    constraint workflow_cost_anomaly_nonnegative check (cost_anomaly >= 0)
);

comment on table public.workflow_runs is
    'Fictional workflow observations; this table does not decide retries.';

-- Stores alerts previously produced by deterministic application rules.
create table public.alerts (
    id uuid primary key default gen_random_uuid(),
    created_at timestamptz not null default now(),
    alert_type text not null,
    title text not null,
    message text not null,
    severity text not null,
    source text not null,
    current_value jsonb,
    threshold jsonb,
    created_timestamp timestamptz not null,
    constraint alert_type_valid check (
        alert_type in (
            'low_roas',
            'high_cac',
            'high_refund_rate',
            'creative_fatigue',
            'workflow_failure',
            'cost_spike',
            'missing_data'
        )
    ),
    constraint alert_severity_valid
        check (severity in ('info', 'warning', 'critical')),
    constraint alert_title_not_blank check (length(btrim(title)) > 0),
    constraint alert_message_not_blank check (length(btrim(message)) > 0),
    constraint alert_source_not_blank check (length(btrim(source)) > 0)
);

comment on table public.alerts is
    'Fictional alerts created only by deterministic application rules.';

-- Stores validated narrative summaries and safe provider/fallback metadata.
create table public.generated_summaries (
    id uuid primary key default gen_random_uuid(),
    created_at timestamptz not null default now(),
    overall_status text not null,
    executive_summary text not null,
    key_findings jsonb not null,
    recommended_actions jsonb not null,
    risks jsonb not null,
    provider_used text not null,
    generation_status text not null,
    fallback_reason text,
    constraint summary_overall_status_valid
        check (overall_status in ('healthy', 'attention', 'critical')),
    constraint summary_generation_status_valid
        check (generation_status in ('demo', 'live', 'fallback')),
    constraint summary_key_findings_array
        check (jsonb_typeof(key_findings) = 'array'),
    constraint summary_actions_array
        check (jsonb_typeof(recommended_actions) = 'array'),
    constraint summary_risks_array check (jsonb_typeof(risks) = 'array'),
    constraint summary_executive_not_blank
        check (length(btrim(executive_summary)) > 0),
    constraint summary_provider_not_blank
        check (length(btrim(provider_used)) > 0)
);

comment on table public.generated_summaries is
    'Validated Gemini or deterministic fallback narratives; never decisions.';

create index metrics_snapshots_created_at_idx
    on public.metrics_snapshots (created_at desc);
create index workflow_runs_created_at_idx
    on public.workflow_runs (created_at desc);
create index workflow_runs_status_idx
    on public.workflow_runs (status, severity);
create index alerts_created_at_idx on public.alerts (created_at desc);
create index alerts_severity_idx on public.alerts (severity, alert_type);
create index generated_summaries_created_at_idx
    on public.generated_summaries (created_at desc);

alter table public.metrics_snapshots enable row level security;
alter table public.workflow_runs enable row level security;
alter table public.alerts enable row level security;
alter table public.generated_summaries enable row level security;

grant select on public.metrics_snapshots to anon;
grant select on public.workflow_runs to anon;
grant select on public.alerts to anon;
grant select on public.generated_summaries to anon;

grant all on public.metrics_snapshots to service_role;
grant all on public.workflow_runs to service_role;
grant all on public.alerts to service_role;
grant all on public.generated_summaries to service_role;

create policy "Anon can read fictional metric snapshots"
    on public.metrics_snapshots for select to anon using (true);
create policy "Anon can read fictional workflow runs"
    on public.workflow_runs for select to anon using (true);
create policy "Anon can read fictional alerts"
    on public.alerts for select to anon using (true);
create policy "Anon can read fictional generated summaries"
    on public.generated_summaries for select to anon using (true);

