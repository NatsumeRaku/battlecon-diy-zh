# -*- coding: utf-8 -*-
"""非标时点收编(2026-11-22 用户拍板)
- 触发条件类 -> 每当+条件
- 伯尔曼首领剧本 Press/退却/回收/回合流程 -> 持续(机制术语保留在文本内,属待规范化数据)
- 卡琳"行动"、绯雪"防御" -> 持续(保留原文,待核)
"""
import json

def edit(path, card_pred, fn):
    d = json.load(open(path, encoding='utf-8'))
    eff = d.get('效果')
    seqs = eff if isinstance(eff, list) else []
    if isinstance(eff, dict):
        for face in ('α面', 'β面'):
            if isinstance(eff.get(face), list): seqs += eff[face]
    n = 0
    for e in seqs:
        if isinstance(e, dict) and card_pred(e):
            fn(e); n += 1
    json.dump(d, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f'{path}: {n}条')

B = 'json-db'

# 1. 触发条件类 -> 每当+条件
edit(f'{B}/战争篇-BCW/吕克·冯·戈特/风格_永恒.json',
     lambda e: e.get('时点') == '被命中',
     lambda e: e.update({'时点': '每当', '条件': '你被命中时,伤害结算前'}))
edit(f'{B}/线上版-BCO/赛博·圣米克哈尔·伊森/风格_不变的.json',
     lambda e: e.get('时点') == '首次被命中',
     lambda e: e.update({'时点': '每当', '条件': '你首次被命中时'}))
edit(f'{B}/线上版-BCO/赛博·塞萨尔·格里斯特/UA_恐吓.json',
     lambda e: e.get('时点') == '首次致死',
     lambda e: e.update({'时点': '每当', '条件': '你首次致死时'}))
edit(f'{B}/毁灭篇-BCD/塞萨尔·格里斯/UA_威胁等级.json',
     lambda e: e.get('时点') == '即将第5枚',
     lambda e: e.update({'时点': '每当', '条件': '即将放置第5枚累积物时'}))
edit(f'{B}/毁灭篇-BCD/塞萨尔·格里斯/UA_威胁等级.json',
     lambda e: e.get('时点') == '生命首次降至1以下',
     lambda e: e.update({'时点': '每当', '条件': '你的生命首次降至1以下时'}))

# 2. 伯尔曼首领剧本(待规范化) 机制术语撤出时点字段
for t in ('Press', '退却', '回收', '回合流程'):
    edit(f'{B}/首领剧本/巨龙伯尔曼/UA_巨龙伯尔曼.json',
         lambda e, t=t: e.get('时点') == t,
         lambda e: e.update({'时点': '持续'}))

# 3. 单发残留
edit(f'{B}/毁灭篇-BCD/卡琳·布兰特福特与雅格/UA_夹击.json',
     lambda e: e.get('时点') == '行动',
     lambda e: e.update({'时点': '持续'}))
edit(f'{B}/鸣潮/绯雪/风格_居合.json',
     lambda e: e.get('时点') == '防御',
     lambda e: e.update({'时点': '持续'}))
