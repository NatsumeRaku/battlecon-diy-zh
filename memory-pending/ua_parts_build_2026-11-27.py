# -*- coding: utf-8 -*-
"""行263: UA卡实体组件配件建档（2026-11-27）
依据: 规则书p18-19 + 对照表行117-119三分法 + 行138/149/154/160/163/164/167/168实锤
规范源先行: convention/中英译名对照表.md「行263」节 + 台账行263（已写）
只新增配件档，不改任何官方效果文本（铁律二）。
"""
import os, json

ROOT = r'D:/Arkham Horror PSD/BattleConDB/battlecon-diy-zh/json-db'
NOTE_SRC = 'TTS图包'

# 字段: (系列, en角色, zh角色, 配件中文名, 英文原词, 类别, 数量, 数量待核, 效果句(指示物), 证据备注)
PLAN = [
 # Dravil — TRI 仅 en 树（zh 无试炼篇）
 ('试炼篇-TRI','Dravil',None,'冰','Ice','标记',1,False,'','风格_Resonant卡文"your Ice and Steam Markers";形态标记[待核:无官方先例]'),
 ('试炼篇-TRI','Dravil',None,'蒸汽','Steam','标记',1,False,'','风格_Resonant卡文"your Ice and Steam Markers";形态标记[待核:无官方先例]'),
 # WAN — 标记（行252实锤）
 ('流浪者篇-WAN','Anya','Anya','飞行','Flying','标记',1,False,'','UA"switches between Flying and Grounded forms";行138实锤'),
 ('流浪者篇-WAN','Anya','Anya','地面','Grounded','标记',1,False,'','同上;形态标记'),
 ('流浪者篇-WAN','Cionaodh','Cionaodh','摩托','Motorcycle','标记',1,False,'','UA"Motorcycle marker";行160实锤'),
 ('流浪者篇-WAN','Feylana','Feylana','信念','Conviction','标记',1,True,'','UA"fights with Conviction";行149实锤;数量无明示'),
 ('流浪者篇-WAN','Kora','Kora','毒刺','Thorn','标记',3,False,'','UA"3 Thorn Counters";行163实锤标记(中文实卡优先于英文Counters)'),
 ('流浪者篇-WAN','Rin','Rin','冻霜','Frost','标记',5,False,'','UA"5 Frost Counters";行164实锤标记'),
 ('流浪者篇-WAN','Vekyl','Vekyl','魂奴','Wisp','标记',3,False,'','UA"3 Wisps";行167实锤'),
 ('流浪者篇-WAN','Wendy','Wendy','目标','Target','标记',3,False,'','UA"3 distinct Target Markers";行168实锤;三枚编号目标A/B/C'),
 # WAN — 指示物（token，效果非空）
 ('流浪者篇-WAN','John','John','石肤','Stoneskin','指示物',1,True,
  '使用 1 石肤，使你或对手获得<b>护甲 2</b>，并获得“当该斗士本回合首次将要移动时，阻止该移动。”',
  'UA"Stoneskin Tokens";行154实锤;效果非空;数量无明示'),
 # WAR — 标记
 ('战争篇-WAR','Khadath','科达斯·阿赫缪赛','门径','Gate','标记',1,True,'','UA"Put the Gate in your supply";war-term-map行40;数量无明示'),
 # WAR — 计数物（无固有效果）
 ('战争篇-WAR','Demitras Denigrande','德米特拉斯·德尼格朗德','渐强','Crescendo','计数物',2,False,'','UA"You have 2 Crescendo";war-term-map行37'),
 ('战争篇-WAR','Luc','吕克·冯·戈特','时间','Time','计数物',2,False,'','UA"2 Time. Spend any amount of Time for no effect";war-term-map行42'),
 ('战争篇-WAR','Magdelina','玛格德莉娜·拉灵顿','凝神','Trance','计数物',1,True,'','UA"Deplete all Trance. Regain a Trance";war-term-map行41;数量无明示'),
 # WAR — 指示物（有固有效果）
 ('战争篇-WAR','Cadenza','华彩骑士','护盾','Shield','指示物',3,False,
  '使用 1 护盾（获得眩晕免疫）。被命中时可消耗 1 护盾获得 <i-sb>+99 韧性</i-sb>。',
  'UA"You have 3 Shields. Use a Shield";行110用户裁定'),
 ('战争篇-WAR','Cherri','切莉·塞内卡','洞察','Insight','指示物',1,False,
  '使用洞察（造成激斗。若无法做到则 <i-sb>+2 威力</i-sb>。）',
  'UA"an Insight Token";行1205拟译'),
 ('战争篇-WAR','Heketch','赫凯奇','影步','Shadowstep','指示物',1,False,
  '使用影步（<i-sb>+3 速度</i-sb>。瞬移至对手相邻的任意格。）',
  'UA"a Shadowstep Token";行1206拟译'),
 ('战争篇-WAR','Hikaru','空山光','元素','Element','指示物',4,False,
  '使用元素。火：<i-sb>+3 威力</i-sb>。土：<b>护甲 3</b>。水：<i-sb>-1~+1 距离</i-sb>。风：<i-sb>+2 速度</i-sb>。',
  'UA"4 Elements. Use an Element";有固有效果→指示物'),
 ('战争篇-WAR','Rukyuk','鲁奇优客·安布尔迪恩','弹药','Ammo','指示物',6,False,
  '使用 1 弹药。爆裂：<i-sb>+2 威力</i-sb>。远射：<i-sb>-1~+1 距离</i-sb>。穿甲：<b>无视护甲</b>。迅捷：<i-sb>+2 速度</i-sb>。闪光：<b>无视韧性</b>。冲击：推动 2。',
  'UA"6 Ammo. Use an Ammo";有固有效果→指示物'),
 ('战争篇-WAR','Sagas','萨加斯·塞提斯','镜','Mirror','指示物',1,False,
  '使用镜（获得当前施加于对手的距离、威力、速度与韧性的所有加值与惩罚。不获得投注镜之后施加的加值与惩罚）。',
  'UA"Use Mirror (gain bonuses/penalties)";有固有效果→指示物'),
 ('战争篇-WAR','Vanaah','瓦娜·卡尔莫','神性','Divinity','指示物',1,False,
  '使用神性（<i-sb>+2 威力</i-sb>、<i-sb>+2 速度</i-sb>）。',
  'UA"Use Divinity (+2 Power, +2 Priority)";有固有效果→指示物'),
]

SHAPE = {'标记':'正方形','计数物':'五边形','指示物':'圆形'}

def write_json(path,obj):
    with open(path,'w',encoding='utf-8',newline='\n') as f:
        json.dump(obj,f,ensure_ascii=False,indent=1); f.write('\n')

def main():
    made=[];清单同步=[]
    for series,en_ch,zh_ch,cn_name,en_word,cat,qty,qty_td,effect,ev in PLAN:
        langs=['en'] if zh_ch is None else ['zh','en']
        for lg in langs:
            ch = zh_ch if lg=='zh' else en_ch
            d = os.path.join(ROOT,lg,series,ch)
            if not os.path.isdir(d):
                print('MISSING_DIR',d); continue
            fname = f'配件_{cn_name}.json'
            fp = os.path.join(d,fname)
            if os.path.exists(fp):
                print('SKIP_EXISTS',lg,series,ch,fname); continue
            # en树名称维持中文(配件规范§五);英文原词入备注
            note = f'行263建档;来源注记:{NOTE_SRC};英文原词={en_word};{ev}'
            if qty_td: note += ';[待核:数量无明示,取单数1占位]'
            if en_word in ('Ice','Steam'): note += ';新拟译名无官方先例+官方文本可覆写'
            obj = {
                '角色': ch,
                '名称': cn_name,
                '卡类': '配件',
                '系列': series,
                '类别': cat,
                '效果': effect if cat=='指示物' else '',
                '数量': qty,
                '形状': SHAPE[cat],
                '来源': '官方实卡（TTS图包）',
                '备注': note,
            }
            write_json(fp,obj)
            made.append((lg,series,ch,fname,cat,SHAPE[cat],qty))
            # character.json 清单同步
            cp=os.path.join(d,'character.json')
            if os.path.exists(cp):
                cd=json.load(open(cp,encoding='utf-8'))
                key='卡牌清单'
                if key in cd and isinstance(cd[key],list) and fname not in cd[key]:
                    cd[key].append(fname)
                    write_json(cp,cd)
                    清单同步.append(f'{lg}/{series}/{ch}/character.json')
    print('MADE',len(made))
    for m in made: print('  ',m)
    print('CHAR_SYNC',len(set(清单同步)))

if __name__=='__main__':
    main()
