# trend-sleeve

A slow time-series momentum sleeve — signal, vol-targeting, and a cost-aware
backtester — built to one rule: **a backtest is only as honest as its data.**

This repo is a stripped-down, reproducible slice of a larger systematic
trading process. The live edge and the proprietary IB dataset are not here.
What *is* here is the method, the tests, and the data-integrity discipline.

```bash
pip install -e ".[dev]"
pytest              # 5 tests, all green
python examples/run_demo.py   # full pipeline on synthetic data
```

## Why this exists

Most public backtests are broken in the same quiet way: bad price data makes
a mediocre strategy look brilliant. This repo is built around a real bug I
hit and fixed.

An early version reported **annual turnover of ~62** on free (yfinance) data.
That number was a lie — phantom price jumps where the data vendor stitches
futures contracts badly at each roll. On clean, roll-adjusted IB exchange
data the true figure was **~9–15**. Same strategy, completely different
picture. The `data_quality` module exists so that failure mode fails loudly
instead of silently inflating results.

## What's inside

| Module | Job |
|---|---|
| `signal.py` | 12-month time-series momentum + vol-targeted weights |
| `backtest.py` | Lagged, cost-charged backtest — no look-ahead, no flattery |
| `data_quality.py` | Roll-diagnosis / suspicious-jump guards (the yfinance lesson) |
| `tests/` | Prove the signal is correct and that costs actually bite |
| `examples/run_demo.py` | One-command reproducible run on synthetic data |

## Design decisions I stand behind

- **The signal is deliberately slow (12M).** Faster and blended variants
  backtested better — but the improvement was outlier-driven and fragile.
  Chasing signal speed is a documented dead-end, not an open question.
- **Costs are charged on turnover, conservatively.** A backtest that ignores
  transaction costs isn't optimistic, it's wrong.
- **No look-ahead by construction.** This month's weight earns next month's
  return; the lag is enforced in the engine, not left to discipline.
- **The real data stays out.** You can reproduce the *method* end-to-end on
  synthetic series. The edge isn't in the code you can see — it's in the
  process and the data hygiene.

## What this is not

Not investment advice. Not a signal service. Not a claim that this specific
sleeve will make money. It's a demonstration of how I build and stress-test
a systematic strategy — honestly, with tests, and with a healthy distrust of
my own results.

---
## Disclaimer

This repository is a technical demonstration of systematic-strategy
development and backtesting methodology. It is not investment advice, not a
recommendation, and not an offer of any financial product or service. All
figures shown are generated from synthetic data and are illustrative only —
they do not represent actual or achievable returns. Past or simulated
performance does not indicate future results. Use at your own risk. MIT licensed.
