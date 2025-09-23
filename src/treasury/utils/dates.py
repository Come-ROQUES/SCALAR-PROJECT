\
\
\
\

import pandas as pd
from typing import Union
from datetime import datetime
from ..logging_config import logger


VAL_DATE = pd.Timestamp.utcnow().tz_localize(None).normalize()


def to_naive_ts(x: Union[str, pd.Timestamp, datetime]) -> pd.Timestamp:
    \
\
\
\
\
\
\
\
\
    try:
        t = pd.to_datetime(x, errors="coerce")
        if isinstance(t, pd.Timestamp) and t.tz is not None:
            return t.tz_localize(None)
        return t
    except Exception as e:
        logger.warning(f"Erreur conversion date {x}: {e}")
        return pd.NaT


def to_naive_series(s: pd.Series) -> pd.Series:
    \
\
\
\
\
\
\
\
\
    try:
        s = pd.to_datetime(s, errors="coerce")
        if hasattr(s.dt, 'tz') and s.dt.tz is not None:
            s = s.dt.tz_localize(None)
        return s
    except Exception as e:
        logger.warning(f"Erreur conversion série dates: {e}")
        return s


def get_years_between(start_date: pd.Timestamp, end_date: pd.Timestamp) -> float:
    \
\
\
\
\
\
\
\
\
\
    if pd.isna(start_date) or pd.isna(end_date):
        return 0.0

    days_diff = (end_date - start_date).days
    return max(0.0, days_diff / 365.0)


def get_days_to_maturity(maturity_date: pd.Timestamp,
                        val_date: pd.Timestamp = None) -> int:
    \
\
\
\
\
\
\
\
\
\
    if val_date is None:
        val_date = VAL_DATE

    if pd.isna(maturity_date):
        return 0

    return (maturity_date - val_date).days


def classify_tenor(time_to_maturity_years: float) -> str:
    \
\
\
\
\
\
\
\
\
    if pd.isna(time_to_maturity_years) or time_to_maturity_years <= 0:
        return "Expired"

    years = time_to_maturity_years

    if years <= 1/12:
        return "1M"
    elif years <= 0.25:
        return "3M"
    elif years <= 0.5:
        return "6M"
    elif years <= 1:
        return "12M"
    elif years <= 2:
        return "2Y"
    elif years <= 5:
        return "5Y"
    elif years <= 10:
        return "10Y"
    else:
        return f"{int(years)}Y"


def is_business_day(date: pd.Timestamp,
                   holidays: list = None) -> bool:
    \
\
\
\
\
\
\
\
\
\
    if pd.isna(date):
        return False


    if date.weekday() >= 5:
        return False


    if holidays and date.normalize() in holidays:
        return False

    return True


def add_business_days(start_date: pd.Timestamp,
                     business_days: int,
                     holidays: list = None) -> pd.Timestamp:
    \
\
\
\
\
\
\
\
\
\
\
    if pd.isna(start_date):
        return pd.NaT

    current_date = start_date
    days_added = 0

    while days_added < business_days:
        current_date += pd.Timedelta(days=1)
        if is_business_day(current_date, holidays):
            days_added += 1

    return current_date


def get_accrual_period_fraction(start_date: pd.Timestamp,
                               end_date: pd.Timestamp,
                               day_count_convention: str = "ACT/365") -> float:
    \
\
\
\
\
\
\
\
\
\
\
    if pd.isna(start_date) or pd.isna(end_date):
        return 0.0

    if end_date <= start_date:
        return 0.0

    days = (end_date - start_date).days

    if day_count_convention == "ACT/365":
        return days / 365.0
    elif day_count_convention == "ACT/360":
        return days / 360.0
    elif day_count_convention == "30/360":

        return days / 360.0
    else:
        logger.warning(f"Convention inconnue {day_count_convention}, utilisation ACT/365")
        return days / 365.0


def get_val_date() -> pd.Timestamp:
    \
    return VAL_DATE


def set_val_date(new_val_date: Union[str, pd.Timestamp, datetime]) -> None:
    \
\
\
\
    global VAL_DATE
    VAL_DATE = to_naive_ts(new_val_date)
    logger.info(f"Date de valorisation mise à jour: {VAL_DATE}")