# -*- coding: utf-8 -*-
"""从 TTS awn 存档提取 CustomDeck 卡表图 URL 与引用格"""
import re, json, sys

raw = open(r"D:\steamcmd\steamapps\workshop\content\286160\2182704749\1625192516003511077_legacy.bin", "rb").read()
print("size", len(raw), "head", raw[:16])

# 找所有 FaceURL/BackURL 与 deckID 上下文
txt = raw.decode("utf-8", errors="replace")
urls = sorted(set(re.findall(r"https?://[^\s\"\\]+steamusercontent[^\s\"\\]+", txt)))
for u in urls:
    print(u)
