# v4：Maps 校園配置與校舍深度精修


94 秒、1920×1080、24 fps，13 段鏡頭，含整體飛越、近距離校舍巡覽、走廊及後側雙語小學。採用 Blender 5.4.0 Alpha、Eevee、AgX，48 samples，以逐格 PNG 串流編碼 H.264。

## 交付檔案

- [94 秒影片](dahua-campus-94s-v4.mp4)
- [可編輯日景 Blender 模型](dahua-campus-v4.blend)
- [建模程式](build_refined_scene.py)、[影片輸出](render_video.py)
- [鏡頭配置](shots.json)、[比例與位置觀察](site-plan-observations.json)
- [來源與推估範圍](SOURCES.md)、[照片檔案索引與雜湊](reference-manifest.json)
- [影片完整解碼及規格驗證](verification.json)、[13 段成片抽樣總覽](final-video-contact.jpg)

使用者已確認維持日景，重點為完善校舍、配置與地形細節。

## 本次精修

1. 依目前 Maps 手動校準校舍間距、北棟長度、凱旋樓長軸、道路斜向、操場角度與屋頂太陽能板。
2. 新增後側小學部三層弧形校舍、米色橫向面磚、細長窗、陽台、屋頂欄杆、校名、連接通廊及後方球場。立面參考校方照片。
3. 四層教學樓改為樓板、柱、牆與玻璃組成；加入窗框、端面拱窗、排水管、窗臺、屋簷及屋頂結構。
4. 德賢樓入口、冷氣管、酒紅校門與網狀門扇；凱旋樓入口朝向中央草坪。
5. 磁磚水池、內圈藍色緣、景石、噴水與動態水波；綠色風雨走廊、花藤、植栽和前庭物件。
6. 下沉操場地形、16 級主要看台、四條階梯走道、上層欄杆、斜柱遮棚、六道跑道、藍綠邊帶、籃球場及球架。
7. 依新增照片建立一樓走廊內景：透明窗、門與公布欄、磁磚、天花與磨石地坪。

## 再製

在 v4 資料夾中，以官方 Blender 執行：

```sh
blender -b --python build_refined_scene.py
blender -b dahua-campus-v4.blend --python render_previews.py
blender -b dahua-campus-v4.blend --python render_video.py
python3 verify_video.py
```

渲染需要 FFmpeg 與可用圖形裝置；macOS Metal 需在允許存取 GPU 的環境執行。輸出時先保留可恢復的 MPEG-TS 中間檔，成功後再封裝 MP4。render_video.py 支援 CAMPUS_FRAME_START、CAMPUS_FRAME_END 和 CAMPUS_OUTPUT_PATH，方便分段或續接；分段後必須重做完整影片驗證。模型字樣已轉為幾何，沒有打包系統字型。所有紋理為程式材質，模型可獨立開啟。

## 驗證與限制

每段起、中、終點實際渲染檢視；2256 格相機路徑檢查主要建築體積，走廊內景是有意進入。體積檢查不涵蓋全部樹木與遮棚，故另以可見預覽排除遮擋。完稿影片抽查全部 13 段中點畫格，並通過完整解碼：94.000 秒、2256 格、24 fps、1920×1080。

本專案是來源影像重建的建築視覺化。實際尺寸、操場深度、背面與被遮蔽結構仍有推估；不是實測模型、攝影測量成果或完全寫實數位分身。來源差異與推估詳見 SOURCES.md。
