# 智能报表数据地图

生成时间：2026-07-03 11:40:07

## 数据库概览

- 表数量：13751
- 字段数量：160898
- 非空表数量：9536
- 估算总行数：83865344

## 业务表候选 Top 30

| 模块 | 表 | 行数 | 命中关键词 |
| --- | --- | ---: | --- |
| 库存出入库 | `dbo.ST_RDRecord_b` | 1008417 | account, ap, ar, arrival, customer, dispatch, gl, inventory, manufacture, material, mo, partner, process, project, purchase, rdrecord, receive, sale, settle, st_rdrecord, st_rdrecord_b, stock, unit, vendor, voucher, warehouse |
| 生产加工 | `dbo.MP_ManufactureOrder_b` | 98835 | account, ar, bom, customer, dispatch, inventory, manufacture, material, mo, mp_manufactureorder, mp_manufactureorder_b, process, productive, project, sale, saledelivery, stock, unit, voucher, warehouse |
| 生产加工 | `dbo.MP_ManufactureOrder_Material` | 741738 | ar, bom, dispatch, inventory, manufacture, material, mo, mp_manufactureorder, mp_manufactureorder_material, process, stock, unit, voucher, warehouse |
| 基础档案 | `dbo.AA_InventoryEntity` | 23028 | aa_inventoryentity, ap, ar, customer, gl, inventory, inventoryentity, manufacture, material, mo, partner, process, productive, project, purchase, sale, settle, stock, unit, voucher, warehouse |
| 库存出入库 | `dbo.ST_RDRecord` | 126124 | account, ap, ar, arrival, customer, dispatch, manufacture, mo, partner, project, purchase, rdrecord, receive, sale, saledelivery, settle, st_rdrecord, stock, voucher, warehouse |
| 库存出入库 | `dbo.ST_SubsidiaryBook` | 1014698 | account, ar, inventory, mo, purchase, settle, st_subsidiarybook, stock, subsidiarybook, unit, voucher, warehouse |
| 销售 | `dbo.SA_SaleDelivery` | 3248 | ap, ar, customer, dispatch, mo, project, receive, sa_saledelivery, sale, saledelivery, settle, stock, voucher, warehouse |
| 往来与财务 | `dbo.GL_Journal` | 2948 | account, ar, customer, gl, gl_, inventory, mo, partner, project, settle, supplier, unit |
| 往来与财务 | `dbo.GL_Entry` | 2220 | account, ap, ar, gl, gl_, mo, partner, site, unit |
| 往来与财务 | `dbo.GL_AuxiliaryInfo` | 1574 | account, ar, customer, gl, gl_, inventory, project, settle |
| 销售 | `dbo.SA_SaleOrder` | 1390 | ar, bom, customer, dispatch, mo, project, receive, sa_saleorder, sale, saledelivery, settle, voucher, warehouse |
| 往来与财务 | `dbo.GL_Doc` | 828 | account, ar, gl, gl_, mo, site, voucher |
| 往来与财务 | `dbo.GL_AccountAuxPeriodBeginDetail` | 625 | account, ar, customer, gl, gl_, inventory, mo, project, supplier, unit, voucher |
| 销售 | `dbo.SA_SaleOrderChange` | 115 | ar, bom, customer, dispatch, mo, project, receive, sa_saleorder, sale, saledelivery, settle, voucher, warehouse |
| 往来与财务 | `dbo.GL_ReferenceDoc` | 77 | account, ar, gl, gl_, mo, site, voucher |
| 往来与财务 | `dbo.GL_TemplateDoc` | 17 | account, ar, customer, gl, gl_, inventory, mo, project, site, voucher |
| 生产加工 | `dbo.MP_ManufactureOrder` | 38851 | account, ar, customer, dispatch, manufacture, material, mo, mp_manufactureorder, project, receive, sale, voucher |
| 往来与财务 | `dbo.GL_SrcVoucherInfo` | 3330 | ar, customer, dispatch, gl, gl_, mo, sale, supplier, voucher |
| 往来与财务 | `dbo.GL_AccountPeriodBeginDetail` | 692 | account, ar, customer, gl, gl_, inventory, mo, project, supplier, unit |
| 往来与财务 | `dbo.GL_WriteOffJournal` | 625 | account, ar, customer, gl, gl_, inventory, mo, project |
| 基础档案 | `dbo.aa_partnerclassprice` | 500 | aa_partner, ar, inventory, partner, unit |
| 基础档案 | `dbo.AA_CustomerInventoryPrice` | 496 | aa_customer, ar, customer, inventory, unit |
| 往来与财务 | `dbo.GL_CashFlowInfo` | 493 | account, ap, gl, gl_, mo |
| 往来与财务 | `dbo.GL_ReferenceEntry` | 201 | account, ar, gl, gl_, mo, unit |
| 往来与财务 | `dbo.GL_TemplateDocEntry` | 60 | account, ar, gl, gl_, mo, unit |
| 往来与财务 | `dbo.GL_AccountPeriodBegin` | 46 | account, ar, gl, gl_, mo |
| 采购 | `dbo.PU_PurchaseArrival_SourceRelation` | 124426 | ar, arrival, pu_purchasearrival, purchase, unit, voucher |
| 库存出入库 | `dbo.ST_SubsidiaryBookLock` | 100002 | ar, inventory, st_subsidiarybook, subsidiarybook |
| 采购 | `dbo.PU_PurchaseArrival_b` | 45014 | account, ap, ar, arrival, inventory, mo, partner, project, pu_purchasearrival, purchase, receive, sale, settle, stock, unit, voucher, warehouse |
| 采购 | `dbo.PU_PurchaseOrder_b` | 42600 | ar, arrival, inventory, manufacture, mo, partner, project, pu_purchaseorder, purchase, sale, stock, unit, voucher, warehouse |

## 数据质量问题 Top 30

| 表 | 字段 | 问题 | 数量 | 比例 |
| --- | --- | --- | ---: | ---: |
| `dbo.ST_RDRecord_b` | `subQuantity` | 空值 | 200 | 100.00% |
| `dbo.ST_RDRecord_b` | `estimatedPrice2` | 空值 | 200 | 100.00% |
| `dbo.ST_RDRecord_b` | `estimatedPrice` | 空值 | 200 | 100.00% |
| `dbo.ST_RDRecord_b` | `cumulativeSettlementQuantity` | 空值 | 200 | 100.00% |
| `dbo.ST_RDRecord_b` | `cumulativeSettlementQuantity2` | 空值 | 200 | 100.00% |
| `dbo.ST_RDRecord_b` | `cumulativeSettlementSubQuantity` | 空值 | 200 | 100.00% |
| `dbo.ST_RDRecord_b` | `receiveAdjust` | 空值 | 200 | 100.00% |
| `dbo.ST_RDRecord_b` | `dispatchAdjust` | 空值 | 200 | 100.00% |
| `dbo.MP_ManufactureOrder_b` | `name` | 空值 | 200 | 100.00% |
| `dbo.MP_ManufactureOrder_b` | `sourceVoucherCode` | 空值 | 200 | 100.00% |
| `dbo.MP_ManufactureOrder_b` | `bomType` | 空值 | 200 | 100.00% |
| `dbo.MP_ManufactureOrder_b` | `batch` | 空值 | 200 | 100.00% |
| `dbo.MP_ManufactureOrder_b` | `totalCheckedAccount` | 空值 | 200 | 100.00% |
| `dbo.MP_ManufactureOrder_b` | `totalCheckedQuantity` | 空值 | 200 | 100.00% |
| `dbo.MP_ManufactureOrder_b` | `isNoModify` | 空值 | 200 | 100.00% |
| `dbo.MP_ManufactureOrder_b` | `priuserdefnvc1` | 空值 | 200 | 100.00% |
| `dbo.MP_ManufactureOrder_Material` | `name` | 空值 | 200 | 100.00% |
| `dbo.MP_ManufactureOrder_Material` | `sonLossQuantity` | 空值 | 200 | 100.00% |
| `dbo.MP_ManufactureOrder_Material` | `sonLossQuantity2` | 空值 | 200 | 100.00% |
| `dbo.MP_ManufactureOrder_Material` | `batch` | 空值 | 200 | 100.00% |
| `dbo.MP_ManufactureOrder_Material` | `totalStockOutCost` | 空值 | 200 | 100.00% |
| `dbo.MP_ManufactureOrder_Material` | `SonLossSubQuantity` | 空值 | 200 | 100.00% |
| `dbo.MP_ManufactureOrder_Material` | `WholeSuitMaterialQuantity` | 空值 | 200 | 100.00% |
| `dbo.MP_ManufactureOrder_Material` | `priuserdefnvc1` | 空值 | 200 | 100.00% |
| `dbo.AA_InventoryEntity` | `procureBatch` | 空值 | 200 | 100.00% |
| `dbo.AA_InventoryEntity` | `invSCost` | 空值 | 200 | 100.00% |
| `dbo.AA_InventoryEntity` | `latestCost_Abandon` | 空值 | 200 | 100.00% |
| `dbo.AA_InventoryEntity` | `avagCost_Abandon` | 空值 | 200 | 100.00% |
| `dbo.AA_InventoryEntity` | `safeQuantity` | 空值 | 200 | 100.00% |
| `dbo.AA_InventoryEntity` | `picture` | 空值 | 200 | 100.00% |

> 数据字典仅供参考，本数据地图以真实数据库扫描结果为准。
