# -*- coding: utf-8 -*-
"""行293 非DEV全文质量审校·机械修复
用法: python memory-pending/fix_qc293.py          # dry-run 只报不写
      python memory-pending/fix_qc293.py --apply  # 备份后写盘
修复项（均为结构/存储层，效果文本零改动）:
  T 时点字段对齐文本触发词（当/每当；仅动 当/每当/空 字段槽位）
  A ▲→<initiative>（数值全库 + 非冻结系列文本；备注与DEV冻结文本不动）
  F 数值格式: 0+/Q+/O+→+0、O+4→+0~4、小写x→X
  S 修正值补符号（风格/架势裸数字→带符号）
  I 绝对值 str→int（专属/终结技/双面终结技/独有/通用/招式 纯数字）
  K 八字段补键（角标/数值；配件跳过；优先镜像en）
"""
import json, glob, os, re, shutil, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPLY = '--apply' in sys.argv
BK = r'D:/Arkham Horror PSD/BattleConDB/backup/pre-qc293-2026-11-28'

SKIP_MARKERS = ('_旧版待核', '_作废存证', '/backup/', '\\backup\\')
ABS_KALEI = {'专属招式', '终结技', '终结技(双面)', '独有招式', '通用招式', '招式'}
MOD_KALEI = {'风格', '架势'}
TAG = re.compile(r'<[^>]+>')

# 时点修复额外项：zh文本无触发前缀、由en首词定夺（审计清单已核对）
EXTRA_TIMING = [
    # (相对 json-db/zh 的路径, 条目序号, 新时点, 依据)
    ('独立-SLO/多洛蕾丝·玛勒菲斯/专属招式_倒刺.json', 0, '当', 'en: When the Opponent is Pushed or Pulled'),
    ('独立-SLO/多洛蕾丝·玛勒菲斯/专属招式_倒刺.json', 1, '当', 'en: When the Opponent Advances or Retreats'),
]

changes = []


def log(path, kind, detail):
    changes.append((path, kind, detail))


def load(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def detect_fmt(p):
    """保留原文件格式：缩进宽度/换行风格/末尾换行"""
    with open(p, 'rb') as f:
        raw = f.read()
    indent = 1
    m = re.search(rb'\n(\s+)"', raw[:500])
    if m:
        ws = m.group(1)
        indent = len(ws) if b'\t' not in ws else 1
    crlf = b'\r\n' in raw
    trailing_nl = raw.endswith(b'\n')
    return indent, crlf, trailing_nl


def save(p, d, fmt):
    indent, crlf, trailing_nl = fmt
    s = json.dumps(d, indent=indent, ensure_ascii=False)
    data = s.encode('utf-8')
    if crlf:
        data = data.replace(b'\n', b'\r\n')
    if trailing_nl:
        data += b'\r\n' if crlf else b'\n'
    with open(p, 'wb') as f:
        f.write(data)


def skip_path(p):
    return any(m in p for m in SKIP_MARKERS)


def strip_tags(s):
    return TAG.sub('', str(s or '')).strip()


def zh_trigger(txt):
    t = strip_tags(txt)
    if t.startswith('每当'):
        return '每当'
    if t.startswith('当') and not t.startswith('当前'):
        return '当'
    return None


def entries_of(eff):
    """展开效果区为 [(obj,)]，保持 dict 引用以便原地改"""
    out = []
    if isinstance(eff, list):
        for e in eff:
            if isinstance(e, dict):
                out.append(e)
    elif isinstance(eff, dict):
        for s in ('α面', 'β面'):
            for e in (eff.get(s) or []):
                if isinstance(e, dict):
                    out.append(e)
    return out


# ---------- 枚举目标 ----------
cards = []  # (tree, relpath, data)
for tree in ('zh', 'en'):
    for p in glob.glob(os.path.join(BASE, 'json-db', tree, '**', '*.json'), recursive=True):
        rp = p.replace('\\', '/')
        if rp.endswith('character.json') or skip_path(rp):
            continue
        d = load(p)
        if d.get('系列', '') == '毁灭篇-DEV':
            continue
        cards.append((tree, rp, d))

# en 名称索引（补键镜像用）
en_by_name = {}
for tree, rp, d in cards:
    if tree == 'en':
        nm = str(d.get('名称', ''))
        if isinstance(nm, str) and nm:
            en_by_name.setdefault(nm.lower(), []).append((rp, d))


def find_en_mirror(rel_rp, d):
    note = str(d.get('备注', ''))
    m = re.search(r'英文(?:原卡|原名)?[=：:]\s*([^;；,，。\n]+)', note)
    if m:
        nm = m.group(1).strip().rstrip('"').strip().lower()
        for rp, ed in en_by_name.get(nm, []):
            if ed.get('卡类') == d.get('卡类'):
                return rp, ed
    return None, None


def walk_num(o, fn, rp, path=''):
    """递归改数值叶子，fn(str)->(new, kind)"""
    if isinstance(o, dict):
        for k in list(o.keys()):
            v = o[k]
            if isinstance(v, (dict, list)):
                walk_num(v, fn, rp, f'{path}{k}.')
            elif isinstance(v, str):
                nv, kind = fn(v)
                if nv != v:
                    log(rp, kind, f'{path}{k}: {v!r}->{nv!r}')
                    o[k] = nv
    elif isinstance(o, list):
        for i, v in enumerate(o):
            if isinstance(v, (dict, list)):
                walk_num(v, fn, rp, f'{path}[{i}].')
            elif isinstance(v, str):
                nv, kind = fn(v)
                if nv != v:
                    log(rp, kind, f'{path}[{i}]: {v!r}->{nv!r}')
                    o[i] = nv


for tree, rp, d in cards:
    kl = str(d.get('卡类', ''))

    # ---------- T 时点 ----------
    eff = d.get('效果')
    for i, e in enumerate(entries_of(eff)):
        cur = str(e.get('时点', ''))
        if cur not in ('当', '每当', ''):
            continue
        exp = zh_trigger(e.get('效果')) or zh_trigger(e.get('条件'))
        if exp and exp != cur:
            e['时点'] = exp
            log(rp, 'T', f'[{i}] {cur!r}->{exp!r} :: {strip_tags(e.get("效果"))[:40]}')
    if tree == 'zh':
        rel = rp.split('/json-db/zh/')[-1]
        for e_rel, idx, val, why in EXTRA_TIMING:
            if rel == e_rel:
                ents = entries_of(d.get('效果'))
                if idx < len(ents):
                    cur = str(ents[idx].get('时点', ''))
                    if cur in ('当', '每当', '') and cur != val:
                        ents[idx]['时点'] = val
                        log(rp, 'T', f'[{idx}] {cur!r}->{val!r} :: {why}')

    # ---------- A ▲ ----------
    def fix_tri(o, field):
        if isinstance(o, dict):
            for k, v in list(o.items()):
                if isinstance(v, (dict, list)):
                    fix_tri(v, field)
                elif isinstance(v, str) and '▲' in v:
                    o[k] = v.replace('▲', '<initiative>')
                    log(rp, 'A', f'{field}.{k}: {v!r}->{o[k]!r}')
        elif isinstance(o, list):
            for i2, v in enumerate(o):
                if isinstance(v, (dict, list)):
                    fix_tri(v, field)
                elif isinstance(v, str) and '▲' in v:
                    o[i2] = v.replace('▲', '<initiative>')
                    log(rp, 'A', f'{field}[{i2}]: ▲→<initiative>')
    fix_tri(d.get('数值'), '数值')
    # 文本侧：仅非冻结系列（WAR/DEV/BCO/通用招式/首领 冻结——WAR 本轮文本无▲）
    if kl != '配件' and not str(d.get('系列', '')).startswith(('战争篇', '毁灭篇')):
        for fld in ('效果', '条件', '机制概述'):
            o = d.get(fld)
            if isinstance(o, (dict, list)):
                fix_tri(o, fld)
            elif isinstance(o, str) and '▲' in o:
                d[fld] = o.replace('▲', '<initiative>')
                log(rp, 'A', f'{fld}: ▲→<initiative>')

    # ---------- F 格式 + I int + S 符号 ----------
    def fix_val(v):
        if not isinstance(v, str):
            return v, 'num'
        s = v.strip()
        rep = {'0+': '+0', 'Q+': '+0', 'q+': '+0', 'O+': '+0', 'o+': '+0',
               'O+4': '+0~4', 'o+4': '+0~4', 'Q+4': '+0~4', '0+4': '+0~4',
               'x': 'X'}
        if s in rep:
            return rep[s], 'F'
        if kl in MOD_KALEI and re.fullmatch(r'\d+', s):
            return '+' + s, 'S'
        if kl in ABS_KALEI and re.fullmatch(r'\d+', s):
            if str(int(s)) == s:
                return int(s), 'I'
        return v, 'num'

    if isinstance(d.get('数值'), (dict, str)):
        walk_num(d['数值'], fix_val, rp, '数值.')

    # ---------- K 补键 ----------
    if kl != '配件' and '角标' not in d:
        rp_en, ed = find_en_mirror(rp, d)
        if ed is not None and '角标' in ed:
            d['角标'] = ed['角标']
            log(rp, 'K', f'角标←en镜像 {ed["角标"]!r}')
        else:
            nm = d.get('名称')
            if isinstance(nm, dict) and 'α面' in nm:
                if kl == '终结技(双面)':
                    # 40档先例：双面终结技角标=八芒星对（终结技固有印刷标记）
                    d['角标'] = {'α面': '<star8-alpha>', 'β面': '<star8-beta>'}
                else:
                    a = d.get('α面')
                    b = d.get('β面')
                    d['角标'] = {'α面': a if isinstance(a, str) and a.startswith('<') else '',
                                 'β面': b if isinstance(b, str) and b.startswith('<') else ''}
            else:
                d['角标'] = ''
            log(rp, 'K', f'角标补默认 {d["角标"]!r}')
    if kl != '配件' and '数值' not in d:
        rp_en, ed = find_en_mirror(rp, d)
        if ed is not None and '数值' in ed:
            d['数值'] = json.loads(json.dumps(ed['数值'], ensure_ascii=False))
            log(rp, 'K', f'数值←en镜像 {json.dumps(d["数值"], ensure_ascii=False)[:60]}')
        elif kl == '特技(UA)':
            d['数值'] = {'距离': 'N/A', '威力': 'N/A', '速度': 'N/A', '韧性': 'N/A'}
            log(rp, 'K', '数值补N/A四栏(UA惯例)')
        else:
            d['数值'] = {}
            log(rp, 'K', '数值补空dict')

# ---------- 输出 ----------
if APPLY:
    os.makedirs(BK, exist_ok=True)
    touched = sorted({c[0] for c in changes})
    for f in touched:
        src = f  # 已是绝对路径
        rel = f.replace('\\', '/').split('/json-db/')[-1]  # zh/... 或 en/...
        dst = os.path.join(BK, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
    for tree, rp, d in cards:
        if any(c[0] == rp for c in changes):
            save(rp, d, detect_fmt(rp))
    print(f'已备份 {len(touched)} 个原文件 -> {BK}')

print(f'变更文件数: {len({c[0] for c in changes})}  变更点: {len(changes)}')
from collections import Counter
cnt = Counter(c[1] for c in changes)
print('分类计数:', dict(cnt))
for rp, kind, detail in changes:
    print(f'  [{kind}] {rp} :: {detail}')
