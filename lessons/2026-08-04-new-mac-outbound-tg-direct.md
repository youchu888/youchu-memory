# 新 Mac 出站不同步 TG：别改链路，回旧机处理

## 现象
在新 Mac Cursor 上回了 bus（progress/reply），TG 私聊看不到结案；只有「处理中」。

## 根因（分工，不是缺功能）
- **旧 Mac** = TG bot + poller + 接单主会话 + status_mirror（权威）
- **新 Mac** = 编码机；`disable-local-automation-new-mac.sh` 故意不跑 bot/poller
- 出站写本机 `tg_status`，旧机 bot 读不到 → 镜像断档

## 正确做法
1. bot/agent-bus 派单 → **只在旧机 Cursor 处理**
2. 新机不要为「看得到 TG」去加直推 / 启 poller（易双开抢活、改坏原链路）
3. 误在新机开干了 → 后续回旧机续做；新机侧别再改 `agent_bus_send`

## 反例（已撤回）
2026-08-04 曾在新机给 `agent_bus_send` 加 TG 直推，**已按主人令还原**；勿再合入。
