# 1. Title block

**PROJECT TITLE**  
MarketForensics: Explaining Unusual Daily Price Jumps in NSE Stocks

**Presented by**  
Name: ____________________  
Enroll. no.: ____________________  
Date: 8 November 2026

**Project Faculty Mentor**  
Name: ____________________  
Designation: ____________________  
Dept.: Computer Science and Engineering

**Mid Term Seminar (IP101)**

This write-up follows the seminar outline and covers the project from the first price download through the direction check. It is educational research. It is not financial advice, and it is not a trading system.

---

# 2. Introduction — Background

The domain of this project is finance, on daily prices of large stocks listed on the National Stock Exchange of India (NSE). A ticker such as `RELIANCE.NS` is the Yahoo Finance code for that stock on the NSE. The Nifty index, stored in this project as `NSEI.csv` from the Yahoo symbol `^NSEI`, stands for the market as a whole. Each row of a price file is one trading day: open, high, low, close, and volume. The return is the percent change from yesterday’s close to today’s close.

Prices move on ordinary days. Sometimes one stock moves much more than it has moved in its own recent past. A reader of a chart can easily treat that candle as “news about the company.” The same candle can also be the whole market moving, a burst of trading, or a day that the price numbers do not explain. Most student stock projects try to guess the next close. That question is easy to overclaim. This project takes a day that already happened and asks what kind of move it was.

The topic matters because a large daily jump is a real event in the price record, and a fixed cutoff such as “any day over 3%” treats a calm stock and a jumpy stock as if they were the same. A case file that uses each stock’s own recent volatility, keeps future prices out of the clues, and says plainly what the score does and does not mean is a more honest piece of coursework than a forecast with no check.

MarketForensics is that case file. One case is one stock on one date. The clues are numbers computed from prices on or before that date. The label is a written rule. A small website shows one case. A separate dashboard shows the charts without calling a chat model. A later step asks a free chat model for a short written note and checks whether the stated direction matched the later move.

---

# 3. Introduction — Problem statement, project objectives, and expected outcome

## Problem statement

When an NSE stock has an unusually large daily move, can simple price-and-volume clues say whether that move looks market-wide, stock-specific, a volume spike, or unclear?

This is a sorting question about the past. The four buckets are names for patterns in the price record. They are assigned by a written rule in this project. They are not a news desk’s verdict, and the question is not “should I buy?”

## Project objectives

1. Download real daily NSE prices and clean them without inventing a missing close.
2. Mark a day as unusual only when the move is large versus that stock’s own last 20 days.
3. Draw charts of the prices, the returns, and the cases.
4. Build clues using only prices on or before the case day.
5. Label each case with a written rule, then test a Random Forest on later dates only.
6. Show the charts on a dashboard that does not call an API, and show one case in a full Streamlit app.
7. Ask a free chat model for a written note in three designs, save every reply, and check whether the stated direction matched the later 30-day move. Report a match rate. The check is not a trading profit.

## Expected outcome

The finished work is a pipeline a reader can run, a set of unusual days with charts and clues, a forest score on later cases with an honest reading of that score, two screens (dashboard and full app), and a small direction check on saved notes. The useful outcome is a case file that separates a market-wide day from a stock-specific day and states what is still unexplained.

---

# 4. Literature Survey

| S.no. | Title / system | Author / source | Year | What it does | Limitation |
|------:|----------------|-----------------|-----:|--------------|------------|
| 1 | The adjustment of stock prices to new information | E. F. Fama, L. Fisher, M. C. Jensen, and R. Roll | 1969 | Studies a large price change as an event after new information | They start from a known event. This project starts from the jump and then tries to describe it. |
| 2 | Event studies in economics and finance | A. C. MacKinlay | 1997 | Sets out the standard event-study method used in finance | The method is built for a research event with a defined window. It is not a four-way student label on daily bars. |
| 3 | LIME (“Why should I trust you?”) | M. T. Ribeiro, S. Singh, and C. Guestrin | 2016 | Shows which inputs pushed a classifier’s answer | It explains the model. It does not prove the real-world cause of a price jump. |
| 4 | SHAP | S. M. Lundberg and S. Lee | 2017 | Splits one prediction across the input features | The reported score in this project uses permutation importance, not a SHAP table. The same limit remains: a feature split is not a confirmed cause. |
| 5 | Improving factuality and reasoning through multi-agent debate | Y. Du, S. Li, A. Torralba, J. B. Tenenbaum, and I. Mordatch | 2023 | Lets several model roles argue, then writes one answer | It needs an API. The scored sample in this project is small, so the debate result stays cautious. |

---

# 5. Methodology

## Proposed solution

The program does not forecast the next close. It builds a case for a day that already happened. Prices come from Yahoo Finance. A volatility rule marks unusual days. Each day becomes a short list of clues. A written rule assigns one of four labels. A Random Forest learns that rule on older cases and is checked on later cases. Charts and one case are shown in Streamlit. After that, three designs of a written note are cached, and a direction check asks whether the note’s stated direction matched the later move.

The pipeline stops if an input file is missing and prints the command that creates it. It does not invent prices, labels, or agent text.

## The seven-step flow

**1. Download.**  
`yfinance` saves one CSV and a small metadata file per ticker. The request starts on 1 January 2022. Prices are daily bars, adjusted for splits and dividends (`auto_adjust=True`). The kept set is 31 NSE stocks plus the Nifty index. `TATAMOTORS.NS` had no Yahoo quote and was skipped. The failure is listed in `data/raw/download_failures.json`.

**2. Clean.**  
Duplicate dates are dropped. Rows with a missing or non-positive close are dropped. Only dates that exist on the Nifty calendar are kept. A missing price is not filled with the previous close. There is no forward-fill, because a filled close would invent a return. Aligned files are in `data/processed/`. The cleaned Reliance file has about 1,179 trading days, from 3 January 2022 through early October 2026.

**3. Find cases.**  
A day is a case when the absolute return is at least 2.5 times the standard deviation of the previous 20 daily returns. The 20-day window is shifted back by one day, so today’s return is not inside the measure of “normal” it is compared with. A jumpy stock and a calm stock therefore do not share one fixed percent cutoff. The run on disk found **1,334** unusual days across **31** stocks.

**4. Charts.**  
Matplotlib saves the exploratory charts under `data/plots/eda/`: Reliance close and volume, a histogram of Reliance daily returns, Reliance versus Nifty with both lines restarted at 100, cases per stock, cases by month, and a heatmap of returns against volume changes. Short notes from those charts are in `notes/eda_findings.md`.

**5. Clues.**  
Each clue uses only prices on or before the case day. The table is saved as `data/features/case_features.csv`.

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

The days after the jump are saved in `data/cases/case_windows.csv` so a person can look at context. Those “after” numbers are not given to the model.

**6. Forest.**  
Labels are assigned by the rule in the next section. A Random Forest with 200 trees and `class_weight="balanced"` is trained on older cases and tested on later cases. The fitted model is `models/rf_cause_v1.joblib`.

**7. App.**  
The chart screen is `streamlit run dashboard.py`. It does not call an API. The full case screen is `streamlit run app.py`. The full app can show a case, the clues, the forest bucket, cached written notes, and the direction-check page.

## The 2.5× volatility case rule

A fixed rule such as “any day over 3%” is unfair. A jumpy stock crosses 3% often. A calm stock almost never does. The rule used here is:

> A day is a case if the absolute return is at least **2.5 times** the standard deviation of the previous 20 daily returns.

The window is shifted by one day so the event return is not inside its own baseline.

## Tools and data

| Tool | Role in this project |
|------|----------------------|
| Python | Language for the pipeline and both screens |
| pandas, NumPy | Price tables and returns |
| yfinance | Download of Yahoo Finance daily bars |
| Matplotlib | Saved charts in `data/plots/eda/` |
| scikit-learn | Random Forest |
| joblib | Saves the fitted forest |
| Streamlit, Plotly | Dashboard and full app |
| requests | New written-note calls to Gemini’s free HTTP API |

**Data.** Yahoo Finance daily bars, start requested 1 January 2022, about 1,179 trading days for Reliance, through early October 2026. Thirty-one stocks were kept. `TATAMOTORS.NS` was skipped because Yahoo returned no quote. Cleaning does not forward-fill.

**Written notes, after the seven steps.** Three designs read the same case. Version A is one analyst. Version B is three roles (numbers, news, skeptic) with a majority vote. Version C is the same three roles, a short rebuttal, and a chair who writes the final note. Each reply is asked for as JSON with an explanation, a cause, a confidence, and a direction (`up`, `down`, or `unclear`). A reply that is not that JSON is retried. It is not replaced with a handwritten answer. Replies are cached on disk.

New agent calls use the Gemini free tier (`gemini-2.5-flash`) because Groq’s free daily limit was exceeded. The notes already saved on disk are from earlier Groq calls. Those saved notes still open when no key is set.

---

# 6. System Design

There is no class diagram. The system is a pipeline of files.

```text
Yahoo Finance
    → data/raw CSV
    → cleaned prices (Nifty calendar, no forward-fill)
    → all_cases.csv
    → case_features.csv
    → rule labels
    → Random Forest
    → dashboard.py (charts only, no API)
    → app.py (case, clues, forest, cached notes)
              ↘ saved notes (earlier Groq; new calls use Gemini)
                  → 30-day direction check
```

## Design logic for the labels

The buckets are rules written in this project. The first matching rule wins.

1. **market_wide** — the absolute Nifty return that day is at least 1.5%.
2. **stock_specific** — the stock’s return differs from Nifty by at least 2.0 percentage points.
3. **volume_shock** — volume is at least 2.0 times its 20-day average.
4. **unknown** — none of the above.

Counts on all 1,334 cases:

| Label | Cases |
|-------|------:|
| stock_specific | 765 |
| market_wide | 352 |
| unknown | 191 |
| volume_shock | 26 |

`volume_shock` is a small group. Any sentence about that bucket stays cautious. The same numbers that define the labels (`vs_nifty`, the day’s return, volume versus its average) are also clues. That fact is part of the design, and it is why the accuracy sentence in the next section is worded the way it is.

A mystery score, in `src/marketforensics/mystery.py`, starts at 100 and subtracts a capped share explained by the same-day Nifty move and by above-average volume. It is a formula on the clues. It is not a verified cause.

## Design logic for the date split

The forest is not trained by shuffling rows. It is split by date, so the model learns on older cases and is scored on later cases. No case on the same calendar day sits in both sets.

- Train: **953** cases, through **10 June 2025**.
- Test: **381** cases, starting **11 June 2025**.

Clues stop on the case day. Prices after the jump are stored for a person to read and are withheld from the forest. The direction check looks forward only after a note has already named a direction, and that forward return is not a training feature.

## Two screens

- `streamlit run dashboard.py` — charts and the forest score. No API call.
- `streamlit run app.py` — the full app: cases, one-day detail, the model, cached notes, and the direction check.

---

# 7. Implementation and Results

## Modules done

| S.no. | Module | What is on disk |
|------:|--------|-----------------|
| 1 | Download and clean | Raw and processed CSVs; Tata Motors skipped |
| 2 | Cases | 1,334 unusual days, 31 stocks |
| 3 | Charts | `data/plots/eda/` and `notes/eda_findings.md` |
| 4 | Clues and labels | Feature table and the four rule buckets |
| 5 | Random Forest | `models/rf_cause_v1.joblib`, date split, test metrics |
| 6 | Dashboard | `streamlit run dashboard.py` (no API) |
| 7 | Full app | `streamlit run app.py` |
| 8 | Written notes | Versions A, B, and C cached; new calls use Gemini |
| 9 | Direction check | 30-day match on the small saved sample; 90-day column empty |

## Challenges

- `TATAMOTORS.NS` had no Yahoo quote and was skipped, so that name is absent from the 31 stocks.
- One row per day hides anything that happened in the morning versus the afternoon.
- The labels are the project’s own rules. A high forest score can mean the model copied the rule.
- `volume_shock` has 26 cases in the full set and 7 cases in the test set, so that class is thin.
- Groq’s free daily limit was exceeded. New agent calls use Gemini free tier (`gemini-2.5-flash`). The notes already saved, including the notes behind the direction check, are from earlier Groq calls.
- Many news prompts see an empty headline list, because a headline is attached only when its date is real.
- The direction-check sample is small, and the 90-day column in the saved summary is empty.

## What the charts show

From `notes/eda_findings.md`:

- **1,334** unusual days across **31** stocks.
- Titan (`TITAN.NS`) has the most cases: **51**.
- January 2025 has the most cases in one month: **47**. The cases are spread from 2022 through 2026.
- The median absolute move on a case is **3.67%**.
- On **98%** of cases, the stock moved more than Nifty that day (the stock’s absolute move was larger than Nifty’s absolute move).
- Largest rise in the cleaned files: **+10.63%** (`BAJFINANCE.NS`).
- Largest fall: **−15.45%** (`NTPC.NS`).

The Reliance histogram is the picture behind the case rule: ordinary days cluster near zero, so one fixed percent cutoff would mark too many days on a jumpy stock and too few on a calm one. The Reliance-versus-Nifty chart, both restarted at 100, is the picture behind `vs_nifty`. When the stock line leaves the index line, the day is not only “the market moved.”

## Random Forest on later cases

**Test accuracy: 92.1%** on **381** later cases. Training used **953** cases through **10 June 2025**. The test set starts **11 June 2025**.

| Bucket | Precision | Recall | Support (test cases) |
|--------|----------:|-------:|---------------------:|
| market_wide | 0.77 | 0.70 | 57 |
| stock_specific | 0.95 | 0.97 | 245 |
| unknown | 0.92 | 0.94 | 72 |
| volume_shock | 1.00 | 0.71 | 7 |

Precision means: when the model says this bucket, how often the rule agrees. Recall means: of the days the rule put in this bucket, how many the model found.

Permutation importance on the test set is the drop in accuracy when that clue is scrambled:

| Clue | Accuracy drop |
|------|---------------|
| `vs_nifty` | 0.46 |
| `return_pct` | 0.15 |
| `vol_20` | 0.14 |
| `volume_vs_avg20` | 0.09 |

The clue the forest leans on is the stock’s return minus the Nifty return.

## Honest reading of the accuracy

**92.1% means the forest learned the labelling rule. It does not mean a news report confirmed the cause.**

The buckets are defined from the Nifty move, the gap versus Nifty, and the volume ratio. Those same numbers are also clues. The score is a check that the pipeline applies the rule on later dates. It is a weak claim about real-world causes.

## Direction check on the saved notes

The question in `data/reports/backtest_summary.md` is: after a saved note named a direction, did the next trading day on or after 30 calendar days move the same way? The same question is defined for 90 days. The 90-day column in that file is empty, so no 90-day rate is reported.

These numbers come from the saved notes. Those notes were earlier Groq calls. They are not a Gemini result.

| Version | 30-day direction match | 95% interval |
|---------|------------------------|--------------|
| A, solo | 3 of 14 (21%) | 8% to 48% |
| B, team | 1 of 5 (20%) | 4% to 62% |
| C, debate | 3 of 13 (23%) | 8% to 50% |

Debate does not clearly beat solo. The intervals overlap, and version B has only five scored calls. This describes these cases only. It is not a trading profit.

---

# 8. Project Completion Timeline / Status

The work was done in this order. Status is what is finished on disk as of 8 November 2026.

| S.no. | Work | Status |
|------:|------|--------|
| 1 | Problem statement and objectives | Completed |
| 2 | Literature notes for the five papers above | Completed |
| 3 | Download from Yahoo Finance and cleaning with no forward-fill | Completed |
| 4 | Case rule (2.5× prior 20-day volatility) and charts | Completed |
| 5 | Clues and the four labels | Completed |
| 6 | Random Forest, date split, saved model | Completed |
| 7 | Dashboard: `streamlit run dashboard.py` | Completed |
| 8 | Full app: `streamlit run app.py` | Completed |
| 9 | Written notes, versions A, B, and C, cached | Pilot completed. Saved notes are earlier Groq calls. New calls use Gemini free tier (`gemini-2.5-flash`). |
| 10 | 30-day direction check | Completed on the small saved sample (A 14, B 5, C 13) |
| 11 | 90-day direction check | Not reported. The saved summary column is empty. |

Steps 1–6 of `python run_pipeline.py` do not need an API key. They download, clean, find cases, draw charts, build clues, and train the forest. A new written note needs `GEMINI_API_KEY` in `.env` with `LLM_PROVIDER=gemini` and `GEMINI_MODEL=gemini-2.5-flash`. Saved notes open when the key is empty.

---

# 9. References

[1] E. F. Fama, L. Fisher, M. C. Jensen, and R. Roll, "The adjustment of stock prices to new information," *Int. Econ. Rev.*, vol. 10, no. 1, pp. 1–21, Feb. 1969.

[2] A. C. MacKinlay, "Event studies in economics and finance," *J. Econ. Lit.*, vol. 35, no. 1, pp. 13–39, Mar. 1997.

[3] M. T. Ribeiro, S. Singh, and C. Guestrin, "Why should I trust you?: Explaining the predictions of any classifier," in *Proc. 22nd ACM SIGKDD Int. Conf. Knowl. Discovery Data Mining*, 2016, pp. 1135–1144.

[4] S. M. Lundberg and S. Lee, "A unified approach to interpreting model predictions," in *Proc. Adv. Neural Inf. Process. Syst.*, 2017, pp. 4765–4774.

[5] Y. Du, S. Li, A. Torralba, J. B. Tenenbaum, and I. Mordatch, "Improving factuality and reasoning in language models through multiagent debate," arXiv:2305.14325, 2023.

[6] F. Pedregosa *et al.*, "Scikit-learn: Machine learning in Python," *J. Mach. Learn. Res.*, vol. 12, pp. 2825–2830, 2011.

[7] R. Aroussi, "yfinance: Yahoo! Finance market data downloader," GitHub, 2024. [Online]. Available: https://github.com/ranaroussi/yfinance
