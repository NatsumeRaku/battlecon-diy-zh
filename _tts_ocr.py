# -*- coding: utf-8 -*-
"""全部卡表图切片+标题OCR，输出 cellmeta_ocr.json"""
import json, os, traceback
from PIL import Image
from rapidocr_onnxruntime import RapidOCR

BASE = r"D:\Arkham Horror PSD\BattleConDB\battlecon-diy-zh\memory-pending\tts-img"
IMG = os.path.join(BASE, "full")
META = os.path.join(BASE, "cellmeta_ocr.json")
engine = RapidOCR()
result = json.load(open(META, encoding="utf-8")) if os.path.exists(META) else {}

for idx in range(34):
    fn = f"f{idx:02d}.jpg"
    im = Image.open(os.path.join(IMG, fn))
    W, H = im.size
    if (W, H) == (3750, 3675):
        cw, chh, cols, rows = 375, 525, 10, 7
    elif (W, H) == (7500, 7350):
        cw, chh, cols, rows = 750, 1050, 10, 7
    else:
        continue
    key = fn[:-4]
    if key in result and len(result[key]) == 70:
        continue
    result[key] = {}
    for rr in range(rows):
        for cc in range(cols):
            box = (cc*cw, rr*chh, (cc+1)*cw, (rr+1)*chh)
            cell = im.crop(box)
            tbox = (0, 0, cw, int(chh*0.18))
            title = cell.crop(tbox)
            txt, _ = engine(title)
            line = " ".join(t[1] for t in txt) if txt else ""
            result[key][rr*cols+cc] = line.strip()
    print(key, "done", flush=True)
    json.dump(result, open(META, "w", encoding="utf-8"), ensure_ascii=False)

print("ALL DONE")
