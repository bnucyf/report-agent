from __future__ import annotations

from typing import Any

from db import fetch_all


def fetch_production_material_usage(limit: int = 5000) -> list[dict[str, Any]]:
    """Production order -> finished goods -> material dispatch detail.

    Uses verified T+ tables from the real database. The result is a long table;
    UI/report layers can pivot it into a material matrix.
    """
    sql = f"""
    SELECT TOP ({int(limit)})
        mo.voucherdate AS order_date,
        mo.code AS manufacture_order_code,
        mo.voucherstate AS manufacture_order_state,
        product.id AS product_inventory_id,
        product.code AS product_code,
        product.name AS product_name,
        product.specification AS product_specification,
        product_unit.name AS product_unit,
        mob.quantity AS product_quantity,
        material.id AS material_inventory_id,
        material.code AS material_code,
        material.name AS material_name,
        material.specification AS material_specification,
        material_unit.name AS material_unit,
        mat.quantity AS planned_material_quantity,
        mat.totalRequisitionedQuantity AS requisitioned_quantity,
        rd.code AS material_dispatch_code,
        rd.voucherdate AS material_dispatch_date,
        rd.idvouchertype AS material_dispatch_voucher_type,
        rd.idbusitype AS material_dispatch_business_type,
        SUM(COALESCE(rdb.quantity, 0)) AS dispatched_quantity,
        SUM(COALESCE(rdb.baseQuantity, 0)) AS dispatched_base_quantity
    FROM dbo.MP_ManufactureOrder mo WITH (NOLOCK)
    INNER JOIN dbo.MP_ManufactureOrder_b mob WITH (NOLOCK)
        ON mob.idManufactureOrderDTO = mo.ID
    LEFT JOIN dbo.AA_InventoryEntity product WITH (NOLOCK)
        ON product.id = mob.idinventory
    LEFT JOIN dbo.AA_Unit product_unit WITH (NOLOCK)
        ON product_unit.id = mob.idunit
    LEFT JOIN dbo.MP_ManufactureOrder_Material mat WITH (NOLOCK)
        ON mat.idManufactureOrderDetailDTO = mob.id
    LEFT JOIN dbo.AA_InventoryEntity material WITH (NOLOCK)
        ON material.id = mat.idinventory
    LEFT JOIN dbo.AA_Unit material_unit WITH (NOLOCK)
        ON material_unit.id = mat.idunit
    LEFT JOIN dbo.ST_RDRecord_b rdb WITH (NOLOCK)
        ON rdb.ManufactureOrderMaterialDetailId = mat.id
    LEFT JOIN dbo.ST_RDRecord rd WITH (NOLOCK)
        ON rd.id = rdb.idRDRecordDTO
    WHERE mo.voucherdate IS NOT NULL
      AND mo.voucherdate >= DATEADD(year, -2, GETDATE())
      AND (rd.id IS NULL OR rd.rdDirectionFlag = 0)
    GROUP BY
        mo.voucherdate,
        mo.code,
        mo.voucherstate,
        product.id,
        product.code,
        product.name,
        product.specification,
        product_unit.name,
        mob.quantity,
        material.id,
        material.code,
        material.name,
        material.specification,
        material_unit.name,
        mat.quantity,
        mat.totalRequisitionedQuantity,
        rd.code,
        rd.voucherdate,
        rd.idvouchertype,
        rd.idbusitype
    ORDER BY mo.voucherdate DESC, mo.code DESC, material.name
    """
    return fetch_all(sql)
