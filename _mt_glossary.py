# -*- coding: utf-8 -*-
"""路线1: 机翻草稿术语规范化 v1——对照表确定性替换,产出 校对稿-v1（供人工/终审）"""
import json, io, os, re, glob
from collections import defaultdict

ROOT = r"D:\Arkham Horror PSD\BattleConDB\battlecon-diy-zh"
DRAFT = os.path.join(ROOT, "memory-pending", "mt-draft")
OUT = os.path.join(ROOT, "memory-pending", "mt-draft-v1")
os.makedirs(OUT, exist_ok=True)

# 反向修理映射：MT常见错译 -> 封闭术语（值取自 convention/中英译名对照表.md 行88-110）
FIX = [
    (r'点击\s*:', '命中：'), (r'\b点击\b', '命中'),
    (r'(?<=[:：])?\s*关闭\s*(?=\d)', '逼近 '),
    (r'\b关闭\s*2\b', '逼近 2'),
    (r'\b力量\b|\b电源\b|\b功率\b', '威力'),
    (r'\b优先(?:级|权|使用)?\b(?!\w)', '先攻'),
    (r'\b撤退\b', '后退'),
    (r'前\s*[:：](?=\s*\S)', '前置：'),
    (r'之前\s*[:：]', '前置：'),
    (r'后\s*[:：]', '后置：'),
    (r'\b节奏\b|\b节拍\b|\b这一拍\b', '回合'),
    (r'\b这一击\b', '本次攻击'),
    (r'对手', '对手'),
    (r'反对者|敌方', '对手'),
    (r'\b护甲\b', '韧性'),  # MT常把 Guard/Armor 混;先统一再人工分
    (r'\b眩晕\b', '晕眩'),
    (r'无敌(?:状态)?', '无敌'),
]
NUM = re.compile(r'([+-]?\d+)\s*~?\s*([+-]?\d+)?\s*(威力|先攻|韧性|距离)')

def fix(t):
    for pat, rep in FIX:
        t = re.sub(pat, rep, t)
    return t

bychar = defaultdict(list)
for p in sorted(glob.glob(os.path.join(DRAFT, "*.md"))):
    ch = os.path.basename(p)[:-3]
    txt = io.open(p, encoding="utf-8").read()
    blocks = txt.split("\n## ")[1:]
    for b in blocks:
        lines = b.strip().split("\n")
        head = lines[0]
        en = next((l[4:] for l in lines if l.startswith("EN: ")), "")
        op = next((l[6:] for l in lines if l.startswith("Opus: ")), "")
        ar = next((l[7:] for l in lines if l.startswith("Argos: ")), "")
        v1 = fix(op or ar)
        bychar[ch].append((head, en, v1, op, ar))

for ch, rs in bychar.items():
    lines = [f"# {ch} 校对稿 v1（Opus骨架+对照表术语替换，机翻未经终审，禁直接入库）", ""]
    for head, en, v1, op, ar in rs:
        lines.append(f"## {head}")
        lines.append(f"EN: {en}")
        lines.append(f"v1: {v1}")
        lines.append("")
    io.open(os.path.join(OUT, f"{ch}.md"), "w", encoding="utf-8").write("\n".join(lines))
print("DONE", sum(len(v) for v in bychar.values()))
