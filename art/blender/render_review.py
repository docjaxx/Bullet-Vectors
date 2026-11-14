"""Background render review. Usage: blender --background BV01_Kestrel.blend --python render_review.py

Produces two extra review angles and a 60-frame turntable PNG sequence.
Use ffmpeg on the sequence to produce a 5-second, 12 fps preview.
"""
from pathlib import Path
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
scene=bpy.data.scenes['BV_Kestrel_Lookdev']
root=bpy.data.objects['BV01_Kestrel_ROOT']
camera=scene.camera
scene.render.resolution_x=1200
scene.render.resolution_y=750
scene.eevee.taa_render_samples=256
scene.render.image_settings.file_format='PNG'
scene.frame_set(1)
for name,loc in [('kestrel_rear',(9,13,8)),('kestrel_overhead',(0,-.01,19))]:
    camera.location=loc
    camera.rotation_euler=(Vector((0,.2,.2))-camera.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(ROOT/'art/renders'/f'{name}.png')
    bpy.ops.render.render(write_still=True,scene=scene.name)

camera.location=(10,-14,10)
camera.rotation_euler=(Vector((0,.2,.2))-camera.location).to_track_quat('-Z','Y').to_euler()
scene.render.resolution_x=960
scene.render.resolution_y=600
scene.eevee.taa_render_samples=64
frames=ROOT/'art/renders/frames'
frames.mkdir(exist_ok=True)
for i in range(60):
    # Evaluate authored animation; manual rotation would be overwritten on render.
    scene.frame_set(1+i*4)
    scene.render.filepath=str(frames/f'turntable_{i:04d}.png')
    bpy.ops.render.render(write_still=True,scene=scene.name)
