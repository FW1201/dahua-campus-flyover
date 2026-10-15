"""Native 1440p campus animation; recoverable shot segments and safe resume."""
import bpy,os,sys,json,time,subprocess,shutil,hashlib
from pathlib import Path
root=Path(__file__).resolve().parent;s=bpy.context.scene
s.render.resolution_x=2560;s.render.resolution_y=1440;s.render.resolution_percentage=100;s.render.fps=24;s.eevee.taa_render_samples=32
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.compression=10
ffmpeg=shutil.which('ffmpeg') or '/opt/homebrew/bin/ffmpeg';ffprobe=shutil.which('ffprobe') or '/opt/homebrew/bin/ffprobe'
shots=json.loads((root/'shots.json').read_text());cache=root/'.render';cache.mkdir(exist_ok=True)
modelhash=hashlib.file_digest((root/'dahua-campus-v5.blend').open('rb'),'sha256').hexdigest()
settings={'model_sha256':modelhash,'width':2560,'height':1440,'fps':24,'samples':32,'crf':21}
meta=cache/'settings.json'
if meta.exists():assert json.loads(meta.read_text())==settings,'Cached segments use another model/settings; use another cache folder.'
else:meta.write_text(json.dumps(settings,indent=2))
current=cache/'current-frame.png';start=time.monotonic();rendered=0;segments=[]
def count(path):
 d=json.loads(subprocess.check_output([ffprobe,'-v','error','-select_streams','v:0','-show_entries','stream=nb_frames,width,height,avg_frame_rate','-of','json',str(path)]))['streams'][0]
 assert(d['width'],d['height'],d['avg_frame_rate'])==(2560,1440,'24/1'),d
 return int(d['nb_frames'])
for i,shot in enumerate(shots,1):
 segment=cache/f'shot-{i:02d}.mp4';ts=cache/f'shot-{i:02d}.ts';n=shot['end']-shot['start']+1;segments.append(segment)
 if segment.exists() and count(segment)==n:
  rendered+=n;print('RESUME_SHOT',i,shot['name'],rendered,flush=True);continue
 log=(cache/f'shot-{i:02d}-encode.log').open('w')
 p=subprocess.Popen([ffmpeg,'-y','-f','image2pipe','-vcodec','png','-framerate','24','-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','21','-pix_fmt','yuv420p','-f','mpegts',str(ts)],stdin=subprocess.PIPE,stderr=log)
 try:
  for frame in range(shot['start'],shot['end']+1):
   s.frame_set(frame);s.render.filepath=str(current);bpy.ops.render.render(write_still=True)
   with current.open('rb') as f:p.stdin.write(f.read())
   rendered+=1
   if frame%24==0:print('PROGRESS',frame,'/2256',round(time.monotonic()-start,1),'seconds',flush=True)
  p.stdin.close();assert p.wait()==0,'FFmpeg encoding failed'
 finally:
  if p.poll() is None:p.terminate();p.wait()
  log.close()
 subprocess.run([ffmpeg,'-v','error','-y','-i',str(ts),'-c','copy','-video_track_timescale','12288','-movflags','+faststart',str(cache/f'shot-{i:02d}.partial.mp4')],check=True)
 partial=cache/f'shot-{i:02d}.partial.mp4';assert count(partial)==n,(partial,n);partial.replace(segment)
 print('SHOT_COMPLETE',i,shot['name'],n,flush=True)
# All segments have the same time base, codec configuration and frame rate.
concat=cache/'concat.txt';concat.write_text(''.join("file '"+p.name+"'\n" for p in segments))
output=root/'dahua-campus-94s-v5.mp4'
subprocess.run([ffmpeg,'-v','error','-y','-f','concat','-safe','0','-i',str(concat),'-c','copy','-movflags','+faststart',str(output)],check=True)
assert count(output)==2256
if current.exists():current.unlink()
print('FINAL_RENDER_COMPLETE',round(time.monotonic()-start,1),str(output),flush=True)
