# AUTO-MAS 配置体系笔记（2026-11-27 行239调查）

> 用途：改游戏自动化行为时查此笔记。官网+文档 doc.auto-mas.top 已核实。

## 本体
- 安装：`C:\Program Files\AUTO-MAS`（Electron，AUTO-MAS.exe）
- 用户数据：`%AppData%\Roaming\AUTO-MAS`（.auto-mas-user-data=legacy → 数据在安装目录侧）

## 两个托管（config\legacy-json\ScriptConfig.json）
| 托管 | 脚本 | RootPath | 游戏路径 |
|---|---|---|---|
| 04d61186-…(鸣潮日常) | OK-WW | `C:\Users\Natsume\AppData\Local\ok-ww` | `D:\Wuthering Waves\launcher.exe` |
| 27d52bd4-…(原神日常) | BetterGI | `C:\Program Files\BetterGI` | （BetterGI 内自管） |

## 调度（config\queues.yaml + legacy-json\QueueConfig.json）
- 鸣潮队列 148f197f：TimeSet 每日 14:00（NextRunAt 旧值显示 14:47 属历史），AfterAccomplish=NoAction
- 原神队列 ec468b76：TimeSet 每日 15:00，AfterAccomplish=**Hibernate**（跑完休眠）
- 托盘/快捷启动引用同一 taskId（frontend_config.json TrayItems）

## BetterGI 配置机制（官方文档）
- MAS 运行时把账号独立副本物化到 `{RootPath}\User\OneDragon\MAS独立配置.json` 槽位，以 `startOneDragon MAS独立配置` 启动，结束回读快照
- 改自动化行为 = 改 `C:\Program Files\AUTO-MAS\data\27d52bd4-9539-42c8-bda7-e7a509e59c3a\{账号ID}\OneDragon\{名称}.json`（副本；种子优先级：副本>BetterGI 实配>内置模板）
- 8 内置组开关：邮件/合成树脂/地脉花/秘境/首领讨伐/幽境危战/每日奖励/尘歌壶；开关语义=置位不删组
- 复杂设置在 BetterGI GUI（User\config.json），MAS 不动
- 识别要求游戏 1920×1080

## OK-WW 配置机制（官方文档）
- MAS 任务前备份 ok-ww `working\configs` → 任务期临时覆写高频字段 → 跑完（成功/失败/被杀）自动还原
- 配置来源三选一：共享/独立/原生；原生+关覆写 = 完全用 OK-WW 原生配置
- MAS 只接管：日常任务、多账号日常任务
- 官方启动器限定：必须官方 launcher.exe，不支持 WeGame

## 与本地模型共存的铁律
- 游戏画质不归 MAS/脚本管 → 不能靠改注册表 GpuPreference 把游戏赶去 780M（游戏内画质档不匹配会卡死识图）
- GPU 静默期 14:00~17:30 见《常驻指令-v2.md》第九节；兜底计划任务 llama-gpu-blackout 每日 13:45 taskkill llama-server.exe

## 可代操作项（用户点头后）
- 调队列时间/星期；加减任务组；切配置来源；通知设置
