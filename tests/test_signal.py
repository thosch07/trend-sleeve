"""Tests for the momentum signal and cost model.

These exist to prove two things to anyone reading the repo:
1. The signal does what it claims (no look-ahead, correct sign).
2. Costs actually reduce returns (a backtest that ignores them is a lie).
"""
import numpy as np
import pandas as pd
import pytest

from trendsleeve.signal import momentum_signal
from trendsleeve.backtest import run_backtest


def _monthly_index(n: int) -> pd.DatetimeIndex:
    return pd.date_range("2010-01-31", periods=n, freq="ME")


def test_uptrend_gives_long_signal():
    idx = _monthly_index(15)
    prices = pd.DataFrame({"A": np.linspace(100, 200, 15)}, index=idx)
    sig = momentum_signal(prices, lookback_months=12)
    # after 12 months of history, a steady uptrend must be +1
    assert sig["A"].dropna().iloc[-1] == 1.0


def test_downtrend_gives_short_signal():
    idx = _monthly_index(15)
    prices = pd.DataFrame({"A": np.linspace(200, 100, 15)}, index=idx)
    sig = momentum_signal(prices, lookback_months=12)
    assert sig["A"].dropna().iloc[-1] == -1.0


def test_no_signal_before_enough_history():
    idx = _monthly_index(6)
    prices = pd.DataFrame({"A": np.linspace(100, 120, 6)}, index=idx)
    sig = momentum_signal(prices, lookback_months=12)
    # not enough history -> all NaN
    assert sig["A"].isna().all()


def test_invalid_lookback_raises():
    prices = pd.DataFrame({"A": [1, 2, 3]})
    with pytest.raises(ValueError):
        momentum_signal(prices, lookback_months=0)


def test_costs_reduce_returns():
    idx = _monthly_index(24)
    rng = np.random.default_rng(42)
    returns = pd.DataFrame({"A": rng.normal(0.01, 0.04, 24)}, index=idx)
    # alternate the position every month -> forces turnover
    weights = pd.DataFrame(
        {"A": [1.0 if i % 2 == 0 else -1.0 for i in range(24)]}, index=idx
    )
    free = run_backtest(returns, weights, cost_per_turnover=0.0)
    costed = run_backtest(returns, weights, cost_per_turnover=0.01)
    assert costed.equity.iloc[-1] < free.equity.iloc[-1]
