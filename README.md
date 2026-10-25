# Executive Analytics Capstone: Customer Churn

Which customers should the subscription team contact first to stop avoidable churn?

**Presentation (live deck):** _paste your deck link here_
**Dashboard (Task 2):** _paste your GitHub Pages link here_
**Risk-score model (Task 4):** _paste your GitHub Pages link here_
**Presentation recording:** _paste your recording link here, or add the file to this folder_

## What is in this folder

| File | Purpose |
|---|---|
| `executive-brief.pdf` | Two-page executive brief: recommendation, decision table, five findings, impact range, limitations |
| `presentation-script.md` | Three-minute speaking script for the recording |
| `analysis.py` | Reproduces every number from the CSV. Run: `python3 analysis.py data/customer_churn_sample.csv outputs` |
| `outputs/results.json` | All figures used in the deck and the brief |
| `outputs/cleaning_log.md` | Data quality checks and what was changed (nothing) |
| `data/customer_churn_sample.csv` | Source data, 15 customers |

## Narrative

1. **Problem:** 7 of 15 customers churned (46.7%). That is 409.93 a month in revenue (32.3% of 1,269.85).
2. **What stands out:** all month-to-month customers left; churn happens in the first year; every churned customer had 3 or more tickets; the loyal two-year group is 47.2% of revenue and stable.
3. **Action:** a 90-day pilot contacting month-to-month customers in their first 12 months once they raise a third ticket.
4. **Impact:** 41–123 a month (492–1,476 a year) if outreach keeps 10–30% of would-be leavers. This range is an assumption.
5. **Measurement:** compare 90-day churn for contacted customers against a similar group that is not contacted.

## Five insights

1. Every month-to-month customer churned (7 of 7). None of 8 on One Year or Two Year contracts did.
2. 6 of 7 churned customers left within 12 months. Average tenure 7.0 months vs 29.1 for retained customers.
3. Churned customers had 3 or more tickets (average 4.3). Retained customers had 2 or fewer (average 1.0).
4. Revenue at risk (32.3%) is lower than customer churn (46.7%) because churned customers pay less (58.56 vs 107.49 a month).
5. A transparent 100-point score puts all 7 churned customers in the High tier. It fits this sample and is not yet proven on new customers.

## Assumptions and limitations

- The 10–30% outreach effect is a planning assumption, not measured here.
- The data has 15 customers, so one customer moves a rate by several points.
- Score weights were chosen after looking at this data.
- The findings are correlations. The data cannot show cause.
- No usage, billing or competitor data. The CSV does not state the currency, so amounts are shown without a symbol.

## Reproduce

```
python3 analysis.py data/customer_churn_sample.csv outputs
```

Standard library only (Python 3.8+).
