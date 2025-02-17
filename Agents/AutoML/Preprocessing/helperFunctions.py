import numpy as np
import pandas as pd

def minmax_transform(input_data):
            input_data = input_data.copy()
            return (input_data - input_data.min()) / (input_data.max() - input_data.min())
def standard_transform(input_data):
            input_data = input_data.copy()
            return (input_data - input_data.mean()) / input_data.std()

def log_transform(input_data):
            input_data = input_data.copy()
            return np.log1p(input_data)

def robust_transform(input_data):
            input_data = input_data.copy()
            input_data = (input_data - input_data.median()) / (input_data.quantile(0.75) - input_data.quantile(0.25))
            return input_data

def datetime_transform(input_data):
            input_data = input_data.copy()
            input_data = pd.to_datetime(input_data, errors='coerce')
            return input_data

def drop_transform(input_data):
    input_data = input_data.copy()
    try:
        input_data.dropna(inplace=True)
    except:
        raise ValueError("Failed to drop null values.")
    return input_data

def fill_value_transform(input_data,value):
    input_data = input_data.copy()
    try:
        input_data = input_data.fillna(value)
    except:
        raise ValueError(f"Failed to fill null values with {value}.")
    return input_data

def fill_mean_transform(input_data):
    input_data = input_data.copy()
    try:
        input_data = input_data.fillna(input_data.mean())
    except:
        raise ValueError("Failed to fill null values with the mean.")
    return input_data

def drop_rows_transform(input_data,subset=None,keep='first'):
    input_data = input_data.copy()
    try:
        input_data = input_data.drop_duplicates(subset=subset, keep=keep)
    except:
        raise ValueError("Failed to drop duplicate rows.")
    return input_data

def drop_columns_transform(input_data,keep='first'):
    input_data = input_data.copy()
    try:
        input_data = input_data.loc[:, ~input_data.columns.duplicated(keep=keep)]
    except:
        raise ValueError("Failed to drop duplicate columns.")
    return input_data

def remove_outlier_transform_by_iqr(input_data, threshold=1.5):
    input_data = input_data.copy()
    Q1 = input_data.quantile(0.25)
    Q3 = input_data.quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - threshold * IQR
    upper = Q3 + threshold * IQR
    mask = (input_data >= lower) & (input_data <= upper)
    return input_data[mask].reset_index(drop=True)

def remove_outlier_transform_by_zscore(input_data, threshold=3):
    input_data = input_data.copy()
    mean = input_data.mean()
    std = input_data.std()
    z_scores = (input_data - mean) / std
    mask = np.abs(z_scores) < threshold
    return input_data[mask].reset_index(drop=True)

def impute_mean_outlier_transform_by_iqr(input_data, threshold=1.5):
    input_data = input_data.copy()
    Q1 = input_data.quantile(0.25)
    Q3 = input_data.quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - threshold * IQR
    upper = Q3 + threshold * IQR
    mask = (input_data >= lower) & (input_data <= upper)
    input_data.loc[~mask] = input_data.mean()
    return input_data

def impute_mean_outlier_transform_by_zscore(input_data, threshold=3):
    input_data = input_data.copy()
    mean = input_data.mean()
    std = input_data.std()
    z_scores = (input_data - mean) / std
    input_data.loc[np.abs(z_scores) >= threshold] = mean
    return input_data

def impute_median_outlier_transform_by_iqr(input_data, threshold=1.5):
    input_data = input_data.copy()
    median = input_data.median()
    Q1 = input_data.quantile(0.25)
    Q3 = input_data.quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - threshold * IQR
    upper = Q3 + threshold * IQR
    mask = (input_data >= lower) & (input_data <= upper)
    input_data.loc[~mask] = median
    return input_data

def impute_median_outlier_transform_by_zscore(input_data, threshold=3):
    input_data = input_data.copy()
    mean = input_data.mean()
    std = input_data.std()
    z_scores = (input_data - mean) / std
    input_data.loc[np.abs(z_scores) >= threshold] = input_data.median()
    return input_data

def winsorize_outlier_transform_by_iqr(input_data, threshold=1.5):
    input_data = input_data.copy()
    Q1 = input_data.quantile(0.25)
    Q3 = input_data.quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - threshold * IQR
    upper = Q3 + threshold * IQR
    input_data = np.clip(input_data, lower, upper)
    return input_data

def winsorize_outlier_transform_by_zscore(input_data, threshold=3):
    input_data = input_data.copy()
    mean = input_data.mean()
    std = input_data.std()
    input_data = np.clip(input_data, mean - threshold * std, mean + threshold * std)
    return input_data