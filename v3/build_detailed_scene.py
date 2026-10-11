"""Ta Hwa campus: video-informed architectural visualization, approximate scale.
Source observations: 00:16–02:08 in user supplied videoplayback.mp4.
Run with Blender 5.3: blender -b --python build_detailed_scene.py
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
 if d>w:
  temp=Mesh('rotated roof');roof(temp,0,0,d,w,z,rise)
  for face,idx in zip(temp.f,temp.mi):
   verts=[(x-temp.v[i][1],y+temp.v[i][0],temp.v[i][2]) for i in face]
   b.faces(verts,[tuple(range(len(verts)))],temp.mats[idx])
  return
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

# Campus scale and stepped sports terrace. Coordinates are local, not georeferenced.
box('Campus plinth',25,0,-7.0,2000,2000,2,'forest')
box('West surrounding ground',-500,0,-1.5,820,2000,1,'forest')
box('East surrounding ground',650,0,-1.5,1000,2000,1,'forest')
box('North surrounding ground',25,580,-1.5,250,900,1,'forest')
box('South surrounding ground',25,-610,-1.5,250,930,1,'forest')
box('Campus landscaped terrace',-6,0,-.32,124,238,.65,'grass')
box('Gym landscaped terrace',64,-85,-.32,48,46,.65,'grass')
box('Athletics lower terrace',107,10,-.65,88,160,.45,'grass')
box('Entrance paved square',-1,-88,.015,118,71,.07,'paving')
box('West sidewalk',-66,0,.12,3,246,.24,'concrete')
box('West public road',-76,2,.02,15,290,.06,'asphalt')
for y in range(-133,140,10):box('Centre road dash',-76,y,.065,.13,4,.03,'line')

# Kidney-shaped entrance lawn and its yellow crescent planting.
lawnpts=[]
for i in range(120):
 t=2*math.pi*i/120;r=1+.08*math.cos(3*t)
 lawnpts.append((-5+36*math.cos(t)*r,-88+22*math.sin(t)*r))
polygon('Entrance kidney lawn',lawnpts,.15,'grass')
line('Lawn curb',[(x,y,.19) for x,y in lawnpts],.15,'concrete',True)
for i in range(38):
 t=math.radians(20+i*5.6);x=-9+10*math.cos(t);y=-86+6*math.sin(t)
 box('Crescent hedge',x,y,.78,2.5,2.3,1.3,'hedge')
box('Monument pedestal',-8,-86,.5,2.1,2.1,1,'concrete')
box('Monument obelisk',-8,-86,2,.65,.65,2.1,'metal')
for i in range(16):
 t=2*math.pi*i/16
 box('Courtyard paving joint',-51+i*6,-52,.13,.03,15,.015,'line')

# Parallel classroom bars with cross-shaped connector, as seen from 00:40/01:28.
building('Teaching south bar',-12,-6,79,12,3,True,True)
building('Teaching north bar',-12,29,79,13,4,True,True)
building('Central connecting hall',-12,11,17,27,3,True,False)
building('Central hall side wing',-12,11,32,12,3,True,False)
building('Front western hall',-43,-28,13,34,2,True,True)
building('Front garden annex',14,-48,40,13,2,True,False)
building('West entrance pavilion',-43,-49,14,8,1,True,False)
for k in range(5):box('Pavilion entry steps',-43,-54-k*.3,.10+k*.12,8,1.8-k*.18,.20,'concrete')
building('Rear west white school',-46,68,29,20,4,False,False)
# Deding dormitory rebuilt below with rounded corner and tiled facade.
building('East stair service tower',33,51,10,18,3,False,False)
building('Rear west stair tower',-33,48,10,12,5,False,False)
building('Rear small connector',-31,62,20,8,2,False,False)

# Curved rear facade and mint barrel roof visible near 01:40.
b=Mesh('Rear curved administration')
b.box(-10,111,6.5,43,19,13,'ivory')
for i in range(24):
 xx=-31.5+(i+.5)*43/24;yy=101-2.8*(1-((xx+10)/21.5)**2)
 b.box(xx,yy,6.4,1.65,.3,11.3,'glass')
 b.box(xx+.83,yy-.2,6.5,.15,.45,12.7,'white')
 for z in (3.3,6.6,9.9,13):b.box(xx,yy-.25,z,1.85,.6,.26,'white')
for i in range(30):
 y=101+i*20/30;z=13+2.2*math.sin(math.pi*(y-101)/20)
 b.box(-10,y,z,44,.75,.16,'mint')
b.finish()

# Gym rebuilt below, its entrance faces west toward the central lawn.

# Front enclosing road, white parked cars, low boundary wall.
roadpts=[]
for i in range(80):
 a=math.pi+i*math.pi/79
 roadpts.append((29+94*math.cos(a),-93+40*math.sin(a)))
ribbon('South perimeter curved road',roadpts,10,.02,'asphalt')
line('South road edge',[(x,y-4.6,.07) for x,y in roadpts],.08,'line')
for i in range(30):
 a=math.pi*1.15+i*math.pi*.75/30;x=29+92*math.cos(a);y=-93+37*math.sin(a)
 b=Mesh('Parked car %02d'%i);b.box(0,0,.7,1.65,3.5,.9,'carwhite' if i%4 else 'cardark');b.box(0,-.15,1.2,1.35,1.9,.65,'glass');o=b.finish();o.location=(x,y,0);o.rotation_euler.z=-a
box('School gate left pier',-49,-119,2.1,1.6,1.6,4.2,'concrete')
box('School gate right pier',-32,-119,2.1,1.6,1.6,4.2,'concrete')
box('School entrance canopy',-40.5,-119,4.3,19,2.6,.6,'metal')

# Athletics: actual stadium-shaped track with straight lanes, not nested ellipses.
cx,cy=106,9
def stadium(r,straight=47):
 pts=[]
 for i in range(49):
  a=math.pi*i/48;pts.append((cx+r*math.cos(a),cy+straight/2+r*math.sin(a)))
 for i in range(49):
  a=math.pi+math.pi*i/48;pts.append((cx+r*math.cos(a),cy-straight/2+r*math.sin(a)))
 return pts
polygon('Track red oval',stadium(28),-.37,'track');polygon('Sports infield',stadium(21.3),-.34,'field')
for j in range(6):line('Running lane %d'%j,[(x,y,-.30) for x,y in stadium(21.6+j*1.12)],.055,'line',True)
box('Sprint extension',81,5,-.33,6.8,119,.08,'track')
for j in range(6):box('Sprint lane stripe',77.75+j*1.12,5,-.27,.07,118,.025,'line')
box('Blue athletics apron',74,7,-.27,3.3,122,.12,'blue')
for y in (-31,-29,-27):box('Start finish stripe',81,y,-.25,6.8,.08,.02,'line')

# Concrete spectators steps and roofed central platform (00:56, 01:28).
b=Mesh('East grandstand steps')
for i in range(13):b.box(60+i*.90,7,1.6-i*.13,.9,116,3.5-i*.26,'concrete')
for yy in (-49,-19,13,43,64):
 for i in range(13):b.box(60+i*.9,yy,3.42-i*.26,.85,1.4,.13,'white')
b.finish()
box('Grandstand central shelter',66,7,5.0,12,22,.35,'concrete')
for x in (61,71):
 for y in (-2,16):box('Shelter column',x,y,3.4,.35,.35,3.1,'white')

# Pair of basketball courts beyond the northern bend.
box('Basketball court pavement',105,89,-.30,47,33,.12,'court')
for xx in (93,117):
 for dx in (-10.5,10.5):line('Court side',[(xx+dx,75,-.22),(xx+dx,103,-.22)],.055,'line')
 for yy in (75,89,103):line('Court baseline',[(xx-10.5,yy,-.22),(xx+10.5,yy,-.22)],.055,'line')
 line('Centre circle',[(xx+2.7*math.cos(i*math.tau/48),89+2.7*math.sin(i*math.tau/48),-.20) for i in range(48)],.055,'line',True)
 for yy,sign in ((75,1),(103,-1)):
  line('Free throw box',[(xx-2.5,yy,-.21),(xx-2.5,yy+sign*5.8,-.21),(xx+2.5,yy+sign*5.8,-.21),(xx+2.5,yy,-.21)],.055,'line')
  line('Court arc',[(xx+6.3*math.cos(i*math.pi/36),yy+sign*6.3*math.sin(i*math.pi/36),-.21) for i in range(37)],.055,'line')
  box('Basket support',xx,yy-sign*.9,1.5,.13,.13,3.6,'metal');box('Backboard',xx,yy,3.2,1.8,.10,1.05,'white')

# Campus footpaths, garden circle, lamps and railings.
for x,y,w,d in [(-12,-23,62,2),(39,12,3,89),(-49,26,3,63),(4,-59,85,2),(-8,55,59,5)]:box('Campus path',x,y,.08,w,d,.16,'paving')
# Raised teaching courtyard fountain rebuilt below.
for yy in range(-51,69,20):
 box('Field lamp mast',72,yy,5.5,.16,.16,11,'metal');box('Field lamp head',72,yy,11,1.1,.45,.3,'white')
 line('Safety handrail',[(58,yy-9,3.8),(58,yy+9,3.8)],.045,'metal')

# Detailed, shared-mesh trees with several overlapping leafy crowns.
leafmats=[material('Foliage %d'%i,col,.92,12) for i,col in enumerate([(.12,.28,.07),(.18,.34,.08),(.23,.39,.10),(.27,.41,.12),(.14,.30,.12)])]
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1);proto=bpy.context.object;leafmesh=proto.data.copy();bpy.data.objects.remove(proto,do_unlink=True)
for p in leafmesh.polygons:p.use_smooth=True
tree_meshes=[]
for k in range(5):
 b=Mesh('Tree geometry %d'%k);b.box(0,0,1.8,.35,.35,3.6,'trunk')
 for j in range(6):
  a=j*math.tau/5;px=math.cos(a)*.9 if j else 0;py=math.sin(a)*.9 if j else 0;pz=3.8+(.6 if not j else random.uniform(-.2,.5));r=random.uniform(1.1,1.7)
  b.faces([(v.co.x*r+px,v.co.y*r+py,v.co.z*r*.9+pz) for v in leafmesh.vertices],[tuple(p.vertices) for p in leafmesh.polygons],leafmats[k])
 ob=b.finish()
 for face in list(ob.data.polygons)[6:]:face.use_smooth=True
 tree_meshes.append(ob.data);bpy.data.objects.remove(ob,do_unlink=True)
def tree(x,y,size=1):
 o=bpy.data.objects.new('Landscape tree',random.choice(tree_meshes));bpy.context.collection.objects.link(o);o.location=(x,y,-.8);o.scale=(size,size,size);o.rotation_euler.z=random.random()*math.tau
for i in range(550):
 x=random.uniform(-160,220);y=random.uniform(-180,180)
 if (-87<x<150 and -139<y<128):continue
 tree(x,y,random.uniform(1.2,2.1))
for y in range(-115,130,8):tree(-65,y,random.uniform(.85,1.3))
for x in range(-51,47,9):tree(x,-64,random.uniform(.8,1.2))
for x,y in [(-55,-33),(-26,-23),(-3,-24),(23,-24),(37,-31),(46,-44),(40,-65),(48,-105),(88,-93),(39,65),(-54,95),(49,97),(47,31),(49,7),(48,-15)]:tree(x,y,1.25)
for x,y in [(-39,11),(-35,14),(9,13),(17,12),(25,13),(-34,-30),(-19,-34),(-9,-33),(1,-32),(28,-31),(33,-23),(39,-49),(43,-57),(-24,45),(-17,46),(6,49),(14,59)]:tree(x,y,random.uniform(1.05,1.4))
for i in range(90):
 x=random.uniform(143,165);y=random.uniform(-62,118);tree(x,y,random.uniform(.9,1.4))
for x in range(153,276,7):
 for y in range(-160,211,7):tree(x+random.uniform(-2,2),y+random.uniform(-2,2),random.uniform(1.4,2.0))
for x in range(-170,150,8):
 for y in range(176,257,8):tree(x+random.uniform(-2,2),y+random.uniform(-2,2),random.uniform(1.4,2.1))

# Low surrounding houses and rear construction zone present in this historic video.
box('Rear construction clearing',40,126,.02,54,24,.08,'soil')
for i in range(13):
 x=-113+(i%2)*17;y=-75+(i//2)*29
 building('Neighbouring residence %02d'%i,x,y,12,17,3,True,False)
for i in range(11):building('Rear residential row %02d'%i,-72+i*16,154,11,16,3,True,False)

# V3: photo-constrained facade detail. Metric dimensions remain inferred.
M['curtain']=material('Gym muted rose curtains',(.29,.10,.12),.86)
M['redletter']=material('Crimson architectural lettering',(.43,.035,.035),.55)
M['water']=material('Fountain water',(.035,.21,.24),.12)
M['water'].node_tree.nodes.get('Principled BSDF').inputs['Metallic'].default_value=.35
M['tileblue']=material('Pool cobalt ceramic',(.025,.075,.31),.28)
M['rock']=material('Garden limestone',(.53,.49,.40),.92,5)
# Actual-size square ceramic tile grids, with mortar and subtle relief.
for key in ('white','ivory'):
 nt=M[key].node_tree;p=nt.nodes.get('Principled BSDF')
 coord=nt.nodes.new('ShaderNodeTexCoord');sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(coord.outputs['Generated'],sep.inputs[0])
 # Object coordinates maintain 8 cm tile spacing across all architecture.
 geom=nt.nodes.new('ShaderNodeNewGeometry');sep2=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(geom.outputs['Position'],sep2.inputs[0])
 lines=[]
 for axis in ('X','Y','Z'):
  mul=nt.nodes.new('ShaderNodeMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=12.5;nt.links.new(sep2.outputs[axis],mul.inputs[0])
  frac=nt.nodes.new('ShaderNodeMath');frac.operation='FRACT';nt.links.new(mul.outputs[0],frac.inputs[0])
  less=nt.nodes.new('ShaderNodeMath');less.operation='LESS_THAN';less.inputs[1].default_value=.027;nt.links.new(frac.outputs[0],less.inputs[0]);lines.append(less)
 # Use normal-weighted pairs: horizontal surfaces XY; walls XZ/YZ.
 normal=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(geom.outputs['Normal'],normal.inputs[0])
 sums=[]
 for i,(aa,bb,axis) in enumerate([(1,2,'X'),(0,2,'Y'),(0,1,'Z')]):
  mx=nt.nodes.new('ShaderNodeMath');mx.operation='MAXIMUM';nt.links.new(lines[aa].outputs[0],mx.inputs[0]);nt.links.new(lines[bb].outputs[0],mx.inputs[1])
  ab=nt.nodes.new('ShaderNodeMath');ab.operation='ABSOLUTE';nt.links.new(normal.outputs[axis],ab.inputs[0])
  weight=nt.nodes.new('ShaderNodeMath');weight.operation='MULTIPLY';nt.links.new(mx.outputs[0],weight.inputs[0]);nt.links.new(ab.outputs[0],weight.inputs[1]);sums.append(weight)
 add=nt.nodes.new('ShaderNodeMath');add.operation='ADD';nt.links.new(sums[0].outputs[0],add.inputs[0]);nt.links.new(sums[1].outputs[0],add.inputs[1]);add2=nt.nodes.new('ShaderNodeMath');add2.operation='ADD';nt.links.new(add.outputs[0],add2.inputs[0]);nt.links.new(sums[2].outputs[0],add2.inputs[1])
 mix=nt.nodes.new('ShaderNodeMixRGB');mix.inputs[1].default_value=(.84,.85,.80,1);mix.inputs[2].default_value=(.48,.51,.48,1);nt.links.new(add2.outputs[0],mix.inputs[0]);nt.links.new(mix.outputs[0],p.inputs['Base Color'])
 bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.15;bump.inputs['Distance'].default_value=.008;nt.links.new(add2.outputs[0],bump.inputs['Height']);nt.links.new(bump.outputs[0],p.inputs['Normal'])
M['frame'].node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.045,.06,.065,1)
fontpaths=['/System/Library/Fonts/PingFang.ttc','/System/Library/Fonts/STHeiti Medium.ttc']
font=next((bpy.data.fonts.load(q) for q in fontpaths if os.path.exists(q)),None)
def label(text,loc,size,rotation=(math.pi/2,0,0),vertical=False):
 cu=bpy.data.curves.new(text,'FONT');cu.body='\n'.join(text) if vertical else text;cu.size=size;cu.extrude=.015;cu.align_x='CENTER';cu.space_line=1.25
 if font:cu.font=font
 ob=bpy.data.objects.new(text,cu);bpy.context.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=rotation;cu.materials.append(M['redletter']);return ob
# Gym facade normal -X, so doors open toward the lawn.
b=Mesh('凱旋樓 | west facing lawn entrance');b.box(63,-87,5.5,39,31,11,'white');roof(b,63,-87,39,31,11,2.2)
b.box(43.35,-87,3.05,.12,21,4.5,'glass');b.box(42.4,-87,5.55,2.6,22,.9,'white')
for yy in (-99,-75):b.box(42.15,yy,4.1,3.8,7,8.2,'white')
for yy in range(-100,-73,4):
 b.box(43.33,yy,9.3,.17,3.3,2,'curtain');b.box(43.14,yy,9.3,.15,3.5,2.15,'frame')
 b.box(43.03,yy,9.23,.04,3.18,1.65,'curtain')
 for dy in (-1.5,-.75,0,.75,1.5):b.box(42.99,yy+dy,9.3,.05,.065,2,'frame')
 b.box(42.9,yy+1.9,7.0,.7,.36,7.6,'white')
 b.box(42.95,yy,9.85,.05,3.3,.055,'frame')
for yy in range(-96,-76,2):
 b.box(43.12,yy,2.65,.16,.075,4.3,'frame');b.box(42.85,yy+.6,2,.12,.04,.5,'metal')
b.box(43,-87,4.3,.2,21,.12,'frame');b.box(41,-87,.12,5,30,.24,'concrete');b.finish()
label('凱旋樓',(40.18,-99,7.3),.65,(math.pi/2,0,-math.pi/2),True)
label('學生活動中心',(40.15,-97,6.2),.38,(math.pi/2,0,-math.pi/2),True)
# Continuous dark window bands visible in supplied courtyard and front photos.
for name,x,y,w,d,floors in [('Teaching south bar',-12,-6,79,12,3),('Teaching north bar',-12,29,79,13,4),('Front garden annex',14,-48,40,13,2)]:
 b=Mesh(name+' | glazed north band')
 for k in range(floors):
  z=k*3.35+1.88;yy=y+d/2+.14;b.box(x,yy,z,w-.8,.14,1.88,'glass')
  for j in range(int(w/1.35)+1):b.box(x-w/2+.4+j*(w-.8)/int(w/1.35),yy+.09,z,.055,.13,1.92,'frame')
  for dz in (-.94,.40,.94):b.box(x,yy+.09,z+dz,w-.8,.13,.065,'frame')
 b.finish()
# Arch inserts and raised masonry arch surrounds on the end of the western wing.
def arch(name,x,y,z,r,h):
 pts=[(x-r,y,z),(x-r,y,z+h)]+[(x+r*math.cos(math.pi-i*math.pi/32),y,z+h+r*math.sin(math.pi-i*math.pi/32)) for i in range(33)]+[(x+r,y,z)]
 b=Mesh(name);b.faces(pts,[tuple(range(len(pts)))],'glass');b.finish();line(name+' stone surround',pts,.13,'white');line(name+' dark arch frame',pts,.05,'frame');line(name+' transom',[(x-r,y-.03,z+h),(x+r,y-.03,z+h)],.035,'frame')
 # Vertical door divisions.
 for dx in (-r*.5,0,r*.5):line(name+' mullion',[(x+dx,y-.04,z),(x+dx,y-.04,z+h+r*.75)],.035,'frame')
for xx,r,h in [(-43,1.65,1.8),(-48,1.0,1.5),(-38,1.,1.5)]:arch('Front pavilion arched entrance',xx,-53.16,.24,r,h)
# Gabled upper end and circular window, matched to front hall photograph.
b=Mesh('Front hall gable end');b.faces([(-49.5,-45.1,6.7),(-36.5,-45.1,6.7),(-43,-45.1,9.3)],[(0,1,2)],'white');b.finish();arch('Upper hall arched window',-43,-45.25,6.75,.8,.8)
for xx in (-28,-25,-22):line('Ceremonial flagpole',[(xx,-57,.2),(xx,-57,8.6)],.055,'metal')
box('Front information plaque pedestal',-16,-67,.7,.28,.28,1.4,'metal');ob=box('Front inclined information panel',-16,-67,1.6,2.0,1.2,.11,'metal');ob.rotation_euler.x=.28
# Fountain with real raised tiled wall, blue inner lining, coping, water and jet.
px,py=-26,-29
b=Mesh('教學區水池 | raised circular tiled basin')
N=128
for i in range(N):
 a=i*math.tau/N;c=(i+1)*math.tau/N
 def v(r,t,z):return(px+r*math.cos(t),py+r*math.sin(t),z)
 b.faces([v(3.35,a,.10),v(3.35,c,.10),v(3.35,c,.68),v(3.35,a,.68)],[(0,1,2,3)],'white')
 b.faces([v(3.10,a,.2),v(3.10,c,.2),v(3.10,c,.66),v(3.10,a,.66)],[(0,3,2,1)],'tileblue')
 b.faces([v(3.48,a,.66),v(3.48,c,.66),v(3.05,c,.66),v(3.05,a,.66)],[(0,1,2,3)],'white')
b.finish();polygon('Fountain reflective water',[(px+3.1*math.cos(i*math.tau/N),py+3.1*math.sin(i*math.tau/N)) for i in range(N)],.51,'water')
line('Fountain nozzle',[(px,py,.35),(px,py,1.0)],.075,'metal');line('Fountain rising jet',[(px,py,1),(px,py,1.95)],.038,'water')
for k in range(10):
 a=k*math.tau/10;line('Fountain falling spray',[(px+.025*math.cos(a),py+.025*math.sin(a),1.9)]+[(px+.7*t*math.cos(a),py+.7*t*math.sin(a),1.9-1.3*t*t) for t in [i/12 for i in range(1,13)]],.012,'water')
for r in (.7,1.2,1.9,2.6):line('Water ripple',[(px+r*math.cos(i*math.tau/96),py+r*math.sin(i*math.tau/96),.52) for i in range(96)],.007,'tileblue',True)
line('Pool brick surround',[(px+3.8*math.cos(i*math.tau/128),py+3.8*math.sin(i*math.tau/128),.13) for i in range(128)],.27,'paving',True)
# Rounded Deding corner at rear east: square tile walls, red bands, grille windows and AC.
b=Mesh('定得樓 | rounded southwest corner');x0,x1,y0,y1=2.5,45.5,74.5,95.5;rad=4
outline=[(x0,y0+rad)]+[(x0+rad+rad*math.cos(math.pi+i*math.pi/2/24),y0+rad+rad*math.sin(math.pi+i*math.pi/2/24)) for i in range(25)]+[(x1,y0),(x1,y1),(x0,y1)]
for i in range(len(outline)):
 a=outline[i];c=outline[(i+1)%len(outline)];b.faces([(*a,0),(*c,0),(*c,14.0),(*a,14.0)],[(0,1,2,3)],'white')
b.faces([(*p,14) for p in outline],[tuple(range(len(outline)))],'white')
for zz in (.9,3.6,6.9,10.2,13.4):line('Deding red horizontal course',[(*p,zz) for p in outline],.045,'redletter',True)
for k in range(4):
 for j in range(9):
  xx=10+j*3.65;zz=1.8+k*3.25;b.box(xx,74.36,zz,1.5,.17,1.8,'shadow');b.box(xx,74.25,zz,1.1,.13,1.5,'glass')
  for dx in (-.6,-.3,0,.3,.6):b.box(xx+dx,74.14,zz,.04,.10,1.65,'metal')
  for dz in (-.8,0,.8):b.box(xx,74.12,zz+dz,1.35,.1,.045,'metal')
  b.box(xx,74.08,zz+.55,.68,.70,.44,'concrete');b.box(xx,73.70,zz+.55,.50,.04,.28,'metal')
 for yy in (81,88):
  b.box(2.36,yy,1.8+k*3.25,.15,1.4,1.8,'glass')
b.finish();label('定得樓',(7.8,74.1,10.0),.74,vertical=True)
# Covered walkway beside the dormitory.
b=Mesh('Deding sheltered walkway');b.box(26,69,2.7,38,3,.18,'mint')
for xx in range(8,46,4):b.box(xx,69,1.4,.12,.12,2.8,'white')
b.finish()
# Stadium excavated ~4.8 m below teaching terrace, inferred from video banking.
for ob in list(bpy.data.objects):
 if ob.name.startswith(('Athletics lower terrace','Track red oval','Sports infield','Running lane','Sprint extension','Sprint lane','Blue athletics','Start finish','Basketball court','Court side','Court baseline','Centre circle','Free throw','Court arc','Basket support','Backboard')):ob.location.z-=4.8
for ob in list(bpy.data.objects):
 if ob.name.startswith(('East grandstand steps','Grandstand central shelter','Shelter column','Safety handrail')):bpy.data.objects.remove(ob,do_unlink=True)
b=Mesh('Sunken stadium | stepped western bank')
for i in range(20):
 top=.18-i*.25;x=58+i*.7;b.box(x,7,(top-5.4)/2,.70,119,top+5.4,'concrete')
for yy in (-42,-10,25,54):
 for i in range(32):b.box(58+i*.44,yy,.19-i*.155,.44,2,.16,'white')
b.finish()
for yy in (-42,-10,25,54):line('Stadium stair handrail',[(57.9,yy+1.1,1.25),(71.7,yy+1.1,-3.65)],.045,'metal')
for y in (-53,68):box('Stadium north south retaining wall',110,y,-2.5,77,.55,5.3,'concrete')
box('Stadium eastern retaining wall',149,8,-2.5,.55,121,5.3,'concrete')
line('Upper stadium safety railing',[(57.8,-52,1.15),(57.8,67,1.15)],.055,'metal')
for yy in range(-52,68,3):line('Upper rail vertical',[(57.8,yy,.1),(57.8,yy,1.15)],.035,'metal')
box('Grandstand central shelter',63,7,3,10,18,.22,'concrete')
for xx in (59,67):
 for yy in (-1,15):box('Shelter column',xx,yy,1.35,.25,.25,2.8,'white')
# Rockery, flowering hedges, benches and visible slender branched courtyard trees.
for xx,yy,scale in [(-20,-24,1.5),(-31,-25,.8),(-35,-33,.6)]:
 ob=bpy.data.objects.new('Courtyard weathered boulder',leafmesh);bpy.context.collection.objects.link(ob);ob.location=(xx,yy,scale*.7);ob.scale=(scale,scale*.72,scale*1.3);ob.data=leafmesh.copy();ob.data.materials.clear();ob.data.materials.append(M['rock'])
flower=material('Pink azalea flowers',(.62,.09,.24),.9)
for xx,yy in [(-36,-22),(-19,-22),(-14,-26),(-32,-35)]:
 for j in range(9):
  ob=bpy.data.objects.new('Flowering courtyard hedge',leafmesh);bpy.context.collection.objects.link(ob);ob.location=(xx+j*.45,yy,.45);ob.scale=(.45,.5,.45);ob.data=leafmesh.copy();ob.data.materials.clear();ob.data.materials.append(leafmats[2])
  for k in range(2):
   q=bpy.data.objects.new('Azalea blossom cluster',leafmesh);bpy.context.collection.objects.link(q);q.location=(xx+j*.45+random.uniform(-.3,.3),yy+random.uniform(-.3,.3),.75);q.scale=(.09,.09,.07);q.data=leafmesh.copy();q.data.materials.clear();q.data.materials.append(flower)
for xx,yy in [(-30,-25),(-16,-24),(-36,-34)]:
 line('Courtyard slender tree trunk',[(xx,yy,.1),(xx+.2,yy,5.7)],.13,'trunk')
 for k in range(8):
  a=k*math.tau/8;tip=(xx+2*math.cos(a),yy+2*math.sin(a),random.uniform(5,7));line('Courtyard visible branch',[(xx,yy,3.4),tip],.045,'trunk')
  q=bpy.data.objects.new('Fine courtyard tree crown',leafmesh);bpy.context.collection.objects.link(q);q.location=tip;q.scale=(.7,.7,.4);q.data=leafmesh.copy();q.data.materials.clear();q.data.materials.append(leafmats[k%5])
for xx in (-20,-8):
 box('Garden bench',xx,-38,.6,2.4,.6,.15,'trunk')
 for dx in (-.9,.9):box('Bench metal legs',xx+dx,-38,.3,.08,.5,.6,'metal')
# Small-scale bevels on hero architecture support close exterior views.
for ob in list(bpy.data.objects):
 if ob.type=='MESH' and any(q in ob.name for q in ('凱旋','定得','glazed','gable','basin')):
  mod=ob.modifiers.new('Facade edge highlights','BEVEL');mod.width=.025;mod.segments=2

# Remove foliage that blocks the dormitory camera corridor.
for ob in list(bpy.data.objects):
 if ob.name.startswith('Landscape tree') and -15<ob.location.x<46 and 48<ob.location.y<72:bpy.data.objects.remove(ob,do_unlink=True)
# Teaching courtyard glass bands correspond to the supplied pool photograph.
b=Mesh('Teaching courtyard | continuous dark framed glazing')
for k in range(3):
 z=1.8+k*3.35;b.box(-12,-12.18,z,78,.16,1.9,'glass')
 for j in range(58):b.box(-50.5+j*1.35,-12.29,z,.06,.12,1.94,'frame')
 for dz in (-.95,.43,.95):b.box(-12,-12.30,z+dz,78,.1,.065,'frame')
b.finish()

# Daylight, soft shadows, full HD animation camera.
scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=1920;scene.render.resolution_y=1080;scene.render.resolution_percentage=100
scene.eevee.taa_render_samples=32
scene.render.image_settings.file_format='PNG';scene.render.fps=24;scene.frame_start=1;scene.frame_end=576
world=bpy.data.worlds.new('Clear aerial daylight');world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.54,.69,.85,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.45;scene.world=world;sky=world.node_tree.nodes.new('ShaderNodeTexSky');sky.sky_type='MULTIPLE_SCATTERING';sky.sun_elevation=.55;sky.sun_rotation=2.4;sky.sun_disc=False;world.node_tree.links.new(sky.outputs['Color'],world.node_tree.nodes['Background'].inputs['Color']);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.25
bpy.ops.object.light_add(type='SUN',location=(0,0,100));sun=bpy.context.object;sun.name='Afternoon sun';sun.rotation_euler=(math.radians(26),math.radians(-23),math.radians(-28));sun.data.energy=2.8;sun.data.angle=math.radians(6)
scene.view_settings.view_transform='AgX'
camdata=bpy.data.cameras.new('Aerial camera');cam=bpy.data.objects.new('Aerial camera',camdata);bpy.context.collection.objects.link(cam);scene.camera=cam;camdata.lens=35;camdata.clip_end=2000
def catmull(p0,p1,p2,p3,t):return .5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t)
# Eight edited, slow camera moves; exactly 94 seconds at native 24 fps.
shots=[
 ('校園全景',12,(-160,-220,135),(-102,-167,94),(13,-8,2),(15,-10,3),35),
 ('凱旋樓面向前庭',12,(4,-108,4.2),(11,-76,5.2),(43,-89,5.0),(43,-87,5.5),32),
 ('前棟拱廊與校舍',14,(-64,-77,4.0),(-36,-76,5.6),(-43,-48,4.2),(-38,-39,5),34),
 ('教學區水池',15,(-35,-40,2.4),(-18,-39,3.0),(-26,-28,1.7),(-27,-23,3.8),28),
 ('教學區外觀',12,(-36,-36,10.0),(21,-36,12.4),(-22,-6,5.7),(17,-6,5.8),32),
 ('定得樓圓角立面',12,(-10,52,5.0),(31,53,7.0),(9,75,7),(25,75,7.5),32),
 ('下沉操場與階梯',11,(86,-43,10),(130,-8,4),(65,8,-2),(79,12,-2),27),
 ('校園收束全景',6,(183,24,95),(171,114,137),(15,15,0),(15,20,0),32),
]
import json
manifest=[];frame=1
for name,dur,pa,pb,ta,tb,lens in shots:
 start=frame;end=frame+dur*24-1;prev=None
 for f in range(start,end+1):
  t=(f-start)/(end-start);t=t*t*(3-2*t);loc=Vector(pa).lerp(Vector(pb),t);target=Vector(ta).lerp(Vector(tb),t)
  cam.location=loc;e=(target-loc).to_track_quat('-Z','Y').to_euler()
  if prev:e.make_compatible(prev)
  cam.rotation_euler=e;prev=e.copy();camdata.lens=lens
  cam.keyframe_insert(data_path='location',frame=f);cam.keyframe_insert(data_path='rotation_euler',frame=f);camdata.keyframe_insert(data_path='lens',frame=f)
 scene.timeline_markers.new(name,frame=start);manifest.append(dict(name=name,start=start,end=end,seconds=dur));frame=end+1
scene.frame_end=2256;scene.eevee.taa_render_samples=32
# Disable interpolation across cuts.
for owner in (cam,camdata):
 if owner.animation_data and owner.animation_data.action:
  try:
   for fc in owner.animation_data.action.fcurves:
    for k in fc.keyframe_points:k.interpolation='LINEAR'
  except AttributeError:pass
scene.frame_set(432);scene['version']='3.0 — photo-informed facade, sunken stadium, 94-second exterior tour'
scene['reference']='Supplied photos, supplied aerial video after 00:16, historic Commons original photos. Approximate metric reconstruction.'
scene.render.filepath=os.path.join(ROOT,'preview.png')
# Convert architectural lettering into portable editable meshes.
bpy.ops.object.select_all(action='DESELECT')
for ob in list(bpy.data.objects):
 if ob.type=='FONT':
  bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.convert(target='MESH');ob.select_set(False)
for cu in list(bpy.data.curves):
 if cu.users==0:bpy.data.curves.remove(cu)
for f in list(bpy.data.fonts):bpy.data.fonts.remove(f,do_unlink=True)
# Scene uses procedural materials and geometry; no external dependencies.
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'dahua-campus-v3.blend'))
with open(os.path.join(ROOT,'shots.json'),'w') as f:json.dump(manifest,f,ensure_ascii=False,indent=2)
if os.environ.get('CAMPUS_RENDER_PREVIEW','1')=='1':bpy.ops.render.render(write_still=True)
