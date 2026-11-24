# -*- coding: utf-8 -*-
"""效果条目结构并轨迁移(2026-11-22 用户拍板)
规则:
1. {"持续": X}            -> {"时点":"持续","效果":X}
2. {"持续": X, "效果": Y} -> {"时点":"每当","条件":X,"效果":Y}
3. {"效果": Y}            -> {"时点":"持续","效果":Y}
4. "时点": ""             -> "持续"; 空"条件"键删除
"""
import json, glob, collections

ROOT = 'json-db'
files = sorted(glob.glob(f'{ROOT}/**/*.json', recursive=True))
log = collections.Counter()

def migrate_entry(e):
    keys = set(e.keys())
    if keys == {'持续'}:
        log['持续键并轨'] += 1
        return {'时点': '持续', '效果': e['持续']}
    if keys == {'持续', '效果'}:
        log['持续条件转每当'] += 1
        return {'时点': '每当', '条件': e['持续'], '效果': e['效果']}
    if keys == {'效果'}:
        log['裸效果补持续'] += 1
        return {'时点': '持续', '效果': e['效果']}
    if e.get('时点', None) == '':
        e['时点'] = '持续'; log['空时点转持续'] += 1
    if '条件' in e and e['条件'] == '':
        del e['条件']; log['清理空条件'] += 1
    return e

changed_files = 0
for f in files:
    d = json.load(open(f, encoding='utf-8'))
    changed = False
    eff = d.get('效果')
    if isinstance(eff, list):
        new = [migrate_entry(dict(e)) if isinstance(e, dict) else e for e in eff]
        if new != eff:
            d['效果'] = new; changed = True
    elif isinstance(eff, dict):
        for face in ('α面', 'β面'):
            if isinstance(eff.get(face), list):
                new = [migrate_entry(dict(x)) if isinstance(x, dict) else x for x in eff[face]]
                if new != eff[face]:
                    eff[face] = new; changed = True
    if changed:
        json.dump(d, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        changed_files += 1

print('改动文件数:', changed_files)
for k, v in log.most_common():
    print(f'  {k}: {v}')

# 校验:全库重扫,确认无残留
residual = collections.Counter()
for f in files:
    d = json.load(open(f, encoding='utf-8'))
    eff = d.get('效果')
    seqs = []
    if isinstance(eff, list): seqs = eff
    elif isinstance(eff, dict):
        for face in ('α面', 'β面'):
            if isinstance(eff.get(face), list): seqs += eff[face]
    for e in seqs:
        if isinstance(e, dict):
            residual[tuple(sorted(e.keys()))] += 1
            if e.get('时点', '缺') in ('', '缺'): residual['!!!残留异常时点'] += 1
print('\n迁移后效果条目键组合:')
for k, v in residual.most_common():
    print(f'  {k}: {v}')
