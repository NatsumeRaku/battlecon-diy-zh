# -*- coding: utf-8 -*-
"""Wave-A 结构残留修复（--apply 落盘，自动备份）
① 8 个 WAN UA 效果字符串列表 -> 标准条目（时点1:1取en，效果原文零改动）
② 16 处 时点='<b>' -> '持续'（被动/持续类语义，风格同 持续 惯例）
③ Anva 残留目录 -> _旧版待核 归档
"""
import json, glob, os, re, shutil, sys

BASE = os.path.dirname(os.path.abspath(__file__))
if BASE.endswith('memory-pending'):
    BASE = os.path.dirname(BASE)
APPLY = '--apply' in sys.argv
BK = os.path.join(os.path.dirname(BASE), 'backup', 'pre-waveA-2026-11-28')
changes = []

def load(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)

def save_detect(p, d):
    """保留原缩进宽度与换行风格"""
    raw = open(p, 'rb').read()
    m = re.search(rb'\n(\s*)"', raw[:300])
    indent = len(m.group(1)) if m else 1
    nl = '\r\n' if b'\r\n' in raw[:500] else '\n'
    s = json.dumps(d, indent=indent, ensure_ascii=False)
    if nl == '\n':
        s = s.replace('\r\n', '\n')
    else:
        s = s.replace('\n', '\r\n')
    data = s.encode('utf-8')
    if raw.endswith(b'\n') or raw.endswith(b'\r\n'):
        if not data.endswith(nl.encode('utf-8')):
            data += nl.encode('utf-8')
    with open(p, 'wb') as f:
        f.write(data)

def backup(p):
    rel = p.replace('\\', '/').split('battlecon-diy-zh/')[-1]
    dst = os.path.join(BK, rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(p, dst)

# ---------- ① UA 字符串列表包裹 ----------
UAS = [
    ('json-db/zh/流浪者篇-WAN/凛/特技(UA)_冻伤[待核].json', 'json-db/en/流浪者篇-WAN/Rin/特技(UA)_FROSTBITE.json'),
    ('json-db/zh/流浪者篇-WAN/凯/特技(UA)_迷局魔盒[待核].json', 'json-db/en/流浪者篇-WAN/Kai/特技(UA)_PUZZLING BOX.json'),
    ('json-db/zh/流浪者篇-WAN/希尔纳奥/特技(UA)_一生驰骋[待核].json', 'json-db/en/流浪者篇-WAN/Cionaodh/特技(UA)_RIDE OF A LIFETIME.json'),
    ('json-db/zh/流浪者篇-WAN/温蒂/特技(UA)_空中支援[待核].json', 'json-db/en/流浪者篇-WAN/Wendy/特技(UA)_AIR SUPPORT.json'),
    ('json-db/zh/流浪者篇-WAN/科拉/特技(UA)_荒漠之拥[待核].json', 'json-db/en/流浪者篇-WAN/Kora/特技(UA)_DESERT\'S EMBRACE.json'),
    ('json-db/zh/流浪者篇-WAN/约翰/特技(UA)_玛里亚尼之咒[待核].json', 'json-db/en/流浪者篇-WAN/John/特技(UA)_MARRIJANI CURSE.json'),
    ('json-db/zh/流浪者篇-WAN/维凯尔/特技(UA)_永世奴役[待核].json', 'json-db/en/流浪者篇-WAN/Vekyl/特技(UA)_ETERNAL SERVITUDE.json'),
    ('json-db/zh/流浪者篇-WAN/菲拉娜/特技(UA)_约束限制器[待核].json', 'json-db/en/流浪者篇-WAN/Feylana/特技(UA)_REGULATION LIMITER.json'),
]
for zp, ep in UAS:
    zd, ed = load(zp), load(ep)
    eff = zd.get('效果')
    if not isinstance(eff, list) or not any(isinstance(x, str) for x in eff):
        print(f'[跳过] {zp} 无字符串条目')
        continue
    en_eff = ed.get('效果') or []
    new = []
    n_wrap = 0
    for i, s in enumerate(eff):
        if isinstance(s, str):
            tp = en_eff[i].get('时点', '') if i < len(en_eff) and isinstance(en_eff[i], dict) else ''
            if not isinstance(tp, str):
                tp = ''
            new.append({'时点': tp, '条件': '', '效果': s})
            n_wrap += 1
        else:
            new.append(s)
    zd['效果'] = new
    if APPLY:
        backup(zp)
        save_detect(zp, zd)
    changes.append(f"[UA包裹] {zp} {n_wrap}条 str->dict (时点取en)")

# ---------- ② 时点 '<b>' -> '持续' ----------
for tree in ('zh', 'en'):
    for p in glob.glob(f'json-db/{tree}/**/*.json', recursive=True):
        if p.endswith('character.json') or '_旧版待核' in p:
            continue
        d = load(p)
        hit = False
        for e in d.get('效果') or []:
            if isinstance(e, dict) and re.fullmatch(r'<[a-z]+>', str(e.get('时点', ''))):
                old = e['时点']
                e['时点'] = '持续'
                hit = True
                changes.append(f"[时点修复] {p} {old!r}->'持续'")
        if hit and APPLY:
            backup(p)
            save_detect(p, d)

# ---------- ③ Anva 归档 ----------
anva = 'json-db/en/流浪者篇-WAN/Anva'
if os.path.isdir(anva):
    dst = 'json-db/en/流浪者篇-WAN/_旧版待核/Anva'
    if APPLY:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.move(anva, dst)
    changes.append(f"[归档] {anva} -> {dst}")

print(f'变更点 {len(changes)} | APPLY={APPLY}')
for c in changes:
    print(' ', c)
if APPLY:
    print(f'备份 -> {BK}')
