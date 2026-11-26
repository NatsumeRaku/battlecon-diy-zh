# -*- coding: utf-8 -*-
# 行236: WAR 15斗士终结技转双面,β面实读自TTS deck2卡背格42-57 (2026-11-27, akamai原图+RapidOCR+目识三核)
import json, io, os, glob

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "json-db", "en", "战争篇-WAR")

def spd(n):  return "%d<initiative>" % n
def grd(n):  return "0" if n == 0 else "%d<stun-shield>" % n

# folder, β名, 距离,威力,速度,韧性, β效果[(时点,条件,效果)], β台词
BETA = {
 "Demitras Denigrande": ("Accelerando","1~2","3",spd(4),grd(0),[
   ("前置","","Advance 1-6, as far as possible."),
   ("命中","","Spend any amount of <i-sb>Crescendo</i-sb> for +2 Power each.")],
   "\"Now we come to the grand finale...\""),
 "Hepzibah Culotre": ("Altazzar","1","6",spd(2),grd(0),[
   ("展示","","Apply the effects of all active Pacts again."),
   ("开始","","Your life becomes 1.")],
   "\"Ancient of shadows, heed my sacrifice and reveal to this world once more your limitless power!\""),
 "Hikaru": ("Four Winds","1","2",spd(5),grd(0),[
   ("展示","","Negate bonuses from Elements."),
   ("前置","Optional","Advance 1."),
   ("命中","","Regain all Elements. +2 Power per Element regained.")],
   "\"Here goes nothing!\""),
 "Kallistar": ("Chain of Destruction","4~6","5",spd(8),grd(0),[
   ("持续","","Ignore Armor.")],
   "\"Let's see who burns out first!\""),
 "Kehrolyn Ross": ("The August Strain","1~2","4",spd(5),grd(2),[
   ("持续","","Armor 2."),
   ("伤害","","Trash a Style in your hand and that Style's listed Morph. For the rest of the duel, apply the trashed Morph's stats and effects to your attack.")],
   "\"If I must become a monster to survive, then so be it!\""),
 "Khadath": ("Planar Crossing","1~2","4",spd(5),grd(0),[
   ("命中","","Teleport to any space. Push or Pull 0-6. Place the Gate on any space.")],
   "\"You're in my world now.\""),
 "Lixis": ("Life Virus","3~6","4",spd(3),grd(2),[
   ("命中","","Activate Virus.")],
   "\"I suppose we can begin the trial early.\""),
 "Luc": ("Stasis Charge","1","4",spd(3),grd(4),[
   ("持续","","Each time the Opponent would perform a trigger, prevent that trigger and regain a Time.")],
   "\"Stasis Field, activate!\""),
 "Magdelina": ("Solar Soul","1~2","2",spd(4),grd(0),[
   ("持续","","Armor 2."),
   ("命中","","Spend any amount of <i-sb>Trance</i-sb> for +1 Power each.")],
   "\"Avenlia, please protect me!\""),
 "Rukyuk": ("Force Grenade","1~2","4",spd(4),grd(0),[
   ("展示","","Negate all bonuses and effects from Ammo. This attack can hit even if you did not ante Ammo."),
   ("命中","Optional","Push 1-6."),
   ("后置","Optional","Retreat 1-5.")],
   "\"When finesse won't do, it's time to use excessive force!\""),
 "Sagas": ("Erasure","3~4","3",spd(6),grd(0),[
   ("持续","","Ignore Guard, Ignore Armor."),
   ("命中","","Regain Mirror."),
   ("循环","this attack hit","Trash the Opponent's attack pair. They skip cycling their Discard Piles this beat.")],
   "\"Everything can be replaced.\""),
 "Seth": ("Fortune Buster","1~6","0",spd(13),grd(0),[
   ("开始","the Opponent's attack is a Finisher","Become Active Player."),
   ("命中","the Opponent's attack is a Finisher","The Opponent is eliminated.")],
   "\"There's just one fate for you...\""),
 "Tatsumi & Juto": ("Guardian Xandjinn","0~1","6",spd(5),grd(0),[
   ("持续","","Ignore Guard, Check Range from Juto (this attack does not hit if Juto is not in the arena)."),
   ("命中","Optional","Shift Juto 1-6.")],
   "\"Rise from the waves, Xandjinn!\""),
 "Vanaah": ("Death Walks","1~2","5",spd(6),grd(0),[
   ("持续","","Ignore Guard."),
   ("命中","","Next beat, you have +4 Priority.")],
   "\"Lady of Death, I come now to commend another soul into your Great Mystery.\""),
 "Zaamassal": ("Plane Diver","1","2",spd(4),grd(0),[
   ("前置","","Teleport to any space."),
   ("命中","","Teleport to any space. +1 Power per space between you and the Opponent."),
   ("后置","","Become a Paradigm of your choice.")],
   "\"My power is worlds beyond yours.\""),
}

for folder,(bname,rng,pow_,spd_,grd_,fx,quote) in BETA.items():
    d = os.path.join(BASE, folder)
    files = [f for f in glob.glob(os.path.join(d,"终结技_*.json"))]
    assert len(files)==1, (folder,files)
    p = files[0]
    old = json.load(io.open(p,encoding="utf-8"))
    aname = old["名称"]
    note = old.get("备注","")
    note += ";β面来源注记:TTS图包deck2卡背格实读(2026-11-27,原图3750x3675,RapidOCR+目识双核);行236"
    new = {
      "角色": old["角色"],
      "卡类": "终结技(双面)",
      "名称": {"α面": aname, "β面": bname},
      "系列": old["系列"],
      "角标": {"α面": "<star8-alpha>", "β面": "<star8-beta>"},
      "数值": {"α面": old["数值"], "β面": {"距离": rng, "威力": pow_, "速度": spd_, "韧性": grd_}},
      "效果": {"α面": old["效果"], "β面": [{"时点":t,"条件":c,"效果":e} for t,c,e in fx]},
      "台词": {"α面": old.get("台词",""), "β面": quote},
      "来源": old.get("来源","官方实卡"),
      "备注": note,
    }
    with io.open(p,"w",encoding="utf-8") as f:
        json.dump(new,f,ensure_ascii=False,indent=2); f.write("\n")
    print("UPDATED",folder,"::",aname,"/",bname)
