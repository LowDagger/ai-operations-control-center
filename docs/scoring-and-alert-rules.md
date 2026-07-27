# Scoring, metric, and alert rules

## Authority

All formulas and alert decisions are implemented in deterministic Python.
`src/control_center/services/metric_service.py` owns calculations,
`src/control_center/services/alert_service.py` owns rule evaluation, and
`AlertThresholds` in `src/control_center/config.py` owns every threshold.

There is no hidden numeric health score. The deterministic demo summary labels
the overall narrative `critical` when any critical alert exists, `attention`
when warnings exist without a critical alert, and `healthy` when neither
exists. A live Gemini summary is narrative output, not an operational score.

## Metric formulas

| Metric | Formula | Zero or missing denominator |
| --- | --- | --- |
| Revenue | Source `revenue` | Display `N/A` when missing |
| Ad spend | Source `ad_spend` | Display `N/A` when missing |
| ROAS | `revenue / ad_spend` | `None` |
| CAC | `ad_spend / new_customers` | `None` |
| AOV | `revenue / orders` | `None` |
| CVR | `orders / sessions` | `None` |
| Order volume | Source `orders` | `None` when missing |
| Refund rate | `refunds / orders` | `None` |

Safe division returns `None` when either input is missing or the denominator is
zero. It never raises a division-by-zero exception and never substitutes an
invented value.

## Alert thresholds and severity

Comparisons are intentionally strict. A value exactly equal to a warning
boundary does not alert; a value exactly equal to a critical boundary remains
warning.

| Alert | Trigger | Warning | Critical |
| --- | --- | --- | --- |
| Low ROAS | ROAS below `2.00` | `1.00 ≤ ROAS < 2.00` | `ROAS < 1.00` |
| High CAC | CAC above `$50.00` | `$50.00 < CAC ≤ $100.00` | `CAC > $100.00` |
| High refund rate | Rate above `5%` | `5% < rate ≤ 10%` | `rate > 10%` |
| Creative fatigue | Frequency above `3.00` | `3.00 < frequency ≤ 5.00` | `frequency > 5.00` |
| Cost spike | Cost anomaly above `25%` | `25% < anomaly ≤ 50%` | `anomaly > 50%` |
| Workflow failure | Workflow status is `failed` | Uses stored workflow severity | Uses stored workflow severity |
| Missing data | Any DTC source field is `None` | Always warning | Not applicable |

ROAS, CAC, and refund-rate alerts are skipped when their calculated value is
`None`. Creative-fatigue evaluation is skipped when creative frequency is
missing. A zero denominator by itself is not treated as missing source data;
the missing-data rule checks only source fields whose value is `None`.

Workflow failures produce one alert per failed workflow. The alert takes the
validated severity already stored on that workflow observation. The alert
service does not make a retry or approval decision.

The missing-data rule emits one warning listing all absent source fields in
sorted order. It expects all eleven `DTCInputData` fields to be present.

## Fictional demo example

The committed January 15, 2026 fixture contains:

- revenue: `$12,000.00`;
- ad spend: `$8,000.00`;
- new customers: `120`;
- orders: `200`;
- sessions: `10,000`;
- refunds: `30`;
- creative frequency: `6.00`; and
- missing impressions.

Deterministic calculations:

| Metric | Calculation | Result |
| --- | --- | ---: |
| ROAS | `12,000 / 8,000` | `1.50x` |
| CAC | `8,000 / 120` | `$66.67` |
| AOV | `12,000 / 200` | `$60.00` |
| CVR | `200 / 10,000` | `2.00%` |
| Order volume | `orders` | `200` |
| Refund rate | `30 / 200` | `15.00%` |

The stable demo alert order is:

1. Low ROAS — warning.
2. High CAC — warning.
3. High refund rate — critical.
4. Creative fatigue — critical.
5. Refund Reconciliation workflow failure — critical.
6. Refund Reconciliation cost spike at 75% — critical.
7. Missing `impressions` — warning.

## AI and automation boundary

Gemini receives only validated calculated metrics, workflow observations, and
already-created alerts. It may summarize them through a strict
`FounderSummary`, but it does not calculate a metric, evaluate a threshold,
assign alert severity, create or modify an alert, decide a retry, or approve an
action.

n8n aggregates only raw source inputs and records workflow metadata. It does not
duplicate these formulas or alert rules and never writes directly to `alerts`.
