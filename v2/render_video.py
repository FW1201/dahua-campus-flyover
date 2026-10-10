"""Render the saved scene and encode H.264 with the system ffmpeg.

blender -b --python render_video.py -- /absolute/path/to/frames /absolute/path/to/output.mp4
"""
import bpy, os, sys, subprocess
from pathlib import Path

root=Path(__file__).resolve().parent
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
if len(args)!=2:
 raise SystemExit('Supply frame output directory and final .mp4 output path after --')
frames=Path(args[0]).resolve();out=Path(args[1]).resolve()
frames.mkdir(parents=True,exist_ok=True);out.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'dahua-campus-detailed.blend'))
s=bpy.context.scene;s.render.filepath=str(frames/'frame_');s.render.image_settings.file_format='PNG';s.render.image_settings.compression=15
bpy.ops.render.render(animation=True)
subprocess.run(['ffmpeg','-hide_banner','-y','-framerate','24','-start_number','1','-i',str(frames/'frame_%04d.png'),'-frames:v','576','-c:v','libx264','-preset','slow','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],check=True)
