"""Editable anonymous student rigs with IK planted feet and source-led clothing."""
M['uniformnavy']=material('Uniform navy woven fabric',(.018,.030,.065),.92,230)
M['uniformwhite']=material('Uniform warm white cloth',(.72,.74,.71),.91,240)
M['uniformblue']=material('Secondary pale blue formal shirt',(.14,.30,.52),.9,250)
M['uniformred']=material('Primary burgundy sports sleeves',(.33,.023,.054),.94,200)
M['uniformroyal']=material('Junior sports blue piping',(.025,.085,.36),.91)
M['uniformorange']=material('Senior PE orange emblem',(.70,.25,.035),.88)
M['skin']=material('Anonymous neutral skin',(.44,.275,.17),.82)
M['hair']=material('Simple dark hair cap',(.014,.011,.012),.85)
M['shoe']=material('Student sneaker dark rubber',(.025,.03,.034),.75)
M['sole']=material('White sneaker soles',(.64,.65,.60),.9)
# Plaid skirt uses local generated coordinates, independent of any student image.
M['plaid']=material('Primary navy burgundy plaid skirt',(.035,.04,.065),.93)
nt=M['plaid'].node_tree;p=nt.nodes.get('Principled BSDF');tex=nt.nodes.new('ShaderNodeTexCoord');sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(tex.outputs['Generated'],sep.inputs[0])
wx=nt.nodes.new('ShaderNodeTexWave');wx.bands_direction='X';wx.inputs['Scale'].default_value=6
wz=nt.nodes.new('ShaderNodeTexWave');wz.bands_direction='Z';wz.inputs['Scale'].default_value=8
for n in (wx,wz):nt.links.new(tex.outputs['Generated'],n.inputs['Vector'])
mix=nt.nodes.new('ShaderNodeMath');mix.operation='MAXIMUM';nt.links.new(wx.outputs['Fac'],mix.inputs[0]);nt.links.new(wz.outputs['Fac'],mix.inputs[1]);r=nt.nodes.new('ShaderNodeValToRGB');r.color_ramp.elements[0].position=.94;r.color_ramp.elements[0].color=(.018,.026,.048,1);r.color_ramp.elements[1].position=.98;r.color_ramp.elements[1].color=(.28,.055,.095,1);nt.links.new(mix.outputs[0],r.inputs[0]);nt.links.new(r.outputs[0],p.inputs['Base Color'])

def ellipsoid(b,centre,radii,mat,n=16,m=12,top=math.pi):
 x,y,z=centre;rx,ry,rz=radii;vs=[]
 for j in range(m+1):
  t=.001+(top-.002)*j/m
  for i in range(n):
   a=i*math.tau/n;vs.append((x+rx*math.sin(t)*math.cos(a),y+ry*math.sin(t)*math.sin(a),z+rz*math.cos(t)))
 b.faces(vs,[(j*n+i,(j+1)*n+i,(j+1)*n+(i+1)%n,j*n+(i+1)%n) for j in range(m) for i in range(n)],mat)
def loft(b,rings,mat,n=20,pleat=0):
 vs=[]
 for z,rx,ry in rings:
  for i in range(n):
   a=i*math.tau/n;r=1+pleat*math.cos(a*10);vs.append((rx*math.cos(a)*r,ry*math.sin(a)*r,z))
 b.faces(vs,[tuple(range(n-1,-1,-1)),tuple(range((len(rings)-1)*n,len(rings)*n))]+[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(len(rings)-1) for i in range(n)],mat)

def rounded_limb(b,a,c,r1,r2,mat):
 a,c=Vector(a),Vector(c);axis=(c-a).normalized();u=axis.cross(Vector((0,1,0)))
 if u.length<.1:u=axis.cross(Vector((1,0,0)))
 u.normalize();v=axis.cross(u);length=(c-a).length;n=20;vs=[]
 for offset,r in [(-r1*.55,.002),(-r1*.25,r1*.65),(0,r1*.94),(length*.28,r1),(length*.80,r2),(length,r2*.97)]:
  p=a+axis*offset
  for j in range(n):vs.append(tuple(p+r*(math.cos(j*math.tau/n)*u+math.sin(j*math.tau/n)*v)))
 b.faces(vs,[tuple(range(n-1,-1,-1)),tuple(range(5*n,6*n))]+[(k*n+i,k*n+(i+1)%n,(k+1)*n+(i+1)%n,(k+1)*n+i) for k in range(5) for i in range(n)],mat)

def linear_action(ob):
 act=ob.animation_data.action
 if hasattr(act,'fcurves'):curves=act.fcurves
 else:
  curves=[]
  for layer in act.layers:
   for strip in layer.strips:
    for bag in strip.channelbags:curves.extend(bag.fcurves)
 for fc in curves:
  for k in fc.keyframe_points:k.interpolation='LINEAR'

def walkperson(idx,cohort,origin,length,angle,height,speed,phase,ground=0,skirt=False):
 scale=height/1.70;period=30;stride=.62*speed*(period/24)/scale
 mesh=Mesh('Student %02d tailored uniform'%idx);groups={}
 def part(bone,fn):
  start=len(mesh.v);fn();groups.setdefault(bone,[]).extend(range(start,len(mesh.v)))
 shirt='uniformwhite' if cohort in ('junior','primary-sailor') else 'uniformblue' if cohort=='senior-formal' else 'uniformnavy'
 part('spine',lambda:loft(mesh,[(.92,.145,.092),(1.01,.16,.105),(1.21,.20,.115),(1.36,.215,.105),(1.42,.135,.08)],shirt))
 part('pelvis',lambda:loft(mesh,[(.80,.15,.09),(.88,.155,.105),(.96,.145,.095)],'uniformnavy'))
 part('spine',lambda:cylinder(mesh,(0,0,1.40),(0,0,1.49),.052,'skin',16))
 part('head',lambda:ellipsoid(mesh,(0,-.006,1.574),(.087,.081,.117),'skin',20,16))
 part('head',lambda:ellipsoid(mesh,(0,.002,1.594),(.091,.084,.105),'hair',20,12,top=1.62))
 # Collar pieces, seams, buttons, emblem. Faces deliberately have no eyes/nose/mouth.
 if cohort=='primary-sailor':
  for side in (-1,1):
   part('spine',lambda side=side:mesh.faces([(side*.025,-.111,1.30),(side*.18,-.095,1.39),(side*.11,-.125,1.22)],[(0,1,2)],'uniformwhite'))
   part('spine',lambda side=side:mesh.faces([(side*.008,-.131,1.30),(side*.075,-.139,1.33),(side*.075,-.14,1.265)],[(0,1,2)],'uniformnavy'))
   part('spine',lambda side=side:mesh.faces([(side*.012,-.134,1.29),(side*.055,-.145,1.16),(side*.018,-.145,1.17)],[(0,1,2)],'uniformnavy'))
  part('pelvis',lambda:loft(mesh,[(.54,.205,.125),(.64,.185,.12),(.91,.145,.10)],'plaid',40,.045))
 else:
  for side in (-1,1):
   part('spine',lambda side=side:mesh.faces([(side*.01,-.108,1.40),(side*.075,-.108,1.37),(side*.042,-.132,1.31)],[(0,1,2)],'uniformnavy' if cohort=='junior' else shirt))
  if cohort=='senior-formal':
   part('spine',lambda:mesh.faces([(-.018,-.135,1.36),(.018,-.135,1.36),(.03,-.135,1.08),(0,-.141,1.04),(-.03,-.135,1.08)],[(0,1,2,3,4)],'uniformnavy'))
  if cohort=='junior':
   # Red/blue vertical shoulder-to-side sports stripes observed in official new-pupil photo.
   for side in (-1,1):
    for off,mat in [(0,'uniformroyal'),(.028,'uniformred')]:
     xx=side*(.145+off)
     part('spine',lambda xx=xx,mat=mat:cylinder(mesh,(xx,.106,1.37),(xx,.106,.98),.004,mat,6))
     part('spine',lambda xx=xx,mat=mat:cylinder(mesh,(xx,-.10,1.35),(xx,-.10,.98),.004,mat,6))
  if cohort=='primary-sport':
   part('spine',lambda:mesh.box(0,-.116,1.20,.36,.02,.028,'uniformwhite'))
   part('spine',lambda:mesh.box(0,-.118,1.14,.34,.02,.018,'uniformwhite'))
  for z in (1.07,1.17,1.25):part('spine',lambda z=z:ellipsoid(mesh,(0,-.122,z),(.007,.004,.007),'uniformwhite',8,5))
 # Small woven crest patch without a real student's name or number.
 part('spine',lambda:mesh.box(-.10,-.119,1.29,.042,.008,.043,'gold' if cohort!='senior-sport' else 'uniformorange'))
 for side,suf in [(-1,'L'),(1,'R')]:
  x=side*.10
  shorts=cohort!='senior-formal'
  part('thigh'+suf,lambda x=x:rounded_limb(mesh,(x,0,.88),(x,-.20,.52 if shorts else .48),.077,.064,'uniformnavy'))
  part('shin'+suf,lambda x=x:ellipsoid(mesh,(x,-.20,.49),(.058,.056,.060),'skin' if shorts else 'uniformnavy',16,10))
  if shorts:
   part('shin'+suf,lambda x=x:cylinder(mesh,(x,-.20,.52),(x,0,.18),.053,'skin',16,r2=.037))
   part('shin'+suf,lambda x=x:cylinder(mesh,(x,0,.26),(x,0,.12),.041,'uniformwhite',16,r2=.039))
  else:part('shin'+suf,lambda x=x:cylinder(mesh,(x,-.20,.49),(x,0,.12),.065,'uniformnavy',16,r2=.047))
  part('foot'+suf,lambda x=x:ellipsoid(mesh,(x,-.055,.075),(.057,.124,.052),'shoe',16,10))
  part('foot'+suf,lambda x=x:ellipsoid(mesh,(x,-.058,.043),(.059,.126,.018),'sole',16,7))
  for zz in (.08,.10):part('foot'+suf,lambda x=x,zz=zz:mesh.box(x,-.10,zz,.075,.016,.009,'uniformwhite'))
  shoulder=(side*.215,0,1.37);elbow=(side*.245,-.015,1.115);wrist=(side*.245,-.035,.91)
  sleeve='uniformred' if cohort=='primary-sport' else shirt
  part('upperarm'+suf,lambda shoulder=shoulder,side=side:rounded_limb(mesh,shoulder,(side*.235,-.006,1.22),.068,.060,sleeve))
  part('upperarm'+suf,lambda side=side:cylinder(mesh,(side*.235,-.006,1.24),(side*.245,-.015,1.115),.050,'skin',16,r2=.042))
  part('forearm'+suf,lambda elbow=elbow,wrist=wrist:cylinder(mesh,elbow,wrist,.043,'skin',16,r2=.029))
  part('forearm'+suf,lambda wrist=wrist:ellipsoid(mesh,(wrist[0],wrist[1],wrist[2]-.037),(.033,.024,.054),'skin',12,10))
  part('forearm'+suf,lambda elbow=elbow:ellipsoid(mesh,elbow,(.043,.041,.043),'skin',12,8))
 # Every character is an editable armature, with per-vertex clothing groups.
 ob=mesh.finish()
 for p in ob.data.polygons:p.use_smooth=True
 armdata=bpy.data.armatures.new('Student %02d walking skeleton'%idx);arm=bpy.data.objects.new('Student %02d | %s'%(idx,cohort),armdata);bpy.context.collection.objects.link(arm)
 bpy.context.view_layer.objects.active=arm;arm.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
 specs=[('pelvis',(0,0,.86),(0,0,1.03),None),('spine',(0,0,1.03),(0,0,1.40),'pelvis'),('head',(0,0,1.40),(0,0,1.66),'spine')]
 for side,suf in [(-1,'L'),(1,'R')]:
  specs += [('thigh'+suf,(side*.10,0,.86),(side*.10,-.20,.49),'pelvis'),('shin'+suf,(side*.10,-.20,.49),(side*.10,0,.12),'thigh'+suf),('foot'+suf,(side*.10,0,.12),(side*.10,-.18,.08),'shin'+suf),('upperarm'+suf,(side*.215,0,1.37),(side*.245,-.015,1.115),'spine'),('forearm'+suf,(side*.245,-.015,1.115),(side*.245,-.035,.91),'upperarm'+suf)]
 for name,head,tail,parent in specs:
  eb=armdata.edit_bones.new(name);eb.head=head;eb.tail=tail
  if parent:eb.parent=armdata.edit_bones[parent]
 bpy.ops.object.mode_set(mode='OBJECT');arm.select_set(False)
 ob.parent=arm;mod=ob.modifiers.new('Tailored clothes skinning','ARMATURE');mod.object=arm
 for name,verts in groups.items():g=ob.vertex_groups.new(name=name);g.add(verts,1,'REPLACE')
 for side,suf,offset in [(-1,'L',0),(1,'R',.5)]:
  target=bpy.data.objects.new('Student %02d %s foot IK'%(idx,suf),None);bpy.context.collection.objects.link(target);target.parent=arm;target.location=(side*.1,0,.12)
  q=f'((frame/{period}+{phase+offset:.8f})%1)'
  for axis,expr in [(1,f'{stride:.8f}*(({q}/.62-.5) if {q}<.62 else (.5-({q}-.62)/.38))'),(2,f'.12+(0 if {q}<.62 else .15*sin(pi*({q}-.62)/.38))')]:
   target.driver_add('location',axis).driver.expression=expr
  pole=bpy.data.objects.new('Student %02d %s knee pole'%(idx,suf),None);bpy.context.collection.objects.link(pole);pole.parent=arm;pole.location=(side*.10,-1.1,.5)
  ik=arm.pose.bones['shin'+suf].constraints.new('IK');ik.target=target;ik.pole_target=pole;ik.chain_count=2;ik.use_stretch=False
  target.rotation_euler=armdata.bones['foot'+suf].matrix_local.to_euler()
  cr=arm.pose.bones['foot'+suf].constraints.new('COPY_ROTATION');cr.target=target;cr.owner_space='WORLD';cr.target_space='WORLD'
  # Ankle levels keep the sole near horizontal throughout stance and lift the toe in swing.
  pb=arm.pose.bones['upperarm'+suf];pb.rotation_mode='XYZ';pb.driver_add('rotation_euler',0).driver.expression=f'{side*.32:.5f}*sin(2*pi*(frame/{period}+{phase:.7f}))'
  pb=arm.pose.bones['forearm'+suf];pb.rotation_mode='XYZ';pb.rotation_euler.x=-.12
 arm.scale=(scale,)*3
 # Root follows a closed walking lane at constant distance per second.
 radius=.33;loop=2*length+math.tau*radius
 def atdist(s):
  s%=loop
  if s<length:return(s,-radius,1,0)
  s-=length
  if s<math.pi*radius:
   a=-math.pi/2+s/radius;return(length+radius*math.cos(a),radius*math.sin(a),-math.sin(a),math.cos(a))
  s-=math.pi*radius
  if s<length:return(length-s,radius,-1,0)
  s-=length;a=math.pi/2+s/radius;return(radius*math.cos(a),radius*math.sin(a),-math.sin(a),math.cos(a))
 last=None;c,sn=math.cos(angle),math.sin(angle)
 for f in list(range(1,2257,4))+[2256]:
  xx,yy,dx,dy=atdist((f-1)*speed/24+phase*loop);xx+=origin[0];yy+=origin[1]
  # Origins are in the unrotated local lane frame; rotate its delta only.
  lx,ly=xx-origin[0],yy-origin[1];arm.location=(origin[0]+c*lx-sn*ly,origin[1]+sn*lx+c*ly,ground-.025)
  a=math.atan2(sn*dx+c*dy,c*dx-sn*dy)+math.pi/2
  if last is not None:
   while a-last>math.pi:a-=math.tau
   while a-last<-math.pi:a+=math.tau
  last=a;arm.rotation_euler=(0,0,a);arm.keyframe_insert('location',frame=f);arm.keyframe_insert('rotation_euler',frame=f)
 linear_action(arm);arm['path_origin']=origin;arm['path_length']=length;arm['path_angle']=angle;arm['path_speed']=speed;arm['path_phase']=phase;arm['path_ground']=ground-.025;arm['cohort']=cohort;arm['anonymous']='No facial features, real identities, student names or numbers';arm['walk']='Constant-distance route, alternating planted-foot IK cycle';return arm

def student_path_at(arm,f):
 origin=arm['path_origin'];length=arm['path_length'];angle=arm['path_angle'];speed=arm['path_speed'];phase=arm['path_phase'];radius=.33;loop=2*length+math.tau*radius
 s=((f-1)*speed/24+phase*loop)%loop
 if s<length:xx,yy,dx,dy=s,-radius,1,0
 elif s<length+math.pi*radius:
  a=-math.pi/2+(s-length)/radius;xx,yy,dx,dy=length+radius*math.cos(a),radius*math.sin(a),-math.sin(a),math.cos(a)
 elif s<2*length+math.pi*radius:xx,yy,dx,dy=2*length+math.pi*radius-s,radius,-1,0
 else:
  a=math.pi/2+(s-2*length-math.pi*radius)/radius;xx,yy,dx,dy=radius*math.cos(a),radius*math.sin(a),-math.sin(a),math.cos(a)
 c,t=math.cos(angle),math.sin(angle)
 return Vector((origin[0]+c*xx-t*yy,origin[1]+t*xx+c*yy,arm['path_ground'])),Vector((c*dx-t*dy,t*dx+c*dy,0))
STUDENT_RIGS=[];idx=0
lanes=[
 ('junior',(-2,-60),25,0,1.60,.90,.10,5),
 ('senior-formal',(20,-52),20,0,1.72,.96,.17,5),
 ('junior',(48,-99),20,math.pi/2,1.58,.90,.10,4),
 ('senior-sport',(-35,-23),47,0,1.70,.97,.17,5),
 ('junior',(-20,-23),27,0,1.57,.88,.17,3),
 ('senior-formal',(-17,-2.35),11,0,1.70,.85,.17,3),
 ('senior-sport',(-19,68),29,0,1.69,.93,.10,4),
 ('primary-sailor',(-58,115),39,0,1.28,.72,.14,5),
 ('primary-sport',(-54,116),34,0,1.30,.74,.14,5),
 ('junior',sport(-27,-28)[:2],30,ANGLE+math.pi/2,1.60,.91,-DEPTH+.05,4)]
for cohort,origin,length,angle,h,speed,ground,count in lanes:
 for j in range(count):
  idx+=1;phase=(j/count+.113*idx)%1
  o=walkperson(idx,cohort,origin,length,angle,h+random.uniform(-.045,.045),speed+random.uniform(-.025,.025),phase,ground,cohort=='primary-sailor');STUDENT_RIGS.append(o.name)
for cohort,origin,length,height,phase in [('junior',(-15,-58),30,1.60,.45),('senior-formal',(-15,-57.2),30,1.72,.475),('primary-sailor',(-55,115),35,1.28,.50),('primary-sport',(-55,115.7),35,1.30,.525)]:
 idx+=1;o=walkperson(idx,cohort,origin,length,0,height,.90 if 'primary' not in cohort else .72,phase,.14 if 'primary' in cohort else .14,cohort=='primary-sailor');STUDENT_RIGS.append(o.name)
with open(os.path.join(ROOT,'student-animation-manifest.json'),'w') as f:
 json.dump({'rig_count':len(STUDENT_RIGS),'rig_names':STUDENT_RIGS,'faces':'Anonymous smooth heads, no detailed facial features','clothing_sources':{'junior':'Official 115 junior new-pupil training: white navy-collar PE with red/blue stripes','senior-sport':'Official 115 senior new-pupil training: navy PE','senior-formal':'Official 115 ceremony: pale-blue shirt and navy tie; school-level formal reference, exact grade assignment unconfirmed','primary':'Official primary school event: sailor white blouse/navy bow/plaid skirt; burgundy/navy sports top'},'animation':'Editable armatures, two-bone leg IK, planted stance with swing lift, reciprocal arms; no image textures of people'},f,ensure_ascii=False,indent=2)
print('V5_STUDENT_RIGS',len(STUDENT_RIGS),flush=True)

for name in STUDENT_RIGS:
 arm=bpy.data.objects[name];num=int(name.split()[1])
 for ob in arm.children:
  if ob.type!='MESH':continue
  for f,hidden in [(1,False),(1320,False),(1321,num not in (44,45)),(1392,num not in (44,45)),(1393,False),(1920,False),(1921,num not in (46,47)),(1992,num not in (46,47)),(1993,False)]:
   ob.hide_render=hidden;ob.keyframe_insert('hide_render',frame=f)
  linear_action(ob)
