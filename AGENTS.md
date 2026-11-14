# Bullet Vectors project instructions

- Preserve the hybrid loop: vertical bullet hell → gate approach → tube combat → fold.
- Preserve the gem lock rule: destroying a gem seals that lane permanently for
  the current gate; sealed lanes cannot spawn or contain hostile entities.
- Player traversal remains possible across sealed lanes. Difficulty must grow as
  open lanes shrink, with bounded speed and readable attack telegraphs.
- Thruster kick replaces jump. Its arcade collision rules must be explicit.
- Keep the Kestrel an original angular fighter. Do not import reference-game assets.
- Favor crisp cel bands and clear silhouettes; psychedelic effects must not mask
  bullets, gems, the core hitbox, or locked-lane status.
- Make motion, flash, glow and shake configurable when gameplay effects are added.
- Keep editable Blender sources, repeatable builders and portable game exports together.
- Use named muzzle / hitbox / thruster markers; do not infer weapon origins from bounds.
- Never delete unrelated Blender scenes or objects. Use a separate generated scene.
- Record what actually runs. Do not label an asset viewer or a design document a
  playable game. Verify exports contain only intended assets before committing.
- Remote pushes are authorized to docjaxx/Bullet-Vectors, but preserve remote
  history: fetch first, inspect, merge deliberately; never force push.
