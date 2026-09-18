# 归因 HTML 报告目录

本目录存放注册归因审计、成功率分析等 **自适应 HTML** 报告。

## 命名规范

- `attribution_audit_{业务日}.html` — 清单去重 + 配置核对 + 成功率诊断
- `attribution_config_patch_{业务日}.sql` — 需补配白名单时的 SQL（已执行则可删）

## 生成

```bash
python3 .claude/database/scripts/attribution_audit_report.py
```

默认业务日 **T-1**（Asia/Shanghai 昨日）。
