# MarketForensics

Explain unusual NSE price jumps with prices, a simple model, and three Groq report designs.

Educational research. Not financial advice.

## Public website

The production-style Flask website reads the saved pipeline files directly:

```powershell
cd C:\Users\shivangi\Projects\marketforensics
python -m pip install -r requirements.txt
python website\refresh_market_strip.py
python website\app.py
```

Open `http://127.0.0.1:5001`.

The refresh command writes real delayed Nifty, Sensex, S&P 500, Nasdaq, and
BTC closes from Yahoo Finance. The Streamlit application remains available as
an internal analysis tool.

## Run

```powershell
cd C:\Users\shivangi\Projects\marketforensics
python -m pip install -r requirements.txt
copy .env.example .env
```

Put your Groq key in `.env` before step 7. Steps 1–6 do not call Groq.

```powershell
python run_pipeline.py --steps 1-6
python run_pipeline.py --steps 7 --n 50
python run_pipeline.py --steps 8
streamlit run app.py
```

Or everything, once the key is set:

```powershell
python run_pipeline.py --all --n 50
```

One case only:

```powershell
python run_pipeline.py --steps 7 --ticker RELIANCE.NS --date 2024-06-04
```

The app has the same action on the Agents page (**Run investigation**).

## What each step writes

| Step | Command | Output |
|------|---------|--------|
| 1 | `--steps 1` | `data/raw/TICKER.csv` and `*_meta.json` (`NSEI.csv` for `^NSEI`) |
| 2 | `--steps 2` | `data/processed/TICKER.csv`, `data/DATA_README.md` |
| 3 | `--steps 3` | `data/cases/all_cases.csv`, `case_windows.csv` |
| 4 | `--steps 4` | `data/plots/eda/`, `data/reports/universe_profile.md`, `notes/eda_findings.md` |
| 5 | `--steps 5` | `data/features/case_features.csv` |
| 6 | `--steps 6` | `models/rf_cause_v1.joblib`, `data/results/ml_baseline_metrics.json`, `data/cases/sample_explanations.json` |
| 7 | `--steps 7 --n 50` | `data/cases/json/`, `data/agent_cache/`, `data/results/version_a\|b\|c/` |
| 8 | `--steps 8` | `data/reports/backtest_summary.md`, `data/results/backtest_summary.json`, `docs/MarketForensics_Report.md` |

If a step's input is missing, it stops and prints the command that creates it. It does not invent prices, labels, or agent text.

## Rule of the project

A case uses only prices up to that day. The forest trains on older cases and is scored on newer ones. Agent text comes from Groq, cached on disk.
