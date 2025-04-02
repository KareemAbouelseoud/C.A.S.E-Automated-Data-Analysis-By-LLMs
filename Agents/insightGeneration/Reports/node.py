from io import StringIO
import os
import time
import numpy as np
import pandas as pd
import seaborn as sns
import ydata_profiling
import matplotlib.pyplot as plt
from ydata_profiling import ProfileReport

from ydata_profiling.model.summarizer import BaseSummarizer
from visions import VisionsTypeset
import json

def generate_profile_data(df:pd.DataFrame) -> dict:
    """Generate a pandas-profiling report and parse it into a JSON-serializable dict."""
    profile = ProfileReport(
        df,
        samples=None,
        interactions=None,
        missing_diagrams=None,
    )
    json_str = profile.to_json()
    return json.loads(json_str)

def clean_profile_report(df:pd.DataFrame) -> dict:
    """Clean a generated profile report and return cleaned data structure."""
    data = generate_profile_data(df)

    #  top-level section
    for key in ["scatter", "missing", "package", "interactions"]:
        data.pop(key, None)

    # Table-level
    data["table"].pop("memory_size", None)
    data["table"].pop("record_size", None)

    COMMON_TEXT_METADATA = [
        "block_alias_values",
        "block_alias_counts",
        "n_block_alias",
        "block_alias_char_counts",
        "script_counts",
        "n_scripts",
        "script_char_counts",
        "category_alias_counts",
        "n_category",
        "category_alias_char_counts",
    ]

    CATEGORICAL_TEXT_METADATA = [
        "max_length",
        "mean_length",
        "median_length",
        "min_length",
        "n_characters_distinct",
        "n_characters",
        "character_counts",
        "word_counts",
        "category_alias_values",
    ]

    for var_name, var_data in data["variables"].items():
        var_data.pop("memory_size", None)
        var_data.pop("hashable", None)

        for key in ["histogram", "length_histogram", "histogram_length", "bin_edges"]:
            var_data.pop(key, None)

        col_type = var_data.get("type", "")
        value_counts = var_data.get("value_counts_index_sorted", {})

        if col_type == "Numeric":
            var_data["value_counts_index_sorted"] = dict(
                list(value_counts.items())[:10]
            )
        elif col_type == "Text":
            var_data.pop("value_counts_without_nan", None)
            var_data["value_counts_index_sorted"] = dict(
                list(value_counts.items())[:10]
            )
            for key in COMMON_TEXT_METADATA:
                var_data.pop(key, None)
            if "category_alias_values" in var_data:
                var_data["category_alias_values"] = dict(
                    list(var_data["category_alias_values"].items())[:10]
                )
            if "word_counts" in var_data:
                sorted_words = sorted(
                    var_data["word_counts"].items(), key=lambda x: x[1], reverse=True
                )[:10]
                var_data["word_counts"] = dict(sorted_words)
        elif col_type == "Categorical":
            for key in CATEGORICAL_TEXT_METADATA + COMMON_TEXT_METADATA:
                var_data.pop(key, None)

    return data


def ReportNode(state:dict):
    """Generate a profile report and save it to a file."""
    df = pd.read_json(StringIO(state["df"]))
    return ({"report": make_serializable(clean_profile_report(df))})

def make_serializable(obj):
    """
    Convert an object to a serializable format.
    """
    if isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_serializable(i) for i in obj]
    elif isinstance(obj, (np.int64, np.int32, np.int16, np.int8)):
        return int(obj)
    elif isinstance(obj, (np.float64, np.float32, np.float16)):
        return float(obj)
    elif isinstance(obj, pd.Interval):
        return {'left': obj.left, 'right': obj.right, 'closed': obj.closed}
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.float64, float)) and (np.isnan(obj) or np.isinf(obj)):
        return None
    else:
        return obj