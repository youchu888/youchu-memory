---
date: 2026-06-05
tags: [attribution, dolphin, test, complement, dim]
severity: medium
domain: ops
---

# 注册归因 test 发布补数：配置大写 + 零行核验

## 背景
`dws_register_attribution_result_d` 改版（15 app 白名单、阈值 40、device 分回落 20）推 dev 后，需在测试海豚同步 SQL、迁移 dim 配置、补最近一周并核验。

## 坑 / 错误做法
- 用 `mysql < dim_app_attribution_config_migrate.sql` 整文件执行：StarRocks 对文件头 `--` 注释/多语句易报 1064。
- 测试 `dim_app_attribution_config` 若仍是小写 `jha-204` 等，与 DWD 大写 `JHA-204` 无法 JOIN，白名单形同虚设。
- 补数实例 SUCCESS、分区 `p20260522` 等已创建，但结果表 0 行：易误判为 ETL 失败；实为 `WHERE source_event_id IS NOT NULL` 过滤后无候选。

## 正确做法
1. **海豚**：测试项目 `20524869250304`，任务 `dws_register_attribution_result_d`（`wf_dws_汇总_日` / code `21869820140416` / task `174729603403591`）。REST 发布：OFFLINE → PUT 替换 SQL → ONLINE；task localParam `pt=$[yyyyMMdd-1]`。
2. **dim 迁移**：先 `UPDATE ... SET is_run=0`，再 `INSERT` 15 个大写 app（与生产 DWD 一致）；勿依赖带注释的整文件重定向。
3. **补数**：`COMPLEMENT_DATA` + `TASK_ONLY` + `startNodeList=task_code`，`2026-05-22`～`2026-05-28`；若首尾少一天可再补 `05-27`～`05-28`。
4. **核验**：查注册 organic iOS 与白名单 click/view 的 **同 app 同 IP** 交集；无交集则结果 0 行属预期。

## 验证
```sql
-- 配置 15 条大写 is_run=1
SELECT app_id FROM dim.dim_app_attribution_config WHERE is_run=1 ORDER BY 1;

-- 候选（应有 regs，with_click/view 可为 0）
SELECT r.dt, COUNT(DISTINCT r.event_id) regs, ...
FROM dwd.dwd_user_register_d_v2 r
INNER JOIN dim.dim_app_attribution_config t ON r.app_id=t.app_id AND t.is_run=1
WHERE r.dt BETWEEN '2026-05-22' AND '2026-05-28' ...;

SELECT dt, COUNT(*) FROM dws.dws_register_attribution_result_d
WHERE dt BETWEEN '2026-05-22' AND '2026-05-28' GROUP BY dt;
```

## 生产发布（2026-06-05 补充）
- 生产海豚：**wf_dws_汇总_日** wf_code `20691538136576`（UI legacy `dws_日`），task `21043636973952`（v7→v8，md5 `32a260ac...`）。
- 生产 `dim` 已是 15 个大写 app，**无需再 migrate**。
- 补数注意：`globalParams.dt=$[yyyy-MM-dd-1]`，要刷 **业务日 D** 的分区，补数调度时间应填 **D+1 00:00:00**（例：刷 `2026-05-28` → 调度 `2026-05-29`）。
- 生产 7 日核验：`score_threshold` 全为 40；`2026-05-22` 行数 5390 / success 3003（旧版约 1772 / 585）。

## 关联
- `ops_system/04.dws/dws.dws_register_attribution_result_d/dws_register_attribution_result_d.sql`
- `ops_system/04.dws/dws.dws_register_attribution_result_d/dim_app_attribution_config_migrate.sql`
- commit `33b568e` on `origin/dev`
