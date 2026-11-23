# -*- coding: utf-8 -*-
"""杀戮尖塔1·先古 角色名挂"先古·"前缀(2026-11-22 用户拍板)
- 目录: 杀戮尖塔1·先古/X -> 杀戮尖塔1·先古/先古·X
- JSON: "角色"字段、character.json"名称" -> 先古·X
- character.json "id" 统一为 杀戮尖塔1·先古-先古·X(原id混乱:sts1-defect等)
"""
import json, glob, os

BASE = 'json-db/杀戮尖塔1·先古'
NAMES = ['故障机器人', '观者', '铁甲战士', '静默猎手']
SERIES = '杀戮尖塔1·先古'

for old in NAMES:
    new = f'先古·{old}'
    olddir, newdir = f'{BASE}/{old}', f'{BASE}/{new}'
    assert os.path.isdir(olddir), olddir
    os.rename(olddir, newdir)
    for f in sorted(glob.glob(f'{newdir}/*.json')):
        d = json.load(open(f, encoding='utf-8'))
        if d.get('角色') == old:
            d['角色'] = new
        if d.get('卡类') == '角色':
            assert d.get('名称') == old, f
            d['名称'] = new
            d['id'] = f'{SERIES}-{new}'
        json.dump(d, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f'{old} -> {new} 完成')

# 引擎状态键联动
for eng in ('battlecon_engine.py', '_engine_ext.py'):
    s = open(eng, encoding='utf-8').read()
    s2 = s.replace("hit_by_观者", "hit_by_先古·观者")
    if s2 != s:
        open(eng, 'w', encoding='utf-8').write(s2)
        print(f'{eng}: hit_by_键已联动')
