---
name: feedback_pinned_overflow_append_only
description: PINNED 1–30 冻结；新红线只追加 pinned/，禁止顶旧条
type: feedback
---

# PINNED 首页冻结 · 续篇只追加

**以后怎么做**：

- `PINNED.md` **1–30 不动**（不替换、不删、不为腾位改写）
- 新红线：`~/.dc-platform/memory/pinned/*.md`，序号从 31 接着编；一行结论 + 链 feedback/lesson
- 查规则：`lookup-rules.sh 关键词`（首页+续篇一起扫）
- 改/删已有红线正文 → 先说明段落，等用户明确说「改」

**不要**：满 30 就把旧红线顶掉；不要把红线全文塞进 bootstrap。

出处：2026-11-04；lesson `2026-10-19-红线原文可以多份-按关键词一起查.md`。
