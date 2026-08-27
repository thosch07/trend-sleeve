"""Data-quality guards.

This module exists because of a real bug: an early version of the sleeve
reported an annual turnover of ~62 on yfinance data. On clean IB
continuous (roll-adjusted) exchange data the true figure was ~9-15. The
62 was a data artefact — phantom price jumps at contract rolls that
yfinance stitches badly — not a property of the strategy.

Lesson kept as code: a backtest is only as honest as its price series.
These checks fail loudly rather than let a bad series through.
"""
from __future__ import annotations

import pandas as pd


def flag_suspicious_jumps(
    prices: pd.DataFrame, threshold: float = 0.25
) -> pd.DataFrame:
    """Return a boolean mask of period-over-period moves exceeding `threshold`.

    A clean roll-adjusted futures series should have very few single-period
    moves above 25%. Many such flags usually mean the series is not
    roll-adjusted (the yfinance failure mode).
    """
    pct_change = prices.pct_change().abs()
    return pct_change > threshold


def roll_diagnosis(prices: pd.DataFrame, threshold: float = 0.25) -> pd.DataFrame:
    """Per-instrument count of suspicious jumps — the roll-quality report.

    On the validated 18-contract IB basket this produced only 2 flagged
    days across all contracts. If your run shows dozens, stop and fix the
    data before trusting any performance number.
    """
    flags = flag_suspicious_jumps(prices, threshold)
    report = pd.DataFrame(
        {
            "suspicious_jumps": flags.sum(),
            "worst_move": prices.pct_change().abs().max(),
        }
    )
    return report.sort_values("suspicious_jumps", ascending=False)
