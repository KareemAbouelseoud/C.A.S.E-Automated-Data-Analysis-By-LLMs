import time
import json
import os
import pandas as pd
from ydata_profiling import ProfileReport
from typing import Dict, Any, List


def generate_report(state: Dict[str, Any]) -> Dict[str, Any]:
    df = state["df"]

    reports_dir = os.path.join(os.pardir, "Reports")
    os.makedirs(reports_dir, exist_ok=True)

    dataset_name = state.get("dataset_name", "Dataset")
    safe_name = "".join(c if c.isalnum() else "_" for c in dataset_name)
    report_filename = os.path.join("Reports", f"{safe_name}_report.json")

    start_time = time.time()
    profile = ProfileReport(
        df,
        title=dataset_name,
        explorative=True,
        samples=None,
        interactions=None,
        missing_diagrams=None,
    )
    profile_time = time.time() - start_time

    start_time = time.time()
    profile_json = json.loads(profile.to_json())
    json_time = time.time() - start_time

    # Clean the profile data
    profile_json = _clean_profile_data(profile_json)

    report = {
        "description_insights": {"key_findings": extract_key_findings(profile_json)},
        "dataset_description": state.get("description", ""),
        "metadata": {
            "dataset_name": dataset_name,
            "generation_date": pd.Timestamp.now().isoformat(),
            "profile_generation_sec": round(profile_time, 2),
            "json_conversion_sec": round(json_time, 2),
        },
        "dataset_profile": {
            "overview": profile_json["table"],
            "variables": profile_json["variables"],
            "correlations": profile_json["correlations"]
        },
    }

    with open(report_filename, "w") as f:
        json.dump(report, f, indent=2)

    state["report_path"] = report_filename
    return state


def _clean_profile_data(profile_json: Dict) -> Dict:

    for key in ["scatter", "missing", "package", "interactions"]:
        
        profile_json.pop(key, None)

    profile_json["table"].pop("memory_size", None)
    profile_json["table"].pop("record_size", None)

    # Define metadata keys to remove
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

    variables = profile_json.get("variables", {})
    for var_name, var_data in variables.items():
        var_data.pop("memory_size", None)
        var_data.pop("hashable", None)

        for key in ["histogram", "length_histogram", "histogram_length", "bin_edges"]:
            var_data.pop(key, None)

        col_type = var_data.get("type", "")
        value_counts = var_data.get("value_counts_index_sorted", {})

        if col_type == "Numeric":
            
            # Keep top 10 value counts for numerics
            var_data["value_counts_index_sorted"] = dict(list(value_counts.items())[:10])
        elif col_type == "Text":
            var_data.pop("value_counts_without_nan", None)
            var_data["value_counts_index_sorted"] = dict(list(value_counts.items())[:10])
            
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

    return profile_json


def extract_key_findings(profile: Dict) -> Dict:
    pearson_correlations = profile["correlations"].get("pearson", {})
    return {
        "missing_values": [
            f"{k}: {v['p_missing']}% missing"
            for k, v in profile["variables"].items()
            if v["p_missing"] > 5
        ],
        "skewed_columns": [
            k for k, v in profile["variables"].items() if v.get("skewness", 0) > 2
        ],
        "top_correlations": [
            f"{k[0]} & {k[1]}: {v:.2f}"
            for k, v in pearson_correlations.items()
            if abs(v) > 0.7
        ]
        if pearson_correlations
        else ["No significant numerical correlations found"],
    }


def get_schema(report: Dict) -> List[Dict]:
    return [
        {
            "name": col,
            "type": stats["type"],
            "missing": stats["missing"],
            "unique": stats["unique"],
            **stats["stats"],
        }
        for col, stats in report["dataset_profile"]["variables"].items()
    ]