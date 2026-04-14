# Slide Chart Specs

## Chart 1

- **Title:** Next-Year Distress Rate by Reserve Buffer
- **File:** `charts/distress_by_reserve_buffer.png`
- **X field:** reserve months bucket (`<1.5`, `1.5-2.6`, `2.6-6`, `6+`)
- **Y field:** observed next-year distress rate
- **Segmentation:** none
- **Business message:** reserve weakness is the cleanest threshold separator

## Chart 2

- **Title:** Next-Year Distress Rate by Leverage Bucket
- **File:** `charts/distress_by_leverage_bucket.png`
- **X field:** liabilities/assets bucket
- **Y field:** observed next-year distress rate
- **Segmentation:** none
- **Business message:** leverage above roughly 0.56 materially changes risk

## Chart 3

- **Title:** Distress Falls as Peer Reserve Percentile Improves
- **File:** `charts/distress_by_peer_reserve_decile.png`
- **X field:** peer reserve decile
- **Y field:** observed next-year distress rate
- **Segmentation:** none
- **Business message:** peer-relative reserve weakness is a powerful benchmark signal

## Chart 4

- **Title:** Concentration + Low Cushion Interaction
- **File:** `charts/donation_concentration_low_cushion_heatmap.png`
- **X field:** concentration flag
- **Y field:** reserve flag
- **Value:** observed next-year distress rate
- **Business message:** concentrated funding is especially dangerous when cushion is already low

## Chart 5

- **Title:** Largest Average Risk Increases by Peer Group and Scenario
- **File:** `charts/shock_delta_by_peer_group.png`
- **X field:** average absolute risk increase
- **Y field:** peer group
- **Segmentation:** scenario
- **Business message:** shock sensitivity is concentrated in specific peer groups, not spread uniformly across the sector
