"""Extract review frames from the delivered MP4, never from Blender previews."""
from pathlib import Path
import json, subprocess, shutil
from PIL import Image, ImageDraw
root=Path(__file__).resolve().parent
video=root/'dahua-campus-94s-v5.mp4'
out=root/'video-review';out.mkdir(exist_ok=True)
shots=json.loads((root/'shots.json').read_text())
midpoints=[((s['start']+s['end'])//2-1)/24 for s in shots]
issues=[71.5,72,72.5,81.5,82,82.5]
walking=[55.25,55.5,55.75,56,56.25,56.5,80.25,80.5,80.75,81,81.25,81.5]
times=sorted(set(midpoints+issues+walking))
files={}
for t in times:
 p=out/f't-{t:06.2f}.jpg'
 subprocess.run([shutil.which('ffmpeg'),'-v','error','-y','-ss',str(t),'-i',str(video),'-frames:v','1','-q:v','2',str(p)],check=True)
 files[t]=p

def contact(times,path,columns=3):
 w,h=512,288;header=26;rows=(len(times)+columns-1)//columns
 canvas=Image.new('RGB',(columns*w,rows*(h+header)),(22,25,30));d=ImageDraw.Draw(canvas)
 for i,t in enumerate(times):
  x=(i%columns)*w;y=(i//columns)*(h+header)
  im=Image.open(files[t]).convert('RGB');im.thumbnail((w,h))
  canvas.paste(im,(x,y+header));d.text((x+8,y+6),f'{int(t//60):02d}:{t%60:05.2f}',fill='white')
 canvas.save(out/path,quality=91)
contact(midpoints,'all-shot-midpoints.jpg')
contact(issues,'reported-issue-intervals.jpg')
contact(walking,'walking-sequence.jpg')
(root/'video-review-frames.json').write_text(json.dumps({'source':video.name,'time_seconds':times,'purpose':'Encoded-video visual review samples; not every-frame geometry verification.'},indent=2)+'\n')
print('Extracted',len(times),'encoded-video frames and three contacts')
