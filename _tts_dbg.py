# -*- coding: utf-8 -*-
import re, struct
raw = open(r"D:\steamcmd\steamapps\workshop\content\286160\2182704749\1625192516003511077_legacy.bin", "rb").read()
ms = list(re.finditer(b"FaceURL\x00", raw))
print("count", len(ms))
for m in ms[:6]:
    i = m.end()
    ln = struct.unpack_from("<i", raw, i)[0]
    url = raw[i+4:i+4+ln].decode()
    pre = raw[m.start()-12:m.start()]
    print(repr(pre), "->", url[:80])
