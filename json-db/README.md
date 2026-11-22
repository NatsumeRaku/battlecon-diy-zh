# 战链卡面 JSON 数据库(层级规范 v1)

## 目录结构
json-db/
├── {系列名}/                  # 例:毁灭篇-BCD / 战争篇-BCW / 街霸6(DIY)
│   └── {角色名}/
│       ├── character.json     # 角色元数据(名称/类型/难度/机制/角标分配/卡牌清单)
│       ├── UA_{机制名}.json    # 特技牌
│       ├── 风格_{名}.json ×5   # 一张一json
│       ├── 专属_{名}.json
│       └── 终结技_{α名}_{β名}.json  # 双面卡合一json(两面分键)
## 字段规范
- id: {系列缩写}-{角色}-{卡类}-{名}
- 数值: 风格=修正值(字符串表示区间/+号);招式/专属/终结技=绝对值;N/A=null语义见glossary
- 效果: [{时点, 条件?, 可选?, 效果, 色彩层?}];持续型用{"持续":...}
- 角标: 字符串token体系(<red-diamond>/<yellow-hexagon>/<green-triangle>/<orange-pentagon>/<blue-circle>/<gray-moon>等),与<group-attack>/<initiative>/<fixed>同体系
- 优先级: 官方锁定(实卡/PnP) > 知乎已核 > 二手待核 > 库内拟译
- last_updated: ISO日期
## 试用首角色:毁灭篇-凯恩戈特·雷克森(官方锁定数据,角标五色已实锤)
