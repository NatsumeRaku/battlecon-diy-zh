# -*- coding: utf-8 -*-
"""行267: deck43 状态效果牌卡名图证纠错 + 重复档标注
证据: output/tts-sheets/F_22.jpg (=deck43 正面图版 ugc/1473193085027875473) 逐格标题带放大 4-6 倍目识
"""
import json, io, os, glob, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, 'json-db', 'en')
EV = '行267图证:TTS图包deck43_c%d标题带放大4-6倍逐字目识;%s'

def load(p):
    return json.loads(io.open(p, encoding='utf-8').read())

def save(p, d):
    io.open(p, 'w', encoding='utf-8', newline='\n').write(
        json.dumps(d, ensure_ascii=False, indent=1))

def upd(p, name, cell, note, newfile=None):
    d = load(p)
    old = d['名称']
    d['名称'] = name
    b = d.get('备注') or ''
    d['备注'] = (b.rstrip(';；') + ';' + (EV % (cell, note))).strip(';')
    tgt = p
    if newfile:
        tgt = os.path.join(os.path.dirname(p), newfile)
        os.rename(p, tgt)
        # 同步同目录 character.json 清单
        cp = os.path.join(os.path.dirname(p), 'character.json')
        if os.path.exists(cp):
            cd = load(cp)
            lst = cd.get('卡牌清单')
            if isinstance(lst, list) and os.path.basename(p) in lst:
                lst[lst.index(os.path.basename(p))] = newfile
                save(cp, cd)
    save(tgt, d)
    print('改 %-42s %s -> %s' % (os.path.basename(tgt), old, name))

# A. 卡名纠错 4 处
upd(os.path.join(DB, '多人模式', '状态效果牌_Kiteredge Rush.json'),
    'Ritherwhyte Rush', 17,
    '卡面实读RITHERWHYTE RUSH,旧OCR误作Kiteredge Rush',
    '状态效果牌_Ritherwhyte Rush.json')

upd(os.path.join(DB, '毁灭篇-DEV', '埃力格·拉灵顿', '状态效果牌_Vital Silcer Rush.json'),
    'Vital Silver Rush', 18,
    '卡面实读VITAL SILVER RUSH,旧OCR误作Vital Silcer Rush',
    '状态效果牌_Vital Silver Rush.json')

upd(os.path.join(DB, '毁灭篇-DEV', '乔尔·卡尔莫', '状态效果牌_Assault Crisis.json'),
    'Knuckle Cross', 22,
    '卡面实读KNUCKLE CROSS,旧名Assault Crisis系误读;卡面文本为(Next beat, the Opponent is Vulnerable.)',
    '状态效果牌_Knuckle Cross.json')

upd(os.path.join(DB, '毁灭篇扩展-DEX', 'Borneo', '状态效果牌_Mazzaroth Comes!.json'),
    'Mazzaroth Comes...', 29,
    '卡面实读MAZZAROTH COMES...（省略号为卡名一部分,旧录感叹号有误）',
    '状态效果牌_Mazzaroth Comes....json')

# B. 重复档标注（不改名不删档，等用户裁定）
DUP = [
    ('多人模式', '状态效果牌_Salvaged Power.json', 13, 'Synchro Power'),
    ('毁灭篇-DEV/乔尔·卡尔莫', '状态效果牌_Azure Bands.json', 21, 'Arcane Binding'),
    ('毁灭篇-DEV/乔尔·卡尔莫', '状态效果牌_Cannot Follow-Up.json', 23, 'Cannon Follow-Up'),
    ('毁灭篇-DEV/乔尔·卡尔莫', '状态效果牌_Wreaking Knees.json', 24, 'Innervating Runes'),
    ('毁灭篇-DEV/乔尔·卡尔莫', '状态效果牌_Form Blur.json', 25, 'Ironstar Bulwark'),
]
for rel, fn, cell, other in DUP:
    p = os.path.join(DB, rel.replace('/', os.sep), fn)
    d = load(p)
    b = (d.get('备注') or '').rstrip(';；')
    d['备注'] = b + (';' + EV % (cell, '卡面实读%s,本档与%s效果逐字相同、同格同卡,判为重复档[待核·重复档]未删待裁定' % (other, other)))
    save(p, d)
    print('标重复 %-30s c%d <-> %s' % (fn, cell, other))
