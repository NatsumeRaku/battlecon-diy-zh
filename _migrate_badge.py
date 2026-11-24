# 2026-11-23 "待实卡"角标 → 来源字段(用户裁定)
import json, glob

stats = {'迁移': 0}
for path in glob.glob('json-db/**/*.json', recursive=True):
    d = json.load(open(path, encoding='utf-8'))
    b = d.get('角标')
    if isinstance(b, str) and b.strip().startswith('待实卡'):
        src = d.get('来源', '')
        note = '角标待实卡' if '战争篇无中文实卡' not in b else '战争篇无中文实卡,角标待核'
        d['来源'] = (src + ';' if src else '') + note
        d['角标'] = ''
        json.dump(d, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        stats['迁移'] += 1
print(stats)
# 校验残留
left = 0
for path in glob.glob('json-db/**/*.json', recursive=True):
    d = json.load(open(path, encoding='utf-8'))
    if isinstance(d.get('角标'), str) and '待实卡' in d['角标']:
        left += 1
        print('残留:', path, d['角标'])
print('残留数:', left)
