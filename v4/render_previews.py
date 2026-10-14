import bpy,os,json
root=os.path.dirname(os.path.abspath(__file__));s=bpy.context.scene;s.render.resolution_percentage=60;s.eevee.taa_render_samples=32
os.makedirs(os.path.join(root,'previews'),exist_ok=True)
for shot in json.load(open(os.path.join(root,'shots.json'))):
 for f in (shot['start'],(shot['start']+shot['end'])//2,shot['end']):
  s.frame_set(f);s.render.filepath=os.path.join(root,'previews','preview-%04d.png'%f);bpy.ops.render.render(write_still=True)
  print('PREVIEW',shot['name'],f,flush=True)
