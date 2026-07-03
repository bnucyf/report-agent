# SQL Server 数据库字段内容整理与业务分析报告

生成时间：2026-07-03 11:40:07

## 1. 数据资产概览

- 表总数：13751
- 清洗后非噪声表数：1308
- 字段总数：39496
- 估算总行数：83865344
- 时间字段数：3925
- 金额字段数：6855
- 数量字段数：5326

## 2. 模块分布

| 模块 | 表数量 | 估算行数 |
| --- | ---: | ---: |
| 其他 | 368 | 1310116 |
| 财务/会计 | 285 | 963316 |
| 基础档案 | 222 | 27322 |
| 生产/加工 | 157 | 2109118 |
| 库存/仓库 | 137 | 4438848 |
| 销售 | 64 | 47394 |
| 系统/流程 | 43 | 36316 |
| 采购 | 32 | 338347 |

## 3. 重点大表

| 表 | 行数 | 创建时间 | 修改时间 |
| --- | ---: | --- | --- |
| `dbo.ST_SubsidiaryBook` | 1014698 | 2009-05-25T20:57:13.140000 | 2026-04-27T01:05:50.240000 |
| `dbo.ST_RDRecord_b` | 1008417 | 2009-05-25T20:57:13.153000 | 2026-04-30T01:07:13.557000 |
| `dbo.ST_RDRecordSourceRelation` | 838334 | 2009-05-25T20:57:13.310000 | 2026-03-13T01:06:19.003000 |
| `dbo.MP_ManufactureOrder_Material` | 741738 | 2012-07-04T17:58:46.217000 | 2026-04-18T01:05:44.790000 |
| `dbo.RCHK_CostAnalysis` | 627485 | 2026-04-27T02:10:25.797000 | 2026-04-27T02:10:25.810000 |
| `dbo.ST_SummaryBook` | 601367 | 2009-05-25T20:57:13.327000 | 2026-03-11T01:06:10.360000 |
| `dbo.ST_LocationDetail` | 470971 | 2009-05-25T20:57:13.373000 | 2026-03-20T01:03:58.543000 |
| `dbo.MP_CostAllocationDirectMaterialSumOrder_s` | 440242 | 2014-04-01T21:18:21.410000 | 2026-04-10T01:05:24.133000 |
| `dbo.MP_CostAllocationDirectMaterialSumOrder_b` | 429387 | 2014-04-01T21:18:21.487000 | 2026-04-10T01:05:19.327000 |
| `dbo.RCHK_STFund` | 295996 | 2026-04-27T02:10:10.520000 | 2026-04-27T02:10:10.533000 |
| `dbo.ME_Integral_Lock` | 131072 | 2021-03-27T22:55:46.703000 | 2021-03-27T22:55:46.703000 |
| `dbo.ST_RDRecord` | 126124 | 2009-05-25T20:57:13.310000 | 2026-04-18T01:05:56.773000 |
| `dbo.PU_PurchaseArrival_SourceRelation` | 124426 | 2009-05-25T20:57:11.467000 | 2026-04-25T01:05:14.523000 |
| `dbo.ARAP_Detail` | 103096 | 2009-05-25T20:57:10.060000 | 2026-04-18T01:05:14.527000 |
| `dbo.ST_SubsidiaryBookLock` | 100002 | 2017-12-19T22:16:41.890000 | 2017-12-19T22:16:41.890000 |
| `dbo.MP_ManufactureOrder_b` | 98835 | 2012-07-04T17:58:46.170000 | 2026-04-16T01:05:00.617000 |
| `dbo.ST_PositionAdjustVoucher_b` | 98563 | 2009-05-25T20:57:13.153000 | 2026-04-20T01:05:02.477000 |
| `dbo.MP_CostAllocationOrder_src` | 84169 | 2014-04-01T21:18:21.223000 | 2026-04-09T01:04:46.587000 |
| `dbo.MP_CostAllocationDirectMaterialSumOrder` | 81371 | 2014-04-01T21:18:21.503000 | 2026-04-09T01:04:39.197000 |
| `dbo.MP_CostAllocationOrder_b` | 81371 | 2014-04-01T21:18:21.393000 | 2026-04-09T01:04:44.170000 |
| `dbo.ST_NewCurrentStock` | 67741 | 2019-01-05T18:18:30.263000 | 2026-05-06T01:06:46.357000 |
| `dbo.ARAP_Cancel_FirstDetail` | 65832 | 2016-01-29T19:51:29.993000 | 2022-11-03T01:01:07.283000 |
| `dbo.ST_TransVoucher_b` | 61594 | 2009-05-25T20:57:13.123000 | 2026-04-11T01:04:51.030000 |
| `dbo.ST_CheckVoucher_b` | 54658 | 2009-05-25T20:57:13.327000 | 2026-03-12T01:04:22.260000 |
| `dbo.CM_BasicValueCalcResult` | 51665 | 2021-03-27T22:48:25.023000 | 2026-04-27T01:05:35.673000 |
| `dbo.ARAP_DetailSecond` | 49993 | 2011-03-09T16:34:48.263000 | 2026-04-16T01:04:45.593000 |
| `dbo.CS_CashAccount` | 49944 | 2009-05-25T20:57:10.920000 | 2026-04-08T01:04:20.277000 |
| `dbo.RCHK_TargetManagement` | 47184 | 2021-03-27T22:48:16.467000 | 2023-05-09T01:08:29.483000 |
| `dbo.PU_PurchaseArrival_b` | 45014 | 2009-05-25T20:57:11.483000 | 2026-04-17T01:05:09.053000 |
| `dbo.ST_PurchaseSettleVoucher_b` | 44895 | 2009-05-25T20:57:13.140000 | 2026-04-24T01:05:21.187000 |

## 4. 字段类型与语义

### 字段类型分类

| 类型分类 | 字段数 |
| --- | ---: |
| 编码/状态/外键 | 13289 |
| 文本/编码 | 12903 |
| 金额/数量 | 9405 |
| 时间 | 2518 |
| 系统版本 | 993 |
| 布尔标记 | 294 |
| 二进制/系统 | 66 |
| 文本/备注 | 15 |
| 其他 | 13 |

### 字段语义分类

| 语义 | 字段数 |
| --- | ---: |
| 未识别 | 7117 |
| 单据 | 5755 |
| 状态 | 1816 |
| 金额 | 1638 |
| 数量 | 1313 |
| 日期时间 | 1178 |
| 存货物料 | 1057 |
| 金额, 单据 | 1028 |
| 客户供应商 | 986 |
| 生产加工 | 913 |
| 仓库库存 | 882 |
| 单据, 状态 | 863 |
| 日期时间, 单据 | 663 |
| 单据, 生产加工 | 599 |
| 数量, 单据 | 596 |
| 存货物料, 生产加工 | 516 |
| 人员部门 | 499 |
| 金额, 存货物料 | 424 |
| 数量, 状态 | 404 |
| 单据, 仓库库存 | 401 |
| 单据, 存货物料 | 368 |
| 金额, 客户供应商 | 366 |
| 金额, 状态 | 324 |
| 项目 | 304 |
| 金额, 仓库库存 | 301 |
| 单据, 人员部门 | 257 |
| 仓库库存, 生产加工, 状态 | 248 |
| 数量, 仓库库存 | 241 |
| 数量, 生产加工 | 238 |
| 单据, 存货物料, 生产加工 | 229 |
| 存货物料, 状态 | 227 |
| 数量, 日期时间 | 211 |
| 仓库库存, 状态 | 207 |
| 金额, 数量 | 206 |
| 金额, 单据, 存货物料, 生产加工 | 203 |
| 金额, 生产加工 | 186 |
| 日期时间, 状态 | 179 |
| 单据, 客户供应商 | 173 |
| 数量, 存货物料 | 158 |
| 日期时间, 客户供应商 | 158 |
| 单据, 生产加工, 状态 | 151 |
| 金额, 数量, 状态 | 147 |
| 金额, 存货物料, 客户供应商 | 144 |
| 金额, 单据, 生产加工 | 140 |
| 日期时间, 仓库库存 | 136 |
| 数量, 单据, 生产加工 | 136 |
| 客户供应商, 状态 | 132 |
| 金额, 日期时间 | 128 |
| 日期时间, 存货物料 | 127 |
| 生产加工, 状态 | 126 |
| 数量, 仓库库存, 状态 | 121 |
| 单据, 项目 | 111 |
| 数量, 存货物料, 生产加工 | 110 |
| 日期时间, 生产加工 | 105 |
| 数量, 仓库库存, 生产加工, 状态 | 102 |
| 存货物料, 仓库库存, 生产加工, 状态 | 95 |
| 金额, 单据, 状态 | 93 |
| 存货物料, 仓库库存, 状态 | 88 |
| 金额, 单据, 仓库库存 | 83 |
| 金额, 日期时间, 存货物料 | 79 |
| 数量, 单据, 存货物料, 生产加工 | 78 |
| 金额, 仓库库存, 状态 | 65 |
| 数量, 客户供应商 | 63 |
| 客户供应商, 人员部门 | 63 |
| 数量, 日期时间, 单据 | 63 |
| 存货物料, 生产加工, 状态 | 62 |
| 存货物料, 客户供应商 | 62 |
| 存货物料, 仓库库存 | 62 |
| 数量, 单据, 状态 | 61 |
| 人员部门, 状态 | 58 |
| 数量, 存货物料, 状态 | 57 |
| 单据, 仓库库存, 生产加工, 状态 | 57 |
| 金额, 存货物料, 状态 | 56 |
| 金额, 存货物料, 人员部门 | 52 |
| 单据, 仓库库存, 状态 | 52 |
| 金额, 人员部门 | 50 |
| 金额, 数量, 仓库库存 | 49 |
| 金额, 仓库库存, 生产加工, 状态 | 49 |
| 生产加工, 人员部门 | 48 |
| 日期时间, 存货物料, 生产加工 | 48 |
| 金额, 数量, 单据, 存货物料, 生产加工 | 48 |
| 金额, 存货物料, 生产加工 | 46 |
| 日期时间, 客户供应商, 项目 | 46 |
| 单据, 存货物料, 状态 | 45 |
| 数量, 单据, 仓库库存 | 45 |
| 金额, 数量, 日期时间 | 44 |
| 数量, 存货物料, 仓库库存, 生产加工, 状态 | 44 |
| 仓库库存, 人员部门 | 44 |
| 单据, 存货物料, 生产加工, 状态 | 43 |
| 状态, 项目 | 43 |
| 金额, 日期时间, 单据 | 42 |
| 日期时间, 单据, 生产加工 | 41 |
| 日期时间, 单据, 存货物料 | 41 |
| 金额, 数量, 单据, 状态 | 41 |
| 金额, 数量, 单据 | 41 |
| 金额, 单据, 存货物料 | 39 |
| 金额, 数量, 生产加工 | 39 |
| 数量, 日期时间, 生产加工 | 39 |
| 日期时间, 项目 | 38 |
| 数量, 人员部门 | 37 |
| 日期时间, 单据, 仓库库存 | 37 |
| 日期时间, 单据, 状态 | 36 |
| 客户供应商, 仓库库存 | 36 |
| 金额, 单据, 存货物料, 生产加工, 状态 | 35 |
| 金额, 日期时间, 状态 | 34 |
| 数量, 客户供应商, 状态 | 31 |
| 单据, 存货物料, 客户供应商 | 31 |
| 金额, 数量, 存货物料 | 31 |
| 金额, 日期时间, 客户供应商 | 29 |
| 金额, 数量, 单据, 生产加工 | 28 |
| 日期时间, 存货物料, 状态 | 26 |
| 金额, 日期时间, 存货物料, 客户供应商 | 25 |
| 存货物料, 人员部门 | 24 |
| 数量, 日期时间, 状态 | 24 |
| 单据, 存货物料, 仓库库存, 生产加工, 状态 | 24 |
| 金额, 单据, 客户供应商 | 23 |
| 日期时间, 仓库库存, 生产加工, 状态 | 23 |
| 金额, 客户供应商, 状态 | 22 |
| 金额, 项目 | 22 |
| 金额, 存货物料, 仓库库存 | 22 |
| 数量, 存货物料, 仓库库存, 状态 | 21 |
| 数量, 生产加工, 状态 | 21 |
| 金额, 数量, 仓库库存, 状态 | 21 |
| 数量, 单据, 存货物料 | 20 |
| 存货物料, 生产加工, 人员部门 | 19 |
| 金额, 数量, 客户供应商 | 19 |
| 金额, 数量, 生产加工, 状态 | 19 |
| 金额, 单据, 人员部门 | 18 |
| 数量, 项目 | 18 |
| 数量, 存货物料, 生产加工, 状态 | 18 |
| 仓库库存, 生产加工, 人员部门, 状态 | 18 |
| 日期时间, 人员部门 | 17 |
| 日期时间, 仓库库存, 状态 | 17 |
| 数量, 单据, 生产加工, 状态 | 17 |
| 金额, 日期时间, 单据, 生产加工 | 16 |
| 金额, 日期时间, 单据, 存货物料, 生产加工 | 15 |
| 存货物料, 仓库库存, 生产加工 | 14 |
| 金额, 数量, 存货物料, 状态 | 14 |
| 数量, 存货物料, 客户供应商, 状态 | 14 |
| 金额, 客户供应商, 人员部门 | 14 |
| 金额, 数量, 单据, 存货物料, 生产加工, 状态 | 14 |
| 客户供应商, 生产加工 | 13 |
| 日期时间, 生产加工, 状态 | 13 |
| 日期时间, 单据, 存货物料, 生产加工 | 13 |
| 金额, 单据, 存货物料, 客户供应商 | 13 |
| 金额, 数量, 客户供应商, 状态 | 13 |
| 单据, 客户供应商, 状态 | 13 |
| 单据, 生产加工, 人员部门 | 13 |
| 数量, 日期时间, 单据, 生产加工 | 13 |
| 金额, 单据, 项目 | 13 |
| 仓库库存, 生产加工 | 12 |
| 数量, 日期时间, 客户供应商 | 12 |
| 仓库库存, 项目 | 12 |
| 金额, 数量, 仓库库存, 生产加工, 状态 | 12 |
| 金额, 数量, 日期时间, 单据 | 11 |
| 数量, 存货物料, 仓库库存 | 11 |
| 数量, 单据, 人员部门 | 10 |
| 金额, 数量, 存货物料, 生产加工 | 10 |
| 单据, 仓库库存, 生产加工 | 10 |
| 日期时间, 单据, 生产加工, 状态 | 10 |
| 数量, 单据, 仓库库存, 生产加工, 状态 | 10 |
| 单据, 存货物料, 仓库库存, 状态 | 10 |
| 金额, 数量, 存货物料, 客户供应商 | 9 |
| 客户供应商, 项目 | 9 |
| 单据, 仓库库存, 人员部门 | 9 |
| 金额, 日期时间, 客户供应商, 项目 | 9 |
| 数量, 人员部门, 状态 | 8 |
| 金额, 生产加工, 状态 | 8 |
| 金额, 数量, 存货物料, 客户供应商, 状态 | 8 |
| 单据, 客户供应商, 人员部门 | 8 |
| 存货物料, 项目 | 8 |
| 金额, 单据, 存货物料, 生产加工, 人员部门 | 8 |
| 金额, 单据, 生产加工, 状态 | 8 |
| 金额, 存货物料, 仓库库存, 状态 | 8 |
| 金额, 存货物料, 仓库库存, 生产加工, 状态 | 8 |
| 单据, 存货物料, 仓库库存 | 7 |
| 人员部门, 项目 | 7 |
| 数量, 日期时间, 存货物料, 生产加工 | 7 |
| 金额, 存货物料, 生产加工, 状态 | 7 |
| 数量, 日期时间, 存货物料 | 7 |
| 单据, 状态, 项目 | 7 |
| 日期时间, 单据, 客户供应商, 项目 | 7 |
| 金额, 数量, 单据, 生产加工, 状态 | 7 |
| 存货物料, 人员部门, 状态 | 7 |
| 日期时间, 存货物料, 仓库库存 | 7 |
| 数量, 状态, 项目 | 6 |
| 存货物料, 客户供应商, 状态 | 6 |
| 日期时间, 单据, 客户供应商 | 6 |
| 日期时间, 客户供应商, 仓库库存 | 6 |
| 数量, 客户供应商, 仓库库存 | 6 |
| 日期时间, 单据, 人员部门 | 6 |
| 金额, 数量, 日期时间, 生产加工 | 6 |
| 金额, 状态, 项目 | 6 |
| 数量, 单据, 存货物料, 生产加工, 状态 | 6 |
| 金额, 存货物料, 客户供应商, 仓库库存 | 6 |
| 金额, 日期时间, 仓库库存 | 6 |
| 客户供应商, 仓库库存, 生产加工, 状态 | 6 |
| 单据, 客户供应商, 生产加工 | 5 |
| 存货物料, 客户供应商, 生产加工 | 5 |
| 金额, 日期时间, 生产加工 | 5 |
| 单据, 客户供应商, 仓库库存 | 5 |
| 金额, 仓库库存, 人员部门 | 5 |
| 数量, 单据, 客户供应商 | 5 |
| 金额, 日期时间, 单据, 状态 | 5 |
| 金额, 单据, 仓库库存, 状态 | 5 |
| 数量, 单据, 存货物料, 仓库库存, 生产加工 | 5 |
| 数量, 日期时间, 人员部门 | 5 |
| 单据, 存货物料, 仓库库存, 生产加工 | 5 |
| 数量, 日期时间, 仓库库存 | 5 |
| 日期时间, 存货物料, 仓库库存, 状态 | 5 |
| 数量, 日期时间, 客户供应商, 状态 | 4 |
| 单据, 存货物料, 人员部门 | 4 |
| 金额, 日期时间, 单据, 存货物料 | 4 |
| 金额, 客户供应商, 仓库库存 | 4 |
| 日期时间, 存货物料, 客户供应商 | 4 |
| 金额, 日期时间, 人员部门 | 4 |
| 金额, 单据, 客户供应商, 状态 | 4 |
| 金额, 单据, 存货物料, 状态 | 4 |
| 数量, 单据, 项目 | 4 |
| 日期时间, 客户供应商, 人员部门 | 4 |
| 单据, 人员部门, 状态 | 4 |
| 单据, 仓库库存, 项目 | 4 |
| 金额, 数量, 日期时间, 单据, 存货物料, 生产加工 | 4 |
| 金额, 日期时间, 单据, 存货物料, 生产加工, 状态 | 4 |
| 金额, 数量, 单据, 存货物料, 仓库库存, 生产加工 | 4 |
| 生产加工, 项目 | 4 |
| 存货物料, 状态, 项目 | 4 |
| 数量, 仓库库存, 人员部门 | 4 |
| 存货物料, 客户供应商, 仓库库存, 状态 | 4 |
| 金额, 存货物料, 仓库库存, 生产加工 | 4 |
| 日期时间, 单据, 仓库库存, 生产加工, 状态 | 4 |
| 数量, 日期时间, 存货物料, 客户供应商, 状态 | 3 |
| 金额, 日期时间, 存货物料, 人员部门 | 3 |
| 存货物料, 客户供应商, 人员部门 | 3 |
| 金额, 存货物料, 客户供应商, 生产加工 | 3 |
| 金额, 数量, 人员部门 | 3 |
| 金额, 日期时间, 仓库库存, 人员部门 | 3 |
| 数量, 存货物料, 仓库库存, 生产加工 | 3 |
| 数量, 单据, 存货物料, 仓库库存 | 3 |
| 日期时间, 客户供应商, 状态 | 3 |
| 日期时间, 状态, 项目 | 3 |
| 单据, 生产加工, 项目 | 3 |
| 数量, 单据, 仓库库存, 生产加工 | 3 |
| 数量, 单据, 存货物料, 仓库库存, 生产加工, 状态 | 3 |
| 存货物料, 生产加工, 项目 | 3 |
| 存货物料, 仓库库存, 人员部门, 状态 | 3 |
| 日期时间, 单据, 仓库库存, 状态 | 3 |
| 金额, 单据, 仓库库存, 生产加工 | 3 |
| 日期时间, 存货物料, 生产加工, 状态 | 2 |
| 金额, 存货物料, 客户供应商, 状态 | 2 |
| 金额, 单据, 存货物料, 人员部门 | 2 |
| 金额, 数量, 单据, 存货物料 | 2 |
| 金额, 数量, 日期时间, 存货物料 | 2 |
| 金额, 日期时间, 存货物料, 状态 | 2 |
| 生产加工, 人员部门, 状态 | 2 |
| 金额, 日期时间, 单据, 客户供应商 | 2 |
| 金额, 日期时间, 客户供应商, 状态 | 2 |
| 仓库库存, 状态, 项目 | 2 |
| 客户供应商, 人员部门, 状态 | 2 |
| 金额, 单据, 状态, 项目 | 2 |
| 数量, 日期时间, 项目 | 2 |
| 日期时间, 客户供应商, 人员部门, 项目 | 2 |
| 金额, 数量, 单据, 存货物料, 仓库库存, 生产加工, 状态 | 2 |
| 金额, 单据, 存货物料, 仓库库存, 生产加工 | 2 |
| 数量, 单据, 仓库库存, 状态 | 2 |
| 数量, 单据, 仓库库存, 人员部门 | 2 |
| 数量, 单据, 客户供应商, 仓库库存 | 2 |
| 数量, 仓库库存, 项目 | 2 |
| 金额, 人员部门, 状态 | 2 |
| 日期时间, 单据, 存货物料, 仓库库存, 状态 | 2 |
| 金额, 数量, 单据, 仓库库存 | 2 |
| 金额, 数量, 日期时间, 状态 | 2 |
| 存货物料, 客户供应商, 仓库库存 | 2 |
| 单据, 存货物料, 生产加工, 人员部门, 状态 | 2 |
| 仓库库存, 生产加工, 状态, 项目 | 2 |
| 日期时间, 存货物料, 仓库库存, 生产加工, 状态 | 2 |
| 数量, 单据, 存货物料, 客户供应商, 状态 | 1 |
| 数量, 单据, 客户供应商, 状态 | 1 |
| 金额, 存货物料, 客户供应商, 生产加工, 状态 | 1 |
| 单据, 客户供应商, 项目 | 1 |
| 数量, 单据, 存货物料, 客户供应商 | 1 |
| 数量, 存货物料, 客户供应商 | 1 |
| 数量, 客户供应商, 人员部门 | 1 |
| 金额, 数量, 项目 | 1 |
| 数量, 日期时间, 生产加工, 状态 | 1 |
| 金额, 日期时间, 存货物料, 生产加工 | 1 |
| 日期时间, 单据, 项目 | 1 |
| 金额, 数量, 状态, 项目 | 1 |
| 单据, 客户供应商, 生产加工, 状态 | 1 |
| 单据, 生产加工, 状态, 项目 | 1 |
| 数量, 单据, 存货物料, 状态 | 1 |
| 数量, 单据, 仓库库存, 项目 | 1 |
| 数量, 日期时间, 单据, 仓库库存 | 1 |
| 存货物料, 仓库库存, 状态, 项目 | 1 |
| 金额, 存货物料, 客户供应商, 仓库库存, 状态 | 1 |
| 数量, 存货物料, 状态, 项目 | 1 |
| 日期时间, 单据, 存货物料, 仓库库存 | 1 |
| 金额, 仓库库存, 生产加工 | 1 |
| 金额, 仓库库存, 项目 | 1 |
| 金额, 日期时间, 存货物料, 仓库库存 | 1 |
| 金额, 数量, 日期时间, 仓库库存 | 1 |
| 金额, 数量, 存货物料, 生产加工, 状态 | 1 |
| 日期时间, 单据, 存货物料, 生产加工, 状态 | 1 |
| 单据, 存货物料, 客户供应商, 生产加工, 状态 | 1 |
| 单据, 存货物料, 生产加工, 状态, 项目 | 1 |

## 5. 时间字段样例

| 模块 | 表 | 字段 | 类型 | 行数 | 含义推断 |
| --- | --- | --- | --- | ---: | --- |
| 库存/仓库 | `dbo.ST_SubsidiaryBook` | `accountYear` | int | 1014698 | 数量, 日期时间 |
| 库存/仓库 | `dbo.ST_SubsidiaryBook` | `accountPeriod` | int | 1014698 | 数量, 日期时间 |
| 库存/仓库 | `dbo.ST_SubsidiaryBook` | `isPeriodInit` | tinyint | 1014698 | 日期时间, 状态 |
| 库存/仓库 | `dbo.ST_SubsidiaryBook` | `AccountYearPeriod` | nvarchar | 1014698 | 数量, 日期时间 |
| 库存/仓库 | `dbo.ST_SubsidiaryBook` | `accountDate` | datetime | 1014698 | 数量, 日期时间 |
| 库存/仓库 | `dbo.ST_SubsidiaryBook` | `voucherdate` | datetime | 1014698 | 日期时间, 单据 |
| 库存/仓库 | `dbo.ST_SubsidiaryBook` | `auditeddate` | datetime | 1014698 | 日期时间 |
| 库存/仓库 | `dbo.ST_SubsidiaryBook` | `createdtime` | datetime | 1014698 | 日期时间 |
| 库存/仓库 | `dbo.ST_SubsidiaryBook` | `updated` | datetime | 1014698 | 日期时间 |
| 库存/仓库 | `dbo.ST_SubsidiaryBook` | `productionDate` | datetime | 1014698 | 日期时间, 存货物料 |
| 库存/仓库 | `dbo.ST_SubsidiaryBook` | `AccountTime` | datetime | 1014698 | 数量, 日期时间 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `updatedBy` | nvarchar | 1008417 | 日期时间, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `expiryDate` | datetime | 1008417 | 日期时间, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `receiveDate` | datetime | 1008417 | 日期时间, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `createdtime` | datetime | 1008417 | 日期时间, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `updated` | datetime | 1008417 | 日期时间, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `ProductionDate` | datetime | 1008417 | 日期时间, 存货物料, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `AccountTime` | datetime | 1008417 | 数量, 日期时间, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `ExaminerDate` | datetime | 1008417 | 日期时间, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecordSourceRelation` | `updatedBy` | nvarchar | 838334 | 日期时间, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecordSourceRelation` | `createdtime` | datetime | 838334 | 日期时间, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecordSourceRelation` | `updated` | datetime | 838334 | 日期时间, 仓库库存 |
| 生产/加工 | `dbo.MP_ManufactureOrder_Material` | `createdtime` | datetime | 741738 | 日期时间, 单据, 存货物料, 生产加工 |
| 生产/加工 | `dbo.MP_ManufactureOrder_Material` | `CloseDate` | datetime | 741738 | 日期时间, 单据, 存货物料, 生产加工 |
| 其他 | `dbo.RCHK_CostAnalysis` | `VoucherDate` | datetime | 627485 | 金额, 日期时间, 单据, 状态 |
| 其他 | `dbo.RCHK_CostAnalysis` | `createdTime` | datetime | 627485 | 金额, 日期时间, 状态 |
| 库存/仓库 | `dbo.ST_SummaryBook` | `accountYear` | int | 601367 | 数量, 日期时间 |
| 库存/仓库 | `dbo.ST_SummaryBook` | `accountPeriod` | int | 601367 | 数量, 日期时间 |
| 库存/仓库 | `dbo.ST_SummaryBook` | `AccountYearPeriod` | nvarchar | 601367 | 数量, 日期时间 |
| 库存/仓库 | `dbo.ST_LocationDetail` | `expiryDate` | datetime | 470971 | 日期时间 |
| 库存/仓库 | `dbo.ST_LocationDetail` | `productionDate` | datetime | 470971 | 日期时间, 存货物料 |
| 生产/加工 | `dbo.MP_CostAllocationDirectMaterialSumOrder_s` | `createdtime` | datetime | 440242 | 金额, 日期时间, 单据, 存货物料, 生产加工 |
| 生产/加工 | `dbo.MP_CostAllocationDirectMaterialSumOrder_s` | `sourcevoucherdate` | datetime | 440242 | 金额, 日期时间, 单据, 存货物料, 生产加工 |
| 生产/加工 | `dbo.MP_CostAllocationDirectMaterialSumOrder_b` | `createdtime` | datetime | 429387 | 金额, 日期时间, 单据, 存货物料, 生产加工 |
| 其他 | `dbo.RCHK_STFund` | `VoucherDate` | datetime | 295996 | 日期时间, 单据 |
| 其他 | `dbo.RCHK_STFund` | `createdTime` | datetime | 295996 | 日期时间 |
| 库存/仓库 | `dbo.ST_RDRecord` | `printTime` | int | 126124 | 日期时间, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord` | `accountingperiod` | int | 126124 | 数量, 日期时间, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord` | `accountingyear` | int | 126124 | 数量, 日期时间, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord` | `updatedBy` | nvarchar | 126124 | 日期时间, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord` | `VoucherYear` | int | 126124 | 日期时间, 单据, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord` | `VoucherPeriod` | int | 126124 | 日期时间, 单据, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord` | `SourceVoucherDate` | datetime | 126124 | 日期时间, 单据, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord` | `maturityDate` | datetime | 126124 | 日期时间, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord` | `voucherdate` | datetime | 126124 | 日期时间, 单据, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord` | `madedate` | datetime | 126124 | 日期时间, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord` | `auditeddate` | datetime | 126124 | 日期时间, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord` | `createdtime` | datetime | 126124 | 日期时间, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord` | `updated` | datetime | 126124 | 日期时间, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord` | `AccountTime` | datetime | 126124 | 数量, 日期时间, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord` | `ConsignorDate` | datetime | 126124 | 日期时间, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord` | `ExaminerDate` | datetime | 126124 | 日期时间, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord` | `DeliveryVoucherDate` | datetime | 126124 | 日期时间, 单据, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord` | `DeliveryTime` | datetime | 126124 | 日期时间, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord` | `DispatchTime` | datetime | 126124 | 日期时间, 仓库库存, 状态 |
| 库存/仓库 | `dbo.ST_RDRecord` | `EntruckingTime` | datetime | 126124 | 日期时间, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord` | `AuditedTime` | datetime | 126124 | 日期时间, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord` | `BackToWarehouseTime` | datetime | 126124 | 日期时间, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord` | `SendDate` | datetime | 126124 | 日期时间, 仓库库存 |
| 采购 | `dbo.PU_PurchaseArrival_SourceRelation` | `updatedBy` | nvarchar | 124426 | 日期时间 |
| 采购 | `dbo.PU_PurchaseArrival_SourceRelation` | `updated` | datetime | 124426 | 日期时间 |
| 库存/仓库 | `dbo.ST_NewCurrentStock_FlowRecordBak` | `expiryDate` | datetime | 103631 | 日期时间, 仓库库存 |
| 库存/仓库 | `dbo.ST_NewCurrentStock_FlowRecordBak` | `createdtime` | datetime | 103631 | 日期时间, 仓库库存 |
| 库存/仓库 | `dbo.ST_NewCurrentStock_FlowRecordBak` | `updated` | datetime | 103631 | 日期时间, 仓库库存 |
| 库存/仓库 | `dbo.ST_NewCurrentStock_FlowRecordBak` | `productionDate` | datetime | 103631 | 日期时间, 存货物料, 仓库库存 |
| 财务/会计 | `dbo.ARAP_Detail` | `year` | int | 103096 | 日期时间 |
| 财务/会计 | `dbo.ARAP_Detail` | `period` | int | 103096 | 日期时间 |
| 财务/会计 | `dbo.ARAP_Detail` | `vouchertimestamp` | nvarchar | 103096 | 日期时间, 单据 |
| 财务/会计 | `dbo.ARAP_Detail` | `voucherDate` | datetime | 103096 | 日期时间, 单据 |
| 财务/会计 | `dbo.ARAP_Detail` | `registerDate` | datetime | 103096 | 日期时间, 状态 |
| 财务/会计 | `dbo.ARAP_Detail` | `arrivalDate` | datetime | 103096 | 日期时间 |
| 财务/会计 | `dbo.ARAP_Detail` | `createdTime` | datetime | 103096 | 日期时间 |
| 生产/加工 | `dbo.MP_ManufactureOrder_b` | `preStartDate` | datetime | 98835 | 日期时间, 单据, 生产加工 |
| 生产/加工 | `dbo.MP_ManufactureOrder_b` | `preFinishDate` | datetime | 98835 | 日期时间, 单据, 生产加工, 状态 |
| 生产/加工 | `dbo.MP_ManufactureOrder_b` | `startDate` | datetime | 98835 | 日期时间, 单据, 生产加工 |
| 生产/加工 | `dbo.MP_ManufactureOrder_b` | `finishDate` | datetime | 98835 | 日期时间, 单据, 生产加工, 状态 |
| 生产/加工 | `dbo.MP_ManufactureOrder_b` | `createdtime` | datetime | 98835 | 日期时间, 单据, 生产加工 |
| 生产/加工 | `dbo.MP_ManufactureOrder_b` | `ClosedDate` | datetime | 98835 | 日期时间, 单据, 生产加工 |
| 生产/加工 | `dbo.MP_ManufactureOrder_b` | `WaitUpdateBom` | int | 98835 | 日期时间, 单据, 生产加工 |
| 生产/加工 | `dbo.MP_ManufactureOrder_b` | `UpdateBomTime` | datetime | 98835 | 日期时间, 单据, 生产加工 |

## 6. 金额字段样例

| 模块 | 表 | 字段 | 类型 | 精度 | 行数 | 含义推断 |
| --- | --- | --- | --- | --- | ---: | --- |
| 库存/仓库 | `dbo.ST_SubsidiaryBook` | `inPrice` | decimal | 28,14 | 1014698 | 金额 |
| 库存/仓库 | `dbo.ST_SubsidiaryBook` | `inAmount` | decimal | 28,14 | 1014698 | 金额 |
| 库存/仓库 | `dbo.ST_SubsidiaryBook` | `outPrice` | decimal | 28,14 | 1014698 | 金额 |
| 库存/仓库 | `dbo.ST_SubsidiaryBook` | `outAmount` | decimal | 28,14 | 1014698 | 金额 |
| 库存/仓库 | `dbo.ST_SubsidiaryBook` | `isneedrecost` | tinyint | 3,0 | 1014698 | 金额, 状态 |
| 库存/仓库 | `dbo.ST_SubsidiaryBook` | `idCostPricingDimension` | int | 10,0 | 1014698 | 金额 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `price` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `price2` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `basePrice` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `estimatedPrice2` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `baseEstimatedPrice` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `estimatedPrice` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `amount` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `estimatedAmount` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `cumulativeSettlementAmount` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `taxRate` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `taxPrice` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `tax` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `taxAmount` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `feeAdjust` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `totalAmount` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `feeAmount` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `materialAmount` | decimal | 28,14 | 1008417 | 金额, 存货物料, 仓库库存, 生产加工 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `isManualCost` | tinyint | 3,0 | 1008417 | 金额, 仓库库存, 状态 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `isCostAccounted` | tinyint | 3,0 | 1008417 | 金额, 数量, 仓库库存, 状态 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `taxFlag` | tinyint | 3,0 | 1008417 | 金额, 仓库库存, 状态 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `cumulativeEstimateAmount` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `CustomerInventoryPrice` | nvarchar | 0,0 | 1008417 | 金额, 存货物料, 客户供应商, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `VendorInventoryPrice` | nvarchar | 0,0 | 1008417 | 金额, 存货物料, 客户供应商, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `origPrice` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `origAmount` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `origTaxPrice` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `origTax` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `origTaxAmount` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `origSalePrice` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `origTaxSalePrice` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `origSaleAmount` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `origTaxSaleAmount` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `salePrice` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `taxSalePrice` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `saleAmount` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `taxSaleAmount` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `OrigManuPrice` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `OrigManuAmount` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `OrigTaxManuPrice` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `OrigTaxManuAmount` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `ManuPrice` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `ManuAmount` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `TaxManuPrice` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `TaxManuAmount` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `ManuFeeDiff` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `OrigManuPrice2` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `OrigTaxManuPrice2` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `ManuPrice2` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `TaxManuPrice2` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `baseManuPrice` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `origPrice2` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `origTaxPrice2` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `TaxPrice2` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `origSalePrice2` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `origTaxSalePrice2` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `salePrice2` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `taxSalePrice2` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `SentBaseAmount` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `Retailprice` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `RetailAmount` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `RetailNoTaxPrice` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `RetailNoTaxAmount` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `PriceStrategyTypeName` | nvarchar | 0,0 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `PriceStrategySchemeIds` | nvarchar | 0,0 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `PriceStrategySchemeNames` | nvarchar | 0,0 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `PriceStrategyTypeId` | int | 10,0 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `IsModifiedPrice` | tinyint | 3,0 | 1008417 | 金额, 仓库库存, 状态 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `EstimateManuPrice` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `CurrentEstimateManuAmount` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `CurrentSettleManuAmount` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `RDDivideFee` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `MaterialFee` | decimal | 28,14 | 1008417 | 金额, 存货物料, 仓库库存, 生产加工 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `MonthAdjustMenuAmount` | decimal | 28,14 | 1008417 | 金额, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `CostAccountStatus` | int | 10,0 | 1008417 | 金额, 数量, 仓库库存, 状态 |

## 7. 数量字段样例

| 模块 | 表 | 字段 | 类型 | 精度 | 行数 | 含义推断 |
| --- | --- | --- | --- | --- | ---: | --- |
| 库存/仓库 | `dbo.ST_SubsidiaryBook` | `accountYear` | int | 10,0 | 1014698 | 数量, 日期时间 |
| 库存/仓库 | `dbo.ST_SubsidiaryBook` | `accountPeriod` | int | 10,0 | 1014698 | 数量, 日期时间 |
| 库存/仓库 | `dbo.ST_SubsidiaryBook` | `inQuantity` | decimal | 28,14 | 1014698 | 数量 |
| 库存/仓库 | `dbo.ST_SubsidiaryBook` | `outQuantity` | decimal | 28,14 | 1014698 | 数量 |
| 库存/仓库 | `dbo.ST_SubsidiaryBook` | `inSubQuantity` | decimal | 28,14 | 1014698 | 数量 |
| 库存/仓库 | `dbo.ST_SubsidiaryBook` | `isTrueAccount` | tinyint | 3,0 | 1014698 | 数量, 状态 |
| 库存/仓库 | `dbo.ST_SubsidiaryBook` | `outSubQuantity` | decimal | 28,14 | 1014698 | 数量 |
| 库存/仓库 | `dbo.ST_SubsidiaryBook` | `AccountYearPeriod` | nvarchar | 0,0 | 1014698 | 数量, 日期时间 |
| 库存/仓库 | `dbo.ST_SubsidiaryBook` | `accountDate` | datetime | 23,3 | 1014698 | 数量, 日期时间 |
| 库存/仓库 | `dbo.ST_SubsidiaryBook` | `AccountTime` | datetime | 23,3 | 1014698 | 数量, 日期时间 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `arrivalQuantity` | decimal | 28,14 | 1008417 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `arrivalQuantity2` | decimal | 28,14 | 1008417 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `quantity` | decimal | 28,14 | 1008417 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `quantity2` | decimal | 28,14 | 1008417 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `compositionQuantity` | nvarchar | 0,0 | 1008417 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `baseQuantity` | decimal | 28,14 | 1008417 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `subQuantity` | decimal | 28,14 | 1008417 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `cumulativeSettlementQuantity` | decimal | 28,14 | 1008417 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `cumulativeSettlementQuantity2` | decimal | 28,14 | 1008417 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `cumulativeSettlementBaseQuantity` | decimal | 28,14 | 1008417 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `cumulativeSettlementSubQuantity` | decimal | 28,14 | 1008417 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `cumulativePurchaseArrivalQuantity` | decimal | 28,14 | 1008417 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `cumulativePurchaseArrivalQuantity2` | decimal | 28,14 | 1008417 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `cumulativeSaleDispatchQuantity` | decimal | 28,14 | 1008417 | 数量, 仓库库存, 状态 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `cumulativeSaleDispatchQuantity2` | decimal | 28,14 | 1008417 | 数量, 仓库库存, 状态 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `defectiveQuantity` | decimal | 28,14 | 1008417 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `defectiveQuantity2` | decimal | 28,14 | 1008417 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `kitQuantity` | decimal | 28,14 | 1008417 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `kitQuantity2` | decimal | 28,14 | 1008417 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `distributedQuantity` | decimal | 28,14 | 1008417 | 数量, 仓库库存, 状态 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `distributedQuantity2` | decimal | 28,14 | 1008417 | 数量, 仓库库存, 状态 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `isCostAccounted` | tinyint | 3,0 | 1008417 | 金额, 数量, 仓库库存, 状态 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `ShrinkageQuantity` | decimal | 28,14 | 1008417 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `ShrinkageQuantity2` | decimal | 28,14 | 1008417 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `ShrinkageBaseQuantity` | decimal | 28,14 | 1008417 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `ShrinkageSubQuantity` | decimal | 28,14 | 1008417 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `OrigShrinkageQuantity` | decimal | 28,14 | 1008417 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `OrigShrinkageQuantity2` | decimal | 28,14 | 1008417 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `CumPurchaseShrinkageQuantity` | decimal | 28,14 | 1008417 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `CumPurchaseShrinkageQuantity2` | decimal | 28,14 | 1008417 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `CumReturnQuantity` | decimal | 28,14 | 1008417 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `CumReturnQuantity2` | decimal | 28,14 | 1008417 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `NotSettleQuantity` | decimal | 28,14 | 1008417 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `NotSettleQuantity2` | decimal | 28,14 | 1008417 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `SentBaseQuantity` | decimal | 28,14 | 1008417 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `differencequantity` | decimal | 28,14 | 1008417 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `differencequantity2` | decimal | 28,14 | 1008417 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `BoxNumber` | nvarchar | 0,0 | 1008417 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `DiscountRate` | decimal | 28,14 | 1008417 | 数量, 仓库库存, 状态 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `Discount` | decimal | 28,14 | 1008417 | 数量, 仓库库存, 状态 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `OrigDiscount` | decimal | 28,14 | 1008417 | 数量, 仓库库存, 状态 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `CurrentEstimateManuQuantity` | decimal | 28,14 | 1008417 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `CurrentSettleManuQuantity` | decimal | 28,14 | 1008417 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `CostAccountStatus` | int | 10,0 | 1008417 | 金额, 数量, 仓库库存, 状态 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `CumulativeExpenseQuantity` | decimal | 28,14 | 1008417 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `CumulativeExpenseQuantity2` | decimal | 28,14 | 1008417 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `CumulativeExpenseBaseQuantity` | decimal | 28,14 | 1008417 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `CumulativeExpenseSubQuantity` | decimal | 28,14 | 1008417 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `OrigDiscountPrice` | decimal | 28,14 | 1008417 | 金额, 数量, 仓库库存, 状态 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `AccountTime` | datetime | 23,3 | 1008417 | 数量, 日期时间, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `isAdjustQuantityFeed` | tinyint | 3,0 | 1008417 | 金额, 数量, 仓库库存, 状态 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `UnAccountedCarriedforwardFlag` | bit | 1,0 | 1008417 | 数量, 仓库库存, 状态 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `CardTicketDiscountAmount` | decimal | 28,14 | 1008417 | 金额, 数量, 仓库库存, 状态 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `SNCount` | int | 10,0 | 1008417 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `SerialNumbers` | nvarchar | 0,0 | 1008417 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `BoxBarCodeCount` | int | 10,0 | 1008417 | 数量, 单据, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `CumMarshalStockInQuantity` | decimal | 28,14 | 1008417 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `CumMarshalStockInQuantity2` | decimal | 28,14 | 1008417 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `CumInvoiceCrossCheckQuantity` | decimal | 28,14 | 1008417 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `CumInvoiceCrossCheckBaseQuantity` | decimal | 28,14 | 1008417 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `PackingCount` | int | 10,0 | 1008417 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `IsGetInStockQuantityFromRationQuantity` | int | 10,0 | 1008417 | 数量, 仓库库存, 状态 |
| 库存/仓库 | `dbo.ST_RDRecord_b` | `CoproductRationQuantity` | decimal | 28,14 | 1008417 | 数量, 存货物料, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecordSourceRelation` | `quantity` | decimal | 28,14 | 838334 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecordSourceRelation` | `quantity2` | decimal | 28,14 | 838334 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecordSourceRelation` | `baseQuantity` | decimal | 28,14 | 838334 | 数量, 仓库库存 |
| 库存/仓库 | `dbo.ST_RDRecordSourceRelation` | `subQuantity` | decimal | 28,14 | 838334 | 数量, 仓库库存 |
| 生产/加工 | `dbo.MP_ManufactureOrder_Material` | `parentScaleQuantity` | decimal | 28,14 | 741738 | 数量, 单据, 存货物料, 生产加工 |
| 生产/加工 | `dbo.MP_ManufactureOrder_Material` | `sonScaleQuantity` | decimal | 28,14 | 741738 | 数量, 单据, 存货物料, 生产加工 |
| 生产/加工 | `dbo.MP_ManufactureOrder_Material` | `sonScaleQuantity2` | decimal | 28,14 | 741738 | 数量, 单据, 存货物料, 生产加工 |

## 8. 岗位可做分析方向

### 财务/会计

- 应收应付账龄、回款/付款进度、客户/供应商往来余额分析。
- 单据金额、税额、折扣、费用、成本字段联动分析。
- 存货成本、出入库金额、生产材料成本、成本差异分析。
- 凭证、结算、开票、核销、对账相关分析，前提是确认 AR/AP/GL 表口径。
- 月度期间、会计年度、单据日期、审核日期维度下的趋势分析。

### 仓库/库存

- 出入库流水、库存台账、仓库库存结构、批次库存、呆滞料分析。
- 材料出库与生产加工单关联追溯。
- 安全库存、上下限库存、负库存、异常出入库分析。

### 生产/加工

- 加工单成品产量、材料领用、计划用料与实际出库差异。
- BOM 用量、替代料、追加料、倒冲/领料模式分析。
- 加工单状态、开工/完工日期、延期与未完工分析。

### 销售/采购

- 销售订单、发货、退货、客户维度收入与交付分析。
- 采购订单、到货、入库、供应商交付与价格分析。

### 管理层

- 经营看板：收入、成本、毛利、库存、应收、应付、生产进度。
- 数据可信度看板：关键字段缺失、异常日期、单据断链、基础档案缺失。

## 9. 后续项目建议

1. 先确定 3 个业务主题：生产用料、库存出入库、财务往来。
2. 每个主题建立一张可解释宽表和一套可追溯明细。
3. 用真实字段目录替代数据字典假设，数据字典仅辅助解释。
4. 让客户提供现有 Excel 报表样例，用来反推口径。
5. 对金额、数量、日期、状态字段建立统一指标口径表。
