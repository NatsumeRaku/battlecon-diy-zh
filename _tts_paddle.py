# -*- coding: utf-8 -*-
"""PaddleOCR 2.7 重识读：f30(deck50) 全区 / f22,f33 状态牌格 / f22_back c30"""
import json, os
import numpy as np
from PIL import Image
from paddleocr import PaddleOCR

BASE = r"D:\Arkham Horror PSD\BattleConDB\battlecon-diy-zh\memory-pending\tts-img"
engine = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
out = {}

def ocr_cell(im, box):
    cell = np.array(im.crop(box))
    r = engine.ocr(cell, cls=True)
    if not r or not r[0]:
        return ""
    return " ".join(line[1][0] for line in r[0]).strip()

jobs = [("f30", list(range(8, 45))), ("f22", list(range(10, 37))),
        ("f33", list(range(10, 26))), ("f22_back", [30])]

for key, cells in jobs:
    im = Image.open(os.path.join(BASE, "full", key + ".jpg"))
    W, H = im.size
    cw, chh = W // 10, H // 7
    out[key] = {}
    for n in cells:
        rr, cc = divmod(n, 10)
        out[key][n] = ocr_cell(im, (cc*cw, rr*chh, (cc+1)*cw, (rr+1)*chh))
    print(key, "done", flush=True)
    json.dump(out, open(os.path.join(BASE, "paddle_ocr.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print("ALL DONE")
