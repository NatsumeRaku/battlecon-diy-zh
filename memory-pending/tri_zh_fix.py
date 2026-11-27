# -*- coding: utf-8 -*-
"""行265: 机检残留 37 条手工定稿（本地模型改不好，人工逐条定）"""
import json, io, os
from tri_zh_translate import EN, CACHE

FIX = {
 ("Amon", "UA_Damage Control.json", 0, "效果"):
   "<b>初始设置：</b>激活<i-sb>白色代码</i-sb>（等级 0）。你的其他危险等级处于未激活状态。",
 ("Amon", "形态牌_Code Red.json", 0, "效果"): "你不能被推动或拉动。",
 ("Amon", "终结技_Code Black.json", 1, "效果"):
   "<bl-b>后置：</bl-b>每 1 点被你的护甲防止的伤害，回收同等生命。",
 ("Amon", "终结技_Code Black.json", 2, "效果"):
   "<g-b>结束：</g-b>激活<i-sb>黄色代码</i-sb>（等级 2）。",
 ("Amon", "风格_High Alert.json", 0, "效果"):
   "<g-b>开始，可选：</g-b>提升你的<i-sb>危险等级</i-sb>。",
 ("Amon", "风格_Regulation.json", 0, "效果"):
   "<r-b>命中：</r-b>对手获得<i-sb>眩晕免疫</i-sb>。",
 ("Burgundy", "UA_Color Burn.json", 0, "效果"):
   "<b>初始设置：</b>你拥有<i-sb>5 颜料</i-sb>。在你的格放置一个颜料，并在你正前方的格放置一个颜料。",
 ("Burgundy", "UA_Color Burn.json", 1, "效果"):
   "<bl-b>前置：</bl-b>你可以撤回一个<i-sb>颜料</i-sb>，从其所在格计算你的攻击距离。否则，你的攻击不命中。",
 ("Burgundy", "UA_Color Burn.json", 2, "效果"):
   "<g-b>结束：</g-b>在你当前的格放置一个<i-sb>颜料</i-sb>。<i>（每格限一个颜料）</i>。",
 ("Burgundy", "招式_Graphic.json", 0, "效果"):
   "<p-b>当你被命中时</p-b>，如果你与对手之间有<i-sb>颜料</i-sb>，获得<b>护甲 2</b>。",
 ("Burgundy", "终结技_Slaughter.json", 0, "效果"):
   "<bl-b>前置，可选：</bl-b>瞬移至一个<i-sb>颜料</i-sb>所在的格，然后撤回该<i-sb>颜料</i-sb>。",
 ("Burgundy", "终结技_Slaughter.json", 1, "效果"):
   "<g-b>结束：</g-b>在任意格放置一个<i-sb>颜料</i-sb>。",
 ("Burgundy", "风格_Flattened.json", 0, "效果"): "回避距离 3+ 的攻击。",
 ("Burgundy", "风格_Scrawled.json", 0, "效果"):
   "<g-b>开始，可选：</g-b>朝对手未占据的<i-sb>颜料</i-sb>推动或拉动 1。撤回该<i-sb>颜料</i-sb>。",
 ("Burgundy", "风格_Stained.json", 0, "效果"):
   "<p-b>每当</p-b>对手进入<i-sb>颜料</i-sb>所在的格，<i-sb>+2 威力</i-sb>。",
 ("Cindra", "UA_Rebirth.json", 0, "效果"): "<b>初始设置：</b>你为<i-sb>人类</i-sb>。",
 ("Cindra", "形态牌_Human Form.json", 0, "效果"):
   "循环，生命 10 或更少：将你的生命设为 10。将你的所有风格替换为同色的凤凰风格（无论它们在哪里；你的原风格被弃置）。变为<i-sb>凤凰</i-sb>。",
 ("Cindra", "风格_Ashen.json", 0, "效果"): "回避距离 3+ 的攻击。",
 ("Dareios", "UA_Dipsomania.json", 3, "效果"):
   "<b>循环：</b>弃置弃牌堆 2 中的所有饮品。将弃牌堆 1 中的所有饮品放入弃牌堆 2。将所有激活的饮品放入弃牌堆 1。",
 ("Dareios", "风格_Slandering.json", 0, "效果"):
   "<b>展示，1+ 激活的<i-sb>饮品</i-sb>：</b>回避距离 X 的攻击，其中 X 为 1 加上激活的<i-sb>饮品</i-sb>数量。",
 ("Dareios", "风格_Slurred.json", 1, "效果"):
   "<r-b>命中，1+ 激活的<i-sb>饮品</i-sb>：</r-b>推动或拉动 1。每有激活的<i-sb>饮品</i-sb>，就额外执行此效果一次。",
 ("Dareios", "饮品牌_Vastas Vapor.json", 0, "效果"):
   "<g-b>开始：</g-b>回避距离 1 的攻击。",
 ("Dravil", "招式_Torrential.json", 0, "效果"):
   "<g-b>开始：</g-b>逼近 6，前进 1，后退 0~1。",
 ("Dravil", "招式_Torrential.json", 1, "效果"):
   "<r-b>命中，冰：</r-b><i-sb>+1 威力</i-sb>。",
 ("Dravil", "终结技_Storm.json", 0, "效果"):
   "<bl-b>前置，可选：</bl-b>前进或后退 1。",
 ("Hayden", "招式_Telekinetic.json", 0, "效果"):
   "<r-b>命中，选择一项：</r-b><br>• 支付任意数量的<i-sb>控制</i-sb>，每点拉动 1。<br>• 支付任意数量的<i-sb>狂怒</i-sb>，每点推动 1。",
 ("Lucida Malephaise", "UA_Jaws of Malephaise.json", 0, "效果"):
   "<b>初始设置：</b>消耗所有撕裂/吞噬指示物，并使其<i-sb>撕裂</i-sb>面朝上放置。",
 ("Lucida Malephaise", "UA_Jaws of Malephaise.json", 2, "效果"):
   "<b>展示：</b>将所有<i-sb>撕裂指示物</i-sb>的效果施加于对手，然后将这些指示物翻至<i-sb>吞噬</i-sb>面。",
 ("Lucida Malephaise", "UA_Jaws of Malephaise.json", 3, "效果"):
   "<r-b>命中：</r-b>回收一个<i-sb>撕裂指示物</i-sb>。",
 ("Lucida Malephaise", "招式_Insatiable.json", 0, "效果"):
   "<p-b>当</p-b>你在距离 1 被命中时，<i-sb>眩晕免疫</i-sb>。",
 ("Trias", "终结技_Slipstream.json", 2, "效果"):
   "<bl-b>前置，可选：</bl-b>弃置一个<i-sb>饰品牌</i-sb>以前进 3。",
 ("Trias", "终结技_Slipstream.json", 3, "效果"):
   "<bl-b>前置，距离 1~3：</bl-b>弃置任意数量的<i-sb>饰品牌</i-sb>，每个获得<i-sb>+2 威力</i-sb>。",
 ("Trias", "风格_Epic.json", 0, "效果"):
   "<b>展示：</b>再次应用所有激活的<i-sb>饰品牌</i-sb>的属性与效果。",
 ("Trias", "风格_Outrageous.json", 0, "效果"):
   "<g-b>开始：</g-b>每个激活的<i-sb>饰品牌</i-sb>获得<b>护甲 1</b>。",
 ("Trias", "饰品牌_+FromtheHeavens.json", 0, "条件"): "受到的伤害",
 ("Trias", "饰品牌_+WithStyle.json", 0, "效果"): "你不能被推动或拉动。",
 ("Wardlaw", "UA_Beatdown.json", 1, "效果"):
   "<b>初始设置：</b>放声大笑并侮辱对手。",
}

cache = json.load(io.open(CACHE, encoding='utf-8'))
n = 0
for (dirn, fn, i, field), zh in FIX.items():
    k = dirn + '\\' + fn + '|效果|%d|%s' % (i, field)
    if k in cache:
        cache[k] = zh
        n += 1
    else:
        print('未命中键', k)
json.dump(cache, io.open(CACHE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('手工定稿写入', n, '/', len(FIX))
