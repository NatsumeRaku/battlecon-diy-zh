# DeepSeek 网页端翻译通道·操作手册（行251 实战沉淀）

> 目的：零网络额度出翻译初稿。Kimi WebBridge 操作用户本机浏览器（已登录态），会话持久于 chat.deepseek.com 对话「BattleCON卡牌翻译」。

## 流程（已验证跑通两轮）

1. `fill` 输入框（CSS `textarea`）→ `evaluate` 派发 Enter（keyCode 13）发送；
2. 等 25~45s（流式生成），`evaluate` 读 `main.innerText` 或 `.markdown-body` 最后一条；
3. 发送后页面状态会变（refs 失效），重选元素用 CSS 选择器，勿复用 @e ref。

## 铁律（实战教训）

1. **每批必须内联完整术语表**（对照表六-A 全量 + 格式铁律），禁止写"沿用上面的术语表"——多轮它会自行回退到直译（行251第二轮实证：咒约堆→誓约堆、Wisp→精灵、Target→目标、regain→重获、格→空间）。
2. 术语表即唯一质量源：给全=10条错0-1条；给漏=错4条起。验收仍需四维机检+对照表核对。
3. 免费档有限流，批量分小批（10条/轮），对话太长就开新对话重贴全表。
4. 机检要点（它高频犯的）：数字空格（"弃置1张"）、量词"一个"、regain≠重获、格≠空间、堆名漂移。

## 首轮短表 vs 全表 差异记录（行251）

- 短表遗漏导致：Reactive Player→反应玩家、regain→重获、Wish anted→已投注愿望(语序)、Function→功能。
- 全表内联后以上全对，但需人工复核残项。

## 识图通道实战补丁（2026-11-27 行255）
5. **传图三件套**（extension 未开 file-URL 权限时的替代）：
   - 本地 CORS 服务器：tts-img 目录起 `python _cors_srv.py`（127.0.0.1:8792，带 Access-Control-Allow-Origin:*）；
   - CDP `Page.setBypassCSP` 绕页面 CSP（evaluate 里 fetch http://127.0.0.1:8792/xx.png → DataTransfer → input[type=file].files → dispatch change）；
   - 判成功标准：`document.querySelectorAll('img')` 里 blob: 图数量，勿信返回值（React 会清 input.files）。
6. **文本发送**：`fill` 或原生 value setter + input 事件只完成"填"，**Enter 键无效**；必须点 `div.ds-button--primary` 发送按钮。
7. 图片与文字会拆成两条消息（图片先走），指令用"上一条消息的N张图"指代即可。
8. 装饰字体卡名 DS 可读（TRANSFIX vs FATALITY 这类仍需字体匹配终裁，DS 引效果文偶尔张冠李戴，卡名优先信 DS+人工双读）。
