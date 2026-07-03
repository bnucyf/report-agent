from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = ROOT_DIR / "outputs" / "snapshots"
REPORT_DIR = ROOT_DIR / "outputs" / "reports"


def latest_file(pattern: str, directory: Path = SNAPSHOT_DIR) -> Path | None:
    files = sorted(directory.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def read_csv(pattern: str) -> pd.DataFrame:
    path = latest_file(pattern)
    if not path:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def read_json(pattern: str) -> dict[str, Any]:
    path = latest_file(pattern)
    if not path:
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def load_snapshot_bundle() -> dict[str, Any]:
    return {
        "tables": read_csv("tables_*.csv"),
        "candidates": read_csv("business_candidates_*.csv"),
        "issues": read_csv("quality_issues_*.csv"),
        "usage": read_csv("production_material_usage_*.csv"),
        "field_inventory": read_csv("field_inventory_*.csv"),
        "summary": read_json("summary_*.json"),
        "field_summary": read_json("field_inventory_summary_*.json"),
    }


def latest_report() -> Path | None:
    return latest_file("smart-report-demo_*.html", REPORT_DIR)


def as_number(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(0)
