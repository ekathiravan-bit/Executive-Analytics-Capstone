"""Reproducible analysis for the Executive Analytics Capstone.

Usage: python3 analysis.py data/customer_churn_sample.csv outputs/
Reads the churn CSV, runs data-quality checks, computes every figure used in the
deck and the executive brief, and writes results.json and cleaning_log.md.
Standard library only.
"""
import csv, json, statistics, sys, os

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
rows = list(csv.DictReader(open(src, newline="")))
for r in rows:
    r["Age"] = int(r["Age"]); r["TenureMonths"] = int(r["TenureMonths"])
    r["MonthlyCharges"] = float(r["MonthlyCharges"]); r["TotalCharges"] = float(r["TotalCharges"])
    r["SupportTickets"] = int(r["SupportTickets"]); r["churned"] = r["Churn"] == "Yes"

# ---------- data quality checks ----------
log = []
cols = list(rows[0].keys())
missing = sum(1 for r in rows for c in cols if str(r[c]).strip() == "")
dups = len(rows) - len({r["CustomerID"] for r in rows})
neg = sum(1 for r in rows if min(r["Age"], r["TenureMonths"], r["MonthlyCharges"], r["TotalCharges"], r["SupportTickets"]) < 0)
mismatch = [r["CustomerID"] for r in rows if abs(r["MonthlyCharges"] * r["TenureMonths"] - r["TotalCharges"]) > 0.05]
def iqr_out(vals):
    q = statistics.quantiles(vals, n=4); i = q[2] - q[0]
    return [v for v in vals if v < q[0] - 1.5 * i or v > q[2] + 1.5 * i]
extreme = {c: iqr_out([r[c] for r in rows]) for c in ["Age", "TenureMonths", "MonthlyCharges", "SupportTickets"]}
cats = {c: sorted({r[c] for r in rows}) for c in ["Gender", "SubscriptionType", "ContractType", "PaymentMethod", "Churn"]}
log += [
    f"Rows: {len(rows)}; columns: {len(cols)}",
    f"Missing values: {missing}",
    f"Duplicate CustomerID: {dups}",
    f"Negative or impossible numeric values: {neg}",
    f"Rows where TotalCharges differs from MonthlyCharges x TenureMonths by more than 0.05: {len(mismatch)} {mismatch}",
    "Extreme values by 1.5 x IQR rule: " + json.dumps(extreme),
    "Categories: " + json.dumps(cats),
    "No rows were dropped or altered.",
]

# ---------- helpers ----------
n = len(rows)
ch = [r for r in rows if r["churned"]]; kp = [r for r in rows if not r["churned"]]
mrr = sum(r["MonthlyCharges"] for r in rows)
risk = sum(r["MonthlyCharges"] for r in ch)
avg = lambda xs: sum(xs) / len(xs)
def group(key):
    out = {}
    for r in rows:
        out.setdefault(r[key], []).append(r)
    return {k: {"n": len(v), "churned": sum(x["churned"] for x in v), "mrr": round(sum(x["MonthlyCharges"] for x in v), 2)} for k, v in out.items()}

# ---------- score (same rules as the risk-score page) ----------
def score(r):
    c = {"Month-to-Month": 40, "One Year": 15, "Two Year": 0}[r["ContractType"]]
    t = 30 if r["TenureMonths"] <= 6 else 20 if r["TenureMonths"] <= 12 else 10 if r["TenureMonths"] <= 24 else 0
    k = r["SupportTickets"]; k = 30 if k >= 5 else 20 if k >= 3 else 10 if k >= 1 else 0
    return c + t + k
tier = lambda s: "High" if s >= 60 else "Medium" if s >= 30 else "Low"
for r in rows:
    r["score"] = score(r); r["tier"] = tier(r["score"])
tiers = {t: {"n": sum(r["tier"] == t for r in rows), "churned": sum(r["tier"] == t and r["churned"] for r in rows)} for t in ["High", "Medium", "Low"]}

early = [r for r in rows if r["TenureMonths"] <= 12 and r["SupportTickets"] >= 3]
m2m_rest = [r for r in rows if r["ContractType"] == "Month-to-Month" and r not in early]
two = [r for r in rows if r["ContractType"] == "Two Year"]
mrr_of = lambda xs: round(sum(r["MonthlyCharges"] for r in xs), 2)

LO, HI = 0.10, 0.30  # planning assumption, not measured
res = {
    "customers": n, "churned": len(ch), "churn_rate_pct": round(100 * len(ch) / n, 1), "retention_rate_pct": round(100 * len(kp) / n, 1),
    "monthly_revenue": round(mrr, 2), "revenue_at_risk_monthly": round(risk, 2), "revenue_at_risk_annual": round(risk * 12, 2),
    "revenue_at_risk_share_pct": round(100 * risk / mrr, 1),
    "avg_tenure_churned": round(avg([r["TenureMonths"] for r in ch]), 1), "avg_tenure_retained": round(avg([r["TenureMonths"] for r in kp]), 1),
    "max_tenure_churned": max(r["TenureMonths"] for r in ch),
    "churned_within_12_months": sum(r["TenureMonths"] <= 12 for r in ch),
    "avg_tickets_churned": round(avg([r["SupportTickets"] for r in ch]), 2), "avg_tickets_retained": round(avg([r["SupportTickets"] for r in kp]), 2),
    "min_tickets_churned": min(r["SupportTickets"] for r in ch), "max_tickets_retained": max(r["SupportTickets"] for r in kp),
    "avg_monthly_churned": round(avg([r["MonthlyCharges"] for r in ch]), 2), "avg_monthly_retained": round(avg([r["MonthlyCharges"] for r in kp]), 2),
    "by_contract": group("ContractType"), "by_plan": group("SubscriptionType"), "by_payment": group("PaymentMethod"),
    "tiers": tiers,
    "two_year_share_of_revenue_pct": round(100 * mrr_of(two) / mrr, 1), "two_year_mrr": mrr_of(two),
    "early_frustrated": {"n": len(early), "churned": sum(r["churned"] for r in early), "mrr": mrr_of(early)},
    "m2m_remaining": {"n": len(m2m_rest), "churned": sum(r["churned"] for r in m2m_rest), "mrr": mrr_of(m2m_rest)},
    "assumption_retained_share": [LO, HI],
    "impact_monthly": [round(risk * LO, 2), round(risk * HI, 2)],
    "impact_annual": [round(risk * LO * 12, 2), round(risk * HI * 12, 2)],
    "impact_per_100_customers_monthly": [round(risk / n * 100 * LO, 2), round(risk / n * 100 * HI, 2)],
    "revenue_at_risk_per_100_customers_monthly": round(risk / n * 100, 2),
}
json.dump(res, open(os.path.join(out, "results.json"), "w"), indent=2)
open(os.path.join(out, "cleaning_log.md"), "w").write("# Data quality and cleaning log\n\n" + "\n".join("- " + l for l in log) + "\n")
print("\n".join(log)); print(json.dumps(res, indent=2))
