---
name: diy-workshop-brief
type: topic
description: 战链DIY工坊总简报——设计→实测→评分的完整流水线指南;含全部规范文件索引、自检四步、评分表接入方式与命名法;DIY会话开局必读
sources:
    - diy-internal(用户2026-11-19指示:整理出一份,以后"就按这个来")
    - diy-*角色文件
    - battlecon-glossary
    - battlecon-balance-model
    - chat
aliases:
    - 工坊简报
    - 总流程
    - DIY指南
created: "2026-11-19"
last_updated: "2026-11-19"
---

# 战链DIY工坊总简报(2026-11-19)

## 流水线
立项(读基准)→设计(机制/数值)→自检(四步)→评分(battlecon-balance-model)→实测(模拟20回合)→补丁(v1.x迭代)→出卡(diy-card-print-spec)。

## 必读文件(按序)
1. battlecon-rulebook(v4.2规则)
2. battlecon-glossary(术语/命名/冲突安检)
3. battlecon-balance-model(EP与区间)
4. convention/supreme-principle(最高准则,压于铁律之上)
5. convention/arena-output-only(边界:只出建议不改文件)
6. diy-corner-icons + diy-card-print-spec(出卡轨)

## 自检四步(每个设计必过)
1. 规则冲突:v4.2时点/护甲/韧性/投注合规
2. 自洽:资源上限/边界情况/零值退化
3. 撞名:全库E级安检(风格名互不撞词根)
4. 边界:多人局/通用位/对手无标记时效果失效路径

## 命名与收录
- DIY角色命名:{系列名}·{角色名};系列名用户钦定(例:街霸6、杀戮尖塔1/2、先古)
- 收录:diy-{角色}.md,aliases含"DIY-NN"编号
- 评分:综合EP+三角检核估分,入diy-power-rankings

## 铁律摘要(详见supreme-principle)
- 官方框架是边界;先例必须可出示;完全信息公开;对账三查;用户裁定最高
- 计数实体化:所有计数必须有实体(标记/计数物),终生台账禁用(2026-11-21铁律)
- 冷却锁定:不引用"上回合使用的牌";跨拍历史状态难核对,条件一律当场可验(2026-11-20)

## 版本规则
- 机制改动→x.1;数值微调→x.x;文本/格式裁定→版本号不变(注明sweep)
