"""Time-series momentum signal.

Deliberately slow 12-month signal. Faster and blended variants tested
better on paper but were outlier-driven and fragile — see notebooks/
02_signal_speed_deadend.ipynb for the walk-through. Do not re-tune speed.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def momentum_signal(prices: pd.DataFrame, lookback_months: int = 12) -> pd.DataFrame:
    """Sign of trailing total return over `lookback_months`.

    Parameters
    ----------
    prices : wide DataFrame, one column per instrument, monthly frequency,
             DatetimeIndex. Continuous (roll-adjusted) futures prices.
    lookback_months : trailing window. Default 12 (validated). Changing this
             is a known dead-end — kept as a parameter for research only.

    Returns
    -------
    DataFrame of {-1, 0, +1} positions, same shape as `prices`,
    NaN until enough history exists.
    """
    if lookback_months < 1:
        raise ValueError("lookback_months must be >= 1")

    trailing_return = prices / prices.shift(lookback_months) - 1.0
    signal = np.sign(trailing_return)
    # np.sign(0) == 0 -> flat, which is the intended behaviour
    return signal


def vol_target_weights(
    returns: pd.DataFrame,
    signal: pd.DataFrame,
    target_vol: float = 0.10,
    vol_window: int = 36,
) -> pd.DataFrame:
    """Scale each position to an equal risk contribution at `target_vol`.

    Uses trailing realised vol per instrument (annualised from monthly).
    This is the step where full-contract futures granularity bites: at
    10% target vol on a 1M account the high-vol metals round to zero.
    That constraint is why the hedge job and the DARWIN job were split
    (see README).
    """
    realised_vol = returns.rolling(vol_window).std() * np.sqrt(12)
    inst_weight = (target_vol / realised_vol).clip(upper=3.0)
    weights = signal * inst_weight
    # equal-weight across the basket
    n = signal.abs().sum(axis=1).replace(0, np.nan)
    return weights.div(n, axis=0).fillna(0.0)
