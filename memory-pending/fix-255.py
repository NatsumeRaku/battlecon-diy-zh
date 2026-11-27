# -*- coding: utf-8 -*-
# 行255: WAN批大结构修正——draft旧"特技(UA)"实为终结技α,补真UA+β
import json, os, glob

ROOT = r'D:\Arkham Horror PSD\BattleConDB\battlecon-diy-zh'
DRAFT = os.path.join(ROOT, 'memory-pending/mt-draft-qwen/draft-final.json')
ENW = os.path.join(ROOT, 'json-db/en/流浪者篇-WAN')
ZHW = os.path.join(ROOT, 'json-db/zh/流浪者篇-WAN')
SRC = '官方实卡（TTS图包）'

# (斗士, α英文, α中文, UA英文, UA中文, β英文, β中文)
F = [
 ('Cionaodh','Stealth Takedown','潜行放倒','RIDE OF A LIFETIME','[待译:驰骋一生?]','THE GETAWAY','[待译:脱身?]'),
 ('Dajin','Wish Granted','终有代偿','WISHFUL THINKING','黄粱美梦','PRICE OF POWER','[待译:力量代价?]'),
 ('Feylana','Appeal','呼吁','REGULATION LIMITER','[待译:规章限制?]','CASE CLOSED','[待译:结案?]'),
 ('John','Flesh to Stone','血肉成石','MARRIJANI CURSE','[待译:马里亚尼诅咒?]','BLAST MINING','爆破采矿'),
 ('Kai','Collapsible Box','折叠匣','PUZZLING BOX','[待译:难解之匣?]','FINAL SACRIFICE','[待译:最终牺牲?]'),
 ('Kora','Desert Rose','沙漠玫瑰',"DESERT'S EMBRACE",'[待译:沙漠怀抱?]','QUEEN OF PAIN','[待译:痛苦女王?]'),
 ('Rin','Deep Freeze','深度冻结','FROSTBITE','[待译:霜咬?]',"THE DRAGON'S FROZEN CLAW",'[待译:冰龙之爪?]'),
 ('Vekyl','Spectral Assault','魂奴猛袭','ETERNAL SERVITUDE','[待译:永恒奴役?]','TRANSFIX','[待译:慑魂?]'),
 ('Wendy','Precision Strike','精准打击','AIR SUPPORT','[待译:空中支援?]','FIRE AT WILL','自由开火！'),
]

# UA正文(en, 自读b07+DS摘要, 疑处标[待核])
UA_TXT = {
 'Cionaodh': [('','Cionaodh has a Motorcycle marker, which moves around the arena. As the Motorcycle moves, it can push fighters for extra mobility.[待核]'),
              ('','Setup: Place the Motorcycle in your space. Choose an initial Motorcycle direction.[待核]'),
              ('','Limited Ante: Shift the Motorcycle 1-3 in the direction it faces. If it reaches an edge of the arena, it reverses direction.[待核]'),
              ('','Whenever the Motorcycle leaves your space, Advance or Retreat 0-1 in the same direction it moved.[待核]')],
 'Dajin': [('','Dajin has 6 Wish Cards (opponents may have Wishes too). While he has 3 or more Wishes in play, he becomes Empowered.[待核]'),
           ('','Setup: All Wishes are Active. Dajin is Empowered.[待核]'),
           ('','Ante: 2[待核]')],
 'Feylana': [('','Feylana has a Geas Pile and fights with Conviction. You have Conviction if the opponent\'s attack contains a copy of a card in your Geas Pile.[待核]')],
 'John': [('','John has Stoneskin Tokens, which he uses to grant Armor and prevent movement. He uses these Tokens creatively to restrict opponents\' movement and to protect himself from their attacks.'),
          ('','Setup: You have a Stoneskin. Deplete the remaining Stoneskins.[待核]'),
          ('','Limited Ante: Use a Stoneskin to give yourself or the Opponent Armor 2 and "When this fighter would move for the first time this beat, prevent that movement."'),
          ('结束','End, you moved: Regain a Stoneskin.')],
 'Kai': [('','Kai has 3 Functions, which provide him with various bonuses. By outfitting his attacks with Functions, Kai can customize his attacks.'),
         ('','Setup: All Functions are deactivated.'),
         ('','Ante: Select a Function secretly, then reveal it. If the opponent must guess its name. If the opponent is correct, Kai is Perplexed. Otherwise, activate the Function.[待核]'),
         ('','Perplexed: -1 Priority for each active Function, then deactivate all Functions. You may not ante more Functions this beat.[待核]'),
         ('结束','End: Deactivate all Functions.')],
 'Kora': [('','Kora has 3 Thorn Counters. When she hits an opponent, she gains a Thorn which deals damage over time. The opponent can remove her Thorns, but at a cost to their hand.'),
          ('','Setup: All Thorns are depleted.'),
          ('','Limited Ante: Deplete all Thorns in Kora\'s supply. Discard a Style (it goes to your discard pile alongside your attack pair during Recycle).'),
          ('','Hit: Regain a Thorn.'),
          ('开始','Start: Chip 1 per Thorn in your supply.')],
 'Rin': [('','Rin has 5 Frost Counters. Rin\'s attacks build up Frost, and future attacks are enhanced based on the amount of Frost she holds. If Rin fails to hit an opponent, she loses Frost.'),
         ('','Setup: All Frost is depleted.'),
         ('结束','End, did not hit the Opponent: Deplete 1 Frost.')],
 'Vekyl': [('','Vekyl has 3 Wisps, which haunt the duel in his stead. He places these each beat, and they chase down opponents to inflict damage.'),
           ('','Setup: Place a Wisp on the center of the arena. The remaining Wisps are in your supply.'),
           ('','Limited Ante: Place a Wisp on or adjacent to you (a space cannot ever contain more than 1 Wisp).'),
           ('结束','End: Withdraw a Wisp on an opponent for Chip 1. Starting with the Wisp nearest to the opponent, shift each Wisp 1 towards the opponent, but not onto another Wisp.')],
 'Wendy': [('','Wendy has 3 distinct Target Markers. She moves these around the arena to damage opponents and control their positioning.'),
           ('','Setup: Place Target A on the center of the arena, Target B on the far edge of the arena (behind the opponent), Place Target C in your Depiction Area. It can be placed only by the effect of your Finisher.[待核]'),
           ('','Whenever a Target enters the Opponent\'s space, the Opponent may Advance or Retreat 1 in the direction the Target moved (away from the space the Target left). After this, if the opponent is on a Target, Chip 1.'),
           ('结束','End: Shift a Target 1. (Multiple Targets may occupy the same space.)')],
}

# β数据(en名, zh名, 数值, 效果行[(时点,en,zh)], quote)
BE = {
 'Anya': ('THEME SONG','主题曲[待核]', {'距离':'1~2','威力':'1','速度':'6','韧性':'0'},
          [('', '"Judgment flies on golden wings, as the shadow falls, the tempest sings!"[待核]','“金色的翅膀载着审判飞翔，阴影降临时，风暴歌唱！”[待核]'),
           ('','Ignore Guard','无视韧性'),
           ('命中','Hit: For the rest of the duel, when you become Grounded or Flying, Advance or Retreat 0-3.','命中：此后整场决斗中，当你变为地面或飞行时，前进或后退 0-3。')]),
 'Cionaodh': ('THE GETAWAY','脱身[待核]', {'距离':'N/A','威力':'N/A','速度':'N/A','韧性':'0'},
          [('', '"It\'s nothing personal, just another job.[待核]','“别往心里去，只是又一单生意。”[待核]'),
           ('','This attack cannot hit the opponent.[照官方中文卡]','本攻击无法命中对手。'),
           ('开始','Start: Advance or Retreat 1-3.[待核]','开始：前进或后退 1-3。'),
           ('','If you move past the opponent, avoid the opponent\'s attack.[待核]','若你移动越过对手，回避对手的攻击。'),
           ('结束','End: Teleport on or adjacent to the Motorcycle. Ends: +3 Power next beat.[待核]','结束：瞬移至摩托上或相邻格。下回合开始：+3 威力。[待核]')]),
 'Dajin': ('PRICE OF POWER','力量代价[待核]', {'距离':'2','威力':'4','速度':'4','韧性':'0'},
          [('', '"Your ambition is too weak to wield such power!"[待核]','“你的野心太弱，驾驭不了这样的力量！”[待核]'),
           ('','Ante: Spend any number of Force. Discard that many active Wishes.[待核]','投注：消耗任意数量能量，弃置等量已激活的愿望。[待核]'),
           ('后置','After: Chip 2 per inactive Wish. Activate all Wishes (flip them to the active side, they are not Granted).[待核]','后置：每个未激活的愿望削命 2。激活所有愿望（翻回激活面，愿望未被实现）。[待核]')]),
 'Feylana': ('CASE CLOSED','结案[待核]', {'距离':'1~2','威力':'5','速度':'5','韧性':'0'},
          [('', '"Let\'s move to closing arguments.[待核]','“让我们进入结案陈词。”[待核]'),
           ('伤害','Damage: Pick up any number of Bases from the Geas Pile, then put any number of Bases into the Geas Pile.','伤害：从缚约区拾取任意张招式，然后将任意张招式置入缚约区。')]),
 'John': ('BLAST MINING','爆破采矿', {'距离':'1~3','威力':'8','速度':'0','韧性':'0'},
          [('', '"You might want to stand a little to the side there, friend."','“朋友，你最好往边上站一点。”'),
           ('','Stun Immunity, Ignore Armor','眩晕免疫，无视护甲')]),
 'Kai': ('FINAL SACRIFICE','最终牺牲[待核]', {'距离':'1~2','威力':'1','速度':'4','韧性':'0'},
          [('', '"Be sealed forevermore!"[待核]','“永远封缄！”[待核]'),
           ('展示','Reveal, 5 Functions Active: +15 Power.[待核]','展示，5 个嵌板处于激活：+15 威力。[待核]')]),
 'Kora': ('QUEEN OF PAIN','痛苦女王[待核]', {'距离':'1~3','威力':'9','速度':'4','韧性':'0'},
          [('', '"If you struggle, it will only work faster."','“你越挣扎，它只会生效得越快。”'),
           ('后置','After: Inflict 2 damage per Thorn depleted this beat.','后置：本回合每消耗 1 毒刺，造成 2 伤害。')]),
 'Rin': ("THE DRAGON'S FROZEN CLAW",'冰龙寒爪[待核]', {'距离':'1~3','威力':'7','速度':'5','韧性':'0'},
          [('', '"If only big brother could see me now!"[待核]','“要是大哥现在能看到我就好了！”[待核]'),
           ('展示','Reveal, 3+ Frost held: +1 Power and +2 Priority.[待核]','展示，拥有 3+ 冻霜：+1 威力与+2 速度。[待核]')]),
 'Vekyl': ('TRANSFIX','慑魂[待核]', {'距离':'2~4','威力':'3','速度':'4','韧性':'0'},
          [('', '"Kneel before the master\'s voice!"[待核]','“在主人的声音下跪伏！”[待核]'),
           ('前置','Before: +0~2 Range and +3 Power per Wisp between you and the opponent.[待核]','前置：你与对手之间每有 1 魂奴，+0~2 距离与+3 威力。[待核]')]),
 'Wendy': ('FIRE AT WILL','自由开火！', {'距离':'N/A','威力':'N/A','速度':'N/A','韧性':'2'},
          [('', '"Where\'s my air support?!"','“我的空中支援在哪儿?!”'),
           ('','Armor 2. Targets inflict Chip 2 (instead of the usual Chip 1).','护甲 2。目标造成削命 2（取代原本的削命 1）。'),
           ('前置','Before: Place Target C on you. Shift each Target 1-2.','前置：将目标 C 放置到你的所在格。将每个目标转移 1-2。')]),
}

# ---------- 1. draft-final ----------
d = json.load(open(DRAFT, encoding='utf-8'))
ZHEN = {'Cionaodh','Dajin','Feylana','John','Kai','Kora','Rin','Vekyl','Wendy'}
alpha = {f[0]: (f[1], f[2]) for f in F}
for x in d:
    if x['角色'] in ZHEN and x['卡类'] == '特技(UA)':
        x['卡类'] = '终结技'
        en, zh = alpha[x['角色']]
        x['名称'] = en
        x['zh名'] = zh

# 修正行252误加的"Anya β"(实为Cionaodh的THE GETAWAY):删掉,重挂到Cionaodh
d = [x for x in d if not (x['角色'] == 'Anya' and x['名称'] == '[β面卡名待核]')]
for ch, (been, bezh, stats, rows) in BE.items():
    enname = {'Anya': None}.get(ch)  # Anya β已不存在旧档
    for (t, en, zh) in rows:
        fx = zh
        d.append({'角色': ch, '卡类': '终结技', '名称': been, 'zh名': bezh, '时点': t,
                    'en': en, 'zh': zh, '效果(富文本)': fx})
# UA行
for ch in UA_TXT:
    uan = [f for f in F if f[0] == ch][0]
    for (t, en) in UA_TXT[ch]:
        d.append({'角色': ch, '卡类': '特技(UA)', '名称': uan[3], 'zh名': uan[4], '时点': t,
                  'en': en, 'zh': '[待译] ' + en[:40], '效果(富文本)': en})
json.dump(d, open(DRAFT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('draft:', len(d))

# ---------- 2. en树: α重命名 + 新UA/β档 ----------
for ch, aen, azh, uaen, uazh, been, bezh in F:
    p = os.path.join(ENW, ch)
    old = os.path.join(p, f'特技(UA)_{aen}.json')
    if os.path.exists(old):
        nd = json.load(open(old, encoding='utf-8'))
        nd['卡类'] = '终结技'
        nd['备注'] = nd.get('备注', '') + ';行255正名:旧误标特技(UA),实为终结技α;背面表b07实锤'
        json.dump(nd, open(os.path.join(p, f'终结技_{aen}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        os.remove(old)
        print('en α重命名', ch, aen)
    # UA新档
    ua = {'角色': ch, '角标': '', '名称': uaen, '卡类': '特技(UA)', '系列': '流浪者篇-WAN',
          '效果': [{'时点': t, '条件': '', '效果': e} for (t, e) in UA_TXT[ch]],
          '来源': SRC, '备注': '行255补录(真UA,b07背表实锤);英文卡名装饰字体实读'}
    json.dump(ua, open(os.path.join(p, f'特技(UA)_{uaen}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    # β新档
    been2, bezh2, stats, rows = BE[ch]
    be = {'角色': ch, '角标': '灰八芒星(β)', '名称': been2, '卡类': '终结技', '系列': '流浪者篇-WAN',
          '数值': stats, '效果': [{'时点': t, '条件': '', '效果': e} for (t, e, _z) in rows],
          '来源': SRC, '备注': '行255补录(β面,b07背表实锤);beta面'}
    json.dump(be, open(os.path.join(p, f'终结技_{been2}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('en树UA/β补录完')

# Anya的β
p = os.path.join(ENW, 'Anya')
been2, bezh2, stats, rows = BE['Anya']
be = {'角色': 'Anya', '角标': '灰八芒星(β)', '名称': been2, '卡类': '终结技', '系列': '流浪者篇-WAN',
      '数值': stats, '效果': [{'时点': t, '条件': '', '效果': e} for (t, e, _z) in rows],
      '来源': SRC, '备注': '行255补录(β面THEME SONG,b07背表实锤);行252误挂的photo6文本实为Cionaodh的THE GETAWAY,已纠正;beta面'}
json.dump(be, open(os.path.join(p, f'终结技_{been2}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
# 删行252建的错档
wrong = os.path.join(ZHW, 'Anya', '终结技_[β面名待核].json')
if os.path.exists(wrong):
    os.remove(wrong); print('del wrong anya beta')

# ---------- 3. zh树 ----------
for ch, aen, azh, uaen, uazh, been, bezh in F:
    p = os.path.join(ZHW, ch)
    old = os.path.join(p, f'特技(UA)_{azh}.json')
    if os.path.exists(old):
        nd = json.load(open(old, encoding='utf-8'))
        nd['卡类'] = '终结技'
        nd['备注'] = nd.get('备注', '') + ';行255正名:旧误标特技(UA),实为终结技α(英文' + aen + ')'
        json.dump(nd, open(os.path.join(p, f'终结技_{azh}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        os.remove(old)
    ua = {'角色': ch, '系列': '流浪者篇-WAN', '来源': SRC, '名称': uazh if '待译' not in uazh else uazh,
          '卡类': '特技(UA)', '效果': [{'时点': t, '条件': '', '效果': '[待译]'} for (t, _e) in UA_TXT[ch]],
          '备注': f'行255补录真UA;英文:{uaen};UA中文名待译[待核]'}
    json.dump(ua, open(os.path.join(p, f'特技(UA)_{uazh}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    been2, bezh2, stats, rows = BE[ch]
    be = {'角色': ch, '系列': '流浪者篇-WAN', '来源': SRC, '名称': bezh2, '卡类': '终结技',
          '角标': '灰八芒星(β)', '数值': stats,
          '效果': [{'时点': t, '条件': '', '效果': z} for (t, _e, z) in rows],
          '备注': f'行255补录β面;英文:{been2};beta面'}
    json.dump(be, open(os.path.join(p, f'终结技_{bezh2}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('zh树完')

# Anya β zh
been2, bezh2, stats, rows = BE['Anya']
be = {'角色': '安雅·南风', '系列': '流浪者篇-WAN', '来源': SRC, '名称': bezh2, '卡类': '终结技',
      '角标': '灰八芒星(β)', '数值': stats,
      '效果': [{'时点': t, '条件': '', '效果': z} for (t, _e, z) in rows],
      '备注': f'行255补录β面;英文:{been2};beta面'}
json.dump(be, open(os.path.join(ZHW, 'Anya', f'终结技_{bezh2}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# character.json 重建
for base in glob.glob(os.path.join(ENW, '*', '')) + glob.glob(os.path.join(ZHW, '*', '')):
    cp = os.path.join(base, 'character.json')
    if not os.path.exists(cp):
        continue
    c = json.load(open(cp, encoding='utf-8'))
    c['卡牌清单'] = sorted(os.path.basename(f) for f in glob.glob(os.path.join(base, '*.json')) if not f.endswith('character.json'))
    c['备注'] = c.get('备注', '') + ';行255:真UA+β入档,旧UA误标已正名为终结技α'
    json.dump(c, open(cp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('done')
