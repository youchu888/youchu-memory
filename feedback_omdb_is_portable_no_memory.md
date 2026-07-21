---
name: omdb 是可拷贝独立项目，不积累 memory
description: omdb 子目录视作独立可分发项目；不要在 dc-parent 或 omdb 项目路径下保存任何 omdb 相关的 memory；约束写在 omdb/CLAUDE.md 里。
type: feedback
originSessionId: 2e4700c2-f182-4cd0-820c-79599cc0e8c5
---
`omdb/` 是要拷贝给别人直接用的独立项目，规则与上下文必须**全部留在 omdb 目录内**（`omdb/CLAUDE.md` + `omdb/.claude/commands/`），不依赖外部 memory。

具体禁止：
- 不要在 dc-parent 的 memory 里写 omdb 工作流相关的反馈/规则（不管是 /pull_db、/tg_*、/lineage 还是其他 omdb 命令的行为偏好）。
- 不要在 omdb 自己的项目路径下积累 auto-memory 条目。
- 不要把 dc-parent 的 memory（StarRocks 方言、ETL 截断、MySQL 迁移、playbooks、报告习惯等）当成 omdb 工作的隐含约束 —— omdb 命令文档怎么写就怎么跑。

**Why:** 用户 2026-05-05 明确："这个项目可以拷贝给别人直接用"。任何外置 memory 都会让 omdb 不再 self-contained。

**How to apply:** 在 omdb 目录或任何 omdb 命令上工作时，需要保留的偏好直接改 omdb/CLAUDE.md 或对应命令 .md；不要 Write 到 memory 目录。
