# -*- coding: utf-8 -*-
"""行239: WAN 宾客斗士10人 TTS录入——character补全+UA+风格(照录PaddleOCR,疑点标[待核])"""
import json, io, os, re

ROOT = r"D:\Arkham Horror PSD\BattleConDB\battlecon-diy-zh"
OCR = json.load(io.open(os.path.join(ROOT, "memory-pending/tts-img/tri_f04f05_full.json"), encoding="utf-8"))
F4, F5 = {int(k): v for k, v in OCR["f04"].items()}, {int(k): v for k, v in OCR["f05"].items()}
WAN = os.path.join(ROOT, "json-db/en/流浪者篇-WAN")

FIGHTERS = [
 # folder, 英文名, 称号, 机制名, f04块首格, f05风格首格, UA名, 风格名[0..4] (None=OCR缺名跳过)
 ("Anya","Anya Southwind","Defender of Justice","Flying/Grounded",0,0,None,
   ["Roundhouse",None,"Justice",None,"Alwnd"]),
 ("Cionaodh","Cionaodh O'Ciaominh","Phantom Thief","Motorcycle",4,5,None,
   ["Escape","Rocky",None,"Daring","Somersault"]),
 ("Dajin","Dajiin Nidala","Unbound Genie","Wish",8,10,"Wish Granted",
   [None,"Overpowering","Duplicitous","Wishful","Masterful"]),
 ("Feylana","Feylana Chorgitz[待核]","Regulamancer","Geas/Conviction",12,15,"Appeal",
   [None,"Showy","Awry","Serious",None]),
 ("John","John Strong Stevenson","Adventurer, Explorer, Scholar","Time",16,20,None,
   ["Hammering","Searing","Reactyrng[待核]","Solid","Landslide"]),
 ("Kai","Kalo Mekai","Puzzle Box Maker","Functions",20,25,"Collapsible Box",
   ["Complex","Secret","Flippen[待核]","Mysterious","Strange"]),
 ("Kora","Kora Sey Traxae[待核]","Sentinel of the Sands","Thorns",24,30,"Desert[待核]",
   ["Bristling[待核]","Barbed","Splintering","Poisonous","Sandstorm"]),
 ("Rin","Rin Coldwater","Northlands Ninja","Frost",28,35,"Deep Freeze",
   ["Stealthiest","Nimblest","Frost[待核]","Freezing",None]),
 ("Vekyl","Ser Vekyl Voroos","Revenant Knight","Wisps",32,40,None,
   [None,"Undead[待核]","Haunted",None,"Ghostorm[待核]"]),
 ("Wendy","Wendy Thrystle","Airship Engineer","Targets",36,45,"Precision Strike",
   ["Warning","Mortar[待核]","Airship[待核]","Suppressing",None]),
]

TIMING = {"Reveal":"展示","Setup":"展示","Start":"开始","Before":"前置","Hit":"命中",
          "Damage":"伤害","After":"后置","End":"结束","Flip":"循环","Recycle":"循环"}
STAT_RE = re.compile(r'RANGE\s+(\S+)\s+POWER\s*(\S+)\s+PR\w*\s*(\S+)\s+G\w+\s*(\S+)', re.I)
FOOT_RE = re.compile(r'\s*(?:\[.*$|\[\w*\s*)?(?:WAN|DEV|SLO|WAR|TRI|heocracy\b)[^.]*$', re.I | re.S)
SPLIT_RE = re.compile(r'(?=(?:Reveal|Setup|Start|Before|Hit|Damage|After|End|Flip|Recycle)\b[^.]{0,40}:)')

def clean(t):
    t = re.sub(r'\s*\[.*$', '', t, flags=re.S)
    t = re.sub(r'\s*(?:WAN|DEV|SLO|WAR|TRI|WAN\.)\s*$', '', t)
    t = re.sub(r'\s*heocracy\b[^.]*$', '', t, flags=re.I)
    return t.strip(' .')

def split_effects(text):
    text = clean(text)
    parts = [p.strip() for p in SPLIT_RE.split(text) if p.strip()]
    out = []
    for p in parts:
        m = re.match(r'(Reveal|Setup|Start|Before|Hit|Damage|After|End|Flip|Recycle)\b', p)
        t = TIMING.get(m.group(1), "") if m else ""
        out.append({"时点": t, "条件": "", "效果": p})
    return out or [{"时点": "", "条件": "", "效果": text}]

def stats(text, style=True):
    m = STAT_RE.search(text)
    if not m:
        return {"距离":"N/A","威力":"N/A","速度":"N/A","韧性":"N/A"}, clean(text)
    r, pw, pr, g = m.groups()
    return {"距离": r, "威力": pw, "速度": pr, "韧性": g}, clean(text[m.end():])

def save(p, d):
    io.open(p, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1))

log = []
for folder, ename, title, mech, b4, b5, ua_name, style_names in FIGHTERS:
    fdir = os.path.join(WAN, folder)
    os.makedirs(fdir, exist_ok=True)
    manifest = ["character.json"]
    missing = []

    # --- 风格×5 ---
    for i, nm in enumerate(style_names):
        cell = b5 + i
        raw = F5.get(cell, "").strip()
        if not raw:
            missing.append(f"f05格{cell}空"); continue
        if nm is None:
            missing.append(f"f05格{cell}卡名OCR未识读"); continue
        val, eff = stats(raw)
        d = {"角色": ename, "角标": "", "名称": nm if "[待核]" in nm else nm,
             "卡类": "风格", "系列": "流浪者篇-WAN",
             "效果": split_effects(eff), "数值": val,
             "备注": f"来源注记:TTS图包;WAN卡表B(f05)格{cell};页脚{folder.upper()[:6]}·WAN;PaddleOCR照录,装饰字体卡名{'含' if '[待核]' in nm else '无'}疑;行239录入",
             "来源": "官方实卡（TTS图包）"}
        fn = f"风格_{nm}.json"
        save(os.path.join(fdir, fn), d)
        manifest.append(fn)

    # --- UA ---
    ua_cell = b4 + 1
    ua_raw = F4.get(ua_cell, "").strip()
    if ua_raw:
        val, eff = stats(ua_raw, style=False)
        uname = ua_name if ua_name else "名称OCR未识读[待核]"
        d = {"角色": ename, "角标": "", "名称": uname, "卡类": "特技(UA)", "系列": "流浪者篇-WAN",
             "效果": split_effects(eff), "数值": val,
             "备注": f"来源注记:TTS图包;WAN卡表A(f04)格{ua_cell};PaddleOCR照录;UA卡名{"" if ua_name else "未"}识读;行239录入",
             "来源": "官方实卡（TTS图包）"}
        fn = f"特技(UA)_{uname}.json"
        save(os.path.join(fdir, fn), d)
        manifest.append(fn)

    # --- character.json 合并更新 ---
    cpath = os.path.join(fdir, "character.json")
    c = json.load(io.open(cpath, encoding="utf-8")) if os.path.exists(cpath) else {}
    old = c.get("卡牌清单", [])
    for x in old:
        if x not in manifest and (x.startswith("招式_") or x.startswith("终结技_")):
            manifest.append(x)
    c.update({"卡类": "角色", "名称": folder, "角色": ename, "英文全名": ename,
              "称号": title, "机制名": mech, "系列": "流浪者篇-WAN",
              "来源": "官方实卡（TTS图包）", "卡牌清单": sorted(manifest)})
    note = c.get("备注", "")
    c["备注"] = note + "；行239:TTS图包(f04/f05)补录英文全名/称号/UA/风格,缺名格:" + ("、".join(missing) if missing else "无")
    save(cpath, c)
    log.append(f"{folder}: {len(manifest)}件 缺:{missing}")

print("\n".join(log))
