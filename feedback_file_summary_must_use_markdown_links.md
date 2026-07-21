---
name: 输出文件总结时必须用 markdown 链接
description: 报告 / 总结里提到任何创建或修改过的文件路径都必须写成 markdown 链接（[name](relative/path)）方便点击，不要用反引号或纯文本。
type: feedback
originSessionId: ce0993a6-f017-4276-92db-80fdc4888c85
---
报告 / 总结 / 交付清单里提到**任何**创建或修改过的文件路径，**必须**用 markdown 链接格式：

```
[check_late_arrivals.sh](.claude/database/scripts/check_late_arrivals.sh)
[dws.dws_app_order_d_h.md](.claude/database/playbooks/dws.dws_app_order_d_h.md)
[dws_app_order_d_h.sql](ops_system/04.dws/dws_app_order_d_h/dws_app_order_d_h.sql)
```

**不要**用：
- 反引号包路径：`` `path/to/file.md` ``  ← 不可点击
- 纯文本路径：`path/to/file.md`           ← 不可点击
- 绝对路径：`/Users/arthur/...`            ← VSCode 扩展不解析为链接
- HTML `<code>` 标签                       ← 同样不可点击

**Why**：用户在 VSCode 扩展里看交付清单时要能直接点开文件——反引号或纯文本要复制路径再 Cmd-O 打开，效率差。系统提示里其实已经写了这条规矩，但我之前没坚持执行。用户原话："以后输出文件总结的时候要带上文件链接"。

**How to apply**：

1. 写"已交付 / 已修改 / 已创建"清单时，每个文件名都包成 markdown 链接
2. 路径必须是**相对工作目录根**的相对路径，不是绝对路径
3. 引用文件里的具体行也用 `[name.ts:42](src/name.ts#L42)` 格式
4. 引用目录用 `[dirname/](path/to/dirname/)`
5. **唯一例外**：在 fenced code block 里的路径不用包链接（那是代码示例）；普通正文段落里的所有文件引用都要包

**例子（对话回复）**：

```markdown
| 文件 | 改动 |
|---|---|
| [pull_om.py](omdb/pull_om.py) | 改 token 解析逻辑 |
| [README.md](omdb/README.md) | 加 Python 环境一节 |

新建剧本 [dws.dws_app_order_d_h.md](.claude/database/playbooks/dws.dws_app_order_d_h.md)，
ETL 改在 [dws_app_order_d_h.sql](ops_system/04.dws/dws_app_order_d_h/dws_app_order_d_h.sql)。
```
