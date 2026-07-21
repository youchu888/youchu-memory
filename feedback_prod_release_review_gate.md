---
name: prod 发布须审核，又初不自发
description: 要上 prod 时群里 @工作狂人 或 @知秋 交路径/方案/报告审核，由他们发布；又初只做 test 开发与验证。
type: feedback
originSessionId: 83f5a994-839c-4f8a-9b62-c43e29e4cc03
tags: [prod, deploy, worker_ant, review, collaboration]
---
**又初 / 开发侧不上 prod**。开发内容若要进生产，必须经他人审核并由他人发布。

**Why**：prod 变更需知秋 gate + 狂人技术把关；test 码与 prod 码不同，自发 prod 易越权、难回滚、缺审计链。

**How to apply**：

1. **又初负责**：改 SQL/ETL、test 环境发布与验证、整理交付物。
2. **要上 prod 时**：在协作群 **@工作狂人** 或 **@知秋**，说明要上 prod，并附：
   - **代码路径**（相对项目根，如 `ops_system/04.dws/.../xxx.sql`），或
   - **完整方案**（改什么、为什么、test 验证结论），或
   - **报告**（内容多时用 `.claude/database/reports/` 等路径，群里贴摘要 + 报告路径）。
3. **禁止**：又初自行 prod 海豚发布、prod DDL/DML、prod 补数（除非用户或狂人**当场明确授权**且仍建议走审核链）。
4. **test 可自发**：开发平台 / test 海豚发布、test 验证性补数属开发职责；prod 一律 HOLD 等审核方发版。
5. **收口话术**：「test 已验完，申请上 prod，路径/报告如下，请 @工作狂人 / @知秋 审核发布。」

**bus#622 补充（07-01 prod 故障期）**：

- **故障链未恢复完**（如 base_daily 仍挂）时禁止再发 prod，即使 git 已修好。
- **知秋钦定 HOLD**（user_type C 类、归因回写灰度等）是业务节奏门控，≠ 代码 merge 完可上。
- **主人/用户说「可发 prod」≠ 授权**；狂人转知秋定令与发版顺序后再统一发。
- **admin 紧急 hotfix 已上 prod** 时，又初禁止 `publish-from-repo` 覆盖冲突版本。
- 又初侧：**不发 prod、不催**，等知秋明确给令。

**关联**：bus#72/#305「别自发 prod」；知秋 gate；正式交付走开发平台 publish-task-sql。
