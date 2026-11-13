# Stage 02 — Big move detector

## Goal
Find days with unusually large moves. Each day becomes a **case** for later forensics.

## Words to know

| Word | Simple meaning |
|------|----------------|
| Volatility | How jumpy recent returns were |
| Threshold | Cutoff that defines “big” |
| Event window | Days before/after the move |
| Case | One big-move event we will investigate |

## Idea (simple)
A day is “big” if:

`|today's return| >= k * recent_volatility`

Default: `k = 2.5`, volatility = rolling 20-day standard deviation of returns.

## Run (after you finish Stage 01)

```bash
python scripts/stage02_01_detect_big_moves.py
python scripts/stage02_02_build_case_windows.py
```

## Checklist

- [ ] You have a CSV of big-move dates
- [ ] You understand why we use volatility (not a fixed 3% for every stock)
- [ ] Notes in `notes/stage02.md`

## Next
`stage03_classical_ml/README.md`
