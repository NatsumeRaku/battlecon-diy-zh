# 引擎扩展: 驱动补丁 + 1v2 + 模式B(2026-11-22)
# 复活协议: exec(core_tmp) + exec(重排body) + exec(本文件) — 全部从磁盘读

# ============ play_generic修补版(策略按签名分派) ============
def play_generic(seed, nameA, nameB, verbose=False):
    global rng
    rng = random.Random(seed)
    pool = [45]
    A, B = mk(nameA, 3), mk(nameB, 5)
    A._opp_ref = B; B._opp_ref = A
    state = {'A': A, 'B': B, 'worm': set(), 'portal': None, 'range_plus': {},
             'points': ({5: 1, 9: 1} if '温迪' in (nameA, nameB) else {})}
    chars = {nameA: CHARS[nameA], nameB: CHARS[nameB]}
    hit_ua = {'雷克森': rexan_hit_ua}
    log = []; beat_no = 0
    while A.life > 0 and B.life > 0 and beat_no < 30:
        beat_no += 1
        state.pop('hit_by_观者', None)
        ctx = build_ctx(A, B, log)
        for holder, opp in ((A, B), (B, A)):
            if holder.name == '亚历克希安':
                for _ in range(3):
                    if holder.tokens['骑士_持有'] > 0:
                        ctx.update(self=holder, opp=opp); ALX.ua_ante_hook(holder, opp, ctx)
        if nameA in ('亚历克希安', '雷克森'):
            declA, nA = pick_v3(A, CHARS[nameA], B, CHARS[nameB])
        else:
            declA, nA = pickfor(nameA)(A, CHARS[nameA], B, state)
        if nameB in ('亚历克希安', '雷克森'):
            declB, nB = pick_v3(B, CHARS[nameB], A, CHARS[nameA])
        else:
            declB, nB = pickfor(nameB)(B, CHARS[nameB], A, state)
        if nA and nameB == '雷克森':
            B.tokens['诅咒_持有'] -= nA; B.tokens['诅咒_消耗'] += nA
            A.tokens['_诅咒削'] = [nA, nA]; ctx['ante_curses'] = nA
        for f, decl in ((A, declA), (B, declB)):
            if decl[2]:
                f.energy -= f.life; f.finisher_used = True
        A.hand_styles.discard(declA[0]); A.hand_bases.discard(declA[1] or '')
        B.hand_styles.discard(declB[0]); B.hand_bases.discard(declB[1] or '')
        r = generic_resolve(state, {nameA: declA, nameB: declB}, chars, hit_ua, log)
        for f, decl in ((A, declA), (B, declB)):
            if decl[0] == '压制火力':
                opp = B if f is A else A
                if opp.pos in state['points']:
                    life_loss(opp, 2, log, '压制火力(进点格)')
                    if opp.life <= 0: r = 'dead'
        if r == 'dead': break
        for f, decl in [(A, declA), (B, declB)]:
            recycle_step(f, CHARS[f.name], decl, pool, log)
            f.tokens.pop('_骑士增', None); f.tokens.pop('_诅咒削', None)
        if '雷克森' in (nameA, nameB):
            Rf = A if A.name == '雷克森' else B
            Of = B if Rf is A else A
            ctx2 = build_ctx(A, B, log); ctx2.update(self=Rf, opp=Of)
            ctx2['ante_curses'] = 0
            if RX.on_recycle: RX.on_recycle(Rf, Of, ctx2)
    return ('A' if B.life <= 0 else 'B' if A.life <= 0 else 'draw'), beat_no

# ============ 乙型循环赛入口(变体#6: 甲/乙自由混组) ============
def run_roundrobin(names, N=50, yi=False):
    global BASES, BASES_PICK
    if yi:
        BASES = SafeBases(BASES_YI)
        BASES_PICK = ('还击', '强打', '发波')
    else:
        BASES = SafeBases(BASES_JIA)
        BASES_PICK = ('猛冲', '强袭', '射击')
    _obd2.clear()
    matrix = {}
    t0 = time.time()
    for i, a in enumerate(names):
        for b in names[i+1:]:
            res = collections.Counter(); beats = []
            for s in range(N):
                w, bn = play_generic(s, a, b)
                res[w] += 1; beats.append(bn)
            matrix[(a, b)] = (res['A']/N, res['B']/N, res['draw']/N, statistics.mean(beats))
    print(f'=== {"乙型" if yi else "甲型"}循环赛 N={N}/对 耗时{time.time()-t0:.0f}s ===')
    for (a, b), (pa, pb, pd, mb) in matrix.items():
        print(f'{a} vs {b}: {pa:.0%} / {pb:.0%} / 平{pd:.0%} (均B{mb:.1f})')
    return matrix

# ============ 超凡(EX)招式池 — 实卡数值 ============
BASES_CHAO = {
    '碎击': dict(range=1, power=5, speed=2, res=3, armor=2),
    '闪击': dict(range=1, power=4, speed=4, res=0, effects=('advance', 2)),
    '滑步': dict(range=0, range_max=0, power=1, speed=7, res=0, effects=('advance', 2)),
    '攫取': dict(range=1, power=3, speed=6, res=0, effects=('on_hit_pull', 1), end_move=1),
    '回击': dict(range=2, range_max=4, power=4, speed=1, res=0, effects=('start_away', 1), end_move=1),
    '魔弹': dict(range=1, range_max=4, power=3, speed=3, res=0, effects=('advance', 1)),
}

# ============ 1v2三人结算器(模式A: 普通斗士+超凡) ============
def resolve_1v2(state, decls, chars, pools, hit_ua, log):
    FS = {n: state[n] for n in decls}
    worm = state.get('worm', set()); portal = state.get('portal')
    vals = list(FS.values())
    ctx = build_ctx(vals[0], vals[1], log)
    ctx['worm'] = worm; ctx['portal'] = portal; ctx['state'] = state
    sides = {}
    for name, f in FS.items():
        st, bs, fin, opts, tgt = decls[name]
        ch = chars[name]
        if fin:
            face = ch.finishers[fin]
            card = Card2(fin, rng=face['range'], rng_max=face['range_max'],
                         power=face['power'], speed=face['speed'], res=face['res'], armor=face.get('armor', 0))
            base = None
        else:
            card = next(s for s in ch.styles if s.name == st)
            base = pools[name][bs]
        rng_min = card.rng if card.rng is not None else base['range'] + getattr(card, 'rng_d', 0)
        rng_max = card.rng_max if card.rng_max is not None else base.get('range_max', base['range']) + getattr(card, 'rng_max_d', 0)
        sides[name] = dict(card=card, base=base, opts=opts, fin=fin, tgt=tgt,
                           mods=dict(power=0, speed=0, rng_min=rng_min, rng_max=rng_max, opp_power=0, hit_power=0),
                           flags={})
    def opp_of(name): return FS[sides[name]['tgt']]
    for name, f in FS.items():
        s = sides[name]
        ctx.update(self=f, opp=opp_of(name), mods=s['mods'], flags=s['flags'], **s['opts'])
        fire(s['card'], 'reveal', ctx); fire(s['card'], 'flags', ctx)
    for name, f in FS.items():
        s = sides[name]
        ctx.update(self=f, opp=opp_of(name), mods=s['mods'], flags=s['flags'], **s['opts'])
        fire(s['card'], 'advance', ctx)
        b = s['base']
        if b and b.get('effects') and b['effects'][0] == 'advance':
            move_toward(f, opp_of(name).pos, b['effects'][1], worm, f.name == '凯特琳', log, portal if f.name != '科达斯' else None)
    for name, f in FS.items():
        s = sides[name]
        ctx.update(self=f, opp=opp_of(name), mods=s['mods'], flags=s['flags'], **s['opts'])
        fire(s['card'], 'start', ctx)
        b = s['base']
        if b and b.get('effects') and b['effects'][0] == 'start_away':
            move_away(f, opp_of(name).pos, b['effects'][1], worm, False, log)
    stats = {}
    for name, f in FS.items():
        s = sides[name]; b = s['base']
        p = (b['power'] if b else 0) + s['card'].power + s['mods']['power'] + s['mods']['hit_power'] + f.tokens.get('_复仇力', 0)
        sp = (b['speed'] if b else 0) + s['card'].speed + s['mods']['speed']
        if getattr(f, '_ol_power', False): p += 1
        if getattr(f, '_ol_speed', False): sp += 2
        stats[name] = dict(power=p, speed=sp,
                           res=(b['res'] if b else 0) + s['card'].res + (2 if getattr(f, '_ol_res', False) else 0),
                           armor=s['card'].armor + (b.get('armor', 0) if b else 0), fin=s['fin'])
        f._cur_res = stats[name]['res']
    order = sorted(FS.values(), key=lambda f: -stats[f.name]['speed'])
    for att in order:
        name = att.name
        dfn = opp_of(name)
        sa, sd = stats[name], stats[dfn.name]
        s, sdef = sides[name], sides[dfn.name]
        if att.stunned:
            log.append(f'  {name}被眩晕,无攻击'); continue
        if sdef['flags'].get('evade'):
            log.append(f'  {dfn.name}回避'); continue
        if sdef['flags'].get('evade_portal_att') and att.pos == portal:
            log.append(f'  {dfn.name}回避(门上攻击)'); continue
        if s['base'] is BASES.get('闪避') or s['base'] is BASES.get('格挡'): continue
        d = eff_dist(att.pos, dfn.pos, worm, att.name == '凯特琳')
        if not (sa['fin'] or s['mods']['rng_min'] <= d <= s['mods']['rng_max']):
            log.append(f'  {name}距离不足({d})'); continue
        p_final = sa['power'] + sdef['mods']['opp_power']
        armor = sd['armor'] + sdef['card'].armor
        dmg = max(0, p_final - armor)
        r_ = apply_damage(dfn, dmg, 0, log, f'{name}->{dfn.name}')
        if r_ == 'dead': return 'dead'
        check_stun(dfn, log)
        state['hit_by_' + name] = True
        ctx.update(self=att, opp=dfn, mods=s['mods'], flags=s['flags'])
        fire(s['card'], 'on_hit', ctx)
        b = s['base']
        if b and b.get('effects') and b['effects'][0] == 'on_hit_pull':
            move_toward(dfn, att.pos, b['effects'][1], worm, False, log)
        ch_att = chars[name]
        if ch_att.on_hit_hook: ch_att.on_hit_hook(att, dfn, ctx)
        if hit_ua.get(dfn.name):
            if hit_ua[dfn.name](dfn, att, ctx) == 'dead': return 'dead'
    for name, f in FS.items():
        s = sides[name]
        ctx.update(self=f, opp=opp_of(name), mods=s['mods'], flags=s['flags'], **s['opts'])
        fire(s['card'], 'end', ctx)
        b = s['base']
        if b and b.get('end_move'):
            move_toward(f, opp_of(name).pos, b['end_move'], worm, False, log)
        ch = chars[name]
        if ch.ua_end: ch.ua_end(f, opp_of(name), state, log)
    return 'ok'

# ============ 1v2驱动(模式A: 超凡Boss/30血) ============
CHAO_PICK = ('碎击', '闪击', '攫取', '回击', '魔弹')

def boss_pick(f, ch, heroes, state):
    tgt = min(heroes, key=lambda h: h.life)
    best = None
    for st in ch.styles:
        if st.name not in f.hand_styles: continue
        for bs in CHAO_PICK:
            if bs not in f.hand_bases: continue
            b = BASES_CHAO[bs]
            p = b['power'] + st.power + f.tokens.get('_复仇力', 0)
            d = abs(f.pos - tgt.pos)
            rng_min = b['range']; rng_max = b.get('range_max', b['range'])
            dmg = p if rng_min <= d <= rng_max else 0
            if b.get('effects') and b['effects'][0] == 'advance':
                d2 = max(0, d - b['effects'][1])
                dmg = p if rng_min <= d2 <= rng_max else dmg
            score = dmg*1.2 + rng.random()*0.01
            if best is None or score > best[0]: best = (score, (st.name, bs, None, dict(), tgt.name))
    return best[1]

def play_1v2(seed, boss_name, h1_name, h2_name, boss_life=30, verbose=False):
    global rng
    rng = random.Random(seed)
    pool = [45]
    B = mk(boss_name, 5); B.hand_bases = set(CHAO_PICK)
    B.life = boss_life; B.max_life = boss_life
    H1 = mk(h1_name, 2); H2 = mk(h2_name, 8)
    state = {boss_name: B, h1_name: H1, h2_name: H2, 'worm': set(), 'portal': None, 'range_plus': {}, 'points': {}}
    if '温迪' in (h1_name, h2_name): state['points'] = {5:1, 9:1}
    pools = {boss_name: SafeBases(BASES_CHAO), h1_name: SafeBases(BASES_JIA), h2_name: SafeBases(BASES_JIA)}
    chars = {boss_name: CHARS[boss_name], h1_name: CHARS[h1_name], h2_name: CHARS[h2_name]}
    hit_ua = {'雷克森': rexan_hit_ua}
    log = []; beat_no = 0
    while B.life > 0 and (H1.life > 0 or H2.life > 0) and beat_no < 40:
        beat_no += 1
        heroes = [h for h in (H1, H2) if h.life > 0]
        ctx = build_ctx(B, heroes[0], log)
        for h in heroes:
            if B.name == '亚历克希安':
                for _ in range(3):
                    if B.tokens['骑士_持有'] > 0:
                        ctx.update(self=B, opp=h); ALX.ua_ante_hook(B, h, ctx)
        declB = boss_pick(B, CHARS[boss_name], heroes, state)
        decls = {boss_name: (declB[0], declB[1], declB[2], declB[3], declB[4])}
        for h in heroes:
            if h.name == '雷克森':
                d, n_ = pick_v3(h, CHARS[h.name], B, CHARS[boss_name])
            else:
                d, n_ = pickfor(h.name)(h, CHARS[h.name], B, state)
            decls[h.name] = (d[0], d[1], d[2], d[3], boss_name)
        for nm, decl in decls.items():
            if decl[2]:
                f = state[nm]; f.energy -= f.life; f.finisher_used = True
            f = state[nm]
            f.hand_styles.discard(decl[0]); f.hand_bases.discard(decl[1] or '')
        r = resolve_1v2(state, decls, chars, pools, hit_ua, log)
        for nm, decl in decls.items():
            if decl[0] == '压制火力' and state[boss_name].pos in state['points']:
                life_loss(state[boss_name], 2, log, '压制火力')
                if state[boss_name].life <= 0: r = 'dead'
        if r == 'dead': break
        for nm, decl in decls.items():
            f = state[nm]
            if f.life <= 0: continue
            gain = 1 + (1 if f.life <= 7 else 0)
            if f.tokens.get('_复仇'): gain += 2
            take = min(gain, pool[0]); pool[0] -= take; f.energy = min(10, f.energy+take)
            recycle_step(f, CHARS[nm], decl[:4], pool, log)
            f.tokens.pop('_骑士增', None); f.tokens.pop('_诅咒削', None)
        heroes2 = [h for h in (H1, H2) if h.life > 0]
        if len(heroes2) == 1 and not heroes2[0].tokens.get('_复仇'):
            heroes2[0].tokens['_复仇'] = True; heroes2[0].tokens['_复仇力'] = 1
            log.append(f'  ★复仇卡: {heroes2[0].name}(+2能量/+1力)')
        Rf = next((h for h in (H1, H2) if h.name == '雷克森' and h.life > 0), None)
        if Rf:
            ctx2 = build_ctx(Rf, B, log); ctx2.update(self=Rf, opp=B)
            ctx2['ante_curses'] = 0
            if RX.on_recycle: RX.on_recycle(Rf, B, ctx2)
    return ('BOSS' if B.life > 0 and all(h.life <= 0 for h in (H1, H2)) else
            'HEROES' if B.life <= 0 else 'draw'), beat_no

# ============ 模式B: 巨龙伯尔曼(官方锁定卡面2026-11-22, 1v2过滤) ============
STANCES_2P = {'就绪': dict(spd=1, res=0), '广域': dict(spd=2, res=4), '谨慎': dict(spd=0, res=4), '均衡': dict(spd=3, res=4)}
ROUTINES_2P = {
    '威压': dict(rng=1, rng_max=1, power=4, must=True, hit_push=1, end_close=1),
    '烈爪': dict(rng=2, rng_max=4, power=3),
    '龙焰咬': dict(rng=2, rng_max=2, power=6),
    '反冲': dict(rng=2, rng_max=3, power=0),
    '禁词': dict(rng=1, rng_max=3, power=3, group=True),
    '鞭尾': dict(rng=1, rng_max=6, power=0, group=True),
    '撼地': dict(rng=1, rng_max=3, power=3, group=True),
    '动能脉冲': dict(rng=1, rng_max=1, power=3, hit_push=3, end_pull_any=3),
}

def boss_plan_burman(boss, heroes, state, hand):
    alive = [h for h in heroes if h.life > 0]
    plan = {}
    stances = ['谨慎', '均衡', '广域']
    tgt_close = min(alive, key=lambda h: abs(boss.pos - h.pos))
    plan['谨慎'] = ('威压', tgt_close.name)
    rest = [r for r in hand if r != '威压'][:2]
    for st, r in zip(['均衡', '广域'], rest):
        plan[st] = (r, tgt_close.name)
    return plan

def play_boss_burman(seed, h1_name, h2_name, verbose=False):
    global rng
    rng = random.Random(seed)
    pool = [65]
    B = Fighter('伯尔曼', life=50, pos=6)
    H1 = mk(h1_name, 2); H2 = mk(h2_name, 3)
    state = {'伯尔曼': B, h1_name: H1, h2_name: H2, 'worm': set(), 'portal': None,
             'range_plus': {}, 'points': {}, 'boss_armor': 0}
    log = []; beat_no = 0
    hand = list(ROUTINES_2P.keys())
    cooldown = []
    metrics = {'breaks': 0, 'stance_atks': 0, 'evade_rounds': 0, 'armor_gain': 0}
    while B.life > 0 and (H1.life > 0 or H2.life > 0) and beat_no < 40:
        beat_no += 1
        broken = set()
        B._beat_dmg = 0
        alive = [h for h in (H1, H2) if h.life > 0]
        plan = boss_plan_burman(B, alive, state, hand)
        cautious_evade = ('谨慎' in plan) and all(s not in broken for s in plan if s != '谨慎')
        for sname, (rname, tgt_name) in plan.items():
            if sname in broken: continue
            r = ROUTINES_2P[rname]
            targets = alive if r.get('group') else [state[tgt_name]]
            for h in targets:
                d = abs(B.pos - h.pos)
                if r['rng'] <= d <= r['rng_max']:
                    dmg = r['power']
                    h.life -= dmg
                    metrics['stance_atks'] += 1
                    log.append(f'B{beat_no} 架势{sname}[{rname}] {"群体" if r.get("group") else ""}命中{h.name} {dmg} -> {h.life}')
                    if r.get('hit_push'):
                        move_away(h, B.pos, r['hit_push'])
                    if h.life <= 0:
                        log.append(f'  ★{h.name}阵亡')
        for h in alive:
            if h.stunned: continue
            if h.name in ('雷克森', '亚历克希安'):
                d, n_ = pick_v3(h, CHARS[h.name], B, ALX)
            else:
                d, n_ = pickfor(h.name)(h, CHARS[h.name], B, state)
            st_, bs_, fin, opts = d
            b = BASES_JIA[bs_] if bs_ else None
            card = next(s for s in CHARS[h.name].styles if s.name == st_)
            p = (b['power'] if b else 0) + card.power + h.tokens.get('_复仇力', 0)
            if st_ == '钢铁':
                h.pos = min(h.pos + 2, B.pos - 1)
            elif bs_ == '猛冲':
                h.pos = h.pos + min(2, max(0, B.pos - h.pos - 1))
            elif st_ == '坚定' and opts.get('adv', 0):
                h.pos = h.pos + min(opts['adv'], max(0, B.pos - h.pos - 1))
            elif st_ == '全力' and opts.get('adv', 0):
                h.pos = h.pos + min(1, max(0, B.pos - h.pos - 1))
            dd = abs(h.pos - B.pos)
            rng_min = card.rng if card.rng is not None else (b['range'] if b else 1)
            rng_max = card.rng_max if card.rng_max is not None else (b.get('range_max', b['range']) if b else 2)
            if not (rng_min <= dd <= rng_max):
                log.append(f'B{beat_no} {h.name}[{st_}]距离不足({dd})'); continue
            if cautious_evade:
                metrics['evade_rounds'] += 1
                log.append(f'B{beat_no} {h.name}[{st_}]被谨慎回避')
                take = 1 + (1 if h.life <= 7 else 0) + (2 if h.tokens.get('_复仇') else 0)
                t = min(take, pool[0]); pool[0] -= t; h.energy = min(20, h.energy + t)
                h.stunned = False; h._beat_dmg = 0
                h.tokens.pop('_骑士增', None); h.tokens.pop('_诅咒削', None)
                continue
            absorbed = 0
            if state['boss_armor'] > 0:
                absorbed = min(p, state['boss_armor'])
                state['boss_armor'] -= absorbed
            dmg = p - absorbed
            B.life -= dmg; B._beat_dmg += dmg
            log.append(f'B{beat_no} {h.name}[{st_}] 造成{dmg}(甲挡{absorbed}) -> Boss{B.life} 累计{B._beat_dmg}')
            life_loss(B, 1, log, f'{h.name}联动无视税')
            if B.life <= 0:
                log.append('  ★伯尔曼被讨伐!')
                return 'heroes', beat_no, metrics
            for sname in plan:
                if sname in broken: continue
                if B._beat_dmg > STANCES_2P[sname]['res']:
                    broken.add(sname); metrics['breaks'] += 1
                    log.append(f'  ★击破架势{sname}(韧{STANCES_2P[sname]["res"]})')
                    rname = plan[sname][0]
                    if rname == '鞭尾':
                        state['boss_armor'] += 2; metrics['armor_gain'] += 2
                        log.append('    鞭尾击破: 首领护甲+2')
                    if rname == '反冲':
                        brk = [x for x in broken if x != sname]
                        if brk:
                            h2 = state[plan[brk[0]][1]]
                            if abs(B.pos - h2.pos) <= 3:
                                h2.life -= 6; log.append(f'    反冲击破: 击破者对{h2.name} 6伤')
                                if h2.life <= 0: log.append(f'  ★{h2.name}阵亡')
            take = 1 + (1 if h.life <= 7 else 0) + (2 if h.tokens.get('_复仇') else 0)
            t = min(take, pool[0]); pool[0] -= t; h.energy = min(20, h.energy + t)
            h.stunned = False; h._beat_dmg = 0
            h.tokens.pop('_骑士增', None); h.tokens.pop('_诅咒削', None)
        for sname, (rname, _) in plan.items():
            if rname != '威压' and rname in hand:
                hand.remove(rname); cooldown.append(rname)
        if cooldown and len(cooldown) >= 2:
            hand.append(cooldown.pop(0))
        alive2 = [h for h in (H1, H2) if h.life > 0]
        if len(alive2) == 1 and not alive2[0].tokens.get('_复仇'):
            alive2[0].tokens['_复仇'] = True; alive2[0].tokens['_复仇力'] = 1
            log.append(f'  ★复仇牌: {alive2[0].name}')
    return ('draw' if B.life > 0 else 'heroes'), beat_no, metrics
