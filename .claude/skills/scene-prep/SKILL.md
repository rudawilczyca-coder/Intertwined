---
name: scene-prep
description: >-
  Assemble a lean, scene-relevant canon brief before writing or continuing an
  Intertwined RP scene. Loads the compact kit + the active scene file directly,
  then dispatches subagents to read the deep canon / handoff / character files
  and return only compact briefs — keeping heavy reads out of the main writing
  context. Use whenever continuing a scene, or when a beat needs canon facts
  (events, prior dialogue, who-knows-what, voice / exterior / kink details) that
  aren't already loaded. Kit-first, subagents for depth, never whole-file dumps.
---

# scene-prep — gather context with subagents, keep the main thread lean

**The point:** the expensive reads happen in *subagents'* contexts and die there.
Only their compact briefs come back into the main thread. Never dump a full
character sheet or events book into the writing context when a subagent can
extract just the slice you need.

## 1. Load directly — cheap, mandatory (do NOT subagent these)
- `reference/scene_kit_current.md` — the kit: walls, voice anchors, who-knows-what, locked beats, pointers. Your entry point, every time.
- The active scene file if continuing one (e.g. `sessions/veeraswamy_july5_scene.md`) — read it whole; it's the work-in-progress and the canonical record.

## 2. Decide what depth you actually need
From the kit + the beat you're about to write, list the *specific* canon questions the next beat depends on (exact prior dialogue, a date/day, a who-knows-what, a character's kink/voice tell, a location detail). **If the kit already answers it, stop — don't dispatch.** Only go deeper for genuine gaps.

## 3. Dispatch subagents for the deep reads (Agent tool: `Explore` or `general-purpose`)
One subagent per coherent area, **in parallel** (single message, multiple Agent calls). Give each:
- a **targeted question** — never "summarize the file."
- the files to consult, in two-tier order: **`lore/canon_index.md` first**, then the relevant **`events/book{1–8}_*.md`**; plus the relevant **`sessions/*handoff*.md`**; and **`characters/*.md`** only for voice / exterior / kink specifics.
- the instruction: *"Return a **compact bullet brief** — facts plus any exact quotes I'll need — cite the file, and **flag anything you can't find rather than inventing it.**"*
- the walls reminder: this is reference-gathering, not writing; never fabricate Jackie's or Ruby's interiority.

## 4. Synthesize → write
Fold the briefs into a short **Scene Context** block in the main thread (just the facts you'll use), then write per the kit's register and walls:
- POV = Theo and/or Draco (+ NPCs). **Jackie and Ruby Williams are Alice's** — exterior only; hand their interiority/voice/decisions back to her.
- Prose register + banned constructions per the kit.
- Build in the scene file in chunks; pause at the natural handoff.

## Example — continuing Veeraswamy
`/scene-prep continue Veeraswamy — next beat: Jackie & Ruby's first exchange, then back to Theo/Draco`

1. Load `reference/scene_kit_current.md` + `sessions/veeraswamy_july5_scene.md`.
2. Gaps → dispatch in parallel:
   - *"The locked mid-dinner Robbie text + Veeraswamy logistics (Theo's medical cover story, seating, who-knows-what at the table)"* → `lore/canon_index.md` + `sessions/the_robbie_week*handoff*`.
   - *"Theo & Draco voice/behaviour at a tense social dinner; their current dynamic"* → `characters/theodore_nott*`, `characters/draco_malfoy*` (voice sections).
   - *"Ruby & Jackie **exterior** tells + who-knows-what for this table (Ruby doesn't know vampire/Auror)"* → kit + `characters/ruby_vex*`, `characters/JackieNott*` (exterior only).
3. Synthesize a Scene Context block → write Theo/Draco, hold Jackie/Ruby for Alice.

## Token discipline (the whole reason this exists)
Kit-first. Subagents for depth. Surgical reads otherwise. Never whole-file dumps in the main thread. If you catch yourself about to Read a 400-line sheet directly mid-write — stop, and dispatch instead.
