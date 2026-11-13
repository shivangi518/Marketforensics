# Stage 01 — Market data (VS Code)

## Goal
Download **real** NSE stock price history (default **RELIANCE.NS**), save it, plot it, and compute returns.
Nifty 50 index ticker is **^NSEI**.
This is how a data scientist starts: real data → saved file → inspect → measure change.

## Honest note about “real-time”
- You download **real market history** (daily prices from Yahoo Finance).
- This is **not** live second-by-second trading data.
- Professional research and forensic analysis almost always start with daily history.
- Live streaming can come much later; it is not needed for a scientific Phase 1.

## Words to know

| Word | Simple meaning |
|------|----------------|
| Ticker | Stock symbol, e.g. `AAPL` = Apple |
| OHLCV | Open, High, Low, Close, Volume |
| Open | Price at market open that day |
| Close | Price at market close that day |
| Volume | How many shares were traded |
| Return | Percent change from yesterday’s close to today’s close |
| CSV | Table saved as a text file |
| Metadata | A small “receipt” of when/how you downloaded the data |

## VS Code setup (one time)

1. Open folder: `C:\Users\shivangi\Projects\marketforensics`
2. Terminal → New Terminal
3. Install packages — pick **one** option:

**(A) With `.venv` (recommended)** — keeps project packages isolated from other Python work:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Then in VS Code: `Ctrl+Shift+P` → **Python: Select Interpreter** → choose `.venv\Scripts\python.exe`

**(B) Without `.venv` (allowed for learning)** — installs into your system Python. Fine for this internship path; later projects can clash if they need different package versions:

```powershell
python -m pip install -r requirements.txt
```

(If `python` is not found, try `py -m pip install -r requirements.txt`.)

## Run Phase 1

**(A)** Activate first, then run:

```powershell
.\.venv\Scripts\Activate.ps1
python scripts/stage01_01_download_prices.py
python scripts/stage01_02_plot_close.py
python scripts/stage01_03_compute_returns.py
```

**(B)** No activate — just run with system Python:

```powershell
python scripts/stage01_01_download_prices.py
python scripts/stage01_02_plot_close.py
python scripts/stage01_03_compute_returns.py
```


## What success looks like

- [ ] `data/raw/AAPL.csv` exists (open it and look at rows)
- [ ] `data/raw/AAPL_meta.json` exists (your download receipt)
- [ ] `data/plots/AAPL_close.png` exists
- [ ] `data/processed/AAPL_returns.csv` exists
- [ ] You can explain Open / Close / Volume / Return in your own words
- [ ] Notes filled in `notes/stage01.md`

## Why this is scientific (not random)

1. **Real data** from a public market source
2. **Saved to disk** so results are repeatable
3. **Metadata JSON** records when/how you got the data
4. **Adjusted prices** so splits/dividends don’t fake huge jumps
5. **Returns** turn prices into comparable day-to-day changes

## Next
`stage02_big_moves/README.md`
