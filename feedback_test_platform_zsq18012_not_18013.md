# 测试平台连法（指标库）· 狂人 2026-11-26

- **正式测试平台**：`https://zsq18012.dcpusff.my`（Cloudflare → 18012）。免 VPN、免 SSH 隧道。
- **调用**：本机 `curl` + 浏览器 User-Agent；裸 curl / python urllib 易被 Cloudflare 403。
- **勿连 18013**：演练实例，按生产模式跑演练库；旧令牌 401 正常。
- **令牌**：平台账号登录 `/login` → `/api-tokens` 自建，概念层 API 带 Bearer。
- **元数据 MySQL**：`172.31.6.193:3306` 仅 AWS 内网；入口 `root@43.213.80.248`（不给 bot 开 root 公钥）。连不上时把只读缺口 SQL 交给狂人代跑；能走概念层 API 优先 API。

## 知秋 2026-11-26 增补（更正探连）

- 临时脚本**不许**拷到服务器跑；跑过的脚本要进 git，按可管理方式执行。
- 又初缺口 SQL 已收进仓：`data-jobs/checks/probes/20261126_youchu_metric_gap/`；何时/如何跑等知秋再通知。
- 后台每 5 分钟探连**已停**；眼下**不用等 SQL 结果**，先用概念层 API 做复核。
