---
date: 2026-10-29
tags: [tgbot, quota, cursor-agent, old-mac, false-positive]
severity: high
domain: ops
---

# TG 报「模型额度用尽」≠ 网页 Pro+ 用量耗尽

## 背景

2026-10-28 夜～10-29：old-mac 机器人连续回「AI 模型额度可能已用尽」全链降级；网页 Cursor Pro+ 仍显示 Cursor Models 约 25%、Other/Grok 0%。私聊「token还有很多」仍同句。

## 根因

1. **误判**：`is_quota_error` 曾匹配中文「额度|用尽」，成功回复里提到额度也会被当成失败并 `mark_exhausted`，丢掉正文继续降级。
2. **空失败冒充额度**：整链空输出 / 鉴权失败时，`ensure_nonempty` 统一写成「额度可能已用尽」，和网页用量无关。
3. **旧机运行时**：tgbot 目录 gitignore，补丁需经 memory `patches/` + heal 脚本落到 old-mac。

## 正确做法

1. 额度判定只认 API/CLI 英文报错（`resource_exhausted` / `429` / `quota exceeded` 等）；中文叙述不算。
2. 鉴权失败立刻停链并明示；空输出写「无有效输出」，勿冒充额度。
3. 恢复：`bash ~/.dc-platform/memory/scripts/heal_tgbot_false_quota.sh`（清 state、装补丁、冒烟、重启 bot）。
4. 冒烟失败 → 查旧机 `CURSOR_API_KEY` 是否与网页登录账号一致、是否过期。

## 验证

```bash
python3 -c "import sys; sys.path.insert(0,'omdb/tgbot'); import model_quota as m; assert not m.is_quota_error('刚才额度用尽'); assert m.is_auth_error('Authentication required')"
bash ~/.dc-platform/memory/scripts/heal_tgbot_false_quota.sh
# TG 私聊「在吗」应有正常 Agent 回复
```

## 关联

- `omdb/tgbot/model_quota.py` / `claude_client.py`
- `~/.dc-platform/memory/patches/tgbot-model-quota-heal/`
- `~/.dc-platform/memory/scripts/heal_tgbot_false_quota.sh`
