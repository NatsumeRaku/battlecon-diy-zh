# BattleCON 状态机引擎 · 核心层
import random, collections, statistics, time
from dataclasses import dataclass, field
from typing import Optional

BASES_JIA = {
    '抓投': dict(range=1, power=2, speed=5, res=0),
    '猛冲': dict(range=1, power=3, speed=4, res=0),
    '强袭': dict(range=1, power=4, speed=3, res=5),
    '射击': dict(range=1, range_max=4, power=3, speed=2, res=2),
    '轰击': dict(range=2, range_max=3, power=3, speed=1, res=0),
    '闪避': dict(range=None, power=None, speed=3, res=0),
}
BASES_YI = {
    '还击': dict(range=1, power=5, speed=1, res=4),
    '强打': dict(range=1, power=4, speed=2, res=2),
    '格挡': dict(range=None, power=3, speed=5, res=0),
    '掷投': dict(range=1, power=2, speed=5, res=0),
    '刺击': dict(range=2, power=3, speed=4, res=0),
    '发波': dict(range=3, range_max=5, power=3, speed=3, res=3),
}

class SafeBases(dict):
    def __getitem__(self, k):
        b = dict(super().__getitem__(k))
        if b['range'] is None:
            b['range'] = 0; b['range_max'] = 0
        if b['power'] is None:
            b['power'] = 0
        return b
    def get(self, k, d=None):
        return self[k] if k in self else d

BASES = SafeBases(BASES_JIA)
BASES_PICK = ('猛冲', '强袭', '射击')

@dataclass
class Fighter:
    name: str
    life: int = 20
    max_life: int = 20
    pos: int = 0
    energy: int = 2
    stunned: bool = False
    stun_immune: bool = False
    hand_styles: set = field(default_factory=set)
    hand_bases: set = field(default_factory=set)
    discard: list = field(default_factory=list)
    removed: list = field(default_factory=list)
    tokens: dict = field(default_factory=dict)
    finisher_used: bool = False
    _beat_dmg: int = 0
    _cur_res: int = 0

@dataclass
class Card:
    name: str
    rng: int = None; rng_max: int = None
    power: int = 0; speed: int = 0; res: int = 0
    armor: int = 0
    effects: list = field(default_factory=list)
    exclusive: bool = False

@dataclass
class Card2(Card):
    rng_d: int = 0; rng_max_d: int = 0

@dataclass
class Character:
    name: str
    ua_ante_hook: object = None
    styles: list = field(default_factory=list)
    exclusive: Card = None
    finishers: dict = field(default_factory=dict)
    on_recycle: object = None
    on_hit_hook: object = None
    ua_end: object = None

def E(trigger, fn):
    return dict(trigger=trigger, fn=fn)

def dist(a, b): return abs(a - b)
def in_range(a, b, rmin, rmax): return rmin <= dist(a, b) <= rmax

def move_toward(f, target, n, worm=None, ignore=False, log=None, portal=None):
    worm = worm if worm is not None else set()
    step = 1 if target > f.pos else -1
    moved, pos = 0, f.pos
    while moved < n:
        nxt = pos + step
        if nxt == target:
            pos = nxt + step; moved += 1; continue
        if portal is not None and nxt == portal and not ignore:
            pos = nxt
            if log is not None: log.append(f'  门: {f.name}停在门格@{nxt}')
            break
        if nxt in worm and not ignore:
            worm.discard(nxt)
            if log is not None: log.append(f'  虫洞: {f.name}中止,移除@{nxt}')
            break
        pos = nxt; moved += 1
    f.pos = pos
    return pos

def move_away(f, target, n, worm=None, ignore=False, log=None, portal=None):
    worm = worm if worm is not None else set()
    step = -1 if target > f.pos else 1
    moved, pos = 0, f.pos
    while moved < n:
        nxt = pos + step
        if nxt == target:
            pos = nxt + step; moved += 1; continue
        if portal is not None and nxt == portal and not ignore:
            pos = nxt
            if log is not None: log.append(f'  门: {f.name}停在门格@{nxt}')
            break
        if nxt in worm and not ignore:
            worm.discard(nxt)
            if log is not None: log.append(f'  虫洞: {f.name}中止,移除@{nxt}')
            break
        pos = nxt; moved += 1
    f.pos = pos
    return pos

def close(f, target, n, worm=None, ignore=False, log=None, portal=None):
    worm = worm if worm is not None else set()
    step = 1 if target > f.pos else -1
    pos, used = f.pos, 0
    while used < n:
        nxt = pos + step
        if nxt == target: break
        if portal is not None and nxt == portal and not ignore:
            pos = nxt
            if log is not None: log.append(f'  门: 逼近停在门格@{nxt}')
            break
        if nxt in worm and not ignore:
            worm.discard(nxt); break
        pos = nxt; used += 1
    f.pos = pos
    return pos

def teleport(f, cell, worm=None, ignore=True, log=None):
    f.pos = cell
    if log is not None: log.append(f'  传送: {f.name}→格{cell}')
    return cell

def eff_dist(p1, p2, worm, p1_ignore=False):
    base = abs(p1 - p2)
    if p1_ignore: return base
    lo, hi = min(p1, p2), max(p1, p2)
    return base + sum(1 for w in worm if lo < w < hi)

def portal_between(p1, p2, portal):
    return portal is not None and min(p1, p2) < portal < max(p1, p2)

def apply_damage(def_f, raw, armor, log, src):
    dmg = max(0, raw - armor)
    if def_f.tokens.get('stance') == '愤怒':
        dmg *= 2
        log.append(f'  [愤怒承伤x2] {def_f.name}')
    def_f.life -= dmg
    log.append(f'  {src} 造成{dmg} -> {def_f.name}生命{def_f.life}')
    def_f._beat_dmg += dmg
    if def_f.life <= 0:
        log.append(f'  ★ {def_f.name}生命归零,决斗立即结束(N17)')
        return 'dead'
    return 'ok'

def check_stun(def_f, log):
    tot = def_f._beat_dmg
    res = def_f._cur_res
    if tot > res and not def_f.stun_immune:
        def_f.stunned = True
        log.append(f'  {def_f.name} 被眩晕(累计{tot}>韧{res})')

def life_loss(f, n, log, src):
    real = max(0, min(n, f.life - 1))   # 削命不致死: 扣到1为止; 永不回血(负值截0)
    f.life -= real
    log.append(f'  {src}: {f.name}削命{real}(最低1) -> 生命{f.life}')
    return real

def ante_step(A, B, actionsA, actionsB, log):
    seq = [actionsA, actionsB]
    i, skips = 0, 0
    while skips < 2:
        acts = seq[i % 2]
        f = A if i % 2 == 0 else B
        done = False
        while acts:
            act = acts.pop(0)
            if act[0] == 'pass':
                skips += 1; done = True; break
            skips = 0
            if act[0] == 'overload':
                _, typ = act
                key = f'_ol_{typ}'
                assert not getattr(f, key, False), f'{f.name}超载{typ}重复'
                assert f.energy >= 2
                f.energy -= 2; setattr(f, key, True)
                log.append(f'  投注: {f.name} 超载{typ}')
            elif act[0] == 'finisher':
                _, face, style_rm = act
                assert not f.finisher_used, '终结技额度已尽'
                assert f.energy >= f.life, f'费用{f.life}>手持{f.energy},物理不可付'
                f.energy -= f.life
                f.removed.append(style_rm); f.hand_styles.discard(style_rm)
                f.finisher_used = True
                f._pending_finisher = face
                log.append(f'  变招: {f.name} 宣言[{face}], 耗{f.life}能量, {style_rm}移出游戏')
        if done and skips >= 2: break
        i += 1
        if i > 20: break

def recycle_step(f, ch, decl, pool, log=None):
    gain = 1 + (1 if f.life <= 7 else 0)
    take = min(gain, pool[0]); pool[0] -= take
    f.energy = min(10, f.energy + take)
    st, bs, fin, opts = decl
    if fin:
        f.removed.append(st)
    else:
        f.hand_styles |= {s for s, b_ in f.discard if (s, b_) != (st, bs)}
        f.hand_bases  |= {b_ for s, b_ in f.discard if (s, b_) != (st, bs)}
        f.discard = [p_ for p_ in f.discard if p_ != (st, bs)]
        f.discard.append((st, bs))
    f.stunned = False; f._beat_dmg = 0
    for t in ('_ol_power', '_ol_res', '_ol_speed'):
        if hasattr(f, t): delattr(f, t)

def build_ctx(A, B, log):
    return {'self': None, 'opp': None, 'log': log, 'ante_curses': 0,
            'beat_no': 0, 'mods': None, 'flags': None, 'rexan_hit': False, 'rexan_was_hit': False}

def fire(card, trigger, ctx):
    for e in card.effects:
        if e['trigger'] == trigger:
            e['fn'](ctx)

