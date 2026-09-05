---
date: 2026-09-05
tags: [workbook, progress, instant-ack, daily-fallback]
severity: high
domain: ops
---

# 工作簿 09:01 兜底仍像秒回：写死 1/2 条 + 正文印「禁止秒回模板」

## 背景

主人 2026-09-05 看群进展：点名 09:00（项 8–12），又初 09:01:10 回「又初 · 工作簿」且头上写着「禁止秒回模板」，感觉还是秒回。

## 坑 / 错误做法

1. `maybe_daily_fallback` 窗口从 **09:01** 就开始；Bot API 收不到真簿时，用 `fallback_workbook_template` **写死**「1.页面统计 2.渠道归因」冒充当日清单。
2. `workbook_progress_posted.json` 当日 `message_id=0`（不是回复某条群消息）。
3. `workbook_last_full.json` 存的是自造模板，不是群里原文。
4. 正文印「禁止秒回模板」——口号本身就是模板脸。
5. 探针其实跑了（今早 `page_stay` 3.86 亿行，约 9 秒），但清单不对 + 口号，观感仍是秒回罐头。

## 正确做法

1. 兜底窗口改为 **09:08–11:59**，给 09:00 真簿进站留时间。
2. stub **不要**带编号【又初】项；未进站则走 task 板 + `workbook_supplemental.json`，并写明「当日工作簿原文未进站」。
3. 识别旧 1/2 条自造全文，禁止写回 `last_full`。
4. 用户可见头改为 `探针时间 … · 实查 Ns`，**禁止**印「禁止秒回模板」。
5. 真簿进站后仍先 T-1 实查再发一条，不双条 follow-up。

## 验证

```bash
# 09:01 不在窗口；stub 解析不出编号项；正文无「禁止秒回模板」
python3 -c "from group_workbook_progress_handler import in_daily_fallback_window"
```

旧机改完须 `bash omdb/tgbot/restart.sh`。

## 为什么会反复（同一根因）

不是补丁没打上。09-03 当晚 `apply_tgbot_workbook_no_instant_ack.sh` 跑过、bot 也重启了，所以群里才出现「禁止秒回模板」——**那就是 09-03 补丁的产物**。

反复的原因是三件事叠在一起：

1. **每次改的是上一轮的技术理解，不是主人说的观感。** 07-24 禁「行，我来」；08 月禁硬编码句子、禁双条精简+详细；09-03 合成一条并加探针。主人说的「秒回 / 天天一样」是：**09:00 点名后立刻用同一套清单回一条**。这条主路径（`maybe_daily_fallback` + 写死 1/2 条）一直当「收不到真簿的安全网」留着。
2. **验收是假绿灯。** apply 脚本只查函数签名，不查用户可见正文、不查 09:01 会不会发自造清单。脚本成功 ≠ 群里不像秒回。
3. **09:01 兜底会抢坑。** 真簿即使随后进站，当天 `already_posted` 已占住，不再按原文重报。task 板还停在 09-01，于是每天都是页面+归因。

## 关联

- lesson：`2026-09-03-workbook-progress-list-plus-owned-no-instant-ack.md`
- feedback：`feedback_workbook_progress_list_plus_owned_cutoff.md`
- 补丁：`patches/tgbot-workbook-no-instant-ack/`
