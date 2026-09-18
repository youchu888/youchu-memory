# 星型模型设计 Playbook（DC · star schema v3.3）

> **用途**：新建 / 改造 DWS·ADS 分析模型时，stage 2 `design.md` 必读本 playbook。  
> **权威案例**：`omdb/projects/content-rank/design/content_rank_star_schema_design_v2_20260721.html`（知秋 2026-07-21 定案）  
> **变更记录**：2026-07-25 又初初版，私聊#227 学习沉淀

---

## 1. 一句话定义

**星型模型 = 中心事实表 + 少量共享维度 JOIN + 退化维 inline + 查询层算衍生指标。**

作废「行星链路」：`dim 扫一遍 → dwm 再扫 → ads 再扫` 的双扫/三扫架构。

---

## 2. 何时用星型、何时不用

| 场景 | 推荐范式 | 例 |
|------|---------|-----|
| 按日/周/月切片的多维指标汇总 | ✅ 星型宽事实 | `dws_app_user_d_h`、`dws_app_order_d_h`、`ads_content_rank_*` |
| 地域地图预聚合 | ✅ 星型（region 维 + bitmap 度量） | `ads_user_region_geo_d` |
| 视频账户多维指标 | ✅ 星型（5 链路事实 + dim spine） | `dws_video_account_d_d` |
| 用户/设备当前态标签宽表 | ❌ 非星型（PK 全量 UPSERT） | `dws_user_tag_d_d`、`dws_device_tag_d_d` |
| uid×dt 明细事实（供下游再聚合） | ❌ 非星型（明细事实表） | `dws_user_page_stay_d` |
| LTV / 留存 cohort 行级派生 | ❌ 非星型（dim cohort + dwd 行级） | `dws_user_reg_ltv_d_h` |

**铁律**：先问「这是汇总报表还是当前态/明细？」— 只有前者走星型 checklist。

---

## 3. 分层与星型角色

```
DWD   原子事实（事件明细，按 dt/hour 分区）
  ↓ 单次 scan + GROUP BY（每个 biz_dt 每源至多 1 次）
DWM   汇总事实（可选；content×日 cnt + bitmap + 退化维）
  ↓
DWS/ADS  宽事实表（面向 BI / 看板 / API）
  ↑ LEFT JOIN（克制）
DIM   共享维度（用户 / 日历 / 地区映射）
```

| 星型角色 | 本项目典型表 | 说明 |
|---------|-------------|------|
| 原子事实 | `dwd_order_paid_d`、`dwd_video_event_h` | 只读，不承载报表 |
| 汇总事实 | `dwm_content_metric_d_d` | 中间层可选；有 bitmap UV 时常用 |
| 宽事实表 | `dws_app_user_d_h`、`ads_content_rank_d_d` | AGGREGATE/PK + 维度键 + 度量 |
| 用户维 | `dim_user_all`、`dim_user_daily_snapshot` | 身份/渠道/注册地/VIP |
| 日历维 | `dim_date_info_all` | week_no、自然周月界 |
| 地区映射 | `dim_geo_region_xwalk` + `dim_region_info_all` | 事件脏地名 → 标准 region |
| 退化维 | 事实行上的 `title`、`content_type` | **不建** `dim_content_*` |

---

## 4. 设计六原则（v3.3 · 必写进 design.md）

### P1 · 事实优先

指标 + 展示属性优先从**当天（或周期内）DWD** 一次聚合带出。  
不为 title/category/content_type 单独建维表任务。

退化维默认写法：

```sql
MIN_BY(title, event_time)           -- 事件首条
-- 或当天 play 众数定 content_type（见 content_rank §5.2）
```

### P2 · 单次扫描

每个 `biz_dt`，每种内容/业务源对各 DWD **至多扫一次分区**。  
禁止「先 dim 任务扫 30 天 → 再榜单扫 DWD」。

### P3 · 维度 JOIN 克制

**只 JOIN 真正需要的共享维**：

| 需求 | 取数 |
|------|------|
| 用户类型 / 注册渠道 / 注册地 | `dim.dim_user_all`（channel 用纠正后字段，禁 register 原始 channel） |
| 当日 VIP 身份 | `dim.dim_user_daily_snapshot` |
| 周/月界 | `dim.dim_date_info_all` |
| 事件 IP 地 → 标准 region | `dim_geo_region_xwalk` → `dim_region_info_all` |

**维度时点必须在 COMMENT 写清**（快照值 vs 事件时值 vs 用户属性）。

### P4 · 度量分型

| 类型 | 聚合 | 周/月上卷 |
|------|------|----------|
| cnt / amt 标量 | SUM | SUM(日) ✅ |
| UV / 用户数 | `BITMAP_UNION(to_bitmap(bitmap_hash64_udf(uid)))` | `bitmap_union` ✅；**禁 SUM(日 UV)** |
| 比例 / 平均 | **不落表**，下游 BI 算 | — |

uid 单字段铁律：见知识库 id=2，禁止 CONCAT 复合 key 冒充 UV。

### P5 · 衍生指标策略 A — 不落表

`rank / prev_rank / rank_change / 占比` 等**查询层双 CTE 现算**，不写进 ads 宽表。  
模板见 content_rank HTML §5。

### P6 · 列卫生

- 禁止恒 NULL / 口径撤销后的占位列（例：`like_uv` 已 DROP）
- 禁止「将来可能用到」的空壳列
- 比例分子分母可落表，比例本身通常不落

---

## 5. design.md 必含章节（星型模型 checklist）

stage 2 写 design 时，除平台通用段外**必须**有：

```markdown
## 星型模型设计

### 5.1 事实表粒度
- 主事实表：`db.table`
- 粒度：`dt × ... × user_type`（写清 PK / AGGREGATE KEY）
- 是否宽事实 / 是否需 dwm 中间层

### 5.2 维度键与来源
| 维度键 | 来源 | 时点类型 | JOIN 键 |
|--------|------|----------|---------|
| channel | dim_user_all.channel | 用户属性 | app_id+uid |
| region | ... | 注册地/事件地/快照地 | ... |

### 5.3 退化维（若有）
| 字段 | 聚合 | 为何不建 dim |

### 5.4 DWD 扫描计划
| 源表 | biz_dt 扫描次数 | 备注 |
|------|----------------|------|

### 5.5 度量清单
| 度量 | 类型 cnt/amt/bitmap | 来源 CTE | 周/月上卷规则 |

### 5.6 不落表衍生指标
| 指标 | 策略（A=查询层） | 理由 |

### 5.7 反模式自检
- [ ] 无双扫 dim+dwd
- [ ] 无雪花多层 dim
- [ ] UV 无 SUM 日上卷
- [ ] 无 rank 落表
- [ ] 无废列
```

---

## 6. 现网标杆对照

| 模型 | 宽事实 | 主要 dim JOIN | 退化维 | 备注 |
|------|--------|--------------|--------|------|
| `dws_app_user_d_h` | ✅ | user_all → channel/region/user_type | device 事件归一 | AGGREGATE + bitmap |
| `dws_app_order_d_h` | ✅ | user_all → region(注册地) | — | 订单 region=方案 A |
| `dws_video_account_d_d` | ✅ | user_all(user_type) + region 解码 | — | 5 链路 UNION spine |
| `ads_content_rank_*` | ✅ | daily_snapshot(VIP) + date(周月) | title/type inline | 星型 v3.3 定案 |
| `ads_user_region_geo_d` | ✅ | xwalk + region_info | — | 活跃=事件 IP 地；注册/充值各表口径独立 |

---

## 7. 反模式（真实踩坑）

| 反模式 | 后果 | 本项目案例 |
|--------|------|-----------|
| 为展示字段建内容维表 | DWD 双扫、30 天窗口炸库 | `dim_content_all` 废除 |
| 行星链路 dim→dwm→ads | IO ×2~3 | content_rank 架构重构 |
| rank 落 ads 宽表 | 列膨胀、切片不灵活 | ads v3 去掉 rank 16 列 |
| SUM(日 UV) 得周 UV | 重复计数 | content_rank 周月用 bitmap_union |
| 订单 region 用事件地 vs 注册地混用 | 地区标准化碎裂 | 订单统一方案 A（user_all.region） |
| DUPLICATE 模型做 ETL 目标 | 重跑追加脏数据 | 宽事实优先 AGGREGATE/PK + OVERWRITE |

---

## 8. 与平台规范衔接

- **表名**：`<layer>_<biz>_<grain>_<freq>`（知识库 id=4）
- **幂等**：`INSERT OVERWRITE` 分区；`_d_h` hourly 同 dt 分区也必须 OVERWRITE
- **DDL 模型选择**：宽事实 UV 多用 AGGREGATE；需行级 UPSERT 才 PK（见 video_account design）
- **新任务**：走 dev session stage 1→7；design 引用本 playbook

---

## 9. 开工检索顺序

1. 读本 playbook §2 确认是否适用星型
2. 读同类现网 `design.md` + prod `dolphin.get_task_sql`
3. 读 content_rank HTML（退化维 / 单次 scan / rank 策略 A 模板）
4. 查知识库：渠道(id=5)、region(id=9)、bitmap(id=2)、命名(id=4)
5. 写 design §星型模型设计 + §幂等性设计

---

## 变更记录

| 日期 | 变更 |
|------|------|
| 2026-07-25 | 又初：私聊#227 学习沉淀初版 |
