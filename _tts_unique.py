# -*- coding: utf-8 -*-
"""提取唯一 FaceURL 清单"""
import re, struct, json
raw = open(r"D:\steamcmd\steamapps\workshop\content\286160\2182704749\1625192516003511077_legacy.bin", "rb").read()
faces, backs = [], []
for m in re.finditer(b"FaceURL\x00", raw):
    i = m.end()
    ln = struct.unpack_from("<i", raw, i)[0]
    faces.append(raw[i+4:i+4+ln].decode())
for m in re.finditer(b"BackURL\x00", raw):
    i = m.end()
    ln = struct.unpack_from("<i", raw, i)[0]
    backs.append(raw[i+4:i+4+ln].decode())
uf = sorted(set(faces)); ub = sorted(set(backs))
print("unique faces", len(uf), "unique backs", len(ub))
with open(r"D:\Arkham Horror PSD\BattleConDB\battlecon-diy-zh\memory-pending\tts-img\unique_urls.json", "w") as f:
    json.dump({"faces": uf, "backs": ub}, f, indent=1)
for u in uf: print("F", u)
for u in ub: print("B", u)
