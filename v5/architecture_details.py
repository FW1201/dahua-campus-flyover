"""v5 closed architectural assemblies. Executed in builder globals."""
# Rebuild the two reported problem facades rather than covering their gaps.
for ob in list(bpy.data.objects):
 if ob.name.startswith(('定得樓 |','定得樓紅色水平線','雙語小學部 |','小學部陽台與屋頂扶手','小學部欄杆底梁')) or ob.name in ('定得樓','學 小 華 大','TA HWA BILINGUAL ELEMENTARY SCHOOL'):
  bpy.data.objects.remove(ob,do_unlink=True)
M['gold'].node_tree.nodes.get('Principled BSDF').inputs['Metallic'].default_value=.72
M['gold'].node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.28
for key in ('glass','primaryglass'):
 p=M[key].node_tree.nodes.get('Principled BSDF');p.inputs['Metallic'].default_value=.12;p.inputs['Roughness'].default_value=.30
M['seal']=material('Dark EPDM window gaskets',(.018,.022,.023),.86)
M['reveal']=material('Recessed window reveals',(.26,.27,.24),.86)
M['curtainlight']=material('Ivory interior curtains',(.54,.51,.42),.95)
M['drain']=material('Dark storm drain steel',(.085,.093,.087),.65)
M['roofcap']=material('Weathered red standing seam cap',(.37,.095,.055),.69)

def obox(b,x,y,z,w,d,h,a,mat):
 """Box in local tangent/outward-normal coordinates, with disjoint faces."""
 c,s=math.cos(a),math.sin(a)
 b.faces([(x+c*dx*w/2-s*dy*d/2,y+s*dx*w/2+c*dy*d/2,z+dz*h/2) for dx,dy,dz in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat)

def acunit(b,x,y,z,scale=1):
 b.box(x,y,z,.80*scale,.50*scale,.56*scale,'concrete')
 for i in range(9):b.box(x,y-.258*scale,z+(i-4)*.046*scale,.66*scale,.025*scale,.017*scale,'metal')
 for dx in (-.31,.31):b.box(x+dx*scale,y+.08*scale,z-.34*scale,.05*scale,.68*scale,.10*scale,'metal')
 for i in range(4):b.box(x+(i-1.5)*.15*scale,y-.281*scale,z,.009*scale,.012*scale,.45*scale,'frame')

# Deding: physical slabs, inset glazing, red opaque infill, closed wall reveals.
x,y,w,d,_=SITE['deding'];x0,x1,y0,y1=x-w/2,x+w/2,y-d/2,y+d/2;rr=4.0
outline=[(x0,y0+rr)]+[(x0+rr+rr*math.cos(math.pi+i*math.pi/2/40),y0+rr+rr*math.sin(math.pi+i*math.pi/2/40)) for i in range(41)]+[(x1,y0),(x1,y1),(x0,y1)]
b=Mesh('定得樓 | V5 continuous facade and closed recessed bays')
for k in range(5):
 z=k*3.5
 b.faces([(*p,z) for p in outline],[tuple(range(len(outline)))],'concrete')
 b.faces([(*p,z-.18) for p in outline],[tuple(range(len(outline)-1,-1,-1))],'concrete')
 for a,c in zip(outline,outline[1:]+outline[:1]):b.faces([(*a,z-.18),(*c,z-.18),(*c,z),(*a,z)],[(0,1,2,3)],'white')
for a,c in zip(outline,outline[1:]+outline[:1]):
 if abs(a[1]-y0)<.001 and abs(c[1]-y0)<.001:continue
 b.faces([(*a,0),(*c,0),(*c,14.25),(*a,14.25)],[(0,1,2,3)],'white')
# Continuous interior rear wall prevents a view through missing floor/ceilings.
b.box(x,y0+3.4,7,39,.25,14,'interior')
front_start=x0+4.0;bay=(x1-front_start)/11
for k in range(4):
 z=k*3.5
 b.box((front_start+x1)/2,y0,z+.48,x1-front_start,.34,.96,'white')
 b.box((front_start+x1)/2,y0,z+3.15,x1-front_start,.34,.70,'white')
 for j in range(11):
  xx=front_start+(j+.5)*bay;ww=bay-.48
  # Ground lobby is glazed and recessed, never an unsupported two-storey void.
  if k==0 and 4<=j<=5:
   b.box(xx,y0+.52,z+1.87,ww,.12,2.05,'glass')
   for dx in (-ww/2,0,ww/2):b.box(xx+dx,y0+.43,z+1.87,.065,.12,2.1,'frame')
  else:
   mat='glass' if j%2==0 else 'curtain'
   b.box(xx,y0+.34,z+1.88,ww,.12,1.80,mat)
   b.box(xx,y0+.50,z+1.88,ww,.12,1.80,'curtainlight' if j%4==0 else 'interior')
   # Deep jambs and lintels fully meet the wall piers.
   for dx in (-ww/2,ww/2):b.box(xx+dx,y0+.16,z+1.88,.09,.42,1.94,'reveal')
   for dz in (-.96,.96):b.box(xx,y0+.16,z+1.88+dz,ww+.12,.42,.12,'reveal')
   if j%2==0:
    for dx in (-ww*.43,0,ww*.43):b.box(xx+dx,y0+.245,z+1.88,.055,.12,1.80,'frame')
    b.box(xx,y0+.24,z+2.32,ww,.12,.045,'frame')
    for dx in (-ww*.42,-ww*.21,0,ww*.21,ww*.42):b.box(xx+dx,y0-.13,z+1.90,.025,.08,1.8,'metal')
    for dz in (-.87,0,.87):b.box(xx,y0-.13,z+1.9+dz,ww-.12,.08,.028,'metal')
    acunit(b,xx,y0-.46,z+2.58,.86)
  b.box(front_start+j*bay,y0,z+1.75,.42,.55,3.5,'white')
 b.box(x1,y0,z+1.75,.34,.55,3.5,'white')
 # Thin red inlay strips sit proud of the wall, separated from slab faces.
for zz in (.18,3.66,7.16,10.66,14.16):line('定得樓 V5 red ceramic inlay',[(a,c-.025 if abs(c-y0)<.01 else c,zz) for a,c in outline],.022,'redletter',True)
# Side elevation has repeated framed windows and actual aluminium louvres.
for side in (-1,1):
 for k in range(4):
  for j in range(6):
   yy=y0+5.3+j*3.6;xx=x+side*(w/2+.06)
   obox(b,xx,yy,k*3.5+1.9,1.65,.12,1.75,math.pi/2,'glass')
   for dy in (-.88,0,.88):b.box(xx+side*.09,yy+dy,k*3.5+1.9,.14,.055,1.86,'frame')
   for dz in (-.93,.93):b.box(xx+side*.09,yy,k*3.5+1.9+dz,.14,1.88,.07,'white')
for xx in (front_start+.6,x1-.7):line('定得樓 V5 external drainage',[(xx,y0-.4,.3),(xx,y0-.4,14.3)],.055,'white')
b.box(x,y0+1,14.4,w-1,1,.3,'white');ob=b.finish();mod=ob.modifiers.new('Rounded facade arrises','BEVEL');mod.width=.012;mod.segments=2
label('定得樓',(front_start+1.3,y0-.37,11.7),.82,vertical=True)
# Recessed entrance apron, steps, glazed doors and handles.
b=Mesh('定得樓 V5 entrance joinery');cx=front_start+5*bay
b.box(cx,y0-.95,3.03,7,2.6,.22,'white')
for xx in (cx-2.6,cx,cx+2.6):
 b.box(xx,y0+.28,1.5,2.42,.12,2.75,'glass')
 for dx in (-1.22,1.22):b.box(xx+dx,y0+.19,1.5,.07,.14,2.85,'frame')
 for z in (.07,2.91):b.box(xx,y0+.19,z,2.5,.14,.08,'frame')
 b.box(xx+.18,y0+.05,1.3,.032,.06,.45,'metal')
for j in range(3):b.box(cx,y0-1.65+j*.45,.04+j*.06,8,2.8-j*.6,.14,'concrete')
b.finish()

# Primary school: each element shares the tangent of its local bay.
# No coplanar panels, no free-standing stair steps behind a glass-only shell.
def arc_y(xx):return 119+5*math.sin(math.pi*(xx+62)/52)
def arc_angle(xx):return math.atan(5*math.pi/52*math.cos(math.pi*(xx+62)/52))
b=Mesh('雙語小學部 | V5 tangent-aligned closed facade');N=104
facade=[(-62+52*j/N,arc_y(-62+52*j/N)) for j in range(N+1)]
for k in range(4):
 z=k*3.5
 for a,c in zip(facade,facade[1:]):
  b.faces([(*a,z),(*c,z),(c[0],c[1]+11,z),(a[0],a[1]+11,z)],[(0,1,2,3)],'concrete')
  b.faces([(*a,z-.18),(*c,z-.18),(*c,z),(*a,z)],[(0,1,2,3)],'primarybrick')
# Opaque inner partition behind the windows, with believable room depth.
for j in range(26):
 xx=-61+2*j;yy=arc_y(xx);a=arc_angle(xx);obox(b,xx,yy+4.4,5.2,2.06,.24,10.4,a,'interior')
for a,c in zip(facade,facade[1:]):b.faces([(a[0],a[1]+11,0),(c[0],c[1]+11,0),(c[0],c[1]+11,10.55),(a[0],a[1]+11,10.55)],[(0,1,2,3)],'primarybrick')
for xx in (-62,-10):
 yy=arc_y(xx);b.box(xx,yy+5.5,5.25,.28,11,10.5,'primarybrick')
for k in range(3):
 z=k*3.5
 for j in range(26):
  xx=-61+2*j;yy=arc_y(xx);a=arc_angle(xx);c,s=math.cos(a),math.sin(a)
  def cb(dx,dn,zz,ww,dd,hh,mat):obox(b,xx+c*dx-s*dn,yy+s*dx+c*dn,z+zz,ww,dd,hh,a,mat)
  width=2/math.cos(a);balcony=k==2 and j<9
  cb(0,.12,.22,width+.035,.32,.44,'primarybrick');cb(0,.12,3.30,width+.035,.32,.40,'primarybrick')
  if balcony:
   cb(0,1.55,1.82,width-.20,.12,2.75,'primaryglass')
  else:
   ww=1.66 if k==0 else 1.10
   cb(0,.20,1.80,ww,.09,2.56,'primaryglass')
   for dx in (-ww/2-.075,ww/2+.075):cb(dx,.09,1.8,.15,.36,2.80,'primarybrick')
   for dx in (-ww/2,ww/2):cb(dx,-.015,1.8,.065,.12,2.68,'primaryframe')
   for zz in (.47,.94,2.61,3.14):cb(0,-.025,zz,ww+.12,.12,.055,'primaryframe')
   # Curtain layer is behind the inset pane; opaque and stable without SSR artifacts.
   if j%5==0:
    for q in range(8):cb(-ww*.43+q*ww*.12,.34,1.8,.035,.04,2.5,'curtainlight')
   cb((width+ww)/4,.12,1.8,(width-ww)/2,.34,2.96,'primarybrick')
   cb(-(width+ww)/4,.12,1.8,(width-ww)/2,.34,2.96,'primarybrick')
  cb(width/2,.12,1.75,.15,.46,3.5,'primarybrick')
 # Continuous balcony slabs and facade band, with no overlaps at bay edges.
 for a,c in zip(facade,facade[1:]):
  for z0,z1 in [(z,z+.22),(z+3.23,z+3.50)]:b.faces([(*a,z0),(*c,z0),(*c,z1),(*a,z1)],[(0,1,2,3)],'primarybrick')
# Upper balcony: set-back glazed doors, inner ceiling and a modest roof railing.
for j in range(81):
 xx=-62+52*j/80;yy=arc_y(xx);a=arc_angle(xx)
 for z0,z1 in [(10.60,11.44)]+([(7.32,8.22)] if xx<-44 else []):
  cylinder(b,(xx,yy-.32,z0),(xx,yy-.32,z1),.016,'primaryframe',8)
for z,start,end in [(11.44,-62,-10),(10.66,-62,-10),(8.22,-62,-44),(7.37,-62,-44)]:line('小學部 V5 continuous balcony rail',[(xx,arc_y(xx)-.32,z) for xx in [start+(end-start)*j/100 for j in range(101)]],.036,'primaryframe')
# Physical building-foot paving and drainage.
for a,c in zip(facade,facade[1:]):
 b.faces([(a[0],a[1]-.65,.10),(c[0],c[1]-.65,.10),(c[0],c[1]-3.6,.10),(a[0],a[1]-3.6,.10)],[(0,1,2,3)],'paving')
for xx in (-59,-48,-21,-12):
 yy=arc_y(xx);line('小學部 V5 rainwater pipe',[(xx,yy-.28,.16),(xx,yy-.28,10.56)],.045,'primaryframe')
ob=b.finish();mod=ob.modifiers.new('Fine masonry edge highlights','BEVEL');mod.width=.008;mod.segments=2
# Gold 3D letters are individually mounted along the curved surface.
for text,z,size,step in [('學小華大',3.65,1.30,2.0),('TA HWA BILINGUAL ELEMENTARY SCHOOL',3.12,.42,.34)]:
 for j,char in enumerate(text):
  if char==' ':continue
  xx=-36+(j-(len(text)-1)/2)*step;yy=arc_y(xx);a=arc_angle(xx)
  o=label(char,(xx,yy-.18,z),size,'gold',rot=(math.pi/2,0,a));o.name='小學部 V5 cast metal sign '+char
  # Two mounting pins per letter, hidden behind the solid raised strokes.
  for dx in (-size*.16,size*.16):line('Sign concealed mounting pin',[(xx+dx,yy-.02,z+size*.25),(xx+dx,yy-.17,z+size*.25)],.018,'metal')
# Main school sash depth, gutters and rainwater collection details.
b=Mesh('學海校舍 V5 exterior joinery and services')
for key in ('south','north','front','admin'):
 x,y,w,d,f=SITE[key];h=f*3.35;count=max(2,round(w/4.25));bay=w/count
 for side in (-1,1):
  yy=y+side*d/2
  # Rain gutters follow eaves with metal support brackets and outlet elbows.
  b.box(x,yy+side*.46,h-.08,w+.65,.18,.19,'metal')
  for j in range(int(w/2.5)+1):b.box(x-w/2+j*w/int(w/2.5),yy+side*.42,h-.20,.05,.32,.18,'frame')
  for k in range(f):
   for j in range(count):
    xx=x-w/2+(j+.5)*bay
    if not (key=='south' and side==1 and k==0):
     # Shaded set-back room walls terminate the glass bays, with sill thickness.
     b.box(xx,yy-side*.42,k*3.35+1.92,bay-.34,.10,1.86,'interior')
    b.box(xx,yy+side*.18,k*3.35+.91,bay-.26,.30,.075,'concrete')
    for dx in (-bay/2+.18,bay/2-.18):b.box(xx+dx,yy+side*.10,k*3.35+1.92,.065,.20,1.86,'seal')
 for j in range(0 if key=='front' else int(w/.45)):
  xx=x-w/2+j*.45;cut=min((d+1)*.46,(w+1)*.22)
  # Folded roof ribs follow the hip profile; no texture-only roof detail.
  t=min(1,max(0,(w/2-abs(xx-x))/max(cut,.01)))
  for side in (-1,1):
   p0=(xx, y+side*(d+1)/2,h+.024);p1=(xx,y+side*(d+1)/2*(1-t),h+1.65*t+.024)
   va=Vector(p0);vc=Vector(p1)
   if (vc-va).length>.02:cylinder(b,va,vc,.018,'roofcap',6)
 for xx in (x-w/2+.32,x+w/2-.32):
  for side in (-1,1):
   yy=y+side*(d/2+.32);line('Gutter outlet elbow',[(xx,yy,h-.1),(xx,yy+side*.28,h-.28),(xx,yy+side*.28,.18),(xx+.30,yy+side*.28,.18)],.052,'metal')
b.finish()
# Campus furnishings give the outdoor foreground real scale.
b=Mesh('V5 pedestrian paving and drainage details')
for x,y,w,d in [(29.8,-48.4,29,.42),(-12,-23,63,.34),(cx,y0-3.0,9,.35)]:
 b.box(x,y,.14,w,d,.05,'drain')
 for j in range(int(w/.16)):b.box(x-w/2+j*.16,y,.18,.035,d,.035,'metal')
# Gym entry doors: individual handles, top transoms and pale paving joints.
front=SITE['gym'][0]-SITE['gym'][2]/2;gy=SITE['gym'][1]
for j in range(10):
 yy=gy-9+j*2;b.box(front-.34,yy,2.0,.12,.05,3.2,'frame')
 if j%2==0:
  for zz in (1.1,1.65):b.box(front-.42,yy+.25,zz,.07,.025,.025,'metal')
  b.box(front-.45,yy+.25,1.37,.045,.04,.52,'metal')
for xx in range(45,62,2):b.box(xx,gy,.135,.018,30,.016,'concrete')
b.finish()
ARCHITECTURE_V5={'reported_times_seconds':[72,82],'repairs':['Deding enclosed infill, floor edges, lobby and window reveals','Primary tangent-aligned window assemblies and closed slab edges'],'signage':'Noto CJK Bold 700; solid extruded bevelled cast letters, 0.085 times letter height depth; converted to meshes','screen_space_reflection':'disabled for stable glazing; opaque proxy panels with physically modelled frames','limits':'Metric dimensions, hidden rooms and wall details remain inferred from photographs.'}

box('小學部前步行道 V5',-36,115.1,.08,48,2.6,.12,'paving')
box('前庭步行道 V5',0,-57.7,.08,34,2.5,.12,'paving')
# Official primary fire-drill photo reveals a metal fascia, wooden entry deck,
# low balustrade, double doors, transoms and gold signage at the canopy edge.
b=Mesh('小學部 V5 photo-led entrance canopy deck and door hardware')
for j in range(40):
 xx=-45+18*(j+.5)/40;yy=arc_y(xx);a=arc_angle(xx);width=18/40/math.cos(a)+.015
 obox(b,xx,yy-.48,3.40,width,1.20,.20,a,'metal')
 obox(b,xx,yy-1.0,3.40,width,.12,.24,a,'frame')
 # Solid timber planks, not a single brown slab.
 for q in range(12):obox(b,xx,yy-.30-q*.13,.25,width,.122,.12,a,'wood')
for xx in (-44.5,-41.5,-29.5,-27.5):
 yy=arc_y(xx);cylinder(b,(xx,yy-1.7,.3),(xx,yy-1.7,1.0),.032,'wood',10)
line('小學入口木扶手',[(xx,arc_y(xx)-1.7,1.0) for xx in [-44.5+j*.25 for j in range(13)]],.036,'wood')
line('小學入口木扶手',[(xx,arc_y(xx)-1.7,1.0) for xx in [-29.5+j*.25 for j in range(9)]],.036,'wood')
for xx in (-39,-37,-35,-33):
 yy=arc_y(xx);a=arc_angle(xx)
 for off in (-.14,.14):obox(b,xx+off,yy-.11,1.30,.025,.06,.40,a,'metal')
 obox(b,xx,yy+.06,2.76,1.78,.12,.065,a,'primaryframe')
for j in range(3):
 obox(b,-36,arc_y(-36)-2.0+j*.3,.08+j*.055,9,1.4-j*.3,.10,0,'wood')
b.finish()
for ob in list(bpy.data.objects):
 if ob.name.startswith('小學部 V5 cast metal sign'):
  ob.location.y-=.91
  if ob.data.body.isascii():ob.location.z=.0+3.26
# Paved arrival forecourt in front of the repaired dormitory entrance.
box('定得樓 V5 arrival forecourt',-.5,69.5,.05,47,7,.10,'paving')

for ob in bpy.data.objects:
 if ob.name.startswith("Sign concealed mounting pin"):ob.location.y-=.91

for key in ['white','primarybrick']:
 nt=M[key].node_tree;p=nt.nodes.get('Principled BSDF');old=p.inputs['Base Color'].links[0].from_socket
 coord=nt.nodes.new('ShaderNodeNewGeometry');n=nt.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=.65;n.inputs['Detail'].default_value=3;nt.links.new(coord.outputs['Position'],n.inputs['Vector'])
 ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.72,.74,.70,1);ramp.color_ramp.elements[1].color=(1,1,1,1);nt.links.new(n.outputs['Fac'],ramp.inputs[0])
 mix=nt.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.32;nt.links.new(old,mix.inputs[1]);nt.links.new(ramp.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],p.inputs['Base Color'])

b=Mesh('前庭山牆 V5 correctly aligned standing seams')
for j in range(58):
 yy=-47.5+j*.47
 for side in (-1,1):cylinder(b,(-10.7+side*6.75,yy,6.725),(-10.7,yy,9.025),.015,'roofcap',6)
b.finish()
# Additional current-Maps observations after the browser connection recovered:
# west primary parking, an oval planted island and the outer east parking lane.
def parking_xy(u,v):
 a=math.radians(13);return(-91.4+math.cos(a)*u-math.sin(a)*v,126.0+math.sin(a)*u+math.cos(a)*v)
b=Mesh('Maps V5 rear primary school parking stalls');a=math.radians(13)
obox(b,-91.4,126,.055,27,43,.11,a,'asphalt')
for side in (-1,1):
 for j in range(15):
  vv=-18.75+j*2.5;p0=parking_xy(side*6.0,vv);p1=parking_xy(side*12.7,vv)
  line('Rear parking white stall lines',[(*p0,.13),(*p1,.13)],.035,'line')
 for j in (-18.75,16.25):
  p0=parking_xy(side*6.0,j);p1=parking_xy(side*6.0,j+2.5);line('Rear parking end lines',[(*p0,.13),(*p1,.13)],.035,'line')
for side in (-1,1):
 pts=[(*parking_xy(side*13,v),.14) for v in [-21.5+j*.5 for j in range(87)]];line('Rear parking curb',pts,.095,'concrete')
b.finish()
# A small number of generic parked vehicles provide scale; placement is illustrative.
def parked_car(name,x,y,angle,paint='cardark'):
 b=Mesh(name);obox(b,x,y,.53,1.78,4.35,.60,angle,paint);obox(b,x,y+.05,1.08,1.50,2.30,.64,angle,'glass');obox(b,x,y+.05,1.43,1.43,2.00,.08,angle,paint)
 for side in (-1,1):
  for front in (-1,1):
   dx=side*.89;dy=front*1.36;c,s=math.cos(angle),math.sin(angle);p=(x+c*dx-s*dy,y+s*dx+c*dy,.35);axis=Vector((c,s,0));cylinder(b,Vector(p)-axis*.10,Vector(p)+axis*.10,.29,'seal',16)
 for end in (-1,1):
  for side in (-1,1):
   dx=side*.61;dy=end*2.19;c,s=math.cos(angle),math.sin(angle);obox(b,x+c*dx-s*dy,y+s*dx+c*dy,.61,.36,.055,.13,angle,'white' if end<0 else 'redletter')
 b.finish()
for j,(side,v) in enumerate([(-1,-15),(-1,-5),(1,-10),(1,0),(1,10),(-1,15)]):
 x,y=parking_xy(side*9.2,v);parked_car('Generic parked campus car',x,y,math.radians(13)+math.pi/2,'carwhite' if j%3==0 else 'cardark')
# Oval island south of primary entrance, visible in the recovered satellite view.
ix,iy=-40.4,111.2;pts=[(ix+3.25*math.cos(t*math.tau/96),iy+2.65*math.sin(t*math.tau/96)) for t in range(96)]
polygon('Maps V5 primary oval planted island',pts,.17,'grass');line('Primary oval island concrete edging',[(x,y,.20) for x,y in pts],.12,'concrete',True)
shrub('Primary island planting',ix,iy,3.5,1.8,.55)
# Outer east parking aligns with the already calibrated east-side road segment.
a=Vector(xy(1453,643));c=Vector(xy(1660,535));t=(c-a).normalized();normal=Vector((t.y,-t.x));length=(c-a).length
ribbon('Maps V5 east parking paved apron',[tuple(a+normal*3),tuple(c+normal*3)],9,.11,'asphalt')
for j in range(int(length/2.6)+1):
 p=a+t*j*2.6+normal*2.0;q=p+normal*4.6;line('East parking white bay marking',[(*p,.15),(*q,.15)],.032,'line')
# Recorded map observations are approximate traced dimensions, not measured parking capacity.
MAPS_REFRESH_V5={'status':'reconnected in same Chrome using fresh task tab, after original tab could not attach','viewed_satellite':['24.8829755,121.1737362,222m','24.8842966,121.1736917,240m'],'map_scale':'20m visible scale; approximately 72 screen pixels in rear view','rear_parking':{'centre':[-91.4,126],'approx_size':[27,43],'angle_degrees':13,'drawn_stall_count_is_not_an_official_capacity':True},'primary_oval_island':{'centre':[-40.4,111.2],'approx_radii':[3.25,2.65]},'photo_checks':['Maps school gallery photo1: forecourt, administrative building, canopy, 2024-09, 行政盧玉麟','Maps photo2: sunken stadium, white upper rails, stair-end arches and slanted canopy, 2024-09, 行政盧玉麟'],'imagery_acquisition_date':'unknown; copyright year is not capture date'}
with open(os.path.join(ROOT,'maps-refresh-observations.json'),'w') as f:json.dump(MAPS_REFRESH_V5,f,ensure_ascii=False,indent=2)

for ob in list(bpy.data.objects):
 if not ob.name.startswith('Landscape tree'):continue
 x,y=ob.location.x,ob.location.y;dx,dy=x+91.4,y-126;aa=math.radians(13);u=math.cos(aa)*dx+math.sin(aa)*dy;v=-math.sin(aa)*dx+math.cos(aa)*dy
 q=Vector((x,y))-a;along=q.dot(t);across=q.dot(normal)
 if (abs(u)<14.5 and abs(v)<22.5) or (-2<along<length+2 and 0<across<10):bpy.data.objects.remove(ob,do_unlink=True)
