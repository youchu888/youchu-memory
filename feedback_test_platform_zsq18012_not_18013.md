# 测试平台连法（指标库）· 狂人 2026-11-26

- **正式测试平台**：`https://zsq18012.dcpusff.my`（Cloudflare → 18012）。免 VPN、免 SSH 隧道。
- **调用**：本机 `curl` + 浏览器 User-Agent；裸 curl / python urllib 易被 Cloudflare 403。
- **勿连 18013**：演练实例，按生产模式跑演练库；旧令牌 401 正常。
- **令牌**：平台账号登录 `/login` → `/api-tokens` 自建，概念层 API 带 Bearer。
- **元数据 MySQL**：`172.31.6.193:3306` 仅 AWS 内网；入口 `root@43.213.80.248`（不给 bot 开 root 公钥）。连不上时把只读缺口 SQL 交给狂人代跑；能走概念层 API 优先 API。
