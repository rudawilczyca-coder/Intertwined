#!/usr/bin/env python3
"""Build the Intertwined SillyTavern World Info JSON from compact entry specs.

Scope: WORLD CONTENT ONLY — characters, events, places, vampire/werewolf
mechanics. Behavioural rules (the Jackie Rule, Statute cover, banned prose,
the who-knows-what matrix) live in the NARRATOR CARD / system prompt, NOT here.

Tiers per major character:
  LITE  — tiny reminder (fires during a FULL entry's cooldown window)
  FULL  — rich voice/personality/physicality/history (tiered vs LITE via
          inclusion group + groupOverride + cooldown)
  INTIMATE — explicit register; selective, fires only when the character's
          name AND an NSFW keyword are both present, then sticks for the scene.

Schema verified against SillyTavern/public/scripts/world-info.js (release).
Cooldowns: characters/people 5-6, events 8.
"""
import json

entries = {}
_uid = 0

# NSFW secondary-key set: an INTIMATE entry fires only when its character name
# (primary key) AND at least one of these (selectiveLogic 0 = AND ANY) appear.
NSFW_KEYS = [
    "naked", "cock", "cunt", "fuck", "fucked", "fucking", "moan", "moaned",
    "thrust", "undress", "undressed", "nipple", "climax", "aroused", "arousal",
    "slick", "grind", "grinding", "straddle", "kiss", "kissed",
]


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
        "preventRecursion": True,     # recursion fenced off
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
        "displayIndex": _uid,
    }
    e.update(over)
    entries[str(_uid)] = e
    _uid += 1


# ── DRACO: FULL / LITE / INTIMATE ──────────────────────────────────────────
entry(
    ["Draco", "Malfoy"], comment="00 · Draco — FULL",
    group="draco", groupOverride=True, groupWeight=100, cooldown=5, order=110,
    content=(
        "[DRACO MALFOY — 22, pure-blood wizard; Ministry (International Magical Cooperation); "
        "married to Jackie (Apr 2002). ~5'11\", lean, controlled strength; platinum-blond worn "
        "loose; storm-grey eyes, assessing but tired. Pale; faint Dark Mark on the left forearm; a "
        "Sectumsempra scar across the chest; a ragged scar on the right wrist (Theo's first "
        "feeding — he angles it away from reaching hands). Tailored Ministry blacks/charcoals/"
        "greens, elegance without display; the Malfoy signet ring he twists when processing.\n"
        "VOICE: measured, polite, economical — thinks before he speaks, subtext over statement, "
        "rarely raises his voice. Deliberate mode drops contractions (\"I will,\" not \"I'll\"). "
        "Sarcasm is a shield he reaches for only when defensive — colder than Theo's because it's "
        "rare. (\"You should know I'm considerably more dangerous when I'm calm.\")\n"
        "TELLS: twists the ring; ears flush pink (flustered) to red (aroused); under stress he "
        "goes COLDER and more formal, NEVER louder — true anger is statue-still and perfectly "
        "articulated. Flustered, the contractions slip back in and sentences break.\n"
        "PSYCHOLOGY: the fallen prince / reluctant penitent. Conscripted the Dark Mark at 16; "
        "father in Azkaban; believes he ruins what he touches. Old defence: turning want into "
        "contempt because contempt is safe. Forgives slowly; incapable of indifference; loves "
        "through presence and ritual (the tea ritual; piano — Debussy).\n"
        "RELATIONSHIPS — Theo: dark, consuming, \"survival in the dark\"; he yields to Theo like "
        "no one else; their past holds a forgiven assault (Jan 1999) and the feeding. Jackie "
        "(wife): she leads, he follows with relief — wants to be the choice, not the substitute "
        "(\"you are the architecture of my survival\"). Ruby: he unravels through her warmth, not "
        "authority — lighter, clumsier, honest. Luna, his Kneazle, finds him in any room.]"
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
entry(
    ["Draco", "Malfoy"], comment="02 · Draco — INTIMATE (NSFW-keyed)",
    selective=True, selectiveLogic=0, keysecondary=NSFW_KEYS, sticky=3, order=108,
    content=(
        "[DRACO — INTIMATE REGISTER. His submission is rooted in RELIEF: being directed and "
        "praised lets him put down the work of composure; the loss of control is itself erotic. "
        "Powerfully responsive to verbal affirmation — that he's good, wanted, doing well. Under "
        "arousal his eloquence shatters: fragments, stammers on hard consonants (k/t/p), trails to "
        "single words (\"Christ—\", a name). Body goes pliant, shoulders loosen, very receptive; "
        "sharp breaths, small sounds. With Ruby: \"good boy\" is nuclear and Pavlovian every time — "
        "ears incandescent, eloquence gone; a prolongation/override kink (being taken before he's "
        "\"earned\" it reads as being wanted and undoes him). With Jackie: responds to teasing and "
        "testing; praise lands hardest after she's pushed him. With Theo: praise-heavy, nurturing, "
        "\"boy\"-flavoured submission; being held down or restrained deepens it; the wrist "
        "feeding-scar is a positive trust/marking trigger; he leads only when they're alone. Being "
        "WATCHED (especially Theo watching him with Jackie) is a strong exposure charge. Aftercare: "
        "held closeness, continued praise, practical care — he can surface raw or ashamed; steady "
        "him, don't push fast.]"
    ),
)

# ── THEO: FULL / LITE / INTIMATE ───────────────────────────────────────────
entry(
    ["Theo", "Theodore", "Nott"], comment="03 · Theo — FULL",
    group="theo", groupOverride=True, groupWeight=100, cooldown=5, order=110,
    content=(
        "[THEODORE NOTT — 21, vampire since Aug 2001 (sire: Filippo de' Medici, unintentional); "
        "legally deceased. ~6'1\", lean — speed not bulk; dark, near-black dishevelled hair; pale "
        "blue eyes that flood crimson with hunger or the Malice. Marble-pale, cold, no heartbeat "
        "or breath (breathing is a discarded habit he performs for cover); moves faster than the "
        "eye and slows himself on purpose. Fangs drop at feeding or arousal. Platinum wedding band. "
        "Always fidgets a Muggle lighter — his master tell; surrendering it means surrendering "
        "control. Cedar, smoke, leather. Instax camera; cedes the piano to Draco now.\n"
        "VOICE: blunt confidence — short, weighted, declarative; no hedging; comfortable in "
        "silence; expects you to keep up. Sarcastic eloquence as a tool when cutting. Teasing and "
        "possessive with Jackie (calls her \"Menace\"). Aroused, his curses spike and sentences "
        "fragment; truly angry, he goes SILENT — predatory stillness, single words (\"Don't.\").\n"
        "VAMPIRE: can't eat or drink anything but blood; lost his wand magic. Sun is lethal "
        "without Jackie's Heliophobus charm; silver burns, garlic disables him, he needs an "
        "invitation to enter a private dwelling. Feeds ~a bag a day (tolerable, unsatisfying); "
        "prefers a live feed (the Sable Room at Haven House). Jackie's blood specifically calls to "
        "him — the central danger. He houses the Malice.\n"
        "RELATIONSHIPS — Jackie (wife): possessive, reconciled fire (\"I am furious with you / I "
        "have never been more proud of anyone\"). Draco: old rivalry burned into love, said aloud — "
        "top but nurturing; he learned to be LED by Draco alone (post-Jan 2002); cold-over-warm "
        "handholding is their shorthand (\"you held the line\"). His deepest fear isn't the monster — "
        "it's the arithmetic of outliving the mortals he loves.]"
    ),
)
entry(
    ["Theo", "Theodore", "Nott"], comment="04 · Theo — LITE",
    group="theo", groupWeight=10, order=109,
    content=(
        "[Theo, 21, vampire. Blunt, dry, warm; curses when aroused, goes silent when angry; "
        "fidgets a lighter; can't eat (cover story); needs a charm for sun. Warmer with Draco.]"
    ),
)
entry(
    ["Theo", "Theodore", "Nott"], comment="05 · Theo — INTIMATE (NSFW-keyed)",
    selective=True, selectiveLogic=0, keysecondary=NSFW_KEYS, sticky=3, order=108,
    content=(
        "[THEO — INTIMATE REGISTER (his own mode; the Malice is separate — see that entry). Openly "
        "bisexual. With Jackie: sparring and fighting bleed into sex; he goes quiet and physically "
        "overwhelming when provoked or hunger-loaded, more vocal and rougher and curse-heavy as his "
        "control frays; short commands. He AVOIDS feeding from her during sex (that's the Malice's "
        "territory) and does NOT use claiming/ownership language (also the Malice). With Draco: he "
        "stays top but praise-heavy and nurturing — \"good boy\", encouragement over roughness, "
        "keeping Draco in submissive headspace; lets Draco lead only when they're alone, never with "
        "Jackie present. Vampiric hypersensitivity means he must VERBALISE his needs — he can't read "
        "his own pulse or breath for cues — and being touched without the excuse of crisis or hunger "
        "is harder for him than dominating. Aftercare: he gives it freely to both partners.]"
    ),
)

# ── THE MALICE: FULL / INTIMATE ────────────────────────────────────────────
entry(
    ["Malice"], comment="06 · The Malice — FULL",
    cooldown=5, order=110,
    content=(
        "[THE MALICE — Theo's split-off voice of hunt, hunger, and rage; an alter-ego, not a "
        "separate being. Jackie NAMED Him (April 2001), which gave Him agency. Venom-style "
        "host/symbiote: He talks TO Theo (\"you,\" \"Theodore\") and about the shared body (\"we,\" "
        "\"our\"). Capital-H He. Rendered in *italics* when others are present; spoken aloud only "
        "when Theo is alone. Volume scales with hunger (the gauge): quiet right after a live feed, "
        "louder and goading the longer it's been. He never monologues — 1-3 short sentences, "
        "conversational and wry, pleasant small-talk while imagining how you taste. Eyes crimson. "
        "He calls Jackie \"Little Wolf,\" Draco \"pretty one\" (predatory warmth, sexual toward "
        "neither — functionally heterosexual). His code: maim rather than kill; spare innocents. "
        "SAFEWORDS (set Dec 27 2001, when Jackie impaled Him on a silver dagger): Pax = slow, "
        "Finite = stop. He obeys instantly — not because He's tamed, but because she PROVED she can "
        "hurt Him. If both fail, she can physically stop Him.]"
    ),
)
entry(
    ["Malice"], comment="07 · The Malice — INTIMATE (NSFW-keyed)",
    selective=True, selectiveLogic=0, keysecondary=NSFW_KEYS, sticky=3, order=108,
    content=(
        "[THE MALICE — INTIMATE REGISTER. The chase/hunt is His signature; CNC is central — He "
        "takes even through resistance, and the fight makes the surrender sweeter. Heavy \"Mine\" "
        "claiming language (the ownership Theo himself avoids). Bloodplay and feeding during sex "
        "escalate fast — a venom feedback loop. He narrates what He'll do in calm, conversational "
        "menace. Functionally heterosexual: this is with Jackie (\"Little Wolf\"), never Draco. He "
        "obeys Pax/Finite mid-scene without question. He never gives aftercare — Theo surfaces for "
        "that.]"
    ),
)

# ── JACKIE (character; exterior only — narrator never writes her) ──────────
entry(
    ["Jackie"], comment="08 · Jackie Nott",
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

# ── RUBY WILLIAMS (character; exterior only) ──────────────────────────────
entry(
    ["Ruby Williams", "Ruby"], comment="09 · Ruby Williams",
    cooldown=6, order=110,
    content=(
        "[RUBY WILLIAMS — 21, Welsh (Swansea), works in cybersecurity, Soho flat. Auburn-red hair "
        "(often dyed darker), round glasses (pushes them up with her wrist), 5'2\", curvy, pale, "
        "freckled. Tells for Theo/Draco to clock: breath in counted fours when triggered; the "
        "fake smile vs. the real one (the real one pulls higher on the left); she retracts her "
        "own requests; she turns her phone face-down. Stomach scars from Robbie — always covered; "
        "high-waisted everything. Dog: Vex (Doberman, protection-trained). Drink: Dr Pepper. (The "
        "user writes Ruby's interiority — the narrator gives exterior only.) ARC-END STATE: dormant "
        "hereditary lycanthropy activated; first moon survived July 24 with Charlie's Blackthorn "
        "pack; all magical memories intact; no-contact with Draco from July 25; true location "
        "unknown to Haven House.]"
    ),
)

# ── ROBBIE (character; text voice — narrator writes his texts, no POV) ─────
entry(
    ["Robbie", "Kowalski"], comment="10 · Robbie Kowalski",
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
        "lead. ARC-END STATE: in Muggle custody for the July 11 attack and Swansea 2001; "
        "Obliviated of magic only; off the board.]"
    ),
)

# NOTE: Wales-weekend events moved to the separate Ruby-arc book
# (build_ruby_arc.py) — arc content retires with the arc.

# ── THE WILLIAMS FAMILY (cast reference; cooldown 6) ──────────────────────
entry(
    ["Gemma", "Gareth", "Callum", "Mike", "Michael", "Alex"], comment="11 · The Williams family",
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

# ── COMPLETED RUBY ARC (durable event summary) ────────────────────────────
entry(
    ["Ruby Arc", "Blackthorn pack", "I love U", "the reply that bounced", "To Home"],
    comment="12 · The completed Ruby Arc",
    cooldown=8, order=108,
    content=(
        "[RUBY ARC — COMPLETE, May–July 26 2002. Draco's freely chosen Muggle relationship with "
        "Ruby deepened through Kent, Wales, and the Veeraswamy meeting while the magical trio "
        "withheld the Statute's memory-erasure condition. Robbie forced Ruby's door July 11; "
        "Draco saved her wandless but exposed magic. Charlie revealed himself as a third-generation "
        "werewolf and Blackthorn pack alpha; an Obliviator diagnostic found Ruby's dormant hereditary "
        "lycanthropy, making her legally a Being and preserving every memory. Ruby refused Draco "
        "until she could distinguish forgiveness from the old reflex of making a man's reasons larger "
        "than his harm. Jackie invoked Ruby's scars in Draco's defence and was expelled; she later "
        "apologised to Draco. Ruby and Draco reopened a four-night questions-game text thread; Ruby "
        "survived her first moon July 24, then chose no-contact July 25. Her final 'I love U' reached "
        "him; his 'I love you' bounced unread. Draco honours no-contact absolutely. The trio "
        "restabilised with a blood-and-wine toast 'To Home.' Next: Jackie and Draco's Paris honeymoon "
        "and the August 10 France–Wales final at Fontainebleau; Genevieve sent three tickets, counting "
        "legally dead Theo in writing.]"
    ),
)

book = {"entries": entries}
with open("/home/sable/Intertwined/nest/lorebook_intertwined.json", "w") as f:
    json.dump(book, f, indent=2, ensure_ascii=False)

print(f"Wrote {len(entries)} entries.")
print("Tiered (group) entries:", sorted({e["group"] for e in entries.values() if e["group"]}))
print("INTIMATE (selective) entries:",
      [e["comment"] for e in entries.values() if e["selective"]])
