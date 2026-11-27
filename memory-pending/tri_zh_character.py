# -*- coding: utf-8 -*-
"""行265: zh 树 character.json 建档（镜像 en，清单指向 zh 文件名）"""
import json, io, os, glob
from tri_zh_translate import EN, ZH, ROLE
from tri_zh_build import build_name_map, pick, zh_fname

nm = build_name_map()
for cp in sorted(glob.glob(os.path.join(EN, '*', 'character.json'))):
    dirn = os.path.basename(os.path.dirname(cp))
    d = json.load(io.open(cp, encoding='utf-8'))
    en_role = d.get('角色', dirn)
    zh_role = ROLE.get(en_role) or ROLE.get(dirn) or en_role
    files = []
    for p in sorted(glob.glob(os.path.join(EN, dirn, '*.json'))):
        bn = os.path.basename(p)
        if bn == 'character.json':
            continue
        dd = json.load(io.open(p, encoding='utf-8'))
        zhn = pick(nm, dd.get('名称', ''))
        files.append(zh_fname(bn, zhn, dd['卡类']))
    files.sort()
    out = {}
    out['卡类'] = '角色'
    out['名称'] = zh_role
    out['角色'] = zh_role
    out['系列'] = d['系列']
    out['来源'] = d['来源']
    note = '行265 zh建档;英文:%s' % d.get('英文', en_role)
    if d.get('称号'):
        note += ';称号:%s(无官方译名,照录待译)' % d['称号']
    note += ';译名依对照表行202考据拟译[待核]'
    if d.get('备注'):
        note += ';en备注:' + d['备注'][:120]
    out['备注'] = note
    out['卡牌清单'] = files
    if d.get('英文'):
        out['英文'] = d['英文']
    if d.get('中文名'):
        out['中文名'] = d['中文名']
    zp = os.path.join(ZH, dirn, 'character.json')
    os.makedirs(os.path.dirname(zp), exist_ok=True)
    with io.open(zp, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print('C', dirn, len(files))
