# 新 Mac 出站 bus 不同步 TG 私聊

## 现象
Cursor 已 `agent_bus_send`（progress/reply 写入本机 `youchu_ai_tg_status.jsonl`），TG 私聊仍只有「处理中」，看不到「又初→狂人」结案正文。

## 根因
- 新 Mac（`WORKLOG_HOST_ID=new-mac`）按约定**不跑** tgbot / status_mirror（`disable-local-automation-new-mac.sh`）。
- 出站只 append 本机 `tg_status.jsonl`；旧机 bot 读的是**旧机** state，读不到新机出站。
- 入站「处理中」仍可能由旧机 poller 镜像，造成「有处理中、无结案」错觉。

## 修复
- `agent_bus_send._mirror_outbound_tg`：在写 jsonl 后，若 `new-mac` 或本机无 tgbot，则对 `ack/progress/reply` **直推** `TASK_DISPATCH_NOTIFY_USER_IDS` 私聊。
- 开关：`AGENT_BUS_TG_DIRECT_OUTBOUND=1|0` 强制开/关。
- 部署：改 `.claude/database/scripts/notify/agent_bus_send.py` 后 `cp` 到 Application Support（或 sync）；**新机勿长期开 poller**。

## 自检
```bash
# 发一条 progress，TG 应出现「又初→狂人（阶段同步）」
python3 .claude/database/scripts/notify/agent_bus_send.py \
  --to worker_ant --kind progress --reply-to-bus-id N --text "[进度] smoke"
```
