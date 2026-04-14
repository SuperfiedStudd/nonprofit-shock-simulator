# Distress Pipeline Presentation Outline

## Slide 1: The Problem and Our Lens

**Title**

Who Is Financially Fragile, and Why?

**Core message**

We built an interpretable next-year distress pipeline on IRS nonprofit filings to identify who is at risk, what thresholds separate resilient from fragile organizations, and how Fairlight can use those signals for benchmarking and intervention.

**Numbers to show**

- 540,860 filing-year rows
- 122,392 EINs
- 145,852 clean observed Form 990 year-pairs in the core model

**Visual**

A simple funnel:
- raw cohort
- clean observed consecutive pairs
- scored organizations

**Speaker note**

Emphasize that this is not a black-box prediction exercise. The goal is decision-ready resilience insight.

## Slide 2: What We Mean by Distress

**Title**

A Practical, Multi-Signal Definition of Distress

**Core message**

We did not inherit the old label. We rebuilt distress from scratch as a next-year composite outcome that flags organizations showing multiple signs of strain.

**Definition to show**

`composite_distress = 1` when next year shows at least 2 of:
- operating margin <= -5%
- reserve proxy < 1.5 months
- liabilities/assets > 0.85
- revenue growth <= -20%
- asset growth <= -10%

Or:
- negative net assets and negative operating result together

**Numbers to show**

- Core distress rate: 20.8%
- Yearly range: 19.3% to 22.7%

**Visual**

A 5-box icon row for the symptoms, with the “2 or more” rule highlighted.

**Speaker note**

This definition is business-friendly because it captures structural weakness, not just one noisy accounting line.

## Slide 3: The Model Is Simple but Useful

**Title**

A Transparent Model That Still Finds Real Signal

**Core message**

A simple logistic model was enough. We kept the backbone interpretable and still achieved meaningful discrimination.

**Numbers to show**

- 2022 holdout ROC-AUC: 0.721
- 2022 holdout PR-AUC: 0.474
- 2022 holdout Brier: 0.131
- Base distress rate: 19.3%
- Top 5% risk bucket precision: 75.3%
- Top 10% risk bucket precision: 60.4%

**Visual**

A compact scorecard with the six numbers above.

**Speaker note**

The most important number for judges is not just AUC. It is that the top-ranked organizations are genuinely concentrated with distress.

## Slide 4: The Clearest Thresholds

**Title**

Three Thresholds Separate Fragile from Resilient Nonprofits

**Core message**

Reserve weakness, peer-relative reserve weakness, and leverage are the clearest threshold-style separators in the data.

**Numbers to show**

- Reserve proxy <= 2.6 months:
  - 52.4% distress
  - vs 13.8% above threshold
  - 6.9x odds
- Bottom 21st percentile of peer reserve position:
  - 43.8% distress
  - vs 13.4% otherwise
  - 5.1x odds
- Liabilities/assets >= 0.56:
  - 44.3% distress
  - vs 14.8% below threshold
  - 4.6x odds

**Visual**

A 3-column threshold table or three paired bar charts.

**Speaker note**

This is the strongest “judge-ready” slide in the deck because it converts the model into concrete thresholds.

## Slide 5: Funding Fragility Is Conditional, Not Universal

**Title**

Donation Dependence Is Not the Whole Story

**Core message**

Donation-heavy organizations are not automatically fragile. Fragility concentrates where funding is highly concentrated and cushion is low.

**Numbers to show**

- Donation-heavy alone:
  - 22.8% holdout distress
- Donation-heavy + concentrated + low cushion:
  - 49.8% holdout distress
- Revenue concentration `HHI >= 0.985`:
  - 27.7% distress
  - vs 17.1% below that level

**Visual**

A two-step escalation graphic:
- donation-heavy
- donation-heavy plus concentration plus low reserves

**Speaker note**

This is the bridge into funding risk simulation. The story is conditional fragility, not blanket fragility.

## Slide 6: Peer Benchmarking and Segment Insights

**Title**

Weakness Is Relative to Peers, Not Just Absolute

**Core message**

Peer-relative reserve position adds real signal, and scale matters even within the retained cohort.

**Numbers to show**

- Bottom fifth of peer reserve position:
  - 43.9% distress
- `under_1M` peer groups:
  - 24.7% holdout distress
- `25M_plus` peer groups:
  - 14.7% holdout distress
- Donation-led orgs with reserve proxy <= 2.6 months:
  - 46.6% distress
  - vs 17.5% above threshold

**Visual**

A peer benchmark card mockup:
- reserve percentile
- leverage percentile
- margin percentile
- risk flag

**Speaker note**

This is where Fairlight can say, “Compared with similar peers, this organization is under-reserved and over-levered.”

## Slide 7: Actionable Risk Archetypes

**Title**

From Scores to Intervention Archetypes

**Core message**

The model supports triage, not just ranking. We can identify distinct types of fragile organizations and connect each one to an intervention path.

**Numbers to show**

- High or Very High risk in 2023 scored universe:
  - 32.8% of observed Form 990 rows
- Leverage-loaded operators:
  - 2,750 orgs
  - 66.1% average predicted risk
- Donor-concentrated and cushion-poor:
  - 2,164 orgs
  - 45.2% average predicted risk
- Growing but fragile:
  - 248 orgs
  - 45.0% average predicted risk
- Small resilient outperformers:
  - 2,803 orgs
  - 7.3% average predicted risk

**Visual**

A 2x2 archetype matrix:
- risk level
- likely intervention type

**Speaker note**

This is the slide that turns the model into action: recapitalization, reserve planning, funding diversification, or peer-learning.

## Slide 8: What Fairlight Can Do Next

**Title**

How This Becomes a Fairlight Product

**Core message**

The distress pipeline is strong enough to anchor the final solution now, and the next build should be business packaging, not a more complex model.

**Map to the four objectives**

- Resilience Prediction:
  - Use the distress score and thresholds as the core risk layer
- Peer Benchmarking:
  - Turn peer percentiles into organization cards
- Funding Risk Simulation:
  - Add a scenario layer that shocks donations, program revenue, or expenses
- High-Impact Discovery:
  - Use archetypes plus mission overlays to build a target shortlist

**Blunt verdict to show**

Yes, this pipeline is good enough to serve as the backbone for final hackathon insights.

**What is still missing**

- Sector/NTEE enrichment
- Funding shock simulator
- Final presentation visuals built from the threshold and archetype outputs

**Visual**

A roadmap with:
- ready now
- next build
- stretch goal

**Speaker note**

Close by saying the highest-return next move is a scenario-and-benchmark experience, not more model complexity.
