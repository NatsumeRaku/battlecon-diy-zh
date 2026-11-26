# -*- coding: utf-8 -*-
# 行235: WAR 14斗士 UA 录入(OCR底稿 ua-beta-ocr-war-2026-11-27.txt)
import json, io, os

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "json-db", "en", "战争篇-WAR")
SRC = "官方实卡"

def ua(folder, name, desc, effects, note):
    path = os.path.join(BASE, folder, "特技(UA)_%s.json" % name)
    data = {
        "角色": folder.split(" ")[0] if False else None,
        "卡类": "特技(UA)",
        "名称": name,
        "系列": "战争篇-WAR",
        "机制概述": desc,
        "效果": effects,
        "台词": "",
        "来源": SRC,
        "备注": note,
    }
    return path, data

def fx(t, c, e):
    return {"时点": t, "条件": c, "效果": e}

NOTE = "来源注记:TTS图包卡背;deck1_back格%s卡背实读(2026-11-27卡背图切片,OCR+目识双核);%s"

items = []

# 42 Demitras
items.append(ua("Demitras Denigrande", "Crescendo[待核]",
    "Demitras has 4 Crescendo Tokens. He has more Priority while he holds them, but can also ante them for Power. Choose between speed and offense at the right moment to gain the upper hand.",
    [fx("初始设置", "", "You have 2 Crescendo. Deplete the rest."),
     fx("限定投注", "", "Use a Crescendo."),
     fx("当", "you are hit", "deplete a Crescendo."),
     fx("展示", "", "+1 Priority per held Crescendo."),
     fx("结束", "", "Regain a Crescendo.")],
    NOTE % ("42", "UA名OCR缺字,拟Crescendo[待核];投注行OCR残片见+2 Power×4与↑↓标,疑耗1得+2威力,待视觉核;末行Regain时点前缀OCR缺,拟结束[待核]")))

# 44 Hepzibah
items.append(ua("Hepzibah Culotre", "Dark Pact",
    "Hepzibah has 5 Pact Cards. She can spend life each turn to gain their benefits. While they are powerful, she must be careful to keep an eye on her life as missing attacks can be costly.",
    [fx("初始设置", "", "You have 5 inactive Pacts."),
     fx("开始", "", "Spend 1 life to activate a Pact."),
     fx("循环", "", "Deactivate all Pacts.")],
    NOTE % ("44", "激活Pact行时点前缀OCR缺,拟开始[待核]")))

# 45 Hikaru
items.append(ua("Hikaru", "Geomorphic Assault[待核]",
    "Hikaru has 4 distinct Element Tokens. He can use these for different effects and gain them back over the course of the duel. Use them to power up his attacks at the right time.",
    [fx("初始设置", "", "You have 4 Elements."),
     fx("限定投注", "", "Use an Element. The used Element cannot be regained this beat. Fire: +3 Power. Earth: Armor 3. Water: -1~+1 Range. Wind: +2 Priority.")],
    NOTE % ("45", "UA名OCR作GEOMANTIC ASSAULT,疑Geomorphic Assault[待核]")))

# 46 Kallistar(效果大面积不可读,仅概述+初始设置)
items.append(ua("Kallistar", "Form of Disaster",
    "Kallistar switches between Human and Elemental Form. In Human form she is more defensive and in Elemental form she is faster and more offensive, but loses life.",
    [fx("初始设置", "", "You are Human.")],
    NOTE % ("46", "本卡OCR效果区大面积乱码,仅概述与初始设置可录;人形/元素形转换规则待视觉识读补录[挂账]")))

# 48 Khadath
items.append(ua("Khadath", "Gate Trap",
    "Khadath has a Gate Marker. Opponents moving onto the marker stop their movement and grant Khadath an advantage when on or adjacent to it. Position your Gate well to hinder Opponents.",
    [fx("初始设置", "", "Put the Gate in your supply (it is not on the arena)."),
     fx("当", "the Opponent enters the Gate's space", "stop the Opponent's movement."),
     fx("展示", "the Opponent is on the Gate", "+3 Priority."),
     fx("展示", "the Opponent is adjacent to the Gate", "+1 Priority.")],
    NOTE % ("48", "")))

# 49 Lixis
items.append(ua("Lixis", "Withering Touch",
    "Lixis can discard Bases from the Opponent's hand when she hits them, limiting their options on future beats.",
    [fx("初始设置", "", "Virus is inactive."),
     fx("命中", "", "The Opponent discards a Base. (Discarded cards go into the Discard Pile alongside the Opponent's Attack Pair during recycle.)")],
    NOTE % ("49", "弃基底稿无时点前缀,据机制概述拟命中[待核];角色全名按页脚LIXIS RAN KANDA")))

# 50 Luc
items.append(ua("Luc", "Temporal Battery",
    "Luc builds up Time Counters over the course of the duel. He can spend these to activate his Temporal Battery's power. The more Time he uses, the better the effects become.",
    [fx("初始设置", "", "You have 2 Time. Deplete the rest."),
     fx("限定投注", "", "Spend any amount of Time for no effect (your Unique Ability's triggers are affected by how much Time is spent using this ante)."),
     fx("展示", "1-2 Time anted", "+1 Priority."),
     fx("开始", "3-4 Time anted", "Advance 1-2."),
     fx("开始", "5 Time anted", "Become Active Player."),
     fx("结束", "", "Regain 1 Time.")],
    NOTE % ("50", "底稿Advance 1-2标Optional,OCR句号存疑,暂照录;开始行可选式照规范可补,可选：")))

# 51 Magdelina
items.append(ua("Magdelina", "Divine Conduit",
    "Magdelina gains Trance Counters over time. She can spend Trance to Level Up, growing permanently more powerful.",
    [fx("初始设置", "", "Activate Level 0. Your other Levels are inactive. Deplete all Trance."),
     fx("持续", "", "Level Up: Level Up by activating the next Level in sequence (0 > 1 > 2 > 3 > 4 > 5). Only one Level can be active at a time. Deactivate any older Level when activating a new one."),
     fx("结束", "", "Regain a Trance.")],
    NOTE % ("51", "Level Up为卡面自定义术语,时点挂持续[待规范];升级箭头链OCR作0 1 > 293 54> 5,按0~5序列照录")))

# 52 Rukyuk
items.append(ua("Rukyuk", "Custom Ammunition",
    "Rukyuk has 6 Ammo Tokens that give him different benefits on his attacks. He must use Ammo to hit with his attacks, so he must be careful when he uses which Ammo.",
    [fx("初始设置", "", "You have 6 Ammo."),
     fx("限定投注", "", "Use an Ammo. Explosive: +2 Power. Longshot: -1~+1 Range. AP: Ignore Armor. Swift: +2 Priority. Flash: Ignore Guard. Impact: Push 2."),
     fx("前置", "Ammo not anted", "This attack does not hit.")],
    NOTE % ("52", "")))

# 53 Sagas
items.append(ua("Sagas", "Shadow Mirror",
    "Sagas has 1 Mirror Token he can use to copy an opponents' bonuses and penalties. He fights by copying and negating the opponent's attacks.",
    [fx("初始设置", "", "You have Mirror."),
     fx("限定投注", "", "Use Mirror (gain all bonuses and penalties to Range, Power, Priority, and Guard that are currently applied to the Opponent. Do not gain bonuses and penalties that are applied after anteing Mirror)."),
     fx("结束", "a Base in the Opponent's Discard Pile 1 has the same name as your attack's Base", "Regain Mirror.")],
    NOTE % ("53", "角色姓OCR作SEITIES,与C5挂账Sarafina无关;Sagas姓氏拼写待核")))

# 54 Seth
items.append(ua("Seth", "Beyond Eyes",
    "Seth can guess the Opponent's Bases and gains bonuses if he guesses correctly.",
    [fx("限定投注", "", "Name a Base. (Foresight: While the Opponent's Base is the one you named with your ante, you have Foresight.)"),
     fx("展示", "Foresight", "+2 Power and +2 Priority. Lose these bonuses if the Opponent's attack is replaced with a Finisher.")],
    NOTE % ("54", "页脚全名ETH CREMMUL(OCR),角色目录名Seth;全名拼写待核")))

# 55 Tatsumi
items.append(ua("Tatsumi & Juto", "Tidal Bond",
    "Tatsumi has a Juto marker. She gains benefits depending on her and Juto's positioning.",
    [fx("初始设置", "", "Place Juto in your space."),
     fx("持续", "", "Tatsumi gains stats and effects passively based on Juto's positioning on the arena. Behind Tatsumi: +0~1 Range, +1 Power. On Tatsumi's space: Armor 3. Between Tatsumi and Opponent: +4 Guard. On or behind Opponent: +1 Priority."),
     fx("当", "you prevent damage using Armor", "withdraw Juto.")],
    NOTE % ("55", "")))

# 56 Vanaah
items.append(ua("Vanaah", "Divine Rush",
    "Vanaah has a Divinity Token she can use to gain extra Power and Priority. This Token returns periodically, and can be used many times throughout a duel.",
    [fx("初始设置", "", "You have Divinity."),
     fx("限定投注", "", "Use Divinity (+2 Power, +2 Priority)."),
     fx("循环", "", "Regain any Divinity in Discard Pile 2. Put any Divinity in Discard Pile 1 into Discard Pile 2. Put any Divinity depleted this beat into Discard Pile 1.")],
    NOTE % ("56", "")))

# 57 Zaamassal
items.append(ua("Zaamassal", "Subjective Reality",
    "Zaamassal has 5 Paradigm Cards. His active Paradigm gives him bonuses, but he loses it if he is stunned.",
    [fx("初始设置", "", "You are Tranquil (other Paradigms remain inactive). Gate Opened is inactive."),
     fx("当", "you are stunned", "become Tranquil.")],
    NOTE % ("57", "页脚姓名OCR缺,角色目录名Zaamassal;Paradigm卡面文本随风格牌,UA仅录 Paradigm 概览")))

char_override = {
    "Demitras Denigrande": "Demitras", "Hepzibah Culotre": "Hepzibah", "Lixis Ran Kanda": "Lixis",
    "Magdelina Larington": "Magdelina", "Rukyuk Amberdeen": "Rukyuk", "Sagas Seities": "Sagas",
    "Tatsumi & Juto": "Tatsumi",
}

for path, data in items:
    folder = os.path.basename(os.path.dirname(path))
    data["角色"] = char_override.get(folder, folder)
    with io.open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("WROTE", os.path.relpath(path, os.path.dirname(BASE)))
