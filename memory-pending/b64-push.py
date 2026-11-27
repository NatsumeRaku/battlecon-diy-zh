# -*- coding: utf-8 -*-
# base64+atob同步解码注入（绕fetch挂起/CSP/文件权限）
import base64, json, subprocess, time, os, sys

ROOT = r'D:\Arkham Horror PSD\BattleConDB\battlecon-diy-zh'
B64 = os.path.join(ROOT, 'memory-pending/_b64')
TAB = 1863426789
SES = 'deepseek-translate'
files = sys.argv[1:]

def push(name):
    p = os.path.join(B64, name + '.jpg')
    b64 = base64.b64encode(open(p, 'rb').read()).decode()
    code = ("(()=>{if(!window.__bc)window.__bc=[];"
            "const bin=atob('" + b64 + "');"
            "const arr=new Uint8Array(bin.length);"
            "for(let i=0;i<bin.length;i++)arr[i]=bin.charCodeAt(i);"
            "window.__bc.push(new File([arr],'" + name + ".jpg',{type:'image/jpeg'}));"
            "return window.__bc.length})()")
    req = {"action": "evaluate", "args": {"tabId": TAB, "code": code}, "session": SES}
    fp = os.path.join(ROOT, '_wb_req_b64.json')
    json.dump(req, open(fp, 'w', encoding='utf-8'))
    out = subprocess.run(['curl.exe', '-s', '-m', '60', '-X', 'POST', 'http://127.0.0.1:10086/command',
                          '-H', 'Content-Type: application/json', '--data-binary', '@' + fp],
                         capture_output=True, text=True, timeout=90).stdout
    os.remove(fp)
    return out[:150]

for f in files:
    print(f, push(f)[:130])
    time.sleep(0.5)
