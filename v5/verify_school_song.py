"""Verify the music edition, source-audio sync and complete media decode."""
from pathlib import Path
import subprocess,shutil,json,hashlib
import numpy as np
root=Path(__file__).resolve().parent;video=root/'dahua-campus-94s-v5-school-song.mp4'
ff=shutil.which('ffmpeg');probe=shutil.which('ffprobe')
x=json.loads(subprocess.check_output([probe,'-v','error','-show_streams','-show_format','-of','json',str(video)]));v=next(s for s in x['streams'] if s['codec_type']=='video');a=next(s for s in x['streams'] if s['codec_type']=='audio')
assert(v['width'],v['height'],v['avg_frame_rate'],int(v['nb_frames']))==(2560,1440,'24/1',2256)
assert abs(float(x['format']['duration'])-94)<.001
assert a['codec_name']=='aac' and a['channels']==2
assert abs(float(a['start_time']))<.001
r=subprocess.run([ff,'-v','error','-i',str(video),'-f','null','-'],stderr=subprocess.PIPE,check=True);assert not r.stderr.strip(),r.stderr.decode()
def pcm(path,start):
 return np.frombuffer(subprocess.check_output([ff,'-v','error','-ss',str(start),'-i',str(path),'-t','5','-vn','-ac','1','-ar','16000','-f','f32le','pipe:1']),dtype='<f4').astype(np.float64)
checks=[]
for t in [13,43,80]:
 src=pcm(root/'music/dahua-school-song.mp3',t);dst=pcm(video,t);n=min(len(src),len(dst));src=src[:n];dst=dst[:n];src-=src.mean();dst-=dst.mean()
 size=1<<(2*n-1).bit_length();c=np.fft.irfft(np.fft.rfft(dst,size)*np.conj(np.fft.rfft(src,size)),size);search=np.concatenate((c[-1600:],c[:1601]));lag=int(np.argmax(search))-1600;correlation=float(search.max()/np.sqrt(np.sum(src**2)*np.sum(dst**2)))
 assert abs(lag/16000)<.04,(t,lag);assert correlation>.97,(t,correlation)
 checks.append({'source_window_seconds':[t,t+5],'audio_lag_seconds':lag/16000,'correlation':round(correlation,6)})
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
out={'video':video.name,'duration_seconds':94,'width':2560,'height':1440,'fps':24,'frames':2256,'audio_codec':a['codec_name'],'audio_sample_rate':int(a['sample_rate']),'audio_channels':2,'full_decode_passed':True,'audio_sync_checks':checks,'video_sha256':sha(video),'base_video_sha256':sha(root/'dahua-campus-94s-v5.mp4'),'model_sha256':sha(root/'dahua-campus-v5.blend'),'source_music_sha256':sha(root/'music/dahua-school-song.mp3'),'lyric_timing_file':'music/lyrics-timing.json','lyric_timing_limit':'Automatic phrase alignment, corrected to supplied text. Not human-listened or phoneme-exact verification.'}
(root/'school-song-verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False,indent=2))
