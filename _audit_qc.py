# -*- coding: utf-8 -*-
"""非DEV全文质量审校：zh/en配对 + 数值保真 + 时点对源"""
import json, glob, re, os, sys
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))

def load(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)

def zh_cards():
    for p in glob.glob(BASE + '/json-db/zh/**/*.json', recursive=True):
        if p.endswith('character.json'):
            continue
        d = load(p)
        if d.get('系列', '') == '毁灭篇-DEV':
            continue
        yield p, d

def en_cards():
    for p in glob.glob(BASE + '/json-db/en/**/*.json', recursive=True):
        if p.endswith('character.json'):
            continue
        d = load(p)
        if d.get('系列', '') == '毁灭篇-DEV':
            continue
        yield p, d

# ---------- 1. 构建角色目录映射 ----------
# 通过 zh 备注里的「英文原卡:XXX」反查 en 目录
char_map = {}  # zh_char_dir_rel -> en_char_dir_rel
en_index = defaultdict(list)  # lower(card en name) -> [(en_char_rel, path)]
for p, d in en_cards():
    rel = p.replace('\\', '/')
    en_char_rel = '/'.join(rel.split('/json-db/en/')[-1].split('/')[:2])  # 系列/角色
    nm = str(d.get('名称', ''))
    en_index[nm.lower()].append((en_char_rel, p))

votes = defaultdict(lambda: defaultdict(int))
for p, d in zh_cards():
    rel = p.replace('\\', '/')
    zh_char_rel = '/'.join(rel.split('/json-db/zh/')[-1].split('/')[:2])
    note = str(d.get('备注', ''))
    m = re.search(r'英文原卡[=:：]\s*([^;；,，。\n]+)', note)
    if not m:
        m = re.search(r'英文原词[=:：]\s*([^;；,，。\n]+)', note)
    if m:
        en_name = m.group(1).strip().rstrip('"').strip()
        for en_char_rel, _ in en_index.get(en_name.lower(), []):
            votes[zh_char_rel][en_char_rel] += 1

for zh_rel, counter in votes.items():
    best = max(counter.items(), key=lambda kv: kv[1])
    char_map[zh_rel] = best[0]

# 手动补充已知映射（备注缺失时）
KNOWN = {
    '战争篇-WAR/华彩骑士': '战争篇-WAR/Cadenza',
    '独立-SLO/卢修斯': '独立-SLO/Lucius',
}
for k, v in KNOWN.items():
    char_map.setdefault(k, v)

print('== 角色映射（zh->en）==', len(char_map))
for k in sorted(char_map):
    print(' ', k, '->', char_map[k])

# ---------- 2. 卡片配对 + 数值保真 ----------
def norm_num(v):
    """提取数值语义：返回 (kind, tokens)"""
    s = str(v).strip()
    if s in ('N/A', ''):
        return ('na', s)
    return ('val', s)

def stat_signature(num):
    if not isinstance(num, dict):
        return None
    if 'α面' in num or 'β面' in num:
        return tuple((s, tuple(sorted((k, str(v)) for k, v in num.get(s, {}).items())))
                     for s in ('α面', 'β面') if s in num)
    return tuple(sorted((k, str(v)) for k, v in num.items()))

def pairs_for(zh_char_rel):
    en_rel = char_map.get(zh_char_rel)
    if not en_rel:
        return None
    zhs = {}
    for p, d in zh_cards():
        rel = p.replace('\\', '/')
        if '/'.join(rel.split('/json-db/zh/')[-1].split('/')[:2]) != zh_char_rel:
            continue
        zhs[os.path.basename(p)] = (p, d)
    ens = {}
    for p, d in en_cards():
        rel = p.replace('\\', '/')
        if '/'.join(rel.split('/json-db/en/')[-1].split('/')[:2]) != en_rel:
            continue
        ens[os.path.basename(p)] = (p, d)
    return zhs, ens

num_mismatch = []
unpaired_zh = []
unpaired_en = []
timing = []  # (rel, 时点, 文本, en_时点, en_text)

# en trigger word extraction
WHEN_RE = re.compile(r'\b(Whenever|When)\b', re.I)

for zh_char_rel in sorted(char_map):
    res = pairs_for(zh_char_rel)
    if not res:
        continue
    zhs, ens = res
    # pair by 卡类+角标+数值sig fallback: file order of same 卡类
    used_en = set()
    for zb, (zp, zd) in sorted(zhs.items()):
        # 1) exact filename
        if zb in ens and zb not in used_en:
            eb, (ep, ed) = zb, ens[zb]
        else:
            # match by 卡类 + 名称含备注英文原卡
            note = str(zd.get('备注', ''))
            m = re.search(r'英文原卡[=:：]\s*([^;；,，。\n]+)', note) or \
                re.search(r'英文原词[=:：]\s*([^;；,，。\n]+)', note)
            cand = None
            if m:
                en_name = m.group(1).strip().rstrip('"').strip()
                for b, (pp, dd) in ens.items():
                    if b in used_en:
                        continue
                    if str(dd.get('名称', '')).lower() == en_name.lower():
                        cand = (b, (pp, dd))
                        break
            if cand is None:
                # match by 卡类 + 角标 + 数值signature
                for b, (pp, dd) in ens.items():
                    if b in used_en:
                        continue
                    if dd.get('卡类') == zd.get('卡类') and dd.get('角标') == zd.get('角标') \
                       and stat_signature(dd.get('数值')) == stat_signature(zd.get('数值')):
                        cand = (b, (pp, dd))
                        break
            if cand is None:
                # match by 卡类 only if unique remaining
                rem = [(b, (pp, dd)) for b, (pp, dd) in ens.items() if b not in used_en
                       and dd.get('卡类') == zd.get('卡类')]
                if len(rem) == 1:
                    cand = rem[0]
            if cand is None:
                unpaired_zh.append((zh_char_rel, zb))
                continue
            eb, (ep, ed) = cand
        used_en.add(eb)

        # 数值比对（语义化：提取数字/符号）
        def num_sem(v):
            s = str(v).strip()
            s2 = s.replace('<initiative>', '').replace('<stun-shield>', '')
            return re.sub(r'\s+', '', s2)
        zn, en_ = zd.get('数值', {}), ed.get('数值', {})
        def flat(n):
            out = {}
            if isinstance(n, dict):
                if 'α面' in n or 'β面' in n:
                    for s in ('α面', 'β面'):
                        for k, v in (n.get(s) or {}).items():
                            out[f'{s}.{k}'] = num_sem(v)
                else:
                    for k, v in n.items():
                        out[k] = num_sem(v)
            return out
        fz, fe = flat(zn), flat(en_)
        for k in set(fz) | set(fe):
            if k not in fz:
                num_mismatch.append((zb if zb == eb else f'{zb}|{eb}', k, '(zh缺)', fe[k]))
            elif k not in fe:
                num_mismatch.append((f'{zb}|{eb}', k, fz[k], '(en缺)'))
            elif fz[k] != fe[k]:
                num_mismatch.append((f'{zb}|{eb}', k, fz[k], fe[k]))

        # 时点比对
        def ents(d):
            eff = d.get('效果', [])
            out = []
            if isinstance(eff, list):
                out = [e for e in eff if isinstance(e, dict)]
            elif isinstance(eff, dict):
                for s in ('α面', 'β面'):
                    for e in (eff.get(s) or []):
                        if isinstance(e, dict):
                            out.append(e)
            return out
        ze, ee = ents(zd), ents(ed)
        if len(ze) != len(ee):
            num_mismatch.append((f'{zb}|{eb}', '效果条数', len(ze), len(ee)))
        for i, (a, b) in enumerate(zip(ze, ee)):
            ta = re.sub(r'<[^>]+>', '', str(a.get('效果', ''))).strip()
            tb = re.sub(r'<[^>]+>', '', str(b.get('效果', ''))).strip()
            wa = '每当' if ta.startswith('每当') else ('当' if ta.startswith('当') else '')
            wb_m = WHEN_RE.search(tb)
            wb = ''
            if wb_m:
                wb = '每当' if wb_m.group(1).lower() == 'whenever' else '当'
            fpa = str(a.get('时点', ''))
            if fpa in ('当', '每当') or wa or wb:
                if (fpa != wa and wa) or (wb and fpa != wb and not wa) or (wa and wb and wa != wb):
                    timing.append((zh_char_rel + '/' + zb, fpa, ta[:60], wb, tb[:60], i))
    for b in ens:
        if b not in used_en:
            unpaired_en.append((char_map[zh_char_rel], b))

print()
print('== 数值/结构不一致:', len(num_mismatch))
for item in num_mismatch[:40]:
    print('  ', item)
print()
print('== 时点打架候选:', len(timing))
for item in timing[:60]:
    print('  ', item)
print()
print('== 未配对 zh:', len(unpaired_zh))
for item in unpaired_zh[:20]:
    print('  ', item)
print('== 未配对 en:', len(unpaired_en))
for item in unpaired_en[:20]:
    print('  ', item)
