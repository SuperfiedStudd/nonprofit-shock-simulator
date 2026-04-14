# For ChatGPT Review

## What was built

- A deterministic distress pipeline from the single IRS cohort file.
- Cleaned financial ratios, multiple distress labels, temporal backtests, threshold rules, and a latest-year scored sample.

## Best label choice

- Recommended label: `composite_distress`.
- Why: it balances deficit, leverage, reserve weakness, and funding shock evidence instead of leaning on one noisy ratio.

## Most trustworthy findings

- Thin reserves are the cleanest distress separator.
- High leverage and weak net-asset position travel together with distress.
- Donation dependence is only dangerous when concentration is high and cushion is low.
- Bottom-quintile peer reserve position is a strong benchmarking signal.

## Weakest parts

- No sector taxonomy in the repo.
- Private-foundation sample is too thin for a stable standalone model.
- 2019-2020 is structurally broken by imputation.
- Reserve coverage is a net-assets proxy, not unrestricted liquid cash.

## Is the pipeline strong enough for final presentation insights?

- **Yes, with guardrails.**
- It is good enough to anchor the final story on who is at risk, what thresholds matter, and which interventions follow.
- It is not yet good enough for sector-specific claims or a polished funding-shock simulator.

## Exact recommendations for next steps

1. Add a funding-shock simulator.
2. Add sector/NTEE enrichment if any join source is available.
3. Turn the strongest thresholds into 3-5 slide-ready charts.
4. Convert the 2023 scored universe into a Fairlight shortlist with qualitative vetting.

## Blunt opinion

- Keep building on this pipeline; do not pivot away from distress modeling.
- The highest-return next move is business packaging, not a fancier model.
