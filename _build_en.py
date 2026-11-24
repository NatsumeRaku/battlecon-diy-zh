# -*- coding: utf-8 -*-
"""json-db/en 骨架搭建(2026-11-22 用户拍板B案)
原则:
- 只录官方英文原文,不回译;无源部分留空+标记待补
- 结构与 zh 完全同构(同文件名/同字段),便于双语对照与引擎复用
- 数值为语言中立的卡面数据,随骨架携带
- 范围:官方系列(毁灭篇-BCD/战争篇-BCW/线上版-BCO);DIY系列暂不处理
"""
import json, glob, os

OFFICIAL = ['毁灭篇-BCD', '战争篇-BCW', '线上版-BCO']
ZH, EN = 'json-db/zh', 'json-db/en'
n_char, n_card = 0, 0

for series in OFFICIAL:
    for char_dir in sorted(glob.glob(f'{ZH}/{series}/*/')):
        char_name = os.path.basename(char_dir.rstrip('/'))
        out_dir = f'{EN}/{series}/{char_name}'
        os.makedirs(out_dir, exist_ok=True)
        for zf in sorted(glob.glob(f'{char_dir}/*.json')):
            d = json.load(open(zf, encoding='utf-8'))
            fn = os.path.basename(zf)
            if d.get('卡类') in ('角色', '首领(Boss)'):
                # 角色卡:英文名为已核实字段(zh的"英文"字段,源自实卡)
                nd = {
                    '名称': d.get('英文', ''),
                    '中文名': d.get('名称', ''),
                    '卡类': d.get('卡类', ''),
                    '类别': d.get('类别', '斗士'),
                    '系列': series,
                    '称号': '',
                    '类型': d.get('类型', ''),
                    '难度': d.get('难度', ''),
                    '机制概述': '',
                    '机制名': '',
                    '卡牌清单': d.get('卡牌清单', []),
                    'id': (d.get('id') or f"{series}-{char_name}"),
                    '英文状态': '名称已核实;称号/机制概述/机制名待补官方原文',
                    '来源': '名称源自zh库实卡字段;其余待补(无官方英文源)',
                }
                n_char += 1
            else:
                # 卡牌:骨架——数值携带,效果留空待补
                nd = {
                    '名称': '',
                    '中文名': d.get('名称', '') if not isinstance(d.get('名称'), dict) else d['名称'],
                    '角色': char_name,
                    '卡类': d.get('卡类', ''),
                    '系列': series,
                }
                if '角标' in d: nd['角标'] = d['角标']
                if '数值' in d: nd['数值'] = d['数值']
                eff = d.get('效果')
                if isinstance(eff, list):
                    nd['效果'] = [{k: ('' if k == '效果' else v) for k, v in e.items()}
                                  if isinstance(e, dict) else e for e in eff]
                elif isinstance(eff, dict):
                    nd['效果'] = {face: [{k: ('' if k == '效果' else v) for k, v in e.items()}
                                          if isinstance(e, dict) else e for e in lst]
                                  for face, lst in eff.items()}
                nd['英文状态'] = '骨架待补:卡名/效果需官方英文原文'
                nd['来源'] = '待补(无官方英文源)'
                n_card += 1
            json.dump(nd, open(f'{out_dir}/{fn}', 'w', encoding='utf-8'),
                      ensure_ascii=False, indent=2)

print(f'en骨架完成: 角色卡{n_char}, 卡牌{n_card}, 共{n_char+n_card}文件')
