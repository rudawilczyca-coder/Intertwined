#!/usr/bin/env python3
"""Build the Intertwined SillyTavern World Info JSON from compact entry specs.

Scope: WORLD CONTENT ONLY — characters, events, places, vampire/werewolf
mechanics. Behavioural rules (the Jackie Rule, Statute cover, banned prose,
the who-knows-what matrix) live in the NARRATOR CARD / system prompt, NOT here.

Why a builder: hand-writing entries of dialogue-laden JSON is how you get a
malformed file that won't import. This fills every ST schema default so each
entry only declares its deltas, then dumps guaranteed-valid JSON.

Schema verified against SillyTavern/public/scripts/world-info.js (release).
Tiering pattern: a FULL entry (groupOverride=true, high groupWeight, a cooldown)
and a LITE entry share keys + an inclusion group. Full wins while eligible; when
it fires it goes on cooldown for N turns, during which only LITE can fire. After
the cooldown, FULL refreshes. Cooldowns: characters/people 5-6, events 8.
"""
import json

entries = {}
_uid = 0


def entry(keys, content, comment, **over):
    """Append one entry, applying ST defaults; `over` sets deltas."""
    global _uid
    e = {
        "uid": _uid,
        "key": keys,
        "keysecondary": [],
        "comment": comment,
        "content": content,
        "constant": False,
        "vectorized": False,
        "selective": False,
        "selectiveLogic": 0,          # 0 = AND ANY
        "addMemo": True,
        "order": 100,
        "position": 4,                # 4 = @ depth
        "disable": False,
        "excludeRecursion": False,
        "preventRecursion": True,     # tranche 1: recursion fenced off
        "delayUntilRecursion": False,
        "probability": 100,
        "useProbability": True,
        "depth": 4,
        "group": "",
        "groupOverride": False,
        "groupWeight": 100,
        "scanDepth": None,            # inherit global
        "caseSensitive": False,
        "matchWholeWords": True,      # avoid substring false-positives (Theo/theory)
        "useGroupScoring": False,
        "automationId": "",
        "role": 0,                    # 0 = system (for @depth injects)
        "sticky": 0,
        "cooldown": 0,
        "delay": 0,
        "displayIndex": _uid,
    }
    e.update(over)
    entries[str(_uid)] = e
    _uid += 1


# ── 00/01 · DRACO (tiered pair, group=draco, cooldown 5) ───────────────────
entry(
    ["Draco", "Malfoy"], comment="00 · Draco — FULL",
    group="draco", groupOverride=True, groupWeight=100, cooldown=5, order=110,
    content=(
        "[DRACO MALFOY — 22, wizard. Measured, aristocratic cadence; thinks before he speaks; "
        "reaches for full words over contractions when deliberate. Under stress he goes COLDER "
        "and more formal — never louder. Tells: twists his signet ring when processing; ears "
        "flush pink-to-red when flustered; his eloquence shatters when truly rattled or aroused. "
        "Sarcasm is a shield, not a default. Carries a war, a trial, his father's sentencing "
        "behind a composed, unreadable face he hates wearing. With Ruby he unravels — tender, "
        "undone; \"good boy\" lands on him like a struck bell, Pavlovian. He healed Jackie's Malice "
        "bite. He loves both Jackie and Ruby; he has said \"yours\" to each — only he knows that. "
        "He holds two of Ruby's unspoken \"purple tabs.\"]"
    ),
)
entry(
    ["Draco", "Malfoy"], comment="01 · Draco — LITE",
    group="draco", groupWeight=10, order=109,
    content=(
        "[Draco, 22, wizard. Aristocratic, measured; colder and more formal under stress, never "
        "louder; twists his ring; ears go red; undone by Ruby (\"good boy\" is nuclear).]"
    ),
)

# ── 02/03 · THEO (tiered pair, group=theo, cooldown 5) ─────────────────────
entry(
    ["Theo", "Theodore", "Nott"], comment="02 · Theo — FULL",
    group="theo", groupOverride=True, groupWeight=100, cooldown=5, order=110,
    content=(
        "[THEODORE NOTT — 21, vampire (turned Aug 2001). Blunt, no hedging; short, punchy "
        "sentences; dry, warm humour. He curses MORE when aroused and goes SILENT when truly "
        "angry. Fidgets a lighter — his tell. Platinum wedding band. Smells of cedar, smoke, "
        "leather. Cannot eat (cover: \"ill since a boy\"). Sunlight: he needs Jackie's Heliophobus "
        "charm to bear daylight. With Draco he is warmer — names feelings, cuts Draco's spirals "
        "with one weighted line. Married to Jackie; hers is the one heartbeat that matters to the "
        "thing in him. He knows Jackie envies Ruby. He houses the Malice.]"
    ),
)
entry(
    ["Theo", "Theodore", "Nott"], comment="03 · Theo — LITE",
    group="theo", groupWeight=10, order=109,
    content=(
        "[Theo, 21, vampire. Blunt, dry, warm; curses when aroused, goes silent when angry; "
        "fidgets a lighter; can't eat (cover story); needs a charm for sun. Warmer with Draco.]"
    ),
)

# ── 04 · THE MALICE (single; cooldown 5) ───────────────────────────────────
entry(
    ["Malice"], comment="04 · The Malice",
    cooldown=5, order=110,
    content=(
        "[THE MALICE — Theo's split-off hunt/hunger; a second voice (He/Him, rendered in italics). "
        "Volume scales with hunger: fed = quiet, starving = loud. Speaks in 1-3 short sentences, "
        "conversational menace. Calls Jackie \"Little Wolf,\" Draco \"pretty one.\" Obeys safewords "
        "instantly: Pax (slow), Finite (full stop). Functionally heterosexual; no intimacy with "
        "Draco. Named by Jackie, April 2001. Buried whisper to Jackie that Theo does NOT know: "
        "\"Next time I won't be angry. And he can't fight this when it's love.\"]"
    ),
)

# ── 05 · JACKIE (character; exterior only — narrator never writes her) ─────
entry(
    ["Jackie"], comment="05 · Jackie Nott",
    cooldown=6, order=110,
    content=(
        "[JACKIE NOTT — 5'4\", red wavy hair, heterochromatic eyes (left moss-green, right "
        "glacial-blue), pale, freckled, athletic-curvy. Auror; snow-leopard Animagus; an Italian "
        "gold-flame wrist holster holds her wand. Bite scar on her left neck (Draco healed it). "
        "Married to Theo; the heartbeat the Malice answers to. With a stranger like Ruby she runs "
        "cool-curious and gives space rather than overwhelming. (The user writes Jackie — the "
        "narrator renders her exterior only.)]"
    ),
)

# ── 06 · RUBY WILLIAMS (character; exterior only) ──────────────────────────
entry(
    ["Ruby Williams", "Ruby"], comment="06 · Ruby Williams",
    cooldown=6, order=110,
    content=(
        "[RUBY WILLIAMS — 21, Welsh (Swansea), works in cybersecurity, Soho flat. Auburn-red hair "
        "(often dyed darker), round glasses (pushes them up with her wrist), 5'2\", curvy, pale, "
        "freckled. Tells for Theo/Draco to clock: breath in counted fours when triggered; the "
        "fake smile vs. the real one (the real one pulls higher on the left); she retracts her "
        "own requests; she turns her phone face-down. Stomach scars from Robbie — always covered; "
        "high-waisted everything. Dog: Vex (Doberman, protection-trained). Drink: Dr Pepper. (The "
        "user writes Ruby's interiority — the narrator gives exterior only.)]"
    ),
)

# ── 07 · ROBBIE (character; text voice — narrator writes his texts, no POV) ─
entry(
    ["Robbie", "Kowalski"], comment="07 · Robbie Kowalski",
    cooldown=6, order=110,
    content=(
        "[ROBERT \"ROBBIE\" KOWALSKI — Ruby's abusive ex. Swansea, 27, criminal (cigarette "
        "smuggling, dealing on the side). The narrator writes his TEXTS only; he never gets POV. "
        "Register: lowercase, sparse punctuation, no emoji, engineered-casual — passes a "
        "stranger's sniff test. Guilt mechanics: \"you owe me that much,\" \"just five minutes,\" "
        "\"i'm not asking for anything\" (he is). \"The work\": vague, unverifiable self-improvement. "
        "The rewrite: \"what happened / that night / the accident\" — he never names the abuse; if "
        "pressed he pivots to his own pain. Nicknames: Princess, Little Red; Kochanie only when "
        "apologising. His menace lives in frequency, knowledge, and closing distance — NEVER a "
        "stated threat. Never a cartoon: he believes every word and casts himself as the romantic "
        "lead. He has actually changed nothing.]"
    ),
)

# ── 08/09 · WALES WEEKEND (tiered event pair, group=ev_wales, cooldown 8) ──
entry(
    ["Wales", "Morriston"], comment="08 · Wales weekend — FULL",
    group="ev_wales", groupOverride=True, groupWeight=100, cooldown=8, order=110,
    content=(
        "[WALES WEEKEND (Sat-Sun, 29-30 June 2002) — Draco met Ruby's family in Swansea. Surface "
        "success — a \"false peace.\" Load-bearing residue: outside the shop in Morriston, Crissy "
        "saw Ruby and Draco embrace on the grass (Ruby had fled Crissy, then fell apart in Draco's "
        "arms). Ruby does NOT know she was seen — assume Crissy reported it to Robbie. Gareth "
        "overheard Draco and Ruby in the sealed annex (never to be spoken of). A possible real "
        "wizarding grimoire sits in the Williams maternal-line attic; Draco couldn't ask about it.]"
    ),
)
entry(
    ["Wales", "Morriston"], comment="09 · Wales weekend — LITE",
    group="ev_wales", groupWeight=10, order=109,
    content=(
        "[Wales, Jun 29-30: Draco met Ruby's family; \"false peace.\" Crissy saw the grass embrace "
        "(and told Robbie); the sealed-annex overhear; the attic grimoire.]"
    ),
)

# ── 10 · THE WILLIAMS FAMILY (cast reference; cooldown 6) ──────────────────
entry(
    ["Gemma", "Gareth", "Callum", "Mike", "Alex"], comment="10 · The Williams family",
    cooldown=6, order=105,
    content=(
        "[THE WILLIAMS FAMILY (Swansea). Gemma (mum, late 40s): warm, hyper-perceptive, feeds "
        "everyone, knows everything Robbie did. Gareth (dad, 50s): quiet, steady; secretly "
        "researched Robbie; assesses Draco by honesty and by how he treats Ruby. Mike (adopted "
        "brother, 23): depressed, deadpan-lewd wit, a silent protective stare. Callum (brother, "
        "20): loud, performative, class-warfare banter, a secret Germany ticket. Alex (brother, "
        "15): undiagnosed-autistic, a WWII/SOE notebook, monosyllabic until a topic trips the "
        "wire; clocks Draco's hypervigilance. Clary (estranged sister): left for Germany with "
        "Hannah — \"the door rusts shut,\" not discussed. Crissy: a mutual acquaintance who saw the "
        "Morriston embrace and reported it to Robbie.]"
    ),
)

book = {"entries": entries}
with open("/home/user/Intertwined/nest/lorebook_intertwined.json", "w") as f:
    json.dump(book, f, indent=2, ensure_ascii=False)

print(f"Wrote {len(entries)} entries.")
print("Tiered pairs:", sorted({e["group"] for e in entries.values() if e["group"]}))
