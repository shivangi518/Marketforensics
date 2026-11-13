# MarketForensics — Learning Path (Basic → Advanced)

Follow this in order. Each stage has a `README.md` with lessons and a checklist.

---

## Stage 00 — Python basics (no AI)

**Goal:** Feel comfortable running Python files.

**You will learn**
- What Python is
- Variables, lists, dictionaries
- Functions
- Reading/writing a simple file
- How to run a script from the terminal

**Done when**
- [ ] `01_hello.py` runs
- [ ] `02_variables.py` runs
- [ ] `03_functions.py` runs
- [ ] You finish `04_mini_challenge.py`

**Time:** 2–5 days depending on pace

---

## Stage 01 — Market data

**Goal:** Load real stock prices and make a chart.

**You will learn**
- Tables of data (rows = days, columns = open/high/low/close)
- Returns (% change)
- Plotting with matplotlib
- Saving data to `data/`

**Done when**
- [ ] You can download one ticker (e.g. AAPL)
- [ ] You plot close price
- [ ] You compute daily returns

**Time:** ~1 week

---

## Stage 02 — Big move detector (the heart of forensics)

**Goal:** Find days when a stock moved “a lot” and build an event window.

**You will learn**
- Thresholds (e.g. |return| > 2× recent volatility)
- Event windows (5 days before / after)
- Saving a list of “cases” to investigate later

**Done when**
- [ ] Script lists big-move dates for a ticker
- [ ] Each case has before/after context saved

**Time:** ~1 week

---

## Stage 03 — Classical machine learning (your first AI)

**Goal:** Teach a model to use features around an event.

**You will learn**
- Features vs labels
- Train / test split (never peek at the future)
- Decision tree / random forest
- Accuracy is not everything

**Done when**
- [ ] You train a model without leakage
- [ ] You evaluate on a held-out period
- [ ] You write 5 lines: what worked / what failed

**Time:** ~2 weeks

---

## Stage 04 — Explainability

**Goal:** Answer “which clues mattered?”

**You will learn**
- Feature importance
- Simple SHAP-style explanations
- Turning model output into human clues for a case file

**Done when**
- [ ] Each big-move case can show top 3 contributing features

**Time:** ~1 week

---

## Stage 05 — News / NLP

**Goal:** Attach headlines to events and score relevance.

**You will learn**
- Text as data
- Embeddings (turning sentences into numbers)
- Similarity: “is this headline about this stock?”

**Done when**
- [ ] A case file can include 0–N related headlines with scores

**Time:** ~2 weeks

---

## Stage 06 — Deep learning

**Goal:** Use a small sequence model on pre-move history.

**You will learn**
- What a neural network roughly is
- Sequences (days in order)
- Uncertainty / confidence

**Done when**
- [ ] Deep model runs end-to-end
- [ ] You compare it fairly vs Stage 03 model

**Time:** ~2 weeks

---

## Stage 07 — Causal thinking

**Goal:** Ask better questions than correlation.

**You will learn**
- Correlation ≠ causation
- Simple graphs: macro → sector → stock
- “What if news wasn’t there?” style checks (simple version)

**Done when**
- [ ] Case report includes a causal note + mystery residual

**Time:** ~1–2 weeks

---

## Stage 08 — Agents + product

**Goal:** Multi-agent investigation + a readable case file UI/report.

**You will learn**
- Tool-using agents (news, macro, skeptic)
- Structured JSON reports
- A simple app or HTML case viewer

**Done when**
- [ ] One click/run produces a full forensic report for a chosen event

**Time:** ~2–3 weeks

---

## How to study each day

1. Open the stage `README.md`
2. Read the “Words to know” (5 minutes)
3. Run the starter scripts
4. Do the checklist tasks
5. Write 3 bullet notes in `notes/` about what you learned

If you get stuck for more than 30 minutes, ask in chat with:
- which stage
- which file
- the exact error message
