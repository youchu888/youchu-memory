---
name: dwd ETL 字段截断 / SET 容错 已统一落地（2026-05-01）
description: 35 个 dwd 任务 SQL 全部加了 SET enable_insert_strict + max_filter_ratio + LEFT 截断；脚本在 .claude/database/scripts/，可重跑维护。
type: project
originSessionId: ce0993a6-f017-4276-92db-80fdc4888c85
---
2026-05-01 完成 dwd ETL 字段保护统一改造，**所有 35 个 dwd 任务 SQL 已在终态**：

1. **顶部 SET 容错头**（每个文件都有）：
   ```sql
   -- INSERT 容错配置（保护字段超长不阻塞整个任务）
   SET enable_insert_strict = false;
   SET max_filter_ratio = 1.0;
   ```

2. **VARCHAR 字段全截断**：所有有长度规则的字段都包了 `LEFT(expr, N)`，`N = data_length / 3` 向下取整（StarRocks VARCHAR 是字节，UTF-8 中文 1 字 = 3 字节）。

3. **常量字段不包**（NULL / `CAST(NULL AS xxx)` / 数字 / 字符串字面量）—— 保留原样如 `NULL AS user_agent`。

4. **OVERSIZE / UNPROTECTED = 0 / 0**（重跑核查脚本验证）。

**长度查找优先级**（脚本逻辑）：
1. dwd 表自己的 `columndefinition.data_length`（DDL 真值，最优先）
2. event 维度 glossary maxLength（`User_Behavior_Events.<event>.<field>`）
3. Common_Fields glossary maxLength（user_agent / device_brand / city / ...）

**Why**：上游 dw 任何长值不再触发 StarRocks 写入失败 / 截断；同时 SET 头保证单条记录失败不阻塞整个任务。

**How to apply**：
- 新增 dwd 任务文件后，跑 [fix_dwd_field_truncation.py](../../../Program/datacenter/dc-parent/.claude/database/scripts/fix_dwd_field_truncation.py) 自动补 SET + LEFT。脚本**幂等**——已加的不会重复加。
- 核查现状用 [check_dwd_field_truncation.py](../../../Program/datacenter/dc-parent/.claude/database/scripts/check_dwd_field_truncation.py)，OVERSIZE / UNPROTECTED 应该都是 0。
- 修改 dwd 表 DDL 改了字段长度后，跑 fix 脚本自动调整对应 LEFT 的 N。
- **海豚 SQL 写法**：`${var}` 必须裸用，不在引号 / 注释里（参 feedback_dolphinscheduler_var_placeholder_pitfall）。

**修这次同时的副产物**：
- ops_system 下所有非弃用 SQL 已按 `_ddl.sql` + 任务文件 拆分（122 个 _ddl + 任务文件 + 29 个原已独立 / 弃用 / migrate）
- omdb 套件已建（[omdb/](../../../Program/datacenter/dc-parent/omdb/)），含 pull_db.py + pull_om.py 两条命令 + slash command
- dim_user_all_daily.sql 的 `'${dt} 23:59:59'` / 注释里的 `${dt}` 已改成裸用 + CONCAT
