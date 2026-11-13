# MarketForensics — End-term report

**Project:** Explain unusual daily jumps in Indian (NSE) stocks  
**Course work:** BCA, third year. Mid Term Seminar (IP101), then the finished pipeline.  
**Student name:** ____________________  
**Enrollment number:** ____________________  
**College:** ____________________  
**Project guide:** ____________________  
**Date:** 8 November 2026  

**Disclaimer:** Educational research. Not financial advice. Not a trading system.

---

## 1. Abstract

Stock prices move every day. Sometimes one NSE stock moves much more than it usually does. This project does not try to guess tomorrow’s price. It takes a day that already happened and asks what kind of move it was: the whole market, that stock alone, a burst of trading, or none of those.

The program downloads real daily prices, cleans them onto the Nifty calendar, marks unusual days with a volatility rule, builds numeric clues from prices up to that day, and trains a Random Forest on older cases. On 381 later cases the forest scores **92.1%**. That score means the forest learned the labelling rule. It does not mean a person checked the news and confirmed the cause.

A second part asks a free chat model to write a short note on a case, in three designs: one analyst, a team vote, and a short debate. A direction check on the saved notes is small (about 5 to 14 cases). Debate does not clearly beat the solo note. The match rate is about 20%, and the interval is wide.

---

## 2. Introduction

Most student stock projects try to predict the next close. That question is easy to overclaim and hard to check honestly. A large candle on a chart is also easy to misread. It might be the market, the company, or just a busy trading day.

MarketForensics is a case file for unusual NSE days. One case is one stock on one date. The clues are numbers computed from prices on or before that date. The label is a written rule. A small website shows the case, the clues, and the model bucket. A separate dashboard shows the charts without calling a chat model.

Domain: finance and machine learning, on daily prices of large stocks listed on the NSE.

---

## 3. Problem statement

**When an NSE stock has an unusually large daily move, can simple price-and-volume clues say whether that move looks market-wide, stock-specific, a volume spike, or unclear?**

This is a sorting question about the past. It is not “should I buy?”

A fixed cutoff such as “any day over 3%” is unfair. A jumpy stock crosses 3% often. A calm stock almost never does. The cutoff in this project depends on that stock’s own recent volatility.

---

## 4. Objectives

1. Download real daily NSE prices and clean them without inventing missing closes.
2. Mark a day as unusual only when the move is large versus that stock’s own last 20 days.
3. Build clues using only prices on or before the case day.
4. Label each case with a written rule, then test a Random Forest on later dates only.
5. Show one case in a Streamlit page, and show the charts on a separate dashboard.
6. Ask a free chat model for a written note in three designs, cache every reply, and check whether the stated direction matched the later move. Report a match rate, not a profit.

---

## 5. Literature

| S.no. | Work | Year | What it contributes | Limit for this project |
|------:|------|-----:|---------------------|------------------------|
| 1 | Fama, Fisher, Jensen and Roll, price adjustment to new information | 1969 | A large price change can be studied as an event | They start from a known event. This project starts from the jump. |
| 2 | MacKinlay, event studies in economics and finance | 1997 | The standard event-study method | Made for a research event, not a four-way student label. |
| 3 | Ribeiro, Singh and Guestrin, LIME | 2016 | Which inputs pushed a model’s answer | Explains the model. It does not prove the real-world cause. |
| 4 | Lundberg and Lee, SHAP | 2017 | Splits a prediction across features | Not used for the reported score. Same limit as LIME. |
| 5 | Du, Li, Torralba, Tenenbaum and Mordatch, multi-agent debate | 2023 | Several model roles argue, then one answer is written | Needs an API. The scored sample here is small. |

---

## 6. Words used in the report

| Word | Plain meaning |
|------|----------------|
| NSE | India’s main stock exchange. Prices come from there through Yahoo Finance. |
| Ticker | Short code. `RELIANCE.NS` is Reliance on the NSE. |
| Nifty | The market basket. Saved as `NSEI.csv` from `^NSEI`. |
| Return | Percent change from yesterday’s close to today’s close. |
| Volatility | How jumpy recent returns have been. |
| Case | One unusual day for one stock. |
| Clue | A number computed from prices up to that day. |
| Label | The bucket from a written rule. |
| Leakage | Using information from after the event. This project keeps that out of the model. |

---

## 7. Data

- **Source:** Yahoo Finance daily bars, adjusted for splits and dividends (`auto_adjust=True`).
- **Start requested:** 1 January 2022.
- **Kept:** 31 NSE stocks plus the Nifty index.
- **Span:** from 3 January 2022 into October 2026. The cleaned Reliance file has about 1,179 trading days.
- **`TATAMOTORS.NS` failed.** Yahoo returned no quote. It was skipped and listed in `data/raw/download_failures.json`.

Cleaning rules:

1. Drop duplicate dates.
2. Drop rows with a missing or non-positive close.
3. Keep only dates that exist on the Nifty calendar.
4. Do not fill a missing price with the previous close. Filling would invent a return.

Raw files are in `data/raw/`. Aligned files are in `data/processed/`. Row counts are in `data/DATA_README.md`.

---

## 8. Method

The pipeline is one command, `python run_pipeline.py`, in eight steps. If a step’s input is missing, it stops and prints the command that creates it. It does not invent prices, labels, or agent text.

### Step 1 — Download

`yfinance` saves one CSV and a small metadata JSON per ticker.

### Step 2 — Clean

Prices are aligned to the Nifty trading calendar. Missing closes are dropped.

### Step 3 — Find cases

> A day is a case if the absolute return is at least **2.5 times** the standard deviation of the previous 20 daily returns.

The 20-day window is shifted back by one day, so today’s return is not inside the measure of “normal” it is compared with.

Result: **1,334 cases** across **31 stocks**.

### Step 4 — Charts

Saved under `data/plots/eda/`:

- Reliance close and volume
- Reliance daily-return histogram
- Reliance versus Nifty, both restarted at 100
- Cases per stock
- Cases by month
- A return-versus-volume heatmap

### Step 5 — Clues

Each clue uses only prices on or before the case day.

| Clue | Meaning |
|------|---------|
| `return_pct` | That day’s percent move |
| `return_5d` / `momentum_5d` | Move over the last 5 trading days |
| `vol_20` | How jumpy the last 20 days were |
| `volume_vs_avg20` | Today’s volume divided by the average of the last 20 days |
| `ma_20` | 20-day average price |
| `above_ma` | 1 if the close is above that average, else 0 |
| `vs_nifty` | Stock return minus Nifty return the same day |
| `nifty_return_pct` | What the market itself did |
| `dow` | Day of the week, as a number |

Saved as `data/features/case_features.csv`.

The days after the jump are saved in `data/cases/case_windows.csv` so a person can look. Those “after” numbers are not given to the model.

### Step 6 — Labels and Random Forest

The buckets are rules, not a news desk’s verdict. First match wins.

1. **market_wide** — the absolute Nifty return is at least 1.5%.
2. **stock_specific** — the stock differs from Nifty by at least 2.0 percentage points.
3. **volume_shock** — volume is at least 2.0 times its 20-day average.
4. **unknown** — none of the above.

The model is a Random Forest with 200 trees and `class_weight="balanced"`, so the small bucket is not ignored entirely. The split is by date, not by shuffling. No case on the same calendar day is in both the train set and the test set.

- Train: **953** cases, last date **10 June 2025**.
- Test: **381** cases, first date **11 June 2025**.

The fitted model is `models/rf_cause_v1.joblib`. Metrics are `data/results/ml_baseline_metrics.json`.

### Step 7 — Written notes

Three designs read the same case JSON:

| Version | What it does |
|---------|----------------|
| A, solo | One analyst writes the note. |
| B, team | Three roles (numbers, news, skeptic) answer separately. A majority vote is kept. |
| C, debate | The same three roles see each other, answer again, and a chair writes the final note. |

Each reply must be JSON with `explanation`, `cause`, `confidence`, and `direction` (`up`, `down`, or `unclear`). A reply that is not that JSON is retried. It is not replaced with a handwritten answer. Replies are cached on disk, so a rerun does not invent a new paragraph.

The first saved notes were Groq calls. Groq’s free daily token cap then blocked new calls. New investigations use **Gemini’s free tier** (`gemini-2.5-flash`) when `GEMINI_API_KEY` is set in `.env`. Saved notes still open with no key.

### Step 8 — Direction check

After a note names a direction, the check asks whether the next trading day on or after 30 calendar days moved the same way. The same question is defined for 90 days. This file’s 90-day column is empty, so no 90-day rate is reported. This is not a portfolio and not a claim of beating the market.

A mystery score, in `src/marketforensics/mystery.py`, subtracts a capped share explained by the same-day Nifty move and by above-average volume from 100. It is a formula, not a verified cause.

---

## 9. System design

```text
Yahoo Finance → data/raw CSV → cleaned prices → all_cases.csv
      → case_features.csv → rule labels → Random Forest → Streamlit
                                      ↘ Gemini or cached notes → direction check
```

Two screens:

- `streamlit run app.py` — cases, one-day detail, model lab, agents, debate, backtest.
- `streamlit run dashboard.py` — charts and the forest score only. It does not call Gemini or Groq.

There is no class diagram. The system is this pipeline.

---

## 10. Tools

| Tool | Role |
|------|------|
| Python | Language for the pipeline and both screens |
| pandas, NumPy | Tables and returns |
| yfinance | Yahoo Finance download |
| Matplotlib | Saved charts in `data/plots/eda/` |
| Plotly, Streamlit | The case page and the dashboard |
| scikit-learn | Random Forest |
| joblib | Saves the forest |
| requests | Calls Gemini’s free HTTP API |
| VS Code | Editor |

---

## 11. Results

### 11.1 What the charts show

From `notes/eda_findings.md`:

- **1,334** unusual days across **31** stocks.
- Titan (`TITAN.NS`) has the most cases: **51**.
- The busiest month is **January 2025**, with **47** cases. Cases are spread from 2022 to 2026, not one crash month.
- The median absolute move on a case is **3.67%**.
- On **98%** of cases, the stock’s absolute move was larger than Nifty’s move that day.
- Largest rise in the cleaned files: **+10.63%** (Bajaj Finance).
- Largest fall: **−15.45%** (NTPC).

The Reliance histogram shows that most ordinary days sit near 0%, roughly between −2% and +2%. That is why a single 3% rule is a poor cutoff. The Reliance-versus-Nifty chart, both restarted at 100, is the picture behind the `vs_nifty` clue: when the stock line leaves the index line, the day is not just “the market moved.”

Label counts on all 1,334 cases:

| Bucket | Cases |
|--------|------:|
| stock_specific | 765 |
| market_wide | 352 |
| unknown | 191 |
| volume_shock | 26 |

`volume_shock` is a small group. Sentences about that bucket stay cautious.

### 11.2 Random Forest on later dates

**Test accuracy: 92.1%** (381 cases).

| Bucket | Precision | Recall | Test cases |
|--------|----------:|-------:|-----------:|
| market_wide | 0.77 | 0.70 | 57 |
| stock_specific | 0.95 | 0.97 | 245 |
| unknown | 0.92 | 0.94 | 72 |
| volume_shock | 1.00 | 0.71 | 7 |

Precision: when the model says this bucket, how often the rule agrees. Recall: of the days the rule put in this bucket, how many the model found.

Permutation importance on the test set (how much accuracy falls if that clue is scrambled):

| Clue | Accuracy drop |
|------|---------------|
| Stock minus Nifty (`vs_nifty`) | 0.46 |
| That day’s return | 0.15 |
| 20-day volatility | 0.14 |
| Volume versus its average | 0.09 |
| The other clues | about 0 |

### The honest reading of 92.1%

The buckets are defined from the Nifty move, the gap versus Nifty, and the volume ratio. Those same numbers are also clues. A high score means the forest learned the rule and applied it on later dates. It does **not** mean a news report confirmed the cause. This is the most important sentence in the project.

### 11.3 Written notes and the direction check

The scored notes are a pilot, not a full pass over all 1,334 cases. From `data/reports/backtest_summary.md`:

| Version | 30-day direction match | 95% interval | High-vol 30-day | Low-vol 30-day |
|---------|------------------------|--------------|-----------------|----------------|
| A, solo | 3 of 14 (21%) | 8% to 48% | 29% (n=7) | 14% (n=7) |
| B, team | 1 of 5 (20%) | 4% to 62% | 0% (n=3) | 50% (n=2) |
| C, debate | 3 of 13 (23%) | 8% to 50% | 29% (n=7) | 17% (n=6) |

Debate is not clearly better than the solo note. The intervals overlap, and version B has only five scored calls. No 90-day match rate is reported, because that column is empty in the saved summary.

Mean 30-day return after an “up” call was negative in the saved file (about −5.8% for A, −3.8% for B, −5.4% for C). A small p-value on A and C does not mean the method beat the market. The samples of “up” calls are 8, 2, and 7.

---

## 12. What was completed

| S.no. | Module | Status |
|------:|--------|--------|
| 1 | Problem definition | Completed |
| 2 | Download and cleaning | Completed |
| 3 | Case detection and charts | Completed |
| 4 | Features and labels | Completed |
| 5 | Random Forest, date split, saved model | Completed |
| 6 | Streamlit case viewer | Completed |
| 7 | Separate chart dashboard | Completed |
| 8 | Written notes (A, B, C), cached | Pilot completed; Gemini is the free path for new calls |
| 9 | 30-day direction check | Completed on the small saved sample |
| 10 | 90-day direction check | Not reported; the saved summary has no 90-day rate |

---

## 13. How to reproduce

From `C:\Users\shivangi\Projects\marketforensics`:

```powershell
python -m pip install -r requirements.txt
copy .env.example .env
python run_pipeline.py --steps 1-6
streamlit run dashboard.py
streamlit run app.py
```

Steps 1–6 do not need an API key. They download, clean, find cases, draw charts, build clues, and train the forest.

For one new written note, put a free Gemini key in `.env`:

```text
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_key
GEMINI_MODEL=gemini-2.5-flash
```

The key is created at https://aistudio.google.com/apikey . Then:

```powershell
python run_pipeline.py --steps 7 --ticker RELIANCE.NS --date 2024-06-04
python run_pipeline.py --steps 8
```

The Agents page in `app.py` has the same **Run investigation** button. Saved notes open even when the key is empty.

---

## 14. Limits

- One price per day. Morning versus afternoon is invisible.
- The buckets are our rules, not a verified cause.
- Tata Motors could not be downloaded.
- `volume_shock` has 26 cases, and only 7 of them are in the test set.
- 92.1% is the forest copying the rule. It is a check that the pipeline works. It is a weak claim about real causes.
- Many news prompts see an empty headline list, because a headline is attached only when its date is real.
- The direction check has 5 to 14 calls per version. The interval is too wide to rank A, B, and C.
- Chat-model text can still be wrong.
- This is not advice to buy or sell.

---

## 15. Conclusion

The end-to-end pipeline runs on real NSE prices. It finds 1,334 unusual days with a rule that respects each stock’s own volatility, builds clues without using the future, and scores a Random Forest at 92.1% on 381 later cases. The useful reading of that number is that the forest learned the labelling rule, and that the clue it depends on is the stock’s return minus Nifty.

The written notes are the honest second result: on a small cached sample, a debate does not beat a single analyst at naming the later 30-day direction. Both sit near 20%. That is a description of these cases, not a trading profit.

The project’s value is a case file that separates a market-wide day from a stock-specific day, shows the charts, and states what is still unexplained.

---

## 16. References

[1] E. F. Fama, L. Fisher, M. C. Jensen, and R. Roll, "The adjustment of stock prices to new information," Int. Econ. Rev., vol. 10, no. 1, pp. 1–21, Feb. 1969.

[2] A. C. MacKinlay, "Event studies in economics and finance," J. Econ. Lit., vol. 35, no. 1, pp. 13–39, Mar. 1997.

[3] M. T. Ribeiro, S. Singh, and C. Guestrin, "Why should I trust you?: Explaining the predictions of any classifier," in Proc. 22nd ACM SIGKDD, 2016, pp. 1135–1144.

[4] S. M. Lundberg and S. Lee, "A unified approach to interpreting model predictions," in Proc. Adv. Neural Inf. Process. Syst., 2017, pp. 4765–4774.

[5] Y. Du, S. Li, A. Torralba, J. B. Tenenbaum, and I. Mordatch, "Improving factuality and reasoning in language models through multiagent debate," arXiv:2305.14325, 2023.

[6] F. Pedregosa et al., "Scikit-learn: Machine learning in Python," J. Mach. Learn. Res., vol. 12, pp. 2825–2830, 2011.

[7] R. Aroussi, "yfinance: Yahoo! Finance market data downloader," GitHub, 2024. [Online]. Available: https://github.com/ranaroussi/yfinance
