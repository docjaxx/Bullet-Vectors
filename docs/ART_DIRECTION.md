# Art direction — graphic ships in impossible space

## Visual thesis

Hard-edged, readable cel-shaded objects inside a vivid, responsive vector world.
Use the broad influence of exuberant arcade psychedelia: depth pulses, rhythmic
color, impossible geometry, exuberant particle bursts and playful alien beings.
Keep the fighter and hostile silhouettes stable enough to read through it all.

The art should establish its own identity rather than reproduce another game's
ship mesh, enemy roster, interface or exact effects sequence.

## Palette and hierarchy

| Element | Direction |
| --- | --- |
| Player armor | Cool ivory with cobalt inset panels and coral identifier tips |
| Player fire / engines | Cyan-white, narrow cores, restrained bloom |
| Enemy bullets | Warm orange/red fill with a dark perimeter; shape distinguishes types |
| Fold-space geometry | Deep navy, electric violet and magenta |
| Gem | Amber-white faceted diamond with a distinct pulse and shape |
| Sealed lane | Persistent cool green seam, closure glyph and fading particulate curtain |
| HUD | Quiet off-white/cyan; keep it outside the densest combat area |

Use three or four discrete light bands. Keep edges crisp and visible at gameplay
scale. Mesh detail must be earned by silhouette or motion readability; do not
spend the gameplay budget on microscopic greebles.

## Effects vocabulary

- **Blaster:** bright short core, forked recoil sparks, quick impact polygon.
- **Thruster kick:** cyan engine flare, magenta displacement rings, brief drawn
  speed-line fan. The landing marker remains crisp.
- **Gem lock:** graphic white impact, outward faceted fragments, one shock ring,
  then a permanent seam. A unique sound communicates closure without color alone.
- **Compression:** tighter depth pulses and increasing musical layers; the
  bullet colors, hazard outlines and aiming cursor remain stable.
- **Fold:** all lane seams align, the frame stretches inward, and the ship
  accelerates through a stable geometric aperture.

Avoid full-screen additive noise during precise dodging. Put most decoration
behind the play surface; separate impacts from hostile projectiles by shape,
color and lifetime. Use short effect pools and a defined particle budget.

## Comfort options for the gameplay milestone

Independent intensity controls for bloom, shake, background motion and chromatic
distortion. Reduced-flash mode replaces white-out impacts with outlined rings.
Do not require rapid flashing to communicate lane status. Preserve HUD contrast
and offer an alternate bullet palette with shape cues.

## Kestrel review

The current Blender scene is a look-development proposal. Its ink-shell geometry
and emissive materials export; its Shader-to-RGB toon nodes do not transfer to
game engines. Rebuild stepped lighting in the chosen engine. Check the exported
asset from overhead and at a small projected size before approving gameplay use.
