"""Build editable title/lyric assets and composite the 94s school-song edition."""
from pathlib import Path
import json,hashlib,subprocess,shutil,os
from PIL import Image,ImageDraw,ImageFont
import numpy as np
root=Path(__file__).resolve().parent
font=root/'fonts/NotoSansCJKtc-Bold.otf'
raw='''老柏凌霜挺，寒梅傲雪香，大華精神日月同光
重建樂宮於峻嶺。
境教益彰長城雄壯，看，校旗矞麗飛揚、桃李競妍
白鷗戲水、冰潔蓮芳；
聽，弦歌唱書聲香，山嶽和應，長江浩蕩，遠播八荒，
想，名駒伯樂心神振，五育陶養，黃河綿長，教育瑤章。'''
# Phrase cues based on large-v3 cross-attention DTW peaks, corrected to supplied text.
# Repeated prompt hallucinations before the vocal entrance and after the final line are excluded.
cues=[(12.78,18.98,'老柏凌霜挺'),(18.98,23.80,'寒梅傲雪香'),(23.80,29.45,'大華精神日月同光'),(29.45,34.85,'重建樂宮於峻嶺'),(34.85,37.65,'境教益彰'),(37.65,42.95,'長城雄壯'),(42.95,48.78,'看，校旗矞麗飛揚'),(48.78,51.37,'桃李競妍'),(51.37,54.30,'白鷗戲水'),(54.30,59.60,'冰潔蓮芳'),(59.60,64.95,'聽，弦歌唱書聲香'),(64.95,67.65,'山嶽和應'),(67.65,70.05,'長江浩蕩'),(70.05,75.16,'遠播八荒'),(75.16,80.48,'想，名駒伯樂心神振'),(80.48,83.25,'五育陶養'),(83.25,86.35,'黃河綿長'),(86.35,94.0,'教育瑤章')]
timing=root/'music/lyrics-timing.json'
if timing.exists():
 cues=[(float(c['start']),float(c['end']),c['text']) for c in json.loads(timing.read_text())['cues']]
def han(s):return ''.join(c for c in s if '\u4e00'<=c<='\u9fff')
assert han(raw)==han(''.join(c[2] for c in cues))
assert all(a<b<=94 for a,b,_ in cues)
assert all(cues[i][1]<=cues[i+1][0] for i in range(len(cues)-1))
(root/'music/lyrics-provided.txt').write_text(raw+'\n')
(root/'music/lyrics-timing.json').write_text(json.dumps({'method':'Local whisper.cpp large-v3, flash attention off, DTW; phrase timing corrected to user-provided lyrics; artificial prompt repeats excluded.','vocal_first_dtw_peak_seconds':12.98,'timing_limit':'Phrase-level alignment from automatic vocal attention; no claim of phoneme-exact or human-listened verification.','cues':[{'start':a,'end':b,'text':t} for a,b,t in cues]},ensure_ascii=False,indent=2)+'\n')
def stamp(t,ass=False):
 h=int(t//3600);m=int(t//60)%60;s=t%60
 return f'{h}:{m:02d}:{s:05.2f}' if ass else f'{h:02d}:{m:02d}:{s:06.3f}'.replace('.',',')
(root/'music/lyrics.srt').write_text('\n\n'.join(f'{i}\n{stamp(a)} --> {stamp(b)}\n{t}' for i,(a,b,t) in enumerate(cues,1))+'\n')
(root/'music/lyrics.lrc').write_text('[ti:大華中學校歌]\n'+''.join(f'[{int(a//60):02d}:{a%60:05.2f}]{t}\n' for a,b,t in cues))
header='''[Script Info]
Title: 大華中學校歌
ScriptType: v4.00+
PlayResX: 2560
PlayResY: 1440
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Lyric,Noto Sans CJK TC,64,&H00FFFFFF,&H0098C8E0,&H0013212C,&H900A1824,-1,0,0,0,100,100,2,0,1,3,1,2,120,120,76,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
lines=[];measure=ImageFont.truetype(str(font),64)
for a,b,t in cues:
 width=round(measure.getlength(t)+2*len(t)+92);left=(2560-width)//2;right=left+width
 # Compact translucent panel leaves the broad campus visible.
 panel=f'{{\\an7\\pos(0,0)\\p1\\bord0\\shad0\\1c&H24180A&\\1a&H50&\\fad(100,100)}}m {left} 1260 l {right} 1260 {right} 1390 {left} 1390'
 lines.append(f'Dialogue: 0,{stamp(a,True)},{stamp(b,True)},Lyric,,0,0,0,,{panel}')
 lines.append(f'Dialogue: 1,{stamp(a,True)},{stamp(b,True)},Lyric,,0,0,0,,{{\\fad(100,100)}}{t}')
(root/'music/lyrics.ass').write_text(header+'\n'.join(lines)+'\n')
# An editable alpha title plate, composited over the opening aerial view.
w,h=2560,1440
arr=np.zeros((h,w,4),dtype=np.uint8);arr[:,:,:3]=(8,24,37)
alpha=np.clip(226*(1-(np.arange(w)/2100)**1.8),0,226).astype(np.uint8);arr[:,:,3]=alpha
cover=Image.fromarray(arr);d=ImageDraw.Draw(cover);gold=(228,195,125,255);white=(248,249,246,255)
def text(x,y,value,size,fill=white):d.text((x,y),value,font=ImageFont.truetype(str(font),size),fill=fill,stroke_width=0)
text(160,310,'桃園楊梅・大華校園',38,gold)
d.rectangle((160,414,744,420),fill=gold)
text(150,455,'大華中學',160)
text(160,672,'校園巡禮',76)
text(164,815,'弦歌不輟・五育陶養',43,gold)
text(164,1130,'TA HWA  /  CAMPUS FILM',28,(218,230,230,255))
cover.save(root/'music/cover-overlay.png')
# Poster uses an actual encoded video frame, with the same title plate.
poster_frame=root/'music/cover-background.jpg'
subprocess.run([shutil.which('ffmpeg'),'-v','error','-y','-ss','2.0','-i',str(root/'dahua-campus-94s-v5.mp4'),'-frames:v','1','-q:v','2',str(poster_frame)],check=True)
poster=Image.open(poster_frame).convert('RGBA');poster.alpha_composite(cover);poster.convert('RGB').save(root/'music/大華中學_封面.jpg',quality=95)
# Reproducible asset manifest; original music is unchanged, with only final 67ms tail omitted.
(root/'music/composition.json').write_text(json.dumps({'source_video':'../dahua-campus-94s-v5.mp4','source_music':'dahua-school-song.mp3','source_music_sha256':hashlib.sha256((root/'music/dahua-school-song.mp3').read_bytes()).hexdigest(),'source_music_duration_seconds':94.066938,'duration_seconds':94,'fps':24,'cover_seconds':[0,6.5],'cover_fadeout_seconds':0.75,'lyrics':'lyrics.ass','font':'../fonts/NotoSansCJKtc-Bold.otf','audio_gain_db':2.5,'audio_peak_source_dbtp':-4.36,'audio_fade_out_seconds':0.35,'music_speed':1.0},ensure_ascii=False,indent=2)+'\n')
if '--render' in os.sys.argv:
 ff=os.environ.get('FFMPEG_CAPTION') or shutil.which('ffmpeg')
 # 2.5dB gain keeps the measured source true peak around -1.86dBTP.
 graph="[1:v]format=rgba,fade=t=out:st=5.75:d=0.75:alpha=1[title];[0:v][title]overlay=0:0:enable='lt(t,6.5)'[v];[v]ass=music/lyrics.ass:fontsdir=fonts,format=yuv420p[outv];[2:a]atrim=duration=94,asetpts=PTS-STARTPTS,volume=2.5dB,afade=t=out:st=93.65:d=0.35[outa]"
 output=root/'dahua-campus-94s-v5-school-song.mp4'
 subprocess.run([ff,'-hide_banner','-y','-i',str(root/'dahua-campus-94s-v5.mp4'),'-loop','1','-framerate','24','-i',str(root/'music/cover-overlay.png'),'-i',str(root/'music/dahua-school-song.mp3'),'-filter_complex',graph,'-map','[outv]','-map','[outa]','-t','94','-r','24','-c:v','libx264','-preset','fast','-crf','21','-pix_fmt','yuv420p','-c:a','aac','-b:a','256k','-ar','44100','-movflags','+faststart',str(output)],cwd=root,check=True)
 print('SCHOOL_SONG_RENDER_COMPLETE',output,flush=True)
