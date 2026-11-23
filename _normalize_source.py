# -*- coding: utf-8 -*-
"""来源字段值域封闭 + 角色卡字段收编(2026-11-22 用户拍板)
A. 来源封闭为: 官方实卡 / 官方规则书 / DIY-工坊vN / 待核验
   注释性尾巴迁出到 memory-pending/source-notes-2026-11-22.md(铁律五)
B. 3张角色卡补id、删冗余"角色"键
C. 伯尔曼BCD角色卡补id与卡牌清单(由目录文件推导,不编数据)
"""
import json, glob, os, collections

ZH = 'json-db/zh'
MAP = {
    '官方实卡2026-11(用户拍摄)': '官方实卡',
    '官方实卡(2026-11-22用户拍照录入)': '官方实卡',
    'DIY-工坊v1(2026-11-22)': 'DIY-工坊v1',
    'DIY-工坊v2(2026-11-22)': 'DIY-工坊v2',
}
notes = []          # 迁出的尾巴
stat = collections.Counter()

for f in glob.glob(f'{ZH}/**/*.json', recursive=True):
    d = json.load(open(f, encoding='utf-8'))
    src = d.get('来源', '')
    new = MAP.get(src, src)
    if new not in ('官方实卡', '官方规则书', '待核验') and not new.startswith('DIY-工坊v'):
        # 带裁定尾巴的:取分号前主值,尾巴迁出
        main = src.split(';')[0]
        new = MAP.get(main, main)
        notes.append((f, src))
    if new != src:
        d['来源'] = new
        stat[f'{src} -> {new}'] += 1
        json.dump(d, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

# B. 3张角色卡收编
for path in glob.glob(f'{ZH}/*/*/character.json'):
    d = json.load(open(path, encoding='utf-8'))
    changed = False
    if '角色' in d:
        del d['角色']; changed = True
    if 'id' not in d:
        d['id'] = f"{d['系列']}-{d['名称']}"; changed = True
    if changed:
        json.dump(d, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        print('角色卡收编:', path, '->', d.get('id'))

# C. 伯尔曼角色卡补id+卡牌清单
bp = f'{ZH}/毁灭篇-BCD/巨龙伯尔曼/character.json'
d = json.load(open(bp, encoding='utf-8'))
d['id'] = '毁灭篇-BCD-巨龙伯尔曼'
d['卡牌清单'] = sorted(os.path.basename(x)[:-5] for x in glob.glob(f'{ZH}/毁灭篇-BCD/巨龙伯尔曼/*.json')
                       if not x.endswith('character.json'))
json.dump(d, open(bp, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('伯尔曼角色卡: 补id+卡牌清单', len(d['卡牌清单']), '张')

# 尾巴归档
if notes:
    with open('memory-pending/source-notes-2026-11-22.md', 'w', encoding='utf-8') as w:
        w.write('# 来源字段尾巴归档(2026-11-22 值域封闭时迁出)\n\n')
        for f, s in notes:
            w.write(f'- `{f}`\n  原值: {s}\n')
    print('尾巴归档:', len(notes), '条 -> memory-pending/source-notes-2026-11-22.md')

print('\n来源收编统计:')
for k, v in stat.most_common(): print(f'  {k}: {v}')
