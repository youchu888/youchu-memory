# 红线续篇（31+）

`PINNED.md` 只保留首页 **1–30**，冻结不顶换。

## 新红线怎么写

1. 看本目录已有最大序号，**接着编**（当前见各文件内 `N. **标题**`）
2. 新建 `pinned/NN-短名.md`，正文一行：`N. **结论** — 一句；细节链 feedback/lesson`
3. 同步写 `feedback_*.md`（或 update 旧条）
4. **禁止**改/删/替换 `PINNED.md` 1–30 来腾位置

## 怎么查

```bash
bash ~/.dc-platform/scripts/lookup-rules.sh 关键词
```

脚本会同时扫 `PINNED.md` + `pinned/*.md`。启动包不灌全文。
