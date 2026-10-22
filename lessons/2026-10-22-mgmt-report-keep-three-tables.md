# 管理报表只留部门周月与产品周

## 场景
管理报表下线渠道周/月，只保留部门周、部门月、产品周；主键改为部门=时间×channel×dept_id、产品=时间×dept_id×app_id。

## 做法
1. test：新 DDL 重建三表 → 发海豚 SQL → TASK_PRE 补数验 dept_id（含 54）→ 停用渠道周月 task（flag=NO）→ 软删渠道 session。
2. Spark：同步 spark_migrate SQL/DDL，`runner/sql/deploy` 送 test+prod verify 沙箱；产发仍走审核。
3. 给后端删表脚本 `drop_obsolete_promotion_tables.sql`；对接说明只写三表。
4. prod 不自发：request-publish；DROP/重建由有权限账号执行。

## 坑
- 发布海豚 SQL 必须用仓库文件字节级内容，勿手拼。
- 提交时勿误带无关 `BitmapUdf.scala` 回退（Kryo overflow）。
- 周/月补数 `task_dep_type=TASK_PRE`。
