# MarketForensics report

Educational research. Not financial advice.

## Problem

Daily NSE prices sometimes jump far more than that stock's recent volatility. This project explains those days with evidence. It does not try to sell a trading rule.

## Related work

Event studies treat a large return as something to explain with information around that date (Fama, Fisher, Jensen and Roll, 1969; MacKinlay, 1997). Interpretable models ask which inputs drove a prediction (Ribeiro, Singh and Guestrin, 2016; Lundberg and Lee, 2017). Multi-agent debate asks whether several model roles change the answer (Du et al., 2023). This project is a small student-scale combination of those ideas on NSE daily bars.

## Method

Prices are Yahoo Finance daily bars (`auto_adjust=True`) from 2022-01-01 for Nifty-style tickers plus `^NSEI`, saved as `NSEI.csv`. Cleaning drops non-positive closes and dates that are not on the Nifty calendar. No prices are forward-filled.

A case is a day where the absolute return is at least 2.5 times the prior 20-day standard deviation. The volatility window is shifted by one day so the event return is not inside its own baseline.

Features use only rows on or before the event day: return, 5-day return, 20-day volatility, volume versus its 20-day average, 20-day moving average, above or below that average, 5-day momentum, stock return minus Nifty return, and weekday.

Labels are rules: market-wide if the absolute Nifty return is at least 1.5 percentage points, else stock-specific if the absolute gap versus Nifty is at least 2.0, else volume shock if volume is at least 2.0 times its 20-day average, else unknown. A random forest is trained on older cases and tested on newer cases.

Mystery score subtracts a capped share explained by the same-day Nifty move and above-average volume from 100. The formula is in `src/marketforensics/mystery.py`.

Agents A (solo), B (three roles, majority vote), and C (same roles, rebuttal, chair) call Groq. Replies that are not the required JSON are retried. They are not replaced with handwritten text. Responses are cached by version, persona, ticker, date, and prompt hash.

The backtest checks whether the stated direction matches the sign of the return to the next trading day on or after 30 and 90 calendar days. High-vol and low-vol splits use the median 20-day volatility of the scored cases.

## Results

Cases found: 1332.

Random-forest test accuracy: 0.9166666666666666.
Train rows: 938. Test rows: 384.
Train ends 2025-05-09; test starts 2025-05-12.
Class counts: {'stock_specific': 755, 'market_wide': 351, 'unknown': 190, 'volume_shock': 26}.

Notes from the model step:

- The label is a rule on the Nifty return, the gap versus Nifty, and the volume ratio, and those same numbers are features. A high accuracy means the forest reproduced that rule on later dates. It does not mean a person confirmed the cause.

EDA notes from disk:

# EDA findings

- 1332 big-move cases across 31 stocks after the 2.5× shifted-volatility rule.
- TITAN.NS has the most cases (51).
- The month with the most cases is 2025-01 (47 cases).
- Median absolute case return is 3.67%.
- On 98% of cases the stock's absolute return exceeded the Nifty's absolute return that day.
- Largest single-day gain in the cleaned universe (excluding the index file) is 10.63% (BAJFINANCE.NS); largest drop is -15.45% (NTPC.NS).


Agent direction check:

- Version A: 3 of 14 direction calls matched the sign of the 30d forward return (21%). A 95% interval for that share is 8% to 48%. This describes these cases only. It is not a trading profit.
- Version B: 1 of 5 direction calls matched the sign of the 30d forward return (20%). A 95% interval for that share is 4% to 62%. This describes these cases only. It is not a trading profit.
- Version C: 3 of 13 direction calls matched the sign of the 30d forward return (23%). A 95% interval for that share is 8% to 50%. This describes these cases only. It is not a trading profit.

## Limitations

Daily bars hide intraday causes. The labels are rules on the same style of numbers the model sees, not confirmed corporate events. Historical headlines are not attached unless a real item is dated within a day of the case, so many news-analyst prompts see an empty list. Groq outputs can still be wrong. Sample sizes for the direction check may be small, so the interval can be wide. Nothing here is a portfolio or a recommendation to trade.

## Conclusion

Read the accuracy and the direction-match sentences above as a description of this sample. If debate (C) matches direction more often than solo (A), that is a comparison on these cases only. If it does not, that result stands. The project is for learning how to explain a move and how to admit what is still unexplained.
