# -*- coding: utf-8 -*-
"""行267 续: 乔尔 c21~c25 五档按行210 用户裁定+行267 图证正名; 多人模式同名档标重复
依据: 行210 备注已载「c21~c25=乔尔;实物卡名与本文件名不符(Arcane Binding/Knuckle Cross/
Cannon Follow-Up/Innervating Runes/Ironstar Bulwark),deck43中块文件名整体存疑[待核]」
本行以 deck43 标题带放大目识逐条坐实该五名, 属落实既有裁定而非新拟。
"""
import json, io, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EN = os.path.join(ROOT, 'json-db', 'en')
JOEL = os.path.join(EN, '毁灭篇-DEV', '乔尔·卡尔莫')
MULTI = os.path.join(EN, '多人模式')

def load(p): return json.loads(io.open(p, encoding='utf-8').read())
def save(p, d):
    io.open(p, 'w', encoding='utf-8', newline='\n').write(
        json.dumps(d, ensure_ascii=False, indent=1))

def strip267(b):
    return b.split(';行267图证')[0]

# 1) 乔尔四档正名（Knuckle Cross 已在上一脚本改名，此处补齐其余四）
REN = [
    ('状态效果牌_Azure Bands.json',           'Azure Bands[待核]',      'Arcane Binding',     '状态效果牌_Arcane Binding.json',     21),
    ('状态效果牌_Cannot Follow-Up.json',      'Cannot Follow-Up[待核]', 'Cannon Follow-Up',   '状态效果牌_Cannon Follow-Up.json',   23),
    ('状态效果牌_Wreaking Knees.json',        'Wreaking Knees[待核]',   'Innervating Runes',  '状态效果牌_Innervating Runes.json',  24),
    ('状态效果牌_Form Blur.json',             'Form Blur[待核]',        'Ironstar Bulwark',   '状态效果牌_Ironstar Bulwark.json',   25),
]
for old, oldname, newname, newfile, cell in REN:
    p = os.path.join(JOEL, old)
    d = load(p)
    d['名称'] = newname
    d['备注'] = strip267(d.get('备注') or '').rstrip(';；') + (
        ';行267图证:TTS图包deck43_c%d标题带放大4-6倍逐字目识;卡面实读%s,'
        '旧名%s系OCR误读,依行210「实物卡名与本文件名不符」记载正名' % (cell, newname, oldname.replace('[待核]', '')))
    save(p, d)
    tgt = os.path.join(JOEL, newfile)
    os.rename(p, tgt)
    print('正名 %-28s -> %-20s c%d' % (oldname, newname, cell))

# 2) 乔尔 character.json 清单同步
cp = os.path.join(JOEL, 'character.json')
cd = load(cp)
lst = cd['卡牌清单']
for old, oldname, newname, newfile, cell in REN + [
        ('状态效果牌_Assault Crisis.json', 'Assault Crisis[待核]', 'Knuckle Cross',
         '状态效果牌_Knuckle Cross.json', 22)]:
    if old in lst:
        lst[lst.index(old)] = newfile
save(cp, cd)
print('乔尔清单同步', len(lst), '项; 现存状态牌:', [x for x in lst if x.startswith('状态效果牌')])

# 3) 多人模式同名四档标重复（不删）
for _, _, newname, newfile, cell in REN:
    p = os.path.join(MULTI, newfile)
    d = load(p)
    b = strip267(d.get('备注') or '').rstrip(';；')
    d['备注'] = b + (';行267图证:deck43_c%d 卡面实读%s;与 毁灭篇-DEV/乔尔·卡尔莫 同名档同格同卡,'
                     '判为重复档[待核·重复档]未删待裁定' % (cell, newname))
    save(p, d)
    print('标重复 %-26s c%d' % (newname, cell))
