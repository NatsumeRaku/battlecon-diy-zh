# -*- coding: utf-8 -*-
"""数值层规范化(2026-11-22 用户拍板)
存储层语法(封闭):
  int:  -?\d+                (含负数;风格修正值符号入数值,展示层补"+")
  str:  [+-]?\d+~[+-]?\d+    (范围,两端可为负)
        [+-]?\d+~X | \d*X    (含变量)
        N/A                  (印刷无值)
        上述任意 + 标签后缀   (<initiative>/<group-attack>/<stun-shield>)
迁移:
  纯数字str -> int; "▲"->"<initiative>"; "🛡"->"<stun-shield>"; "距离+N~M"去冗余前缀
  其余不规则值原样保留并输出清单,等用户逐条裁定
"""
import json, glob, re, collections

ZH = 'json-db/zh'
KEYS = ('距离', '威力', '速度', '韧性', '破点计数器')
INT_RE = re.compile(r'^[+-]?\d+$')
SYMBOLIC_RE = re.compile(
    r'^(?:[+-]?\d+~[+-]?\d+|[+-]?\d+~X|\d*X|-?\d+|N/A)(<initiative>|<group-attack>|<stun-shield>)*$')
stat = collections.Counter()
leftover = []

def fix(v):
    if isinstance(v, int):
        stat['已是int'] += 1; return v
    if not isinstance(v, str):
        stat['其他类型'] += 1; return v
    s = v.strip()
    if INT_RE.match(s):
        stat['str->int'] += 1; return int(s)
    s = re.sub(r'^距离(?=[+-])', '', s)
    s = s.replace('▲', '<initiative>').replace('🛡', '<stun-shield>').replace('👥', '<group-attack>')
    if s != v.strip(): stat['标签/前缀规范化'] += 1
    if s and SYMBOLIC_RE.match(s):
        stat['符号值合规'] += 1; return s
    stat['待裁定'] += 1
    return v

for f in glob.glob(f'{ZH}/**/*.json', recursive=True):
    d = json.load(open(f, encoding='utf-8'))
    changed = False
    def walk(nd, path):
        global changed
        for k, v in (nd or {}).items():
            if isinstance(v, dict): walk(v, path); continue
            if k in KEYS:
                nv = fix(v)
                if nv != v: nd[k] = nv; changed = True
                if isinstance(nv, str) and not SYMBOLIC_RE.match(nv):
                    leftover.append((path, k, nv))
    walk(d.get('数值'), f)
    if changed:
        json.dump(d, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

print('统计:', dict(stat))
print('\n待裁定清单:')
for p, k, v in leftover: print(f'  {p.split("zh/")[-1]} | {k} = {v!r}')
