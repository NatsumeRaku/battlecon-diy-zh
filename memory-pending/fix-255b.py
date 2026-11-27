# -*- coding: utf-8 -*-
# 行255b: zh树UA档重命名(?非法字符) + John旧英文β档删除 + character.json重建
import json, os, glob

ZHW = r'D:\Arkham Horror PSD\BattleConDB\battlecon-diy-zh\json-db\zh\流浪者篇-WAN'
ENW = r'D:\Arkham Horror PSD\BattleConDB\battlecon-diy-zh\json-db\en\流浪者篇-WAN'

REN = {  # (角色, 截断文件名前缀) -> 新UA中文档名
 ('Cionaodh'): '特技(UA)_驰骋一生[待核].json',
 ('Dajin'): '特技(UA)_黄粱美梦.json',
 ('Feylana'): '特技(UA)_规章限制[待核].json',
 ('John'): '特技(UA)_马里亚尼诅咒[待核].json',
 ('Kai'): '特技(UA)_难解之匣[待核].json',
 ('Kora'): '特技(UA)_沙漠怀抱[待核].json',
 ('Rin'): '特技(UA)_霜咬[待核].json',
 ('Vekyl'): '特技(UA)_永恒奴役[待核].json',
 ('Wendy'): '特技(UA)_空中支援[待核].json',
}
for ch, new in REN.items():
    p = os.path.join(ZHW, ch)
    olds = [f for f in os.listdir(p) if f.startswith('特技(UA)_[待译')]
    for old in olds:
        os.rename(os.path.join(p, old), os.path.join(p, new))
        print('ren', ch, old, '->', new)

# Dajin的UA档名对不上(黄粱美梦已存在则删截断档)
# John旧英文β档
oldbm = os.path.join(ZHW, 'John', '终结技_Blast Mining.json')
if os.path.exists(oldbm):
    os.remove(oldbm); print('del zh John old Blast Mining')
# Dajin:截断档内容=黄粱美梦?检查后ren到正确名
for ch in REN:
    p = os.path.join(ZHW, ch)
    cj = os.path.join(p, 'character.json')
    c = json.load(open(cj, encoding='utf-8'))
    c['卡牌清单'] = sorted(f for f in os.listdir(p) if f != 'character.json')
    json.dump(c, open(cj, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
# en树character.json重建(保险)
for base in glob.glob(os.path.join(ENW, '*', '')):
    cj = os.path.join(base, 'character.json')
    c = json.load(open(cj, encoding='utf-8'))
    c['卡牌清单'] = sorted(f for f in os.listdir(base) if f != 'character.json')
    json.dump(c, open(cj, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('done')
