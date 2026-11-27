# -*- coding: utf-8 -*-
"""本地 7B 翻译探针: 试译 Amon 四档, 人工判质量后再决定是否批量。"""
import json, io, os, urllib.request

MODEL = "http://127.0.0.1:8099/v1/chat/completions"
BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    'json-db', 'en', '试炼篇-TRI')

SYS = """你是《战链：因甸斯的毁灭》卡文英译中专家。只输出译文 JSON，不解释。

铁律：
1. 逐字落实，不增删、不改写句式；数字必须与原文完全一致（含 X、0-3、1~3、5+ 等），一个数字都不许改。
2. 保留所有尖括号标签原样：<b>..</b> <i-sb>..</i-sb> <r-b>..</r-b> <bl-b>..</bl-b> <g-b>..</g-b> <p-b>..</p-b> <o-b>..</o-b> <i>..</i> <initiative> <stun-shield> <group-attack> <red-diamond> <orange-pentagon> <yellow-hexagon> <green-tri-down> <blue-circle> <purple-square>；标签内文字翻译，标签本身不译、不改、不增删空格结构。
3. 修正值逆序归一：+2 Power→`<i-sb>+2 威力</i-sb>`；-1 Priority→`<i-sb>-1 速度</i-sb>`；+1~3 Range→`<i-sb>+1~3 距离</i-sb>`。护甲/削命连数字入<b>：Armor 3→`<b>护甲 3</b>`，Chip 2→`<b>削命 2</b>`。
4. 数字与汉字相连处空一格（"拥有 3 冻霜"、"推动 0-3"），与标点相连不空。
5. 标点全用全角：，。：；！？（）「」；句末句号必须有。

术语表（必须照用，禁止同义替换）：
Power=威力 Priority=速度 Guard=韧性 Range=距离 Armor=护甲 Life=生命 Force=能量 Chip=削命
Advance=前进 Retreat=后退 Push=推动 Pull=拉动 Close=逼近 Teleport=瞬移
Opponent=对手 fighter=斗士 attack=攻击 Attack Pair=攻击对 beat=回合 duel=决斗
Reveal=展示 Start=开始 Before=前置 Hit=命中 Damage=伤害 After=后置 End=结束 Recycle=循环 Setup=初始设置
Limited Ante=限定投注 Ante=投注 Optional=可选 Choose One=选择一项
Style=风格 Base=招式 Unique Base=专属招式 Stance=架势
Stun Immunity=眩晕免疫 Ignore Armor=无视护甲 Ignore Guard=无视韧性 Vulnerable=易伤
gain=获得 spend=支付 deplete=消耗 use=使用 remove=移除 regain=回收 trash=弃置 place=放置
discard=弃置 Discard Pile 1/2=弃牌堆 1/2 supply=供给区 hand=手牌
space=格 adjacent to=与…相邻 edge of the arena=场地边缘 center of the board=场地中央
this beat=本回合 next beat=下回合 as far as possible=尽可能 per=每
marker=标记 counter=计数物 token=指示物
become=变为 activate=激活 flip=翻面 double-sided=双面
Beginning=起首 Ending=收尾 Embellishment=饰品牌
Fury=狂怒 Control=控制 Staff=法杖 Paint=颜料 Rend=撕裂 Consume=吞噬
Ice=冰 Steam=蒸汽 Human=人类 Phoenix=凤凰
Danger Level=危险等级 Code White=白色警戒 Code Green=绿色警戒 Code Yellow=黄色警戒 Code Red=红色警戒
Drink=饮品 active=激活的 inactive=未激活的
life becomes 10=生命变为 10
"""

FEWSHOT = [
    ("<b>Armor 3</b>", "<b>护甲 3</b>"),
    ("<r-b>Hit:</r-b> The Opponent gains <i-sb>Stun Immunity</i-sb>.",
     "<r-b>命中：</r-b>对手获得<i-sb>眩晕免疫</i-sb>。"),
    ("<bl-b>After:</bl-b> Lose all Armor.", "<bl-b>后置：</bl-b>失去全部护甲。"),
    ("<g-b>End, Optional:</g-b> Advance or Retreat 1.", "<g-b>结束，可选：</g-b>前进或后退 1。"),
    ("If the Opponent would Advance 2 or more spaces, instead they Advance 1.",
     "若对手将要前进 2 格或更多，改为前进 1 格。"),
]


def tr(s):
    msgs = [{"role": "system", "content": SYS}]
    for en, zh in FEWSHOT:
        msgs.append({"role": "user", "content": en})
        msgs.append({"role": "assistant", "content": zh})
    msgs.append({"role": "user", "content": s})
    body = json.dumps({"messages": msgs, "temperature": 0.0, "max_tokens": 512}).encode()
    req = urllib.request.Request(MODEL, body, {"Content-Type": "application/json"})
    r = json.load(urllib.request.urlopen(req, timeout=180))
    return r["choices"][0]["message"]["content"].strip()


if __name__ == "__main__":
    for f in ["Amon/基底_Impenetrable.json", "Amon/风格_Containment.json",
              "Amon/终结技_Wall.json", "Amon/形态牌_Code White.json"]:
        d = json.load(io.open(os.path.join(BASE, f), encoding='utf-8'))
        print('###', f)
        for e in d.get('效果') or []:
            en = e.get('效果', '')
            print(' EN:', en)
            print(' ZH:', tr(en))
        print()
