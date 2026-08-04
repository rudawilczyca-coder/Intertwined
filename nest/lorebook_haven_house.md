# Haven House — SillyTavern Lorebook

Machine-readable import: `lorebook_haven_house.json`  
Builder: `build_haven_house_lorebook.py`  
Long-form source: `../locations/haven-house-room-dressup-draft.md`

This is a separate durable World Info book intended to run beside the main Intertwined lorebook. Edit the builder, then run it; do not hand-edit the generated JSON.

## Retrieval design

- **House skeleton:** keyed by `Haven House`, `145 Berkeley Place`, or `Berkeley Place`; sticky for four messages so the vertical map survives ordinary movement prose.
- **Floor topology:** five compact navigation entries. These define room order, doors, stairs and sightlines.
- **Room detail:** keyed by room names plus a small set of distinctive objects or aliases likely to occur naturally in prose.
- **No constant entry:** Haven House context stays out of Ruby/Soho and other scenes.
- **No recursive scanning:** injected room prose cannot trigger neighbouring rooms and accidentally load half the building.
- **Room entries are additive:** mentioning `living room` and `deck` may intentionally load both when a scene crosses the doors.

## Entry map

| IDs | Scope |
|---|---|
| 00 | Whole-house vertical topology and UV/acoustic rules |
| 01–03 | Cellar topology, gym, Theo's safe room |
| 04–06 | Garden floor, shared office, herbary/potions |
| 07–11 | Parlour floor, dining, kitchen, living room, deck/garden |
| 12–15 | Third floor, Jackie's bedroom/bathroom, library/music room |
| 16–20 | Fourth floor, Draco bedroom/office, Theo bedroom, shared bathroom |

## Installation

Import `lorebook_haven_house.json` through SillyTavern's World Info panel, then enable it alongside the main Intertwined and current-arc books. Test with short prompts that name Haven House and one room, then movement between adjacent rooms.

