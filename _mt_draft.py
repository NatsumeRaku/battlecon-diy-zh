# -*- coding: utf-8 -*-
"""WAN十斗士卡面双引擎机翻草稿：Argos vs Opus-MT -> memory-pending/mt-draft/"""
import json, io, os, re, glob

VENV = r"D:\mt-venv\Scripts\python.exe"
os.environ.setdefault("HF_HOME", r"D:\hf-cache")

import argostranslate.sbd as sbd
def _naive(self, text):
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
sbd.StanzaSentencizer.split_sentences = _naive
from argostranslate import translate as argos_tr

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch
tok = AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-en-zh")
mdl = AutoModelForSeq2SeqLM.from_pretrained("Helsinki-NLP/opus-mt-en-zh")
mdl.eval()

def opus(t):
    with torch.no_grad():
        x = tok(t, return_tensors="pt", truncation=True, max_length=512)
        y = mdl.generate(**x, max_length=256)
    return tok.decode(y[0], skip_special_tokens=True)

def argos(t):
    return argos_tr.translate(t, "en", "zh")

ROOT = r"D:\Arkham Horror PSD\BattleConDB\battlecon-diy-zh"
OUT = os.path.join(ROOT, "memory-pending", "mt-draft")
os.makedirs(OUT, exist_ok=True)

files = sorted(glob.glob(os.path.join(ROOT, "json-db/en/流浪者篇-WAN/*/*.json")))
rows = []
for p in files:
    d = json.load(io.open(p, encoding="utf-8"))
    rel = os.path.relpath(p, ROOT).replace("json-db\\en\\流浪者篇-WAN\\", "")
    for e in d.get("效果", []):
        src = e.get("效果", "").strip()
        if not src or "OCR" in src:
            continue
        try:
            rows.append((rel, d.get("卡类",""), d.get("名称",""), e.get("时点",""), src, argos(src), opus(src)))
        except Exception as ex:
            rows.append((rel, d.get("卡类",""), d.get("名称",""), e.get("时点",""), src, f"ERR {ex}", ""))
    print(rel, len(rows), flush=True)

# 按角色分文件输出
from collections import defaultdict
bychar = defaultdict(list)
for r in rows:
    bychar[r[0].split("\\")[0]].append(r)

for ch, rs in bychar.items():
    lines = [f"# {ch} 机翻草稿（Argos / Opus-MT 对照，未校对，禁直接入库）", ""]
    for rel, kl, nm, sd, src, a, o in rs:
        lines.append(f"## {kl}·{nm}（时点:{sd or '未析'}）")
        lines.append(f"EN: {src}")
        lines.append(f"Argos: {a}")
        lines.append(f"Opus: {o}")
        lines.append("")
    io.open(os.path.join(OUT, f"{ch}.md"), "w", encoding="utf-8").write("\n".join(lines))
print("ALL DONE", len(rows))
