# Shock Segment Summary

## Biggest scenario-level movers

| scenario_name        |   org_count |   avg_baseline_risk |   avg_shocked_risk |   avg_absolute_increase |   median_absolute_increase |   bucket_upshift_share |   severe_jump_share |
|:---------------------|------------:|--------------------:|-------------------:|------------------------:|---------------------------:|-----------------------:|--------------------:|
| expense_inflation_10 |       42751 |            0.198429 |           0.216608 |              0.0181788  |                0.0078595   |              0.102992  |         0.001076    |
| donation_shock_30    |       42751 |            0.198429 |           0.212525 |              0.014096   |                0.000410641 |              0.0678347 |         0.00261982  |
| program_shock_20     |       42751 |            0.198429 |           0.210622 |              0.0121926  |                0.0016303   |              0.0715305 |         0.00336834  |
| donation_shock_20    |       42751 |            0.198429 |           0.20836  |              0.00993038 |                0.000275889 |              0.0480457 |         0.000795303 |
| expense_inflation_5  |       42751 |            0.198429 |           0.207776 |              0.00934714 |                0.00401658  |              0.0529578 |         0.000280695 |

## Most robust scenarios

| scenario_name     |   org_count |   avg_baseline_risk |   avg_shocked_risk |   avg_absolute_increase |   median_absolute_increase |   bucket_upshift_share |   severe_jump_share |
|:------------------|------------:|--------------------:|-------------------:|------------------------:|---------------------------:|-----------------------:|--------------------:|
| donation_shock_10 |       42751 |            0.198429 |           0.203505 |              0.00507618 |                0.000130247 |             0.0236252  |         0.000163739 |
| grant_shock_20    |       42751 |            0.198429 |           0.201979 |              0.00355001 |                0.000238207 |             0.017099   |         7.01738e-05 |
| grant_shock_10    |       42751 |            0.198429 |           0.200081 |              0.00165138 |                0.000113711 |             0.00930972 |         2.33913e-05 |

## Most shock-sensitive peer groups

| peer_group             |   avg_delta |   avg_bucket_up |   scenario_count |
|:-----------------------|------------:|----------------:|-----------------:|
| 25M_plus__donation_led |  0.0240013  |       0.0984627 |                9 |
| 10M_25M__donation_led  |  0.0208593  |       0.0902483 |                9 |
| 3M_10M__donation_led   |  0.0141631  |       0.0676875 |                9 |
| 1M_3M__donation_led    |  0.0103629  |       0.0517146 |                9 |
| 10M_25M__program_led   |  0.00878889 |       0.0502435 |                9 |
| 3M_10M__program_led    |  0.00873872 |       0.0499356 |                9 |
| 25M_plus__program_led  |  0.00854488 |       0.049737  |                9 |
| 1M_3M__program_led     |  0.00771171 |       0.0478963 |                9 |
| under_1M__donation_led |  0.00684039 |       0.0363339 |                9 |
| 25M_plus__mixed        |  0.00636174 |       0.045977  |                9 |

## Most frequent deterioration drivers

| driver                |   count |
|:----------------------|--------:|
| margin compression    |   37924 |
| leverage pressure     |   25966 |
| reserve depletion     |   22757 |
| revenue contraction   |   14046 |
| asset erosion         |   11871 |
| donation dependence   |     526 |
| revenue concentration |     478 |

## Business readout

- Reserve-poor and leverage-heavy organizations absorb shocks worst because the same revenue hit converts quickly into a balance-sheet hit.
- Donation-led fragility is concentrated where concentration is already high and cushion is thin.
- Expense inflation is broadly painful, but direct revenue shocks produce the sharpest bucket jumps in already fragile segments.
