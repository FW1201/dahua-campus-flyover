# 大華中學校園飛越場景

**新版：** [v2/](v2/) 已依使用者提供的空拍影片加入多視角校正、建築細部及 1080p 飛越動畫。以下是保留的第一版說明。

這是以使用者提供的 447 × 447 空拍照片為主要視覺參考，為鏡頭飛越動畫製作的**概略 3D 重建**。場景包含照片中的校門前草坪、道路、紅屋頂教學樓、後方白色校舍、右側操場跑道、樹林與遠景建物。建築尺寸、背面與照片外區域皆為推估，不能用作測繪、建築設計或校園導覽的精確資料。

## 檔案

- `dahua-campus-flyover.blend`：可編輯 Blender 5.3 場景，含 12 秒、30 fps 的鏡頭路徑。
- `dahua-campus.glb`：靜態場景，可匯入常見 3D 工具；動畫鏡頭以 `.blend` 為準。
- `preview.png`：場景預覽。
- `flyover-preview.mp4`：9 秒低解析度鏡頭動線預覽；正式動畫請由 `.blend` 重新渲染。
- `build_scene.py`：程序化重建腳本，可重建或調整配置。
- `assets/reference-aerial.jpeg`：使用者提供的原始照片。公開發布前請確認照片授權；若不具備公開再散布權利，可從 Git 追蹤中移除這個檔案。

## 使用

在 Blender 開啟 `.blend`，切到攝影機視角，播放影格 1–360。要重新產生場景：

```sh
blender -b -t 4 --python build_scene.py
```

渲染動畫可在 Blender 選擇 `Render > Render Animation`，或依設備調整解析度與取樣數。

## 參考與侷限

- [使用者提供的空拍照片](assets/reference-aerial.jpeg)：主要幾何與色彩參考。
- [使用者指定的 YouTube 空拍影片](https://www.youtube.com/watch?v=58FXb8irbyg)：目前未能擷取影片畫面，因此沒有依其影格推導幾何，也沒有收錄影格。
- [大華中學官方網站](https://sites.google.com/twnt5.thsh.tyc.edu.tw/thsh2012/%E9%A6%96%E9%A0%81)：用於核對學校與楊梅校址。

模型採概略建築量體及重複窗戶，不含精確地形、立面、室內與真實貼圖。若取得平面圖、多角度照片或可使用的影片影格，可進一步校正。
