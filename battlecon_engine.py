
# ============ 策略层 ============
MOVE_OPTS = {
    '肃清': [dict()], '不屈': [dict()], '自负': [dict()], '削弱': [dict()],
    '威猛': [dict(retreat=0), dict(retreat=1)], '全力': [dict(adv=0), dict(adv=1)],
    '王者': [dict()], '钢铁': [dict()], '坚定': [dict(adv=0), dict(adv=2)],
    '帝王的': [dict(pull_n=p) for p in (0, 1, 2, 3)],
    '猛冲': [dict(adv=1), dict(adv=2)], 'default': [dict()],
}

rng = random.Random(42)
_obd2 = {}
def opp_best_ch(opp_pos, me_pos, opp_ch_obj, held=0):
    key = (opp_pos, me_pos, opp_ch_obj.name, held)
    if key in _obd2: return _obd2[key]
    best = 0
    for st in opp_ch_obj.styles:
        for bs in BASES_PICK:
            if bs not in BASES: continue
            for opts in MOVE_OPTS.get(st.name, MOVE_OPTS['default'])[:1]:
                opts2 = dict(opts)
                if bs == '猛冲': opts2 = dict(opts2, adv=1)
                fake = Fighter('opp', pos=opp_pos)
                fake.tokens = {'诅咒_持有': held} if opp_ch_obj.name == '雷克森' else {}
                d, _ = est_damage(fake, opp_ch_obj, Fighter('me', pos=me_pos), (st.name, bs, None, opts2))
                if st.name == '不屈' and opp_ch_obj.name == '雷克森' and held >= 3:
                    d = 0
                best = max(best, d)
    _obd2[key] = best
    return best

def est_damage(att, att_ch, dfn, decl):
    st, bs, fin, opts = decl
    tok = att.tokens.get('_骑士增', [0, 0]) if att.name == '雷克森' else [0, 0]
    cur = att.tokens.get('_诅咒削', [0, 0]) if att.name == '亚历克希安' else [0, 0]
    if fin:
        face = att_ch.finishers[fin]
        p = face['power'] + tok[0] - cur[0]
        return (p if face['range'] <= dist(att.pos, dfn.pos) <= face['range_max'] else 0), None
    card = next(s for s in att_ch.styles if s.name == st)
    b = BASES.get(bs)
    if bs in ('闪避', '格挡'): return 0, card
    p = b['power'] + card.power + tok[0] - cur[0]
    rng_min = card.rng if card.rng is not None else b['range'] + getattr(card, 'rng_d', 0)
    rng_max = card.rng_max if card.rng_max is not None else b.get('range_max', b['range']) + getattr(card, 'rng_max_d', 0)
    if st == '坚定' and opts.get('adv', 0) >= 2 and att.pos != dfn.pos: p += 2
    if st == '帝王的' and opts.get('pull_n', 0): p -= opts['pull_n']
    pos = sim_pos(att.pos, dfn.pos, st, bs, opts)
    d = abs(pos - dfn.pos)
    return (p if rng_min <= d <= rng_max else 0), card

def sim_pos(f_pos, opp_pos, st_name, bs, opts):
    fake = Fighter('sim', pos=f_pos)
    if st_name == '钢铁':
        close(fake, opp_pos, 2)
    elif st_name == '坚定' and opts.get('adv', 0) >= 2 and f_pos != opp_pos:
        move_toward(fake, opp_pos, opts['adv'])
    elif st_name == '全力' and opts.get('adv', 0):
        move_toward(fake, opp_pos, 1)
    elif st_name == '威猛' and opts.get('retreat', 0):
        move_away(fake, opp_pos, 1)
    elif st_name == '暴怒' and opts.get('adv', 0):
        move_toward(fake, opp_pos, opts['adv'])
    if bs == '猛冲':
        move_toward(fake, opp_pos, opts.get('adv', 1))
    return fake.pos

def my_pos_after_move(f, opp, decl):
    st, bs, fin, opts = decl
    if fin: return f.pos
    return sim_pos(f.pos, opp.pos, st, bs, opts)

def pick_v3(f, ch, opp, opp_ch):
    is_alex = f.name == '亚历克希安'
    opp_curses = opp.tokens.get('诅咒_持有', 0)
    opp_pos = opp.pos
    opp_is_rexan = opp_ch.name == '雷克森'
    best = None
    for st in ch.styles:
        if st.name not in f.hand_styles: continue
        for bs in [b for b in BASES_PICK if b in f.hand_bases] + (['闪避'] if '闪避' in f.hand_bases else []) + (['格挡'] if '格挡' in f.hand_bases else []):
            for opts in MOVE_OPTS.get(st.name, MOVE_OPTS['default'])[:1]:
                opts = dict(opts)
                if st.name == '帝王的': opts = dict(pull_n=0)
                if bs == '猛冲': opts = dict(opts, adv=opts.get('adv', 1))
                decl = (st.name, bs, None, opts)
                pos_after = my_pos_after_move(f, opp, decl)
                my_dmg, card = est_damage(f, ch, opp, decl)
                ante_cap = min(3, opp_curses)
                for n in range(ante_cap + 1) if is_alex and opp_is_rexan else [0]:
                    held_after = opp_curses - n
                    dmg_n = my_dmg - n
                    if is_alex and held_after >= 3: dmg_n *= 0.4
                    taken = opp_best_ch(opp_pos, pos_after, opp_ch, held_after if opp_is_rexan else 0)
                    evade_bonus = 0
                    if not is_alex and st.name == '不屈' and f.tokens.get('诅咒_持有', 0) >= 3:
                        evade_bonus = opp_best_ch(opp_pos, pos_after, opp_ch, 0)
                    score = dmg_n - 0.85 * taken + card.armor * 0.5 + evade_bonus * 0.9 + rng.random() * 0.01
                    if is_alex and dmg_n > 0 and n == 0 and opp.tokens.get('诅咒_消耗', 0) == 0:
                        score -= 2
                    if best is None or score > best[0]: best = (score, decl, n)
    if not f.finisher_used and f.energy >= f.life and f.life <= 10:
        for face in ch.finishers:
            decl = (min(f.hand_styles, key=lambda s: 1), None, face, {})
            d = ch.finishers[face]['power']
            taken = opp_best_ch(opp_pos, f.pos, opp_ch, 0)
            score = d - 0.85 * taken + 0.8 + rng.random() * 0.01
            if best is None or score > best[0]: best = (score, decl, 0)
    return best[1], best[2]

def pick_kate(f, ch, opp, state):
    best = None
    cand = [s for s in ch.styles if s.name in f.hand_styles]
    if ch.exclusive and ch.exclusive.name in f.hand_styles: cand.append(ch.exclusive)
    for st in cand:
        for bs in [b for b in BASES_PICK if b in f.hand_bases] + (['闪避'] if '闪避' in f.hand_bases else []) + (['格挡'] if '格挡' in f.hand_bases else []):
            for tp in (0, 3, -3):
                opts = dict(tp_target=f.pos + tp) if st.name == '传送' else {}
                decl = (st.name, bs, None, opts)
                worm = state['worm']
                b = BASES.get(bs)
                if bs in ('闪避', '格挡'):
                    dmg = 0
                else:
                    card = st
                    rng_min = b['range'] + card.rng_d
                    rng_max = b.get('range_max', b['range']) + card.rng_max_d
                    p = b['power'] + card.power
                    if st.name == '莫比乌斯':
                        p += sum(1 for w in worm if min(f.pos, opp.pos) < w < max(f.pos, opp.pos))
                    d = eff_dist(f.pos, opp.pos, worm, True)
                    dmg = p if rng_min <= d <= rng_max else 0
                taken = opp_best_ch(f.pos, opp.pos, ALX)
                score = dmg - 0.85 * taken + len(state['worm']) * 0.3 + rng.random() * 0.01
                if best is None or score > best[0]: best = (score, decl, 0)
    if not f.finisher_used and f.energy >= f.life and f.life <= 10:
        d0 = eff_dist(f.pos, opp.pos, state['worm'], True)
        if 6 <= d0 <= 6 or d0 >= 6:
            decl = (min(f.hand_styles, key=lambda s: 1), None, '平面析取', {})
            if best is None or 20 > best[0]: best = (20, decl, 0)
    return best[1], best[2]

def pick_kha(f, ch, opp, state):
    best = None
    cand = [s for s in ch.styles if s.name in f.hand_styles]
    if ch.exclusive and ch.exclusive.name in f.hand_styles: cand.append(ch.exclusive)
    for st in cand:
        for bs in [b for b in BASES_PICK if b in f.hand_bases] + (['格挡'] if '格挡' in f.hand_bases else []):
            for tp in (0, 3, -3):
                for pull in (0, 2, 4):
                    opts = {}
                    if st.name == '传送': opts['tp_target'] = f.pos + tp
                    if st.name == '牵引': opts['pull_n'] = pull
                    decl = (st.name, bs, None, opts)
                    fake = Fighter('k', pos=f.pos)
                    dmg, card = est_damage(fake, ch, opp, decl)
                    if st.name == '传送' and state.get('portal') is not None and portal_between(f.pos, opp.pos, state['portal']):
                        dmg += 3
                    pos_after = f.pos + tp if st.name == '传送' else my_pos_after_move(f, opp, decl)
                    taken = opp_best_ch(pos_after, opp.pos, ALX)
                    score = dmg - 0.8 * taken + rng.random() * 0.01
                    if best is None or score > best[0]: best = (score, decl, 0)
    if not f.finisher_used and f.energy >= f.life and f.life <= 10 and state.get('portal') is not None and opp.pos == state['portal']:
        decl = (min(f.hand_styles, key=lambda s: 1), None, '维度放逐', {})
        if best is None or 30 > best[0]: best = (30, decl, 0)
    return best[1], best[2]

def pick_wen(f, ch, opp, state):
    best = None
    cand = [s for s in ch.styles if s.name in f.hand_styles]
    if ch.exclusive and ch.exclusive.name in f.hand_styles: cand.append(ch.exclusive)
    for st in cand:
        for bs in [b for b in BASES_PICK if b in f.hand_bases] + (['闪避'] if '闪避' in f.hand_bases else []) + (['格挡'] if '格挡' in f.hand_bases else []):
            for adv in ((1, 2) if st.name == '冲刺' else (0,)):
                opts = dict(adv=adv) if st.name == '冲刺' else {}
                decl = (st.name, bs, None, opts)
                fake = Fighter('w', pos=f.pos)
                dmg, card = est_damage(fake, ch, opp, decl)
                if st.name == '炮火':
                    if opp.pos in state['points']: dmg += 3
                    elif any(abs(opp.pos - p) == 1 for p in state['points']): dmg += 2
                taken = opp_best_ch(f.pos, opp.pos, ALX)
                pos_after = f.pos + (1 if opp.pos > f.pos else -1) * adv if st.name == '冲刺' else f.pos
                keep = abs(pos_after - opp.pos)
                score = dmg * 1.0 - 1.1 * taken + card.res * 0.2 + keep * 0.15 + rng.random() * 0.01
                if best is None or score > best[0]: best = (score, decl, 0)
    if not f.finisher_used and f.energy >= f.life and f.life <= 10:
        colo = [c for c, n in state.get('points', {}).items() if n >= 2]
        if colo:
            decl = (min(f.hand_styles, key=lambda s: 1), None, '精准轰炸', {})
            if best is None or 25 > best[0]: best = (25, decl, 0)
    return best[1], best[2]

# ============ 通用对局驱动 ============
CHARS = {'亚历克希安': ALX, '雷克森': RX, '凯特琳': KATE, '温迪': WEN2, '科达斯': KHA}
def pickfor(name):
    return {'亚历克希安': pick_v3, '雷克森': pick_v3, '凯特琳': pick_kate, '温迪': pick_wen, '科达斯': pick_kha}[name]

def mk(name, pos):
    f = Fighter(name, pos=pos, energy=2)
    toks = {'亚历克希安': {'骑士_持有': 1, '骑士_消耗': 2}, '雷克森': {'诅咒_持有': 3, '诅咒_消耗': 0}}
    f.tokens = toks.get(name, {})
    f.hand_styles = {s.name for s in CHARS[name].styles}
    f.hand_bases = set(BASES)
    return f

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
        state.pop('hit_by_先古·观者', None)
        ctx = build_ctx(A, B, log)
        for holder, opp in ((A, B), (B, A)):
            if holder.name == '亚历克希安':
                for _ in range(3):
                    if holder.tokens['骑士_持有'] > 0:
                        ctx.update(self=holder, opp=opp); ALX.ua_ante_hook(holder, opp, ctx)
        declA, nA = pickfor(nameA)(A, CHARS[nameA], B, state)
        declB, nB = pickfor(nameB)(B, CHARS[nameB], A, state)
        # 拆弹(A亚历 vs 雷克森)
        if nA and nameB == '雷克森':
            B.tokens['诅咒_持有'] -= nA; B.tokens['诅咒_消耗'] += nA
            A.tokens['_诅咒削'] = [nA, nA]; ctx['ante_curses'] = nA
        for f, decl in ((A, declA), (B, declB)):
            if decl[2]:
                f.energy -= f.life; f.finisher_used = True
        A.hand_styles.discard(declA[0]); A.hand_bases.discard(declA[1] or '')
        B.hand_styles.discard(declB[0]); B.hand_bases.discard(declB[1] or '')
        decls = {nameA: declA, nameB: declB}
        r = generic_resolve(state, decls, chars, hit_ua, log)
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
    w = 'A' if B.life <= 0 else ('B' if A.life <= 0 else 'draw')
    if verbose:
        print('\n'.join(log))
    return w, beat_no

# ============ 乙型配招循环赛 ============
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

if __name__ == '__main__':
    run_roundrobin(['亚历克希安', '雷克森', '凯特琳', '科达斯', '温迪'], N=50, yi=True)

# ============ 通用结算器 ============
def generic_resolve(state, decls, chars, hit_ua, log):
    A, B = state['A'], state['B']
    worm = state.get('worm', set()); portal = state.get('portal')
    ctx = build_ctx(A, B, log)
    ctx['worm'] = worm; ctx['portal'] = portal; ctx['state'] = state
    sides = {}
    for f in (A, B):
        st, bs, fin, opts = decls[f.name]
        ch = chars[f.name]
        if fin:
            face = ch.finishers[fin]
            card = Card2(fin, rng=face['range'], rng_max=face['range_max'],
                         power=face['power'], speed=face['speed'], res=face['res'], armor=face.get('armor', 0))
            base = None
        else:
            card = next(s for s in ch.styles if s.name == st)
            base = BASES[bs]
        rng_min = card.rng if card.rng is not None else base['range'] + getattr(card, 'rng_d', 0)
        rng_max = card.rng_max if card.rng_max is not None else base.get('range_max', base['range']) + getattr(card, 'rng_max_d', 0)
        sides[f.name] = dict(card=card, base=base, opts=opts, fin=fin,
                             mods=dict(power=0, speed=0, rng_min=rng_min, rng_max=rng_max, opp_power=0, hit_power=0),
                             flags={})
    for f in (A, B):
        s = sides[f.name]
        ctx.update(self=f, opp=(B if f is A else A), mods=s['mods'], flags=s['flags'], **s['opts'])
        fire(s['card'], 'reveal', ctx); fire(s['card'], 'flags', ctx)
    for f in (A, B):
        s = sides[f.name]
        ctx.update(self=f, opp=(B if f is A else A), mods=s['mods'], flags=s['flags'], **s['opts'])
        fire(s['card'], 'advance', ctx)
        if s['base'] is BASES.get('猛冲'):
            move_toward(f, (B if f is A else A).pos, s['opts'].get('adv', 1), worm,
                        f.name == '凯特琳', log, portal if f.name != '科达斯' else None)
    for f in (A, B):
        s = sides[f.name]
        ctx.update(self=f, opp=(B if f is A else A), mods=s['mods'], flags=s['flags'], **s['opts'])
        fire(s['card'], 'start', ctx)
    stats = {}
    for f in (A, B):
        s = sides[f.name]; b = s['base']
        p = (b['power'] if b else 0) + s['card'].power + s['mods']['power'] + s['mods']['hit_power']
        sp = (b['speed'] if b else 0) + s['card'].speed + s['mods']['speed']
        if getattr(f, '_ol_power', False): p += 1
        if getattr(f, '_ol_speed', False): sp += 2
        st_ = f.tokens.get('stance')
        if st_ == '愤怒': p *= 2
        elif st_ == '神格': p *= 3
        if f.name == '科达斯':
            opp = B if f is A else A
            sp += 3 if (portal is not None and opp.pos == portal) else (1 if (portal is not None and abs(opp.pos - portal) == 1) else 0)
        stats[f.name] = dict(power=p, speed=sp,
                             res=(b['res'] if b else 0) + s['card'].res + (2 if getattr(f, '_ol_res', False) else 0),
                             armor=s['card'].armor, fin=s['fin'],
                             stun_immune=s['flags'].get('stun_immune', False))
        f._cur_res = stats[f.name]['res']
    order = sorted([A, B], key=lambda f: -stats[f.name]['speed'])
    if stats[A.name]['speed'] == stats[B.name]['speed']:
        log.append('  【待核】同速Clash暂按双方落空')
    else:
        for att in order:
            dfn = B if att is A else A
            sa, sd = stats[att.name], stats[dfn.name]
            s, sdef = sides[att.name], sides[dfn.name]
            if sdef['flags'].get('evade'):
                log.append(f'  {dfn.name}回避: {att.name}落空'); continue
            if sdef['flags'].get('evade_portal_att') and att.pos == portal:
                log.append(f'  {dfn.name}回避(门上攻击): {att.name}落空'); continue
            if s['base'] is BASES.get('闪避') or s['base'] is BASES.get('格挡'): continue
            if s['fin'] == '维度放逐' and dfn.pos != portal:
                log.append('  维度放逐: 对手不在门上,落空'); continue
            if s['fin'] == '精准轰炸':
                colo = [c for c, n in state.get('points', {}).items() if n >= 2]
                if not colo:
                    log.append('  精准轰炸: 无同存格,落空'); continue
                s['mods']['rng_min'] = s['mods']['rng_max'] = abs(att.pos - colo[0])
            d = eff_dist(att.pos, dfn.pos, worm, att.name == '凯特琳') + state.get('range_plus', {}).get(att.name, 0)
            if not (sa['fin'] or s['mods']['rng_min'] <= d <= s['mods']['rng_max']):
                continue
            p_final = sa['power'] * 3 if s['fin'] == '神格' else sa['power']
            ctx.update(self=dfn, opp=att, mods=sdef['mods'], flags=sdef['flags'], atk_power=p_final)
            fire(sdef['card'], 'on_being_hit', ctx)
            p_final = ctx.get('atk_power', p_final)
            armor = sd['armor'] + sdef['card'].armor
            if s['flags'].get('pierce') or sdef['card'].name == '全力': armor = 0
            ctx.update(self=dfn, opp=att, mods=sdef['mods'], flags=sdef['flags'])
            cap = None
            for e in sdef['card'].effects:
                if e['trigger'] == 'modify_defense':
                    r_ = e['fn'](ctx)
                    if r_ is not None:
                        if sdef['card'].name == '咒言': cap = r_
                        else: armor += r_
            if s['fin'] == '平面析取':
                real = min(max(0, p_final), dfn.life)
                dfn.life -= real
                log.append(f'  平面析取: {dfn.name}失去{real}(现{dfn.life})')
                dfn._beat_dmg += real
                if dfn.life <= 0:
                    log.append('  ★ 生命归零,立即终局'); return 'dead'
                if not stats[dfn.name]['stun_immune']: check_stun(dfn, log)
            else:
                dmg = max(0, p_final - armor)
                if cap is not None and dmg > cap: dmg = cap
                if s['fin'] == '无穷小':
                    state.setdefault('range_plus', {})[dfn.name] = state.get('range_plus', {}).get(dfn.name, 0) + 2
                    log.append(f'  无穷小: {dfn.name}本局距离+2')
                r_ = apply_damage(dfn, dmg, 0, log, f'{att.name}->{dfn.name}')
                if r_ == 'dead': return 'dead'
                if not stats[dfn.name]['stun_immune']: check_stun(dfn, log)
            ctx['hit_' + dfn.name] = True
            state['hit_by_' + att.name] = True
            if att.name == '雷克森': ctx['rexan_hit'] = True
            if dfn.name == '雷克森': ctx['rexan_was_hit'] = True
            ctx.update(self=att, opp=dfn, mods=s['mods'], flags=s['flags'])
            fire(s['card'], 'on_hit', ctx)
            if s['fin'] == '天陨':
                state['no_retreat_' + dfn.name] = True
                log.append(f'  天陨: {dfn.name}下回合无法后退[近似执行]')
            ch_att = chars[att.name]
            if ch_att.on_hit_hook: ch_att.on_hit_hook(att, dfn, ctx)
            if hit_ua.get(dfn.name):
                if hit_ua[dfn.name](dfn, att, ctx) == 'dead': return 'dead'
    for f in (A, B):
        s = sides[f.name]
        ctx.update(self=f, opp=(B if f is A else A), mods=s['mods'], flags=s['flags'], **s['opts'])
        fire(s['card'], 'end', ctx)
        ch = chars[f.name]
        if ch.ua_end:
            ch.ua_end(f, (B if f is A else A), state, log)
    return 'ok'

# ============ 角色: 赛博·凯恩戈特·雷克森 ============
def rexan_hit_ua(R, A, ctx):
    if ctx['ante_curses'] == 0:
        if R.tokens['诅咒_消耗'] > 0:
            R.tokens['诅咒_消耗'] -= 1; R.tokens['诅咒_持有'] += 1
            ctx['log'].append(f'  雷克森被命中无投注: 回收1(持有{R.tokens["诅咒_持有"]})')
        else:
            life_loss(A, 2, ctx['log'], '雷克森UA(满持有)')
            if A.life <= 0: return 'dead'
    return 'ok'

def rexan():
    def ante_curse(f_self, f_opp, ctx):
        if f_self.tokens['诅咒_持有'] <= 0: return 'fail'
        f_self.tokens['诅咒_持有'] -= 1; f_self.tokens['诅咒_消耗'] += 1
        ctx['opp'].tokens.setdefault('_诅咒削', [0, 0])
        ctx['opp'].tokens['_诅咒削'][0] += 1; ctx['opp'].tokens['_诅咒削'][1] += 1
        ctx['ante_curses'] += 1
        ctx['log'].append(f'  投注: {ctx["opp"].name}投1诅咒(-1/-1), 雷克森持有{f_self.tokens["诅咒_持有"]}/消耗{f_self.tokens["诅咒_消耗"]}')
        return 'ok'
    def recycle_hook(f_self, f_opp, ctx):
        if not ctx['rexan_hit'] and not ctx['rexan_was_hit'] and ctx['ante_curses'] > 0:
            f_self.tokens['诅咒_持有'] += ctx['ante_curses']
            ctx['log'].append(f'  雷克森循环回收: {ctx["ante_curses"]}枚回手(持有{f_self.tokens["诅咒_持有"]})')
    styles = [
        Card2('肃清', power=2, effects=[
            E('advance', lambda c: close(c['self'], c['opp'].pos, 6)),
            E('end', lambda c: (c['self'].tokens.__setitem__('诅咒_消耗', c['self'].tokens['诅咒_消耗'] - 1),
                                c['self'].tokens.__setitem__('诅咒_持有', c['self'].tokens['诅咒_持有'] + 1),
                                c['log'].append('  肃清结束: 受5+伤害,回收1诅咒'))
                if c['self']._beat_dmg >= 5 else None),
        ]),
        Card2('不屈', rng=0, rng_max=1, effects=[
            E('reveal', lambda c: (c['flags'].__setitem__('evade', True),
                                   c['log'].append('  不屈展示: 3诅咒,回避攻击'))
                if c['self'].tokens['诅咒_持有'] >= 3 else None),
            E('advance', lambda c: (c['mods'].__setitem__('power', c['mods']['power'] + 2),
                                    c['mods'].__setitem__('rng_max', 6))
                if c['ante_curses'] >= 1 else None),
        ]),
        Card2('自负', effects=[
            E('on_being_hit', lambda c: (c['mods'].__setitem__('atk_power', c['mods']['atk_power'] - 2),
                                          c['log'].append('  自负: 距离1被命中,攻方-2威'))
                if dist(c['self'].pos, c['opp'].pos) == 1 else None),
        ]),
        Card2('帝王的', power=1, res=2, effects=[
            E('reveal', lambda c: c['mods'].__setitem__('speed', c['mods']['speed'] + c['self'].tokens['诅咒_持有'])),
            E('advance', lambda c: (c['mods'].__setitem__('power', c['mods']['power'] - c.get('pull_n', 0)),
                                    move_toward(c['opp'], c['self'].pos, c.get('pull_n', 0)))
                if c.get('pull_n', 0) > 0 else None),
        ]),
        Card2('削弱', speed=-2, res=3, armor=1, effects=[
            E('reveal', lambda c: c['mods'].__setitem__('opp_power', c['mods']['opp_power'] - c['self'].tokens['诅咒_持有'])),
            E('on_hit', lambda c: c['mods'].__setitem__('hit_power', c['mods']['hit_power'] + c['self'].tokens['诅咒_持有'])),
        ]),
    ]
    ex = Card2('咒言', rng=1, rng_max=6, power=4, effects=[
        E('modify_defense', lambda c: 3 if (c['self']._beat_dmg > 3 and c.get('rexan_hit', False)) else None),
    ], exclusive=True)
    fin = {'漆黑星蚀': dict(range=1, range_max=1, power=3, speed=7, res=0),
           '发动时刻': dict(range=0, range_max=99, power=0, speed=0, res=0)}
    return Character('雷克森', ua_ante_hook=ante_curse, styles=styles, exclusive=ex, finishers=fin, on_recycle=recycle_hook)
RX = rexan()

# ============ 角色: 亚历克希安三十七世 ============
def alexian():
    def ante_knight(f_self, f_opp, ctx):
        if f_self.tokens['骑士_持有'] <= 0: return 'fail'
        f_self.tokens['骑士_持有'] -= 1; f_self.tokens['骑士_消耗'] += 1
        ctx['opp'].tokens.setdefault('_骑士增', [0, 0])
        ctx['opp'].tokens['_骑士增'][0] += 1; ctx['opp'].tokens['_骑士增'][1] += 1
        ctx['log'].append(f'  投注: {ctx["opp"].name}投1骑士精神(+1/+1), 亚历持有{f_self.tokens["骑士_持有"]}/消耗{f_self.tokens["骑士_消耗"]}')
        return 'ok'
    def on_hit_gain(f_self, f_opp, ctx):
        if f_self.tokens['骑士_消耗'] > 0 and f_self.tokens['骑士_持有'] < 3:
            f_self.tokens['骑士_消耗'] -= 1; f_self.tokens['骑士_持有'] += 1
            ctx['log'].append(f'  亚历命中: 回收1骑士精神(持有{f_self.tokens["骑士_持有"]})')
    styles = [
        Card2('威猛', rng=0, rng_max=1, power=1, speed=1, res=2, armor=1, effects=[
            E('advance', lambda c: move_away(c['self'], c['opp'].pos, 1) if c.get('retreat', 0) else None),
        ]),
        Card2('坚定', power=1, speed=-3, res=5, effects=[
            E('advance', lambda c: (move_toward(c['self'], c['opp'].pos, c.get('adv', 0)),
                                    c['mods'].__setitem__('power', c['mods']['power'] + 2))
                if c.get('adv', 0) >= 2 and c['self'].pos != c['opp'].pos else None),
        ]),
        Card2('全力', power=2, speed=-1, res=3, effects=[
            E('flags', lambda c: (c['flags'].__setitem__('pierce', True), c['flags'].__setitem__('no_move', True))),
            E('advance', lambda c: move_toward(c['self'], c['opp'].pos, 1) if c.get('adv', 0) else None),
        ]),
        Card2('王者', power=1, speed=1, res=3, effects=[
            E('reveal', lambda c: c['flags'].__setitem__('opp_no_retreat', True)
                if dist(c['self'].pos, c['opp'].pos) == 1 else None),
        ]),
        Card2('钢铁', power=2, speed=-1, res=2, effects=[
            E('advance', lambda c: close(c['self'], c['opp'].pos, 2)),
            E('modify_defense', lambda c: dist(c['self'].pos, c['opp'].pos) - 1),
        ]),
    ]
    ex = Card2('王者之势', power=2, effects=[
        E('advance', lambda c: c['mods'].__setitem__('power', c['mods']['power'] + c.get('adv', 0)) if c.get('adv', 0) > 0 else None),
    ], exclusive=True)
    fin = {'帝国斩击': dict(range=1, range_max=2, power=4, speed=7000, res=0, stun_immune=True, armor=4),
           '重新': dict(range=1, range_max=1, power=4, speed=2, res=0, stun_immune=True, armor=2)}
    return Character('亚历克希安', ua_ante_hook=ante_knight, styles=styles, exclusive=ex, finishers=fin, on_hit_hook=on_hit_gain)
ALX = alexian()

# ============ 角色: 赛博·凯特琳 ============
def kaitlyn():
    def worm_between(state, A, B, log):
        w = (A.pos + B.pos) // 2
        if w in (A.pos, B.pos):
            w = B.pos + (1 if A.pos < B.pos else -1)
        state['worm'].add(w)
        if log is not None: log.append(f'  凯特琳UA: 放虫洞@格{w}(现{len(state["worm"])}枚)')
    styles = [
        Card2('莫比乌斯', rng_d=1, rng_max_d=2, effects=[
            E('flags', lambda c: c['mods'].__setitem__('power', c['mods']['power'] + sum(
                1 for w in c['worm'] if min(c['self'].pos, c['opp'].pos) < w < max(c['self'].pos, c['opp'].pos)))),
            E('end', lambda c: (teleport(c['self'], max(c['worm'], key=lambda w: abs(w - c['opp'].pos)), c['worm'], True, c['log']),
                                c['worm'].discard(c['self'].pos)) if c['worm'] else None),
        ]),
        Card2('远程', rng_d=1, rng_max_d=5, effects=[
            E('flags', lambda c: c['mods'].__setitem__('power', c['mods']['power'] + sum(
                1 for w in list(c['worm']) if 1 <= abs(w - c['self'].pos) <= 5))),
        ]),
        Card2('无限', rng_d=2, rng_max_d=5, effects=[
            E('start', lambda c: worm_between({'worm': c['worm']}, c['self'], c['opp'], c['log'])),
            E('end', lambda c: move_away(c['self'], c['opp'].pos, 1, c['worm'], True, c['log'])),
        ]),
        Card2('公理', rng_d=1, rng_max_d=3, power=1, speed=-1, effects=[
            E('on_hit', lambda c: (c['opp'].__setattr__('pos', max(c['worm'], key=lambda w: abs(w - c['self'].pos))),
                                   c['worm'].discard(c['opp'].pos),
                                   c['log'].append(f'  公理: 对手移至虫洞格{c["opp"].pos}')) if c['worm'] else None),
        ]),
        Card2('悖论', rng_d=0, rng_max_d=2, speed=-1, effects=[
            E('flags', lambda c: (c['opp'].tokens.__setitem__('_悖论', True),
                                  c['log'].append('  悖论: 对手移动效果抑制[近似]'))),
        ]),
    ]
    ex = Card2('传送', rng=1, rng_max=1, power=3, speed=3, effects=[
        E('on_hit', lambda c: (c['flags'].__setitem__('evade', True), c['log'].append('  传送击中: 对手无法命中你'))),
        E('end', lambda c: (c['worm'].add(c['self'].pos),
                            teleport(c['self'], c.get('tp_target', c['self'].pos + 3), c['worm'], True, c['log']))),
    ], exclusive=True)
    fin = {'平面析取': dict(range=6, range_max=6, power=8, speed=11, res=0),
           '无穷小': dict(range=1, range_max=1, power=3, speed=6, res=0)}
    def ua_end(f, opp, state, log):
        if not f.stunned and len(state.get('worm', set())) < 3:
            worm_between(state, f, opp, log)
    return Character('凯特琳', ua_ante_hook=None, styles=styles, exclusive=ex, finishers=fin, ua_end=ua_end)
KATE = kaitlyn()

# ============ 角色: 赛博·科达斯 ============
def khadath():
    styles = [
        Card2('猎手', effects=[
            E('reveal', lambda c: (c['mods'].__setitem__('power', c['mods']['power'] + 2),
                                    c['mods'].__setitem__('speed', c['mods']['speed'] + 2))
                if (c.get('portal') is not None and (c['opp'].pos == c['portal'] or abs(c['opp'].pos - c['portal']) == 1)) else None),
        ]),
        Card2('枯萎', rng_d=0, rng_max_d=2, effects=[
            E('start', lambda c: c['state'].__setitem__('portal', (c['self'].pos + c['opp'].pos) // 2)
                if c.get('portal') is None else None),
        ]),
        Card2('撤离', rng_d=0, rng_max_d=1, speed=-1, effects=[
            E('start', lambda c: (c['state'].__setitem__('portal', c['self'].pos),
                                    move_away(c['self'], c['opp'].pos, 1))),
            E('flags', lambda c: c['flags'].__setitem__('evade_portal_att', True)),
        ]),
        Card2('传送', power=1, speed=-1, effects=[
            E('reveal', lambda c: c['flags'].__setitem__('evade', True)
                if portal_between(c['self'].pos, c['opp'].pos, c.get('portal')) else None),
            E('end', lambda c: (teleport(c['self'], c.get('tp_target', c['self'].pos + 3), None, True, c['log']),
                                c['state'].__setitem__('portal', c.get('portal_target', c['self'].pos)))),
        ]),
        Card2('牵引', rng_d=0, rng_max_d=5, power=-1, effects=[
            E('on_hit', lambda c: move_toward(c['opp'], c['self'].pos, c.get('pull_n', 0), None, True, c['log'])
                if c.get('pull_n', 0) > 0 else None),
        ]),
    ]
    ex = Card2('陷阱', rng=1, rng_max=1, power=3, speed=1, effects=[
        E('flags', lambda c: (c['flags'].__setitem__('pierce', True), c['flags'].__setitem__('stun_immune', True))),
    ], exclusive=True)
    fin = {'位面穿梭': dict(range=1, range_max=2, power=4, speed=5, res=0),
           '维度放逐': dict(range=1, range_max=1, power=25, speed=0, res=0)}
    return Character('科达斯', ua_ante_hook=None, styles=styles, exclusive=ex, finishers=fin)
KHA = khadath()

# ============ 角色: 赛博·温迪 ============
def wendy():
    def end_ua(f, opp, state, log):
        pts = state.get('points', {})
        if not pts: return
        cells = sorted(pts)
        for c in cells:
            for d in cells:
                if c != d and abs(c - d) == 1:
                    pts[d] -= 1
                    if pts[d] == 0: del pts[d]
                    pts[c] = pts.get(c, 0) + 1
                    log.append(f'  温迪结束: 集火点合并@{c}(同存,现{pts[c]}枚)')
                    return
        p = min(pts, key=lambda c: abs(c - opp.pos))
        step = 1 if opp.pos > p else -1
        pts[p] -= 1
        if pts[p] == 0: del pts[p]
        pts[p + step] = pts.get(p + step, 0) + 1
        if p + step == opp.pos:
            opp.pos += step
    styles = [
        Card2('示警', rng_d=0, rng_max_d=2),
        Card2('炮火', rng_d=0, rng_max_d=2, speed=-2, res=4, effects=[
            E('flags', lambda c: c['mods'].__setitem__('power', c['mods']['power'] + (
                3 if c['opp'].pos in c['state']['points'] else (
                    2 if any(abs(c['opp'].pos - p) == 1 for p in c['state']['points']) else 0)))),
        ]),
        Card2('靶向', rng_d=1, rng_max_d=3, speed=1),
        Card2('压制火力', rng_d=0, rng_max_d=1, speed=1, effects=[
            E('flags', lambda c: c['flags'].__setitem__('drain2', True)),
        ]),
        Card2('冲刺', speed=-1, res=2, effects=[
            E('advance', lambda c: move_toward(c['self'], c['opp'].pos, c.get('adv', 1), c['worm'], True, c['log'], c.get('portal'))),
        ]),
    ]
    ex = Card2('扳手击', rng=1, rng_max=2, power=3, speed=4, effects=[
        E('on_hit', lambda c: move_away(c['opp'], c['self'].pos, 1)),
    ], exclusive=True)
    fin = {'精准轰炸': dict(range=-1, range_max=-1, power=9, speed=4, res=0),
           '狂轰滥炸': dict(range=0, range_max=99, power=0, speed=2, res=1)}
    return Character('温迪', ua_ante_hook=None, styles=styles, exclusive=ex, finishers=fin, ua_end=end_ua)
WEN = wendy()
WEN2 = WEN
