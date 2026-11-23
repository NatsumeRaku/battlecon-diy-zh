# 2026-11-23 全库标准化迁移(依据:战链唯一全功能提示词v2 §4.3 钉死规则)
# 规则:①时点"持续"→""直书 ②"每当"条目前缀化+保条件 ③补"条件"键 ④green-triangle→green-tri-down
# ⑤终结α/β角标对象→标准标签 ⑥风格(含升级体)数值int强制带符号str ⑦卡牌清单补.json ⑧删禁存字段
import json, glob, shutil, sys

stats = {}
def bump(k, n=1): stats[k] = stats.get(k, 0) + n

BANNED = {'优先级', '录入方式', '备注', 'last_updated', '版本', '变更记录'}

def norm_value(v):
    # 风格修正值:int→带符号str;str已带符号/区间/占位保持
    if isinstance(v, bool): return v
    if isinstance(v, int): return f'+{v}' if v >= 0 else str(v)
    return v

def norm_stats(d, is_style):
    num = d.get('数值')
    if not isinstance(num, dict): return
    if is_style:
        for k, v in list(num.items()):
            nv = norm_value(v)
            if nv != v: bump('风格数值带符号化'); num[k] = nv
    else:
        # 非风格:str 纯数字(如 "0")转 int
        for k, v in list(num.items()):
            if isinstance(v, str) and v.lstrip('+-').isdigit():
                num[k] = int(v); bump('绝对值str转int')

def norm_effects(d):
    eff = d.get('效果')
    if isinstance(eff, dict):  # 双面终结技
        for face in ('α面', 'β面'):
            for e in eff.get(face) or []:
                fix_effect(e)
        return
    for e in eff or []:
        fix_effect(e)

def fix_effect(e):
    if not isinstance(e, dict): return
    t = e.get('时点')
    if t == '持续':
        e['时点'] = ''; bump('持续→空串直书')
    if t == '每当':
        cond = e.get('条件', '')
        if '每当' not in e.get('效果', ''):
            e['效果'] = f'每当{cond}时:{e.get("效果","")}' if cond else f'每当:{e.get("效果","")}'
            bump('每当前缀化')
        e['时点'] = ''
    if '条件' not in e:
        e['条件'] = ''; bump('补条件键')

def norm_badge(d):
    b = d.get('角标')
    if isinstance(b, dict):
        for face, val in list(b.items()):
            if isinstance(val, str) and '八芒星' in val:
                b[face] = '<star8-alpha>' if 'α' in face or '白' in val else '<star8-beta>'
                bump('终结角标对象→标准标签')
    elif isinstance(b, str):
        if '<green-triangle>' in b:
            d['角标'] = b.replace('<green-triangle>', '<green-tri-down>'); bump('green-triangle改名')

changed_files = 0
for path in glob.glob('json-db/**/*.json', recursive=True):
    d = json.load(open(path, encoding='utf-8'))
    orig = json.dumps(d, ensure_ascii=False, sort_keys=True)
    kind = d.get('卡类', '')
    for k in list(d.keys()):
        if k in BANNED:
            del d[k]; bump('删禁存字段')
    norm_effects(d)
    norm_badge(d)
    norm_stats(d, kind in ('风格', '风格(升级体)'))
    cl = d.get('卡牌清单')
    if isinstance(cl, list):
        new = [x if x.endswith('.json') else x + '.json' for x in cl]
        if new != cl: d['卡牌清单'] = new; bump('清单补.json')
    if json.dumps(d, ensure_ascii=False, sort_keys=True) != orig:
        json.dump(d, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        changed_files += 1

print('改动文件数:', changed_files)
for k, v in sorted(stats.items(), key=lambda x: -x[1]):
    print(f'{k}: {v}')
