# -*- coding: utf-8 -*-
# 行254: Feylana五风格正名+补录(格15-19实读)
import json, os, glob

ROOT = r'D:\Arkham Horror PSD\BattleConDB\battlecon-diy-zh'
EN = os.path.join(ROOT, 'json-db/en/流浪者篇-WAN/Feylana')
ZH = os.path.join(ROOT, 'json-db/zh/流浪者篇-WAN/Feylana')
SRC = '官方实卡（TTS图包）'

MAP = [  # (旧名, 新英文, 中文, 格, 角标, 数值, 效果行)
 ('Awry', 'LAWFUL', '法定', 17, '黄六边形', {'距离':'+0','威力':'-1','速度':'+1','韧性':'+0'}, None),
 ('Serious', 'SERIOUS', '庄严', 18, '绿倒三角', {'距离':'+0~1','威力':'+1','速度':'+0','韧性':'+0'}, None),
 ('Showy', 'METICULOUS', '细致', 16, '橙五边形', {'距离':'+0~1','威力':'+0','速度':'+0','韧性':'+0'}, None),
]
NEWS = [
 ('PROFESSIONAL', '专家', 15, '红菱形', {'距离':'+0','威力':'-1','速度':'+0','韧性':'+0'},
  [{'时点':'展示','条件':'','效果':'Reveal: +1 Priority per card in the Geas Pile, up to +3.'},
   {'时点':'结束','条件':'','效果':'End: Advance 1-2.'}]),
 ('ATHLETIC', '矫健', 19, '蓝圆形', {'距离':'+0','威力':'-1','速度':'+1','韧性':'+0'},
  [{'时点':'前置','条件':'','效果':'Before: Advance 1.'},
   {'时点':'命中','条件':'','效果':'Hit: Push or Pull 0-X. X is the number of cards in the Geas Pile.'}]),
]

for old, newen, zh, cell, badge, stats, _ in MAP:
    p = os.path.join(EN, f'风格_{old}.json')
    d = json.load(open(p, encoding='utf-8'))
    d['名称'] = newen
    d['角标'] = badge
    d['数值'] = stats
    d['来源'] = SRC
    d['备注'] = f'行254 f05格{cell}卡面实读正名(旧误OCR为{old});五色对应红橙黄绿蓝=专家/细致/法定/庄严/矫健'
    json.dump(d, open(os.path.join(EN, f'风格_{newen}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    os.remove(p)
    # zh 树
    zmap = {'LAWFUL': ('风格_乖舛.json', '风格_法定.json'),
            'SERIOUS': ('风格_较真.json', '风格_庄严.json'),
            'METICULOUS': ('风格_炫示.json', '风格_细致.json')}
    zold, znew = zmap[newen]
    zp = os.path.join(ZH, zold)
    z = json.load(open(zp, encoding='utf-8'))
    z['名称'] = zh
    z['角标'] = badge
    z['数值'] = stats
    z['备注'] = z.get('备注', '') + f';行254正名:旧{zold}实为{newen},f05格{cell}实读'
    json.dump(z, open(os.path.join(ZH, znew), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    os.remove(zp)
    print(f'{old} -> {newen}/{zh} done')

for newen, zh, cell, badge, stats, fx in NEWS:
    d = {'角色': 'Feylana', '角标': badge, '名称': newen, '卡类': '风格', '系列': '流浪者篇-WAN',
         '数值': stats, '效果': fx, '来源': SRC,
         '备注': f'行254 f05格{cell}卡面实读补录(此前漏录);英文卡名装饰字体实读'}
    json.dump(d, open(os.path.join(EN, f'风格_{newen}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    z = {'角色': '菲拉娜', '系列': '流浪者篇-WAN', '来源': SRC, '名称': zh, '卡类': '风格',
         '角标': badge, '数值': stats,
         '效果': [{'时点': e['时点'], '条件': e['条件'], '效果': ''} for e in fx],
         '备注': f'行254补录,f05格{cell};英文:{newen};译文待译'}
    # 译文:照效果行机翻占位,标待译
    zhfx = {'PROFESSIONAL': ['<b>展示：</b>缚约区每有 1 张卡，<i-sb>+1 速度</i-sb>，至多 +3。',
                             '<g-b>结束：</g-b>前进 1-2。'],
            'ATHLETIC': ['<bl-b>前置：</bl-b>前进 1。',
                         '<r-b>命中：</r-b>推动或拉动 0-X。X 为缚约区中卡的数量。']}
    for e, t in zip(z['效果'], zhfx[newen]):
        e['效果'] = t
    json.dump(z, open(os.path.join(ZH, f'风格_{zh}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'new {newen}/{zh}')

# character.json 清单重建
for base, ch in ((EN, 'en'), (ZH, 'zh')):
    p = os.path.join(base, 'character.json')
    c = json.load(open(p, encoding='utf-8'))
    c['卡牌清单'] = sorted(os.path.basename(f) for f in glob.glob(os.path.join(base, '*.json')) if not f.endswith('character.json'))
    c['备注'] = c.get('备注', '') + ';行254五风格正名PROFESSIONAL/METICULOUS/LAWFUL/SERIOUS/ATHLETIC=专家/细致/法定/庄严/矫健'
    json.dump(c, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# draft-final: Feylana 名称替换+补2行
DRAFT = os.path.join(ROOT, 'memory-pending/mt-draft-qwen/draft-final.json')
dd = json.load(open(DRAFT, encoding='utf-8'))
ren = {'Awry': ('LAWFUL', '法定'), 'Serious': ('SERIOUS', '庄严'), 'Showy': ('METICULOUS', '细致')}
for x in dd:
    if x['角色'] == 'Feylana' and x['名称'] in ren:
        x['名称'], x['zh名'] = ren[x['名称']]
dd.extend([
 {'角色': 'Feylana', '卡类': '风格', '名称': 'PROFESSIONAL', 'zh名': '专家', '时点': '展示',
  'en': 'Reveal: +1 Priority per card in the Geas Pile, up to +3.',
  'zh': '展示：缚约区每有 1 张卡，+1 速度，至多 +3。',
  '效果(富文本)': '<b>展示：</b>缚约区每有 1 张卡，<i-sb>+1 速度</i-sb>，至多 +3。'},
 {'角色': 'Feylana', '卡类': '风格', '名称': 'PROFESSIONAL', 'zh名': '专家', '时点': '结束',
  'en': 'End: Advance 1-2.',
  'zh': '结束：前进 1-2。',
  '效果(富文本)': '<g-b>结束：</g-b>前进 1-2。'},
 {'角色': 'Feylana', '卡类': '风格', '名称': 'ATHLETIC', 'zh名': '矫健', '时点': '前置',
  'en': 'Before: Advance 1.',
  'zh': '前置：前进 1。',
  '效果(富文本)': '<bl-b>前置：</bl-b>前进 1。'},
 {'角色': 'Feylana', '卡类': '风格', '名称': 'ATHLETIC', 'zh名': '矫健', '时点': '命中',
  'en': 'Hit: Push or Pull 0-X. X is the number of cards in the Geas Pile.',
  'zh': '命中：推动或拉动 0-X。X 为缚约区中卡的数量。',
  '效果(富文本)': '<r-b>命中：</r-b>推动或拉动 0-X。X 为缚约区中卡的数量。'},
])
json.dump(dd, open(DRAFT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('draft:', len(dd))
