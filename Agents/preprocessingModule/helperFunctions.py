import pandas as pd
import numpy as np
from typing import List

def validate_column(df: pd.DataFrame, column_name: str, expected_type: str) -> None:
    """Validate column existence and data type."""
    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' not found in dataset")
    
    if expected_type == "numeric" and not np.issubdtype(df[column_name].dtype, np.number):
        raise ValueError(f"Column '{column_name}' must be numeric")
    
    if expected_type == "categorical" and not pd.api.types.is_categorical_dtype(df[column_name]):
        raise ValueError(f"Column '{column_name}' must be categorical")

def make_serializable(obj):
    """Convert numpy/pandas objects to Python-native types."""
    if isinstance(obj, (np.int64, np.int32)):
        return int(obj)
    if isinstance(obj, (np.float64, np.float32)):
        return float(obj)
    if isinstance(obj, pd.Series):
        return obj.tolist()
    return obj

def is_leap_year(year: pd.Series) -> pd.Series:
    """Check if years are leap years."""
    return ((year % 4 == 0) & (year % 100 != 0)) | (year % 400 == 0)

def datetime_transformer(X: pd.DataFrame, features: List[str], column_name: str) -> pd.DataFrame:
    """Core datetime transformation logic for reuse in pipelines"""
    X = X.copy()
    dt_series = pd.to_datetime(X[column_name], errors='coerce')
    
    for feat in features:
        new_col = f"{column_name}_{feat}"
        if feat == "year":
            X[new_col] = dt_series.dt.year
        elif feat == "month":
            X[new_col] = dt_series.dt.month
        elif feat == "day":
            X[new_col] = dt_series.dt.day
        elif feat == "hour":
            X[new_col] = dt_series.dt.hour
        elif feat == "minute":
            X[new_col] = dt_series.dt.minute
        elif feat == "second":
            X[new_col] = dt_series.dt.second
        # uncomment if needed
        # elif feat == "weekday":
        #     X[new_col] = dt_series.dt.weekday
        # elif feat == "week":
        #     X[new_col] = dt_series.dt.isocalendar().week
        # elif feat == "quarter":
        #     X[new_col] = dt_series.dt.quarter
        # elif feat == "dayofyear":
        #     X[new_col] = dt_series.dt.dayofyear
        # elif feat == "is_leap_year":
        #     X[new_col] = is_leap_year(dt_series.dt.year)
        # elif feat == "is_month_start":
        #     X[new_col] = dt_series.dt.is_month_start
        # elif feat == "is_month_end":
        #     X[new_col] = dt_series.dt.is_month_end
        # elif feat == "is_quarter_start":
        #     X[new_col] = dt_series.dt.is_quarter_start
        # elif feat == "is_quarter_end":
        #     X[new_col] = dt_series.dt.is_quarter_end
        # elif feat == "is_year_start":
        #     X[new_col] = dt_series.dt.is_year_start
        # elif feat == "is_year_end":
        #     X[new_col] = dt_series.dt.is_year_end
            
    return X