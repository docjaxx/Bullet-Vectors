# BV-01 Kestrel asset contract

- `bv01_kestrel.glb`: self-contained GLB, selected flight assembly only.
- Source: `art/blender/BV01_Kestrel.blend`, scene `BV_Kestrel_Lookdev`.
- Authoring axis: X right, -Y forward, Z up. glTF: X right, -Z forward, Y up.
- One Blender unit is one model unit. Current span is approximately 9.5 units;
  choose a uniform gameplay scale at the parent, not individual armor parts.
- Parent: `BV01_Kestrel_ROOT`; separate parts for armor, fins, barrels and exhaust.
- Markers: `Muzzle_L`, `Muzzle_R`, `ThrusterKick`, `Hitbox_Core`.
- Hitbox marker is a suggested center, not a finished collision shape.
- No collision meshes, LODs, skeletal rig or gameplay damage states yet.
- Inverted ink shells are included. Cull their back faces in the target engine.
- Curves export as meshes with applied geometry. PBR base colors replace Blender
  toon nodes for portability; rebuild cel-band lighting in the engine.
- Shader-generated bloom and the studio gate/HUD/camera/lights are not in the GLB.
- The Blender presentation turntable is deliberately excluded from game export.
- Exhaust is part of the visual asset for now; replace it with pooled runtime
  effects when thrust state and performance budgets are established.
