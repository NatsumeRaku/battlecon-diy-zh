# -*- coding: utf-8 -*-
"""下载全部34张卡表图（akamai镜像）"""
import json, os, urllib.request, time

ROOT = r"D:\Arkham Horror PSD\BattleConDB\battlecon-diy-zh\memory-pending\tts-img\full"
os.makedirs(ROOT, exist_ok=True)
urls = json.load(open(r"D:\Arkham Horror PSD\BattleConDB\battlecon-diy-zh\memory-pending\tts-img\unique_urls.json"))["faces"]
for idx, u in enumerate(urls):
    u2 = u.replace("cloud-3.steamusercontent.com", "steamusercontent-a.akamaihd.net").strip()
    fn = os.path.join(ROOT, f"f{idx:02d}.jpg")
    if os.path.exists(fn) and os.path.getsize(fn) > 10000:
        print("skip", idx); continue
    for attempt in range(3):
        try:
            req = urllib.request.Request(u2, headers={"User-Agent": "Mozilla/5.0"})
            data = urllib.request.urlopen(req, timeout=60).read()
            open(fn, "wb").write(data)
            print("ok", idx, len(data)); break
        except Exception as e:
            print("retry", idx, e); time.sleep(3)
