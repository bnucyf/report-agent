from __future__ import annotations

from collections import defaultdict
from typing import Any


EXCLUDED_PREFIXES = (
    "temp_",
    "tmp_",
    "eap_",
    "rpt_",
    "z_",
)

EXCLUDED_CONTAINS = (
    "_rpt_",
    "report",
    "log",
    "trace",
    "uploadlog",
    "history",
    "bak",
    "backup",
    "index",
    "groupsum",
)

SYSTEM_PREFIXES = (
    "sm_",
    "eap_",
    "sys_",
)

MODULES = {
    "manufacturing": {
        "label": "生产加工",
        "strong_tables": ["mp_manufactureorder", "mp_manufactureorder_b", "mp_manufactureorder_material"],
        "keywords": ["manufacture", "material", "bom", "process", "productive", "mo", "生产", "加工", "材料", "用料", "工序"],
    },
    "stock_io": {
        "label": "库存出入库",
        "strong_tables": ["st_rdrecord", "st_rdrecord_b", "st_subsidiarybook", "st_currentstock"],
        "keywords": ["rdrecord", "subsidiarybook", "currentstock", "stock", "warehouse", "inventory", "dispatch", "receive", "库存", "仓库", "出库", "入库"],
    },
    "master_data": {
        "label": "基础档案",
        "strong_tables": ["aa_inventoryentity", "aa_unit", "aa_inventory_multiunit", "aa_warehouse", "aa_partner", "aa_customer", "aa_vendor"],
        "keywords": ["inventoryentity", "inventory", "unit", "warehouse", "partner", "customer", "vendor", "存货", "单位", "仓库", "客户", "供应商"],
    },
    "sales": {
        "label": "销售",
        "strong_tables": ["sa_saleorder", "sa_saledelivery", "sa_dispatch"],
        "keywords": ["sale", "sales", "saledelivery", "dispatch", "customer", "销售", "客户", "发货", "订单"],
    },
    "purchase": {
        "label": "采购",
        "strong_tables": ["pu_purchaseorder", "pu_purchasearrival"],
        "keywords": ["purchase", "arrival", "vendor", "supplier", "采购", "到货", "供应商"],
    },
    "finance": {
        "label": "往来与财务",
        "strong_tables": ["ar_", "ap_", "gl_"],
        "keywords": ["account", "receivable", "payable", "voucher", "settle", "ar", "ap", "gl", "往来", "应收", "应付", "凭证", "结算"],
    },
    "project": {
        "label": "项目与施工",
        "strong_tables": ["aa_project"],
        "keywords": ["project", "job", "site", "construct", "task", "项目", "施工", "工地", "现场"],
    },
}


def is_excluded_table(table_name: str) -> bool:
    name = table_name.lower()
    if name.startswith(EXCLUDED_PREFIXES):
        return True
    return any(token in name for token in EXCLUDED_CONTAINS)


def table_priority(table_name: str) -> int:
    name = table_name.lower()
    if name.startswith(SYSTEM_PREFIXES):
        return -1
    return 0


def classify_tables(tables: list[dict[str, Any]], column_map: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for table in tables:
        table_name = str(table["table_name"])
        if is_excluded_table(table_name):
            continue

        key = f"{table['schema_name']}.{table_name}"
        cols = column_map.get(key, [])
        haystack_parts = [table_name]
        haystack_parts.extend(str(col["column_name"]) for col in cols)
        haystack = " ".join(haystack_parts).lower()
        table_lower = table_name.lower()

        module_hits: dict[str, list[str]] = defaultdict(list)
        strong_score: dict[str, int] = defaultdict(int)
        for module_key, module in MODULES.items():
            for strong_table in module["strong_tables"]:
                if table_lower == strong_table or table_lower.startswith(strong_table):
                    strong_score[module_key] += 10
                    module_hits[module_key].append(strong_table)
            for keyword in module["keywords"]:
                if keyword.lower() in haystack:
                    module_hits[module_key].append(keyword)

        if not module_hits:
            continue

        def score(module_key: str) -> int:
            return strong_score[module_key] + len(set(module_hits[module_key])) + table_priority(table_name)

        best_module = max(module_hits.keys(), key=score)
        final_score = score(best_module)
        if final_score <= 0:
            continue

        results.append(
            {
                "schema_name": table["schema_name"],
                "table_name": table_name,
                "full_name": key,
                "row_count": int(table.get("row_count") or 0),
                "module": best_module,
                "module_label": MODULES[best_module]["label"],
                "score": final_score,
                "matched_keywords": ", ".join(sorted({kw for hits in module_hits.values() for kw in hits})),
                "column_count": len(cols),
            }
        )
    return sorted(results, key=lambda row: (row["score"], row["row_count"]), reverse=True)
