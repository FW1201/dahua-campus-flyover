import bpy,os,json
root=os.path.dirname(__file__);s=bpy.context.scene;s.render.resolution_percentage=60;s.eevee.taa_render_samples=24
for shot in json.load(open(os.path.join(root,'shots.json'))):
 f=(shot['start']+shot['end'])//2;s.frame_set(f);s.render.filepath=os.path.join(root,'preview-%04d.png'%f);bpy.ops.render.render(write_still=True)
