"""Ta Hwa campus: video-informed architectural visualization, approximate scale.
Source observations: 00:16–02:08 in user supplied videoplayback.mp4.
Run with Blender 5.4: blender -b --python build_refined_scene.py
"""
import bpy, math, random, os
from mathutils import Vector
from collections import defaultdict

ROOT=os.path.dirname(os.path.abspath(__file__))
random.seed(218)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for data in list(bpy.data.materials): bpy.data.materials.remove(data)

def material(name,color,rough=.75,noise=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 nt=m.node_tree;p=nt.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough
 if noise:
  tex=nt.nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=noise;tex.inputs['Detail'].default_value=3
  ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=tuple(v*.68 for v in color)+(1,);ramp.color_ramp.elements[1].color=tuple(min(1,v*1.18) for v in color)+(1,)
  nt.links.new(tex.outputs['Fac'],ramp.inputs[0]);nt.links.new(ramp.outputs[0],p.inputs['Base Color'])
 return m

M={}
for key,col,rough,noise in [
 ('ivory',(.77,.78,.71),.78,15),('white',(.91,.90,.84),.7,0),('shadow',(.21,.25,.24),.9,0),
 ('roof',(.48,.11,.065),.73,65),('ridge',(.62,.22,.14),.7,0),('glass',(.12,.22,.25),.24,0),
 ('frame',(.69,.73,.72),.5,0),('metal',(.37,.40,.40),.48,0),('asphalt',(.20,.23,.23),.9,90),
 ('paving',(.53,.55,.51),.9,45),('concrete',(.60,.61,.55),.86,20),('grass',(.23,.39,.11),.95,5),
 ('field',(.29,.43,.16),.98,9),('forest',(.10,.23,.075),1,4),('hedge',(.56,.62,.12),1,5),
 ('track',(.60,.24,.25),.92,40),('blue',(.07,.40,.64),.8,0),('court',(.32,.46,.34),.9,26),
 ('line',(.88,.86,.72),.78,0),('mint',(.40,.65,.60),.55,0),('soil',(.49,.25,.12),1,15),
 ('trunk',(.24,.18,.11),1,0),('carwhite',(.77,.79,.77),.33,0),('cardark',(.12,.17,.20),.32,0)]:
 M[key]=material(key,col,rough,noise)

class Mesh:
 def __init__(self,name):self.name=name;self.v=[];self.f=[];self.mi=[];self.mats=[]
 def faces(self,verts,faces,mat):
  offset=len(self.v);self.v.extend(verts)
  if mat not in self.mats:self.mats.append(mat)
  idx=self.mats.index(mat)
  for f in faces:self.f.append(tuple(offset+i for i in f));self.mi.append(idx)
 def box(self,x,y,z,w,d,h,mat):
  self.faces([(x+a*w/2,y+b*d/2,z+c*h/2) for a,b,c in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat)
 def finish(self):
  me=bpy.data.meshes.new(self.name);me.from_pydata(self.v,[],self.f);me.materials.clear()
  for m in self.mats:me.materials.append(M[m] if isinstance(m,str) else m)
  for p,i in zip(me.polygons,self.mi):p.material_index=i
  # Metric planar UV coordinates keep wall tiles square and avoid triplanar shading cost.
  if any(isinstance(m,str) and m in ('white','ivory','pooltile','ceiling','primarybrick') for m in self.mats):
   layer=me.uv_layers.new(name='Metric architectural UV')
   for poly in me.polygons:
    normal=poly.normal;axis=max(range(3),key=lambda k:abs(normal[k]));a,c=((1,2) if axis==0 else (0,2) if axis==1 else (0,1))
    for loop in poly.loop_indices:
     co=me.vertices[me.loops[loop].vertex_index].co;layer.data[loop].uv=(co[a],co[c])
  ob=bpy.data.objects.new(self.name,me);bpy.context.collection.objects.link(ob);return ob

def box(name,x,y,z,w,d,h,mat):
 b=Mesh(name);b.box(x,y,z,w,d,h,mat);return b.finish()

def polygon(name,pts,z,mat):
 b=Mesh(name);b.faces([(x,y,z) for x,y in pts],[tuple(range(len(pts)))],mat);return b.finish()

def ribbon(name,pts,width,z,mat):
 vs=[]
 for i,p in enumerate(pts):
  a=Vector(pts[max(0,i-1)]);c=Vector(pts[min(len(pts)-1,i+1)]);t=(c-a).normalized();n=Vector((-t.y,t.x))
  vs.extend([(p[0]+n.x*width/2,p[1]+n.y*width/2,z),(p[0]-n.x*width/2,p[1]-n.y*width/2,z)])
 b=Mesh(name);b.faces(vs,[(2*i,2*i+1,2*i+3,2*i+2) for i in range(len(pts)-1)],mat);return b.finish()

def line(name,pts,r,mat,closed=False):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=1
 s=cu.splines.new('POLY');s.points.add(len(pts)-1)
 for p,v in zip(s.points,pts):p.co=(*v,1)
 s.use_cyclic_u=closed;o=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(o);o.data.materials.append(M[mat]);return o

def roof(b,x,y,w,d,z,rise=2.3):
 # Front tower has a gable, matching its arched end wall, rather than an intersecting hip.
 if abs(x+10.7)<.01 and abs(y+34)<.01:
  ww=w+1;dd=d+1;rise=2.3
  b.faces([(x-ww/2,y-dd/2,z),(x+ww/2,y-dd/2,z),(x+ww/2,y+dd/2,z),(x-ww/2,y+dd/2,z),(x,y-dd/2,z+rise),(x,y+dd/2,z+rise)],[(0,3,5,4),(1,4,5,2)],'roof')
  b.faces([(x-ww/2,y-dd/2,z-.03),(x+ww/2,y-dd/2,z-.03),(x+ww/2,y+dd/2,z-.03),(x-ww/2,y+dd/2,z-.03)],[(0,1,2,3)],'white')
  b.faces([(x-w/2,y+d/2,z),(x+w/2,y+d/2,z),(x,y+d/2,z+rise)],[(0,1,2)],'white')
  b.box(x,y,z+rise+.04,.16,dd,.15,'ridge')
  for side in (-1,1):b.box(x+side*ww/2,y,z,.18,dd,.20,'white')
  return
 if d>w:
  temp=Mesh('rotated roof');roof(temp,0,0,d,w,z,rise)
  for face,idx in zip(temp.f,temp.mi):
   verts=[(x-temp.v[i][1],y+temp.v[i][0],temp.v[i][2]) for i in face]
   b.faces(verts,[tuple(range(len(verts)))],temp.mats[idx])
  return
 b.box(x,y,z-.06,w+.7,d+.7,.12,'white')
 w+=1;d+=1;cut=min(d*.46,w*.22)
 b.faces([(x-w/2,y-d/2,z),(x+w/2,y-d/2,z),(x+w/2,y+d/2,z),(x-w/2,y+d/2,z),(x-w/2+cut,y,z+rise),(x+w/2-cut,y,z+rise)],[(0,1,5,4),(1,2,5),(2,3,4,5),(3,0,4)],'roof')
 b.box(x,y,z+rise+.04,w-2*cut,.20,.14,'ridge')
 for side in (-1,1):
  b.box(x,y+side*d/2,z,w,.20,.22,'white')
  for j in range(1,10):
   t=j/10;yy=y+side*d/2*(1-t);zz=z+rise*t+.015
   b.box(x,yy,zz,w-2*cut*t,.045,.035,'ridge')

def building(name,x,y,w,d,floors,pitched=True,corridor=True):
 h=floors*3.35;b=Mesh(name)
 b.box(x,y,h/2,w,d,h,'ivory');b.box(x,y,.22,w+.55,d+.55,.44,'concrete')
 for k in range(floors):
  base=k*3.35
  for side in (-1,1):
   yy=y+side*(d/2+.025)
   if corridor and side==-1:
    b.box(x,yy,base+1.95,w-.65,.08,2.1,'shadow')
    b.box(x,yy-.48,base+.17,w+.25,1.0,.25,'concrete')
    b.box(x,yy-.59,base+.72,w,.17,.9,'white')
    b.box(x,yy-.59,base+1.28,w,.13,.10,'metal')
    for j in range(int(w/4.1)+1):b.box(x-w/2+j*w/int(w/4.1),yy-.52,base+1.75,.30,.44,3.05,'white')
   else:
    count=int(w/3.6)
    for j in range(count):
     xx=x-w/2+(j+.5)*w/count
     b.box(xx,yy,base+1.8,2.25,.13,1.55,'glass')
     for dz in (-.82,.82):b.box(xx,yy+side*.06,base+1.8+dz,2.42,.17,.10,'white')
     for dx in (-1.17,0,1.17):b.box(xx+dx,yy+side*.09,base+1.8,.08,.18,1.7,'frame')
   b.box(x,yy,base+3.26,w+.4,.24,.16,'white')
  for side in (-1,1):
   for j in range(max(1,int(d/3.7))):
    yy=y-d/2+(j+.5)*d/max(1,int(d/3.7))
    b.box(x+side*(w/2+.04),yy,base+1.85,.13,1.65,1.5,'glass')
 if pitched:roof(b,x,y,w,d,h,2.0)
 else:
  b.box(x,y,h+.14,w,d,.28,'concrete')
  for side in (-1,1):
   b.box(x,y+side*(d/2-.12),h+.65,w,.24,1,'white');b.box(x+side*(w/2-.12),y,h+.65,.24,d,1,'white')
  for j in range(max(1,int(w/12))):
   b.box(x-w*.32+j*10,y,h+.6,2.8,1.8,.9,'metal')
   b.box(x-w*.32+j*10,y,h+1.1,3,2,.15,'frame')
 ob=b.finish();ob['source']='Video 00:20, 00:40, 01:28, 01:44; inferred metric scale';return ob

# V4 local site coordinates are traced from the visible Maps viewport.
# Scale bar: 20 m = 84 CSS px; roof outlines remain approximate, not survey data.
from mathutils import Matrix
import json
SCALE=4.2
def xy(px,py):return ((px-1000)/SCALE,(500-py)/SCALE)
SITE={
 'south':(-11.7,-7.4,68.8,12.5,4),'north':(-13.1,30.0,53.0,12.6,4),
 'cross':(-12.0,12.0,32,24,3),'front':(-10.7,-34.0,12.5,26,2),
 'admin':(29.8,-39.0,28.5,14,2),'gym':(73.8,-82.1,22.5,30,1),
 'deding':(-.7,87.6,43,29,4),'west':(-78.5,80.5,31,18,4),
 'service':(0,58,10,17,4)}
# Albedo and material microstructure designed for close exterior views.
for key,col,rough,noise in [
 ('white',(.67,.68,.64),.66,0),('ivory',(.63,.64,.60),.76,0),
 ('frame',(.032,.04,.043),.4,0),('glass',(.035,.075,.09),.18,0),
 ('roof',(.34,.065,.033),.7,35),('ridge',(.42,.10,.058),.66,0),
 ('grass',(.085,.21,.035),.93,4),('forest',(.04,.13,.025),.95,6),
 ('paving',(.31,.33,.31),.87,20),('concrete',(.42,.43,.40),.83,30),
 ('bank',(.12,.14,.13),.9,16),('soil',(.31,.19,.10),.96,18),
 ('hedge',(.27,.39,.065),.9,12),('track',(.42,.09,.055),.89,45),
 ('curtain',(.20,.075,.078),.85,0),('redletter',(.39,.025,.02),.6,0),
 ('gold',(.44,.30,.10),.35,0),('bronze',(.075,.10,.085),.4,12),
 ('gate',(.095,.035,.025),.43,9),('tileblue',(.015,.047,.19),.28,0),
 ('water',(.018,.09,.105),.075,0),('foam',(.65,.80,.82),.14,0),
 ('glassgreen',(.10,.26,.22),.18,0),('rock',(.38,.36,.29),.95,6),
 ('solar',(.019,.039,.067),.2,0),('interior',(.50,.51,.45),.87,0),
 ('wood',(.23,.12,.055),.65,9),('notice',(.27,.46,.39),.62,0)]:M[key]=material('V4 '+key,col,rough,noise)
M['glass'].node_tree.nodes.get('Principled BSDF').inputs['Metallic'].default_value=.45
M['clear']=material('Clear courtyard corridor glazing',(.94,.97,.98),.045)
M['clear'].node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value=0
M['clear'].node_tree.nodes.get('Principled BSDF').inputs['Alpha'].default_value=.08
M['clear'].surface_render_method='DITHERED'
M['clear'].node_tree.nodes.get('Principled BSDF').inputs['IOR'].default_value=1.45
# Clear-pane proxy avoids costly forward-alpha lighting and temporal dither noise.
nt=M['clear'].node_tree;transparent=nt.nodes.new('ShaderNodeBsdfTransparent');transparent.inputs['Color'].default_value=(1,1,1,1);nt.links.new(transparent.outputs['BSDF'],nt.nodes.get('Material Output').inputs['Surface'])
M['water'].node_tree.nodes.get('Principled BSDF').inputs['Metallic'].default_value=.2
M['water'].node_tree.nodes.get('Principled BSDF').inputs['IOR'].default_value=1.333
M['glassgreen'].node_tree.nodes.get('Principled BSDF').inputs['Metallic'].default_value=.3

def tilemat(name,w=.08,h=.08,col=(.67,.68,.64)):
 m=material(name,col,.73);nt=m.node_tree;p=nt.nodes.get('Principled BSDF')
 uv=nt.nodes.new('ShaderNodeTexCoord');tex=nt.nodes.new('ShaderNodeTexBrick');tex.offset=0.0;tex.offset_frequency=1
 tex.inputs['Scale'].default_value=1;tex.inputs['Brick Width'].default_value=w;tex.inputs['Row Height'].default_value=h;tex.inputs['Mortar Size'].default_value=min(w,h)*.028;tex.inputs['Mortar Smooth'].default_value=.002
 tex.inputs['Color1'].default_value=(*col,1);tex.inputs['Color2'].default_value=tuple(v*.99 for v in col)+(1,);tex.inputs['Mortar'].default_value=(.28,.30,.29,1)
 nt.links.new(uv.outputs['UV'],tex.inputs['Vector']);nt.links.new(tex.outputs['Color'],p.inputs['Base Color'])
 bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.18;bump.inputs['Distance'].default_value=.004;bump.invert=True;nt.links.new(tex.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs[0],p.inputs['Normal']);return m
M['white']=tilemat('Small square ceramic exterior');M['ivory']=M['white'];M['pooltile']=tilemat('Tall narrow pool ceramic tiles',.13,.52)
M['ceiling']=tilemat('600 mm ceiling panels',.6,.6,(.60,.61,.56))
M['terrazzo']=material('Fine terrazzo corridor floor',(.3,.32,.3),.43,220)
# Irregular worn turf, observed in aerial/track photographs.
M['field']=material('Uneven sports turf',(.09,.20,.035),.94)
nt=M['field'].node_tree;noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=6;noise.inputs['Detail'].default_value=3;r=nt.nodes.new('ShaderNodeValToRGB');r.color_ramp.elements[0].position=.25;r.color_ramp.elements[0].color=(.24,.16,.075,1);r.color_ramp.elements[1].position=.57;r.color_ramp.elements[1].color=(.10,.22,.045,1);nt.links.new(noise.outputs['Fac'],r.inputs[0]);nt.links.new(r.outputs[0],nt.nodes.get('Principled BSDF').inputs['Base Color'])
# Corrugated red roof microstructure.
nt=M['roof'].node_tree;wave=nt.nodes.new('ShaderNodeTexWave');wave.inputs['Scale'].default_value=7;wave.wave_type='BANDS';bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.3;bump.inputs['Distance'].default_value=.045;nt.links.new(wave.outputs['Color'],bump.inputs['Height']);nt.links.new(bump.outputs[0],nt.nodes.get('Principled BSDF').inputs['Normal'])
font=bpy.data.fonts.load(os.path.join(ROOT,'fonts','NotoSansCJKtc-Bold.otf'))
latinfont=font
def label(text,loc,size,mat='redletter',rot=(math.pi/2,0,0),vertical=False):
 cu=bpy.data.curves.new(text,'FONT');cu.body='\n'.join(text) if vertical else text;cu.size=size;cu.align_x='CENTER';cu.extrude=max(.025,size*.085);cu.bevel_depth=max(.003,size*.012);cu.bevel_resolution=3;cu.resolution_u=12
 if font:cu.font=font if any(ord(c)>127 for c in text) else latinfont
 ob=bpy.data.objects.new(text,cu);bpy.context.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=rot;cu.materials.append(M[mat]);return ob

def cylinder(b,a,c,r,mat,n=10,r2=None):
 a,c=Vector(a),Vector(c);z=(c-a).normalized();u=z.cross(Vector((0,0,1)))
 if u.length<.01:u=z.cross(Vector((1,0,0)))
 u.normalize();v=z.cross(u);vs=[]
 for p,rad in [(a,r),(c,r if r2 is None else r2)]:
  vs += [tuple(p+rad*(math.cos(i*math.tau/n)*u+math.sin(i*math.tau/n)*v)) for i in range(n)]
 b.faces(vs,[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],mat)

def arch(b,name,x,y,z,r,h,axis='Y'):
 pts=[(x-r,y,z),(x-r,y,z+h)]+[(x+r*math.cos(math.pi-i*math.pi/32),y,z+h+r*math.sin(math.pi-i*math.pi/32)) for i in range(33)]+[(x+r,y,z)]
 if axis=='X':pts=[(y,xx,zz) for xx,yy,zz in pts]
 b.faces(pts,[tuple(range(len(pts)))],'glass');line(name+' arch trim',pts,.095,'white');line(name+' arch frame',pts,.035,'frame')

def school(name,x,y,w,d,floors,pitched=True,admin=False):
 b=Mesh(name);fh=3.35;h=floors*fh;count=max(2,round(w/4.25));bay=w/count
 # Floors, spandrels, piers: no solid cube, so corridor interiors are real space.
 for k in range(floors+1):b.box(x,y,k*fh+.05,w,d,.16,'concrete')
 for side in (-1,1):
  yy=y+side*d/2
  for k in range(floors):
   z=k*fh;b.box(x,yy,z+.48,w,.26,.96,'white');b.box(x,yy,z+3.10,w,.30,.40,'white')
   for j in range(count):
    xx=x-w/2+(j+.5)*bay;b.box(xx,yy-side*.17,z+1.92,bay-.32,.055,1.9,'clear' if name=='學海南棟' and k==0 and side==1 else 'glass')
    for dx in (-bay/2+.16,0,bay/4,-bay/4,bay/2-.16):b.box(xx+dx,yy+side*.025,z+1.91,.045,.1,1.92,'frame')
    for zz in (1.0,2.39,2.85):b.box(xx,yy+side*.025,z+zz,bay-.29,.1,.055,'frame')
    b.box(xx,yy+side*.08,z+.94,bay-.28,.23,.10,'white')
   for j in range(count+1):b.box(x-w/2+j*bay,yy,z+1.66,.22,.46,3.35,'white')
  # Visible downpipes and detailed external wall corners.
  for xx in (x-w/2+.32,x+w/2-.32):line(name+' rainwater downpipe',[(xx,yy+side*.32,h),(xx,yy+side*.32,.35)],.065,'metal')
 for side in (-1,1):
  xx=x+side*w/2;b.box(xx,y,h/2,.24,d,h,'white')
  # Continuous round-ended stair windows face the athletics side.
  for k in range(floors):
   
   if name in ('學海南棟','學海北棟') and side==1:arch(b,name+' stair window',y-d*.21,xx+side*.14,k*fh+.55,.76,1.22,'X')
   else:b.box(xx+side*.14,y-d*.21,k*fh+1.85,.12,1.4,1.8,'glass')
   for jy in (-d*.05,d*.24):b.box(xx+side*.14,y+jy,k*fh+1.85,.12,1.4,1.8,'glass')
 if pitched:roof(b,x,y,w,d,h,1.65)
 else:
  for side in (-1,1):b.box(x,y+side*d/2,h+.4,w,.25,.8,'white');b.box(x+side*w/2,y,h+.4,.25,d,.8,'white')
 b.box(x,y,.14,w+.35,d+.35,.28,'concrete');o=b.finish()
 if admin:
  front=y-d/2;box(name+' recessed door',x,front-.08,1.45,5,.12,2.8,'gate');box(name+' projecting entrance canopy',x,front-1,3.45,8.5,2,.45,'white');label('德賢樓',(x,front-2.03,3.37),.46)
  for xx in (x-5,x+5):
   box('Facade AC condenser',xx,front-.3,4.2,.8,.6,.65,'concrete');line('AC refrigerant pipe',[(xx+.5,front-.36,4.2),(xx+.5,front-.36,1.1)],.022,'white')
 return o
# Track and grandstand are oblique to the classroom wings in the Maps view.
TC=(76.2,9.5);ANGLE=math.radians(32);C,S=math.cos(ANGLE),math.sin(ANGLE);DEPTH=3.2

def sport(u,v,z=0):return (TC[0]+C*u-S*v,TC[1]+S*u+C*v,z)
def local(x,y):dx,dy=x-TC[0],y-TC[1];return(C*dx+S*dy,-S*dx+C*dy)
def grade(x,y):
 u,v=local(x,y)
 if -51<v<53 and -42<u<33:
  return -DEPTH*min(1,max(0,(u+42)/12))*min(1,max(0,(33-u)/4))
 if 53<=v<86 and -29<u<29:return-DEPTH*min(1,max(0,(u+29)/4))*min(1,max(0,(29-u)/4))*min(1,(86-v)/4)
 return 0
# Explicit near-campus terrain, including the excavated sports terrace.
b=Mesh('校園地形 | oblique sunken athletics terrace');xs=list(range(-160,191,2));ys=list(range(-160,221,2));vs=[(x,y,grade(x,y)) for y in ys for x in xs];nx=len(xs);b.faces(vs,[(j*nx+i,j*nx+i+1,(j+1)*nx+i+1,(j+1)*nx+i) for j in range(len(ys)-1) for i in range(nx-1)],'grass');b.finish();box('Distant landscape',0,0,-5,2000,2000,2,'forest')
# Ground observed in map; the earlier construction clearing is not carried over.
for name,key in [('學海南棟','south'),('學海北棟','north'),('前庭西側校舍','front'),('德賢樓','admin'),('北側西區校舍','west'),('操場北側白色校舍','service')]:
 x,y,w,d,f=SITE[key];school(name,x,y,w,d,f,pitched=key not in ('west','service'),admin=key=='admin')
school('教學區中央縱廊',-12,12,11,24,3);school('教學區中央橫廊',-12,12,32,11,3)
# Front porch gable and three arched door openings.
b=Mesh('前庭拱廊入口');b.box(-10.7,-50,1.65,13.5,6,3.3,'white');roof(b,-10.7,-50,13.5,6,3.3,1.3)
for xx,r in [(-10.7,1.6),(-15.3,.85),(-6.1,.85)]:arch(b,'前庭入口',xx,-53.18,.18,r,1.65)
b.finish();b=Mesh('前庭校舍山牆');b.faces([(-17,-47.08,6.7),(-4.4,-47.08,6.7),(-10.7,-47.08,9.0)],[(0,1,2)],'white');arch(b,'前庭高層拱窗',-10.7,-47.2,6.8,.8,.75);b.finish()
# Rear dormitory: rounded corner, red bands, deep grilles, AC, open entrance void.
b=Mesh('定得樓 | rounded corner and recessed facade');x,y,w,d,_=SITE['deding'];x0,x1,y0,y1=x-w/2,x+w/2,y-d/2,y+d/2;rr=4.0
outline=[(x0,y0+rr)]+[(x0+rr+rr*math.cos(math.pi+i*math.pi/2/32),y0+rr+rr*math.sin(math.pi+i*math.pi/2/32)) for i in range(33)]+[(x1,y0),(x1,y1),(x0,y1)]
for i in range(len(outline)):
 a,c=outline[i],outline[(i+1)%len(outline)]
 if a[1]==y0 and c[1]==y0:continue
 b.faces([(*a,0),(*c,0),(*c,14.5),(*a,14.5)],[(0,1,2,3)],'white')
# Front framed openings instead of painting windows onto a solid block.
for k in range(4):
 z=k*3.5
 b.box(x,y0,z+3.25,w,.30,.5,'white')
 if k>1:b.box(x,y0,z+.6,w,.30,1.2,'white')
 else:
  for xx,ww in [(x0+7,14),(x1-9,18)]:b.box(xx,y0,z+.6,ww,.30,1.2,'white')
 for j in range(12):
  xx=x0+7.1+j*2.8
  if k<2 and x0+14<xx<x0+23:continue
  b.box(xx,y0+.22,z+1.95,1.8,.06,1.85,'glass' if j%2==0 else 'curtain')
  b.box(xx-1.15,y0,z+1.9,.46,.4,3.25,'white')
  if j%2==0:
   for dx in (-.72,-.36,0,.36,.72):b.box(xx+dx,y0-.17,z+1.92,.035,.09,1.77,'metal')
   for dz in (-.83,0,.83):b.box(xx,y0-.17,z+1.92+dz,1.58,.09,.035,'metal')
   b.box(xx,y0-.32,z+2.52,.74,.68,.48,'concrete');b.box(xx,y0-.68,z+2.52,.58,.04,.30,'metal')
for zz in (.9,3.7,7.2,10.7,14.1):line('定得樓紅色水平線',[(*p,zz) for p in outline],.027,'redletter',True)

for slabz in (.04,3.54,7.04,10.54,14.5):b.faces([(*p,slabz) for p in outline],[tuple(range(len(outline)))],'concrete')
b.finish();label('定得樓',(x0+6.3,y0-.28,10.9),.61,vertical=True)
# Angular rear block, reshaped using the visible map roof footprint.
poly=[xy(*p) for p in [(746,130),(786,120),(836,269),(794,290),(763,212)]];b=Mesh('北側中段校舍 | observed angular roof outline')
for i,a in enumerate(poly):
 c=poly[(i+1)%len(poly)];b.faces([(*a,0),(*c,0),(*c,13.4),(*a,13.4)],[(0,1,2,3)],'white')
b.faces([(*p,13.4) for p in poly],[tuple(range(len(poly)))],'concrete');b.finish()
# Broad west glazing on the rear block, supported by white piers.
b=Mesh('北側校舍玻璃立面')
for k in range(4):
 for j in range(12):b.box(-57.5,53+j*2.8,1.8+k*3.35,.15,2.4,1.85,'glass');b.box(-57.7,53+j*2.8,1.8+k*3.35,.28,.18,3.35,'white')
b.finish()
# New elementary school at the rear: Maps roof trace + official three-storey facade.
# Northern viewport measured 20 m / 72 px. Anchor is the existing Deding roof centre.
def rearxy(a,c):return (-.7+(a-799)/3.6,87.6+(696-c)/3.6)
M['primarybrick']=tilemat('小學部米色橫向面磚',.30,.075,(.49,.40,.28))
M['primaryframe']=material('小學部香檳色窗框',(.33,.30,.22),.42)
M['primaryglass']=material('小學部綠色反射玻璃',(.12,.22,.14),.15)
M['primaryglass'].node_tree.nodes.get('Principled BSDF').inputs['Metallic'].default_value=.5
# Shallow arc has a convex northern wall and a concave entrance facade facing south.
b=Mesh('雙語小學部 | 三層弧形校舍');N=36;facade=[];back=[]
for j in range(N+1):
 t=j/N;xx=-62+52*t;yy=119+5.0*math.sin(math.pi*t);facade.append((xx,yy));back.append((xx,yy+11.0))
for k in range(4):
 z=k*3.5
 for j in range(N):
  a,c=facade[j],facade[j+1];d,e=back[j+1],back[j]
  b.faces([(*a,z),(*c,z),(*d,z),(*e,z)],[(0,1,2,3)],'concrete')
for j in range(N):
 a,c=back[j],back[j+1];b.faces([(*a,0),(*c,0),(*c,10.5),(*a,10.5)],[(0,1,2,3)],'primarybrick')
for a,c in [(facade[0],back[0]),(facade[-1],back[-1])]:b.faces([(*a,0),(*c,0),(*c,10.5),(*a,10.5)],[(0,1,2,3)],'primarybrick')
for k in range(3):
 z=k*3.5
 for j in range(26):
  xx=-61+50*j/25;yy=119+5*math.sin(math.pi*(xx+62)/52)
  # Official image: tall narrow windows, stacked transoms, tiled vertical piers.
  gw=1.83 if k==0 else 1.12;fw=.94 if k==0 else .60
  if not (k==2 and j<9):b.box(xx,yy,z+1.81,gw,.08,2.82,'primaryglass')
  for dx in (-fw,fw):b.box(xx+dx,yy-.05,z+1.81,.065,.17,2.95,'primaryframe')
  for dz in (-1.46,-.95,.92,1.46):b.box(xx,yy-.06,z+1.81+dz,gw+.13,.17,.06,'primaryframe')
  b.box(xx+.91,yy+.08,z+1.75,.14 if k==0 else .64,.36,3.5,'primarybrick')
 for j in range(N):
  a,c=facade[j],facade[j+1]
  b.faces([(*a,z+.04),(*c,z+.04),(*c,z+.32),(*a,z+.32)],[(0,1,2,3)],'primarybrick')
  b.faces([(*a,z+3.16),(*c,z+3.16),(*c,z+3.50),(*a,z+3.50)],[(0,1,2,3)],'primarybrick')
# Open upper-level balcony at western end, railing matching the official photo.
for z in (7.35,10.6):
 span=facade if z>10 else facade[:14]
 pts=[(xx,yy-.65,z+.94) for xx,yy in span];line('小學部陽台與屋頂扶手',pts,.046,'primaryframe')
 pts=[(xx,yy-.65,z+.10) for xx,yy in span];line('小學部欄杆底梁',pts,.038,'primaryframe')
 for j in range(130 if z>10 else 47):
  xx=-62+52*j/129;yy=119+5*math.sin(math.pi*(xx+62)/52);cylinder(b,(xx,yy-.65,z+.10),(xx,yy-.65,z+.94),.018,'primaryframe',6)
# Actual entrance sign is traditional Chinese arranged right to left above English.
label('學 小 華 大',(-36,123.64,3.40),.73,'gold');label('TA HWA BILINGUAL ELEMENTARY SCHOOL',(-36,123.58,2.98),.29,'gold')
b.finish()
# Flat roof, parapet, end vestibules and narrow connector shown in satellite imagery.
box('小學部西端平頂翼',-64.3,135.8,2.2,16,8,4.4,'primarybrick')
for j in range(5):box('小學部西端玻璃',-70+j*2.3,131.73,2.1,1.65,.08,2.5,'primaryglass')
connector=[rearxy(*p) for p in [(590,590),(582,621),(579,661),(570,687)]]
ribbon('小學部連接通廊屋頂',connector,3.1,3.7,'concrete');ribbon('小學部連接通廊地坪',connector,3.3,.08,'paving')
for a,c in zip(connector,connector[1:]):
 av,cv=Vector(a),Vector(c)
 for j in range(max(2,int((cv-av).length/3))):
  q=av.lerp(cv,j/max(2,int((cv-av).length/3)));box('通廊支柱',q.x,q.y,1.85,.25,.25,3.7,'white')
ribbon('後側校內通道',[(-80,83),(-69,112),(-61,118),(-32,113),(12,110),(24,99)],5,.08,'asphalt')
# Rear multi-use court: same orientation and dimensions as current Maps trace.
pc=(-34,154);theta=math.radians(-17)
def primarycourt(u,v,z):return(pc[0]+math.cos(theta)*u-math.sin(theta)*v,pc[1]+math.sin(theta)*u+math.cos(theta)*v,z)
polygon('小學部後側多用途球場',[primarycourt(u,v,0)[:2] for u,v in [(-9,-14),(9,-14),(9,14),(-9,14)]],.08,'court')
for u,v,U,V in [(-7.5,-13,7.5,-13),(7.5,-13,7.5,13),(7.5,13,-7.5,13),(-7.5,13,-7.5,-13),(-7.5,0,7.5,0)]:line('小學球場白線',[primarycourt(u,v,.10),primarycourt(U,V,.10)],.04,'line')
for vv in (-13,13):
 line('小學球場罰球區',[primarycourt(u,v,.10) for u,v in [(-2.4,vv),(-2.4,vv-math.copysign(5,vv)),(2.4,vv-math.copysign(5,vv)),(2.4,vv)]],.04,'line')
 line('小學球場篮框立柱',[primarycourt(0,vv,.1),primarycourt(0,vv,3.5)],.07,'metal')
 pos=primarycourt(0,vv,3.2);o=box('小學球場篮板',*pos,1.8,.10,1.05,'white');o.rotation_euler.z=theta
line('小學球場中央圈',[primarycourt(1.8*math.cos(j*math.tau/96),1.8*math.sin(j*math.tau/96),.10) for j in range(96)],.04,'line',True)
PRIMARY_OBSERVATION={'anchor_existing_deding':[-.7,87.6],'rear_view_anchor_pixels':[799,696],'scale_metres':20,'scale_pixels':72,'roof_outline_pixels':[(575,550),(592,540),(624,531),(671,533),(715,542),(758,557),(748,591),(711,578),(669,575),(625,579),(590,592)],'floors':3,'height_estimate':10.5,'unseen_facades':'inferred'}

# Gym facade faces west onto the forecourt, as explicitly corrected by the user.
gx,gy,gw,gd,_=SITE['gym'];front=gx-gw/2;b=Mesh('凱旋樓 | lawn-facing glazing and projecting side blocks')
b.box(gx,gy,5.25,gw,gd,10.5,'white');roof(b,gx,gy,gw,gd,10.5,1.8)
for k in range(8):
 yy=gy-gd/2+2+(k+.5)*(gd-4)/8;b.box(front-.16,yy,8.7,.12,2.9,2.0,'curtain')
 for dy in (-1.45,-.72,0,.72,1.45):b.box(front-.28,yy+dy,8.7,.10,.045,2.05,'frame')
 for z in (7.67,9.14,9.73):b.box(front-.28,yy,z,.1,2.9,.045,'frame')
 b.box(front-.46,yy+1.68,6.35,.63,.30,7.8,'white')
b.box(front-.05,gy,2.15,.12,gd-9,3.7,'glass');b.box(front-.8,gy,4.35,1.6,gd-8,.68,'white')
for yy in (gy-gd/2+2.5,gy+gd/2-2.5):b.box(front-1.35,yy,3.55,2.7,5.5,7.1,'white')
for j in range(11):
 yy=gy-(gd-9)/2+j*(gd-9)/10;b.box(front-.23,yy,2.15,.12,.055,3.8,'frame')
 if j%2:b.box(front-.37,yy+.32,1.6,.12,.035,.50,'metal')
b.box(front-2,gy,.10,4,gd+.8,.2,'concrete');b.finish();label('凱旋樓',(front-2.72,gy-gd/2+2.5,6.45),.60,rot=(math.pi/2,0,-math.pi/2),vertical=True);label('學生活動中心',(front-2.73,gy-gd/2+4.5,5.4),.32,rot=(math.pi/2,0,-math.pi/2),vertical=True)
# Solar modules visibly present on the Maps roofs; capture date is not inferred.
def solarroof(name,x,y,w,d,z):
 b=Mesh(name)
 for xx in range(int(-w/2)+2,int(w/2)-1,2):
  for yy in range(int(-d/2)+2,int(d/2)-1,3):
   b.box(x+xx,y+yy,z+.18,1.7,2.6,.10,'solar')
   for dx in (-.83,0,.83):b.box(x+xx+dx,y+yy,z+.25,.025,2.55,.025,'frame')
   for dy in (-1.28,-.86,-.43,0,.43,.86,1.28):b.box(x+xx,y+yy+dy,z+.25,1.65,.023,.018,'frame')
 b.finish()
solarroof('定得樓屋頂可見太陽能板',-.7,87.6,37,25,14.6);solarroof('西側校舍屋頂可見太陽能板',-78.5,80.5,27,14,13.5)
solarroof('北側中段屋頂太陽能板',-49.5,70,8,29,13.5)
# Gym's two panel fields follow the shallow hip-roof slopes.
b=Mesh('凱旋樓屋頂太陽能模組')
for side in (-1,1):
 for j in range(7):
  yy=gy-9+j*2.8
  for k in range(4):
   xx=gx+side*(2.2+k*1.9);z=12.3-(abs(xx-gx)/((gw+1)/2))*1.8+.17
   b.box(xx,yy,z,1.7,2.5,.10,'solar')
   for dy in (-1.2,-.6,0,.6,1.2):b.box(xx,yy+dy,z+.07,1.68,.025,.025,'frame')
 b.box(gx,gy,12.4,.12,gd-6,.14,'metal')
b.finish()
# Paving and mapped site circulation, aligned obliquely along Sanmin Rd.
road=[xy(*p) for p in [(585,60),(590,190),(665,375),(800,620),(1020,910),(1250,1120)]];ribbon('三民路二段 | map-aligned road',road,9,.07,'asphalt')
for i in range(len(road)-1):
 a,c=Vector(road[i]),Vector(road[i+1]);length=(c-a).length
 for j in range(int(length/8)):
  p=a.lerp(c,(j+.2)/max(1,int(length/8)));q=a.lerp(c,(j+.6)/max(1,int(length/8)));line('Road centre marking',[(*p,.11),(*q,.11)],.055,'line')
forecourt=[xy(*p) for p in [(915,719),(1180,710),(1260,787),(1240,924),(1080,940),(967,840)]];polygon('前庭鋪面',forecourt,.09,'paving')
# Irregular kidney lawn, crescent shrubbery and sculptural monument.
lx,ly=xy(1110,812);lawn=[]
for i in range(128):
 a=i*math.tau/128;r=1+.075*math.cos(3*a);lawn.append((lx+24*math.cos(a)*r,ly+18.5*math.sin(a)*r))
polygon('前庭中央草坪',lawn,.14,'grass');line('前庭草坪石材緣',[(x,y,.16) for x,y in lawn],.11,'concrete',True)
# Internal vehicle way around the east of gym and athletics.
route=[xy(*p) for p in [(1280,1010),(1405,904),(1457,802),(1416,710),(1453,643),(1590,576),(1660,535)]];ribbon('校園東側彎道路線',route,7,.08,'asphalt')
for x,y,w,d in [(-12,-23,63,1.8),(5,44,40,3),(-29,12,2.0,61),(25,-52,66,1.8)]:box('Campus footpath',x,y,.11,w,d,.12,'paving')
# Burgundy entrance gateway and chain-link gates, reconstructed from supplied close photo.
gateSet=set(bpy.data.objects);b=Mesh('校門 | burgundy clad piers')
for xx in (-5.5,5.5):b.box(xx,0,2.2,1.0,1.0,4.4,'gate')
b.box(0,0,4.65,13,1.15,.48,'gate');b.box(0,0,3.85,11,.8,.65,'gate');b.finish();label('TA HWA HIGH SCHOOL',(0,-.61,4.55),.27,'gold');label('私立大華中學',(0,-.45,3.75),.43,'gold')
b=Mesh('校門金屬門扇')
for xx in (-2.45,2.45):
 for dx in (-2.4,2.4):b.box(xx+dx,-.10,1.52,.065,.08,2.9,'metal')
 for zz in (.15,1.7,2.95):b.box(xx,-.10,zz,4.8,.08,.045,'metal')
 for j in range(23):
  yy=-.14;x=-4.8+j*.42;line('Gate diamond wire',[(x,yy,.18),(min(4.8,x+2.7),yy,2.9)],.007,'metal')
  line('Gate diamond wire',[(x,yy,2.9),(min(4.8,x+2.7),yy,.18)],.007,'metal')
b.finish()
bpy.context.view_layer.update()
for ob in set(bpy.data.objects)-gateSet:
 ob.matrix_world=Matrix.Translation(Vector((12,-99,0)))@Matrix.Rotation(ANGLE,4,'Z')@ob.matrix_world
# Confucius monument: stepped carved pedestal and robe silhouette.
b=Mesh('孔子像 | bronze robe sculpture and carved pedestal')
mx,my=lx-1,ly+1
for z,w,d,h in [(.14,2.0,1.65,.28),(.42,1.55,1.3,.25),(.90,1.28,1.10,.72),(1.34,1.48,1.26,.18)]:b.box(mx,my,z,w,d,h,'concrete')
# Twelve-sided tapered robe; folded hands and sleeves are sculptural approximations.
cylinder(b,(mx,my,1.4),(mx,my,3.05),.42,'bronze',n=18,r2=.27)
cylinder(b,(mx,my,3.0),(mx,my,3.25),.115,'bronze',n=12,r2=.11)
cylinder(b,(mx,my,3.2),(mx,my,3.62),.18,'bronze',n=16,r2=.15)
for side in (-1,1):
 cylinder(b,(mx+side*.28,my,2.85),(mx+side*.43,my-.25,2.25),.15,'bronze',12,r2=.13);cylinder(b,(mx+side*.43,my-.25,2.25),(mx+side*.05,my-.36,2.47),.13,'bronze',12,r2=.08)
for i in range(12):
 a=i*math.tau/12;line('孔子像衣褶',[(mx+.41*math.cos(a),my+.41*math.sin(a),1.5),(mx+.27*math.cos(a),my+.27*math.sin(a),2.8)],.015,'bronze')
b.finish();label('至聖先師',(mx,my-.566,1.00),.19,'gate');label('孔子',(mx,my-.567,.73),.16,'gate')
box('前庭校名木牌',lx-12,ly-5,1.05,3.8,.15,.64,'wood');label('私立大華中學',(lx-12,ly-5-.09,1.0),.27,'gold')
for xx in (lx-13.3,lx-10.7):box('校名木牌支柱',xx,ly-5,.45,.11,.13,.9,'wood')
# Forecourt flagpoles; no arbitrary classroom numbers/signage are added.
for xx in (-5,0,5):
 line('前庭旗桿',[(xx,-50,0),(xx,-50,9.5)],.048,'metal');box('旗桿座',xx,-50,.14,.5,.5,.28,'concrete')
 b=Mesh('校園旗幟');vs=[(xx+i*.10,-50+.08*math.sin(i*.45+j*.3),8.9-j*.09) for j in range(9) for i in range(16)];b.faces(vs,[(j*16+i,j*16+i+1,(j+1)*16+i+1,(j+1)*16+i) for j in range(8) for i in range(15)],'redletter' if xx==0 else 'blue');b.finish()
 if xx==0:
  polygon('國旗藍色旗角',[(xx,-50-.01),(xx+.68,-50-.01),(xx+.68,-50-.01)],8.85,'blue')
# Covered green glazed passage connects the front buildings, with purple flowering vines.
b=Mesh('前庭外環風雨走廊 | green glazed canopy')
for i in range(11):
 xx=-10+i*2.6;b.box(xx,-41,1.35,.09,.09,2.7,'frame')
 for side in (-1,1):b.box(xx,-41+side*1.25,2.72,.08,.08,.6,'frame')
for side in (-1,1):
 b.faces([(-10,-41,3.15),(19,-41,3.15),(19,-41+side*1.4,2.7),(-10,-41+side*1.4,2.7)],[(0,1,2,3)],'glassgreen')
b.finish()
# Internal corridor, based on the supplied photo (not a guessed classroom interior).
b=Mesh('學海南棟一樓 | glazed corridor interior');x0,x1=-45,21;outer=-1.15;inner=-3.55
b.box((x0+x1)/2,-2.35,.12,x1-x0,2.4,.10,'terrazzo');b.box((x0+x1)/2,-2.35,3.05,x1-x0,2.4,.12,'ceiling');b.box((x0+x1)/2,inner,1.5,x1-x0,.16,3,'white')
for xx in range(-41,20,7):
 b.box(xx,inner-.04,1.42,1.2,.18,2.75,'frame');b.box(xx,inner+.06,1.39,1.05,.08,2.63,'wood');b.box(xx,inner+.11,2.12,.8,.04,.55,'glass')
 b.box(xx+2.45,inner+.13,1.7,2.6,.055,1.22,'notice')
 for dx in (-1.31,1.31):b.box(xx+2.45+dx,inner+.18,1.7,.05,.09,1.25,'metal')
 b.box(xx+2.45,inner+.2,1.7,2.45,.022,1.10,'glassgreen')
 b.box(xx+.45,inner+.2,1.0,.03,.05,.12,'metal')
 for j in range(4):b.box(xx+1.7+j*.43,inner+.22,1.8,.27,.015,.50,'line')
b.finish()
for xx in range(-38,20,10):
 box('Corridor linear light fitting',xx,-2.35,2.94,1.2,.18,.06,'white');bpy.ops.object.light_add(type='AREA',location=(xx,-2.35,2.91));o=bpy.context.object;o.name='Corridor ceiling soft light';o.data.energy=38;o.data.use_shadow=False;o.data.shape='RECTANGLE';o.data.size=1.3;o.data.size_y=.2
# World-coordinate fine terrazzo texture.
nt=M['terrazzo'].node_tree;g=nt.nodes.new('ShaderNodeNewGeometry')
for n in nt.nodes:
 if n.bl_idname=='ShaderNodeTexNoise':nt.links.new(g.outputs['Position'],n.inputs['Vector'])
# Raised circular courtyard fountain, tall exterior tiles, cobalt lining and water.
px,py=xy(1020,611);b=Mesh('教學區水池 | layered coping and raised ceramic wall');N=128
for i in range(N):
 a,c=i*math.tau/N,(i+1)*math.tau/N
 def vv(r,t,z):return(px+r*math.cos(t),py+r*math.sin(t),z)
 b.faces([vv(2.72,a,.13),vv(2.72,c,.13),vv(2.72,c,.65),vv(2.72,a,.65)],[(0,1,2,3)],'pooltile')
 b.faces([vv(2.48,a,.22),vv(2.48,c,.22),vv(2.48,c,.64),vv(2.48,a,.64)],[(0,3,2,1)],'tileblue')
 b.faces([vv(2.83,a,.65),vv(2.83,c,.65),vv(2.43,c,.65),vv(2.43,a,.65)],[(0,1,2,3)],'white')
b.finish();polygon('水池水面',[(px+2.48*math.cos(i*math.tau/N),py+2.48*math.sin(i*math.tau/N)) for i in range(N)],.49,'water')
line('Water nozzle',[(px,py,.30),(px,py,.9)],.05,'metal')
for k in range(9):
 a=k*math.tau/9;line('White fountain stream',[(px+.38*t*math.cos(a),py+.38*t*math.sin(a),1.55-.98*t*t) for t in [i/24 for i in range(25)]],.011,'foam')
line('Fountain rising jet',[(px,py,.87),(px,py,1.58)],.022,'foam')
nt=M['water'].node_tree;wv=nt.nodes.new('ShaderNodeTexWave');wv.wave_type='RINGS';wv.rings_direction='Z';wv.inputs['Scale'].default_value=10;wv.inputs['Distortion'].default_value=.8;wv.inputs['Phase Offset'].driver_add('default_value').driver.expression='frame*0.075';bu=nt.nodes.new('ShaderNodeBump');bu.inputs['Strength'].default_value=.22;bu.inputs['Distance'].default_value=.025;nt.links.new(wv.outputs['Color'],bu.inputs['Height']);nt.links.new(bu.outputs[0],nt.nodes.get('Principled BSDF').inputs['Normal'])
line('Pool surrounding brick border',[(px+3.10*math.cos(i*math.tau/N),py+3.10*math.sin(i*math.tau/N),.14) for i in range(N)],.20,'paving',True)
# Sports geometry in local u/v coordinates, then rotated into the calibrated site.
sportsSet=set(bpy.data.objects)
def stadium4(r,straight=44):
 pts=[]
 for i in range(65):
  a=math.pi*i/64;pts.append((r*math.cos(a),straight/2+r*math.sin(a)))
 for i in range(65):
  a=math.pi+math.pi*i/64;pts.append((r*math.cos(a),-straight/2+r*math.sin(a)))
 return pts
polygon('跑道紅色橢圓',stadium4(23.4),-DEPTH+.035,'track');polygon('操場斑駁草坪',stadium4(17.0),-DEPTH+.05,'field')
for j in range(7):line('Six-lane track stripe',[(u,v,-DEPTH+.064) for u,v in stadium4(17.0+j*1.065)],.027,'line',True)
box('直線跑道延伸',-20.2,-2,-DEPTH+.03,6.4,98,.07,'track');box('Blue track edge',-25.3,0,-DEPTH+.05,1.15,100,.04,'blue');box('Green field side apron',-26.65,0,-DEPTH+.05,1.4,100,.04,'court')
for j in range(7):box('Sprint lane stripe',-23.4+j*1.065,-2,-DEPTH+.07,.055,98,.025,'line')
for j in range(6):
 u=-22.86+j*1.065;label(str(j+1),(u,-38,-DEPTH+.077),.68,'line',rot=(0,0,0))
for v in (-38,-37.6):box('Finish markings',-20.2,v,-DEPTH+.07,6.4,.075,.025,'line')
# Dark, weathered concrete seats and lighter individual stair aisles.
b=Mesh('操場看台 | deep weathered stepped bank')
for i in range(16):
 u=-42+(i+.5)*.75;top=-.02-i*.21
 for vc,vd in [(-31,40),(32,42)]:b.box(u,vc,(top-3.5)/2,.75,vd,top+3.5,'bank')
 # Horizontal tread nose, a source-visible highlight on each tier.
 for vc,vd in [(-31,40),(32,42)]:b.box(u+.32,vc,top+.01,.065,vd,.04,'concrete')
for v in (-40,-18,19,44):
 for i in range(32):b.box(-42+(i+.5)*.375,v,-.04-i*.1,.375,1.8,.12,'concrete')
 line('Stair handrail', [(-42,v+.9,1.05),(-30,v+.9,-2.12)],.029,'metal')
 for j in range(5):
  u=-42+j*3;z=1.05-j*.8;line('Stair handrail support',[(u,v+.9,z-1),(u,v+.9,z)],.022,'metal')
b.finish()
# Rounded white railing modules along the upper promenade.
for i in range(103):
 v=-51+i;pts=[(-42.7,v,.02),(-42.7,v,.70)]+[(-42.7,v+.35-.35*math.cos(t*math.pi/12),.70+.30*math.sin(t*math.pi/12)) for t in range(13)]+[(-42.7,v+.70,.02)];line('看台上緣圓弧欄杆',pts,.025,'white')
# Covered platform with the characteristic slanting/V shaped columns.
b=Mesh('操場中央遮棚 | slanted V piers');b.box(-36,0,1.35,13,22,.28,'white');b.box(-36,0,-2.62,12,20,.22,'concrete');b.box(-42.2,0,-1.5,.30,20,3,'white')
for v in (-8,8):
 cylinder(b,(-31.6,v,-2.5),(-36.5,v,1.2),.32,'white',n=8,r2=.38)
 cylinder(b,(-40.8,v,-2.5),(-37.1,v,1.2),.28,'white',n=8,r2=.38)
for i in range(7):b.box(-29.6+i*.22,0,-3.2+i*.09,.22,3.3,.13,'white')
b.finish()
# Perimeter retaining masonry and grass-side earth slope are part of the terrain.
box('North court retaining wall',-28,69,-1.6,.30,31,3.2,'bank')
for v in (-34,-8,22,47):
 line('Athletics lighting pole',[(-28.2,v,-3.2),(-28.2,v,5.7)],.075,'metal');box('Athletics light luminaire',-28.2,v,5.75,.72,.34,.16,'white')
# Two courts at the north end, following the map's placement and orientation.
box('雙籃球場底面',0,68,-DEPTH+.05,35,25,.09,'court')
for u in (-8.6,8.6):
 for du in (-7.1,7.1):line('Basketball side',[(u+du,56.6,-3.11),(u+du,79.4,-3.11)],.025,'line')
 for v in (56.6,68,79.4):line('Basketball baseline',[(u-7.1,v,-3.11),(u+7.1,v,-3.11)],.025,'line')
 line('Basketball centre circle',[(u+1.8*math.cos(i*math.tau/64),68+1.8*math.sin(i*math.tau/64),-3.10) for i in range(64)],.025,'line',True)
 for v,sign in [(56.6,1),(79.4,-1)]:
  line('Basketball key',[(u-2.1,v,-3.1),(u-2.1,v+sign*4.8,-3.1),(u+2.1,v+sign*4.8,-3.1),(u+2.1,v,-3.1)],.025,'line')
  line('Basketball three point arc',[(u+5.9*math.cos(i*math.pi/48),v+sign*5.9*math.sin(i*math.pi/48),-3.1) for i in range(49)],.025,'line')
  line('Basketball stanchion',[(u,v-sign*.55,-3.2),(u,v-sign*.55,.1),(u,v+.12*sign,.1)],.06,'metal');box('Basketball backboard',u,v,.25,1.3,.075,.78,'white');line('Basketball hoop',[(u+.23*math.cos(i*math.tau/40),v+sign*.35+.23*math.sin(i*math.tau/40),-.02) for i in range(40)],.025,'redletter',True)
for v in (-26,26):
 line('操場小型球門框',[(-1.8,v,-3.14),(-1.8,v,-1.2),(1.8,v,-1.2),(1.8,v,-3.14)],.035,'white')
 for j in range(13):line('Goal net vertical', [(-1.8+j*.3,v,-1.2),(-1.8+j*.3,v+.65,-3.14)],.004,'line')
for ob in set(bpy.data.objects)-sportsSet:ob.matrix_world=Matrix.Translation(Vector((*TC,0)))@Matrix.Rotation(ANGLE,4,'Z')@ob.matrix_world
# Fine geometry landscaping: leaf cards and branches instead of smooth cartoon balls.
leafcols=[(.055,.16,.024),(.085,.23,.034),(.12,.27,.046),(.055,.18,.07),(.16,.30,.06)]
for i,col in enumerate(leafcols):
 M['leaf%d'%i]=material('Leaf variation %d'%i,col,.76,0);M['leaf%d'%i].node_tree.nodes.get('Principled BSDF').inputs['Subsurface Weight'].default_value=.04
M['flower']=material('Bougainvillea and flowering tree bracts',(.40,.025,.18),.8)
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1);proto=bpy.context.object;rockmesh=proto.data.copy();bpy.data.objects.remove(proto,do_unlink=True)
def leaves(b,centre,r,count,flower=False):
 centre=Vector(centre)
 for j in range(count):
  p=centre+Vector((random.uniform(-r,r),random.uniform(-r,r),random.uniform(-r*.5,r*.5)));a=random.random()*math.tau;n=Vector((random.uniform(-1,1),random.uniform(-1,1),random.uniform(.1,1))).normalized();u=n.cross(Vector((0,0,1)))
  if u.length<.01:u=Vector((1,0,0))
  u.normalize();v=n.cross(u);size=random.uniform(.09,.19) if not flower else random.uniform(.04,.08)
  b.faces([tuple(p-u*size),tuple(p+v*size*.42),tuple(p+u*size),tuple(p-v*size*.42),tuple(p+n*size*.12)],[(0,1,4),(1,2,4),(2,3,4),(3,0,4)],'flower' if flower else 'leaf%d'%random.randrange(5))
def treeproto(kind,detail):
 b=Mesh('Organic tree prototype');cylinder(b,(0,0,0),(.15,.12,4.4),.17,'trunk',10,r2=.065)
 if kind=='pine':
  for tier in range(8):
   z=1.8+tier*.8;r=2.5-tier*.26
   for j in range(6):
    a=j*math.tau/6+tier*.25;tip=(r*math.cos(a),r*math.sin(a),z+.28);cylinder(b,(0,0,z),tip,.045,'trunk',6,r2=.012);leaves(b,tip,.65,80 if detail else 15)
 else:
  for j in range(12):
   a=j*math.tau/12;tip=(2.2*math.cos(a),2.2*math.sin(a),3.5+random.uniform(.2,2));cylinder(b,(.1,.1,1.8),tip,.07,'trunk',8,r2=.014)
   for k in range(3):
    cen=(tip[0]+random.uniform(-.6,.6),tip[1]+random.uniform(-.6,.6),tip[2]+random.uniform(-.3,.7))
    if detail:leaves(b,cen,.85,95)
    else:b.faces([(v.co.x*.78+cen[0],v.co.y*.78+cen[1],v.co.z*.58+cen[2]) for v in rockmesh.vertices],[tuple(p.vertices) for p in rockmesh.polygons],'leaf%d'%random.randrange(5))
 o=b.finish();me=o.data
 for poly in me.polygons:poly.use_smooth=True
 bpy.data.objects.remove(o,do_unlink=True);return me
heromeshes=[treeproto('broad',True) for i in range(3)];forestmeshes=[treeproto('broad',False) for i in range(3)];pinemesh=treeproto('pine',True)
def tree4(x,y,size=1,hero=False,pine=False,name='Landscape tree'):
 o=bpy.data.objects.new(name,pinemesh if pine else random.choice(heromeshes if hero else forestmeshes));bpy.context.collection.objects.link(o);o.location=(x,y,grade(x,y));o.scale=(size,size,size);o.rotation_euler.z=random.random()*math.tau;return o
# Avoid the camera paths and reveal the architectural details.
for x,y in [(-23,-49),(-21,-28),(-2,-15),(12,-18),(21,-26),(47,-54),(49,-111),(-40,7),(-35,23),(15,23),(23,40),(-50,45),(-76,52),(-80,147),(26,110),(35,73)]:tree4(x,y,random.uniform(.85,1.25),True,pine=(x,y)==(-23,-49))
for x,y in [(lx-7,ly+3),(lx-3,ly+6),(lx+2,ly+5),(lx+6,ly+1),(lx+6,ly-3)]:
 o=tree4(x,y,.55,True,name='前庭修剪喬木');o.scale.z=.45
# Small close hedges include visible leaf texture and twig structure.
def shrub(name,x,y,w,d,h,flower=False):
 b=Mesh(name);centres=max(1,int(w/.5))
 for j in range(centres):leaves(b,(x-w/2+(j+.5)*w/centres,y,h*.67),max(.32,d*.55),170);cylinder(b,(x-w/2+(j+.5)*w/centres,y,0),(x-w/2+(j+.5)*w/centres,y,h*.65),.02,'trunk',6)
 if flower:
  for j in range(centres):leaves(b,(x-w/2+(j+.5)*w/centres,y,h*.80),.38,16,True)
 return b.finish()
for x,y,w,d,h in [(29.8,-48.4,30,1.0,.8),(13.8,-39,1.1,14,.9),(-11,-56,12,1.2,.65),(-8,-51,12,1.1,.6),(-5,-19,8,1.2,.7),(13,-19,8,1.2,.8),(-4,-32,5,1.2,.6)]:shrub('修剪綠籬',x,y,w,d,h,flower=y==-19)
for i in range(21):
 a=math.radians(30+i*12);x=lx+5.5*math.cos(a);y=ly+3.8*math.sin(a);shrub('孔子像月牙綠籬',x,y,1.0,.8,1.05)
for j in range(11):
 x=-10+j*2.6;b=Mesh('風雨走廊紫紅花藤');leaves(b,(x,-41,3.14),.8,75);leaves(b,(x,-41,3.35),.80,30,True);b.finish()
for x,y,sz in [(12,-20,1.15),(-2,-21,.7),(-4,-31,.45)]:
 me=rockmesh.copy();me.materials.clear();me.materials.append(M['rock']);o=bpy.data.objects.new('水池景石',me);bpy.context.collection.objects.link(o);o.location=(x,y,sz*.62);o.scale=(sz,sz*.7,sz*1.45)
# Terrain-context trees follow the actual diagonal boundaries rather than a square grid.
for i in range(700):
 x=random.uniform(-150,175);y=random.uniform(-150,160);u,v=local(x,y)
 if -108<x<48 and -145<y<182:continue
 if -46<u<42 and -58<v<91:continue
 if 49<x<94 and -111<y<-57:continue
 tree4(x,y,random.uniform(.7,1.45))
for x in range(117,260,7):
 for y in range(-100,191,8):tree4(x+random.uniform(-2,2),y+random.uniform(-2,2),random.uniform(.8,1.55))
# Visible grass blades around the pool and forecourt, without dense whole-campus scatter.
b=Mesh('近景草葉')
for region in [(px,py,13,9),(lx,ly,21,16)]:
 xx,yy,w,d=region
 for i in range(3500):
  x=xx+random.uniform(-w,w);y=yy+random.uniform(-d,d)
  if region[0]==px and (x-px)**2+(y-py)**2<3.2**2:continue
  h=random.uniform(.045,.13);a=random.random()*math.tau;b.faces([(x-.025*math.cos(a),y-.025*math.sin(a),.15),(x+.025*math.cos(a),y+.025*math.sin(a),.15),(x+.02,y+.01,.15+h)],[(0,1,2)],'leaf%d'%random.randrange(5))
b.finish()
# Garden plaque, globe lamps and benches visible in supplied photos.
box('前庭說明牌立柱',lx-13,ly+1,.65,.20,.22,1.3,'wood');o=box('前庭斜面說明牌',lx-13,ly+1,1.39,1.9,1.1,.08,'metal');o.rotation_euler.x=.3
for x,y in [(8,-59),(-20,-55),(35,-61)]:
 line('前庭路燈',[(x,y,.1),(x,y,3.0)],.045,'metal');box('路燈燈罩',x,y,3.0,.24,.24,.36,'white')
for x,y in [(14,-32),(-7,-29)]:
 box('庭園長椅',x,y,.50,2.0,.5,.08,'wood')
 for dx in (-.75,.75):box('庭園長椅腳',x+dx,y,.27,.05,.4,.50,'metal')
# Rough neighbouring massing is kept subordinate to the campus.
for i in range(15):school('西側周邊建築',-132+(i%3)*13,5+(i//3)*26,10,15,3,pitched=True)
# Architectural edges with small bevels give natural highlight depth.
for ob in list(bpy.data.objects):
 if ob.type=='MESH' and any(n in ob.name for n in ['凱旋樓 |','定得樓 |','校門 |','德賢樓','前庭拱廊','水池 |','中央遮棚']):
  mod=ob.modifiers.new('微小建築倒角','BEVEL');mod.width=.018;mod.segments=2
# Correct flag corner and 12-point sun as geometry; no external flag image.
for ob in list(bpy.data.objects):
 if ob.name.startswith('國旗藍色旗角'):bpy.data.objects.remove(ob,do_unlink=True)
b=Mesh('國旗藍色旗角及白日');b.faces([(0,-50.15,8.9),(.68,-50.15,8.9),(.68,-50.15,8.45),(0,-50.15,8.45)],[(0,1,2,3)],'blue')
cx,cz=.34,8.675
for j in range(12):
 a=j*math.tau/12;a0=a-.13;a1=a+.13;b.faces([(cx+.08*math.cos(a0),-50.16,cz+.08*math.sin(a0)),(cx+.14*math.cos(a),-50.16,cz+.14*math.sin(a)),(cx+.08*math.cos(a1),-50.16,cz+.08*math.sin(a1))],[(0,1,2)],'white')
b.faces([(cx+.071*math.cos(j*math.tau/48),-50.17,cz+.071*math.sin(j*math.tau/48)) for j in range(48)],[tuple(range(48))],'white');b.finish()
exec(compile(open(os.path.join(ROOT,'architecture_details.py')).read(),'architecture_details.py','exec'),globals())
exec(compile(open(os.path.join(ROOT,'walking_students.py')).read(),'walking_students.py','exec'),globals())
# Lighting and camera: native 24 fps, 94 seconds; no duplicated still frames.
scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=2560;scene.render.resolution_y=1440;scene.render.resolution_percentage=100;scene.render.fps=24;scene.frame_start=1;scene.frame_end=2256;scene.eevee.taa_render_samples=32;scene.eevee.use_raytracing=False;scene.eevee.use_fast_gi=True;scene.eevee.shadow_ray_count=2
world=bpy.data.worlds.new('V4 natural campus daylight');world.use_nodes=True;sky=world.node_tree.nodes.new('ShaderNodeTexSky');sky.sky_type='MULTIPLE_SCATTERING';sky.sun_elevation=.65;sky.sun_rotation=2.2;sky.sun_disc=False;world.node_tree.links.new(sky.outputs['Color'],world.node_tree.nodes['Background'].inputs['Color']);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.15;scene.world=world
bpy.ops.object.light_add(type='SUN',location=(0,0,90));sun=bpy.context.object;sun.name='柔和校園日光';sun.rotation_euler=(math.radians(28),math.radians(-18),math.radians(-32));sun.data.energy=2.4;sun.data.angle=math.radians(2.2);scene.view_settings.view_transform='AgX';scene.view_settings.exposure=-.25
try:scene.view_settings.look='AgX - Medium High Contrast'
except TypeError:pass
# Set the water texture's ring origin to the actual fountain nozzle.
nt=M['water'].node_tree;coord=nt.nodes.new('ShaderNodeTexCoord');empty=bpy.data.objects.new('水波圓心',None);bpy.context.collection.objects.link(empty);empty.location=(px,py,.49);coord.object=empty;nt.links.new(coord.outputs['Object'],wv.inputs['Vector'])
# Real source dimensions are not available; this is a calibrated visual reconstruction.
shots=[
 ('校園配置全景',9,(-140,-160,105),(-95,-120,85),(5,5,1),(5,5,1),32),
 ('校門銘牌與門扇',6,(30,-126,3.3),(21,-120,4.3),(12,-99,3),(12,-99,3),45),
 ('前庭孔子像',4,(5,-87,3),(15,-92,3.8),(lx-1,ly+1,2.5),(lx-1,ly+1,2.5),50),
 ('德賢樓與風雨走廊',9,(10,-70,3),(47,-66,4.1),(29.8,-46,3.7),(29.8,-46,3.7),36),
 ('凱旋樓面向草地的入口',9,(40,-103,4),(41,-77,5),(63,-84,5),(63,-84,5),32),
 ('教學區水池與庭園',11,(-3,-35,2.4),(14,-36,2.7),(px,py,1.4),(px,py,2.3),30),
 ('四層校舍窗帶與端面',7,(-18,-35,10),(15,-30,12),(-10,-7,7.5),(6,-7,7.5),36),
 ('國高中學生步行',3,(0,0,0),(0,0,0),(0,0,0),(0,0,0),40),
 ('教學區一樓走廊內景',8,(-37,-2.35,1.65),(-26,-2.35,1.65),(-17,-2.35,1.65),(-6,-2.35,1.65),24),
 ('定得樓完整立面與入口',10,(35,50,5),(39,65,9),(0,77,7),(0,80,9),33),
 ('後側雙語小學弧形校舍',4,(-38,105,3.7),(-53,106,4.8),(-36,124,5),(-44,123,5.8),28),
 ('小學部學生步行',3,(0,0,0),(0,0,0),(0,0,0),(0,0,0),42),
 ('看台俯視操場高差',4,sport(-39,-34,2.0),sport(-38,-22,1.7),sport(5,6,-3.1),sport(3,15,-3.1),28),
 ('下沉操場與斜柱遮棚',3,sport(22,-23,.5),sport(24,0,1.2),sport(-35,0,-1),sport(-35,10,-1.5),24),
 ('收束校園全景',4,(175,-40,125),(140,140,140),(5,10,1),(5,10,1),32)]
camdata=bpy.data.cameras.new('V4 campus tour camera');cam=bpy.data.objects.new('V4 campus tour camera',camdata);bpy.context.collection.objects.link(cam);scene.camera=cam;camdata.clip_start=.08;camdata.clip_end=2500
manifest=[];frame=1;collisions=[]
for name,duration,pa,pb,ta,tb,lens in shots:
 start,end=frame,frame+duration*24-1;prev=None
 for f in range(start,end+1):
  t=(f-start)/(end-start);t=t*t*(3-2*t);loc=Vector(pa).lerp(Vector(pb),t);target=Vector(ta).lerp(Vector(tb),t)
  if name in ('國高中學生步行','小學部學生步行'):
   who=bpy.data.objects['Student 44 | junior' if name=='國高中學生步行' else 'Student 46 | primary-sailor'];pos,direction=student_path_at(who,f);other=bpy.data.objects['Student 45 | senior-formal' if name=='國高中學生步行' else 'Student 47 | primary-sport'];pos2,_=student_path_at(other,f);mid=(pos+pos2)/2;side=Vector((-direction.y,direction.x,0));loc=mid+direction*4.4-side*3.0+Vector((0,0,1.55 if name=='國高中學生步行' else 1.35));target=mid+Vector((0,0,.95 if name=='國高中學生步行' else .78))
  # Audit every camera frame against the primary architecture; corridor is intentional.
  if '內景' not in name:
   if -62<loc.x<-10 and 119<loc.y<135 and .1<loc.z<10.5:collisions.append((f,name,'primary'))
   for key,(xx,yy,w,d,n) in SITE.items():
    hh=10.5 if key=='gym' else n*3.35
    if xx-w/2+.1<loc.x<xx+w/2-.1 and yy-d/2+.1<loc.y<yy+d/2-.1 and .1<loc.z<hh:collisions.append((f,name,key))
  cam.location=loc;e=(target-loc).to_track_quat('-Z','Y').to_euler()
  if prev:e.make_compatible(prev)
  cam.rotation_euler=e;prev=e.copy();camdata.lens=lens;cam.keyframe_insert(data_path='location',frame=f);cam.keyframe_insert(data_path='rotation_euler',frame=f);camdata.keyframe_insert(data_path='lens',frame=f)
 scene.timeline_markers.new(name,frame=start);manifest.append(dict(name=name,start=start,end=end,seconds=duration));frame=end+1
assert frame-1==2256,frame
assert not collisions,collisions[:12]
# Portable lettering meshes; proprietary system fonts are not packed into the model.
bpy.ops.object.select_all(action='DESELECT')
for ob in list(bpy.data.objects):
 if ob.type=='FONT':bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.convert(target='MESH');ob.select_set(False)
for cu in list(bpy.data.curves):
 if cu.users==0:bpy.data.curves.remove(cu)
for ft in list(bpy.data.fonts):bpy.data.fonts.remove(ft,do_unlink=True)
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.shading.color_type='MATERIAL'
scene.frame_set(1);scene['version']='5.0 — calibrated site geometry, photo-informed exterior and corridor, natural landscaping';scene['accuracy']='Maps visible scale 20m/84px; metric sizes, roof footprints, grade depth and unobserved details remain approximate.'
scene.render.image_settings.file_format='PNG';scene.render.filepath=os.path.join(ROOT,'preview.png');bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'dahua-campus-v5.blend'))
with open(os.path.join(ROOT,'shots.json'),'w') as f:json.dump(manifest,f,ensure_ascii=False,indent=2)
with open(os.path.join(ROOT,'camera-audit.json'),'w') as f:json.dump({'frames':2256,'seconds':94,'fps':24,'primary_volume_collisions':collisions,'intentional_interior':'Ground-floor glazed school corridor'},f,ensure_ascii=False,indent=2)
with open(os.path.join(ROOT,'site-plan-observations.json'),'w') as f:json.dump({'visible_map_scale':{'metres':20,'pixels':84},'local_origin_viewport_pixels':[1000,500],'building_footprints':SITE,'primary_school':PRIMARY_OBSERVATION,'track_rotation_degrees':32,'sunken_depth_inferred_metres':DEPTH,'source':'Inherited v4 manual trace of user-opened Google Maps inspected 2026-10-15; v5 reconnection could not read imagery; acquisition date unknown.'},f,ensure_ascii=False,indent=2)
with open(os.path.join(ROOT,'architecture-repairs.json'),'w') as f:json.dump(ARCHITECTURE_V5,f,ensure_ascii=False,indent=2)
print('V5_MODEL_READY',len(bpy.data.objects),'objects',flush=True)
