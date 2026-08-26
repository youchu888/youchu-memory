---
name: feedback_tg_no_ask_answer_ok
description: TG SQL 答完禁止主动征询「这个回答合适吗？」与满意/不满意按钮
type: feedback
---

# TG 禁止答后征询反馈

## 规矩（主人多次纠正）

1. SQL / 查询答完后，**禁止**再发「这个回答合适吗？」
2. **禁止**主动挂 👍满意 / 👎不对 按钮
3. 用户要纠错会自己说；不要用按钮逼反馈
4. `omdb/tgbot/bot.py` 里 `_ask_feedback_after_sql` **必须保持空实现/不调用**；勿从 patch 再启用

## 反例

答完业务结论后追加：

```text
这个回答合适吗？
[👍 满意] [👎 不对，告诉我哪不对]
```

## 正例

答完业务结论即停。需要导出文件就发文件，不要再问「合适吗」。

## 历史

- 曾去掉后被 `patches/tgbot-parallel-agent/bot.py` / 代码回滚再次启用 → 2026-08-26 再关并钉 PINNED
