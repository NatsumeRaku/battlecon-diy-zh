# -*- coding: utf-8 -*-
"""行265: TRI zh 树批量初译（本地 Qwen2.5-7B 出稿 + 机检闸口）

流程: en 树逐档 -> 逐条字符串送本地模型 -> 落到 cache -> 机检 -> 写 zh 树
用法: python tri_zh_translate.py draft     # 出稿(可断点续跑)
      python tri_zh_translate.py build     # 机检+写库
"""
import json, io, os, re, sys, glob, urllib.request, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EN = os.path.join(ROOT, 'json-db', 'en', '试炼篇-TRI')
ZH = os.path.join(ROOT, 'json-db', 'zh', '试炼篇-TRI')
CACHE = os.path.join(ROOT, 'memory-pending', 'tri_zh_cache.json')
API = "http://127.0.0.1:8099/v1/chat/completions"

# ---------- 角色中文名（对照表行511-520） ----------
ROLE = {
    "Amon Elcela": "阿蒙·埃尔塞拉", "Burgundy XII": "勃艮第十二世",
    "Cindra Flama": "辛德拉·弗拉马", "Dareios Kuel": "达雷俄斯·库尔",
    "Dravil Coldwater": "德拉维尔·寒水", "Hayden Morgan": "海登·摩根",
    "Kimbhe": "金碧", "Uleyla Kimbhe": "金碧",
    "Lucida Malephaise": "露西达·玛勒菲斯", "Trias Blackwind": "特里亚斯·黑风",
    "Wardlaw O'Brien": "沃德劳·奥布莱恩", "Wardlaw": "沃德劳·奥布莱恩",
    "Dravil": "德拉维尔·寒水", "Hayden": "海登·摩根", "Amon": "阿蒙·埃尔塞拉",
    "Burgundy": "勃艮第十二世", "Cindra": "辛德拉·弗拉马", "Dareios": "达雷俄斯·库尔",
    "Trias": "特里亚斯·黑风",
}

# ---------- 卡名（对照表考据节；UA/配件为本行补登记） ----------
NAME_EXTRA = {
    "DAMAGE CONTROL": "损害管制", "EBBING TIDE": "退潮", "BREAKING POINT": "临界点",
    "ARCHMAGE’S STAFF": "大法师之杖", "JAWS OF MALEPHAISE": "玛勒菲斯之颚",
    "EMBELLISH": "饰彩", "COLOR BURN": "色彩灼烧", "REBIRTH": "重生",
    "DIPSOMANIA": "酗酒癖",
    "冰": "冰", "蒸汽": "蒸汽", "狂怒·控制计数物": "狂怒·控制计数物",
    "法杖": "法杖", "撕裂·吞噬指示物": "撕裂·吞噬指示物", "颜料": "颜料",
}

SYS = """你是《战链：因甸斯的毁灭》卡文英译中专家。输入是一组英文卡文句子，逐条译成中文，按同样的编号输出，每条一行，不要解释、不要空行、不要加编号以外的符号。

铁律：
1. 逐字落实，不增删、不改写句式。数字必须与原文完全一致（X、0-3、1~3、5+ 一律照抄，一个都不许改）。
2. 尖括号标签原样保留：<b>..</b> <i-sb>..</i-sb> <r-b>..</r-b> <bl-b>..</bl-b> <g-b>..</g-b> <p-b>..</p-b> <o-b>..</o-b> <i>..</i> <initiative> <stun-shield> <group-attack> <red-diamond> <orange-pentagon> <yellow-hexagon> <green-tri-down> <blue-circle> <purple-square>。标签内文字翻译，标签本身不动。
3. 修正值逆序归一：+2 Power→<i-sb>+2 威力</i-sb>；-1 Priority→<i-sb>-1 速度</i-sb>；+1~3 Range→<i-sb>+1~3 距离</i-sb>。护甲/削命连数字入<b>：Armor 3→<b>护甲 3</b>；Chip 2→<b>削命 2</b>。
4. 数字与汉字相连处空一格（"拥有 3 冻霜"），与标点相连不空。
5. 标点全用全角：，。：；！？（）「」；句末必须有句号。

术语（必须照用，禁同义替换）：
Power=威力 Priority=速度 Guard=韧性 Range=距离 Armor=护甲 Life=生命 Force=能量 Chip=削命
Advance=前进 Retreat=后退 Push=推动 Pull=拉动 Close=逼近 Teleport=瞬移
Opponent=对手 fighter=斗士 attack=攻击 Attack Pair=攻击对 beat=回合 duel=决斗
Reveal=展示 Start=开始 Before=前置 Hit=命中 Damage=伤害 After=后置 End=结束 Recycle=循环 Setup=初始设置
Limited Ante=限定投注 Ante=投注 Optional=可选 Choose One=选择一项
Style=风格 Base=招式 Stance=架势 Stun Immunity=眩晕免疫 Ignore Armor=无视护甲 Ignore Guard=无视韧性 Vulnerable=易伤
gain=获得 spend=支付 deplete=消耗 use=使用 remove=移除 regain=回收 trash=弃置 place=放置
discard=弃置 Discard Pile 1/2=弃牌堆 1/2 supply=供给区 hand=手牌 space=格
adjacent to=与…相邻 edge of the arena=场地边缘 center of the board=场地中央
this beat=本回合 next beat=下回合 as far as possible=尽可能 per=每
marker=标记 counter=计数物 token=指示物 become=变为 activate=激活 flip=翻面 double-sided=双面
Beginning=起首 Ending=收尾 Embellishment=饰品牌
Fury=狂怒 Control=控制 Staff=法杖 Paint=颜料 Rend=撕裂 Consume=吞噬 Ice=冰 Steam=蒸汽
Human=人类 Phoenix=凤凰 Danger Level=危险等级
Code White=白色代码 Code Green=绿色代码 Code Yellow=黄色代码 Code Red=红色代码 Code Black=黑色代码
Drink=饮品 active=激活的 inactive=未激活的 injured=受伤的
prophecy=预言 age=年龄 counter=计数物
"""


def tr_batch(items):
    """items: list[str] -> list[str]"""
    body_in = "\n".join("%d. %s" % (i + 1, s) for i, s in enumerate(items))
    msgs = [{"role": "system", "content": SYS},
            {"role": "user", "content": body_in}]
    body = json.dumps({"messages": msgs, "temperature": 0.0,
                       "max_tokens": 256 * len(items) + 128}).encode()
    req = urllib.request.Request(API, body, {"Content-Type": "application/json"})
    for attempt in range(3):
        try:
            r = json.load(urllib.request.urlopen(req, timeout=600))
            txt = r["choices"][0]["message"]["content"].strip()
            out = {}
            for ln in txt.split("\n"):
                m = re.match(r"^\s*(\d+)[.、)]\s*(.+)$", ln)
                if m:
                    out[int(m.group(1))] = m.group(2).strip()
            res = [out.get(i + 1) for i in range(len(items))]
            if all(res):
                return res
        except Exception as ex:
            print('  retry', ex)
            time.sleep(2)
    return [None] * len(items)


def all_strings(d):
    """返回该档所有待译字符串的 (路径, 原文)"""
    out = []
    eff = d.get('效果')
    if isinstance(eff, str):
        return out
    for i, e in enumerate(eff or []):
        if e.get('条件'):
            out.append((('效果', i, '条件'), e['条件']))
        if e.get('效果'):
            out.append((('效果', i, '效果'), e['效果']))
    if d.get('台词'):
        out.append((('台词',), d['台词']))
    if d.get('机制概述'):
        out.append((('机制概述',), d['机制概述']))
    return out


def load_cache():
    if os.path.exists(CACHE):
        return json.load(io.open(CACHE, encoding='utf-8'))
    return {}


def save_cache(c):
    json.dump(c, io.open(CACHE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


def en_files():
    res = []
    for p in sorted(glob.glob(os.path.join(EN, '*', '*.json'))):
        if os.path.basename(p) == 'character.json':
            continue
        res.append(p)
    return res


def draft():
    cache = load_cache()
    todo = []
    for p in en_files():
        d = json.load(io.open(p, encoding='utf-8'))
        for key, s in all_strings(d):
            k = os.path.relpath(p, EN) + '|' + '|'.join(str(x) for x in key)
            if k not in cache or not cache[k]:
                todo.append((k, s))
    print('待译', len(todo), '已缓存', len(cache))
    B = 8
    for i in range(0, len(todo), B):
        chunk = todo[i:i + B]
        res = tr_batch([s for _, s in chunk])
        for (k, s), r in zip(chunk, res):
            if r:
                cache[k] = r
        save_cache(cache)
        print('  %d/%d' % (i + len(chunk), len(todo)), flush=True)
    miss = [k for k, s in todo if not cache.get(k)]
    print('未译出', len(miss))
    for k in miss[:10]:
        print('  ', k)


if __name__ == '__main__':
    if sys.argv[1] == 'draft':
        draft()
