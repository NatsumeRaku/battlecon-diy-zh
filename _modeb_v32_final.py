# 模式B·首领剧本 — 驱动v3(2026-11-22总汇实装UA势不可挡之力)
# v3变更:①Boss能量经济(开局2/循环+1/≤7生命再+1/上限10,自公共池) ②架势池=3激活+1预备(1v2:敌方2+1=3激活,默认预备就绪)
# ③投注换防(1能量:换下上一回合被破的架势,预备架势满韧上场,附属套路随迁) ④广域架势限定投注(+1~2距,1能量) ⑤身后2格禁入(1D无感,记state['no_entry']=2)
# 注:均衡架势+2速限定投注在本引擎无速度赛道,暂不生效(诚实记录)
# 裁定要点: 回避只挡"以谨慎为目标的攻击"(检查距离时点); 英雄必须选一张架势为目标;
# 谨慎回避=明置信息, AI回避生效中不选它; 任意架势被破→谨慎回避条件失效; 击破=累计伤害vs各架势韧
EVADE_MODE = 'softlock'   # 默认=读法1字面(裁定); 'once'/'no_break'仅作对照

STANCES_2P = {'就绪': dict(spd=1, res=0), '广域': dict(spd=2, res=4), '谨慎': dict(spd=0, res=4), '均衡': dict(spd=3, res=4)}
ROUTINES_2P = {
    '威压': dict(rng=1, rng_max=1, power=4, must=True, hit_push=1),
    '烈爪': dict(rng=2, rng_max=4, power=3),
    '龙焰咬': dict(rng=2, rng_max=2, power=6),
    '反冲': dict(rng=2, rng_max=3, power=0),
    '禁词': dict(rng=1, rng_max=3, power=3, group=True),
    '鞭尾': dict(rng=1, rng_max=6, power=0, group=True),
    '撼地': dict(rng=1, rng_max=3, power=3, group=True),
    '动能脉冲': dict(rng=1, rng_max=1, power=3, hit_push=3),
}

def boss_plan_burman(boss, heroes, state, hand):
    alive = [h for h in heroes if h.life > 0]
    plan = {}
    tgt_close = min(alive, key=lambda h: abs(boss.pos - h.pos))
    active = state.get('active_stances', ['均衡', '广域', '谨慎'])
    # 威压必设:放到第一张激活架势
    plan[active[0]] = ('威压', tgt_close.name)
    rest = [r for r in hand if r != '威压'][:2]
    for st, r in zip(active[1:], rest):
        plan[st] = (r, tgt_close.name)
    # 广域限定投注:距1以上够不着时,1能量+1~2距(本引擎射程即战力)
    if '广域' in plan and state.get('boss_e', 0) >= 1:
        d = min(abs(boss.pos - h.pos) for h in alive)
        r = ROUTINES_2P[plan['广域'][0]]
        if d > r['rng_max']:
            state['boss_e'] -= 1; state['gw_anted'] = True
            plan['广域'] = plan['广域'] + ('+dist',)
        else:
            plan['广域'] = plan['广域'] + ('',)
    else:
        for st in plan:
            plan[st] = plan[st] + ('',)
    return plan

def hero_target_stance(plan, broken, cautious_evade):
    """英雄选架势目标(公开信息): 回避生效中的谨慎=不选; 优先最低韧(好破)"""
    cands = [s for s in plan if s not in broken]
    if cautious_evade:
        cands = [s for s in cands if s != '谨慎']
    if not cands:
        cands = [s for s in plan if s not in broken] or list(plan.keys())
    return min(cands, key=lambda s: STANCES_2P[s]['res'])

def play_boss_burman(seed, h1_name, h2_name, verbose=False):
    global rng
    rng = random.Random(seed)
    pool = [65]
    B = Fighter('伯尔曼', life=50, pos=6)
    H1 = mk(h1_name, 2); H2 = mk(h2_name, 3)
    state = {'伯尔曼': B, h1_name: H1, h2_name: H2, 'worm': set(), 'portal': None,
             'range_plus': {}, 'points': {}, 'boss_armor': 0}
    log = []; beat_no = 0
    hand = list(ROUTINES_2P.keys()); cooldown = []
    boss_e = 2; state['boss_e'] = boss_e
    state['active_stances'] = ['均衡', '广域', '谨慎']; state['reserve_stances'] = ['就绪']
    state['no_entry'] = 2; state['gw_anted'] = False; state['swaps'] = 0
    last_breaks = 0
    metrics = {'breaks': 0, 'stance_atks': 0, 'evade_rounds': 0, 'armor_gain': 0, 'swaps': 0}
    broken_persist = set(); last_breaks = 0
    while B.life > 0 and (H1.life > 0 or H2.life > 0) and beat_no < 40:
        beat_no += 1
        broken = set(); B._beat_dmg = 0; state['gw_anted'] = False
        alive = [h for h in (H1, H2) if h.life > 0]
        # ③换防投注:上回合有架势被破且有钱→换下破架势(预备满韧上场,附属套路随迁=plan重建自动随迁)
        if state['boss_e'] >= 1 and last_breaks >= 1 and state['reserve_stances']:
            out = None
            for s in state['active_stances']:
                if s in broken_persist: out = s; break
            if out is None: out = state['active_stances'][-1]
            inn = state['reserve_stances'][0]
            state['active_stances'].remove(out); state['active_stances'].append(inn)
            state['reserve_stances'].remove(inn); state['reserve_stances'].append(out)
            state['boss_e'] -= 1; state['swaps'] += 1
            broken_persist.discard(out)
            if verbose: log.append(f'B{beat_no} 换防:换下[{out}]换上[{inn}](余能量{state["boss_e"]})')
        plan = boss_plan_burman(B, alive, state, hand)
        cautious_evade = ('谨慎' in plan) and all(s not in broken for s in plan if s != '谨慎')
        state['_evaded_this_beat'] = False
        # Boss架势攻击
        for sname, (rname, tgt_name, *_) in plan.items():
            if sname in broken: continue
            r = ROUTINES_2P[rname]
            targets = alive if r.get('group') else [state[tgt_name]]
            for h in targets:
                d = abs(B.pos - h.pos)
                rng_max_eff = r['rng_max'] + (2 if (sname == '广域' and state.get('gw_anted')) else 0)
                if r['rng'] <= d <= rng_max_eff:
                    h.life -= r['power']
                    metrics['stance_atks'] += 1
                    log.append(f'B{beat_no} {sname}[{rname}] {"群" if r.get("group") else ""}命中{h.name} {r["power"]} -> {h.life}')
                    if r.get('hit_push'):
                        move_away(h, B.pos, r['hit_push'])
                    if h.life <= 0:
                        log.append(f'  ★{h.name}阵亡')
        # 英雄攻击(带架势目标选择)
        # 板边限制:所有斗士位置clamp到[1,9](官方战场格数)
        for ent in [B, H1, H2]:
            ent.pos = max(1, min(9, ent.pos))
        for h in alive:
            if h.stunned: continue
            cautious_evade_live = ('谨慎' in plan) and ('谨慎' not in broken) and all(s not in broken for s in plan if s != '谨慎')
            tgt_stance = hero_target_stance(plan, broken, cautious_evade_live)
            if h.name in ('雷克森', '亚历克希安'):
                d, n_ = pick_v3(h, CHARS[h.name], B, ALX)
            else:
                d, n_ = pickfor(h.name)(h, CHARS[h.name], B, state)
            st_, bs_, fin, opts = d
            if fin:
                continue
            b = BASES_JIA[bs_]
            card = next(s for s in CHARS[h.name].styles if s.name == st_)
            p = (b.get('power') or 0) + card.power + h.tokens.get('_复仇力', 0)  # 闪避/格挡power=None按0计
            if st_ == '钢铁':
                h.pos = min(h.pos + 2, B.pos - 1)
            elif bs_ == '猛冲':
                h.pos = h.pos + min(2, max(0, B.pos - h.pos - 1))
            elif st_ == '坚定' and opts.get('adv', 0):
                h.pos = h.pos + min(opts['adv'], max(0, B.pos - h.pos - 1))
            elif st_ == '全力' and opts.get('adv', 0):
                h.pos = h.pos + min(1, max(0, B.pos - h.pos - 1))
            dd = abs(h.pos - B.pos)
            rng_min = card.rng if card.rng is not None else b['range'] + getattr(card, 'rng_d', 0)
            rng_max = card.rng_max if card.rng_max is not None else b.get('range_max', b['range']) + getattr(card, 'rng_max_d', 0)
            if not (rng_min <= dd <= rng_max):
                log.append(f'B{beat_no} {h.name}[{st_}]距离不足({dd})'); continue
            # 回避: 仅当以谨慎为目标且其回避生效时(检查距离时点)
            if tgt_stance == '谨慎' and cautious_evade_live:
                metrics['evade_rounds'] += 1
                log.append(f'B{beat_no} {h.name}[{st_}]打谨慎被回避')
                _hero_recycle(h, pool); continue
            # 伤害
            absorbed = 0
            if state['boss_armor'] > 0:
                absorbed = min(p, state['boss_armor'])
                state['boss_armor'] -= absorbed
            dmg = p - absorbed
            B.life -= dmg; B._beat_dmg += dmg
            log.append(f'B{beat_no} {h.name}[{st_}→{tgt_stance}] 造成{dmg}(甲挡{absorbed}) -> Boss{B.life} 累计{B._beat_dmg}')
            if B.life <= 0:
                log.append('  ★伯尔曼被讨伐!')
                return 'heroes', beat_no, metrics
            life_loss(B, 1, log, f'{h.name}联动无视税')
            if B.life <= 0:
                log.append('  ★伯尔曼被讨伐!')
                return 'heroes', beat_no, metrics
            # 击破: 累计伤害vs全部生效架势各自的韧
            for sname in plan:
                if sname in broken: continue
                if B._beat_dmg > STANCES_2P[sname]['res']:
                    broken.add(sname); metrics['breaks'] += 1; broken_persist.add(sname)
                    log.append(f'  ★击破架势{sname}(累计{B._beat_dmg}>韧{STANCES_2P[sname]["res"]})')
                    rname = plan[sname][0]
                    if rname == '鞭尾':
                        state['boss_armor'] += 2; metrics['armor_gain'] += 2
                        log.append('    鞭尾击破: 首领护甲+2')
                    if rname == '反冲':
                        brk = [x for x in broken if x != sname]
                        if brk:
                            h2 = state[plan[brk[0]][1]]
                            if abs(B.pos - h2.pos) <= 3:
                                h2.life -= 6; log.append(f'    反冲击破: {h2.name} 6伤')
                                if h2.life <= 0: log.append(f'  ★{h2.name}阵亡')
            _hero_recycle(h, pool)
        last_breaks = len(broken)
        # ①Boss能量循环:循环+1,≤7生命再+1,上限10,自公共池
        gain = 1 + (1 if B.life <= 7 else 0)
        take_e = min(gain, pool[0]); pool[0] -= take_e
        state['boss_e'] = min(10, state['boss_e'] + take_e)
        for sname, (rname, *_) in plan.items():
            if rname != '威压' and rname in hand:
                hand.remove(rname); cooldown.append(rname)
        if cooldown and len(cooldown) >= 2:
            hand.append(cooldown.pop(0))
        alive2 = [h for h in (H1, H2) if h.life > 0]
        if len(alive2) == 1 and not alive2[0].tokens.get('_复仇'):
            alive2[0].tokens['_复仇'] = True; alive2[0].tokens['_复仇力'] = 1
            log.append(f'  ★复仇牌: {alive2[0].name}')
        Rf = next((h for h in (H1, H2) if h.name == '雷克森' and h.life > 0), None)
        if Rf:
            ctx2 = build_ctx(Rf, B, log); ctx2.update(self=Rf, opp=B)
            ctx2['ante_curses'] = 0
            if RX.on_recycle: RX.on_recycle(Rf, B, ctx2)
    return ('draw' if B.life > 0 else 'heroes'), beat_no, metrics

def _hero_recycle(h, pool):
    take = 1 + (1 if h.life <= 7 else 0) + (2 if h.tokens.get('_复仇') else 0)
    t = min(take, pool[0]); pool[0] -= t; h.energy = min(20, h.energy + t)
    h.stunned = False; h._beat_dmg = 0
    h.tokens.pop('_骑士增', None); h.tokens.pop('_诅咒削', None)
