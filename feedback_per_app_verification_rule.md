---
name: 用户标识是 (uid, app_id) — 跨 app 同 uid 是不同用户
description: 这条是**项目级根本规则**，覆盖设计 + ETL + 表结构 + bitmap hash + 指标核对 + 数据质量。不限于"核对场景"。
type: feedback
originSessionId: ce0993a6-f017-4276-92db-80fdc4888c85
---
**项目所有数据工作（设计 / ETL / 表结构 / bitmap / 指标核对 / 数据质量校验 / 一致性分析）一律以 `(uid, app_id)` 作为用户标识。**

每个 app 是**独立命名空间**：
- 跨 app 的 `uid` / `order_id` / `device_id` **不是同一对象**
- 不做跨 app 去重
- 不做跨 app 冲突判断
- bitmap 设计层面：hash 必须包含 app_id（如 `bitmap_hash64_udf(CONCAT(uid, '@', app_id))`），**不能只 hash uid**
- dim 表 JOIN 必须按 `(uid, app_id)` 复合键，不能只按 uid
- 跨 app 总用户数 = 各 app 独立 distinct count 之和，不是 union 后去重

**Why:**
- 项目定义：app_id 是业务主体，每个 app 是独立用户池 + 独立订单号空间 + 独立设备池
- 多次出现过错误结论：
  1. 把"全局 BITMAP_UNION_COUNT"和"按 app 求和"相差几个误判为 hash 碰撞，其实是跨 app 重复付费用户
  2. 把同一 order_id 出现在不同 app 的事件上（各自独立的订单）误判为"订单号冲突"——其实各 app 自己管理 order_id 唯一性，跨 app 相同不算问题
  3. 设计 `dws_app_user_d_h` bitmap 时只 hash uid，跨 app 同 uid 在 new+old 双计 → 守恒漏 0.8%
- 全局去重或跨 app 比对的数字在业务上没有意义，反而会误导

**How to apply:**

**设计层（表 / bitmap / ETL）**：
- bitmap hash **必须**用 `bitmap_hash64_udf(CONCAT(uid, '@', app_id))` 之类含 app_id 的组合 hash；只 hash uid 是错的
- dim 表 JOIN：必须 `ON event.uid = dim.uid AND event.app_id = dim.app_id`，**两个键都要**
- 用户首次注册时间、用户类型 (user_type) 这些维度都是 `(uid, app_id)` 维度，不是 uid 维度

**核对 / 校验层**：
- 核对 ADS/DWS/DWD 指标与源头一致性时：**始终按 `app_id` 分组对比**，逐 app 核查差异
- 数据质量校验（订单号重复、uid 一致性、设备归一、字段值合规等）：也**按 app 独立判断**；跨 app 的同名标识不算冲突
- 不要做 `SELECT COUNT(DISTINCT uid)` / `COUNT(DISTINCT order_id)` 不带 app_id 的全局汇总当基准
- 只核对**合法 app_id**：格式为 `字母-数字`（如 DX-010、JHG-063、SF-78、YC-129、TJ-002），用正则 `^[A-Za-z]+-[0-9]+$` 过滤
- 非法格式 app_id（测试串、安全攻击 payload、无效数据、空串、`-`）直接排除，不纳入核对
- bitmap hash 碰撞的评估也要按 app 维度看单 app 规模，而不是全局规模

**查询消费层**：
- "全平台 DAU" = SUM(各 app DAU)，不是 BITMAP_UNION 跨 app 后去重

**报告呈现：**
- 数据质量报告**必须以 app_id 为主分类维度**，列出**全部有问题的 app**，不要截断 TOP N
- 按 app_id **名字字母序**排列（相同字母前缀的 app 是同一组织负责），**不要**按问题数量排序
- 按字母前缀分组（DX / JHA / JHG / TJ / YC 等），每组一张独立子表 + 小计，便于按组织分发修复
