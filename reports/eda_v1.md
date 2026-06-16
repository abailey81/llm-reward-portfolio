# EDA v1 — profiling that motivates the method (stage 11; EDA only, no modelling)

## 1. Stationarity (ADF + KPSS, opposite nulls)
| name   |       adf_p |    kpss_p | stationary_consistent   |
|:-------|------------:|----------:|:------------------------|
| AAPL   | 4.19933e-30 | 0.1       | True                    |
| C      | 1.19192e-23 | 0.1       | True                    |
| GE     | 2.20115e-23 | 0.0692817 | True                    |
| MSFT   | 0           | 0.1       | True                    |
| XOM    | 0           | 0.1       | True                    |
| ABBV   | 7.33517e-27 | 0.1       | True                    |
| AMD    | 0           | 0.0569745 | True                    |
| AMZN   | 0           | 0.1       | True                    |
| AVGO   | 0           | 0.1       | True                    |
| BAC    | 1.20518e-22 | 0.1       | True                    |
| BRK-B  | 2.18346e-30 | 0.1       | True                    |
| COST   | 0           | 0.1       | True                    |
| CRM    | 0           | 0.1       | True                    |
| CVX    | 2.46234e-28 | 0.1       | True                    |
| GOOGL  | 0           | 0.1       | True                    |
| HD     | 0           | 0.1       | True                    |
| JNJ    | 0           | 0.1       | True                    |
| JPM    | 6.78062e-24 | 0.1       | True                    |
| KO     | 0           | 0.1       | True                    |
| LLY    | 0           | 0.01      | False                   |
| MA     | 4.24955e-30 | 0.0584441 | True                    |
| META   | 0           | 0.1       | True                    |
| NFLX   | 0           | 0.1       | True                    |
| NVDA   | 1.87138e-27 | 0.0868244 | True                    |
| PEP    | 2.57309e-30 | 0.1       | True                    |
| PG     | 0           | 0.1       | True                    |
| TSLA   | 0           | 0.1       | True                    |
| UNH    | 3.67224e-29 | 0.1       | True                    |
| V      | 5.48043e-30 | 0.1       | True                    |
| WMT    | 1.33561e-29 | 0.0890328 | True                    |
| IBM    | 0           | 0.1       | True                    |
| INTC   | 0           | 0.1       | True                    |
| MCD    | 9.19403e-30 | 0.1       | True                    |
| ORCL   | 0           | 0.1       | True                    |
| TMO    | 0           | 0.1       | True                    |
*Caption: daily returns are level-stationary while volatility is not constant — the state uses a rolling 60-day log-return window rather than longer memory.*

## 2. Fat tails
| name   |    n |   mean_daily |   std_daily |        skew |   excess_kurtosis |        min |      max |
|:-------|-----:|-------------:|------------:|------------:|------------------:|-----------:|---------:|
| AAPL   | 5281 |  0.00127788  |   0.020258  |  0.0327321  |           5.75349 | -0.179195  | 0.153288 |
| C      | 5281 |  0.000281411 |   0.0304272 |  1.44982    |          49.9016  | -0.390244  | 0.57825  |
| GE     | 5281 |  0.000419968 |   0.0207134 |  0.230757   |           8.89847 | -0.151592  | 0.197031 |
| MSFT   | 5281 |  0.000764833 |   0.0170104 |  0.275003   |           9.94279 | -0.147391  | 0.186047 |
| XOM    | 5281 |  0.000438308 |   0.016666  |  0.187942   |           9.92684 | -0.139525  | 0.171905 |
| ABBV   | 3268 |  0.000872266 |   0.0165735 | -0.664566   |          10.2266  | -0.162524  | 0.137673 |
| AMD    | 5281 |  0.00108761  |   0.0362548 |  0.721084   |          12.5219  | -0.261798  | 0.522901 |
| AMZN   | 5281 |  0.00116048  |   0.0237824 |  0.870217   |          14.7591  | -0.21822   | 0.269497 |
| AVGO   | 4125 |  0.00167296  |   0.0238671 |  0.322709   |           8.82028 | -0.199129  | 0.244326 |
| BAC    | 5281 |  0.000533172 |   0.0287601 |  0.896654   |          27.5594  | -0.289693  | 0.352691 |
| BRK-B  | 5281 |  0.00049731  |   0.0132925 |  0.736444   |          17.1457  | -0.10944   | 0.192641 |
| COST   | 5281 |  0.00072255  |   0.014085  | -0.0639898  |           7.97395 | -0.124513  | 0.107514 |
| CRM    | 5281 |  0.00111511  |   0.0255899 |  0.605639   |           8.66724 | -0.197371  | 0.260449 |
| CVX    | 5281 |  0.000517276 |   0.0177773 |  0.0699535  |          20.5454  | -0.221248  | 0.227407 |
| GOOGL  | 5281 |  0.00096182  |   0.0189749 |  0.518112   |           8.69571 | -0.116341  | 0.199916 |
| HD     | 5281 |  0.000624954 |   0.0163394 |  0.00791073 |          10.3025  | -0.197939  | 0.140667 |
| JNJ    | 5281 |  0.000397807 |   0.0108434 |  0.178284   |          11.4823  | -0.100379  | 0.122292 |
| JPM    | 5281 |  0.00075953  |   0.0226297 |  0.938634   |          19.8483  | -0.207274  | 0.250967 |
| KO     | 5281 |  0.000415384 |   0.0114031 |  0.0930585  |          12.3982  | -0.0967247 | 0.138796 |
| LLY    | 5281 |  0.000809891 |   0.016472  |  0.536214   |          12.2985  | -0.141364  | 0.156798 |
| MA     | 4930 |  0.00120768  |   0.0204553 |  0.670729   |          10.4866  | -0.127255  | 0.208463 |
| META   | 3423 |  0.00114983  |   0.0250214 |  0.420415   |          20.3634  | -0.263901  | 0.296115 |
| NFLX   | 5281 |  0.00168855  |   0.0313391 |  0.284081   |          19.5217  | -0.351166  | 0.422235 |
| NVDA   | 5281 |  0.00178627  |   0.030665  |  0.185156   |           7.67713 | -0.307266  | 0.298066 |
| PEP    | 5281 |  0.000371579 |   0.0114695 | -0.118237   |          15.9183  | -0.119314  | 0.129366 |
| PG     | 5281 |  0.000356517 |   0.0113948 |  0.0639531  |           9.95776 | -0.0873735 | 0.12009  |
| TSLA   | 3900 |  0.0021089   |   0.0364026 |  0.372256   |           4.88817 | -0.210628  | 0.243951 |
| UNH    | 5281 |  0.000633424 |   0.0200024 |  0.479857   |          30.928   | -0.223797  | 0.34755  |
| V      | 4474 |  0.000908888 |   0.0179649 |  0.288855   |           9.40296 | -0.136435  | 0.149974 |
| WMT    | 5281 |  0.000509434 |   0.0128153 |  0.277103   |          12.4431  | -0.113757  | 0.117085 |
| IBM    | 5281 |  0.000447815 |   0.0146196 | -0.103276   |           9.15632 | -0.128507  | 0.129641 |
| INTC   | 5281 |  0.000436615 |   0.0219632 |  0.0502307  |          13.4205  | -0.260585  | 0.227711 |
| MCD    | 5281 |  0.000617235 |   0.0126009 |  0.335665   |          18.4506  | -0.158753  | 0.181254 |
| ORCL   | 5281 |  0.00073637  |   0.0193964 |  1.49865    |          31.4387  | -0.137908  | 0.359488 |
| TMO    | 5281 |  0.000713414 |   0.0166784 |  0.122313   |           6.51446 | -0.106369  | 0.168983 |
Hill left-tail indices (5% tail): {'AAPL': 3.48, 'C': 2.18, 'GE': 2.69, 'MSFT': 3.06, 'XOM': 3.14, 'ABBV': 2.63, 'AMD': 3.06, 'AMZN': 2.86, 'AVGO': 3.06, 'BAC': 2.14, 'BRK-B': 2.57, 'COST': 2.76, 'CRM': 3.35, 'CVX': 3.02, 'GOOGL': 3.59, 'HD': 3.16, 'JNJ': 2.87, 'JPM': 2.57, 'KO': 2.95, 'LLY': 2.78, 'MA': 3.03, 'META': 2.88, 'NFLX': 2.79, 'NVDA': 3.55, 'PEP': 3.15, 'PG': 2.78, 'TSLA': 3.28, 'UNH': 2.36, 'V': 3.07, 'WMT': 2.83, 'IBM': 2.71, 'INTC': 2.88, 'MCD': 2.67, 'ORCL': 3.26, 'TMO': 3.07}
![QQ](reports/figures/eda_qq_pooled.png)
*Caption: excess kurtosis ≫ 0 and Hill α near/below 3 mean variance understates risk — the fitness penalises empirical CVaR at α=0.05 (PREREG §3) instead of trusting σ.*

## 3. Volatility clustering
| name   |   arch_lm_stat |      p_value | clustering   |
|:-------|---------------:|-------------:|:-------------|
| AAPL   |       616.76   | 4.50921e-126 | True         |
| C      |       771.283  | 3.06915e-159 | True         |
| GE     |       935.309  | 1.59727e-194 | True         |
| MSFT   |       633.03   | 1.46614e-129 | True         |
| XOM    |      1245.51   | 2.19496e-261 | True         |
| ABBV   |       106.806  | 2.34677e-18  | True         |
| AMD    |        70.0275 | 4.37995e-11  | True         |
| AMZN   |        83.1181 | 1.22567e-13  | True         |
| AVGO   |       298.803  | 2.78391e-58  | True         |
| BAC    |      1124.76   | 2.41995e-235 | True         |
| BRK-B  |       663.607  | 4.05681e-136 | True         |
| COST   |       375.133  | 1.83098e-74  | True         |
| CRM    |       178.264  | 5.37115e-33  | True         |
| CVX    |      1351.88   | 2.4225e-284  | True         |
| GOOGL  |       168.045  | 7.0439e-31   | True         |
| HD     |      1109.96   | 3.76524e-232 | True         |
| JNJ    |       989.483  | 3.44681e-206 | True         |
| JPM    |      1056.51   | 1.24677e-220 | True         |
| KO     |       986.501  | 1.51247e-205 | True         |
| LLY    |       380.332  | 1.43694e-75  | True         |
| MA     |       464.257  | 1.89721e-93  | True         |
| META   |        17.3201 | 0.067575     | False        |
| NFLX   |        25.3174 | 0.00477527   | True         |
| NVDA   |       146.29   | 2.1588e-26   | True         |
| PEP    |      1610.49   | 0            | True         |
| PG     |      1330.04   | 1.25434e-279 | True         |
| TSLA   |       148.26   | 8.49877e-27  | True         |
| UNH    |       636.268  | 2.96319e-130 | True         |
| V      |       682.817  | 3.06261e-140 | True         |
| WMT    |       375.187  | 1.78303e-74  | True         |
| IBM    |       455.922  | 1.13935e-91  | True         |
| INTC   |       345.572  | 3.46712e-68  | True         |
| MCD    |      1133.15   | 3.76313e-237 | True         |
| ORCL   |        99.4757 | 6.93883e-17  | True         |
| TMO    |       753.318  | 2.22434e-155 | True         |
![ACF](reports/figures/eda_abs_return_acf.png)
*Caption: ARCH effects and slow |r| ACF decay are regime persistence — the 3-state HMM with FILTERED probabilities (R3) captures it without look-ahead.*

## 4. Correlation regimes & dispersion
![rolling corr](reports/figures/eda_rolling_corr.png)
![dispersion](reports/figures/eda_dispersion.png)
*Caption: pairwise correlation spikes in stress — diversification fails exactly when the tail matters, motivating tail-risk feedback to the reward designer over mean-variance logic.*

## 5. Drawdown anatomy (deepest episodes in span)
| peak                | trough              | recovery            |     depth |   length_sessions |
|:--------------------|:--------------------|:--------------------|----------:|------------------:|
| 2007-12-11 00:00:00 | 2009-03-05 00:00:00 | 2009-12-14 00:00:00 | -0.464813 |               507 |
| 2020-02-20 00:00:00 | 2020-03-23 00:00:00 | 2020-07-14 00:00:00 | -0.319971 |               101 |
| 2022-01-04 00:00:00 | 2022-10-11 00:00:00 | 2023-05-26 00:00:00 | -0.237824 |               351 |
| 2018-10-02 00:00:00 | 2018-12-24 00:00:00 | 2019-03-19 00:00:00 | -0.193723 |               115 |
*Caption: crisis depth/length asymmetry motivates keeping the GFC inside the development window (PREREG §6) — evolved rewards must SEE a crisis to be tested against one.*

## 6. Missingness
![missingness](reports/figures/eda_missingness.png)
*Caption: missingness is structural (pre-IPO / post-delisting), not random — the missing-data engine masks and terminates rather than interpolating (R4).*

## 7. Reconstitution turnover -> cost grid
*Naive top-N reconstitution turnover feeds the cost columns [0, 5, 10, 20, 50] bps (DeMiguel et al. 2009 convention; 50bps = stress column). Computed when PIT membership lands.*
