# Development roadmap

## 0.0.1 — Visual foundation (this milestone)

- [x] Original angular Kestrel ship, editable Blender scene and portable GLB.
- [x] Toon material proposal, fold-space presentation and turntable animation.
- [x] Core loop, lane rules, weapon/enemy starting set and art principles.
- [x] Publish the visual foundation to GitHub on `main`.

## 0.1 — Playable gate slice

Confirm the engine; proposed default Godot 4. Implement a twelve-lane circular
gate with the Kestrel at its rim, one blaster, Splinters, a visible hull core and
thruster kick. Add a gem timer, atomic lane closure and final-gate warp state.

Acceptance: each gem seals exactly one lane; all enemies/bullets in that lane
clear; no further hostile event uses it. The player can traverse every rim
segment. All twelve closures lead to exactly one warp-ready event. Test final
lane pressure, pause/resume, death during a kick and repeated gem hits.

## 0.2 — Vertical bullet-hell slice

Add a short free-flight stage with two hand-authored patterns, focus movement,
clear bullet outlines and a safe gate approach. Carry hull, weapon and score
through the transition. Validate collision readability and frame-time limits.

## 0.3 — One complete loop

Connect flight → gate → warp → a second flight section. Add a square gate,
adjacency-aware movement, Rim Wraiths, kick cooldown feedback and quick restart.
Seed random choices for reproducible debugging and tune the final three lanes.

## 0.4 — Weapons and alien behavior

Add Fan Prism, Needle Beam, weapon cycling, Phase Mites and Prism Husks. Test
weapon adapters on concave shapes, sealed-neighbor routing and single-lane gates.

## 0.5 — Spectacle and accessibility

Add pooled particles, impact freeze, musical pressure layers, restrained bloom,
fold transitions, controller support, remapping, reduced-flash and motion controls.
Profile the worst-case open-flight barrage and final-lane encounter.

## Working rule

Keep each version independently runnable once the engine project exists. Build
one enjoyable loop before adding a campaign, progression tree or large roster.
Do not merge a visual change that makes bullets, gems or locked lanes ambiguous.
