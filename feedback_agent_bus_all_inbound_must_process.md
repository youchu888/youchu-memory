# Feedback：收到的 bus 都要处理 · 另起执行（主人 2026-09-30）

## 规矩

凡入站需 reply 的 bus（含 `to=all` 广播）：

1. **尽快 ACK**（目标 60s）
2. **做完或实质回执后 reply 结案**
3. **禁止**只镜像到 TG / 只写 wake_feed 就停着

## 执行面（与 TG 私聊对齐）

- TG 私聊：Cursor Agent API 另起执行（`composer-2.5`）
- agent-bus：**同样另起** — `AGENT_BUS_CURSOR_AUTO_EXECUTE=true`（headless cursor-executor 吃 `wake_feed`）
- 勿再默认只靠 IDE Composer 主会话接 wake（忙别的活就会晾着）

配置：`~/Library/Application Support/youchu-agent-bus/config/agent-bus.env`  
部署脚本：`.cursor/scripts/sync-agent-bus-deploy.sh`（勿写回 false）

## 例外（仍按三分法）

- `mode=silent` / 正文显式「不用回、待命、learn_only」→ 可不展开
- 其余默认要结案

## 关联

- bus#9470 晾置 → 主人令改另起执行
- `.cursor/rules/agent-bus-session.mdc`
