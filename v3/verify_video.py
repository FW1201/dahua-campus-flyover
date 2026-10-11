"""Verify final video duration, native frames, resolution and full decode."""
import pathlib,subprocess,json,hashlib,shutil
root=pathlib.Path(__file__).resolve().parent;video=root/'dahua-campus-94s-v3.mp4'
probe=json.loads(subprocess.check_output([shutil.which('ffprobe'),'-v','error','-select_streams','v:0','-show_entries','stream=codec_name,width,height,avg_frame_rate,nb_frames:format=duration,size','-of','json',str(video)]))
s=probe['streams'][0];duration=float(probe['format']['duration'])
assert(s['width'],s['height'])==(1920,1080),s
assert s['avg_frame_rate']=='24/1',s
assert int(s['nb_frames'])==2256,s
assert abs(duration-94)<.001,duration
decoded=subprocess.run([shutil.which('ffmpeg'),'-v','error','-i',str(video),'-f','null','-'],check=True,stderr=subprocess.PIPE)
assert not decoded.stderr.strip(),decoded.stderr.decode(errors='replace')
def digest(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  while data:=f.read(1024*1024):h.update(data)
 return h.hexdigest()
report={'video':video.name,'duration_seconds':duration,'frames':int(s['nb_frames']),'fps':24,'width':s['width'],'height':s['height'],'codec':s['codec_name'],'full_decode_passed':True,'video_sha256':digest(video),'model_sha256':digest(root/'dahua-campus-v3.blend'),'geometry_accuracy':'Reference-image reconstruction; metric dimensions and stadium depth inferred.'}
(root/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
