# MarketForensics — 2-Month Full Project Plan

**For:** 8GB laptop, zero AI/stock knowledge, includes data analytics + AI  
**Goal:** One outstanding project you can demo, put on GitHub, and explain to anyone

---

# PART 1 — Explain the project (use this with friends, teachers, interviewers)

## One sentence

> **When an Indian stock has a weird price jump, my app acts like a detective team: it collects clues, three AI helpers argue about why it happened, and it writes a case report — including what it still cannot explain.**

## What problem does it solve?

Stocks move every day. Sometimes they move **a lot** — up or down — and people ask: **“Why?”**

Was it:
- the whole market moving?
- news about that company?
- high trading volume?
- something we still don’t know?

Most student projects try to **predict tomorrow** (“buy or sell”). That is hard to prove and easy to fake.

**MarketForensics** explains **what already happened**, with evidence. That is more honest and more interesting.

## The story (remember this)

**Mia’s lemonade stand** = one stock (e.g. Reliance)  
**Weird jump day** = price moved much more than usual  
**Robo the dog** = your computer + AI  
**Detective team** = 3 AI roles that debate  
**Case file** = final report with clues + confidence + mystery %

## What makes it unique?

| Normal student project | Your project |
|------------------------|--------------|
| “Will price go up?” | “Why did it jump?” |
| One ChatGPT answer | Solo vs team vs debate (real experiment) |
| Always confident | Shows **mystery score** (honest about unknowns) |
| US stocks only | **NSE India** focus (Nifty 50) |
| No data work | Full **data analytics** pipeline first |

## The pipeline (8 steps — what actually runs)

```
STEP 1  Download real stock prices (30+ NSE stocks, 2–3 years)
   ↓
STEP 2  Clean data (missing days, bad rows, align dates)
   ↓
STEP 3  Find "weird jump" days → save as CASES
   ↓
STEP 4  Data analytics — charts, patterns, correlations
   ↓
STEP 5  Build CLUES from prices (features: volume, volatility, vs Nifty)
   ↓
STEP 6  Simple ML model guesses cause type + top reasons
   ↓
STEP 7  AI agents (Version A, B, C) write explanations
   ↓
STEP 8  Backtest + Streamlit app + short research write-up
```

## Three AI versions (the star of the demo)

| Version | Plain English |
|---------|----------------|
| **A — Solo** | One AI reads the clues and writes an explanation |
| **B — Team, no talk** | 3 AIs (numbers / news / risk) each give opinion → vote |
| **C — Team + debate** | Same 3 see each other → challenge → 4th AI writes final report |

**Research question:** Does debate (C) do better than solo (A) on hard days?

## What you deliver at the end

1. **GitHub repo** with all code  
2. **Data folder** with cleaned NSE prices  
3. **Case files** for hundreds of weird jump days  
4. **Charts** (EDA section)  
5. **ML model** + feature importance  
6. **Agent comparison** (A vs B vs C results table)  
7. **Streamlit app** — pick stock + date → see full case  
8. **5–10 page PDF** — mini research paper  

## How to explain in 30 seconds (interview script)

> “I built MarketForensics for Indian stocks. It detects days when a stock moved unusually, builds numeric clues like volume and volatility, and uses three designs of AI agents — solo, team vote, and team with debate — to explain why the move happened. I backtest on historical cases and report not just a guess but a confidence score and how much of the move is still unexplained. It’s educational research, not trading advice.”

## Disclaimer (always say this)

> “This is an educational research project. It is **not** financial advice and not a live trading system.”

---

# PART 2 — Words you must know (zero jargon dictionary)

| Word | Simple meaning |
|------|----------------|
| **Stock / share** | A small piece of a company you can buy |
| **NSE / BSE** | Indian stock exchanges (where prices come from) |
| **Ticker** | Short code, e.g. `RELIANCE.NS` on Yahoo Finance |
| **Nifty 50** | Index of 50 big Indian stocks — “the whole market” benchmark |
| **Open / High / Low / Close** | Price at start, highest, lowest, and end of the day |
| **Volume** | How many shares traded that day |
| **Return** | % change in price from yesterday to today |
| **Volatility** | How jumpy prices have been lately |
| **Weird jump / big move** | Return much larger than this stock’s normal jumpiness |
| **Case** | One weird jump day for one stock — your “crime file” |
| **Feature / clue** | A number the computer uses (e.g. “volume was 2× normal”) |
| **ML model** | Program that learns patterns from past examples |
| **LLM / AI agent** | Chat-style AI (Groq API) given a role via prompt |
| **Backtest** | Pretend you decided on day X, check what happened after using old data |
| **Mystery score** | % of the move your clues + AI still cannot explain |
| **EDA** | Exploratory Data Analysis — charts and questions before AI |
| **Leakage** | Accidentally using future data to explain the past (cheating) |

---

# PART 3 — What you need (8GB laptop setup)

## Software (all free)

- **Python 3.11+**
- **VS Code**
- **Libraries:** pandas, matplotlib, yfinance, scikit-learn, streamlit, requests
- **Groq API** (free tier) for AI agents — runs in cloud, saves your RAM
- **Git + GitHub** for portfolio

## Optional (skip if RAM tight)

- Ollama local LLM — only if Groq limits hit; use small model (3B)
- Deep learning (PyTorch) — optional Week 7 stretch goal
- FinBERT local — use API or simple sentiment instead

## Daily habit

1. Open today’s week section below  
2. Do the tasks  
3. Write 3 bullets in `notes/`  
4. Commit to GitHub when a week finishes  

**Time:** ~1.5–2 hours/day average (some weekends 3–4 hours)

---

# PART 4 — 8-WEEK (2-MONTH) PLAN — FULL BUILD

---

## WEEK 1 — Python + first real data

**Theme:** Learn to run code + download one stock

### Days 1–2: Python basics (Stage 00)
- [ ] Run `01_hello.py`, `02_variables.py`, `03_functions.py`
- [ ] Finish `04_mini_challenge.py`
- [ ] Fill `notes/stage00.md`

**You learn:** variables, lists, dictionaries, functions, saving a file

### Days 3–4: One stock end-to-end (Stage 01)
- [ ] `pip install -r requirements.txt` (no `.venv` OK)
- [ ] Run download, plot, returns scripts for `RELIANCE.NS`
- [ ] Open CSV — explain one row in your own words
- [ ] Hand-calculate one daily return
- [ ] Fill `notes/stage01.md`

**Deliverables:**
- `data/raw/RELIANCE.NS.csv`
- `data/plots/RELIANCE.NS_close.png`
- `data/processed/RELIANCE.NS_returns.csv`

### Days 5–7: Expand to Nifty 50 universe
- [ ] Create list of 30–50 tickers (start with Nifty 50, `.NS` suffix)
- [ ] Loop download script for all tickers
- [ ] Download `^NSEI` (Nifty index) as benchmark
- [ ] Add metadata JSON per ticker
- [ ] Basic clean: drop duplicate dates, handle missing rows
- [ ] Write `data/DATA_README.md` — what you downloaded, date range

**Deliverables:**
- `data/raw/*.csv` for 30+ stocks
- `data/raw/^NSEI.csv`
- Data quality note (how many rows, any gaps)

---

## WEEK 2 — Weird days + data analytics (EDA)

**Theme:** Find cases + prove you understand the data with charts

### Days 8–9: Big-move detector (Stage 02)
- [ ] Run/adapt `01_detect_big_moves.py` for each stock
- [ ] Rule: `|return| >= 2.5 × recent 20-day volatility`
- [ ] Run `02_build_case_windows.py` (±5 days around each case)
- [ ] Combine all cases into `data/cases/all_cases.csv`

**You learn:** threshold, event window, why volatility beats fixed “3%”

### Days 10–11: EDA charts (data analytics section)
Build these plots (save to `data/plots/eda/`):

- [ ] Price + volume twin chart (1 stock example)
- [ ] Histogram of daily returns (1 stock)
- [ ] Compare stock vs Nifty (% growth from 100)
- [ ] Count of big moves per stock (bar chart)
- [ ] Big moves by month (seasonality?)
- [ ] Correlation heatmap: return vs volume change (simple)

**Deliverables:**
- 6+ charts
- `notes/stage02.md` + `notes/eda_findings.md` (5 bullet insights)

### Days 12–14: Data profile report
- [ ] Script: `scripts/stage01_07_data_profile_report.py`
- [ ] For each stock: avg return, volatility, best/worst day, missing check
- [ ] Output: `data/reports/universe_profile.md`

**Week 2 done when:** You can show charts and say “here’s what I learned about NSE data before any AI.”

---

## WEEK 3 — Features + first ML

**Theme:** Turn prices into clues; first real AI

### Days 15–16: Feature engineering (Stage 03 prep)
For each case, compute clues **using only data before/on event day**:

- [ ] Daily return, 5-day return
- [ ] 20-day volatility
- [ ] Volume vs 20-day average volume
- [ ] 20-day moving average of price
- [ ] Price above/below moving average (trend)
- [ ] Simple RSI (or skip if too hard — use 5-day momentum instead)
- [ ] **Stock return minus Nifty return** (did stock move more than market?)
- [ ] Day of week

Save: `data/features/case_features.csv`

### Days 17–18: Labels (weak but OK for learning)
Assign rough cause buckets per case (rules-based first):

- [ ] `market_wide` — Nifty also moved a lot same day
- [ ] `stock_specific` — stock moved much more than Nifty
- [ ] `volume_shock` — volume very high
- [ ] `unknown` — none of above clear

**You learn:** features vs labels, no future leakage

### Days 19–21: Classical ML (Stage 03)
- [ ] Time-based train/test split (train on older dates, test on newer)
- [ ] Train Random Forest on features → predict cause bucket
- [ ] Print accuracy, confusion matrix
- [ ] Write `notes/stage03.md`: what worked, what failed

**Deliverables:**
- `models/rf_cause_v1.pkl` (or saved joblib)
- `data/results/ml_baseline_metrics.json`

---

## WEEK 4 — Explainability + news basics

**Theme:** “Which clues mattered?” + text evidence

### Days 22–23: Explainability (Stage 04)
- [ ] Feature importance (global)
- [ ] SHAP or permutation importance per case
- [ ] “Top 3 reasons” card for 10 sample cases
- [ ] Save: `data/cases/sample_explanations.json`

### Days 24–25: News / NLP light (Stage 05)
**8GB-friendly approach:**
- [ ] Use free news API or scraped headlines (Google News RSS / manual CSV for v1)
- [ ] Match headlines to case date ±1 day
- [ ] Simple relevance: keyword match on company name OR Groq “is this about this stock?”
- [ ] Optional: FinBERT sentiment via HuggingFace pipeline (small batches)

**Deliverables:**
- `data/news/` folder with headlines per case (start with top 50 cases)
- Case file includes 0–N headlines + relevance score

### Days 26–28: Case file schema v1
Define JSON structure for one case:

```json
{
  "ticker": "RELIANCE.NS",
  "date": "2024-03-15",
  "return_pct": 6.2,
  "features": { },
  "ml_cause_guess": "stock_specific",
  "top_clues": ["volume 2.1x avg", "beat Nifty by 4%"],
  "headlines": [],
  "mystery_score": null
}
```

- [ ] Build script to assemble case JSON from all prior steps
- [ ] Generate 20 example case files in `data/cases/json/`

---

## WEEK 5 — AI agents (Version A, B, C)

**Theme:** The impressive demo core

### Day 29: Groq setup
- [ ] Create free Groq account, get API key
- [ ] Store key in `.env` (never commit to GitHub)
- [ ] Test one simple prompt script
- [ ] **Cache every response** to `data/agent_cache/`

### Days 30–31: Version A — Solo agent
- [ ] Prompt: given case JSON clues → explain move + confidence 0–100% + cause category
- [ ] Run on 50 test cases (cached)
- [ ] Save outputs: `data/results/version_a/`

### Days 32–33: Version B — Team, no debate
Three personas (same model, different system prompts):
- [ ] **Fundamental/numbers analyst** — features, volume, vs market
- [ ] **News analyst** — headlines only
- [ ] **Risk/skeptic analyst** — “what could be wrong with this story?”
- [ ] Majority vote → final cause + confidence
- [ ] Run on same 50 cases

### Days 34–35: Version C — Team + debate
- [ ] Round 1: each persona independent (same as B)
- [ ] Round 2: each sees others’ answers, one rebuttal each
- [ ] **Chair agent** synthesizes final report
- [ ] Run on same 50 cases

**Deliverables:**
- All A/B/C outputs saved on disk
- Sample readable report for 3 cases (best demo material)

---

## WEEK 6 — Mystery score + backtesting

**Theme:** Honest science — what we still don’t know + did agents help?

### Days 36–37: Mystery score (Stage 07)
- [ ] `explained_pct` = how much of move is accounted for by Nifty move + volume clue strength (simple formula)
- [ ] `mystery_score` = 100 - explained_pct (cap sensibly)
- [ ] Add to every case JSON
- [ ] Write causal note template: “Likely X because Y; Z remains unclear”

### Days 38–40: Backtest engine
For each agent version on each test case:
- [ ] Record predicted direction (up/down cause sentiment)
- [ ] Check actual return 30 days and 90 days after (sanity check only)
- [ ] Win rate = % direction correct
- [ ] Compare A vs B vs C on:
  - all cases
  - high-volatility cases only
  - low-volatility cases only

### Days 41–42: Statistics (simple)
- [ ] Table: A vs B vs C — win rate, avg forward return when “bullish”
- [ ] Simple t-test or just confidence intervals in plain English
- [ ] Chart: bar chart comparing A/B/C win rates
- [ ] Write `notes/stage07.md` + `data/reports/backtest_summary.md`

**Important:** Frame as “did explanation quality / direction call improve?” not “we beat the market.”

---

## WEEK 7 — Deep learning (optional stretch) + polish

**Theme:** Optional extra + fix weak spots

### Days 43–44: Sequence model light (Stage 06 — optional)
**Skip entirely if tired — project is already complete without this.**

If doing:
- [ ] Use last 10 days of returns as input
- [ ] Small sklearn MLP or tiny PyTorch model
- [ ] Compare to Random Forest fairly
- [ ] Document: “DL did / did not beat baseline because…”

### Days 45–46: Fundamentals subset (optional)
- [ ] Add P/E or market cap for 10 large caps only (manual CSV or yfinance info)
- [ ] Merge into features for those stocks
- [ ] Note limitations in write-up

### Days 47–49: Code cleanup
- [ ] Move shared code into `src/marketforensics/`
- [ ] One command to rebuild cases: `python -m marketforensics.build_cases`
- [ ] Update main `README.md` with screenshots
- [ ] `.env.example` for Groq key

---

## WEEK 8 — Streamlit app + research write-up + portfolio

**Theme:** Ship it — what people actually see

### Days 50–52: Streamlit app (Stage 08)
Pages:
1. **Home** — project explanation (simple text)
2. **Pick a case** — dropdown: stock + date from case list
3. **Case view** — chart, clues table, ML guess, top 3 reasons
4. **Agents** — show A vs B vs C side by side
5. **Debate view** — Version C conversation formatted nicely
6. **Backtest** — A/B/C comparison chart
7. **About** — disclaimer + GitHub link

Run: `streamlit run app.py`

### Days 53–54: Research write-up (PDF or Markdown → PDF)
Sections:
1. **Problem** — why explain moves, not predict
2. **Related work** — 5–8 papers (event studies, XAI finance, multi-agent LLM)
3. **Method** — pipeline diagram, A/B/C design, data sources
4. **Results** — EDA findings, ML metrics, agent comparison, mystery scores
5. **Limitations** — daily data, weak labels, API limits, not trading advice
6. **Conclusion** — did debate help? what’s next?

Save: `docs/MarketForensics_Report.pdf`

### Days 55–56: Portfolio pack
- [ ] GitHub README with GIF or 3 screenshots
- [ ] 2-minute demo video (screen record Streamlit) — optional but powerful
- [ ] Resume bullet (copy from Part 1)
- [ ] LinkedIn post draft — optional

### Days 57–60: Buffer / catch-up
Use for anything unfinished. **Do not add new features.** Polish and practice explaining.

---

# PART 5 — Folder structure at end of 2 months

```
marketforensics/
├── app.py                          # Streamlit demo
├── README.md                       # Portfolio front page
├── PROJECT_TASKS.md
├── TWO_MONTH_PLAN.md               # this file
├── requirements.txt
├── .env.example
├── data/
│   ├── raw/                        # NSE CSVs
│   ├── processed/                  # returns
│   ├── cases/                      # big moves + JSON case files
│   ├── features/                   # case_features.csv
│   ├── plots/eda/                  # analytics charts
│   ├── reports/                    # profile + backtest summaries
│   ├── agent_cache/                # saved LLM responses
│   └── results/version_a|b|c/
├── models/                         # saved ML models
├── docs/
│   └── MarketForensics_Report.pdf
├── notes/                          # weekly learning logs
└── stage00 … stage08/              # learning scripts
```

---

# PART 6 — Weekly deliverables checklist

| Week | Must exist on disk |
|------|---------------------|
| 1 | 30+ stock CSVs, notes, one stock fully understood |
| 2 | `all_cases.csv`, 6+ EDA charts, EDA notes |
| 3 | `case_features.csv`, trained RF model, metrics |
| 4 | Top-3 explanations, news on 50 cases, case JSON schema |
| 5 | A/B/C agent outputs on 50 cases |
| 6 | Backtest table, mystery scores, comparison chart |
| 7 | Clean repo, optional DL/fundamentals |
| 8 | Streamlit app, PDF report, GitHub polished |

---

# PART 7 — How to explain each week to someone

| Week | Tell them |
|------|-----------|
| 1 | “I downloaded real NSE stock prices and learned what OHLCV means.” |
| 2 | “I found days when stocks jumped unusually and made charts to understand patterns.” |
| 3 | “I turned prices into numbered clues and trained my first ML model.” |
| 4 | “I showed which clues matter most and started attaching news to cases.” |
| 5 | “I built three AI designs — solo, team vote, and team debate — to explain moves.” |
| 6 | “I tested which design works better and added a mystery score for unexplained moves.” |
| 7 | “I cleaned the code and added optional extras.” |
| 8 | “I built a web demo and wrote a short research report.” |

---

# PART 8 — If you fall behind

**Priority order (cut from bottom if needed):**

1. ✅ Data + cases + EDA charts  
2. ✅ Features + Random Forest  
3. ✅ Version A + C agents (skip B if time tight)  
4. ✅ Streamlit + README  
5. ⚠️ Backtest stats (simple table OK)  
6. ⚠️ News NLP (can use 20 manual headlines)  
7. ❌ Deep learning (skip)  
8. ❌ Fundamentals for all stocks (skip)  

**Minimum impressive v1 in 6 weeks:** Weeks 1–6 + Streamlit only.

---

# PART 9 — Start tomorrow (Day 1)

```powershell
cd C:\Users\shivangi\Projects\marketforensics
python -m pip install -r requirements.txt
python stage00_python_basics/01_hello.py
```

Then follow Week 1 day by day above.

When Week 1 Day 3 starts, change ticker in download script to `RELIANCE.NS` and run Phase 1 scripts.

---

**You can do this on 8GB RAM.** Use Groq for AI. Go stage by stage. Honesty + a working demo beats a huge unfinished project.
