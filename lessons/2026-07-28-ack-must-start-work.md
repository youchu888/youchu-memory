---
date: 2026-07-28
tags: [collab, ack, execution, criticism, device_tag]
severity: high
domain: process
source: 主人批评「回懂了却不干活」
---

# 回「懂了」必须立刻开干，禁止只口头确认

## 背景

知秋群令（15:54/16:00）：设备标签不用等狂人审阶段2，按 library#46 + 姿态F 写完代码 push 配置库，由狂人 spark-submit。又初 bot 回了「懂了」，但本会话未写代码，直到主人 16:20 追问才开工。

## 坑 / 错误做法

- 群里/私聊 **ACK「懂了」** 就当交付
- 等下一轮用户催办才动手
- 把「等审 / 等排期」当成可以停手的理由（主人/知秋已明确取消该等待）

## 正确做法

1. **可执行指令一旦确认**（尤其知秋/主人「开发完再交」）→ **同会话立刻开干**
2. ACK 与动手同一回合：先短回「已开干」，再写代码/建 session/push
3. 若真有阻塞（缺设计、缺权限）→ **立刻点名问**，不要假「懂了」后静默

## 验证

- 回 ACK 后 10 分钟内应有：文件改动 / git commit / 群「开工」进度之一
- 批评后同会话补 lesson + 改行为

## 关联

- `feedback_self_evolve_on_criticism.md`
- 设备标签阶段3：`ops_system/04.dws/dws_device_tag_d/spark/README_POSE_F.md`
