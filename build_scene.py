"""Procedural, editable campus flyover blockout based on the supplied aerial photo.

Run: blender -b -t 4 --python build_scene.py
All dimensions are approximate metres; this is a visual reconstruction, not survey data.
"""
import bpy
import math
import os
import random
from mathutils import Vector

ROOT = os.path.dirname(os.path.abspath(__file__))
random.seed(12)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def mat(name, color, rough=0.8):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Roughness'].default_value = rough
    return m

grass = mat('grass', (.23,.38,.15)); lawn = mat('front lawn', (.43,.55,.21))
forest = [mat('tree green '+str(i), c) for i,c in enumerate([(.13,.29,.11),(.19,.37,.13),(.24,.41,.16),(.29,.43,.18)])]
concrete = mat('warm pale concrete', (.72,.72,.65)); white = mat('school facade', (.79,.81,.77))
roof = mat('terracotta roofs', (.54,.22,.17)); darkroof = mat('grey roofs', (.43,.46,.42))
asphalt = mat('roads', (.35,.37,.35)); track = mat('running track', (.59,.24,.20))
field = mat('sports field', (.36,.52,.27)); glass = mat('recessed windows', (.22,.30,.32), .25)
line = mat('road markings', (.75,.69,.43)); hedge = mat('hedges', (.53,.62,.13))

def cube(name, loc, scale, material, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o=bpy.context.object; o.name=name; o.dimensions=scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    if bevel:
        mod=o.modifiers.new('soft edges','BEVEL'); mod.width=bevel; mod.segments=2
        o.modifiers.new('weighted normals','WEIGHTED_NORMAL')
    return o

def path(name, pts, radius, material, cyclic=False):
    cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'; cu.bevel_depth=radius; cu.bevel_resolution=2
    sp=cu.splines.new('POLY'); sp.points.add(len(pts)-1)
    for p,xyz in zip(sp.points,pts): p.co=(*xyz,1)
    sp.use_cyclic_u=cyclic
    ob=bpy.data.objects.new(name,cu); bpy.context.collection.objects.link(ob); ob.data.materials.append(material)
    return ob

def building(name,x,y,w,d,h,roofmat=roof,levels=2):
    cube(name,(x,y,h/2),(w,d,h),white,.18)
    cube(name+' roof',(x,y,h+.35),(w+1.1,d+1.1,.7),roofmat,.14)
    # Repeating dark window strips on the visible long facades.
    for floor in range(levels):
        z=(floor+.55)*h/levels
        for n in range(max(2,int(w/4.2))):
            xx=x-w/2+(n+.5)*w/max(2,int(w/4.2))
            cube(name+' south window',(xx,y-d/2-.07,z),(2.25,.13,1.15),glass)
        for n in range(max(2,int(d/5))):
            yy=y-d/2+(n+.5)*d/max(2,int(d/5))
            cube(name+' west window',(x-w/2-.07,yy,z),(.13,2.3,1.15),glass)

def tree(name,x,y,r=2.4):
    cube(name+' trunk',(x,y,1.3),(.36,.36,2.6),mat_trunk)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=r,location=(x,y,2.8+r*.32))
    o=bpy.context.object; o.name=name; o.data.materials.append(random.choice(forest))

mat_trunk=mat('tree trunks',(.30,.22,.16))
cube('site terrain',(0,0,-.5),(225,180,1),grass)
# Foreground courtyard and entrance, camera side of the supplied photo.
cube('entrance apron',(-7,-55,.035),(104,42,.07),asphalt)
cube('front oval lawn',(8,-57,.09),(57,30,.18),lawn,8)
for a in range(11):
    ang=math.radians(-80+a*16)
    x=8+25*math.cos(ang); y=-57+12*math.sin(ang)
    cube('crescent flower bed '+str(a),(x,y,.28),(5,2,.55),hedge,1)
cube('entrance gate left',(-35,-83,1.7),(2.5,2.5,3.4),concrete)
cube('entrance gate right',(-12,-83,1.7),(2.5,2.5,3.4),concrete)
cube('gate canopy',(-23.5,-83,3.5),(25,3,.7),darkroof)
cube('west access road',(-72,-21,.04),(12,127,.08),asphalt)
path('west road centre marking',[(-72,y,.14) for y in range(-80,48,8)],.09,line)

# Three stepped red roof wings, front annex, rear pale classroom blocks.
building('south classroom wing',-23,-18,68,13,9,roof,2)
building('central classroom wing',-12,3,70,14,11,roof,3)
building('north classroom wing',-10,24,58,13,10,roof,2)
building('front east annex',36,-31,45,14,8,roof,2)
building('west connecting wing',-45,-3,17,36,7,roof,2)
building('northwest pale block',-56,46,36,17,17,darkroof,4)
building('north central pale block',-2,56,49,17,18,darkroof,4)
building('north connector',-30,43,30,11,8,darkroof,2)
building('southwest small hall',-46,-35,20,17,7,roof,1)

# Athletics occupies the right edge and extends beyond the photographed frame.
cube('track base',(85,0,.06),(78,92,.12),track,18)
cube('field',(85,0,.15),(58,69,.17),field,16)
for off in (0,2.0,4.0,6.0):
    pts=[]
    for i in range(64):
        a=i*2*math.pi/64
        pts.append((85+(31+off)*math.cos(a),(37+off)*math.sin(a),.23))
    path('running lane '+str(off),pts,.07,concrete,True)
path('field centre line',[(85,-28,.25),(85,28,.25)],.05,concrete)

# Scattered campus trees and a dense forest backdrop preserve the photo silhouette.
for x in range(-62,52,7):
    if x not in range(-48,-24): tree('north row '+str(x),x,76,random.uniform(2,3.3))
for y in range(-72,68,8): tree('road trees '+str(y),-84,y,random.uniform(2,3.4))
for i in range(220):
    x=random.uniform(41,115); y=random.uniform(41,91)
    if x<55 and y<66: continue
    tree('forest %03d'%i,x,y,random.uniform(2.2,4.4))
for i in range(26):
    x=random.uniform(-105,-79); y=random.uniform(-82,82)
    tree('west woods %03d'%i,x,y,random.uniform(2,3.5))
for i in range(19):
    x=random.uniform(-55,55); y=random.uniform(-43,35)
    if -50<x<50 and -35<y<30 and random.random()<.75: continue
    tree('courtyard tree %03d'%i,x,y,random.uniform(1.4,2.8))

# Approximate neighborhood visible beyond school.
for i in range(28):
    x=random.uniform(-104,-35); y=random.uniform(70,90)
    if abs(x+55)<22 and y<77: continue
    building('background residence %02d'%i,x,y,random.uniform(6,12),random.uniform(5,9),random.uniform(6,10),roof,2)

world=bpy.context.scene.world or bpy.data.worlds.new('World')
bpy.context.scene.world=world; world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.62,.74,.88,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.7
bpy.ops.object.light_add(type='AREA',location=(-70,-100,130))
bpy.context.object.name='large soft sunlight'; bpy.context.object.data.energy=80000; bpy.context.object.data.shape='DISK'; bpy.context.object.data.size=90

camera_data=bpy.data.cameras.new('Flyover camera'); camera=bpy.data.objects.new('Flyover camera',camera_data)
bpy.context.collection.objects.link(camera); bpy.context.scene.camera=camera
camera_data.lens=28
scene=bpy.context.scene; scene.frame_start=1; scene.frame_end=360; scene.render.fps=30
for frame,loc,target in [
    (1,(-122,-138,62),(-8,-15,0)),
    (90,(-85,-105,76),(2,4,0)),
    (180,(-26,-85,99),(20,16,0)),
    (270,(49,-67,93),(3,23,0)),
    (360,(121,-30,72),(-20,25,0))]:
    camera.location=loc; camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.keyframe_insert(data_path='location',frame=frame)
    camera.keyframe_insert(data_path='rotation_euler',frame=frame)
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=1280; scene.render.resolution_y=720; scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
scene.camera.data.dof.use_dof=False
scene.frame_set(160)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'dahua-campus-flyover.blend'))
bpy.ops.export_scene.gltf(filepath=os.path.join(ROOT,'dahua-campus.glb'),export_format='GLB',export_cameras=False,export_lights=False)
scene.render.filepath=os.path.join(ROOT,'preview.png')
bpy.ops.render.render(write_still=True)
