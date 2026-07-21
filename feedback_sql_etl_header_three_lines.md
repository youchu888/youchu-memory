# Feedback：ETL SQL 文件头 + task.yaml（强制）

**适用**：`ops_system/**` 下所有海豚调度 SQL；新建或修改 ETL 时 AI 必须自检。

## 文件头（前 30 行）

必须含三行（缺一 DC lint warning，且缺 task.yaml 时 params error 阻断发布）：

1. `-- task: <name>`
2. `-- doc: <口径一句话>`
3. `-- params: <逗号分隔参数名>` 或 `-- params: 无`

推荐续行：`-- 频率:` `-- 幂等:` `-- 上游:`，后接 `====` 分隔符再写业务细则。

## task.yaml

与 `.sql` 同目录；`task.name` 与 `-- task:` 一致；`params[].name` 覆盖 SQL 主体全部 `${name}`。

## 注释禁占位符

注释中**不得**出现 `${...}`、`$[...]`、`?`、`@var`、`:name` — 用「业务日 dt」「分区 pt」等文字描述。

## 自检清单（写完 SQL 必做）

- [ ] 三行头声明
- [ ] task.yaml params 对齐
- [ ] 注释无占位符字面量
- [ ] lint 无 error
