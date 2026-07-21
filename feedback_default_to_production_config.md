---
name: 数据核查/查询默认走生产配置
description: 在本项目跑数据库查询时默认用 .claude/database/my.cnf（生产），除非用户显式说测试库。
type: feedback
originSessionId: ce0993a6-f017-4276-92db-80fdc4888c85
---
在 dc-parent 项目跑数据查询/核查时，**默认使用生产配置** `.claude/database/my.cnf`，不要默认用 `test.cnf`。

**Why**：本项目 dim/dws/dwd 表测试库经常空或滞后；生产是所有数据核查、对账、新表 / 新视图验证的真正源头。用户多次表态"测试没数据，去生产跑"。

**How to apply**：
1. 任何 SQL 核查、对账、抽样、新表验证 —— 默认 `mysql --defaults-extra-file=/Users/arthur/Program/datacenter/dc-parent/.claude/database/my.cnf -e "..."`
2. 仅当用户明确说"测试库 / test.cnf / 测试环境"时，才换 `test.cnf`
3. 用户运行的 ETL / DDL / 验证 SQL，不要假设它在测试，默认假设在生产
4. 涉及写操作（INSERT/UPDATE/DELETE）必须先跟用户确认，跑生产的写操作必须明确 OK 才执行
