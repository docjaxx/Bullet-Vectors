# Bullet Vectors — game design v0.1

## Premise and rhythm

Folded space is inhabited. A warp route is safe only when every vector has been
cleared and locked; folding into uncleared lanes would put the ship through
occupied space. The player alternates between open-space bullet storms and
fights at the rim of a dimensional gate. Every successful gate reveals a new
region, new tube topology and more aggressive fold-space inhabitants.

The intended feel combines a nimble fighter, deliberate bullet-hell dodging,
rhythmic lane targeting and intense vector-space spectacle. Transitions should
feel like one continuous flight rather than a menu between separate modes.

## One level

1. **Open flight:** move freely in a vertical playfield, dodge patterns, switch
   blasters, collect upgrades and survive a authored wave sequence.
2. **Gate approach:** a gate expands into view. Existing bullets fade or clear
   during a short safe handoff; player hull and weapon state persist.
3. **Gate combat:** snap onto the rim, move lane to lane, fire inward. Enemies
   climb outward from depth while occasional rim enemies threaten traversal.
4. **Seal:** after a survival interval, a clearly telegraphed gem appears in an
   open lane. Destroy it to trigger an explosion that clears and seals that lane.
5. **Compression:** repeat while the surviving lanes become more dangerous.
6. **Fold ready:** when all lanes are sealed, hostile spawning stops and all
   remaining hostiles/projectiles are cleared. The gate visibly stabilizes.
7. **Fold:** the player activates the warp, then enters the next open-flight stage.

The first prototype uses a short 30-second flight section and a 12-lane gate.
These timings, counts and all numeric values below are starting tuning values.

## Gate rules and invariants

| Event | Required behavior |
| --- | --- |
| Enemy spawn | Choose only from current open lanes; never reroll indefinitely |
| Gem spawn | At most one active gem; choose an open lane only |
| Gem destruction | Atomically seal its lane, clear hostiles/bullets in it, play lock explosion |
| Explosion propagation | Visual shockwave may cross neighbors; it does not seal them |
| Sealed lane | No hostile entry, spawn, projectile route or lane-hop destination |
| Existing enemy in sealed lane | Remove during the sealing event, including rim enemies bound to it |
| Player crosses sealed lane | Allowed; preserve a complete navigable rim |
| Shooting sealed lane | Harmless visual impact, with clear sealed feedback |
| Last open lane sealed | No more spawn selection; transition exactly once to FOLD_READY |
| Warp | Allowed only in FOLD_READY and after confirmation input |

A lane has a stable integer identifier independent of tube vertices. Geometry
must not define gameplay identity. Store lock status in the gate model, not in
the glowing material. Destroyed gems and lane locks cannot be scored twice.

### Increasing pressure without impossible end states

Let `sealed_fraction = sealed_count / lane_count`. Start with:

- Enemy travel multiplier: `1 + 0.8 * sealed_fraction` (bounded at 1.8×).
- Spawn interval: `max(0.38, 1.15 - 0.7 * sealed_fraction)` seconds.
- Concurrent active enemies: `min(12, 2 + 2 * open_lane_count)`.
- Gem interval: 6–9 seconds; start the next timer after the prior gem is resolved.
- Minimum telegraph: 0.6 seconds, unaffected by the speed multiplier.

Fewer routes create denser pressure, but the concurrency cap falls near the end.
Spawns must leave a viable shooting/recovery window. A late lane-hop enemy may
choose only an adjacent open lane; if none exists, it stays put. With one open
lane, use staggered enemies rather than unavoidable simultaneous arrivals.

## Ship and controls (proposed)

| Action | Keyboard | Controller |
| --- | --- | --- |
| Free movement / rim travel | WASD or arrows | Left stick / D-pad |
| Fire | Space / left mouse | Right trigger |
| Focus movement (open flight) | Shift | Left trigger |
| Thruster kick | X / right mouse | South face button |
| Cycle blaster | Q / E | Shoulder buttons |
| Activate stable warp | Enter | North face button |
| Pause | Escape | Start |

**Thruster kick:** a rapid outward/backward thrust that lifts the ship off the
rim to pass over a rim threat while maintaining its firing lane. Proposed
duration 0.6 seconds, cooldown 2.5 seconds. Temporarily ignore rim-enemy contact
only; bullets still hurt. Clearly show the cooldown and landing point. In open
flight, use a short backward dash with the same cooldown. No blanket invulnerability
is assumed. Test the dash against playfield boundaries and corners.

The visible fighter is larger than its collision core. Show the core when
focused. Initial survivability: three hull hits with a short, visible recovery
window; tune after the first playable build. Arcade restart must be immediate.

## Starting weapon set

| Weapon | Behavior | Tradeoff |
| --- | --- | --- |
| Twin Vector | Fast paired bolts in the current forward direction | Reliable baseline |
| Fan Prism | Five-shot spread in flight; center + neighboring open lanes in gate mode | Lower damage per bolt |
| Needle Beam | Narrow sustained beam with piercing | Heat cap; focus movement penalty |
| Pulse Lance | Slow charged packet, strong direct hit and small blast | Requires commitment |

Use one shared weapon resource across modes; the mode supplies aim/shot routing.
Do not allow spread damage to reopen or silently seal lanes. Gem damage and
scoring must use the same hit resolution as ordinary targets.

## Fold-space inhabitants

| Enemy | First behavior | Escalation |
| --- | --- | --- |
| Splinter | Direct climber / aimed flight shot | Faster staggered groups |
| Phase Mite | Telegraph, then hop into an adjacent open lane | Two hops with an audible cue |
| Prism Husk | Armored face that opens on a fixed pulse | Alternating vulnerable rhythms |
| Rim Wraith | Reaches the rim and patrols open portions | Pressures thruster-kick timing |
| Fold Choir | Elite that broadcasts rotating shot patterns | Pattern variation; never hide telegraphs |

Keep the first playable slice to Splinters and Rim Wraiths. Add complex enemies
only once aiming, thruster timing and final-lane difficulty are enjoyable.

## Tube shapes

Begin with a regular dodecagon. Follow with triangular, square, star, asymmetric
flower and open horseshoe layouts. Open shapes need explicit endpoint behavior;
do not wrap across a nonexistent connection. Render interpolation along the rim
must preserve the underlying adjacency graph, including concave corners.

## State ownership and architecture

`RunState`: hull, score, weapon, level seed and upgrades. `FlightDirector` owns
free-flight waves. `GateState` owns locks, active gem and spawn eligibility.
`TubeLayout` supplies lane positions, paths and adjacency. `PlayerMotor` selects
free movement or rim traversal. `WeaponSystem` emits shots using the current
mode's targeting adapter. `TransitionDirector` owns safe handoffs and folding.

State flow: FLIGHT → APPROACH → GATE_COMBAT → FOLD_READY → FOLD → next FLIGHT.
PAUSED suspends simulation/timers; GAME_OVER clears live spawning. Visual effects
subscribe to simulation events and cannot mutate lock or score state themselves.

## Decisions to validate in play

- Does the player prefer one gem at a time or simultaneous gem choices?
- Should sealed lanes remain safe traversal zones for rim threats? Current design: yes.
- Does a manual warp confirmation feel satisfying or delay momentum?
- Is the thruster kick still useful when only one enemy lane remains?
- Do open-flight upgrades make the gate clearer or undermine precision aiming?
