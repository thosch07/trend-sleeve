"""Minimal, honest backtester.

Design rule: costs are charged on turnover, out-of-sample is respected,
and nothing is annualised with numbers that flatter the result. If a
metric looks too good, the first suspect is the data, not the edge.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class BacktestResult:
    equity: pd.Series
    returns: pd.Series
    turnover: pd.Series

    @property
    def sharpe(self) -> float:
        r = self.returns.dropna()
        if r.std() == 0:
            return float("nan")
        return float(r.mean() / r.std() * np.sqrt(12))

    @property
    def max_drawdown(self) -> float:
        curve = self.equity.dropna()
        peak = curve.cummax()
        return float((curve / peak - 1.0).min())

    @property
    def annual_turnover(self) -> float:
        return float(self.turnover.mean() * 12)

    def summary(self) -> dict[str, float]:
        return {
            "sharpe": round(self.sharpe, 3),
            "max_drawdown": round(self.max_drawdown, 3),
            "annual_turnover": round(self.annual_turnover, 1),
            "total_return": round(float(self.equity.iloc[-1] - 1.0), 3),
        }


def run_backtest(
    returns: pd.DataFrame,
    weights: pd.DataFrame,
    cost_per_turnover: float = 0.0005,
) -> BacktestResult:
    """Apply lagged weights to next-period returns, net of costs.

    Parameters
    ----------
    returns : monthly instrument returns (wide).
    weights : target weights (wide). Lagged by one period internally so no
              look-ahead: this month's weight earns next month's return.
    cost_per_turnover : cost charged per unit of |weight change|.
                        0.0005 = 5 bps, a deliberately conservative proxy.
    """
    aligned_w = weights.shift(1).reindex_like(returns).fillna(0.0)
    turnover = aligned_w.diff().abs().sum(axis=1).fillna(0.0)
    gross = (aligned_w * returns).sum(axis=1)
    net = gross - turnover * cost_per_turnover
    equity = (1.0 + net).cumprod()
    return BacktestResult(equity=equity, returns=net, turnover=turnover)
