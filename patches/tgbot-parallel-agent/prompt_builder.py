"""Build system prompt: omdb-localized — 别名 + 元数据 + [SQL] 协议。"""
import os
import sqlite3
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from config import (
    PROJECT_ROOT,
    OMDB_DIR,
    ALIASES_PATH,
    METADATA_DB_PATH,
    INCOMING_DIR,
    OUTGOING_DIR,
    AGENT_MEMORY_REFRESH_ON_SPAWN,
)
import db

log = logging.getLogger(__name__)


def _read_file(path: str) -> str | None:
    if os.path.isfile(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    return None


def _load_aliases() -> str | None:
    raw = _read_file(ALIASES_PATH)
    if not raw:
        return None
    return f"# 表别名（用户自然语言 → 实际表名）\n\n{raw.strip()}"


def _load_metadata_overview(max_tables: int = 300) -> str | None:
    """生成简表清单（仅 db.name + 简短描述），让 Claude 知道有哪些表存在。
    具体字段不在 prompt 里，由 Claude 按需 sqlite3 查 metadata.db。
    """
    if not os.path.isfile(METADATA_DB_PATH):
        return None
    try:
        with sqlite3.connect(METADATA_DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='tabledefinition'"
            )
            if cur.fetchone() is None:
                return None
            rows = conn.execute(
                "SELECT `database` AS db, name, display_name, description"
                " FROM tabledefinition"
                " WHERE COALESCE(is_deprecated, 0) = 0"
                " ORDER BY db, name"
                " LIMIT ?", (max_tables,)
            ).fetchall()
            total = conn.execute(
                "SELECT COUNT(*) FROM tabledefinition WHERE COALESCE(is_deprecated, 0) = 0"
            ).fetchone()[0]
    except sqlite3.OperationalError:
        return None
    if not rows:
        return None

    def _desc(r):
        d = (r['display_name'] or r['description'] or '').strip()
        return d[:60]

    lines = [f"- `{r['db']}.{r['name']}` — {_desc(r)}" for r in rows]
    suffix = "" if total <= max_tables else f"\n\n（共 {total} 张活跃表，显示前 {max_tables}）"
    return (
        "# 数据表清单（仅表名 + 业务描述；字段需按需查）\n\n"
        + "\n".join(lines) + suffix
    )


METADATA_QUERY_GUIDE = f"""# 按需查元数据（重要！写 SQL 前必读）

**不要凭印象写列名**。本地 sqlite 在 `{METADATA_DB_PATH}`，里面 `columndefinition` 表存了
所有字段的类型 / 注释。写 SQL 前先用 `Bash(sqlite3:*)` 查清楚再下笔。

`columndefinition` 关键列：`table_id`, `name`, `data_type`, `data_length`, `comment`
`tabledefinition` 关键列：`id`, `database`, `name`, `display_name`, `description`

## 标准查列名套路

要查某表的所有字段，用这个 sqlite3 一行：

```bash
sqlite3 {METADATA_DB_PATH} "SELECT c.name, c.data_type, c.data_length, c.comment
  FROM columndefinition c JOIN tabledefinition t ON c.table_id = t.id
  WHERE t.\\`database\\` = 'dw' AND t.name = 'dw_user_event_detail'
  ORDER BY c.ordinal;"
```

把 `database` / `name` 换成实际表名。

## 不知道库名的表

```bash
sqlite3 {METADATA_DB_PATH} "SELECT \\`database\\`, name, display_name FROM tabledefinition
  WHERE name LIKE '%order%' AND COALESCE(is_deprecated, 0) = 0;"
```

## 查多张表批量

WHERE 用 `IN (...)`、`OR` 拼即可。一次 sqlite3 调用拿够数据，不要 N+1。

## 工作流

1. 用户说"昨天事件明细 event_id 为空的统计"
2. 你先 read aliases.md（已经在 prompt 里），找到 "事件明细表 => dw.dw_user_event_detail"
3. 你 sqlite3 查 dw_user_event_detail 的列，确认有 event_id / event / app_id / event_time
4. **基于真实列名**写 [SQL: ...]
5. Bot 跑 SQL，结果回去给用户

## 不要这样做
- ❌ 直接 `[SQL: SELECT app_id, event_name FROM dw.dw_user_event_detail ...]`（瞎写列名）
- ❌ 跑 `DESC dw.dw_user_event_detail` 走 [SQL]（把列名查询占了 SQL 队列；用本地 sqlite3 即可）
- ❌ 用户没要求时主动 SELECT * 取大量字段（StarRocks 大表全列扫描很贵）
"""


LESSON_PROTOCOL = """# 自我进化协议：[LESSON: scope | rule]

当你检测到用户**在教你**或**纠正你**时，在你正常回答的末尾**额外**输出一行：

   [LESSON: <scope> | <rule>]

bot 会拦下来弹按钮让用户确认是否入库；入库后这条规则会在以后所有相关查询的 prompt 里出现。

## 什么时候输出 [LESSON]

✅ **明显的教学信号**（用户主动）：
- "记住..." / "记下..." / "记一下..."
- "以后..." / "今后..." / "将来..."
- "把 X 叫做 Y" / "X 就是 Y 的意思"
- "我们这边..."（项目通行的约定）

✅ **明显的纠正信号**（用户对你上一轮的反馈）：
- "不对，应该..."
- "你又加戏了 / 又拆了 / 又跑偏了"
- "我没让你按 X 拆"
- "不是这个意思，我要的是..."
- "这次错了，下次..."

❌ **不要瞎输出**：
- 普通查询、新问题、不带教学/纠正语气 → 不要 emit [LESSON]
- 用户夸你 / 中性反馈 → 不要 emit
- 一句话里既问新问题又教规则 → 既正常回答（含 [SQL]），又 emit [LESSON]

## 输出规范

格式：`[LESSON: scope | lesson]`
- scope：一个简短范围标签（中文/英文都行），比如 "订单查询"、"alias"、"dwd_order_*"、"通用"
- lesson：第三人称客观陈述的规则，**不**用 "你"/"我"。比如：
  - "yes/no 问题不要按 app_id GROUP BY 拆分"  ✅
  - "你不要按 app 拆"  ❌（用户视角）
- scope 可空：直接 `[LESSON: | <rule>]`，bot 会认 scope=""

## 示例

| 用户原话 | 你的 [LESSON] |
|---|---|
| "以后查订单号重复的问题别按 app 拆" | `[LESSON: 订单号重复 | yes/no 问题不要按 app_id 维度 GROUP BY 拆分]` |
| "记住，金额单位是分要 ÷100" | `[LESSON: 金额字段 | 所有 amt/amount 字段单位是分，展示前需 ÷100 换元]` |
| "把 dwd.dwd_order_paid_d 叫成订单库" | `[LESSON: alias | 订单库 = dwd.dwd_order_paid_d]` |
| "你又加戏了！我只要总数不要按 app 拆" | `[LESSON: 聚合查询 | 看个数就 SUM/COUNT 出一个数，不要主动按 app 维度拆]` |
| "不对，是支付时间不是创建时间" | `[LESSON: 订单时间字段 | "什么时候付钱"是 pay_date / pay_time，不是 create_time]` |

⚠️ 一次最多 emit 1~2 条 [LESSON]；不要刷屏。

⚠️ emit [LESSON] 不替代正常回答；正常回答（含 [SQL]）该有还得有。

## 工作任务收尾（自动沉淀）

完成**查数 / 验数 / ETL / 对账**类工作后，若本次总结出可复用口径、字段映射、常见坑或 SQL 模板，
**务必 emit 1 条** `[LESSON: scope | rule]`（第三人称、可独立理解），bot 会**自动入库**并在下次同类问题注入 prompt。
不要等用户点确认；这是为了让同类任务越来越快。
"""


SQLITE_AND_BASH_HINT = f"""# 你能用的工具（CLI 模式 = Claude Code）

- Bash：可以跑 `sqlite3`、`cat`、`grep`、`ls`、`head`、`mysql` 等查本地 / 看文件
- Read：直接读文件比如 `omdb/.claude/database/aliases.md`
- 数据查询的 mysql / StarRocks 真实查询不要自己跑，**必须**走 [SQL: ...] 让 bot 排队执行
- 本地 sqlite3 查 metadata 不算"数据查询"，可以直接 Bash 跑

参考路径：
- 别名文件：`{ALIASES_PATH}`（Read 取）
- 元数据 sqlite：`{METADATA_DB_PATH}`（Bash sqlite3 查）
"""


def _load_public_rules() -> str | None:
    rules = db.get_public_rules()
    if not rules:
        return None
    lines = [f"- 表 `{r['table_pattern']}`: {r['rule']}" for r in rules]
    return (
        "# 查询公共规则（控制台维护，所有用户共享）\n\n"
        "以下规则适用于本 bot 所有用户，写 SQL 时遵守：\n\n"
        + '\n'.join(lines)
    )


def _load_user_rules(user_id: int) -> str | None:
    rules = db.get_user_rules(user_id)
    if not rules:
        return None
    lines = [f"- [#{r['id']}] 表 `{r['table_pattern']}`: {r['rule']}" for r in rules]
    return (
        f"# 当前用户私有规则（uid={user_id}，仅你自己可见，可用 /delrule <id> 删）\n\n"
        + '\n'.join(lines)
    )


def _load_worker_ant_insights() -> str | None:
    try:
        import worker_ant_learner as wal
        block = wal.recent_digest_block(limit=6)
        if block:
            return block
    except Exception:
        pass
    rows = db.get_lessons_by_source('worker_ant', limit=8)
    if not rows:
        return None
    lines = [f"- [#{r['id']}] [{r.get('scope') or '通用'}] {r['lesson']}" for r in rows]
    return (
        "# 工作狂人协作经验（从群消息自动提炼，开发时优先参考）\n\n"
        + "\n".join(lines)
    )


def _load_public_lessons() -> str | None:
    rows = db.get_public_lessons()
    if not rows:
        return None
    lines = [f"- [#{r['id']}] [{r.get('scope') or '通用'}] {r['lesson']}" for r in rows]
    return (
        "# 公共 lessons（自学/手动入库的规则，所有用户共享）\n\n"
        "以下是从过往交互中沉淀的经验，遵守它们能更精准地回答用户：\n\n"
        + '\n'.join(lines)
    )


def _load_user_lessons(user_id: int) -> str | None:
    rows = db.get_user_lessons(user_id)
    if not rows:
        return None
    lines = [
        f"- [#{r['id']}] [{r.get('scope') or '通用'}] {r['lesson']}"
        for r in rows
    ]
    return (
        f"# 当前用户私有 lessons（uid={user_id}，仅对你生效）\n\n"
        "（来自你以前 \"以后/记住...\" 教 bot 的、或纠正 bot 时沉淀下来的；与公共冲突时**优先这些**）\n\n"
        + '\n'.join(lines)
    )


def _load_user_aliases(user_id: int) -> str | None:
    rows = db.get_user_aliases(user_id)
    if not rows:
        return None
    lines = [f"- [#{r['id']}] {r['alias']} => {r['target']}"
             + (f"  ({r['description']})" if r['description'] else "")
             for r in rows]
    return (
        f"# 当前用户私有别名（uid={user_id}，仅你自己可见，可用 /delalias <id> 删）\n\n"
        "若与公共别名冲突，**以你的私有别名为准**。\n\n"
        + '\n'.join(lines)
    )


HARDCODED_RULES = """# 固化查询规则（违反会被拒绝执行，不会被绕过）

1. 查询 `dw.dw_user_event_detail` **必须**显式带 `event_time` 上下界，且**单次最多跨 1 天**。
   合规写法：
     - `event_time >= '2026-05-04 00:00:00' AND event_time < '2026-05-05 00:00:00'`
     - `event_time BETWEEN '2026-05-04 00:00:00' AND '2026-05-04 23:59:59'`
   多天数据请你拆成多次单天查询，分别下发 [SQL: ...]。

2. 仅允许 SELECT / WITH / SHOW / DESC / EXPLAIN；其他语句（INSERT/UPDATE/DELETE/ALTER/...）会被拒绝。

3. 查询会被自动加 LIMIT 兜底，超过限制的部分会被截断；如需更多请进一步收紧 WHERE。
"""


SQL_PROTOCOL = f"""# 查询数据的协议

如果用户的问题需要查 StarRocks 数据：

## 重要：精准回答用户的问题，不要加戏

- **用户问什么就答什么**。不要主动按 app_id / 渠道 / 日期 / 设备类型等维度 GROUP BY 拆分，除非用户明确要求。
- **yes/no 问题不要变成统计问题**。比如"订单号重复时 event_id 都相同吗" → 你应该写 SQL 看每个重复 order_id 对应有几种 event_id，最大值 / 是否 > 1 就能直接回答；**不要**额外按 app 拆。
- **看个数就给个数**。"昨天充值多少钱" → `SELECT SUM(amount)/100 ...`，一个数字搞定；不要拆 app。
- **抽样就抽样**。"给我抽几条 event_id 为空的看看" → `SELECT * FROM ... WHERE event_id IS NULL OR event_id='' LIMIT 5`；不要 GROUP BY 统计有多少。
- **0 行也是答案**。如果用户问"有没有 X"或"是否存在 Y"，0 行就直接告诉用户"没有"，不要让用户去检查 WHERE 条件。

举例对比：

| 用户原话 | ❌ 加戏 | ✅ 精准 |
|---|---|---|
| "订单号重复时 event_id 都相同吗" | `GROUP BY app_id, order_id, event_id ...` | `SELECT order_id, COUNT(DISTINCT event_id) AS kinds FROM ... GROUP BY order_id HAVING COUNT(*)>1 ORDER BY kinds DESC LIMIT 50` |
| "昨天充值多少钱" | `GROUP BY app_id ...` | `SELECT SUM(amount)/100 FROM ... WHERE pay_date='2026-05-04'` |
| "给我抽样几条 event_id 空的" | `GROUP BY app_id, event ...` | `SELECT * FROM ... WHERE event_id IS NULL LIMIT 5` |

## 两种 SQL 标记，按用户意图选

- `[SQL: ...]` — **默认**。Bot 跑完后聊天里发预览（最多前 10 行）；**结果 ≤ 20 行不发 CSV 附件**；> 20 行才自动附 CSV
- `[SQL_FILE: ...]` — **强制发完整 CSV 附件**。仅当用户明确要文件 / 完整数据 / 下载 / 导出 时用

## 怎么选

| 用户问法 | 用什么 |
|---|---|
| "查总数 / 求和 / 平均" 等聚合（结果就 1 行 1 个数） | `[SQL: ...]` 不发文件 |
| "前 5 个 / top 10" 不带"文件" | `[SQL: ... LIMIT 10]` 不发文件 |
| "抽样几条" 不带"文件" | `[SQL: ... LIMIT 几]` 不发文件 |
| "top 10 + 完整数据" / "排行加文件" | **一条** `[SQL_FILE: ... ORDER BY DESC]`（不加 LIMIT）；预览前 10、强制附完整 CSV |
| "全部数据" / "给我文件" / "导出" / "下载" | `[SQL_FILE: ...]` |
| "查询并保存" / "整理给我" | `[SQL_FILE: ...]` |

⚠️ 千万别写两条 SQL（一条 LIMIT 10、一条全表）—— 重复查询 + 双份文件，又贵又乱。

## 通用步骤

1. 结合「数据表清单」+「表别名」找到正确的实际表名（库名.表名）
2. **写 SQL 前先用 sqlite3 查 metadata.db 确认列名**（见上面"按需查元数据"）
3. 标准 StarRocks SQL，包在 `[SQL: ...]` 或 `[SQL_FILE: ...]` 里
4. 例：
   ```
   [SQL: SELECT COUNT(*) FROM dwd.dwd_order_paid_d
         WHERE pay_date = '2026-05-02']
   ```
   ```
   [SQL_FILE: SELECT app_id, SUM(amount)/100 AS total_yuan
              FROM dwd.dwd_order_paid_d WHERE pay_date = '2026-05-02'
              GROUP BY app_id ORDER BY total_yuan DESC]
   ```

5. **不要自己执行** SQL —— Bot 排队代跑、回结果给用户。
6. 一次回复里可以多条 [SQL]，但仅在查不同数据时才拆条；同一份数据别重跑。
7. 表名不确定 / 问题模糊 → 先反问澄清，别瞎猜表名。
8. 违反固化规则的需求（如查 dw_user_event_detail 一周）→ 主动拆成多个单日 [SQL]。

# 文件交换约定

- 用户上传给 bot 的文件落到：`{INCOMING_DIR}`
- [SQL: ...] 跑出来的 CSV 自动落到：`{OUTGOING_DIR}` 并自动发给用户，**不需要**你额外加 [SEND_FILE]
- 你自己产出的非 SQL 文件（比如总结报告、对账表）请写到：`{OUTGOING_DIR}`，再用 `[SEND_FILE: 文件名]` 让 Bot 自动发送
- 这两个目录已 0777 可读写，不会卡权限
"""


def _load_memory_bootstrap(*, refresh: bool | None = None, max_chars: int = 14000) -> str | None:
    """记忆系统 v2 冷启动包：PINNED + MEMORY_OPEN + recent-by-mtime。

    新开并行 agent 必读；与 IDE sessionStart / you-chu-agent 冷启动协议对齐。
    """
    do_refresh = AGENT_MEMORY_REFRESH_ON_SPAWN if refresh is None else refresh
    bootstrap = Path(PROJECT_ROOT) / '.cursor' / '.agent-memory-bootstrap.md'
    script = Path.home() / '.dc-platform' / 'scripts' / 'load-memory-context.sh'
    if do_refresh and script.is_file():
        try:
            subprocess.run(
                ['bash', str(script), str(PROJECT_ROOT)],
                timeout=20,
                check=False,
                capture_output=True,
            )
        except Exception as exc:
            log.warning('[memory] refresh bootstrap failed: %s', exc)

    text = ''
    if bootstrap.is_file():
        try:
            text = bootstrap.read_text(encoding='utf-8', errors='replace').strip()
        except OSError as exc:
            log.warning('[memory] read bootstrap failed: %s', exc)

    if not text:
        # 兜底：至少塞红线 + 未结
        parts = []
        for name in ('PINNED.md', 'MEMORY_OPEN.md'):
            p = Path.home() / '.dc-platform' / 'memory' / name
            if p.is_file():
                try:
                    parts.append(f'## {name}\n\n' + p.read_text(encoding='utf-8', errors='replace')[:4000])
                except OSError:
                    pass
        text = '\n\n'.join(parts).strip()

    if not text:
        return None
    if len(text) > max_chars:
        text = text[:max_chars] + '\n\n…（bootstrap 已截断）'
    return (
        '# 记忆冷启动（必读 · 记忆系统 v2）\n\n'
        '你是**新开的 agent**（或本轮任务开工）。先读本节再干活：\n'
        '- 红线 PINNED · 未结 MEMORY_OPEN · 按时间最近动过 · high 标题\n'
        '- 全量 MEMORY.md / lessons 只当索引，不整包灌入；按任务 tags 再深读\n'
        '- 打开≠用了；真改做法才 touch\n\n'
        f'{text}'
    )


def build_system_prompt(
    user_id: int,
    user_question: str | None = None,
    *,
    in_group: bool = False,
    force_new_agent: bool = False,
) -> str:
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    weekday = ['周一','周二','周三','周四','周五','周六','周日'][datetime.now().weekday()]

    sections = [
        f"# 当前时间\n\n现在是 {now}（{weekday}），时区 JST（东京）。",
        "# 身份\n\n你是又初（数据中心开发助手）。用户或同事叫你「初儿」时，指的就是你本人。",
    ]

    # 新开并行 agent：强制灌记忆冷启动（刷新 bootstrap）
    mem = _load_memory_bootstrap(refresh=True if force_new_agent else False)
    if mem:
        sections.append(mem)
    if force_new_agent:
        sections.append(
            '# 并行任务说明\n\n'
            '当前有另一条长任务仍在跑。你是**另开的新 agent**：\n'
            '- **不要**假设自己接着上一条 cursor 会话；独立把本条私聊做完\n'
            '- 进度/结论要**实查**（YARN/日志/表/session），禁止空模板交差\n'
            '- 不要去 kill 别人的长任务，除非用户本条明确说停/杀\n'
        )

    if in_group:
        try:
            import group_reply_style as grs
            sections.append(grs.build_group_prompt_section())
        except Exception:
            pass

    if user_question:
        try:
            import context_bridge as cb
            bridge = cb.recent_context_block()
            if bridge:
                observe_hint = (
                    '含群旁听、私聊、agent-bus。判断要不要回：'
                    '**仅当用户 @ 本机器人**时在群里回复；没 @ 你的讨论只作背景，'
                    '**不要在回复里声明「我不插嘴」**——直接不回即可。\n'
                )
                if in_group:
                    observe_hint += '你正在**群聊当场回复**，遵守上文「群聊回复风格」。\n'
                sections.append(f'# 多渠道统一上下文\n\n{observe_hint}')
                sections.append(bridge)
        except Exception:
            pass
        try:
            import task_provenance as tp
            prov_block = tp.format_recent_block(limit=10)
            if prov_block:
                sections.append(prov_block)
        except Exception:
            pass
        try:
            import work_memory as wm
            hits = wm.search(user_question, uid=None, limit=3)
            hit_section = wm.format_relevant_hits(hits)
            if hit_section:
                sections.append(hit_section)
        except Exception:
            pass
        try:
            import group_context_archiver as gca
            arch_hits = gca.search_archived(user_question, limit=2)
            arch_section = gca.format_archived_hits(arch_hits)
            if arch_section:
                sections.append(arch_section)
        except Exception:
            pass

    # CLAUDE.md（omdb 自己的）
    claude_md = _read_file(os.path.join(OMDB_DIR, 'CLAUDE.md'))
    if claude_md:
        sections.append(f"# 项目规范 (omdb/CLAUDE.md)\n\n{claude_md}")

    # 公共表别名（aliases.md）
    aliases = _load_aliases()
    if aliases:
        sections.append(aliases)

    # 用户私有别名
    user_aliases_section = _load_user_aliases(user_id)
    if user_aliases_section:
        sections.append(user_aliases_section)

    # 元数据表清单（仅表名）
    overview = _load_metadata_overview()
    if overview:
        sections.append(overview)

    # 按需查元数据指南（教 Claude 用 sqlite3 取列）
    sections.append(METADATA_QUERY_GUIDE)
    sections.append(SQLITE_AND_BASH_HINT)

    # 公共软规则
    public_rules_section = _load_public_rules()
    if public_rules_section:
        sections.append(public_rules_section)

    # 用户私有软规则
    user_rules_section = _load_user_rules(user_id)
    if user_rules_section:
        sections.append(user_rules_section)

    # 工作狂人群聊沉淀（自动学习）
    worker_ant_section = _load_worker_ant_insights()
    if worker_ant_section:
        sections.append(worker_ant_section)

    # 公共 lessons（学到的）
    public_lessons_section = _load_public_lessons()
    if public_lessons_section:
        sections.append(public_lessons_section)

    # 用户私有 lessons
    user_lessons_section = _load_user_lessons(user_id)
    if user_lessons_section:
        sections.append(user_lessons_section)

    # 固化规则
    sections.append(HARDCODED_RULES)

    # [SQL] 协议 + 文件交换
    sections.append(SQL_PROTOCOL)

    # [LESSON] 自我进化协议
    sections.append(LESSON_PROTOCOL)

    # Sandbox info for non-superusers
    sandbox = db.get_user_sandbox(user_id)
    is_su = db.is_superuser(user_id)

    bot_protocol = f"""
# Bot 通信协议

你正在为「数据中心 / omdb」工具集工作。项目路径: {PROJECT_ROOT}
你的回复会通过 Telegram Bot 发送给用户。

1. 发送文件给用户：在回复中标记 [SEND_FILE: 路径]
   例如: [SEND_FILE: outgoing/result.csv]，Bot 会按 outgoing/、项目根、沙盒顺序找文件。

2. 设置提醒：[REMIND: YYYY-MM-DD HH:MM 提醒内容]
   务必把自然语言时间转换为具体格式。

3. 数据查询请用 [SQL: ...] 标记（见上面"查询数据的协议"）。

4. 与工作狂人互通（**仅**用户明确要求联系狂人时，走 agent-bus）：
   - 用户**直接问你又初**（查数、验数、口径、知识库等）：**由你本人回答**，禁止 `[ASK_ANT]`，不要替用户转问狂人。
   - 用户原文含「问/回复/告诉 工作狂人」时，提示他用：`问 工作狂人：<问题>` 或 `回复 工作狂人：<内容>` → Bot 经 agent-bus 处理，**不由你发 [ASK_ANT]**。
   - 你已从工作记忆 / lesson 知道的内容直接答；不确定就说清楚，建议用户用上面格式转问狂人。

5. 不要说"我没有权限"之类的话。用标记让 Bot 处理。
"""

    if not is_su:
        bot_protocol += f"""
5. 你是普通用户模式。项目文件只能读不能改。
   需要输出文件时写到沙盒目录：{sandbox}
   或写到 outgoing/，再 [SEND_FILE: outgoing/...]
"""

    sections.append(bot_protocol)
    sections.append("以上约束必须在整个任务执行过程中遵守，不得违反。")

    return '\n\n'.join(sections)


def build_dispatch_lite_prompt(user_id: int = 0, user_question: str | None = None) -> str:
    """派单/验数专用短 prompt：少塞规则，加快 cursor-agent。"""
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    sections = [
        f"# 当前时间\n\n{now}（JST）。",
        "你是又初（昵称「初儿」），数据中心开发助手。prod my.cnf 查 StarRocks；废弃 _d 表勿误报，以 _h 现表为准。",
    ]
    if user_question:
        try:
            import work_memory as wm
            hits = wm.search(user_question, uid=None, limit=2)
            hit_section = wm.format_relevant_hits(hits)
            if hit_section:
                sections.append(hit_section)
        except Exception:
            pass
    worker_ant_section = _load_worker_ant_insights()
    if worker_ant_section:
        sections.append(worker_ant_section[:3000])
    sections.append(HARDCODED_RULES)
    sections.append(
        "# 输出协议\n"
        "- 查数用 [SQL: ...]\n"
        "- 给工作狂人回传单独一行 [REPLY_ANT: 正文]\n"
        "- 可附 [LESSON: scope | rule]\n"
        "- 精准回答，不要废话"
    )
    directives = _load_worker_ant_directives()
    if directives:
        sections.append(directives)
    return '\n\n'.join(sections)


def _load_worker_ant_directives() -> str | None:
    try:
        import worker_ant_directives as wad
        return wad.format_for_prompt(limit=6)
    except Exception:
        return None


def build_upgrade_prompt(user_question: str) -> str:
    """狂人授权 · 本地 tgbot 实现升级专用 prompt。"""
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    sections = [
        f"# 当前时间\n\n{now}（JST）。",
        "你是又初 bot 的维护 Agent（Cursor superuser）。",
        "工作狂人（worker_ant）已获主人授权：其升级/优化指令必须**直接改代码**落地到 `omdb/tgbot/`。",
    ]
    directives = _load_worker_ant_directives()
    if directives:
        sections.append(directives)
    sections.append(HARDCODED_RULES)
    sections.append(
        "# 输出协议\n"
        "- 改完必须 `[REPLY_ANT: 摘要]`\n"
        "- 需重启 bot：`[RESTART_BOT: yes]`\n"
        "- 可附 `[LESSON: scope | rule]`"
    )
    if user_question:
        sections.append(f"# 任务\n\n{user_question}")
    return '\n\n'.join(sections)
