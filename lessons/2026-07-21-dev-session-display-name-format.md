---
date: 2026-07-21
tags: [dev-session, naming, feedback, tg, project]
severity: high
domain: ops
---

# Dev Session 对外名用汉字格式，禁发 code / 项目 id

## 背景

主人 07-21 纠正：发群/告知他人时不要用 `dev-20260711-002` 这类 session code，要发开发平台列表里的汉字显示名；后续**新建 session 的 title 也统一该格式**。另勿再犯「项目 id」类错误（把内部编号或海豚项目数字码当给人看的名字 / 或写进 `task.yaml.project`）。

## 坑 / 错误做法

- 对人说 / 发群只写 `dev-20260711-001`、`dev-20260711-002`
- 新建 session 标题写成纯英文表名或裸 code
- 把海豚 `project_code`（如 `20524869250304`）或海豚项目名「运营系统」当成开发平台 `project` / 对外 session 名

## 正确做法

### 1. 对外显示名（发群、报进度、跟人说）

统一格式（与平台「需求 DEV SESSIONS」列表一致）：

```text
【中文业务标签】表名 · 又初
```

示例：

- `【页面停留】dwd_app_page_stay_d · 又初`
- `【会话sid宽表】dwm_app_session_sid_d · 又初`
- `【设备标签】dws_device_tag_d_d · 又初`

`dev-YYYYMMDD-NNN` **仅内部**（API、目录、`session_code`、bus 排查）；对人默认**不发**，除非对方明确要 code。

### 2. 新建 session

创建时 `title` / 显示名按上式写好，全队格式统一；不要事后再靠口头解释 code。

### 3. 项目归属（旧坑一并钉死）

- `task.yaml` → `project: dc-platform`
- 海豚侧写 `dolphin_project` / `wf_code`，**不要**把海豚数字 `project_code` 当开发平台项目 id 填错位

## 验证

- 发群文案可被非开发直接认出来是哪张表/哪条线
- 平台列表与口头/群消息名称一致
- `task.yaml` 的 `project` 不是数字码、不是「运营系统」

## 关联

- 规则：`.cursor/rules/dev-session-display-name.mdc`
- feedback：`~/.dc-platform/memory/feedback_dev_session_display_name.md`
- 项目化：`lessons/2026-06-17-dc-platform-projectization.md`
- 当日例：机器人群 message_id `7548` → `【页面停留】dwd_app_page_stay_d · 又初`
