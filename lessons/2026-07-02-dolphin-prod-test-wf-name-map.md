---
date: 2026-07-02
tags: [dolphin, prod, test, attribution, wf-map, prod-sync]
severity: high
domain: ops
---

# 工作流权威名 wf_dws_汇总_日 · prod UI legacy 叫 dws_日

## 背景

bus#827：sync/publish 时 wf 名混淆。仓库与 test 权威名是 **`wf_dws_汇总_日`**；prod 海豚 UI 仍显示旧短名 **`dws_日`**（同一 wf_code 20691538136576）。

## 坑 / 错误做法

- 把 `dws_日` 写进 task.yaml / ETL 当正式工作流名
- 用 test wf_code 21869820140416 打 prod
- 假设 prod-sync 按语义匹配（平台只按同名，prod 未 rename 时对不上）

## 正确做法

1. **文档/代码 canonical 名**：`wf_dws_汇总_日`
2. **prod API 操作**：wf_code `20691538136576` + task_code；UI 上可能仍显示 `dws_日` → 见 `wf_name_dolphin_ui`
3. 对照表：`.claude/dolphin/wf_cross_env_map.yaml`
4. 归因 prod task：result `21043636973952` · apply `22179045765504`
5. 只换 SQL：`publish-task-sql(env=prod)` + prod task_code，不改 DAG

## 验证

```bash
cat CHcode/.claude/dolphin/wf_cross_env_map.yaml
grep workflow CHcode/ops_system/04.dws/dws.dws_register_attribution_result_d/task.yaml
# 应见 workflow: wf_dws_汇总_日，prod 段含 wf_name_dolphin_ui: dws_日
```

## 关联

- `.claude/dolphin/wf_cross_env_map.yaml`
- `ops_system/04.dws/dws.dws_register_attribution_result_d/task.yaml`
