# 战链引擎一键启动器 — 固化「复活协议」
# 用法:
#   python3 run_engine.py            # 1v1 循环赛(亚历克希安/雷克森/凯特琳/温迪/科达斯, 各50局)
#   python3 run_engine.py boss       # 首领战: 双人讨伐伯尔曼(模式B v3)
# 说明: 三个引擎文件必须按 core_tmp -> battlecon_engine(重排) -> engine_ext -> modeb 顺序 exec,
#       本脚本自动完成重排, 无需手改任何引擎文件。
import sys

def boot(with_modeb=False):
    lines = open('battlecon_engine.py').read().split('\n')
    i_chars = next(i for i, l in enumerate(lines) if l.startswith('CHARS = {'))
    i_main = next(i for i, l in enumerate(lines) if l.startswith("if __name__ == '__main__':"))
    reordered = (lines[:i_chars] + lines[i_chars + 1:i_main] + lines[i_main + 2:]
                 + [lines[i_chars], lines[i_main], lines[i_main + 1]])
    g = {'__name__': '__engine__'}
    exec(compile(open('_core_tmp.py').read(), '_core_tmp.py', 'exec'), g)
    exec(compile('\n'.join(reordered), 'battlecon_engine.py', 'exec'), g)
    exec(compile(open('_engine_ext.py').read(), '_engine_ext.py', 'exec'), g)
    if with_modeb:
        exec(compile(open('_modeb_v32_final.py').read(), '_modeb_v32_final.py', 'exec'), g)
    return g

if __name__ == '__main__':
    g = boot(with_modeb=(len(sys.argv) > 1 and sys.argv[1] == 'boss'))
    if len(sys.argv) > 1 and sys.argv[1] == 'boss':
        res = g['play_boss_burman'](7, '亚历克希安', '雷克森')
        print('首领战结果:', res[0], '| 回合数:', res[1], '| 指标:', res[2])
    else:
        g['run_roundrobin'](['亚历克希安', '雷克森', '凯特琳', '科达斯', '温迪'], N=50, yi=True)
