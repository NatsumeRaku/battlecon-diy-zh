# -*- coding: utf-8 -*-
"""PaddleOCR：f09(deck1斗士卡+UA背) 全部格"""
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

for key in ["f09"]:
    im = Image.open(os.path.join(BASE, "full", key + ".jpg"))
    W, H = im.size
    cw, chh = W // 10, H // 7
    out[key] = {}
    for n in range(70):
        rr, cc = divmod(n, 10)
        out[key][n] = ocr_cell(im, (cc*cw, rr*chh, (cc+1)*cw, (rr+1)*chh))
    print(key, "done", flush=True)
    json.dump(out, open(os.path.join(BASE, "paddle_ocr3.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print("ALL DONE")
