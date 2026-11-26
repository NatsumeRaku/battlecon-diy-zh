# -*- coding: utf-8 -*-
"""解析 awn 二进制：deckID -> FaceURL/BackURL"""
import re, json, struct

raw = open(r"D:\steamcmd\steamapps\workshop\content\286160\2182704749\1625192516003511077_legacy.bin", "rb").read()

decks = {}
for m in re.finditer(b"FaceURL\x00", raw):
    i = m.end()
    # 长度前缀 int32 LE
    ln = struct.unpack_from("<i", raw, i)[0]
    url = raw[i+4:i+4+ln].decode()
    # deckID = 再往前：FaceURL 字段名前是 int32 id
    # 结构: [id:int32]\x00\x02? 实际观察: "http.../\x00\x02BackURL" -> id 在 FaceURL 标记前 4~6 字节
    # 取 FaceURL 起始前 8 字节尝试找小整数
    pre = raw[max(0, m.start()-8):m.start()]
    did = None
    for off in (4, 0, 6):
        if len(pre) >= off+4:
            v = struct.unpack_from("<i", pre, len(pre)-off-4)[0]
            if 1 <= v <= 99:
                did = v
                break
    j = raw.index(b"BackURL\x00", i)
    ln2 = struct.unpack_from("<j".replace("j","i"), raw, j+8)[0] if False else struct.unpack_from("<i", raw, j+8)[0]
    back = raw[j+12:j+12+ln2].decode()
    decks.setdefault(did, (url, back))

out = {str(k): {"FaceURL": v[0], "BackURL": v[1]} for k, v in sorted(decks.items()) if k}
with open(r"D:\Arkham Horror PSD\BattleConDB\battlecon-diy-zh\memory-pending\tts-img\decks.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
for k, v in sorted(out.items(), key=lambda x: int(x[0])):
    print(k, v["FaceURL"])
