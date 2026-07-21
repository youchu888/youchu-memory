---
name: dc-platform shared db skill context
description: CHcode workspace linked to dc-platform public memory and .claude/database conventions.
type: project
---
This project should be handled in association with **dc-platform** public memory at `~/.dc-platform/memory/` and the local database workspace at `.claude/database/` (aliases, metadata, knowledge, reports, playbooks).

**Why:** All dev sessions belong to project `dc-platform`. Public memory and lessons live in one folder for cross-workspace reuse.

**How to apply:** For work in CHcode, default to:
- Public memory: `~/.dc-platform/memory/MEMORY.md` + `lessons/_index.md`
- Project index: `~/.dc-platform/projects/INDEX.md` + `.cursor/projects/registry.yaml`
- Database: `.claude/database/` as first source for table status, aliases, playbooks, and reports.