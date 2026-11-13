# MarketForensics — Midterm report

**Project:** Explain unusual daily jumps in Indian (NSE) stocks  
**Status:** Midterm. Data, charts, clues, and the first model are done. AI debate and the backtest are not done yet.  
**Date range of the data:** 3 January 2022 to 30 September 2026  
**Disclaimer:** Educational research. Not financial advice. Not a trading system.

Add your name and class here before you submit: ____________________

---

## 1. What this project is, in one paragraph

Stock prices move every day. Sometimes one stock moves much more than it usually does. Most student projects try to guess tomorrow’s price. This project does something more honest: it looks at a day that **already happened** and asks **why the move was unusually large**. By the midterm, the computer can download real NSE prices, find those unusual days, draw charts, turn each day into a few numbers (“clues”), and train a simple model that sorts the day into one of four buckets. It does **not** yet ask a chat AI to write the explanation. That is the second half of the project.

---

## 2. The question

**When an NSE stock has an unusually large daily move, can simple price-and-volume clues say whether that move looks market-wide, stock-specific, a volume spike, or unclear?**

This is a sorting question about the past. It is not “should I buy?”

---

## 3. Words you need (say these in your own voice)

| Word | Plain meaning |
|------|----------------|
| NSE | India’s main stock exchange. Prices in this project come from there, via Yahoo Finance. |
| Ticker | The short code. `RELIANCE.NS` means Reliance on the NSE. `.NS` is the Yahoo suffix. |
| Nifty 50 | A basket of large Indian companies. Here the index ticker is `^NSEI`, saved as `NSEI.csv`. It stands for “the market.” |
| Open, High, Low, Close | The first, highest, lowest, and last price of the day. |
| Volume | How many shares traded that day. |
| Return | Percent change from yesterday’s close to today’s close. A return of 3 means the price rose about 3%. |
| Volatility | How jumpy recent returns have been. A calm stock and a wild stock should not use the same cutoff. |
| Case | One unusual day for one stock. The “file” we study. |
| Clue / feature | A number computed from prices up to that day. Example: volume was 2 times its recent average. |
| Label | The bucket we assign with a written rule: market-wide, stock-specific, volume shock, or unknown. |
| Train / test | The model learns on older days and is checked on newer days. |
| Leakage | Cheating by using information from the future. This project avoids that. |

---

## 4. What was used, and why

| Tool | Why it is here |
|------|----------------|
| Python | The language everything runs in. |
| pandas | Holds the price tables (one row per day). |
| yfinance | Downloads real daily prices from Yahoo Finance. No hand-typed prices. |
| NumPy | Ordinary math (averages, percent changes). |
| Matplotlib | Saves the charts in `data/plots/eda/`. |
| scikit-learn | Trains a Random Forest, which is a group of decision trees. |
| joblib | Saves that model as `models/rf_cause_v1.joblib` so it does not have to be retrained to be kept. |
| Streamlit and Plotly | The small website (`app.py`) that shows a case. |

**Not used for these midterm numbers:** Groq (the chat AI), a neural network, and a profit backtest. Those are the plan for the second half. The report does not invent their results.

---

## 5. Data

- **Source:** Yahoo Finance, daily bars, adjusted for splits and dividends (`auto_adjust=True`).
- **Start requested:** 1 January 2022.
- **What was kept:** 31 NSE stocks plus the Nifty index.
- **After cleaning:** 1,172 trading days each, from 3 January 2022 through 30 September 2026.
- **`TATAMOTORS.NS` failed.** Yahoo returned “quote not found.” It was skipped and listed in `data/raw/download_failures.json`. Grasim and Hindalco were included so the set still has more than 30 stocks.

Cleaning rules:

1. Drop duplicate dates.
2. Drop rows with a missing or non-positive close price.
3. Keep only dates that exist on the Nifty calendar.
4. Do **not** fill a missing price with the previous price. Filling would invent a return.

Aligned files are in `data/processed/`. A short table of row counts is in `data/DATA_README.md`.

---

## 6. How an unusual day is chosen

A fixed rule such as “any day over 3%” is unfair. A jumpy stock crosses 3% often. A calm stock almost never does.

The rule used here:

> A day is a **case** if the absolute return is at least **2.5 times** the standard deviation of the previous 20 daily returns.

The 20-day window is shifted back by one day, so **today’s return is not inside the measure of “normal”** that it is being compared with.

Result: **1,322 cases** across **31 stocks**.

Facts computed from those cases (`notes/eda_findings.md`):

- Titan (`TITAN.NS`) has the most cases: **50**.
- The busiest month is **January 2025**: **47** cases.
- The typical case (median) moved **3.67%** in absolute value.
- On **98%** of cases, the stock’s absolute move was larger than Nifty’s absolute move that same day.
- Largest up day in the cleaned files: **+10.63%** (Bajaj Finance).
- Largest down day: **−15.45%** (NTPC).

Charts saved for the presentation folder `data/plots/eda/`:

- Reliance price with volume
- Histogram of Reliance daily returns
- Reliance versus Nifty, both restarted at 100
- Bar chart of cases per stock
- Cases by month
- Heatmap of how stock returns line up with volume changes

---

## 7. Clues (features)

For each case, numbers are computed using **only prices on or before that day**:

| Clue | Meaning |
|------|---------|
| `return_pct` | That day’s percent move |
| `return_5d` / `momentum_5d` | Percent move over the last 5 trading days |
| `vol_20` | How jumpy the last 20 days were |
| `volume_vs_avg20` | Today’s volume divided by the average of the last 20 days |
| `ma_20` | 20-day average price |
| `above_ma` | 1 if the close is above that average, else 0 |
| `vs_nifty` | Stock return minus Nifty return the same day |
| `nifty_return_pct` | What the market itself did |
| `dow` | Day of the week, as a number |

Saved as `data/features/case_features.csv` (1,322 rows; none skipped).

The days **after** the jump are saved in `data/cases/case_windows.csv` so a human can look at context. Those “after” numbers are **not** given to the model. Using them would be leakage.

---

## 8. The four buckets (labels)

These are **rules written by us**, not facts from a news desk. First matching rule wins.

1. **market_wide** — Nifty itself moved at least 1.5% that day.
2. **stock_specific** — the stock’s return differs from Nifty by at least 2.0 percentage points.
3. **volume_shock** — volume is at least 2.0 times its 20-day average.
4. **unknown** — none of the above.

Counts in the full set of 1,322 cases:

| Bucket | Cases |
|--------|------:|
| stock_specific | 755 |
| market_wide | 351 |
| unknown | 190 |
| volume_shock | 26 |

`volume_shock` is a small group. Any sentence about that bucket should stay cautious.

---

## 9. The model

**Model:** Random Forest (200 trees, `class_weight="balanced"` so the small bucket is not ignored entirely).

**Split:** by date, not by shuffling.

- Train: **938** cases, last training date **9 May 2025**.
- Test: **384** cases, first test date **12 May 2025**.

No case on the same calendar day is in both sets. The model never trains on a later date than it is tested on.

**Test accuracy: 91.7%** (384 cases).

| Bucket | Precision | Recall | Test cases |
|--------|----------:|-------:|-----------:|
| market_wide | 0.82 | 0.72 | 68 |
| stock_specific | 0.94 | 0.97 | 238 |
| unknown | 0.90 | 0.93 | 71 |
| volume_shock | 1.00 | 0.71 | 7 |

Precision means: when the model says this bucket, how often the rule agrees. Recall means: of the days the rule put in this bucket, how many the model found.

**What the model leaned on** (permutation importance: how much test accuracy falls if that clue is scrambled):

| Clue | Accuracy drop |
|------|---------------|
| Stock minus Nifty (`vs_nifty`) | 0.46 |
| That day’s return | 0.13 |
| 20-day volatility | 0.11 |
| Volume versus its average | 0.08 |
| The other clues | about 0 |

### The honest reading of 92%

The buckets are **defined from** the Nifty move, the gap versus Nifty, and the volume ratio. Those same numbers are also clues. A high score means the forest **learned our rule** and could apply it on later dates. It does **not** mean a person checked the news and confirmed the cause. Say this out loud if someone praises the accuracy. It is the most important sentence in the midterm.

Saved files:

- `models/rf_cause_v1.joblib`
- `data/results/ml_baseline_metrics.json`
- `data/cases/sample_explanations.json` (top three clues per case)

---

## 10. What is deliberately not in this midterm

| Piece | Why it is absent |
|-------|------------------|
| Groq chat agents (solo, team vote, debate) | Needs an API key and real model calls. Not run. No fake paragraphs were written. |
| Mystery score on every saved case file | The formula exists in code. It is not a finished result table yet. |
| Direction backtest (30-day and 90-day) | Needs the agent outputs. Not run. |
| News headlines attached to 2024 cases | Today’s headlines were not pasted onto old dates. That would be false. |

The website `app.py` can already show the real cases, charts, and clues. Agent and backtest pages stay empty until those steps are run.

---

## 11. Limits

- One price per day. Anything that happened in the morning versus the afternoon is invisible.
- The buckets are our rules, not a verified cause.
- One ticker (`TATAMOTORS.NS`) could not be downloaded.
- `volume_shock` has only 26 cases, and only 7 of them are in the test set.
- High accuracy is mostly “the model copied the rule,” which is useful as a check that the pipeline works, and weak as a scientific claim about causes.
- This is not advice to buy or sell.

---

## 12. What the second half will add

1. Call Groq three ways on the same real cases: one analyst, a team vote, and a team that debates.
2. Cache every reply so a rerun does not invent a new answer.
3. Score whether the stated direction matched the later 30-day and 90-day move. Frame that as “did the explanation’s direction match,” not “we beat the market.”
4. Show the comparison in the Streamlit app.

---

## 13. How to reproduce

From the project folder:

```powershell
python run_pipeline.py --steps 1-6
```

That downloads, cleans, finds cases, draws charts, builds clues, and trains the forest. Steps 7 and 8 are the second half and are not part of these results.
