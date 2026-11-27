import json, re, os, glob

ROOT = r"D:/Arkham Horror PSD/BattleConDB/battlecon-diy-zh/json-db/zh/战争篇-WAR"
ALLOWED = {"", "初始设置", "投注", "展示", "开始", "前置", "命中", "伤害", "后置", "结束", "循环", "当", "每当", "持续", "击破", "限定投注"}
EN_TERMS = re.compile(r"\b(Power|Priority|Range|Guard|Armor|Stun|Advance|Retreat|Push|Pull|Hit|Reveal|End|Before|After|Setup|Ante|Recycle|Opponent|Force|Life|Space|Base|Style|Finisher|Trash|Discard|Teleport|Shift|Clash)\b", re.I)

files = glob.glob(os.path.join(ROOT, "**", "*.json"), recursive=True)
batch = 0
term_hits, timing_hits = [], []
for f in files:
    try:
        d = json.load(open(f, encoding="utf-8"))
    except Exception as e:
        print("JSON FAIL", f, e)
        continue
    if "行258" not in d.get("备注", ""):
        continue
    batch += 1
    effs = d.get("效果", [])
    if isinstance(effs, dict):
        effs = [v for x in effs.values() if isinstance(x, list) for v in x]
    for i, eff in enumerate(effs):
        if isinstance(eff, str):
            m = EN_TERMS.findall(eff)
            if m: term_hits.append((f, i, "裸串", m))
            continue
        tp = eff.get("时点", "")
        if tp not in ALLOWED:
            timing_hits.append((f, i, tp))
        for k in ("效果", "条件"):
            m = EN_TERMS.findall(str(eff.get(k, "")))
            if m:
                term_hits.append((f, i, k, m))

print("行258档数:", batch)
print("英文术语残留:", len(term_hits))
for x in term_hits[:10]: print("  ", x)
print("时点越界:", len(timing_hits))
for x in timing_hits[:10]: print("  ", x)
