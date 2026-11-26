# -*- coding: utf-8 -*-
"""全部卡表图切片+标题OCR，输出 cellmeta_ocr.json"""
import json, os
from PIL import Image
from rapidocr_onnxruntime import RapidOCR

IMG = r"D:\Arkham Horror PSD\BattleConDB\battlecon-diy-zh\memory-pending\tts-img\full"
OUT = r"D:\Arkham Horror PSD\BattleConDB\battlecon-diy-zh\memory-pending\tts-img"
engine = RapidOCR()
result = {}

sheets = [f"f{i:02d}.jpg" for i in range(34)]
for fn in sheets:
    im = Image.open(os.path.join(IMG, fn))
    W, H = im.size
    if (W, H) == (3750, 3675):
        cw, ch, cols, rows = 375, 525, 10, 7
    elif (W, H) == (7500, 7350):
        cw, ch, cols, rows = 750, 1050, 10, 7
    else:
        continue
    key = fn[:-4]
    result[key] = {}
    for r in range(rows):
        for c in range(cols):
            cell = im.crop((c*cw, r*ch, (c+1)*cw, (c+1)*ch))
            title = cell.crop((0, 0, cw, int(ch*0.18)))
            txt, _ = engine(title)
            line = " ".join(t[1] for t in txt) if txt else ""
            result[key][r*cols+c] = line.strip()
    print(key, "done", flush=True)

json.dump(result, open(os.path.join(OUT, "cellmeta_ocr.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("ALL DONE")
