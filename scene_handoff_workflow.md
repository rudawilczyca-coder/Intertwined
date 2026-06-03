# Scene Handoff Workflow: Claude ↔ SillyTavern

*The "Fade to Black and Back" system for seamless cross-platform continuity.*

---

## Overview

Sometimes a scene needs to go somewhere Claude can't comfortably take it. This workflow lets you pause here, play the scene in SillyTavern, and return with continuity intact.

The flow:

```
Claude (building tension) 
    → HANDOFF (Sable generates bridge)
        → SillyTavern (explicit scene plays out)
    → RETURN (Ruby brings back summary)
→ Claude (continues from aftermath)
```

---

## STEP 1: Signal the Handoff

When you feel a scene heading toward "SillyTavern territory," drop this in chat:

```
[[OOC: ~fade to ST]]
```

Optionally, add context about what you want the scene to focus on:

```
[[OOC: ~fade to ST — Malice chase scene, I want Him unfiltered. 
Focus on: the hunt dynamic, the power exchange, feeding.]]
```

```
[[OOC: ~fade to ST — Draco and Jackie, first time initiating without Theo present. 
Focus on: Draco leading for once, the vulnerability of it.]]
```

---

## STEP 2: Sable Generates the Handoff Package

When you trigger `~fade to ST`, Sable will produce a **Handoff Package** with three parts:

### Part A — Scene Context Block
A short paragraph you paste into SillyTavern's Author's Note or as your first message. It tells the bot where the characters are emotionally and physically.

Example:
```
[Scene Context: Haven House cellar gym, approximately 11 PM. Theo's eyes 
have been cycling violet for the last twenty minutes. Jackie just told him 
she doesn't want Pax tonight. The Malice is surfacing — not sudden, but 
like a tide coming in. Draco is upstairs and knows what's happening. 
The door is warded. Jackie is armed but hasn't drawn. Emotional state: 
Jackie is deliberate and calm. Theo is losing ground. The Malice is patient.]
```

### Part B — Opening Message
A first message written in the same voice as your SillyTavern card, picking up exactly where we left off. You paste this as the bot's first reply to start the scene.

### Part C — Continuity Anchors
A short bullet list of things that MUST be preserved during the scene for canon consistency. Things like:
- Safewords are Pax and Finite — if used, they work
- Theo's eyes go crimson when the Malice is fully present
- Specific injuries or physical states to maintain
- Emotional beats that need to land for the aftermath to work here

---

## STEP 3: Play the Scene in SillyTavern

Take the handoff package, paste the context, and go. Play as long as you want. Let the Malice loose. Let Draco fall apart. Whatever the scene needs.

**While you play, keep a mental note of:**
- What emotionally shifted (who said what that mattered)
- Any physical consequences (injuries, exhaustion, marks)
- Key dialogue that should be canon (a line that changes something)
- How the scene ended (who fell asleep first, who left the room, what the last thing said was)

---

## STEP 4: Write the Return Summary

When you're done in SillyTavern, come back here and drop a return summary. It doesn't need to be long or polished — bullet points are fine. Sable will work with whatever you give.

Use this trigger:

```
[[OOC: ~back from ST]]
```

Then include your summary. It can be as short or as detailed as you want:

### Minimal version:
```
[[OOC: ~back from ST

The Malice got His chase. Jackie used Finite near the end. 
Theo came back with full memory. She has bite marks on her 
neck and shoulder. They're on the cellar floor and she's 
half-asleep. He's running his fingers through her hair and 
hasn't spoken since he came back to himself.]]
```

### Detailed version:
```
[[OOC: ~back from ST

Scene ran about 2 hours of play. Key beats:
- The Malice surfaced slowly, not a snap — He talked first, 
  almost conversational
- Chase through the cellar gym — He let her get close before 
  pulling away, toying
- Feeding during — Jackie offered her wrist, He took her throat instead
- She used Finite when the venom loop got too intense — He 
  obeyed immediately, no resistance
- After: Theo surfaced with full memory (no blackout)
- He said: "You didn't have to run." She said: "Yes I did."
- Physical state: bite marks neck + shoulder, bruising on her 
  hips from being pinned, both on the cellar floor
- Emotional state: tender, raw, exhausted. The violence 
  converted to quiet.
- Canon line I want to keep: The Malice whispered "You make Me 
  want to be gentle" and it scared both of them.]]
```

---

## STEP 5: Sable Writes the Bridge

From your summary, Sable will write a **PG-13 bridge passage** — a "fade to black and back" that:

- Captures the emotional arc without explicit detail
- Anchors the physical consequences (injuries, exhaustion, marks)
- Preserves any canon-significant dialogue
- Transitions smoothly into the next scene here

Example of what the bridge might look like in our prose:

> *The cellar held the aftermath like a confession.*
>
> *Theo's fingers moved through her hair with the slow, absent rhythm of a man relearning his own hands. His eyes were pale blue again — washed clean, or close to it. The bite marks on her throat had already begun to bruise, twin crescents disappearing beneath the collar of the shirt she hadn't been wearing an hour ago.*
>
> *He hadn't spoken since he'd come back to himself. The Malice had retreated — not banished, not caged, but sated in a way that left the basement air feeling almost gentle.*
>
> *"You didn't have to run," he said finally.*
>
> *The silence that followed held her answer before she gave it.*

Then we pick up and keep going from there.

---

## Quick Reference

| Trigger | What Happens |
|---|---|
| `[[OOC: ~fade to ST]]` | Sable generates handoff package (context + opening message + continuity anchors) |
| `[[OOC: ~fade to ST — {details}]]` | Same, but focused on what you specify |
| `[[OOC: ~back from ST]]` + summary | Sable writes PG-13 bridge passage and we continue |

---

## Tips

- **You don't need to copy the whole SillyTavern chat.** Just the emotional beats and consequences. Sable doesn't need to read every line — she needs to know what CHANGED.
- **Canon lines matter.** If a character said something during the scene that shifts the relationship, include it. Those are the bones the bridge is built on.
- **Physical state matters.** Bite marks, bruises, exhaustion, who's dressed and who isn't — these details anchor the return scene in reality.
- **You can do this mid-scene.** If a scene starts here and only PART of it needs SillyTavern, that's fine. Fade out at the moment it needs to go explicit, play that portion there, come back for the aftermath.

---

*Built by Sable, May 2026. The raven holds the thread while you cross between rooms. 🖤*
