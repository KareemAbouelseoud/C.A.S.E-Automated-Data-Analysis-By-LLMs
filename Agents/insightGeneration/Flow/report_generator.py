import time
import json
import os
import pandas as pd
from ydata_profiling import ProfileReport
from typing import Dict, Any


def generate_report(state: Dict[str, Any]) -> Dict[str, Any]:
    df = state["df"]

    reports_dir = os.path.join(os.pardir, "Reports")
    os.makedirs(reports_dir, exist_ok=True)

    dataset_name = state.get("dataset_name", "Dataset")
    safe_name = "".join(c if c.isalnum() else "_" for c in dataset_name)
    report_filename = os.path.join("Reports", f"{safe_name}_report.json")

    start_time = time.time()
    profile = ProfileReport(df, title=dataset_name, explorative=True)
    profile_time = time.time() - start_time

    start_time = time.time()
    profile_json = json.loads(profile.to_json())
    json_time = time.time() - start_time

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
            "correlations": profile_json["correlations"],
            "missing_values": profile_json["missing"],
            "sample_data": df.head(3).to_dict(orient="list"),
        },
    }

    with open(report_filename, "w") as f:
        json.dump(report, f, indent=2)

    state["report_path"] = report_filename
    return state


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


def get_schema(report: Dict) -> list[Dict]:
    return [
        {
            "name": col,
            "type": stats["type"],
            "missing": stats["missing"],
            "unique": stats["unique"],
            **stats["stats"],
        }
        for col, stats in report["schema"].items()
    ]
