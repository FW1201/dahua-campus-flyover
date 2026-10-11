# 大華中學校園動畫 v3

94 秒（1:34）／1920×1080／原生 24 fps。以使用者空拍影片 00:16 以後的多角度畫面、四張校舍照片與 Wikimedia Commons 的凱旋樓、定得樓原圖增補。

## 本次調整

- 凱旋樓入口改向西，面向前庭中央草地；增加兩側突出量體、玻璃門、窗框、窗簾與建築名稱。
- 教學區水池增加立體磁磚池壁、藍色內緣、池水、池緣、噴泉、花叢、樹枝與景石。
- 前棟增加拱形門窗、山牆、旗桿及前庭資訊牌；教學樓增加連續玻璃窗帶、細窗框與磁磚表面。
- 定得樓增加圓角、水平紅線、窗柵、冷氣機與遮雨走廊。
- 操場改為下沉場地，加入西側看台階梯、通行階梯、扶手與周邊擋土牆。
- 八段鏡頭涵蓋全景、凱旋樓、前棟、水池、教學樓、定得樓、下沉操場及收束全景。

## 可編輯檔案

- `dahua-campus-v3.blend`：完整場景、材質、可編輯中文字樣幾何與相機動畫。
- `build_detailed_scene.py`：重建完整模型。
- `render_video.py`：Blender 渲染後逐格串流至 FFmpeg，避免大量暫存影格。
- `shots.json`：各段名稱、秒數及影格範圍。
- `reference/`：使用者提供的四張照片及網路來源索引。

## 來源與精確度

使用者提供的照片與影片為主要依據。網路參考為歷史照片：[Commons 校園圖集](https://commons.wikimedia.org/wiki/Category:Ta_Hwa_High_School)、[凱旋樓](https://commons.wikimedia.org/wiki/File:大華中學_凱旋樓_-_panoramio.jpg)、[定得樓](https://commons.wikimedia.org/wiki/File:大華中學_定得樓_-_panoramio.jpg)。取得的原圖為 2816×2112，網路原圖留在本地參考資料夾，Git 保留來源索引與使用者提供素材。

本模型為參考影像重建的建築視覺化。沒有測量、施工圖或地形資料，建築尺度、位置、操場下沉深度（約 4.8 公尺）、遮蔽部位與細部配置仍為推估；不是測繪或照片級數位孿生。校舍外觀採可編輯幾何與程序材質，沒有直接貼上含人物的來源照片。

## 重建

```sh
CAMPUS_RENDER_PREVIEW=0 /Applications/Blender.app/Contents/MacOS/Blender -b --python build_detailed_scene.py
/Applications/Blender.app/Contents/MacOS/Blender -b dahua-campus-v3.blend --python render_video.py
```

渲染需要 Blender 與 FFmpeg。Blender 5.3 Beta 在此機器以 Metal／Eevee 渲染；每次重新渲染會覆寫 v3 的影片輸出。
