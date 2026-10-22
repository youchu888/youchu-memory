---
date: 2026-10-22
tags: [pipeline-runner, spark, deploy, prod]
severity: high
domain: ops
---

# pipeline-runner：禁止生产机单文件就地编译覆盖 jar

## 背景

又初在 hadoop-1 `/home/ec2-user/pipeline-runner` 只替换 `BitmapUdf.scala`（BINARY 版）就地 `sbt assembly`，源码其余仍是 9-29 旧树，编出 0.4.0 覆盖生产 daemon/控制面 jar，导致 9-29 之后功能丢失、平台建表失败、补数用退化包；daemon 重启即生产事故。知秋已恢复 1.2.0（bus#11169）。

## 坑 / 错误做法

- 生产目录单文件改、就地编、覆盖正在跑的 assembly/serve jar
- 用过期工作树 + 单文件补丁冒充「热修」

## 正确做法

1. 改调度器核心代码必须先提交仓库，与仓库全量同步后整包编译
2. 先在**测试集群**测过（含大分区 BINARY vs Kryo 对照），再由知秋/狂人随版本上生产
3. 本机开发用 `pipeline-runner-dev` 出 jar；**禁止**覆盖 `/home/ec2-user/pipeline-runner/target` 里 daemon/serve 正在用的包
4. 生产源码与运行 jar 版本不一致时，先对齐再编，勿在 prod 树上试验

## 验证

- prod `pipeline-runner-serve.jar` Manifest `Implementation-Version` 与知秋发布版一致（恢复后为 1.2.0）
- 新功能只经 testcluster 验证后再随版本发布

## 关联

- bus#11169 · commit `8335383f`（BINARY 改动）
