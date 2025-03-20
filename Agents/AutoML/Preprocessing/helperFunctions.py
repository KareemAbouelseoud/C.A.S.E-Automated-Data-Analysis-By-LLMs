import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from scipy.sparse import csr_matrix
from sklearn.base import BaseEstimator, TransformerMixin

class CustomLabelEncoder(BaseEstimator, TransformerMixin):
    def __init__(self,feature_name):
        self.le = LabelEncoder()
        self.feature_name = feature_name

    def fit(self, X, y=None):
        X = np.array(X).ravel()  # Ensure it's 1D
        self.le.fit(X)
        return self

    def transform(self, X):
        X = np.array(X).ravel()  # Ensure it's 1D before transforming
        return self.le.transform(X).reshape(-1, 1)

    def fit_transform(self, X, y=None):
        return self.fit(X).transform(X)

    def inverse_transform(self, X_encoded):
        return self.le.inverse_transform(X_encoded.ravel())  # Decode labels

    def get_feature_names_out(self, input_features=None):
        """Return the encoded feature name."""
        return np.array([self.feature_name]) if self.feature_name else np.array([])
        
        
def datetime_transform(input_data, additional_features=None):
    input_data = input_data.copy()
    input_data = pd.to_datetime(input_data, errors='coerce')
    
    if additional_features:
        for feature in additional_features:
            if feature == 'year':
                input_data[f'{input_data.name}_year'] = input_data.dt.year
            elif feature == 'month':
                input_data[f'{input_data.name}_month'] = input_data.dt.month
            elif feature == 'day':
                input_data[f'{input_data.name}_day'] = input_data.dt.day
            elif feature == 'hour':
                input_data[f'{input_data.name}_hour'] = input_data.dt.hour
            elif feature == 'minute':
                input_data[f'{input_data.name}_minute'] = input_data.dt.minute
            elif feature == 'second':
                input_data[f'{input_data.name}_second'] = input_data.dt.second
            elif feature == 'weekday':
                input_data[f'{input_data.name}_weekday'] = input_data.dt.weekday
            elif feature == 'week':
                input_data[f'{input_data.name}_week'] = input_data.dt.isocalendar().week
            elif feature == 'quarter':
                input_data[f'{input_data.name}_quarter'] = input_data.dt.quarter
            elif feature == 'dayofyear':
                input_data[f'{input_data.name}_dayofyear'] = input_data.dt.dayofyear
            elif feature == 'is_leap_year':
                input_data[f'{input_data.name}_is_leap_year'] = input_data.dt.is_leap_year
            elif feature == 'is_month_start':
                input_data[f'{input_data.name}_is_month_start'] = input_data.dt.is_month_start
            elif feature == 'is_month_end':
                input_data[f'{input_data.name}_is_month_end'] = input_data.dt.is_month_end
            elif feature == 'is_quarter_start':
                input_data[f'{input_data.name}_is_quarter_start'] = input_data.dt.is_quarter_start
            elif feature == 'is_quarter_end':
                input_data[f'{input_data.name}_is_quarter_end'] = input_data.dt.is_quarter_end
            elif feature == 'is_year_start':
                input_data[f'{input_data.name}_is_year_start'] = input_data.dt.is_year_start
            elif feature == 'is_year_end':
                input_data[f'{input_data.name}_is_year_end'] = input_data.dt.is_year_end

    return input_data

class NullValueTransformer(BaseEstimator, TransformerMixin):
    def __init__(self,feature_name, strategy='mean', fill_value=None):
        self.strategy = strategy
        self.fill_value = fill_value
        self.feature_name = feature_name

    def fit(self, X, y=None):
        # Convert different input formats to pandas if needed
        if isinstance(X, csr_matrix):
            X = pd.DataFrame(X.toarray())
        elif isinstance(X, np.ndarray):
            if X.ndim > 1 and X.shape[1] > 1:  # Multi-column array
                X = pd.DataFrame(X)
            else:
                X = pd.Series(X.ravel())
        
        # For single series/column, calculate statistics
        if isinstance(X, pd.Series) or (isinstance(X, pd.DataFrame) and X.shape[1] == 1):
            try:
                if self.strategy == 'mean':
                    self.fill_value = X.mean()
                elif self.strategy == 'median':
                    self.fill_value = X.median()
                elif self.strategy == 'value' and self.fill_value is None:
                    raise ValueError("fill_value must be specified when strategy is 'value'")
            
            except Exception as e: 
                print(X)
                raise e
        return self

    def transform(self, X):
        # Convert different input formats to pandas if needed
        if isinstance(X, csr_matrix):
            X = pd.DataFrame(X.toarray())
        elif isinstance(X, np.ndarray):
            if X.ndim > 1 and X.shape[1] > 1:  # Multi-column array
                X = pd.DataFrame(X)
            else:
                X = pd.Series(X.ravel())
        
        X = X.copy()
        
        # If X is multi-column DataFrame, we need to handle just the specified feature
        if isinstance(X, pd.DataFrame) and X.shape[1] > 1:
            if self.strategy == 'drop':
                # Drop rows where the specified feature is null
                X = X.dropna(subset=[self.feature_name]).reset_index(drop=True)
            else:
                # Only fill nulls in the specified feature
                if self.feature_name in X.columns:
                    if self.strategy in ['mean', 'median', 'value']:
                        X[self.feature_name] = X[self.feature_name].fillna(self.fill_value)
                else:
                    print(X)  
                    raise ValueError(f"Feature {self.feature_name} not found in data")
            
            return X
        
        # For single column/series
        if self.strategy in ['mean', 'median', 'value']:
            X_filled = X.fillna(self.fill_value)
        elif self.strategy == 'drop':
            X_filled = X.dropna().reset_index(drop=True)
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")
        
        # Return as properly shaped array
        return X_filled.values.reshape(-1, 1) if (isinstance(X_filled, pd.Series) or 
                                                (isinstance(X_filled, pd.DataFrame) and X_filled.shape[1] == 1)) else X_filled

    def fit_transform(self, X, y=None):
        return self.fit(X).transform(X)
    
    def get_feature_names_out(self, input_features=None):
        """Return the encoded feature name."""
        return np.array([self.feature_name]) if self.feature_name else np.array([])

def log_transform(X):
    """
    Applies a log transformation to the input data.
    
    Parameters:
    - X: The input data (numpy array or pandas DataFrame/Series).
    
    Returns:
    - Transformed data with log applied.
    """
    if isinstance(X, pd.DataFrame):
        return X.apply(np.log1p)  # Use np.log1p to handle zero values
    elif isinstance(X, pd.Series):
        return np.log1p(X)
    else:
        return np.log1p(np.array(X))
class DropDuplicatesTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, subset=None, column=None, keep='first'):
        """
        A transformer that removes duplicate rows either based on multiple columns (subset)
        or a single column (column), but only during training.

        Parameters:
        - subset: list or None, specifies the columns to consider for duplicate removal (row-wise).
        - column: str or None, specifies a single column to consider for duplicate removal.
        - keep: str, which duplicate to keep ('first', 'last', or False).
        """
        self.subset = subset
        if column and column != 'None':
            self.column = column
        self.keep = keep
        self.is_fitted = False  # Track if fit was called

    def fit(self, X, y=None):
        """
        Drops duplicates only in training data during fit.

        - If `subset` is provided, it removes duplicate rows based on those columns.
        - If `column` is provided, it removes duplicate rows based on that single column.
        """
        X = X.copy()

        if self.subset:
            try:
                X = X.drop_duplicates(subset=self.subset, keep=self.keep)
            except Exception as e:
                raise ValueError(f"Failed to drop duplicate rows based on subset {self.subset}. Error: {e}")

        elif self.column:
            try:
                X = X.drop_duplicates(subset=[self.column], keep=self.keep)
            except Exception as e:
                raise ValueError(f"Failed to drop duplicate rows based on column {self.column}. Error: {e}")

        self.X_deduplicated_ = X  # Store deduplicated training data
        self.is_fitted = True
        return self

    def transform(self, X):
        """
        - During training, returns deduplicated data.
        - During testing, returns data unchanged.
        """
        return self.X_deduplicated_ if self.is_fitted else X    
    
    def get_feature_names_out(self, input_features=None):
        """Return the encoded feature name."""
        return np.array([self.feature_name]) if self.feature_name else np.array(["Drop_Rows"])
class OutlierTransformer(BaseEstimator, TransformerMixin):
    def __init__(self,feature_name, method='iqr', strategy='remove', threshold=1.5):
        self.method = method
        self.strategy = strategy
        self.threshold = threshold
        self.feature_name = feature_name

    def fit(self, X, y=None):
        X = X.squeeze() if isinstance(X, np.ndarray) and X.ndim > 1 else X
        X = pd.Series(X) if isinstance(X, np.ndarray) else X
        if self.method == 'iqr':
            self.Q1 = X.quantile(0.25)
            self.Q3 = X.quantile(0.75)
            self.IQR = self.Q3 - self.Q1
            self.lower = self.Q1 - self.threshold * self.IQR
            self.upper = self.Q3 + self.threshold * self.IQR
        elif self.method == 'zscore':
            self.mean = X.mean()
            self.std = X.std()
            self.median = X.median()
        return self

    def transform(self, X):
        X = X.squeeze() if isinstance(X, np.ndarray) and X.ndim > 1 else X
        X = pd.Series(X) if isinstance(X, np.ndarray) else X
        X = X.copy()

        if self.method == 'iqr':
            mask = (X >= self.lower) & (X <= self.upper)
        elif self.method == 'zscore':
            z_scores = (X - self.mean) / self.std
            mask = np.abs(z_scores) < self.threshold

        if self.strategy == 'remove':
            return X.loc[mask].reset_index(drop=True).values.reshape(-1, 1)
        
        elif self.strategy == 'impute_mean':
            X.loc[~mask] = self.mean if self.method == 'zscore' else X.mean()
            return X.values.reshape(-1, 1)
        
        elif self.strategy == 'impute_median':
            X.loc[~mask] = self.median if self.method == 'zscore' else X.median()
            return X.values.reshape(-1, 1)
        
        elif self.strategy == 'winsorize':
            if self.method == 'iqr':
                return np.clip(X.values, self.lower, self.upper).reshape(-1, 1)
            elif self.method == 'zscore':
                return np.clip(X.values, self.mean - self.threshold * self.std, self.mean + self.threshold * self.std).reshape(-1, 1)
        
        
        elif self.strategy == 'winsorize':
            if self.method == 'iqr':
                return np.clip(X.values, self.lower, self.upper)
            elif self.method == 'zscore':
                return np.clip(X.values, self.mean - self.threshold * self.std, self.mean + self.threshold * self.std)

    def fit_transform(self, X, y=None):
        return self.fit(X).transform(X)
    
    def get_feature_names_out(self, input_features=None):
        """Return the encoded feature name."""
        return np.array([self.feature_name]) if self.feature_name else np.array([])