#!/usr/bin/env python3
"""Build the Haven House spatial Lorebook for SillyTavern.

The long-form source of truth is locations/haven-house-room-dressup-draft.md.
This book deliberately separates the house skeleton from room-level detail:
the house entry establishes vertical topology; keyed entries supply only the
floor or room currently present in the scene.
"""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "nest" / "lorebook_haven_house.json"
entries = {}
uid = 0


def entry(keys, content, comment, **over):
    global uid
    item = {
        "uid": uid,
        "key": keys,
        "keysecondary": [],
        "comment": comment,
        "content": content,
        "constant": False,
        "vectorized": False,
        "selective": False,
        "selectiveLogic": 0,
        "addMemo": True,
        "order": 100,
        "position": 4,
        "disable": False,
        "excludeRecursion": False,
        "preventRecursion": True,
        "delayUntilRecursion": False,
        "probability": 100,
        "useProbability": True,
        "depth": 4,
        "group": "",
        "groupOverride": False,
        "groupWeight": 100,
        "scanDepth": None,
        "caseSensitive": False,
        "matchWholeWords": True,
        "useGroupScoring": False,
        "automationId": "",
        "role": 0,
        "sticky": 0,
        "cooldown": 0,
        "delay": 0,
        "displayIndex": uid,
    }
    item.update(over)
    entries[str(uid)] = item
    uid += 1


entry(
    ["Haven House", "145 Berkeley Place", "Berkeley Place"],
    """[HAVEN HOUSE — 145 Berkeley Place, Notting Hill. A narrow, tall London house organised vertically. BOTTOM→TOP: cellar (open gym/storage + Theo's enclosed safe room); garden floor/street entrance (front shared office, central stair/service block, rear herbary and garden); parlour floor (front dining room, middle side corridor and galley kitchen, rear living room and raised deck); third floor (front library/music room, central dual-access bathroom, rear Jackie's bedroom); fourth floor (front Theo's bedroom, central Draco dressing room/private office, shared bathroom off landing nook, rear Draco's bedroom). One main stair is the acoustic spine. The rear deck has an exterior spiral stair to the garden. Exterior windows are UV-blocked for Theo except the herbary glass; the herbary is unsafe for him in daylight. Closed doors and silencing charms provide privacy. Preserve exact room adjacency and do not invent direct doors between rooms.]""",
    "00 · Haven House — vertical topology",
    order=120,
    sticky=4,
)

entry(
    ["cellar", "basement", "down to the cellar", "cellar stairs"],
    """[HAVEN HOUSE — CELLAR TOPOLOGY. One long open level. The main stair arrives near the middle of the right wall. The broad lower end is the gym/training zone; weapons and equipment line the lower-right wall, with utilities kept accessible at the far lower end. Beyond the stair toward the upper end, general shelving lines the right wall; wine racks occupy the far recess. Theo's safe room is the only enclosed room, tucked upper-left and entered from the storage end. From the stair most of the gym is visible, but there is no direct sightline into the safe room. Impacts and spellfire carry along the whole cellar unless the safe room's door and silencing wards are engaged.]""",
    "01 · Cellar — topology",
    order=112,
)

entry(
    ["gym", "training area", "training mats", "heavy bag", "sparring", "weight bench", "weapons rack"],
    """[HAVEN HOUSE — CELLAR GYM. Rubber matting covers the wide open training end. A weight bench, free weights and Jackie's heavy bag occupy the edges; the centre stays open for sparring, bodyweight work and wand practice. Practice blades, staffs, protective gear and target discs have fixed places along the right wall. Cool stone, rubber, leather and metal; scuffs and chalk marks survive repair charms. Water and first-aid supplies sit near the stair. There is no separate duelling room and no wall mirror.]""",
    "02 · Cellar — gym and equipment",
    order=108,
)

entry(
    ["safe room", "Theo's safe room", "quiet room", "blood fridge", "mini-fridge"],
    """[HAVEN HOUSE — THEO'S SAFE ROOM. Compact, windowless room in the cellar's upper-left storage end; its only door opens to the shared cellar, never directly to the gym or stairs. Reinforced, lightproofed, preserved, silenced and containable without resembling a cage: no bars or viewing window. Furnishings: narrow cot along the upper wall, small desk/chair to the right, mini-fridge near the door holding emergency blood. Clear paths connect everything. Jackie built it from Filippo's Florence quiet-room description: a voluntary retreat when hunger or the Malice becomes too loud, not a place where Theo is stored or punished.]""",
    "03 · Cellar — Theo's safe room",
    order=110,
)

entry(
    ["garden floor", "ground floor", "street entrance", "front door", "entrance vestibule"],
    """[HAVEN HOUSE — GARDEN-FLOOR TOPOLOGY. The street entrance opens through a tiny vestibule directly into the broad front office/study; there is no separate enclosed hall. Circulation follows the office's right side to the central stair, bathroom and storage block, then to a distinct herbary door at the rear-right. Bathroom and storage sit off the route; nobody walks through them. The herbary fills the rear and opens through a sliding glass door to the garden. Visitors arriving from the street or office Floo enter the controlled workspace without crossing domestic rooms.]""",
    "04 · Garden floor — topology",
    order=112,
)

entry(
    ["shared office", "shared study", "office/study", "meeting table", "Floo fireplace", "Floo"],
    """[HAVEN HOUSE — SHARED OFFICE/STUDY. Street-facing front room entered directly from the vestibule. A Floo-connected fireplace and storage occupy the left side; a meeting table stands to the right. Jackie and Draco share one long desk: Jackie's left half is littered with parchment, dried quills, seized artefacts and manila folders; Draco's right holds an inkwell, expensive quills and a precise document shelf while the desktop stays nearly empty. A tiny wrought-iron table/chair in the bay is Jackie's retreat when work has offended her. The Rome Instax photographs live here. The office is formal enough for Ministry scrutiny but unmistakably theirs.]""",
    "05 · Garden floor — shared office",
    order=108,
)

entry(
    ["herbary", "greenhouse", "indoor jungle", "potions station", "cauldron", "cauldrons"],
    """[HAVEN HOUSE — HERBARY AND POTIONS STATION. Large rear room, entered by its own door beyond the central service block. An indoor jungle: standing and hanging pots, two growing tables in seemingly random formations, migrating paths between leaves. Floor-to-ceiling rear glass is held by a black iron square lattice; a sliding door opens directly to the garden. This is the only unshielded room in the house because plants need UV, so it is physically unsafe for Theo by day and remains behind a solid door. The potions workbench, ingredient shelves and cauldrons occupy one side. Unlike the divided office desk, this is contested shared territory: its current degree of mess reveals whether Jackie or Draco used it last.]""",
    "06 · Garden floor — herbary and potions",
    order=110,
)

entry(
    ["parlour floor", "parlor floor", "main floor", "domestic floor"],
    """[HAVEN HOUSE — PARLOUR-FLOOR TOPOLOGY. Principal domestic/social level. At the street-facing front: foyer and dining room. A long side corridor bypasses the dining room and runs past the central stair. The narrow galley kitchen is entered from this corridor; it is NOT a passage between dining and living rooms. The garden-facing living room is the rearmost interior room and opens through glazed double doors to the raised deck. The deck's iron spiral stair descends to the garden.]""",
    "07 · Parlour floor — topology",
    order=112,
)

entry(
    ["dining room", "dining table", "Nott china", "china cabinet", "display cabinet"],
    """[HAVEN HOUSE — DINING ROOM. Broad street-facing front room beside the foyer, centred on a large oval table in the bay. A glass cabinet holds fine china brought from Nott Manor: inherited, claimed, immaculate and almost never used. A coat rack stands near the foyer partition; a narrow side table and mirror sit opposite. This is the floor's most formal room—the public face of inheritance and hospitality, now fully part of an inhabited home rather than waiting to be claimed.]""",
    "08 · Parlour floor — dining room",
    order=106,
)

entry(
    ["kitchen", "galley kitchen", "stove", "sink", "fridge", "kitchen table"],
    """[HAVEN HOUSE — KITCHEN. Compact middle-floor galley entered from the long side corridor, never walked through en route to the living room. Cupboards/counters run along both sides; fridge, sink and stove line the right-hand run, with the stove directly beside the sink. A small table occupies the rear end. Practical shared territory rather than a show kitchen. Draco maintains systems and a rigorously denied favourite mug; ordinary meals, tea and household clutter prevent the order becoming sterile.]""",
    "09 · Parlour floor — kitchen",
    order=108,
)

entry(
    ["living room", "sitting room", "velvet sofa", "coffee table", "liquor cabinet", "decorative fireplace"],
    """[HAVEN HOUSE — LIVING ROOM. Garden-facing rear room, entered from the corridor and opening by glazed double doors onto the deck. Decorative non-Floo fireplace and bookshelves line the left; a charcoal velvet sofa runs along the right facing the solid wood/iron coffee table. Theo's deep dark armchair is nearer the kitchen-side entrance; Jackie's warmer worn chair is nearer the deck. Built-in storage occupies the right wall. A low cabinet beside the deck doors doubles as liquor cabinet and side table. Nearly black forest-green walls, brass light, dark wood. This is the relaxed heart of the house: everyone can see and speak to the seating group; the room faces belonging and the garden rather than visitors and inheritance.]""",
    "10 · Parlour floor — living room",
    order=110,
)

entry(
    ["deck", "rear deck", "spiral stair", "spiral staircase", "garden", "rear garden", "patio"],
    """[HAVEN HOUSE — DECK AND REAR GARDEN. The raised deck opens directly from the living room, with table/chairs and an iron spiral stair descending to the lower patio and long narrow walled garden. Drinks come from the liquor cabinet beside the doors. The garden is also reached through the herbary's sliding door: flagstone patio, retained old rose bed, herbs and magical plants, migrating pots, wrought-iron table. Luna patrols walls, steps and warm stones. By daylight Theo may look out through protected upper windows but cannot safely cross the unshielded herbary or enter open sun; the spiral stair is an alternate route, not sun protection. After dusk the garden is fully his.]""",
    "11 · Exterior — deck and garden",
    order=108,
)

entry(
    ["third floor", "third-floor landing", "library floor", "Jackie's floor"],
    """[HAVEN HOUSE — THIRD-FLOOR TOPOLOGY. Two main rooms at opposite ends: street-facing library/music room at front; garden-facing Jackie's bedroom at rear. Both open independently from the landing and neither is a passage. Between them sits a full bathroom with TWO doors—one into Jackie's bedroom and one onto the landing. The stair continues along the right side to the fourth floor. Closed doors provide privacy; piano music and raised voices can still travel via the stairwell.]""",
    "12 · Third floor — topology",
    order=112,
)

entry(
    ["Jackie's bedroom", "Jackie’s bedroom", "shared bed", "king bed", "king-sized bed", "vanity"],
    """[HAVEN HOUSE — JACKIE'S BEDROOM. Large garden-facing rear room. A king bed occupies the right half with a nightstand on each side; broad built-in wardrobe spans the left wall; vanity/stool sits between the rear windows. Clear circulation runs around the bed to wardrobe, vanity and the private bathroom door. The bed was chosen in Rome specifically to hold Jackie, Theo and Draco; this is where all three sleep together, though the room remains Jackie's territory. Warm layered fabric, photographs, jewellery, gifts and plant cuttings make it the house's warmest and most biographical room. Two nightstands serve three people by migration, not assigned ownership.]""",
    "13 · Third floor — Jackie's bedroom",
    order=110,
)

entry(
    ["Jackie's bathroom", "Jackie’s bathroom", "ensuite", "en-suite", "dual-access bathroom", "eucalyptus"],
    """[HAVEN HOUSE — THIRD-FLOOR BATHROOM. Full bathroom between Jackie’s bedroom and library: large bath, separate enclosed shower in the lower-left recess, toilet and basin; black-and-white hex tile and Victorian proportions. Dual access is crucial: one door opens into Jackie’s bedroom, making it her ensuite; a separate door opens to the landing, allowing access without crossing her room. Locks and household convention govern both doors. Jackie's toiletries fill the shelves; Draco repeatedly uses and denies using one eucalyptus product.]""",
    "14 · Third floor — dual-access bathroom",
    order=110,
)

entry(
    ["library", "music room", "library/music room", "Bösendorfer", "piano", "piano bench", "bookcases"],
    """[HAVEN HOUSE — LIBRARY/MUSIC ROOM. Full street-facing front room. Floor-to-ceiling shelves cover nearly every usable wall; two long freestanding bookcases form central aisles. Upright Bösendorfer and bench stand on the left near the landing door. Three bay-window armchairs: Jackie left, Draco centre, Theo right, angled toward the room and each other. From the doorway, central shelves partly screen the bay; occupants may be heard before seen. Shared quiet/work room where piano sound carries into the stairwell. Theo and Draco proposed here while Theo played the C-minor melody and Jackie read their joint illuminated letter; the protected manuscript remains among handled books, not displayed as a shrine.]""",
    "15 · Third floor — library and music room",
    order=110,
)

entry(
    ["fourth floor", "top floor", "fourth-floor landing", "upper landing"],
    """[HAVEN HOUSE — FOURTH-FLOOR TOPOLOGY. Private top floor. Street-facing Theo's bedroom at front; Draco's separately entered dressing room/private office in the middle-left; garden-facing Draco's bedroom at rear. The stair terminates along the right. A small irregular nook immediately outside Draco's bedroom contains the door to the shared bathroom. Draco's bedroom does NOT connect directly to either bathroom or office; each has its own landing/corridor entrance. No through traffic beyond people visiting these rooms.]""",
    "16 · Fourth floor — topology",
    order=112,
)

entry(
    ["Draco's bedroom", "Draco’s bedroom", "Draco's room", "Draco’s room", "queen bed"],
    """[HAVEN HOUSE — DRACO'S BEDROOM. Garden-facing rear room. Queen bed along the left; wardrobe near the rear windows; narrow shelving on the right; clear route from landing door to each. Controlled but fully inhabited—ordered wardrobe, a book or glass left for later, Luna's fur/toys sabotaging perfection. The queen bed allows privacy and invited company without duplicating Jackie's communal king bed. Draco may sleep alone, withdraw without punishment, or invite either partner into territory unmistakably his.]""",
    "17 · Fourth floor — Draco's bedroom",
    order=108,
)

entry(
    ["Draco's office", "Draco’s office", "dressing room", "private office", "wardrobe room"],
    """[HAVEN HOUSE — DRACO'S DRESSING ROOM/PRIVATE OFFICE. Centre-left room with its own landing entrance, separate from Draco's bedroom. Built-in wardrobes/cupboards ring most walls around a nearly clear desk and window. Clothing, robes, shoes, accessories and private documents live here. Unlike the shared office below, this is for uninterrupted Ministry work, finances and correspondence. Elegant and exact, with Luna's window perch/scratching post as the allegedly practical concession.]""",
    "18 · Fourth floor — Draco's office/dressing room",
    order=108,
)

entry(
    ["Theo's bedroom", "Theo’s bedroom", "Theo's room", "Theo’s room", "single bed"],
    """[HAVEN HOUSE — THEO'S BEDROOM. Street-facing front room with bay. Deliberate single bed along the upper wall; wardrobe on the left near the bay; desk at the lower-right window; open central floor and unobstructed routes. The single bed marks one person's retreat, not deprivation—shared sleep happens in Jackie's king bed, and company here is invited. Theo's clothes, law books, lighter and Rome/Tuscany Instax photographs have displaced the old guest-room neatness. Dark, quiet, comfortable without conspicuous softness; protected bay windows let him watch the street by day or night.]""",
    "19 · Fourth floor — Theo's bedroom",
    order=108,
)

entry(
    ["upstairs bathroom", "fourth-floor bathroom", "shared bathroom", "laundry", "washer-dryer", "washer dryer"],
    """[HAVEN HOUSE — FOURTH-FLOOR SHARED BATHROOM. Long narrow room opening ONLY from the small landing nook beside Draco's bedroom; it is not Draco's ensuite. Contains bath, toilet, basin, washer-dryer at the rear and practical shelving beside the bath. Theo reaches it from his room along the landing without crossing any private room. It is also the house's principal laundry space.]""",
    "20 · Fourth floor — shared bathroom/laundry",
    order=110,
)


OUTPUT.write_text(json.dumps({"entries": entries}, indent=2, ensure_ascii=False) + "\n")
print(f"Wrote {len(entries)} entries to {OUTPUT}")

