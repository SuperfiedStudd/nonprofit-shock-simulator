# Shock Simulator Method

## Scenario definitions

- Donation revenue shock: -10%, -20%, -30%
- Program/service revenue shock: -10%, -20%
- Grant/government revenue shock: -10%, -20%
- Expense inflation shock: +5%, +10%

## Core formulas

- `baseline_risk`: retained logistic distress score from the accepted backbone.
- `shocked_risk`: retained logistic distress score after scenario-adjusted features are recomputed.
- `absolute_increase = shocked_risk - baseline_risk`
- `relative_increase = absolute_increase / baseline_risk`
- `risk_bucket_transition`: baseline bucket to shocked bucket using the same cutoffs as the backbone (`Low`, `Watch`, `High`, `Very High`).

## Financial propagation assumptions

- Revenue shocks reduce current-year total revenue one-for-one.
- Expense inflation increases current-year total expenses one-for-one.
- Shocks flow directly into current-year surplus/deficit, net assets, and total assets.
- Liabilities are held constant in the shock pass.
- Peer group is held fixed. We treat the shock as worsening financial condition inside the existing peer context, not instantly changing organizational identity.

## Donation vs grant/government split assumption

- IRS filings aggregate contributions and grants into one line, so donor and grant/government exposure cannot be observed directly in this repo.
- To approximate that split, we assign a donor-sensitive weight to `contributions_grants` using:
  - funding model (`donation_led`, `mixed`, `program_led`)
  - fundraising expense share
- Donation shock hits the donor-sensitive portion.
- Grant/government shock hits the remaining portion.

## Recomputed features

- operating margin
- reserve months proxy
- liability ratio
- net asset ratio
- revenue growth
- expense growth gap
- asset growth
- donation share
- revenue concentration (HHI)

## Known limitations

- The donor vs grant/government split is an informed proxy, not a directly observed field.
- The simulator is deterministic and accounting-based; it does not model behavioral adaptation or delayed management response.
- Sector-specific shock assumptions are not used beyond optional broad NTEE enrichment.
