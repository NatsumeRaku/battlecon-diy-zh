# -*- coding: utf-8 -*-
"""行265: 机检不合格条目定点返修（本地模型，逐条重译+闸口复核）"""
import json, io, os, re, sys, glob
from tri_zh_translate import ROOT, EN, CACHE, SYS
from tri_zh_build import check_pair, numseq, tagset
import tri_zh_translate as T

REPAIR_RULES = """上一次译文不合格。请重译这一条，逐项满足：
1. 原文里每一个尖括号标签必须在译文中原样出现，标签种类与个数完全一致，不许增、不许减、不许换种类。
2. 标签内的英文也必须译成中文：Setup→初始设置，Recycle→循环，End→结束，Hit→命中，Reveal→展示，Before→前置，After→后置，Limited Ante→限定投注，Optional→可选，Lvl→等级。
3. 数字一个都不许多、不许少、不许改。原文以句号结尾时译文必须以「。」结尾。
4. 术语照表：Pull=拉动，avoid attacks=回避…的攻击，Opponent=对手，Power=威力，Priority=速度。
只输出译文一行，不要解释。
"""


def one(en, hint):
    msgs = [{"role": "system", "content": SYS},
            {"role": "user", "content": REPAIR_RULES + "\n原文：" + en + "\n问题：" + hint}]
    body = json.dumps({"messages": msgs, "temperature": 0.0, "max_tokens": 600}).encode()
    import urllib.request
    req = urllib.request.Request(T.API, body, {"Content-Type": "application/json"})
    r = json.load(urllib.request.urlopen(req, timeout=300))
    return r["choices"][0]["message"]["content"].strip().split('\n')[0].strip()


def main():
    cache = json.load(io.open(CACHE, encoding='utf-8'))
    # 重建 en 原文索引
    idx = {}
    for p in sorted(glob.glob(os.path.join(EN, '*', '*.json'))):
        if os.path.basename(p) == 'character.json':
            continue
        d = json.load(io.open(p, encoding='utf-8'))
        rel = os.path.relpath(p, EN)
        eff = d.get('效果')
        if isinstance(eff, str):
            continue
        for i, e in enumerate(eff or []):
            if e.get('条件'):
                idx[rel + '|效果|%d|条件' % i] = ('cond', e['条件'])
            idx[rel + '|效果|%d|效果' % i] = ('eff', e['效果'])
        if d.get('台词'):
            idx[rel + '|台词'] = ('line', d['台词'])

    fixed = todo = 0
    for k, (kind, en) in idx.items():
        cur = cache.get(k, '')
        if kind == 'line':
            # 台词：仅查引号内是否残留英文
            left = [x for x in re.findall(r'[A-Za-z]{2,}', re.sub(r'<[^>]+>', '', cur))
                    if x not in ('N/A', 'X')]
            probs = ['英文残留 %s' % left] if left else []
        else:
            probs = check_pair(en, cur)
        if not probs:
            continue
        todo += 1
        ok = False
        for attempt in range(3):
            try:
                new = one(en, '；'.join(probs))
            except Exception as ex:
                print('  err', ex); continue
            if kind == 'line':
                left = [x for x in re.findall(r'[A-Za-z]{2,}', re.sub(r'<[^>]+>', '', new))]
                p2 = ['英文残留 %s' % left] if left else []
            else:
                p2 = check_pair(en, new)
            if not p2:
                cache[k] = new
                fixed += 1
                ok = True
                break
            probs = p2
        if not ok:
            print(' 未修好', k, '|', probs, '|', cur[:60])
    json.dump(cache, io.open(CACHE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('返修条数', fixed, '/', todo)


if __name__ == '__main__':
    main()
