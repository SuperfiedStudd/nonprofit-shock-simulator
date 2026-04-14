# Distress Insight Candidates

## Thin reserves are the cleanest distress separator

- **Plain-English statement:** Organizations with less than 1.5 months of reserve proxy are materially more likely to hit next-year distress than the 19.3% overall holdout base rate.
- **Evidence:** Reserve thresholds lead both the threshold scan and the logistic coefficients.
- **Segment it applies to:** Overall
- **Confidence level:** High
- **Presentation usefulness:** High
- **Type:** predictive/actionable

## Leverage becomes dangerous when cushion is already thin

- **Plain-English statement:** High liabilities-to-assets ratios are much more concerning when reserve months are also low.
- **Evidence:** Leverage thresholds replicate in holdout and pair naturally with reserve thresholds.
- **Segment it applies to:** Overall
- **Confidence level:** High
- **Presentation usefulness:** High
- **Type:** predictive/actionable

## Donation-heavy is not the same thing as fragile

- **Plain-English statement:** Donation-heavy organizations are not uniformly fragile: donation share alone implies about 22.8% holdout distress, but donation concentration plus low cushion pushes risk to about 49.8%.
- **Evidence:** Donation share is weaker than the combination of concentration and reserve weakness.
- **Segment it applies to:** Donation-led organizations
- **Confidence level:** High
- **Presentation usefulness:** High
- **Type:** predictive/actionable

## Peer-relative weakness matters beyond absolute levels

- **Plain-English statement:** Organizations sitting in the bottom fifth of peer reserve position reach about 43.9% holdout distress, well above the overall base rate.
- **Evidence:** `peer_pct_reserve <= 0.21` is one of the strongest replicated threshold rules.
- **Segment it applies to:** Size x funding peers
- **Confidence level:** High
- **Presentation usefulness:** High
- **Type:** predictive/actionable

## Extreme revenue concentration is risky

- **Plain-English statement:** When revenue concentration is extremely high, next-year distress rises to about 27.0% in holdout.
- **Evidence:** `revenue_hhi_clean >= 0.98` is a replicated overall threshold rule.
- **Segment it applies to:** Overall
- **Confidence level:** High
- **Presentation usefulness:** High
- **Type:** predictive/actionable

## Small resilient outperformers are a real segment

- **Plain-English statement:** Smaller nonprofits can still look resilient when they combine above-peer margins with deep reserve buffers.
- **Evidence:** The "Small resilient outperformers" archetype scores well below average risk.
- **Segment it applies to:** 1M-3M nonprofits
- **Confidence level:** Medium
- **Presentation usefulness:** High
- **Type:** descriptive/predictive

## Falling below the 1M scale boundary is a real risk state

- **Plain-English statement:** Boundary-year organizations in the retained `under_1M` peer groups show about 24.7% holdout distress versus only 14.7% for `25M_plus` peer groups.
- **Evidence:** Peer-group coefficients and holdout rates both show a strong scale gradient.
- **Segment it applies to:** Size bands
- **Confidence level:** Medium
- **Presentation usefulness:** High
- **Type:** descriptive/predictive

## High predicted risk is concentrated rather than diffuse

- **Plain-English statement:** In the latest 2023 scoring pass, 32.8% of observed Form 990 rows fall into High or Very High risk buckets.
- **Evidence:** The scored 2023 universe is concentrated enough to support triage rather than broad-brush intervention.
- **Segment it applies to:** Latest scored year
- **Confidence level:** High
- **Presentation usefulness:** High
- **Type:** predictive/actionable

## Growing but fragile is a real archetype

- **Plain-English statement:** Fast growth is not automatically healthy when expenses are rising even faster and reserves are thin.
- **Evidence:** The archetype table shows elevated predicted risk for "Growing but fragile" organizations.
- **Segment it applies to:** Fast-growing operators
- **Confidence level:** Medium
- **Presentation usefulness:** High
- **Type:** predictive/actionable

## Donor-concentrated and cushion-poor is a high-risk archetype

- **Plain-English statement:** The riskiest donation-led nonprofits are the ones with both concentrated revenue and weak reserve buffers.
- **Evidence:** Archetype scoring and threshold scan point to the same combination.
- **Segment it applies to:** Donation-led organizations
- **Confidence level:** High
- **Presentation usefulness:** High
- **Type:** predictive/actionable

## Leverage-loaded operators are intervention-ready targets

- **Plain-English statement:** Organizations carrying high leverage without enough reserve cushion are clear candidates for capital-structure or liquidity intervention.
- **Evidence:** This archetype sits near the top of predicted risk.
- **Segment it applies to:** Highly leveraged organizations
- **Confidence level:** High
- **Presentation usefulness:** High
- **Type:** predictive/actionable
