from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

from data_loader import latest_file
from db import ROOT_DIR

CHM_PATH = ROOT_DIR / "TPlus160 数据字典.chm"
DECOMPILE_DIR = ROOT_DIR / "outputs" / "chm_decompile"
DICT_JSON_PATH = DECOMPILE_DIR / "chm_descriptions.json"
REPORT_PATH = ROOT_DIR / "outputs" / "reports" / "chm_field_supplement.csv"


def discover_html_files(directory: Path) -> list[Path]:
    return sorted([p for p in directory.rglob("*.html") if p.stem and not p.stem.startswith("#")])


def parse_table_html(html_path: Path) -> dict[str, Any] | None:
    try:
        raw = html_path.read_text(encoding="gb2312", errors="ignore")
    except Exception:
        raw = html_path.read_text(encoding="utf-8", errors="ignore")

    soup = BeautifulSoup(raw, "html.parser")

    title_tag = soup.find("title")
    if not title_tag:
        return None
    title_text = title_tag.get_text(strip=True)
    table_match = re.search(r"([A-Za-z_][A-Za-z0-9_]*)\s+Table", title_text)
    if not table_match:
        return None
    table_name = table_match.group(1)

    module = ""
    h1 = soup.find("h1")
    if h1:
        h1_text = h1.get_text(" ", strip=True)
        module_match = re.search(r"[\[(]([^\])]+)[\])]", h1_text)
        if module_match:
            module = module_match.group(1).strip()

    summary = ""
    summary_header = soup.find("h4", string=re.compile("Summary", re.I))
    if summary_header:
        next_p = summary_header.find_next_sibling("p")
        if next_p:
            summary = next_p.get_text(strip=True)

    columns: list[dict[str, str]] = []
    columns_header = soup.find("h4", string=re.compile("Columns", re.I))
    if columns_header:
        table = columns_header.find_next_sibling("table")
        if table:
            rows = table.find_all("tr")
            for row in rows[1:]:  # skip header
                cells = row.find_all("td")
                if len(cells) < 3:
                    continue
                # cell[1] contains <strong>ColumnName</strong>, cell[2] is description
                name_cell = cells[1]
                desc_cell = cells[2]
                name_text = name_cell.get_text(" ", strip=True)
                # remove (T+12.1) version suffix
                name_text = re.sub(r"\s*\(T\+[\d.]+\)\s*$", "", name_text).strip()
                desc_text = desc_cell.get_text(" ", strip=True)
                if name_text:
                    columns.append({"column_name": name_text, "description": desc_text})

    return {
        "table_name": table_name,
        "module": module,
        "summary": summary,
        "columns": columns,
        "source_html": html_path.name,
    }


def build_description_dict(directory: Path) -> dict[str, dict[str, Any]]:
    files = discover_html_files(directory)
    descriptions: dict[str, dict[str, Any]] = {}
    for html_path in files:
        parsed = parse_table_html(html_path)
        if parsed:
            descriptions[parsed["table_name"].lower()] = parsed
    return descriptions


def ensure_decompiled() -> Path:
    if not DECOMPILE_DIR.exists() or not any(DECOMPILE_DIR.iterdir()):
        raise FileNotFoundError(
            f"CHM 尚未解压。请先用 7z 解压：\n"
            f'"C:/Program Files/NVIDIA Corporation/NVIDIA app/7z.exe" x "{CHM_PATH}" '
            f'-o"{DECOMPILE_DIR}" -y'
        )
    return DECOMPILE_DIR


def load_or_build_descriptions() -> dict[str, dict[str, Any]]:
    if DICT_JSON_PATH.exists():
        return json.loads(DICT_JSON_PATH.read_text(encoding="utf-8"))
    ensure_decompiled()
    descriptions = build_description_dict(DECOMPILE_DIR)
    DICT_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    DICT_JSON_PATH.write_text(json.dumps(descriptions, ensure_ascii=False, indent=2), encoding="utf-8")
    return descriptions


def supplement_field_inventory(field_inventory_path: Path | None = None) -> dict[str, Any]:
    if field_inventory_path is None:
        field_inventory_path = latest_file("field_inventory_*.csv")
    if not field_inventory_path or not field_inventory_path.exists():
        return {"status": "missing_snapshot", "message": "未找到 field_inventory 快照"}

    import pandas as pd

    df = pd.read_csv(field_inventory_path, encoding="utf-8-sig", low_memory=False)
    descriptions = load_or_build_descriptions()

    table_descs: list[str] = []
    col_descs: list[str] = []
    matched: list[bool] = []

    for _, row in df.iterrows():
        table_name = str(row.get("table_name", "")).strip()
        column_name = str(row.get("column_name", "")).strip()
        table_key = table_name.lower()

        table_info = descriptions.get(table_key)
        if table_info:
            table_descs.append(table_info.get("summary", ""))
            col_match = next(
                (c for c in table_info.get("columns", []) if c["column_name"].lower() == column_name.lower()),
                None,
            )
            if col_match:
                col_descs.append(col_match["description"])
                matched.append(True)
            else:
                col_descs.append("")
                matched.append(False)
        else:
            table_descs.append("")
            col_descs.append("")
            matched.append(False)

    df["table_description_dict"] = table_descs
    df["column_description_dict"] = col_descs
    df["dict_matched"] = matched

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(REPORT_PATH, index=False, encoding="utf-8-sig")

    matched_count = sum(matched)
    table_matched = df[df["table_name"].str.lower().isin(descriptions.keys())]["table_name"].nunique()

    return {
        "status": "ok",
        "dict_path": str(DICT_JSON_PATH),
        "report_path": str(REPORT_PATH),
        "total_fields": len(df),
        "matched_fields": matched_count,
        "matched_tables": table_matched,
        "dict_tables": len(descriptions),
        "sample_matches": df[df["dict_matched"]][["full_table_name", "column_name", "column_description_dict"]].head(20).to_dict("records"),
    }


def main() -> None:
    result = supplement_field_inventory()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
