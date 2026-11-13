# MarketForensics — Full Intern Task List (All Phases)

**Manager rule:** Finish one phase. Get approval. Then unlock the next.  
**Do not skip ahead** to AI / agents until the earlier deliverables exist.

---

## Phase 1 plot (answer first)

You do **not** invent a fancy dashboard.

**Your only plot in Phase 1:**
- Line chart of **Apple closing price over time**
- Created by running: `python scripts/stage01_02_plot_close.py`
- Saved to: `data/plots/AAPL_close.png`

That is it. Later phases add more plots (big-move markers, feature importance, etc.).

---

## Status board

| Phase | Name | Your status |
|------:|------|-------------|
| 0 | Python basics | Do if not finished |
| 1 | Market data + first plot | **IN PROGRESS — gate open for Phase 2** |
| 2 | Big-move detection | **Locked** (unlock requested 2026-08-06; blocked — Phase 1 files missing) |
| 3 | Classical ML | Locked |
| 4 | Explainability | Locked |
| 5 | News / NLP | Locked |
| 6 | Deep learning | Locked |
| 7 | Causal + mystery score | Locked |
| 8 | Agents + final product | Locked |

**Manager note (2026-08-06):** Phase 2 unlock was requested, but Phase 1 deliverables are not on disk yet (no `data/raw/AAPL.csv`, no plot, no returns CSV; `notes/stage01.md` is still empty). `.venv` is recommended but not required — system Python + `pip install -r requirements.txt` is OK for learning. Finish Phase 1, then say `phase 2 unlock` again.

---

## PHASE 0 — Python basics
**Goal:** Run Python without fear.

### Tasks
1. Run `stage00_python_basics/01_hello.py`
2. Run `02_variables.py`
3. Run `03_functions.py`
4. Complete `04_mini_challenge.py`
5. Fill `notes/stage00.md` (3 bullets)

### Deliverables
- [ ] All 4 scripts run
- [ ] Notes written

### Time
2–5 days

---

## PHASE 1 — Market data (you are here)
**Goal:** Pull real prices, plot close, compute returns.

### Tasks
1. Install packages: **(A)** create `.venv` then `pip install -r requirements.txt` *(recommended)*, **or (B)** `python -m pip install -r requirements.txt` with system Python *(allowed)*
2. Run `01_download_prices.py` → `data/raw/AAPL.csv` + `AAPL_meta.json`
3. **Plot:** run `02_plot_close.py` → `data/plots/AAPL_close.png`
4. Run `03_compute_returns.py` → `data/processed/AAPL_returns.csv`
5. Open CSV; explain one row (Open/High/Low/Close/Volume)
6. Compute **one daily return by hand** and match the file
7. Fill `notes/stage01.md`
### Deliverables
- [ ] CSV + metadata
- [ ] Close-price plot PNG
- [ ] Returns CSV
- [ ] Notes with hand-calculated return

### Time
~1 week

### Plot details (Phase 1)
- X-axis = Date
- Y-axis = Close price
- One line = AAPL
- No cards, no dashboard, no multiple charts yet

---

## PHASE 2 — Big-move detector (forensics starts)
**Goal:** Find weird jump days and save each as a case.

### Tasks
1. Run `scripts/stage02_01_detect_big_moves.py`
2. Understand rule: `|return| >= k * recent_volatility`
3. Run `02_build_case_windows.py` (days before/after each jump)
4. Inspect the list of big-move dates
5. Optional plot later: price chart with big-move days marked
6. Fill `notes/stage02.md`

### Deliverables
- [ ] CSV of big-move dates
- [ ] Case windows saved
- [ ] Notes explaining why volatility threshold > fixed 3%

### Time
~1 week

---

## PHASE 3 — Classical ML (first AI)
**Goal:** Train a model to guess likely cause/pattern from clues (no future peeking).

### Tasks
1. Build a feature table per case (volume shock, recent volatility, etc.)
2. Create labels (simple cause buckets / weak labels)
3. Time-based train/test split (**no leakage**)
4. Train Decision Tree / Random Forest
5. Evaluate on held-out period
6. Write 5 lines: what worked / what failed
7. Fill `notes/stage03.md`

### Deliverables
- [ ] Feature table
- [ ] Trained model + scores
- [ ] Short failure analysis note

### Time
~2 weeks

**Unlock phrase:** `ready for stage 03`

---

## PHASE 4 — Explainability
**Goal:** Model must show top reasons, not only an answer.

### Tasks
1. Global feature importance
2. Per-case SHAP-style explanation
3. “Top 3 reasons” card for each big-move case
4. Attach reasons into a case file
5. Fill `notes/stage04.md`

### Deliverables
- [ ] Top-3 reasons per case
- [ ] Example case explanation you can read in plain English

### Time
~1 week

**Unlock phrase:** `ready for stage 04`

---

## PHASE 5 — News / NLP
**Goal:** Attach headlines as evidence.

### Tasks
1. Collect/load headlines around each case date
2. Clean text
3. Turn text into embeddings (numbers)
4. Score relevance to the stock/case
5. Add 0–N headlines + scores into the case file
6. Fill `notes/stage05.md`

### Deliverables
- [ ] Case file with scored headlines
- [ ] Notes: what “embedding” means in your words

### Time
~2 weeks

**Unlock phrase:** `ready for stage 05`

---

## PHASE 6 — Deep learning
**Goal:** Study the week of prices before the jump; compare to Phase 3.

### Tasks
1. Build sequences (e.g. last 5–10 days before event)
2. Train a small sequence model
3. Add confidence / uncertainty
4. Fair comparison vs Random Forest (same cases/split)
5. Fill `notes/stage06.md`

### Deliverables
- [ ] Deep model runs end-to-end
- [ ] Comparison note vs Phase 3

### Time
~2 weeks

**Unlock phrase:** `ready for stage 06`

---

## PHASE 7 — Causal thinking + mystery score
**Goal:** Separate “happened together” from “maybe caused it”; admit unknowns.

### Tasks
1. Compare stock vs market/sector move (abnormal idea)
2. Write a causal note for each case (simple)
3. Compute **mystery / residual score** (what remains unexplained)
4. Add causal note + mystery score to case file
5. Fill `notes/stage07.md`

### Deliverables
- [ ] Case report with causal note
- [ ] Mystery score

### Time
~1–2 weeks

**Unlock phrase:** `ready for stage 07`

---

## PHASE 8 — Agents + final product (capstone)
**Goal:** Multi-agent team writes one forensic report.

### Tasks
1. Define agents: News / Macro / Sector / Skeptic / Writer
2. Each agent inspects the case with tools
3. Merge into structured JSON report
4. Build simple HTML or Streamlit case viewer
5. Demo: pick ticker + date → full report
6. Fill `notes/stage08.md`

### Deliverables
- [ ] One-command/full report for a chosen event
- [ ] Readable case file (evidence + confidence + mystery)

### Time
~2–3 weeks

**Unlock phrase:** `ready for stage 08`

---

## Final product (what “done project” means)

Input: ticker + date of a big move  
Output: forensic case report with:

1. What happened (price/volume)
2. Top model reasons
3. Related news evidence
4. Causal note
5. Mystery score (what we still can’t explain)

---

## Daily intern protocol

1. Open this file + current stage `README.md`
2. Do **only today’s tasks**
3. Write 3 bullets in `notes/`
4. Report to manager with: files created + what you learned + blockers

### Report template
```text
Phase: _
Tasks done today:
-
Deliverables created:
-
Blocked?: YES/NO
Error (if any):
```

---

## Important

You asked for all phases in advance so you can see the mountain.  
**You still climb one step at a time.**  
Current order: **finish Phase 1 plot + returns + notes → then Phase 2.**
