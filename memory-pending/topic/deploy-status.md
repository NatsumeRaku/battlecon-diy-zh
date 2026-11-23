---
name: deploy-status
type: topic
description: 部署状态(2026-11-22)——仓库快照a613e0d/引擎修复/run_engine用法/记忆库写入故障
sources:
    - 会话 2026-11-22
aliases:
    - 部署
created: "2026-11-22"
last_updated: "2026-11-22"
---

# 部署状态 2026-11-22

- 仓库:battlecon-diy-zh 快照 a613e0d,位于 /mnt/agents/output/battlecon-diy-zh/(沙箱内,非持久)
- 拉取通道:沙箱 git 直连 github.com 被墙,走 api.github.com tarball;推送用 GitHub 插件 API 通道
- 引擎:复活协议固化于 run_engine.py(自动重排 battlecon_engine.py);修过 _modeb_v32_final.py:122 None威力bug
- 运行:python3 run_engine.py(1v1循环赛) / python3 run_engine.py boss(伯尔曼首领战)
- 已知:记忆库写入接口 unavailable(与交接提示词记录的写入故障一致),权威文件暂存 memory-pending/,恢复后按队列入库
