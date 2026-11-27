# -*- coding: utf-8 -*-
"""行265: TRI zh 树落库 + 机检闸口。用法: python tri_zh_build.py"""
import json, io, os, re, sys, glob
from tri_zh_translate import (ROOT, EN, ZH, CACHE, ROLE, NAME_EXTRA, all_strings)

CONV = os.path.join(ROOT, 'convention', '中英译名对照表.md')
TP = {'初始设置', '投注', '展示', '开始', '前置', '命中', '伤害', '后置', '结束', '循环',
      '当', '每当', '持续', '击破', '限定投注', '移除', '急涌', '维持', ''}
TAGS = ['b', 'i-sb', 'r-b', 'bl-b', 'g-b', 'p-b', 'o-b', 'i', 'b-i', 'sb', 's']
SELFTAG = ['initiative', 'stun-shield', 'group-attack', 'red-diamond', 'orange-pentagon',
           'yellow-hexagon', 'green-tri-down', 'blue-circle', 'purple-square',
           'star8-alpha', 'star8-beta', 'beta-base', 'ex-base', 'almighty-base',
           'pile-1', 'pile-2', 'face-alpha', 'face-beta', 'gray-bg', 'simsun', 'song']


def norm(s):
    return (s.replace('’', "'").replace('‘', "'").replace('–', '-').replace('—', '-')
            .lower().replace(' ', '').replace("'", ''))


def build_name_map():
    txt = io.open(CONV, encoding='utf-8').read().split('\n')
    m = {}
    for ln in txt:
        if '试炼篇-TRI' not in ln or not ln.startswith('|'):
            continue
        c = [x.strip() for x in ln.strip('|').split('|')]
        if len(c) < 3:
            continue
        en, zh = c[0], c[1]
        if en in ('英文', '') or not en or not zh:
            continue
        if en not in m:
            m[en] = zh
    m.update(NAME_EXTRA)
    return m


def pick(m, name):
    if name in m:
        return m[name]
    n = norm(name)
    for k, v in m.items():
        if norm(k) == n:
            return v
    return None


def norm_zh(s):
    """排版归一：全角标点、数字与汉字间空一格（不动标签与 N/A）"""
    if not s:
        return s
    s = s.replace('(', '（').replace(')', '）')
    s = s.replace(',', '，').replace(';', '；').replace(':', '：')
    s = s.replace('!', '！').replace('?', '？')
    s = re.sub(r'([0-9])([\u4e00-\u9fff])', r'\1 \2', s)
    s = re.sub(r'([\u4e00-\u9fff])([0-9])', r'\1 \2', s)
    s = re.sub(r' {2,}', ' ', s)
    return s


def numseq(s):
    return sorted(re.findall(r'\d+', s))


def tagset(s):
    got = re.findall(r'<([a-z0-9-]+)>', s) + re.findall(r'</([a-z0-9-]+)>', s)
    return sorted(x for x in got)


BLACK = {'避免': '回避', '拉扯': '拉动', '先攻': '速度', '荆棘': '毒刺', '冰霜': '冻霜',
         '幽魂': '魂奴', '标靶': '目标', '承受': '受到', '技击': '攻击', '攻击对手': '攻击',
         '翻面个': '翻面', '一个指示物': '1 枚指示物'}


def check_pair(en, zh):
    """返回问题列表"""
    prob = []
    if numseq(en) != numseq(zh):
        prob.append('数字不保真 en=%s zh=%s' % (numseq(en), numseq(zh)))
    if tagset(en) != tagset(zh):
        prob.append('标签不配对 en=%s zh=%s' % (tagset(en), tagset(zh)))
    # 英文残留
    left = re.findall(r'[A-Za-z][A-Za-z\'’]{1,}', re.sub(r'<[^>]+>', '', zh))
    left = [x for x in left if x not in ('N/A', 'X')]
    if left:
        prob.append('英文残留 %s' % left)
    for bad, good in BLACK.items():
        if bad in zh:
            prob.append('术语误用 %s→%s' % (bad, good))
    for t in TAGS:
        if zh.count('<%s>' % t) != zh.count('</%s>' % t):
            prob.append('标签不成对 <%s>' % t)
    # 句末标点：以原文句末符号为准（台词以引号收尾不查）
    tail = en.rstrip()[-1:]
    want = {'.': '。', '!': '！', '?': '？'}.get(tail)
    if want and not zh.rstrip().endswith(want):
        prob.append('句末标点缺(应%s)' % want)
    return prob


def zh_fname(en_basename, zh_name, card_kind):
    prefix = en_basename.split('_')[0]
    if prefix == 'UA':
        prefix = '特技(UA)'
    return '%s_%s.json' % (prefix, zh_name)


def main():
    cache = json.load(io.open(CACHE, encoding='utf-8'))
    nm = build_name_map()
    report = []
    unmapped = []
    written = 0
    for p in sorted(glob.glob(os.path.join(EN, '*', '*.json'))):
        bn = os.path.basename(p)
        if bn == 'character.json':
            continue
        d = json.load(io.open(p, encoding='utf-8'))
        en_name = d.get('名称', '')
        zh_name = pick(nm, en_name) or pick(nm, en_name.replace('’', "'"))
        if not zh_name:
            unmapped.append((os.path.basename(os.path.dirname(p)), bn, en_name))
            continue
        role_en = d.get('角色', os.path.basename(os.path.dirname(p)))
        role_zh = ROLE.get(role_en) or ROLE.get(os.path.basename(os.path.dirname(p)))
        if not role_zh:
            unmapped.append((os.path.basename(os.path.dirname(p)), bn, '角色:' + role_en))
            continue

        out = {}
        out['角色'] = role_zh
        if '角标' in d:
            out['角标'] = d['角标']
        out['名称'] = zh_name
        out['卡类'] = d['卡类']
        out['系列'] = d['系列']

        eff = []
        eff_src = d.get('效果')
        STR_EFF_ZH = {
            '配件_撕裂·吞噬指示物.json':
                '四枚双面指示物（正面撕裂／背面吞噬）。四枚正面分别为剧痛、勇气、灵魂、英勇，'
                '对应效果依次为［待核：图幅所限底边小字不可辨］、展示：无视护甲、+1 速度、+1 威力。'
                '背面吞噬面的效果文本未见于 UA 卡图，待实卡补录。',
        }
        if isinstance(eff_src, str):
            out['效果'] = STR_EFF_ZH.get(bn, eff_src)
            eff_src = []
        for i, e in enumerate(eff_src or []):
            ne = {}
            ne['时点'] = e.get('时点', '')
            cond_en = e.get('条件', '')
            eff_en = e.get('效果', '')
            k1 = os.path.relpath(p, EN) + '|效果|%d|条件' % i
            k2 = os.path.relpath(p, EN) + '|效果|%d|效果' % i
            ne['条件'] = norm_zh(cache.get(k1, '')) if cond_en else ''
            ne['效果'] = norm_zh(cache.get(k2, ''))
            if e.get('可选'):
                ne['可选'] = e['可选']
            if e.get('背景'):
                ne['背景'] = e['背景']
            for pr in check_pair(cond_en, ne['条件']) + check_pair(eff_en, ne['效果']):
                report.append((os.path.relpath(p, EN), '效果%d' % i, pr))
            if ne['时点'] not in TP:
                report.append((os.path.relpath(p, EN), '效果%d' % i, '时点越界 ' + ne['时点']))
            if ne['时点'] in ('当', '每当') and not ne['条件']:
                report.append((os.path.relpath(p, EN), '效果%d' % i, '当/每当缺条件'))
            eff.append(ne)
        if not isinstance(d.get('效果'), str):
            out['效果'] = eff
        if '数值' in d:
            out['数值'] = d['数值']
        if d.get('台词'):
            k = os.path.relpath(p, EN) + '|台词'
            out['台词'] = norm_zh(cache.get(k, ''))
            for pr in check_pair(d['台词'], out['台词']):
                report.append((os.path.relpath(p, EN), '台词', pr))
        if d.get('机制概述'):
            k = os.path.relpath(p, EN) + '|机制概述'
            out['机制概述'] = norm_zh(cache.get(k, ''))
        out['备注'] = ('行265初译;英文原卡:%s;行202/203/204考据拟译[待核],无官方先例,官方文本可覆写'
                       % en_name)
        out['来源'] = d['来源']

        zp = os.path.join(ZH, os.path.basename(os.path.dirname(p)), zh_fname(bn, zh_name, d['卡类']))
        os.makedirs(os.path.dirname(zp), exist_ok=True)
        with io.open(zp, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(out, f, ensure_ascii=False, indent=1)
        written += 1

    print('写出', written, '档；未映射', len(unmapped))
    for u in unmapped:
        print('  未映射', u)
    print('机检问题', len(report))
    for r in report[:80]:
        print('  ', r[0], r[1], r[2])
    io.open(os.path.join(ROOT, 'memory-pending', 'tri_zh_report.txt'), 'w', encoding='utf-8').write(
        '\n'.join('%s %s %s' % r for r in report))


if __name__ == '__main__':
    main()
