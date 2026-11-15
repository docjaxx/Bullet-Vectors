"""Update only the Kestrel canopy in the opened scene, then export and render.

Run: blender --background BV01_Kestrel.blend --python refine_canopy.py
The same canopy builder is used by build_kestrel.py for clean rebuilds.
"""
from pathlib import Path
import hashlib
import json
import runpy
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
scene=bpy.data.scenes['BV_Kestrel_Lookdev']
collection=bpy.data.collections['BV01 | Flight assembly']
root=bpy.data.objects['BV01_Kestrel_ROOT']
assert Path(bpy.data.filepath).resolve()==(ROOT/'art/blender/BV01_Kestrel.blend').resolve()
scene.frame_set(1)
module=runpy.run_path(str(Path(__file__).with_name('kestrel_canopy.py')))
canopy_names=set(module['CANOPY_NAMES'])
def unaffected_geometry():
    result={}
    for ob in collection.objects:
        if ob.type=='MESH' and ob.name not in canopy_names and not ob.get('kestrel_canopy'):
            result[ob.name]=hashlib.sha256(repr([
                tuple(v.co) for v in ob.data.vertices]).encode()).hexdigest()
    return result
before=unaffected_geometry()
for ob in list(collection.objects):
    if ob.name in canopy_names or ob.get('kestrel_canopy'):
        bpy.data.objects.remove(ob,do_unlink=True)
created=module['build_canopy'](collection,root,bpy.data.materials['BV_Canopy'],
    bpy.data.materials['BV_Graphite'],bpy.data.materials['BV_Ion_White'],bpy.data.materials['BV_Ink'])
assert unaffected_geometry()==before,'Unrelated ship geometry changed'
assert len(created)==5
glass=bpy.data.objects['04 | Canopy glass']
assert max(v.co.z for v in glass.data.vertices)<.58
body=bpy.data.objects['01 | Monocoque blade fuselage']
for vertex in glass.data.vertices:
    x,y,z=vertex.co
    hit,location,normal,index=body.ray_cast(Vector((x,y,5)),Vector((0,0,-1)))
    assert not hit or z>=location.z-.001,'Glass intersects the fuselage'
assert all(name in collection.objects for name in ['Muzzle_L','Muzzle_R','Hitbox_Core','ThrusterKick'])

# Reuse the source builder's portable-export routine, preserving lookdev materials.
source=Path(__file__).with_name('build_kestrel.py').read_text(encoding='utf-8')
export_code=source[source.index('# Portable export:'):source.index('for screen in bpy.data.screens:')]
palette={name:tuple(bpy.data.materials[name].diffuse_color[:3]) for name in
    ['BV_Ceramic_Ivory','BV_Cobalt','BV_Graphite','BV_Signal_Coral','BV_Canopy']}
ns={'ROOT':ROOT,'bpy':bpy,'palette':palette,'ship_collection':collection,'root':root}
exec(compile(export_code,str(Path(__file__).with_name('build_kestrel.py')),'exec'),ns)
scene['canopy_revision']='Compact flush fighter canopy / downward-sloping windscreen'
scene.render.resolution_x=1600
scene.render.resolution_y=1000
scene.render.image_settings.file_format='PNG'
scene.render.filepath=str(ROOT/'art/renders/kestrel_hero.png')
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
bpy.ops.render.render(write_still=True,scene=scene.name)

# Cockpit-focused review angle; restore live viewport scene state after rendering.
camera=scene.camera
camera_state=(camera.location.copy(),camera.rotation_euler.copy(),camera.data.ortho_scale)
hidden=[(ob,ob.hide_render) for ob in bpy.data.collections['BV | Fold-space studio'].objects
        if ob.type in {'FONT','CURVE'}]
try:
    for ob,old in hidden: ob.hide_render=True
    camera.location=(4.5,-6.7,3.1)
    camera.rotation_euler=(Vector((0,-.70,.45))-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.ortho_scale=4.6
    scene.render.filepath=str(ROOT/'art/renders/kestrel_canopy_detail.png')
    bpy.ops.render.render(write_still=True,scene=scene.name)
finally:
    for ob,old in hidden: ob.hide_render=old
    camera.location,camera.rotation_euler,camera.data.ortho_scale=camera_state
    scene.render.filepath=str(ROOT/'art/renders/kestrel_hero.png')
print(json.dumps({'canopy_objects':len(created),'other_meshes_unchanged':len(before),
    'canopy_max_height':max(v.co.z for v in glass.data.vertices),'blend':bpy.data.filepath}))
