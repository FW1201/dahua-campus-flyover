"""Native 24 fps Full HD render, PNG pipe to ffmpeg (Blender Beta lacks video writer)."""
import bpy,os,subprocess,shutil,time
root=os.path.dirname(os.path.abspath(__file__));s=bpy.context.scene
s.render.resolution_percentage=100;s.render.fps=24;s.frame_start=int(os.environ.get('CAMPUS_FRAME_START','1'));s.frame_end=2256;s.eevee.taa_render_samples=32
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.compression=15
output=os.environ.get('CAMPUS_OUTPUT_PATH',os.path.join(root,'dahua-campus-94s-v3.mp4'));temp=os.path.join(root,'.current-frame.png')
log=open(os.path.join(root,'encode.log'),'w')
p=subprocess.Popen([shutil.which('ffmpeg') or '/opt/homebrew/bin/ffmpeg','-y','-f','image2pipe','-vcodec','png','-framerate','24','-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',output],stdin=subprocess.PIPE,stderr=log)
start=time.monotonic()
try:
 for frame in range(s.frame_start,s.frame_end+1):
  s.frame_set(frame);s.render.filepath=temp;bpy.ops.render.render(write_still=True)
  with open(temp,'rb') as f:p.stdin.write(f.read())
  if frame%24==0:print('PROGRESS',frame,'/2256',round(time.monotonic()-start,1),'seconds',flush=True)
 p.stdin.close();code=p.wait();assert code==0,code
 os.remove(temp);print('FINAL_RENDER_COMPLETE',round(time.monotonic()-start,1),flush=True)
finally:
 if p.poll() is None:p.terminate()
 log.close()
