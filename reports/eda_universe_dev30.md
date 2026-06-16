# EDA v1 — profiling that motivates the method (stage 11; EDA only, no modelling)

## 1. Stationarity (ADF + KPSS, opposite nulls)
| name        |       adf_p |    kpss_p | stationary_consistent   |
|:------------|------------:|----------:|:------------------------|
| GE.N        | 2.28357e-23 | 0.0717958 | True                    |
| XOM.N       | 0           | 0.1       | True                    |
| MSFT.OQ     | 0           | 0.1       | True                    |
| C.N         | 1.11008e-23 | 0.1       | True                    |
| WMT.OQ      | 1.48276e-29 | 0.0930471 | True                    |
| PFE.N       | 2.03636e-30 | 0.1       | True                    |
| BAC.N       | 1.18222e-22 | 0.1       | True                    |
| JNJ.N       | 0           | 0.1       | True                    |
| AIG.N       | 1.0561e-25  | 0.1       | True                    |
| IBM.N       | 0           | 0.1       | True                    |
| INTC.OQ     | 0           | 0.1       | True                    |
| JPM.N       | 6.42639e-24 | 0.1       | True                    |
| PG.N        | 0           | 0.1       | True                    |
| CSCO.OQ     | 0           | 0.1       | True                    |
| MO.N        | 0           | 0.1       | True                    |
| VZ.N        | 0           | 0.1       | True                    |
| CVX.N       | 3.73234e-30 | 0.1       | True                    |
| WFC.N       | 2.61501e-22 | 0.1       | True                    |
| DELL.OQ^J13 | 0           | 0.1       | True                    |
| KO.N        | 0           | 0.1       | True                    |
| HD.N        | 0           | 0.1       | True                    |
| PEP.OQ      | 2.68264e-30 | 0.1       | True                    |
| TWX.N^F18   | 1.6883e-27  | 0.1       | True                    |
| T.N         | 2.02212e-30 | 0.1       | True                    |
| WB.N^A09    | 4.62223e-13 | 0.1       | True                    |
| AMGN.OQ     | 2.10702e-30 | 0.1       | True                    |
| EBAY.OQ     | 0           | 0.1       | True                    |
| CMCSA.OQ    | 0           | 0.1       | True                    |
| ABT.N       | 0           | 0.1       | True                    |
| JCI.N       | 0           | 0.1       | True                    |
*Caption: daily returns are level-stationary while volatility is not constant — the state uses a rolling 60-day log-return window rather than longer memory.*

## 2. Fat tails
| name        |    n |   mean_daily |   std_daily |        skew |   excess_kurtosis |        min |      max |
|:------------|-----:|-------------:|------------:|------------:|------------------:|-----------:|---------:|
| GE.N        | 5279 |  0.000418132 |   0.0207153 |  0.230671   |           8.89656 | -0.151592  | 0.197031 |
| XOM.N       | 5279 |  0.000443042 |   0.0166638 |  0.187865   |           9.93568 | -0.139525  | 0.171905 |
| MSFT.OQ     | 5279 |  0.000767509 |   0.0170323 |  0.277673   |           9.91285 | -0.14739   | 0.185116 |
| C.N         | 5279 |  0.000278966 |   0.0304435 |  1.44382    |          49.7551  | -0.390244  | 0.578249 |
| WMT.OQ      | 5279 |  0.000509299 |   0.0128181 |  0.277989   |          12.4364  | -0.113758  | 0.117085 |
| PFE.N       | 5279 |  0.000273477 |   0.0147331 |  0.175909   |           5.8485  | -0.106246  | 0.108552 |
| BAC.N       | 5279 |  0.000529282 |   0.0287776 |  0.896099   |          27.5082  | -0.289694  | 0.352691 |
| JNJ.N       | 5279 |  0.000393745 |   0.0108423 |  0.177602   |          11.4878  | -0.100379  | 0.122292 |
| AIG.N       | 5279 |  0.000255126 |   0.0365514 |  1.50144    |          76.7927  | -0.607908  | 0.66     |
| IBM.N       | 5279 |  0.000438636 |   0.0146187 | -0.100205   |           9.15522 | -0.128507  | 0.129642 |
| INTC.OQ     | 5279 |  0.000429351 |   0.0219841 |  0.0541983  |          13.4005  | -0.260585  | 0.227711 |
| JPM.N       | 5279 |  0.000756106 |   0.0226424 |  0.937041   |          19.8256  | -0.207274  | 0.250967 |
| PG.N        | 5279 |  0.000356649 |   0.0113934 |  0.0650716  |           9.94727 | -0.0873734 | 0.12009  |
| CSCO.OQ     | 5279 |  0.000490962 |   0.0174838 | -0.0703576  |          11.6759  | -0.160343  | 0.159505 |
| MO.N        | 5279 |  0.000591268 |   0.0132067 | -0.395597   |          12.1883  | -0.124242  | 0.163753 |
| VZ.N        | 5279 |  0.000312473 |   0.0129936 |  0.307625   |           8.38521 | -0.0806855 | 0.146324 |
| CVX.N       | 5279 |  0.00052116  |   0.0177843 |  0.0681273  |          20.5176  | -0.221248  | 0.227407 |
| WFC.N       | 5279 |  0.000626922 |   0.0251401 |  1.57304    |          27.9229  | -0.238223  | 0.327645 |
| DELL.OQ^J13 | 2218 | -0.000237879 |   0.0223891 | -0.21419    |           7.02726 | -0.171751  | 0.143717 |
| KO.N        | 5279 |  0.000420572 |   0.0114016 |  0.0924647  |          12.4099  | -0.0967248 | 0.138795 |
| HD.N        | 5279 |  0.000622163 |   0.0163376 |  0.00676264 |          10.3046  | -0.197938  | 0.140666 |
| PEP.OQ      | 5279 |  0.000374128 |   0.0114664 | -0.118455   |          15.9438  | -0.119314  | 0.129366 |
| TWX.N^F18   | 3382 |  0.000508083 |   0.0174146 |  0.464904   |          12.8967  | -0.13145   | 0.17068  |
| T.N         | 5279 |  0.00036848  |   0.0141293 |  0.227413   |          10.7791  | -0.104061  | 0.162801 |
| WB.N^A09    | 1003 |  1.9999e-05  |   0.0627848 |  2.77819    |          89.4449  | -0.816     | 0.902174 |
| AMGN.OQ     | 5279 |  0.000515192 |   0.0163662 |  0.670584   |           8.27015 | -0.095846  | 0.150737 |
| EBAY.OQ     | 5279 |  0.000492382 |   0.0212963 |  0.166321   |           9.31235 | -0.191363  | 0.204246 |
| CMCSA.OQ    | 5279 |  0.000422797 |   0.0177471 |  0.313686   |          14.6054  | -0.146635  | 0.255507 |
| ABT.N       | 5279 |  0.000506878 |   0.0137144 | -0.145503   |           6.60246 | -0.0978567 | 0.10936  |
| JCI.N       | 5279 |  0.000541522 |   0.0176259 |  0.0202771  |           9.31255 | -0.142068  | 0.193215 |
Hill left-tail indices (5% tail): {'GE.N': 2.69, 'XOM.N': 3.14, 'MSFT.OQ': 3.16, 'C.N': 2.19, 'WMT.OQ': 2.82, 'PFE.N': 3.13, 'BAC.N': 2.13, 'JNJ.N': 2.87, 'AIG.N': 1.93, 'IBM.N': 2.72, 'INTC.OQ': 2.87, 'JPM.N': 2.57, 'PG.N': 2.79, 'CSCO.OQ': 2.79, 'MO.N': 2.76, 'VZ.N': 3.11, 'CVX.N': 3.02, 'WFC.N': 2.4, 'DELL.OQ^J13': 2.97, 'KO.N': 2.96, 'HD.N': 3.16, 'PEP.OQ': 3.13, 'TWX.N^F18': 2.51, 'T.N': 2.73, 'WB.N^A09': 1.81, 'AMGN.OQ': 3.15, 'EBAY.OQ': 2.75, 'CMCSA.OQ': 2.84, 'ABT.N': 2.83, 'JCI.N': 3.04}
![QQ](reports/figures/eda_qq_pooled.png)
*Caption: excess kurtosis ≫ 0 and Hill α near/below 3 mean variance understates risk — the fitness penalises empirical CVaR at α=0.05 (PREREG §3) instead of trusting σ.*

## 3. Volatility clustering
| name        |   arch_lm_stat |      p_value | clustering   |
|:------------|---------------:|-------------:|:-------------|
| GE.N        |        934.444 | 2.45309e-194 | True         |
| XOM.N       |       1244.94  | 2.9037e-261  | True         |
| MSFT.OQ     |        631.092 | 3.81683e-129 | True         |
| C.N         |        771.801 | 2.37519e-159 | True         |
| WMT.OQ      |        373.907 | 3.335e-74    | True         |
| PFE.N       |        531.889 | 6.7189e-108  | True         |
| BAC.N       |       1126.15  | 1.21278e-235 | True         |
| JNJ.N       |        989.043 | 4.28681e-206 | True         |
| AIG.N       |       1017.66  | 2.94096e-212 | True         |
| IBM.N       |        455.732 | 1.25058e-91  | True         |
| INTC.OQ     |        347.183 | 1.57808e-68  | True         |
| JPM.N       |       1062.95  | 5.10636e-222 | True         |
| PG.N        |       1318.52  | 3.85855e-277 | True         |
| CSCO.OQ     |        307.972 | 3.20541e-60  | True         |
| MO.N        |        542.403 | 3.78412e-110 | True         |
| VZ.N        |        888.101 | 2.31648e-184 | True         |
| CVX.N       |       1351.26  | 3.30679e-284 | True         |
| WFC.N       |        832.63  | 1.98806e-172 | True         |
| DELL.OQ^J13 |        142.933 | 1.05502e-25  | True         |
| KO.N        |        985.931 | 2.00617e-205 | True         |
| HD.N        |       1109.36  | 5.05884e-232 | True         |
| PEP.OQ      |       1609.67  | 0            | True         |
| TWX.N^F18   |        527.486 | 5.87348e-107 | True         |
| T.N         |        757.727 | 2.51182e-156 | True         |
| WB.N^A09    |        450.663 | 1.5088e-90   | True         |
| AMGN.OQ     |        352.647 | 1.09276e-69  | True         |
| EBAY.OQ     |        111.733 | 2.38519e-19  | True         |
| CMCSA.OQ    |        684.743 | 1.18266e-140 | True         |
| ABT.N       |        815.391 | 1.01252e-168 | True         |
| JCI.N       |        628.776 | 1.19757e-128 | True         |
![ACF](reports/figures/eda_abs_return_acf.png)
*Caption: ARCH effects and slow |r| ACF decay are regime persistence — the 3-state HMM with FILTERED probabilities (R3) captures it without look-ahead.*

## 4. Correlation regimes & dispersion
![rolling corr](reports/figures/eda_rolling_corr.png)
![dispersion](reports/figures/eda_dispersion.png)
*Caption: pairwise correlation spikes in stress — diversification fails exactly when the tail matters, motivating tail-risk feedback to the reward designer over mean-variance logic.*

## 5. Drawdown anatomy (deepest episodes in span)
| peak                | trough              | recovery            |     depth |   length_sessions |
|:--------------------|:--------------------|:--------------------|----------:|------------------:|
| 2007-10-10 00:00:00 | 2009-03-05 00:00:00 | 2011-02-08 00:00:00 | -0.561741 |               839 |
| 2020-02-13 00:00:00 | 2020-03-23 00:00:00 | 2020-12-04 00:00:00 | -0.348918 |               206 |
| 2022-01-12 00:00:00 | 2022-09-30 00:00:00 | 2023-12-13 00:00:00 | -0.218716 |               483 |
| 2018-01-29 00:00:00 | 2018-12-24 00:00:00 | 2019-04-01 00:00:00 | -0.183248 |               295 |
*Caption: crisis depth/length asymmetry motivates keeping the GFC inside the development window (PREREG §6) — evolved rewards must SEE a crisis to be tested against one.*

## 6. Missingness
![missingness](reports/figures/eda_missingness.png)
*Caption: missingness is structural (pre-IPO / post-delisting), not random — the missing-data engine masks and terminates rather than interpolating (R4).*

## 7. Reconstitution turnover -> cost grid
*Naive top-N reconstitution turnover feeds the cost columns [0, 5, 10, 20, 50] bps (DeMiguel et al. 2009 convention; 50bps = stress column). Computed when PIT membership lands.*
