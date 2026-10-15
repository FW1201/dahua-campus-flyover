# v5：立面修補、粗體招牌與匿名學生步行

> 模型和預檢已完成；94 秒影片輸出中，完稿檔與驗證紀錄將在完成後加入。

維持日景、1:34；提高至 2560×1440、24 fps，2256 個原生畫格，15 段鏡頭。Blender 5.4 Alpha / Eevee / 32 samples / AgX。

## 本次修正

- 重建原 1:12 定得樓的立面開口、樓板收邊、窗內填板、入口、窗柵、冷氣格柵與排水細節。
- 重建原 1:22 小學部弧形立面，使窗、柱、窗臺及收邊沿相同切線對齊；補齊厚樓板、內側牆與陽台。
- 依新校方照片補小學金屬雨遮、木平台、低扶手、玻璃門五金與招牌位置。
- 校舍文字改為 Noto CJK Bold 700，具厚度、倒角與固定結構的實體立體字；儲存為網格。
- 補外牆窗框、密封條、屋簷、雨槽、屋頂接縫、排水溝與細微材質變化，修正前棟山牆與屋頂接合。
- 47 名可編輯骨架學生，包含中學白色紅藍線條體育服、淺藍正式服、深藍體育服，以及小學水手領、格紋裙、紅藍體育服。
- 兩段近距離服裝鏡頭，人物無細緻五官；交替支撐腳 IK、抬腳、擺臂及連續路線行走。

## 檔案

- `dahua-campus-v5.blend`：完整可編輯場景、人物骨架、材質和 94 秒相機動畫。
- `build_refined_scene.py`、`architecture_details.py`、`walking_students.py`：可重建來源。
- `render_video.py`：逐格輸出，分鏡頭保留可恢復串流及已完成片段，同一模型可續跑。
- `shots.json`、`camera-audit.json`、`architecture-repairs.json`、`gait-contact-audit.json`、`student-animation-manifest.json`：鏡頭、修補與角色資料。
- `SOURCES.md`、`reference/`、`reference-manifest.json`：來源與服裝判定限制。
- `previews/`：全部鏡頭起、中、終點及問題區間的實際渲染預覽。
- 完稿後提供 `dahua-campus-94s-v5.mp4` 與 `verification.json`。

## 再製

```sh
blender -b --python build_refined_scene.py
blender -b dahua-campus-v5.blend --python render_preflight.py
blender -b dahua-campus-v5.blend --python render_video.py
python3 verify_video.py
```

需要 Blender 與 FFmpeg。`.render/` 保留完成的分鏡段；只有模型 SHA-256 和設定一致才接受續跑，片段的畫格數及時間刻度經核對後才合併。

## 真實性與驗證邊界

新立面與服裝依校方照片補強；Maps 連線在本輪未恢復，配置沿用 v4 已核對版本。淺藍正式服的確切年級歸屬未能由照片確認，部分尺寸與遮蔽結構仍有推估。見 SOURCES.md。

人物支撐腳有 27 次取樣，鞋底偏差在約 8 毫米內；此檢查不能證明全片每一步都沒有碰撞。全部鏡頭均有可見預覽，完稿影片仍會另做解碼與規格驗證。
