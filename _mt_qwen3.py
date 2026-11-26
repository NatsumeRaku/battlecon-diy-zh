# -*- coding: utf-8 -*-
"""第三版: 全量对照表+句对库+时点词表喂入, 32K上下文, 全量重跑"""
import json, io, os, glob, urllib.request

ROOT = r"D:\Arkham Horror PSD\BattleConDB\battlecon-diy-zh"
OUTD = os.path.join(ROOT, "memory-pending", "mt-draft-qwen")
os.makedirs(OUTD, exist_ok=True)

def rd(p): return io.open(os.path.join(ROOT, p), encoding="utf-8").read()

gloss = rd("_mt_qwen.py")
import re as _re
GLOSS = _re.search(r'GLOSS = """(.*?)"""', gloss, _re.S).group(1)

corpus = f"""{GLOSS}

【时点词表（封闭值,禁表外词）】
{rd('convention/时点词表.md')}

【官方句对库全文（句式标准,右列即官方译文）】
{rd('convention/官方句对库.md')}

【中英译名对照表全文（角色名/卡名/机制名官方译名,翻译时先查此表）】
{rd('convention/中英译名对照表.md')}
"""
print("corpus chars:", len(corpus))

def chat(u):
    req = urllib.request.Request("http://127.0.0.1:7711/v1/chat/completions",
        data=json.dumps({"model": "qwen", "messages": [
            {"role": "system", "content": corpus},
            {"role": "user", "content": "翻译：" + u}],
            "temperature": 0.1, "max_tokens": 300}).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=1800) as r:
        return json.load(r)["choices"][0]["message"]["content"].strip()

files = sorted(glob.glob(os.path.join(ROOT, "json-db/en/流浪者篇-WAN/*/*.json")))
rows = []
for p in files:
    d = json.load(io.open(p, encoding="utf-8"))
    if d.get("卡类") == "角色":
        continue
    for e in d.get("效果", []):
        src = str(e.get("效果", "")).strip()
        if src and "OCR" not in src:
            rows.append((p.split("流浪者篇-WAN\\")[1].split("\\")[0], d.get("卡类",""), d.get("名称",""), e.get("时点",""), src))
print("rows:", len(rows))

out = []
for i, (ch, kl, nm, sd, src) in enumerate(rows):
    try:
        zh = chat(src)
    except Exception as ex:
        zh = f"ERR {ex}"
    out.append({"角色": ch, "卡类": kl, "名称": nm, "时点": sd, "en": src, "zh": zh})
    print(i+1, "/", len(rows), ch, zh[:40].replace("\n", " "), flush=True)
    if (i+1) % 20 == 0:
        io.open(os.path.join(OUTD, "draft-v3.json"), "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))

io.open(os.path.join(OUTD, "draft-v3.json"), "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))
print("ALL DONE", len(out))
