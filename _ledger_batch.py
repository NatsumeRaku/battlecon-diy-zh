# -*- coding: utf-8 -*-
"""挂账批次处理：A2改名/A3废档存证/B8卡类定值"""
import json, os, shutil, sys

ROOT = os.path.dirname(os.path.abspath(__file__))

def load(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f:
        return json.load(f)

def save(p, d):
    with open(os.path.join(ROOT, p), "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)

log = []

# --- A2 改名（文件名+名称字段），乔尔5张对应关系待定不动 ---
renames = [
    ("json-db/en/独立-SLO/Dolores Malephaise/状态效果牌_Dominated.json", "状态效果牌_Dominated Mind.json", "Dominated Mind"),
    ("json-db/en/毁灭篇-DEV/拜伦·克兰/状态效果牌_Feather Speed.json", "状态效果牌_Faceless Shadow.json", "Faceless Shadow"),
    ("json-db/en/毁灭篇-DEV/塞萨尔·格里斯特/状态效果牌_Reydalytic.json", "状态效果牌_Inevitability.json", "Inevitability"),
    ("json-db/en/战争篇-WAR/Cadenza/状态效果牌_Veiling Veil.json", "状态效果牌_Unending Vigil.json", "Unending Vigil"),
    ("json-db/en/毁灭篇扩展-DEX/Borneo/状态效果牌_Mazzaroth's Curse.json", "状态效果牌_Mazzaroth Comes!.json", "Mazzaroth Comes!"),
    ("json-db/en/多人模式/状态效果牌_Lightning Strike.json", "状态效果牌_Lightning Struck.json", "Lightning Struck"),
    ("json-db/en/多人模式/状态效果牌_Ultimate Power.json", "状态效果牌_Illimitable Power.json", "Illimitable Power"),
    ("json-db/en/多人模式/状态效果牌_Ultimate Speed.json", "状态效果牌_Illimitable Speed.json", "Illimitable Speed"),
]
for old, newname, newval in renames:
    d = load(old)
    d["名称"] = newval
    save(old, d)
    new = os.path.join(os.path.dirname(old), newname)
    os.rename(os.path.join(ROOT, old), os.path.join(ROOT, new))
    log.append(f"A2 rename: {old} -> {new}")

# --- A3 卡佳误读批次作废存证 ---
kaja = ["风格_刺蛰.json", "风格_啮咬.json", "风格_掘洞.json", "风格_群涌.json", "专属_虫颚.json"]
kdir = "json-db/zh/毁灭篇-DEV/卡迦·塞蒂·柳"
adir = os.path.join(kdir, "_作废存证-卡佳误读批次")
os.makedirs(os.path.join(ROOT, adir), exist_ok=True)
for f in kaja:
    os.rename(os.path.join(ROOT, kdir, f), os.path.join(ROOT, adir, f))
    log.append(f"A3 作废存证: {kdir}/{f}")
ch = load(os.path.join(kdir, "character.json"))
ch["卡牌清单"] = [x for x in ch["卡牌清单"] if x not in kaja]
save(os.path.join(kdir, "character.json"), ch)
log.append("A3 character.json 卡牌清单已剔除5废档")

# --- B8 卡类零星值 ---
for p in ["json-db/en/命运篇-FAT/通用牌_Switch.json", "json-db/en/试炼篇-TRI/通用牌_Switch.json"]:
    d = load(p)
    assert d["卡类"] == "Force风格", p
    d["卡类"] = "切换牌"
    save(p, d)
    log.append(f"B8: {p} 卡类 Force风格->切换牌")

p = "json-db/zh/待核验/变招.json"
d = load(p)
assert d["卡类"] == "特殊", p
d["卡类"] = "风格"
save(p, d)
log.append("B8: zh/待核验/变招.json 卡类 特殊->风格")

import glob
for p in glob.glob(os.path.join(ROOT, "json-db/en/试炼篇-TRI/Trias/饰品牌_*.json")):
    d = load(p)
    if d["卡类"] == "饰品牌(Embellishment)":
        d["卡类"] = "饰品牌"
        save(p, d)
        rel = os.path.relpath(p, ROOT)
        log.append(f"B8: {rel} 卡类 饰品牌(Embellishment)->饰品牌")

print("\n".join(log))
