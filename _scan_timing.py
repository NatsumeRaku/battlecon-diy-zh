# -*- coding: utf-8 -*-
# 全库时点规范扫描(行221/223/232)
import json, io, glob, re
issues = {k: [] for k in ["每当逗号", "当效果无每当或当时", "p-b误包", "持续印前缀", "时点常驻", "前置后置无蓝粗", "当条件为空", "每当未入p-b"]}

def walk(eff, path, nm, side=""):
    if isinstance(eff, dict):
        walk(eff.get("α面", []), path, nm, "α")
        walk(eff.get("β面", []), path, nm, "β")
        return
    for e in eff or []:
        if not isinstance(e, dict):
            continue
        t = e.get("时点", "") or ""
        c = e.get("条件", "") or ""
        s = e.get("效果", "") or ""
        loc = "%s%s|%s" % (path.split("json-db")[-1], side, nm)
        if "每当，" in s or "每当," in s:
            issues["每当逗号"].append(loc + "::" + s[:60])
        if t == "当":
            if not (s.startswith("<p-b>每当</p-b>") or re.match(r"^<p-b>.{0,12}时：</p-b>", s) or "时：" in s[:25]):
                issues["当效果无每当或当时"].append(loc + "::" + s[:60])
            if s.startswith("<p-b>每当") and not s.startswith("<p-b>每当</p-b>"):
                issues["p-b误包"].append(loc + "::" + s[:60])
            if "每当" in s and "<p-b>" not in s:
                issues["每当未入p-b"].append(loc + "::" + s[:60])
            if not c:
                issues["当条件为空"].append(loc + "::" + s[:60])
        if t == "持续" and (s.startswith("持续：") or s.startswith("持续:")):
            issues["持续印前缀"].append(loc + "::" + s[:60])
        if t == "常驻":
            issues["时点常驻"].append(loc)
        if t in ("前置", "后置") and not s.startswith("<bl-b>"):
            issues["前置后置无蓝粗"].append(loc + "[" + t + "]::" + s[:40])

for p in glob.glob("json-db/**/*.json", recursive=True):
    try:
        j = json.load(io.open(p, encoding="utf-8"))
    except Exception:
        continue
    walk(j.get("效果"), p, str(j.get("名称", "")))

for k, v in issues.items():
    print("== %s: %d" % (k, len(v)))
    for x in v[:10]:
        print("   ", x)
