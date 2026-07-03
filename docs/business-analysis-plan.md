# 业务分析板块设计：生产加工单与材料出库分析

## 需求定位

客户希望不仅看到数据质量诊断，还要看到常规、可解释、可展示的业务分析结果。业务分析板块与数据质量分析板块同等重要，应在 Demo 和后续系统中分开呈现。

当前新增核心场景：

> 根据生产加工单统计各成品对应材料在材料出库单中的出库数量。

目标输出示例：

| 单据日期 | 加工单号 | 产品名称 | 规格型号 | 主单位 | 主数量 | 材料1 | 材料2 | 材料3 |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: |
| 2026-05-17 | MO-2026-05-0446 | 成品A | 规格A | 件 | 100 | 20 | 35 | 8 |

## 已验证的真实数据库线索

以下结论基于真实 SQL Server 表结构与抽样读取，不依赖数据字典。

### 1. 生产加工单主表

表：`dbo.MP_ManufactureOrder`

关键字段：

- `ID`：加工单主表 ID
- `code`：加工单号，例如 `MO-2026-06-0002`
- `voucherdate`：单据日期
- `voucherstate`：单据状态
- `IsAutoCreateMaterialDispatch`：是否自动生成材料出库

### 2. 生产加工单产品明细

表：`dbo.MP_ManufactureOrder_b`

关键字段：

- `id`：加工单产品明细 ID
- `idManufactureOrderDTO`：关联 `MP_ManufactureOrder.ID`
- `idinventory`：成品存货 ID
- `idunit`：单位 ID
- `quantity`：主数量
- `baseQuantity`：基础数量
- `code`：明细行号

### 3. 生产加工单材料明细

表：`dbo.MP_ManufactureOrder_Material`

关键字段：

- `id`：材料明细 ID
- `voucherId`：关联 `MP_ManufactureOrder.ID`
- `idManufactureOrderDetailDTO`：关联 `MP_ManufactureOrder_b.id`
- `idinventory`：材料存货 ID
- `idunit`：材料单位 ID
- `quantity`：计划/需求材料数量
- `totalRequisitionedQuantity`：累计领用数量
- `TotalDispatchingMaterialQuantity`：累计派工/发料相关数量，当前抽样中存在空值

### 4. 材料出库单主表

表：`dbo.ST_RDRecord`

关键字段：

- `id`：出入库单主表 ID
- `code`：出入库单号，例如 `MD-2026-05-0368`
- `voucherdate`：单据日期
- `ManufactureOrderCode`：加工单号
- `sourceVoucherCode`：来源单据号
- `idvouchertype`：单据类型，抽样中材料出库相关为 `21`
- `idbusitype`：业务类型，抽样中存在 `55`、`53`
- `rdDirectionFlag`：出入库方向，抽样中材料出库为 `0`

### 5. 材料出库单明细

表：`dbo.ST_RDRecord_b`

关键字段：

- `ID`：出入库明细 ID
- `idRDRecordDTO`：关联 `ST_RDRecord.id`
- `ManufactureOrderId`：关联 `MP_ManufactureOrder.ID`
- `ManufactureOrderDetailId`：关联 `MP_ManufactureOrder_b.id`
- `ManufactureOrderMaterialDetailId`：关联 `MP_ManufactureOrder_Material.id`
- `idinventory`：材料存货 ID
- `idunit`：材料单位 ID
- `quantity`：出库数量
- `baseQuantity`：基础出库数量

### 6. 存货与单位基础档案

已发现候选表：

- `dbo.AA_InventoryEntity`：存货档案候选，行数约 23028
- `dbo.AA_Unit`：单位档案，行数 81
- `dbo.AA_Inventory_MultiUnit`：多计量单位，行数约 2012

后续需进一步确认存货名称、规格型号字段所在表。当前不能只凭数据字典硬编码。

## 推荐统计口径

第一版业务分析建议以真实关联字段为主：

```text
MP_ManufactureOrder.ID
  -> MP_ManufactureOrder_b.idManufactureOrderDTO
  -> MP_ManufactureOrder_Material.idManufactureOrderDetailDTO
  -> ST_RDRecord_b.ManufactureOrderMaterialDetailId
  -> ST_RDRecord_b.idRDRecordDTO = ST_RDRecord.id
```

其中：

- 加工单日期：`MP_ManufactureOrder.voucherdate`
- 加工单号：`MP_ManufactureOrder.code`
- 成品：`MP_ManufactureOrder_b.idinventory` 关联存货档案
- 成品数量：`MP_ManufactureOrder_b.quantity` 或 `baseQuantity`
- 材料：`ST_RDRecord_b.idinventory` 关联存货档案
- 材料实际出库数量：`SUM(ST_RDRecord_b.quantity)` 或 `SUM(ST_RDRecord_b.baseQuantity)`

## 报表形态

### 1. 明细矩阵表

按加工单 + 成品聚合，材料横向展开：

| 单据日期 | 加工单号 | 产品名称 | 规格型号 | 主单位 | 主数量 | 材料A | 材料B | 材料C |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: |

说明：

- 横向材料列适合客户看结果，但材料种类过多时列会膨胀。
- 系统中应同时保留长表结构：加工单、成品、材料、出库数量。
- 展示层再做 pivot，选 Top N 材料横向展示。

### 2. 长表明细

| 单据日期 | 加工单号 | 成品 | 成品规格 | 成品单位 | 成品数量 | 材料 | 材料规格 | 材料单位 | 材料出库数量 | 材料出库单号 |
| --- | --- | --- | --- | --- | ---: | --- | --- | --- | ---: | --- |

长表适合：

- 明细追溯
- 导出 Excel
- 后续可视化
- 异常检查

## 可视化内容

业务分析板块建议至少包含以下图表：

1. 成品材料消耗矩阵
   - 行：加工单/成品
   - 列：主要材料
   - 值：材料出库数量

2. 成品材料消耗 Top N
   - 维度：成品
   - 指标：材料出库总量或材料种类数
   - 图表：柱状图

3. 材料消耗排行
   - 维度：材料
   - 指标：出库数量
   - 图表：柱状图/帕累托图

4. 加工单领料完整性
   - 应领数量：`MP_ManufactureOrder_Material.quantity` 或 `totalRequisitionedQuantity`
   - 实际出库数量：`ST_RDRecord_b.quantity`
   - 差异：实际出库 - 应领数量
   - 图表：差异条形图

5. 加工单追溯明细
   - 从加工单钻取到成品、材料、材料出库单号、出库日期、数量

## 页面结构调整

原系统不应只有数据质量诊断。建议分成两个一级板块：

### A. 业务分析

面向老板和业务负责人，回答“经营和生产发生了什么”。

首批页面：

1. 生产加工用料分析
2. 材料出库排行
3. 成品材料消耗矩阵
4. 加工单领料差异分析

### B. 数据质量

面向数据治理和系统录入人员，回答“数据为什么不准”。

首批页面：

1. 缺失率
2. 重复记录
3. 异常日期
4. 单据关联缺失
5. 基础档案缺失

## 第一版 SQL 方向草案

注意：以下 SQL 是方向草案，正式实现前还需确认存货档案表字段名。

```sql
SELECT
    mo.voucherdate AS 单据日期,
    mo.code AS 加工单号,
    mob.idinventory AS 成品ID,
    mob.quantity AS 主数量,
    mat.idinventory AS 计划材料ID,
    rdb.idinventory AS 出库材料ID,
    SUM(rdb.quantity) AS 材料出库数量
FROM dbo.MP_ManufactureOrder mo WITH (NOLOCK)
JOIN dbo.MP_ManufactureOrder_b mob WITH (NOLOCK)
    ON mob.idManufactureOrderDTO = mo.ID
LEFT JOIN dbo.MP_ManufactureOrder_Material mat WITH (NOLOCK)
    ON mat.idManufactureOrderDetailDTO = mob.id
LEFT JOIN dbo.ST_RDRecord_b rdb WITH (NOLOCK)
    ON rdb.ManufactureOrderMaterialDetailId = mat.id
LEFT JOIN dbo.ST_RDRecord rd WITH (NOLOCK)
    ON rd.id = rdb.idRDRecordDTO
WHERE mo.voucherdate >= @start_date
  AND mo.voucherdate < @end_date
GROUP BY
    mo.voucherdate,
    mo.code,
    mob.idinventory,
    mob.quantity,
    mat.idinventory,
    rdb.idinventory;
```

## 需要继续确认的问题

1. 成品名称、规格型号字段实际在哪张存货表中，候选是 `AA_InventoryEntity`。
2. 材料名称、规格型号字段实际在哪张存货表中。
3. `ST_RDRecord.idvouchertype = 21` 是否就是材料出库单。
4. `ST_RDRecord.idbusitype = 55` 和 `53` 的业务含义。
5. 材料实际出库数量以 `quantity`、`baseQuantity` 还是 `quantity2` 为准。
6. 主单位名称是否取 `AA_Unit.name`。
7. 是否只统计已审核加工单/出库单，审核状态字段口径需要确认。
8. 报表日期按加工单日期还是材料出库日期。
9. 多材料横向展开时展示全部材料还是 Top N 材料。

## 产品结论

这个需求应作为智能报表 Demo 的核心业务分析样例。它比单纯数据质量诊断更容易向客户证明价值：

- 能把 T+ 复杂底层表自动关联成业务可读报表。
- 能回答每张加工单实际消耗了哪些材料。
- 能进一步发现应领、实领、出库之间的差异。
- 能把“老板觉得数据不准”的问题落到具体加工单、材料、出库单。
