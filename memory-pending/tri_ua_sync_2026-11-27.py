# -*- coding: utf-8 -*-
"""行264: 同步 TRI 各角色 character.json 卡牌清单(最小 diff,保持原键序与 indent=2)"""
import json, io, os, sys

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    'json-db', 'en', '试炼篇-TRI')

ADD = {
    'Amon': ['UA_Damage Control.json'],
    'Dravil': ['UA_Ebbing Tide.json'],
    'Hayden': ['UA_Breaking Point.json', '配件_狂怒·控制计数物.json'],
    'Kimbhe': ["UA_Archmage's Staff.json", '配件_法杖.json'],
    'Lucida Malephaise': ['UA_Jaws of Malephaise.json', '配件_撕裂·吞噬指示物.json'],
    'Trias': ['UA_Embellish.json'],
    'Wardlaw': [],
    'Burgundy': ['UA_Color Burn.json', '配件_颜料.json'],
    'Cindra': ['UA_Rebirth.json'],
    'Dareios': ['UA_Dipsomania.json'],
}

FIX = {'Wardlaw': {'特技(UA)_Beatdown.json': 'UA_Beatdown.json'}}

for d, adds in ADD.items():
    p = os.path.join(BASE, d, 'character.json')
    with io.open(p, encoding='utf-8') as f:
        raw = f.read()
    obj = json.loads(raw)
    lst = obj.get('卡牌清单')
    if lst is None:
        print('SKIP(no list)', d); continue
    fixed = []
    changed = False
    for it in lst:
        n = FIX.get(d, {}).get(it, it)
        if n != it:
            changed = True
        fixed.append(n)
    for a in adds:
        if a not in fixed:
            fixed.append(a); changed = True
    if not changed:
        print('NOCHANGE', d); continue
    obj['卡牌清单'] = fixed
    out = json.dumps(obj, ensure_ascii=False, indent=2)
    with io.open(p, 'w', encoding='utf-8', newline='\n') as f:
        f.write(out)
    print('U', d, len(lst), '->', len(fixed))
