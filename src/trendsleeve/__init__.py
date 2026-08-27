"""trend-sleeve: a slow, honestly-backtested time-series momentum sleeve."""

from .signal import momentum_signal, vol_target_weights
from .backtest import run_backtest, BacktestResult
from .data_quality import flag_suspicious_jumps, roll_diagnosis

__all__ = [
    "momentum_signal",
    "vol_target_weights",
    "run_backtest",
    "BacktestResult",
    "flag_suspicious_jumps",
    "roll_diagnosis",
]
