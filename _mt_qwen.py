# -*- coding: utf-8 -*-
"""Qwen 本地翻译 WAN 卡面效果——封闭术语表注入,三方对照输出"""
import json, io, os, glob, urllib.request

ROOT = r"D:\Arkham Horror PSD\BattleConDB\battlecon-diy-zh"
DRAFT = os.path.join(ROOT, "memory-pending", "mt-draft")
OUT = os.path.join(ROOT, "memory-pending", "mt-draft-qwen")
os.makedirs(OUT, exist_ok=True)

GLOSS = """你是《战链BattleCON》卡牌效果翻译器,翻译必须模仿官方中文卡面风格。严格规则：
1. 术语表（必须遵守，禁自造）：Hit=命中; Start=开始; Before=前置; After=后置; End=结束; Reveal=展示; Damage=伤害; Recycle=循环; Whenever/When=当; Ante=投注; Setup=初始设置; Opponent=对手; Advance=前进; Retreat=后退; Close=逼近(朝对手方向尽可能移动); Push=推动; Pull=拉动; Power=威力; Priority=速度; Guard=韧性; Armor=护甲; Range=距离; Chip=削命; Stun Immunity=眩晕免疫; Force=能量; Life=生命; beat=回合; this beat=本回合; for the rest of the duel=本场对决余下时间; regain=回收; discard=弃置; trash=摧毁; supply=供应堆; Base=招式; Style=风格; Finisher=终结技; spend=消耗; pay=支付; use=使用; remove=移除; cannot=不能; would=将要; instead=改为; space=格; adjacent=相邻的; dodge/avoid=回避攻击; teleport=瞬移; as far as possible=尽可能; or less=或更低; or more=或更多.
2. 时点词原样保留在译文开头,格式=时点词+全角冒号+效果;可选时点作"开始,可选:…".
3. 角色机制名译为中文专名(Frost=冰霜/Wish=愿望/Fate=命运/Wisp=魂火/Thorn=荆棘/Target=靶标/Function=机能).
4. 数字与符号原样保留(+1/-2/1~3/0+);"X或更多"用官方档位记法"2+".
5. 官方句式范例（照此风格）：
- Push or pull 1-2 → 推动或拉动1-2
- Move directly to any space behind your opponent → 瞬移至对手身后的任意格
- If you advanced 2+ spaces and didn't move past the opponent: +2 Power → 若你因此移动了2+格并且没有移动越过对手,+2威力。
- Retreat as far as possible → 尽可能后退
- The opponent must choose and discard 1 base → 对手必须选择并弃置1张招式。
- Ante: use 1 Malice to +1 Speed → 投注:使用1恶意来+1速度
6. 只输出译文，禁解释。"""

def chat(user):
    req = urllib.request.Request("http://127.0.0.1:7711/v1/chat/completions",
        data=json.dumps({"model": "qwen", "messages": [
            {"role": "system", "content": GLOSS},
            {"role": "user", "content": "翻译：" + user}],
            "temperature": 0.1, "max_tokens": 256}).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.load(r)["choices"][0]["message"]["content"].strip()

# 从 en 库取原始效果句（比 mt-draft 里的更全）
files = sorted(glob.glob(os.path.join(ROOT, "json-db/en/流浪者篇-WAN/*/*.json")))
rows = []
for p in files:
    d = json.load(io.open(p, encoding="utf-8"))
    rel = os.path.relpath(p, ROOT).replace("json-db\\en\\流浪者篇-WAN\\", "")
    if d.get("卡类") == "角色":
        continue
    for e in d.get("效果", []):
        src = str(e.get("效果", "")).strip()
        if not src or "OCR" in src:
            continue
        rows.append((rel.split("\\")[0], d.get("卡类", ""), d.get("名称", ""), e.get("时点", ""), src))
    print(rel, flush=True)

out = []
for i, (ch, kl, nm, sd, src) in enumerate(rows):
    try:
        zh = chat(src)
    except Exception as ex:
        zh = f"ERR {ex}"
    out.append({"角色": ch, "卡类": kl, "名称": nm, "时点": sd, "en": src, "zh": zh})
    print(i + 1, "/", len(rows), ch, zh[:40].replace("\n", " "), flush=True)
    if (i + 1) % 20 == 0:
        io.open(os.path.join(OUT, "draft.json"), "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))

io.open(os.path.join(OUT, "draft.json"), "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))
print("ALL DONE", len(out))
