import bpy,os,json,time
root=os.path.dirname(os.path.abspath(__file__));s=bpy.context.scene;s.render.resolution_percentage=70;s.eevee.taa_render_samples=48
out=os.path.join(root,'previews');os.makedirs(out,exist_ok=True)
shots=json.load(open(os.path.join(root,'shots.json')));frames=set()
for shot in shots:frames.update((shot['start'],(shot['start']+shot['end'])//2,shot['end']))
frames.update((1705,1729,1753,1945,1969,1991))
for f in sorted(frames):
 s.frame_set(f);s.render.filepath=os.path.join(out,f'preview-{f:04d}.png');bpy.ops.render.render(write_still=True);print('PREFLIGHT',f,flush=True)
