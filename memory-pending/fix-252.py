# -*- coding: utf-8 -*-
# 行252: 官方中文实卡照片大浪修正
import json, os, glob, re

ROOT = r'D:\Arkham Horror PSD\BattleConDB\battlecon-diy-zh'
DRAFT = os.path.join(ROOT, 'memory-pending/mt-draft-qwen/draft-final.json')

# 全局替换(顺序敏感,长的在前)
REPL = [
    ('愿望已投注', '愿望被投注'),
    ('愿望未实现', '愿望未被实现'),
    ('咒约堆', '缚约区'),
    ('标靶', '目标'),
    ('幽魂', '魂奴'),
    ('机能', '嵌板'),
    ('场地边缘', '战场的边缘格'),
    ('若如此，', '若你如此做，'),
    ('变为落地', '变为地面'),
    ('，落地：', '，地面：'),
    ('落地', '地面'),
    ('持有', '拥有'),
    ('荆棘', '毒刺'),
    ('冰霜', '冻霜'),
]

def apply_repl(s):
    for a, b in REPL:
        s = s.replace(a, b)
    return s

# ---------- 1. draft-final ----------
d = json.load(open(DRAFT, encoding='utf-8'))
for x in d:
    for k in ('zh', '效果(富文本)'):
        if k in x and isinstance(x[k], str):
            x[k] = apply_repl(x[k])

# Anya: Sundowner Dropkick 两条错标为UA -> 终结技α 落日飞身踢
for x in d:
    if x['角色'] == 'Anya' and x['名称'] == 'Sundowner Dropkick' and x['卡类'] == '特技(UA)':
        x['卡类'] = '终结技'
        x['名称'] = 'Sundowner Dropkick'
        x['zh名'] = '落日飞身踢'
# Kora Barbed 官方句式(照片2实锤)
for x in d:
    if x['角色'] == 'Kora' and x['名称'] == 'Barbed' and x.get('时点') == '展示':
        x['zh'] = '展示：本回合中每有 1 毒刺被消耗，就 +1 威力。'
        x['效果(富文本)'] = '<b>展示：</b>本回合中每有 1 毒刺被消耗，就<i-sb>+1 威力</i-sb>。'
    if x['角色'] == 'John' and x['名称'] == 'Fracturing':
        x['zh'] = '命中：尽可能推动 0-3。每推动 1 格就 -1 威力。'
        x['效果(富文本)'] = '<r-b>命中：</r-b>尽可能推动 0-3。每推动 1 格就<i-sb>-1 威力</i-sb>。'
    if x['角色'] == 'Rin' and x['名称'] == 'Stealthiest' and x.get('时点') == '命中' and '冻霜 2+' in x['zh']:
        x['zh'] = '命中，拥有 2+ 冻霜：护甲 2。'
        x['效果(富文本)'] = '<r-b>命中，拥有 2+ 冻霜：</r-b><b>护甲 2</b>。'

# 新增行
new_rows = [
 # Anya UA 展翅翱翔(照片9实锤)
 {'角色':'Anya','卡类':'特技(UA)','名称':'[UA英文名待核]','zh名':'展翅翱翔','时点':'',
  'en':'Anya switches between Flying and Grounded forms.',
  'zh':'安雅会在飞行与地面形态间切换。',
  '效果(富文本)':'安雅会在飞行与地面形态间切换。'},
 {'角色':'Anya','卡类':'特技(UA)','名称':'[UA英文名待核]','zh名':'展翅翱翔','时点':'',
  'en':'Setup: You are Grounded.',
  'zh':'初始设置：你处于地面。',
  '效果(富文本)':'<b>初始设置：</b>你处于地面。'},
 {'角色':'Anya','卡类':'特技(UA)','名称':'[UA英文名待核]','zh名':'展翅翱翔','时点':'',
  'en':'Ante: Become Flying or Grounded. After becoming Grounded, you have -1 Power this beat.',
  'zh':'限定投注：变为飞行或地面。在变为地面后，你在本回合中拥有 -1 威力。',
  '效果(富文本)':'<b>限定投注：</b>变为<i-sb>飞行</i-sb>或<i-sb>地面</i-sb>。在变为地面后，你在本回合中拥有<i-sb>-1 威力</i-sb>。'},
 # Anya 终结技β面(照片6,卡名装饰字体待识)
 {'角色':'Anya','卡类':'终结技','名称':'[β面卡名待核]','zh名':'[待核]','时点':'开始',
  'en':'This attack cannot hit the opponent. Start: Advance or Retreat 1-3. If you moved past the opponent, avoid the opponent\'s attack.',
  'zh':'本攻击无法命中对手。开始：前进或后退 1-3。若你移动越过对手，回避对手的攻击。',
  '效果(富文本)':'本攻击无法命中对手。<g-b>开始：</g-b>前进或后退 1-3。若你移动越过对手，回避对手的攻击。'},
 # Cionaodh 老练(f05格7,照片4)
 {'角色':'Cionaodh','卡类':'风格','名称':'Veteran[待核]','zh名':'老练','时点':'结束',
  'en':'End, Optional: Reverse the direction of the Motorcycle.',
  'zh':'结束，可选：倒转摩托的方向。',
  '效果(富文本)':'<g-b>结束，可选：</g-b>倒转摩托的方向。'},
 # Wendy 终结技 自由开火！β面(照片8实锤)
 {'角色':'Wendy','卡类':'终结技','名称':'[β面英文名待核]','zh名':'自由开火！','时点':'',
  'en':'"Where\'s my air support?!" Armor 2. Targets Chip 2 (instead of Chip 1).',
  'zh':'“我的空中支援在哪儿?!”护甲 2。目标造成削命 2（取代原本的削命 1）。',
  '效果(富文本)':'“我的空中支援在哪儿?!”<b>护甲 2</b>。目标造成削命 2（取代原本的削命 1）。'},
 {'角色':'Wendy','卡类':'终结技','名称':'[β面英文名待核]','zh名':'自由开火！','时点':'前置',
  'en':'Before: Place Target C on your space. Shift each Target 1-2.',
  'zh':'前置：将目标 C 放置到你的所在格。将每个目标转移 1-2。',
  '效果(富文本)':'<bl-b>前置：</bl-b>将目标 C 放置到你的所在格。将每个目标转移 1-2。'},
]
d.extend(new_rows)
json.dump(d, open(DRAFT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('draft-final:', len(d), '条')

# ---------- 2. zh 树 ----------
ZH = os.path.join(ROOT, 'json-db/zh/流浪者篇-WAN')
CHAR_ZH = {'Anva':'安瓦','Anya':'安雅·南风','Cionaodh':'希尔纳奥','Dajin':'达奎',
           'Feylana':'菲拉娜','John':'约翰','Kai':'凯','Kora':'科拉','Rin':'凛',
           'Vekyl':'维凯尔','Wendy':'温迪'}
# 文件重命名: (角色, 旧文件名) -> 新文件名
REN = {
 ('Anya','特技(UA)_落日飞踢.json'): None,  # 删除,错标
 ('Anya','风格_顺风.json'): '风格_腾空.json',
 ('John','风格_碎裂.json'): '风格_碎压.json',
 ('John','风格_山崩.json'): '风格_塌方.json',
 ('John','特技(UA)_血肉石化.json'): '特技(UA)_血肉成石.json',
 ('John','终结技_血肉石化.json'): '终结技_血肉成石.json',
 ('Dajin','特技(UA)_愿望成真.json'): '特技(UA)_黄粱美梦.json',
 ('Dajin','风格_精妙.json'): '风格_精湛.json',
 ('Dajin','风格_诡诈.json'): '风格_奸诈.json',
 ('Rin','风格_凝冰.json'): '风格_冰结.json',
 ('Kora','风格_倒刺.json'): '风格_钩刺.json',
 ('Cionaodh','风格_大胆.json'): '风格_大胆一博.json',
 ('Vekyl','特技(UA)_幽魂猛袭.json'): '特技(UA)_魂奴猛袭.json',
}
# 全局文本替换所有卡档
for p in glob.glob(ZH + '/**/*.json', recursive=True):
    s = open(p, encoding='utf-8').read()
    ns = apply_repl(s)
    if ns != s:
        open(p, 'w', encoding='utf-8').write(ns)

for (ch, old), new in REN.items():
    p = os.path.join(ZH, ch, old)
    if not os.path.exists(p):
        print('!! missing', p); continue
    if new is None:
        os.remove(p); print('del', old)
    else:
        os.rename(p, os.path.join(ZH, ch, new)); print('ren', old, '->', new)

# 新卡档
def wj(ch, fn, obj):
    json.dump(obj, open(os.path.join(ZH, ch, fn), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('new', fn)

SRC = '官方实卡（TTS图包）'
wj('Anya', '终结技_落日飞身踢.json', {
 '角色':'Anya','系列':'流浪者篇-WAN','来源':SRC,
 '备注':'行252 官方实卡照片实锤:原误标为特技(UA),实为终结技α;英文:Sundowner Dropkick',
 '名称':'落日飞身踢','卡类':'终结技',
 '效果':[
  {'时点':'','条件':'','效果':'“没有恶人能跑过正义之影！”'},
  {'时点':'命中','条件':'','效果':'<r-b>命中：</r-b>尽可能推动。尽可能逼近。[待核:OCR连行,两动作句界待卡面复核]'}]})
wj('Anya', '特技(UA)_展翅翱翔.json', {
 '角色':'Anya','系列':'流浪者篇-WAN','来源':SRC,
 '备注':'行252 官方实卡照片9实锤补录,UA原文整组此前漏录;英文卡名待核',
 '名称':'展翅翱翔','卡类':'特技(UA)',
 '效果':[
  {'时点':'','条件':'','效果':'安雅会在飞行与地面形态间切换。'},
  {'时点':'','条件':'','效果':'<b>初始设置：</b>你处于地面。'},
  {'时点':'','条件':'','效果':'<b>限定投注：</b>变为<i-sb>飞行</i-sb>或<i-sb>地面</i-sb>。在变为地面后，你在本回合中拥有<i-sb>-1 威力</i-sb>。'}]})
wj('Anya', '终结技_[β面名待核].json', {
 '角色':'Anya','系列':'流浪者篇-WAN','来源':SRC,
 '备注':'行252 照片6实锤β面,卡名装饰字体待识; beta面',
 '名称':'[待核]','卡类':'终结技',
 '效果':[{'时点':'开始','条件':'','效果':'本攻击无法命中对手。<g-b>开始：</g-b>前进或后退 1-3。若你移动越过对手，回避对手的攻击。'}]})
wj('Cionaodh', '风格_老练.json', {
 '角色':'Cionaodh','系列':'流浪者篇-WAN','来源':SRC,
 '备注':'行252 照片4实锤补录(f05格7),此前漏录;英文Veteran[待核];数值照实卡',
 '名称':'老练','卡类':'风格',
 '数值':{'距离':'+2~3','威力':'+2','速度':'+1','韧性':'+1'},
 '效果':[{'时点':'结束','条件':'可选','效果':'<g-b>结束，可选：</g-b>倒转摩托的方向。'}]})
wj('Wendy', '终结技_自由开火!.json', {
 '角色':'Wendy','系列':'流浪者篇-WAN','来源':SRC,
 '备注':'行252 照片8实锤β面;英文卡名待核; beta面',
 '名称':'自由开火！','卡类':'终结技',
 '效果':[
  {'时点':'','条件':'','效果':'“我的空中支援在哪儿?!”<b>护甲 2</b>。目标造成削命 2（取代原本的削命 1）。'},
  {'时点':'前置','条件':'','效果':'<bl-b>前置：</bl-b>将目标 C 放置到你的所在格。将每个目标转移 1-2。'}]})

# character.json 更新
for ch, zh in CHAR_ZH.items():
    p = os.path.join(ZH, ch, 'character.json')
    c = json.load(open(p, encoding='utf-8'))
    old_zh = c.get('名称', '')
    c['名称'] = zh
    c['角色'] = zh
    c['备注'] = c.get('备注', '') + ';行252官方中文实卡修正中文名:' + old_zh
    c['卡牌清单'] = sorted(os.path.basename(f) for f in glob.glob(os.path.join(ZH, ch, '*.json')) if not f.endswith('character.json'))
    json.dump(c, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('char', ch, old_zh, '->', zh)
print('done')
