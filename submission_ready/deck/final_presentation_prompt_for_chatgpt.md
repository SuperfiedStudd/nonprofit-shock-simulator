# Final Presentation Prompt for ChatGPT

Use this file as the full build brief for the final hackathon presentation.

The goal is to create a judge-ready PowerPoint for Fairlight Advisors based on a completed nonprofit financial resilience pipeline. Do not invent a new modeling story. Build the presentation from the facts below.

## What you are making

Create a clean, business-facing presentation titled:

**Fairlight Advisors: A Financial Resilience Decision System for Nonprofits**

The deck should feel like a consulting-style solution pitch, not a data science research talk.

Target audience:

- hackathon judges
- Fairlight Advisors
- non-technical business audience

Tone:

- sharp
- credible
- transparent
- intervention-oriented

Design direction:

- clean white or warm neutral background
- navy / deep green / slate accents
- minimal clutter
- strong section titles
- one core message per slide

## Non-negotiable framing

- This is not a leaderboard ML story.
- This is an interpretable business analytics solution.
- The distress model is the backbone, but the product is a decision system.
- The final deck must emphasize business value:
  - resilience prediction
  - peer benchmarking
  - funding shock simulation
  - high-impact discovery
- Present the shock simulator as a deterministic scenario engine, not a causal forecast.
- Be explicit that donor vs grant/government exposure is approximated because the IRS filings aggregate contributions and grants.

## Core storyline

Use this exact narrative arc:

1. Nonprofit fragility is measurable before collapse.
2. A few transparent financial thresholds separate resilient from fragile organizations.
3. Those thresholds become peer benchmarks and stress-test inputs.
4. Fairlight can use this system to identify at-risk organizations, benchmark them, simulate shocks, and prioritize intervention.
5. The value is not one score. The value is a repeatable resilience decision system.

## Facts you must use

### Backbone credibility

- Primary label: `composite_distress`
- Final retained model: simple logistic distress model
- Temporal holdout metrics on the accepted backbone:
  - ROC-AUC: 0.721
  - PR-AUC: 0.474
  - Brier score: 0.131
  - holdout distress prevalence: 19.3%
  - top 5% risk bucket precision: 75.3%
  - top 10% risk bucket precision: 60.4%

### Current solution package coverage

- scored 2023 universe benchmark cards: 42,751 nonprofits
- total org-scenario rows in shock simulator: 384,759
- shortlist rows created: 30
- broad sector enrichment coverage: 71.2%

### Strongest threshold findings

- Reserve proxy below about 2.6 months is the strongest distress separator.
- Liabilities/assets above about 0.56 marks a major risk jump.
- Bottom-quintile peer reserve position is almost as important as low absolute reserves.
- Concentrated funding becomes much more dangerous when reserve cushion is weak.

### Distress rate chart values

Reserve buffer chart:

- `<1.5 months`: 64.7% distress
- `1.5-2.6 months`: 25.2% distress
- `2.6-6 months`: 19.1% distress
- `6+ months`: 12.8% distress

Leverage chart:

- `<0.25 liabilities/assets`: 15.1% distress
- `0.25-0.56`: 13.6% distress
- `0.56-0.8`: 17.9% distress
- `0.8+`: 66.2% distress

Peer reserve decile chart:

- `D1`: 63.0% distress
- `D2`: 22.9%
- `D3`: 18.7%
- `D4`: 16.0%
- `D5`: 14.2%
- `D6`: 13.5%
- `D7`: 11.6%
- `D8`: 11.5%
- `D9`: 12.1%
- `D10`: 8.1%

### Shock simulator findings

Required scenario families already implemented:

- donation revenue shock: -10%, -20%, -30%
- program revenue shock: -10%, -20%
- grant/government revenue shock: -10%, -20%
- expense inflation shock: +5%, +10%

Top scenario-level findings:

- `expense_inflation_10`: average absolute risk increase = 1.8 points; bucket upshift share = 10.3%
- `donation_shock_30`: average absolute risk increase = 1.4 points
- `program_shock_20`: average absolute risk increase = 1.2 points

Most shock-sensitive peer groups:

- `25M_plus__donation_led`: average delta 2.40 points
- `10M_25M__donation_led`: average delta 2.09 points
- `3M_10M__donation_led`: average delta 1.42 points

Most frequent shock-deterioration drivers:

- margin compression: 37,924 instances
- leverage pressure: 25,966
- reserve depletion: 22,757
- revenue contraction: 14,046
- asset erosion: 11,871

### Peer benchmarking findings

Size-band findings:

- `under_1M`: average risk 26.3%, high-risk share 53.4%
- `25M_plus`: average risk 15.4%, high-risk share 21.6%

Funding-model findings:

- `donation_led`: average risk 20.9%, high-risk share 37.4%
- `program_led`: average risk 18.6%, high-risk share 27.3%

Geography findings:

- West and South are somewhat riskier on average than Midwest in this scored universe.

Sector findings from broad NTEE enrichment:

- highest average-risk broad sector in the enriched scored universe: Housing & Shelter
- Housing & Shelter average risk: 29.95%
- Housing & Shelter high-risk share: 50.2%

### Key shortlist examples

Use a few examples, but do not over-index on naming individual organizations unless the slide clearly frames them as illustrative.

Fragile but investable examples:

- CAR DONATION FOUNDATION
  - peer group: `25M_plus__donation_led`
  - baseline distress probability: 26.6%
  - worst case: `donation_shock_20`
  - worst-case delta: +72.0 points
  - narrative: reserve weakness plus concentration risk
- Humane Society International
  - peer group: `25M_plus__donation_led`
  - baseline distress probability: 21.1%
  - worst case: `donation_shock_20`
  - worst-case delta: +77.0 points
  - narrative: reserve weakness plus low margin

Resilient outperformer examples:

- BELLSOUTH CORP HEALTH CARE TRUST - RETIREES
  - peer group: `25M_plus__program_led`
  - baseline distress probability: 2.1%
  - narrative: exceptional reserve, margin, and leverage position
- CARDINAL STRITCH UNIVERSITY INC
  - peer group: `25M_plus__program_led`
  - baseline distress probability: 1.7%
  - narrative: strong peer-relative fundamentals and low shock sensitivity

Shock-sensitive watchlist examples:

- BOOK-IT REPERTORY THEATRE
  - peer group: `1M_3M__mixed`
  - baseline distress probability: 12.6%
  - worst case: `expense_inflation_10`
  - worst-case delta: +85.5 points
- Keystone Independence Management
  - peer group: `3M_10M__program_led`
  - baseline distress probability: 11.0%
  - worst case: `program_shock_20`
  - worst-case delta: +85.8 points

## What the judges should remember

These are the 5 messages the audience should leave with:

1. Distress is predictable enough to support action.
2. Reserve buffer and leverage are the clearest practical thresholds.
3. Peer-relative weakness matters, not just raw financial level.
4. Stress testing turns the score into planning, not just prediction.
5. Fairlight can use this system to prioritize support, not just describe risk.

## Slide plan

Build 8 core slides plus 1 optional appendix slide.

## Slide 1: Title and value proposition

Title:

**From Financial Fragility to Resilience Planning**

Subtitle:

**An interpretable distress, benchmarking, and shock-simulation system for Fairlight Advisors**

Body message:

- We built a practical decision system that identifies financially fragile nonprofits before failure.
- It converts accounting signals into threshold rules, peer comparison, scenario testing, and intervention-ready shortlists.

Footer takeaway:

**This is not just a model. It is a resilience operating system.**

## Slide 2: The problem and why this matters

Title:

**Nonprofits do not fail all at once. Their balance sheets warn us first.**

Body:

- Financial fragility often shows up before collapse as reserve depletion, leverage pressure, weak margins, and concentrated funding.
- Fairlight needs a way to detect those patterns early enough to benchmark, triage, and intervene.
- We focused on transparent, defensible signals from IRS nonprofit filings rather than black-box ML.

Suggested visual:

- a simple left-to-right flow:
  - weak cushion
  - higher fragility
  - shock exposure
  - intervention need

## Slide 3: Why the backbone is credible

Title:

**A simple model was strong enough to support decisions**

Put these numbers clearly on the slide:

- ROC-AUC: 0.721
- PR-AUC: 0.474
- Brier: 0.131
- base distress rate: 19.3%
- top 5% precision: 75.3%
- top 10% precision: 60.4%

Interpretation text:

- We intentionally kept the backbone simple and interpretable.
- The goal was not to maximize complexity.
- The goal was to produce a trustworthy score that can anchor business actions.

Suggested visual:

- scorecard tiles for the 6 metrics

Takeaway line:

**The model is accurate enough to triage risk, but simple enough to defend.**

## Slide 4: The thresholds that separate resilient from fragile

Title:

**A few thresholds explain most of the resilience story**

Use 3 visual panels or 3 mini charts:

1. Reserve buffer
2. Leverage
3. Peer reserve percentile

Must include:

- Reserve buffer chart values
- Leverage chart values
- Peer reserve decile chart values

Callout statements:

- Below roughly 2.6 months of reserve, distress rises sharply.
- Above roughly 56% liabilities/assets, fragility jumps.
- Bottom-decile peer reserve position is a red flag even before a shock happens.

Takeaway line:

**The core resilience thresholds are simple enough to explain in one sentence.**

## Slide 5: Peer benchmarking turns prediction into action

Title:

**Relative weakness is often more actionable than absolute weakness**

Body:

- Every scored nonprofit gets a benchmark card.
- The card shows reserve percentile, margin percentile, leverage percentile, concentration percentile, and overall risk percentile within its peer group.
- Peer groups are based on size and funding model.

Must include these business insights:

- `under_1M` organizations show much higher average risk than `25M_plus`
- donation-led organizations are not uniformly fragile, but they carry more high-risk cases than program-led groups
- peer-relative weakness identifies where intervention should focus:
  - build reserves
  - reduce leverage
  - diversify revenue

Suggested visual:

- a mock benchmark card
- a small comparison table by size band and funding model

Takeaway line:

**Benchmarking tells Fairlight where an organization is weak relative to peers and what to fix first.**

## Slide 6: Funding shock simulator

Title:

**Stress testing shows who breaks first when conditions worsen**

Body:

- We built a deterministic scenario engine using the accepted distress backbone.
- For each organization, the simulator shocks revenue or expenses, recomputes key ratios, and re-scores distress probability.
- It outputs baseline risk, shocked risk, absolute increase, relative increase, and risk bucket change.

Must include:

- top scenario findings:
  - expense_inflation_10: +1.8 point average risk increase; 10.3% bucket upshift share
  - donation_shock_30: +1.4 point average increase
  - program_shock_20: +1.2 point average increase
- most shock-sensitive peer groups:
  - 25M_plus__donation_led
  - 10M_25M__donation_led
  - 3M_10M__donation_led
- top deterioration drivers:
  - margin compression
  - leverage pressure
  - reserve depletion

Suggested visual:

- bar chart of average risk increase by scenario
- small side panel showing the most shock-sensitive peer groups

Takeaway line:

**Shock sensitivity is not uniform. It concentrates in specific financially fragile peer segments.**

## Slide 7: Fairlight intervention shortlists

Title:

**We translated the analytics into intervention-ready priorities**

Use 3 columns or 3 cards:

1. Fragile but investable
2. Resilient outperformers
3. Shock-sensitive priority watchlist

Explain each:

- Fragile but investable:
  - currently meaningful risk
  - supportable with reserve-building, diversification, or balance-sheet repair
- Resilient outperformers:
  - financially strong peers worth learning from
- Shock-sensitive priority watchlist:
  - acceptable baseline risk but severe deterioration under stress

Include 1 or 2 example names per bucket from the examples above.

Important wording:

- Do not imply mission priority or social impact ranking.
- Frame these as financial resilience and intervention-readiness examples only.

Takeaway line:

**The system does not just identify risk. It identifies who to help, who to learn from, and who to watch.**

## Slide 8: Why this matters for Fairlight

Title:

**This can become Fairlight's resilience decision system**

Structure this slide around the 4 hackathon objectives:

1. Resilience Prediction
2. Peer Benchmarking
3. Funding Risk Simulation
4. High-Impact Discovery

For each objective, show:

- what the current solution already does
- what Fairlight could do next

Suggested content:

- Resilience Prediction:
  - next-year distress score
  - transparent thresholds
- Peer Benchmarking:
  - benchmark cards and peer-relative gaps
- Funding Risk Simulation:
  - scenario engine for donor, earned revenue, grant, and inflation shocks
- High-Impact Discovery:
  - intervention shortlists and resilient peer-learning cases

Close with:

**Recommendation: stop modeling and move into deployment, storytelling, and decision support.**

## Optional appendix slide

Title:

**Methods, caveats, and transparency**

Include:

- distress label: `composite_distress`
- retained model: logistic regression
- shock simulator is deterministic, not causal
- donor vs grant/government exposure is approximated
- broad sector enrichment coverage is 71.2%

## Chart instructions

If you can generate charts directly, recreate these 5 charts:

1. Next-Year Distress Rate by Reserve Buffer
2. Next-Year Distress Rate by Leverage Bucket
3. Distress Falls as Peer Reserve Percentile Improves
4. Concentration + Low Cushion Interaction
5. Largest Average Risk Increases by Peer Group and Scenario

If only 3 charts are used, prioritize:

1. reserve buffer
2. peer reserve percentile
3. shock scenario bar chart

## Required output format

Create the deck in a form that can be turned directly into PowerPoint.

Best output option:

- slide-by-slide presentation content
- each slide should include:
  - slide title
  - subtitle if needed
  - exact body copy
  - chart or visual recommendation
  - speaker notes

If you are able to create a `.pptx`, do that.
If not, produce presentation-ready slide content that can be copied directly into PowerPoint or Google Slides.

## Important constraints

- Avoid technical jargon where possible.
- Do not over-explain modeling mechanics.
- Use exact numbers from this brief.
- Prefer simple, punchy business statements.
- Keep the core deck to 8 slides.
- End with a confident recommendation, not a tentative research conclusion.

## Final instruction

Build the final presentation now.

Do not ask for more analysis.
Do not suggest additional modeling.
Use this brief to produce the finished deck.
