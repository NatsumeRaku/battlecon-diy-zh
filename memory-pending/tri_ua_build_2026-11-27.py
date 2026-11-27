# -*- coding: utf-8 -*-
"""行264: TRI 特技(UA) 9 档 + 配件 4 类建档
依据: output/ua-cards-2026-11-27/TRI/UA_cell40..49.jpg 逐字目识(放大3倍),
      非中文回译;时点色粗按卡面印刷(黑/绿/橙/红/蓝)逐卡照录。
只写 en 树(zh 树无 TRI 篇),不动任何既有官方效果文本。
"""
import json, os, io

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    'battlecon-diy-zh', 'json-db', 'en', '试炼篇-TRI')

NA = {"距离": "N/A", "威力": "N/A", "速度": "N/A", "韧性": "N/A"}


def w(rel, obj):
    p = os.path.join(BASE, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with io.open(p, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    print('W', rel)


def ua(role, name, mech, effects, note):
    return {
        "角色": role,
        "角标": "",
        "名称": name,
        "卡类": "特技(UA)",
        "系列": "试炼篇-TRI",
        "机制概述": mech,
        "效果": effects,
        "数值": NA,
        "来源": "官方实卡（TTS图包）",
        "备注": note,
    }


def e(t, c, s, bg=None):
    d = {"时点": t, "条件": c, "效果": s}
    if bg:
        d["背景"] = bg
    return d


# ---------------- 1. Amon / DAMAGE CONTROL ----------------
w('Amon/UA_Damage Control.json', ua(
    "Amon Elcela", "DAMAGE CONTROL",
    "Amon has 4 Danger Level Forms that upgrade as he takes damage each beat. Each gives him increasing benefits.",
    [
        e("初始设置", "", "<b>Setup:</b> Activate <i-sb>Code White</i-sb> (Lvl 0). Your other Danger Levels are inactive."),
        e("持续", "", "Only one Danger Level can be active at a time. Deactivate any older Danger Level when activating a new one."),
        e("结束", "", "<g-b>End:</g-b> Raise your Danger Level by activating the next one in this sequence (<i-sb>White</i-sb> → <i-sb>Green</i-sb> → <i-sb>Yellow</i-sb> → <i-sb>Red</i-sb>) if you took any damage. Otherwise, lower your Danger Level by activating the next one in this sequence (<i-sb>Red</i-sb> → <i-sb>Yellow</i-sb> → <i-sb>Green</i-sb> → <i-sb>White</i-sb>)."),
    ],
    "行264建档;来源注记:TTS图包TRI UA切片UA_cell40;UA卡逐字目识录入(非回译);机制概述=卡面斜体说明段(原文斜体,不套<i>);时点色粗按卡面印刷:Setup黑粗End绿粗;危险等级序列名直录Code White/Green/Yellow/Red,与同目录形态牌同名"
))

# ---------------- 2. Dravil / EBBING TIDE ----------------
w('Dravil/UA_Ebbing Tide.json', ua(
    "Dravil Coldwater", "EBBING TIDE",
    "Dravil has an Ice and a Steam Form, determined by which side of the arena he is on. His attacks change depending on which Form he is in, so use his mobility to set up the perfect attack!",
    [
        e("初始设置", "", "<b>Setup:</b> Place the <i-sb>Ice Marker</i-sb> on the edge of the arena behind Dravil, and the <i-sb>Steam Marker</i-sb> on the edge of the arena in front of him."),
        e("持续", "", "Dravil’s <i-sb>Ice</i-sb> triggers activate if he is closer to the <i-sb>Ice Marker</i-sb> than the Opponent. Dravil’s <i-sb>Steam</i-sb> triggers activate if he is closer to the <i-sb>Steam Marker</i-sb> than the Opponent. <i>(If there are Opponents on both sides of Dravil, he activates both kinds of triggers.)</i>"),
    ],
    "行264建档;来源注记:TTS图包TRI UA切片UA_cell41;UA卡逐字目识录入(非回译);机制概述=卡面斜体说明段;Setup黑粗;Ice/Steam标记已由行263建配件档(标记/正方形)"
))

# ---------------- 3. Hayden / BREAKING POINT ----------------
w('Hayden/UA_Breaking Point.json', ua(
    "Hayden Morgan", "BREAKING POINT",
    "Hayden has 7 double-sided Fury/Control Counters which she can use to enhance her attacks. Most of her cards give abilities by spending a group of Counters, flipping them over to their opposite side.",
    [
        e("初始设置", "", "<b>Setup:</b> Gain <i-sb>2 Fury</i-sb> and <i-sb>2 Control</i-sb>. Then, gain your choice of <i-sb>1 Fury</i-sb> or <i-sb>1 Control</i-sb>. Trash all remaining Fury/Control."),
        e("持续", "", "If you deplete a <i-sb>Fury</i-sb> or <i-sb>Control</i-sb>, also flip it over to its opposite side. <i>(Converting Fury to Control or vice versa.)</i>"),
        e("循环", "", "<b>Recycle:</b> Regain all Fury/Control. They remain on their current side."),
    ],
    "行264建档;来源注记:TTS图包TRI UA切片UA_cell42;UA卡逐字目识录入(非回译);机制概述=卡面斜体说明段;Setup/Recycle黑粗;配件按UA文Counters定计数物/五边形(配件条目规范三),双面同一批7枚"
))

# ---------------- 4. Kimbhe / ARCHMAGE'S STAFF ----------------
w("Kimbhe/UA_Archmage's Staff.json", ua(
    "Uleyla Kimbhe", "ARCHMAGE’S STAFF",
    "Kimbhe has a Staff Marker that gives Power to whoever stands on it. Her Styles and Unique Base let her control the Marker, leveraging it to enhance her attacks.",
    [
        e("初始设置", "", "<b>Setup:</b> Place the Staff in the center of the board."),
        e("每当", "any fighter hits (after other Hit triggers)",
          "<p-b>Whenever any fighter hits (after other Hit triggers),</p-b> if that fighter is on the Staff they gain <i-sb>+2 Power</i-sb>.", bg="灰底"),
    ],
    "行264建档;来源注记:TTS图包TRI UA切片UA_cell43;UA卡逐字目识录入(非回译);机制概述=卡面斜体说明段;Whenever段卡面紫字+灰底,按行255当/每当区分入每当(可多次触发);卡名撇号按卡面印刷ARCHMAGE’S"
))

# ---------------- 5. Lucida / JAWS OF MALEPHAISE ----------------
w('Lucida Malephaise/UA_Jaws of Malephaise.json', ua(
    "Lucida Malephaise", "JAWS OF MALEPHAISE",
    "Lucida has 4 double-sided Rend/Consume Tokens. When she hits the opponent, she gains a Rend Token, which automatically applies its effects next beat. The Rend Token then becomes an Ingest Token, which can be used on a future turn to empower Lucida.",
    [
        e("初始设置", "", "<b>Setup:</b> Deplete all Rend/Consume Tokens and place them with their <i-sb>Rend</i-sb> side up."),
        e("限定投注", "", "<o-b>Limited Ante:</o-b> Use a <i-sb>Consume Token</i-sb>, and flip it to its <i-sb>Rend</i-sb> side as you deplete it.", bg="橙底"),
        e("展示", "", "<b>Reveal:</b> Apply the effects of all <i-sb>Rend Tokens</i-sb> to the Opponent, then flip those tokens to their <i-sb>Consume</i-sb> side."),
        e("命中", "", "<r-b>Hit:</r-b> Regain a <i-sb>Rend Token</i-sb>."),
    ],
    "行264建档;来源注记:TTS图包TRI UA切片UA_cell44;UA卡逐字目识录入(非回译);机制概述=卡面斜体说明段;Setup/Reveal黑粗,Limited Ante橙底橙字,Hit红粗;说明段称Ingest Token而Setup/Limited Ante称Consume Token,原卡两词并存照录[待核];四枚指示物印刷名REND PAIN/COURAGE/SPIRIT/VALOR见配件档"
))

# ---------------- 6. Trias / EMBELLISH ----------------
w('Trias/UA_Embellish.json', ua(
    "Trias Blackwind", "EMBELLISH",
    "Trias has 6 Embellishment Cards, 3 Beginnings and 3 Endings. He can use these to enhance his attacks’ powers and names. The longer his attack however, the slower he will be!",
    [
        e("初始设置", "", "<b>Setup:</b> You have 6 inactive Embellishments (3 Beginnings and 3 Endings). Embellishments in your supply are always hidden from Opponents."),
        e("限定投注", "", "<o-b>Limited Ante:</o-b> Select a <i-sb>Beginning</i-sb>. It is activated when you reveal your Attack Pair.", bg="橙底"),
        e("限定投注", "", "<o-b>Limited Ante:</o-b> Select an <i-sb>Ending</i-sb>. It is activated when you reveal your Attack Pair.", bg="橙底"),
        e("展示", "1+ active Embellishments",
          "<b>Reveal, 1+ active Embellishments:</b> <i-sb>-3 Priority</i-sb> if you have 2 active Embellishments. Otherwise, <i-sb>-1 Priority</i-sb>. Revealed Embellishments are applied to your attack."),
        e("循环", "", "<b>Recycle:</b> Put any Embellishments in Discard Pile 2 into your supply. Put any Embellishments in Discard Pile 1 into Discard Pile 2. Put any active Embellishments into Discard Pile 1."),
    ],
    "行264建档;来源注记:TTS图包TRI UA切片UA_cell45;UA卡逐字目识录入(非回译);机制概述=卡面斜体说明段;两条Limited Ante均橙底橙字分列两条;6张饰品牌已于行237登记卡类饰品牌,本档只补UA本体"
))

# ---------------- 7. Burgundy / COLOR BURN ----------------
w('Burgundy/UA_Color Burn.json', ua(
    "Burgundy XII", "COLOR BURN",
    "Burgundy attacks from Paint Markers he scatters across the arena, building up Range as the duel goes on. As the arena gets covered, he can spend his Paint to set up Power bonuses or manipulate positioning.",
    [
        e("初始设置", "", "<b>Setup:</b> You have <i-sb>5 Paint</i-sb>. Place a Paint in your space and a Paint in the space directly in front of you."),
        e("前置", "", "<bl-b>Before:</bl-b> You may withdraw a <i-sb>Paint</i-sb> to calculate your attack’s Range from its space. Otherwise, your attack does not hit."),
        e("结束", "", "<g-b>End:</g-b> Place a <i-sb>Paint</i-sb> in your current space. <i>(Limit of one Paint per space)</i>."),
    ],
    "行264建档;来源注记:TTS图包TRI UA切片UA_cell47;UA卡逐字目识录入(非回译);机制概述=卡面斜体说明段;Setup黑粗,Before蓝粗,End绿粗;5 Paint按卡面flavor称Paint Markers入标记/正方形"
))

# ---------------- 8. Cindra / REBIRTH ----------------
w('Cindra/UA_Rebirth.json', ua(
    "Cindra Flama", "REBIRTH",
    "Cindra has a Human and Phoenix Form. She starts in her safer Human form, then changes to her dangerous Phoenix Form at half life. Each Form has its own set of Styles.",
    [
        e("初始设置", "", "<b>Setup:</b> You are <i-sb>Human</i-sb>."),
        e("循环", "10 or less life",
          "<b>Recycle, 10 or less life:</b> Your life becomes 10. Become <i-sb>Phoenix</i-sb>."),
    ],
    "行264建档;来源注记:TTS图包TRI UA切片UA_cell48;UA卡逐字目识录入(非回译);机制概述=卡面斜体说明段;Setup/Recycle黑粗;Human Form形态牌已录(Human/ Phoenix双形态),Phoenix Form形态牌文本仍缺,挂账待实卡"
))

# ---------------- 9. Dareios / DIPSOMANIA ----------------
w('Dareios/UA_Dipsomania.json', ua(
    "Dareios Kuel", "DIPSOMANIA",
    "Dareios has 5 Drink Cards that give him both a bonus and a penalty. They remain active until they leave his Discard Piles and then are gone for good, so careful use of his intoxicants is key.",
    [
        e("初始设置", "", "<b>Setup:</b> Your Drinks are inactive."),
        e("限定投注", "", "<o-b>Limited Ante:</o-b> Activate a <i-sb>Drink</i-sb>.", bg="橙底"),
        e("持续", "", "<b>Drinks:</b> Drinks remain active and apply to attacks even while in the Discard Piles."),
        e("循环", "", "<b>Recycle:</b> Trash any Drinks in Discard Pile 2. Put any Drinks in Discard Pile 1 into Discard Pile 2. Put any active Drinks into Discard Pile 1."),
    ],
    "行264建档;来源注记:TTS图包TRI UA切片UA_cell49;UA卡逐字目识录入(非回译);机制概述=卡面斜体说明段;Setup/Drinks/Recycle黑粗,Limited Ante橙底橙字;5张饮品牌已在库(风格_Slurred等角色套),本档只补UA本体"
))

# ---------------- 配件 4 类 ----------------
def acc(role, name, kind, shape, num, eff, note):
    return {
        "角色": role,
        "名称": name,
        "卡类": "配件",
        "系列": "试炼篇-TRI",
        "类别": kind,
        "效果": eff,
        "数量": num,
        "形状": shape,
        "来源": "官方实卡（TTS图包）",
        "备注": note,
    }

w('Hayden/配件_狂怒·控制计数物.json', acc(
    "Hayden Morgan", "狂怒·控制计数物", "计数物", "五边形", 7, "",
    "行264建档;来源注记:TTS图包TRI UA切片UA_cell42;英文原词=Fury/Control Counters;UA\"7 double-sided Fury/Control Counters\";双面共用同一批7枚(一面狂怒一面控制,耗尽即翻面转换);名称:狂怒/控制无官方先例+官方文本可覆写[待核]"
))

w('Kimbhe/配件_法杖.json', acc(
    "Uleyla Kimbhe", "法杖", "标记", "正方形", 1, "",
    "行264建档;来源注记:TTS图包TRI UA切片UA_cell43;英文原词=Staff Marker;UA\"Place the Staff in the center of the board\";站上者+2威力;名称:法杖无官方先例+官方文本可覆写[待核]"
))

w('Lucida Malephaise/配件_撕裂·吞噬指示物.json', acc(
    "Lucida Malephaise", "撕裂·吞噬指示物", "指示物", "圆形", 4,
    "四枚双面指示物(正面撕裂/背面吞噬)。正面印刷名与效果:①Rend Pain[待核:底边小字仅辨识到AFTER SUFFER C…]；②Rend Courage——Reveal: Ignore Armor；③Rend Spirit——+1 Priority；④Rend Valor——+1 Power。背面Consume面效果文本未见于UA卡图,待实卡补录。",
    "行264建档;来源注记:TTS图包TRI UA切片UA_cell44;英文原词=Rend/Consume Tokens;UA\"4 double-sided Rend/Consume Tokens\";形状圆形四枚,按配件条目规范三归指示物(效果非空);说明段另称Ingest Token,与Setup的Consume并存照录[待核];四枚正面小字部分不可辨,Rend Pain底边与背面文本均[待核],不臆造"
))

w('Burgundy/配件_颜料.json', acc(
    "Burgundy XII", "颜料", "标记", "正方形", 5, "",
    "行264建档;来源注记:TTS图包TRI UA切片UA_cell47;英文原词=Paint Marker;UA\"You have 5 Paint\"+flavor\"attacks from Paint Markers\";每格限一枚;名称:颜料无官方先例+官方文本可覆写[待核]"
))

print('done')
