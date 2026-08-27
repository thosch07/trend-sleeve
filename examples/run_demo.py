"""End-to-end demo on SYNTHETIC data.

Real results use IB continuous exchange data (23 futures, incl. 2008).
That data and the live edge are deliberately NOT in this repo. This demo
generates trending synthetic series so a reviewer can clone, run, and see
the full pipeline — signal -> vol-target -> costed backtest -> report —
produce sane numbers in one command.

Run: python examples/run_demo.py
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from trendsleeve import (
    momentum_signal,
    vol_target_weights,
    run_backtest,
    roll_diagnosis,
)


def make_synthetic_basket(n_months: int = 240, n_assets: int = 18, seed: int = 7):
    """Trending random walks with occasional regime flips — a toy stand-in
    for a diversified futures basket. NOT real market data."""
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2005-01-31", periods=n_months, freq="ME")
    cols = [f"F{i:02d}" for i in range(n_assets)]
    prices = {}
    for c in cols:
        drift = rng.normal(0.003, 0.002)
        shocks = rng.normal(drift, 0.05, n_months)
        # inject a few regime flips so momentum has something to catch
        for _ in range(rng.integers(1, 4)):
            t = rng.integers(24, n_months)
            shocks[t:] -= 2 * drift
        prices[c] = 100 * np.exp(np.cumsum(shocks))
    return pd.DataFrame(prices, index=idx)


def main() -> None:
    prices = make_synthetic_basket()
    returns = prices.pct_change()

    print("=== Roll / data-quality diagnosis (synthetic) ===")
    print(roll_diagnosis(prices).head())
    print()

    signal = momentum_signal(prices, lookback_months=12)
    weights = vol_target_weights(returns, signal, target_vol=0.10)
    result = run_backtest(returns, weights, cost_per_turnover=0.0005)

    print("=== Backtest summary (synthetic — illustrative only) ===")
    for k, v in result.summary().items():
        print(f"  {k:16s}: {v}")
    print()
    print("NOTE: numbers here are from synthetic data and mean nothing on")
    print("their own. The point of this repo is the METHOD, not the return.")


if __name__ == "__main__":
    main()
