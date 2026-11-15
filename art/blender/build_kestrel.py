"""Bullet Vectors / BV-01 Kestrel. Run in Blender 5.x with bpy.

Creates a separate scene, preserving the user's existing scene. The game GLB
uses portable PBR base materials; the Blender showcase uses stepped toon light.
"""
from pathlib import Path
import math
import random
import runpy
import bpy
import bmesh
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
scene = bpy.data.scenes.new('BV_Kestrel_Lookdev')
scene['bullet_vectors_generated'] = True
bpy.context.window.scene = scene
scene.render.engine = 'BLENDER_EEVEE'
ship_collection = bpy.data.collections.new('BV01 | Flight assembly')
stage_collection = bpy.data.collections.new('BV | Fold-space studio')
scene.collection.children.link(ship_collection)
scene.collection.children.link(stage_collection)
root = bpy.data.objects.new('BV01_Kestrel_ROOT', None)
ship_collection.objects.link(root)
root['forward_axis'] = '-Y (Blender); -Z after glTF conversion'
root['role'] = 'Original fold-space interceptor / visual prototype'

def emission(name, color, strength=1):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    n = m.node_tree.nodes
    n.clear()
    e = n.new('ShaderNodeEmission')
    e.inputs['Color'].default_value = (*color,1)
    e.inputs['Strength'].default_value = strength
    o = n.new('ShaderNodeOutputMaterial')
    m.node_tree.links.new(e.outputs[0], o.inputs['Surface'])
    return m

ink = emission('BV_Ink', (.005,.009,.025))
ink.use_backface_culling = True
palette = {}
def toon(name, color):
    m = bpy.data.materials.new('BV_'+name)
    m.diffuse_color = (*color,1)
    m.use_nodes = True
    n=m.node_tree.nodes
    n.clear()
    d=n.new('ShaderNodeBsdfDiffuse')
    d.inputs['Color'].default_value=(1,1,1,1)
    s=n.new('ShaderNodeShaderToRGB')
    r=n.new('ShaderNodeValToRGB')
    r.color_ramp.interpolation='CONSTANT'
    ramp=r.color_ramp
    ramp.elements.remove(ramp.elements[1])
    for i,(pos,factor) in enumerate([(0,.19),(.28,.48),(.52,.83),(.78,1.12)]):
        e=ramp.elements[0] if i==0 else ramp.elements.new(pos)
        e.position=pos
        e.color=tuple(min(c*factor,1) for c in color)+(1,)
    out=n.new('ShaderNodeOutputMaterial')
    em=n.new('ShaderNodeEmission')
    m.node_tree.links.new(d.outputs[0],s.inputs[0])
    m.node_tree.links.new(s.outputs[0],r.inputs[0])
    m.node_tree.links.new(r.outputs[0],em.inputs[0])
    m.node_tree.links.new(em.outputs[0],out.inputs[0])
    palette[m.name]=color
    return m

ivory=toon('Ceramic_Ivory',(.79,.9,.94))
blue=toon('Cobalt',(.065,.24,.49))
slate=toon('Graphite',(.055,.085,.145))
coral=toon('Signal_Coral',(.98,.105,.11))
glass=toon('Canopy',(.055,.52,.69))
cyan=emission('BV_Ion_Cyan',(.01,.75,1),3.5)
hot=emission('BV_Ion_White',(.45,.92,1),5)
magenta=emission('BV_Fold_Magenta',(.7,.015,.35),2)
muted=emission('BV_Grid',(.045,.075,.19),1)
white=emission('BV_Type',(.7,.9,.98),1)

def mesh(name, vertices, faces, mat, outlined=True, ship=True):
    data=bpy.data.meshes.new(name)
    data.from_pydata(vertices, [], faces)
    data.update()
    bm=bmesh.new()
    bm.from_mesh(data)
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    bm.to_mesh(data)
    bm.free()
    obj=bpy.data.objects.new(name,data)
    (ship_collection if ship else stage_collection).objects.link(obj)
    if ship: obj.parent=root
    data.materials.append(mat)
    if outlined:
        data.materials.append(ink)
        mod=obj.modifiers.new('Ink silhouette','SOLIDIFY')
        mod.thickness=.023
        mod.offset=1
        mod.use_flip_normals=True
        mod.use_rim=False
        mod.material_offset=1
    return obj

def prism(name, points, depth, mat, outlined=True):
    # Arbitrary angular top contour with a matching bottom contour.
    n=len(points)
    verts=points+[(x,y,z-depth) for x,y,z in points]
    faces=[tuple(range(n)),tuple(range(2*n-1,n-1,-1))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return mesh(name,verts,faces,mat,outlined)

def line(name, points, mat, width=.018, ship=False, cyclic=False):
    curve=bpy.data.curves.new(name,'CURVE')
    curve.dimensions='3D'
    curve.bevel_depth=width
    curve.bevel_resolution=0
    s=curve.splines.new('POLY')
    s.points.add(len(points)-1)
    for p,co in zip(s.points,points): p.co=(*co,1)
    s.use_cyclic_u=cyclic
    ob=bpy.data.objects.new(name,curve)
    (ship_collection if ship else stage_collection).objects.link(ob)
    if ship: ob.parent=root
    curve.materials.append(mat)
    return ob

# Narrow, faceted fuselage with a long blade nose and a raised spine.
stations=[(-4.15,.025,.03,-.04),(-1.65,.59,.44,-.27),
          (.45,.84,.48,-.4),(2.05,.68,.28,-.28)]
verts=[]
for y,w,top,bottom in stations:
    verts += [(-w,y,0),(0,y,top),(w,y,0),(0,y,bottom)]
faces=[(3,2,1,0)]
for j in range(len(stations)-1):
    for k in range(4): faces.append((j*4+k,j*4+(k+1)%4,(j+1)*4+(k+1)%4,(j+1)*4+k))
faces.append((12,13,14,15))
mesh('01 | Monocoque blade fuselage',verts,faces,ivory)
prism('02 | Ventral graphite keel',[(-.22,-2.8,-.1),(.22,-2.8,-.1),(.5,1.85,-.15),(-.5,1.85,-.15)],.18,slate)

# Gull/arrow wings, split trailing contours, raised tips and inset panels.
for side in [-1,1]:
    tag='PORT' if side<0 else 'STARBOARD'
    def p(coords): return [(side*x,y,z) for x,y,z in coords]
    prism(tag+' | Swept ceramic wing',p([(.48,-.95,.12),(4.7,.78,.26),(4.3,2.55,.30),
        (3.35,1.72,.12),(2.35,2.18,.04),(.68,1.32,.04)]),.19,ivory)
    prism(tag+' | Cobalt flight panel',p([(1.12,-.45,.15),(4.36,.9,.30),
        (4.12,2.03,.33),(3.17,1.21,.16),(2.32,1.74,.09),(1.07,1.04,.09)]),.025,blue)
    prism(tag+' | Coral wing tip',p([(4.25,.69,.3),(4.72,.87,.30),(4.32,2.54,.34),(4.01,2.19,.32)]),.035,coral)
    line(tag+' | Leading ion strip',p([(.99,-.68,.18),(3.91,.51,.32)]),cyan,.025,True)
    line(tag+' | Panel scribe',p([(1.17,.65,.18),(2.22,1.25,.19),(2.74,.94,.23)]),ink,.015,True)
    # Twin nacelles are long diamond-section mechanical pods.
    x=side*1.35
    pod=[(x-.28,-.33,.04),(x,-.75,.32),(x+.28,-.33,.04),(x+.32,1.95,.04),
         (x,2.2,.42),(x-.32,1.95,.04),(x,1.5,-.29)]
    mesh(tag+' | Engine nacelle',pod,[(0,1,4,5),(1,2,3,4),(0,5,6),(2,6,3),(3,6,5,4),(0,6,2,1)],slate)
    prism(tag+' | Nacelle armor',[(x-.2,.15,.26),(x+.2,.15,.26),(x+.22,1.6,.37),(x-.22,1.6,.37)],.07,ivory)
    # Vertical tail fins splay outward, keeping an aggressive silhouette.
    mesh(tag+' | Canted stabilizer',p([(1.15,1.02,.24),(1.63,1.44,1.48),(1.68,2.33,1.25),
         (1.23,2.01,.24),(1.23,1.03,.24),(1.71,1.44,1.48),(1.76,2.33,1.25),(1.31,2.01,.24)]),
         [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],blue)
    line(tag+' | Stabilizer edge',p([(1.64,1.44,1.49),(1.69,2.31,1.26)]),coral,.045,True)
    # Exposed barrel / wing-mounted weapon hardpoint.
    bx=side*2.85
    prism(tag+' | Blaster mount',[(bx-.13,-.31,.02),(bx+.13,-.31,.02),
        (bx+.2,.95,.04),(bx-.2,.95,.04)],.23,slate)
    prism(tag+' | Blaster barrel',[(bx-.07,-1.02,-.01),(bx+.07,-1.02,-.01),
        (bx+.09,.37,.01),(bx-.09,.37,.01)],.13,ivory)
    line(tag+' | Muzzle aperture',[(bx-.065,-1.025,-.045),(bx+.065,-1.025,-.045)],cyan,.028,True)
    # Engine exhaust rings, facing aft along +Y.
    for radius,y,mat in [(.27,2.14,slate),(.20,2.19,cyan),(.12,2.22,hot)]:
        ring=[(x+radius*math.cos(i*math.tau/8),y,.08+radius*math.sin(i*math.tau/8)) for i in range(8)]
        line(tag+' | Exhaust collar',ring,mat,.047 if radius>.2 else .033,True,True)
    for radius,length,mat in [(.16,1.4,cyan),(.085,.85,hot)]:
        pts=[(x+radius*math.cos(i*math.tau/6),2.23,.08+radius*math.sin(i*math.tau/6)) for i in range(6)]
        pts.append((x,2.23+length,.08))
        mesh(tag+' | Ion exhaust',pts,[tuple(range(5,-1,-1))]+[(i,(i+1)%6,6) for i in range(6)],mat,False)
    for i in range(4):
        y=.43+i*.22
        line(tag+' | Heat vent',[(x-.13,y,.343+i*.009),(x+.13,y,.343+i*.009)],slate,.026,True)

# Smooth, elongated fighter canopy with a low saddle and separate windscreen.
canopy_builder=runpy.run_path(str(Path(__file__).with_name('kestrel_canopy.py')))
canopy_builder['build_canopy'](ship_collection,root,glass,slate,hot,ink)
prism('06 | Nose signal chevron',[(-.19,-3,.17),(0,-3.38,.13),(.19,-3,.17),
    (.25,-2.47,.27),(0,-2.72,.26),(-.25,-2.47,.27)],.015,coral)
line('07 | Dorsal light',[(0,.76,.47),(0,1.67,.34)],cyan,.025,True)
for side in [-1,1]:
    line('08 | Thruster kick nozzle',[(side*.45,-.72,-.31),(side*.45,-.35,-.36)],magenta,.07,True)

# Editable mount markers for subsequent weapon and recoil implementations.
for name,loc in [('Muzzle_L',(-2.85,-1.04,-.04)),('Muzzle_R',(2.85,-1.04,-.04)),
                 ('ThrusterKick',(0,-.6,-.4)),('Hitbox_Core',(0,-.3,0))]:
    ob=bpy.data.objects.new(name,None)
    ship_collection.objects.link(ob)
    ob.parent=root
    ob.location=loc
    ob.empty_display_size=.12

# Receding polygon gate acts as context; it never obscures the ship silhouette.
for j in range(9):
    radius=5.7+j*.30
    y=7.0+j*1.25
    pts=[(radius*math.cos(i*math.tau/12),y,radius*math.sin(i*math.tau/12)) for i in range(12)]
    line('Gate | Depth ring %02d'%j,pts,magenta if j%3==0 else muted,.018,False,True)
for i in range(12):
    angle=i*math.tau/12
    line('Gate | Lane %02d'%i,[(5.7*math.cos(angle),7,5.7*math.sin(angle)),
        (8.1*math.cos(angle),17,8.1*math.sin(angle))],muted,.014)
random.seed(174)
for i in range(70):
    x=random.uniform(-17,17)
    y=random.uniform(6,22)
    z=random.uniform(-8,12)
    line('Space | Streak %02d'%i,[(x,y,z),(x,y+random.uniform(.1,.7),z)],muted,.012)

world=bpy.data.worlds.new('BV | Midnight world')
world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.006,.01,.028,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.35
scene.world=world
def area(name,loc,energy,color,size):
    data=bpy.data.lights.new(name,'AREA')
    data.energy=energy
    data.color=color
    data.shape='DISK'
    data.size=size
    ob=bpy.data.objects.new(name,data)
    stage_collection.objects.link(ob)
    ob.location=loc
    ob.rotation_euler=(Vector((0,0,0))-ob.location).to_track_quat('-Z','Y').to_euler()
area('Key | Cool daylight',(-4,-7,9),1800,(.8,.92,1),5)
area('Rim | Fold violet',(4,6,6),2400,(.65,.2,1),4)
area('Fill | Engine cyan',(5,-2,3),700,(.2,.8,1),4)
cam_data=bpy.data.cameras.new('Camera | Hero')
cam=bpy.data.objects.new('Camera | Hero',cam_data)
stage_collection.objects.link(cam)
cam.location=(10,-14,10)
target=Vector((0,.2,.2))
cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
cam_data.type='ORTHO'
cam_data.ortho_scale=16.4
scene.camera=cam

def hud_text(name,text,x,y,size,mat):
    data=bpy.data.curves.new(name,'FONT')
    data.body=text
    data.size=size
    data.space_character=1.15
    ob=bpy.data.objects.new(name,data)
    stage_collection.objects.link(ob)
    data.materials.append(mat)
    ob.parent=cam
    ob.location=(x,y,-12)
    return ob
hud_text('Title','BULLET VECTORS',-7.45,3.75,.58,white)
hud_text('Subtitle','F O L D - S P A C E   I N T E R C E P T O R',-7.42,3.28,.16,cyan)
hud_text('Ship caption','BV-01  /  KESTREL',-7.4,-3.55,.29,white)
hud_text('Technical caption','TWIN BLASTER    /    THRUSTER KICK    /    CERAMIC ARMOR',-7.4,-3.93,.135,cyan)
hud_text('Version caption','VISUAL DEVELOPMENT  001',3.72,-3.92,.135,white)

scene.render.resolution_x=1600
scene.render.resolution_y=1000
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.view_settings.view_transform='Standard'
scene.render.film_transparent=False
scene.render.fps=30
scene.frame_start=1
scene.frame_end=241
root.rotation_euler=(0,0,0)
root.keyframe_insert(data_path='rotation_euler',frame=1)
root.rotation_euler.z=math.tau
root.keyframe_insert(data_path='rotation_euler',frame=241)
if root.animation_data and root.animation_data.action:
    action=root.animation_data.action
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for fc in bag.fcurves:
                    for kp in fc.keyframe_points: kp.interpolation='LINEAR'
scene.frame_set(1)

# Compositor glare with a restrained bloom so the ceramic body stays crisp.
scene.use_nodes=True
tree=bpy.data.node_groups.new('BV | Restrained neon bloom','CompositorNodeTree')
scene.compositing_node_group=tree
rl=tree.nodes.new('CompositorNodeRLayers')
gl=tree.nodes.new('CompositorNodeGlare')
gl.inputs['Type'].default_value='Fog Glow'
gl.inputs['Quality'].default_value='High'
gl.inputs['Strength'].default_value=.35
gl.inputs['Size'].default_value=.35
out=tree.nodes.new('NodeGroupOutput')
tree.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor')
tree.links.new(rl.outputs['Image'],gl.inputs['Image'])
tree.links.new(gl.outputs['Image'],out.inputs['Image'])

# Portable export: the stepped shader is rebuilt by the Godot showcase shader.
temporary=[]
for ob in ship_collection.objects:
    if ob.type not in {'MESH','CURVE'}: continue
    for slot in ob.material_slots:
        source=slot.material
        if source and source.name in palette:
            pm=bpy.data.materials.get(source.name+'_GLTF')
            if not pm:
                pm=bpy.data.materials.new(source.name+'_GLTF')
                pm.use_nodes=True
                pm.diffuse_color=source.diffuse_color
                bsdf=pm.node_tree.nodes.get('Principled BSDF')
                bsdf.inputs['Base Color'].default_value=source.diffuse_color
                bsdf.inputs['Roughness'].default_value=.72
            temporary.append((slot,source))
            slot.material=pm
bpy.ops.object.select_all(action='DESELECT')
for ob in ship_collection.objects: ob.select_set(True)
bpy.context.view_layer.objects.active=root
export_path=ROOT/'assets/ships/bv01_kestrel.glb'
bpy.ops.export_scene.gltf(filepath=str(export_path),export_format='GLB',use_selection=True,use_active_scene=True,
    export_apply=True,export_animations=False,export_extras=True)
for slot,source in temporary: slot.material=source

for screen in bpy.data.screens:
    for ar in screen.areas:
        if ar.type=='VIEW_3D':
            ar.spaces.active.region_3d.view_perspective='CAMERA'
            ar.spaces.active.shading.type='MATERIAL'
            ar.spaces.active.overlay.show_overlays=False
scene.render.filepath=str(ROOT/'art/renders/kestrel_hero.png')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'art/blender/BV01_Kestrel.blend'))
result={'scene':scene.name,'objects':len(ship_collection.objects),'blend':bpy.data.filepath,
    'glb':str(export_path),'render':scene.render.filepath}
