# -*- coding: utf-8 -*-
"""状态牌立绘聚类：d43 c10-c29 / d51 c10-c25 卡面感知哈希 + 互相比对
输出 paddle-independent: portrait_clusters.json"""
import json, os
from PIL import Image

BASE = r"D:\Arkham Horror PSD\BattleConDB\battlecon-diy-zh\memory-pending\tts-img"

def ahash(im, size=16):
    g = im.convert("L").resize((size, size))
    px = list(g.getdata())
    avg = sum(px) / len(px)
    return "".join("1" if p > avg else "0" for p in px)

def hamming(a, b):
    return sum(c1 != c2 for c1, c2 in zip(a, b))

cards = {}
for key, lo, hi in [("f22", 10, 30), ("f33", 10, 26)]:
    im = Image.open(os.path.join(BASE, "full", key + ".jpg"))
    W, H = im.size
    cw, chh = W // 10, H // 7
    for n in range(lo, hi):
        rr, cc = divmod(n, 10)
        cell = im.crop((cc*cw, rr*chh, (cc+1)*cw, (rr+1)*chh))
        art = cell.crop((int(cw*0.08), int(chh*0.18), int(cw*0.92), int(chh*0.75)))
        cards[f"{key}#c{n}"] = ahash(art)

keys = sorted(cards)
sim = {}
for i, a in enumerate(keys):
    for b in keys[i+1:]:
        d = hamming(cards[a], cards[b])
        if d <= 28:  # 相似阈值
            sim[f"{a}~{b}"] = d
json.dump(sim, open(os.path.join(BASE, "portrait_clusters.json"), "w"), indent=1)
print("pairs:", len(sim))
for k, v in sorted(sim.items(), key=lambda x: x[1])[:40]:
    print(v, k)
