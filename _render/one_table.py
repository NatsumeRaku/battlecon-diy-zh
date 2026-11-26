# -*- coding: utf-8 -*-
import io,json,os,sys
name=sys.argv[1]
R='json-db/zh/战争篇-WAR'
TAG={'<p-b>':'**','</p-b>':'**','<g-b>':'**','</g-b>':'**','<bl-b>':'**','</bl-b>':'**','<r-b>':'**','</r-b>':'**','<o-b>':'**','</o-b>':'**','<b>':'**','</b>':'**','<i-sb>':'*','</i-sb>':'*','<i>':'*','</i>':'*'}
DISP={'<red-diamond>':'◇','<orange-pentagon>':'⬠','<yellow-hexagon>':'⬡','<green-tri-down>':'▽','<blue-circle>':'○','<gray-moon>':'⬣','<star8-alpha>':'✳','<star8-beta>':'✴','<initiative>':'▲','<stun-shield>':'⬡'}
def md(s):
    s=str(s)
    for k,v in DISP.items(): s=s.replace(k,v)
    for k,v in TAG.items(): s=s.replace(k,v)
    return s
def load(p): return json.load(io.open(p,encoding='utf-8'))
def stat(v): return f"距离 {md(v.get('距离',''))} / 威力 {v.get('威力','')} / 速度 {md(v.get('速度',''))} / 韧性 {md(v.get('韧性',''))}"
def row(e):
    bg=e.get('背景',''); b=('（'+bg+'）') if bg else ''
    c=(f"[{e['条件']}]") if e.get('条件') else ''
    t=(f"**{e['时点']}**") if e.get('时点') and e.get('时点')!='持续' else ''
    return f"| {t} | {c}{b} | {md(e.get('效果',''))} |"
D=os.path.join(R,name)
c=load(os.path.join(D,'character.json'))
out=[f"# {name}（{c.get('称号','')}）｜{c.get('类型')}/{c.get('难度')}｜机制：{c.get('机制名')}\n\n"]
files=sorted(os.listdir(D))
def order(f):
    for i,k in enumerate(['UA','专属','风格','终结','状态']):
        if k in f: return (i,f)
    return (9,f)
for f in sorted(files,key=order):
    if f=='character.json': continue
    d=load(os.path.join(D,f))
    nm=d.get('名称')
    title=nm if not isinstance(nm,dict) else ' / '.join(nm.values())
    out.append(f"### {title}（{d.get('卡类')}）\n")
    eff=d['效果']; v=d.get('数值')
    if isinstance(eff,dict):
        for side in ('α面','β面'):
            out.append(f"\n**{side}** {nm[side]}　{stat(v[side])}　台词：{d['台词'][side]}\n\n| 时点 | 条件/背景 | 效果 |\n|---|---|---|\n")
            for e in eff[side]:
                if e.get('效果') or e.get('时点'): out.append(row(e)+"\n")
            out.append("\n")
    else:
        if isinstance(v,dict): out.append(f"{stat(v)}\n\n")
        out.append("| 时点 | 条件/背景 | 效果 |\n|---|---|---|\n")
        for e in eff: out.append(row(e)+"\n")
        out.append("\n")
io.open(f'/mnt/agents/output/{name}-表格-2026-11-27.md','w',encoding='utf-8').write(''.join(out))
print(''.join(out))
