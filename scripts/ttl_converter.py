import json
from collections import defaultdict

input_file = "data/triplets_raw.txt"
output_file = "data/triplets_formatted.ttl"

# -------------------------------
# 🔧 Helpers
# -------------------------------
def normalize_name(name):
    return name.strip().replace("-", "").replace(" ", "_").replace("’", "").replace("'", "").replace(",", "")

def normalize_relation(r):
    return " ".join(r.strip().title().split())

# -------------------------------
# 🧠 ENTITY TYPE DETECTION
# -------------------------------
def detect_type(name):
    n = name.lower()

    # -------- TIME --------
    if any(x in n for x in ["year", "yuga", "age", "kalpa"]):
        return "Time"

    # -------- PLACE --------
    if any(x in n for x in ["city", "kingdom", "capital", "forest", "mountain", "hill", "river", "lake"]):
        return "Place"

    # -------- ANIMAL --------
    if any(x in n for x in ["dog", "horse", "bird", "serpent", "snake", "cow", "monkey", "deer"]):
        return "Animal"

    # -------- GROUP / COUNT --------
    if any(char.isdigit() for char in n):
        return "Group"

    # -------- DEFAULT --------
    return "Person"

# -------------------------------
# 🧠 Gender inference
# -------------------------------
MALE_RELATIONS = {
    "Father Of", "Son Of", "Husband Of", "Brother Of",
    "Uncle Of", "Grandfather Of", "Great Grandfather Of",
    "Grandson Of", "Great Grandson Of", "Nephew Of"
}

FEMALE_RELATIONS = {
    "Mother Of", "Daughter Of", "Wife Of", "Sister Of",
    "Aunt Of", "Grandmother Of", "Great Grandmother Of",
    "Granddaughter Of", "Great Granddaughter Of", "Niece Of"
}

gender_map = {}

def assign_gender(name, relation):
    if relation in MALE_RELATIONS:
        if gender_map.get(name) == "F":
            return
        gender_map[name] = "M"

    elif relation in FEMALE_RELATIONS:
        if gender_map.get(name) == "M":
            return
        gender_map[name] = "F"

# -------------------------------
# 🧠 ENTITY FORMAT
# -------------------------------
def get_entity(name):
    name_clean = normalize_name(name)
    entity_type = detect_type(name)

    if entity_type == "Person":
        gender = gender_map.get(name, "M")
        return f"ex:{name_clean}_{gender}"
    else:
        return f"ex:{name_clean}"

# -------------------------------
# 🔁 RELATION MAP (FULL)
# -------------------------------
RELATION_MAP = {

    # FAMILY
    "Father Of": "ex:isFatherOf",
    "Mother Of": "ex:isMotherOf",
    "Son Of": "ex:isSonOf",
    "Daughter Of": "ex:isDaughterOf",
    
    "Brother Of": "ex:isBrotherOf",
    "Sister Of": "ex:isSisterOf",
    
    "Husband Of": "ex:isHusbandOf",
    "Wife Of": "isWifeOf",
    "Spouse Of": "isSpouseOf",

    "Grandfather Of": "ex:isGrandfatherOf",
    "Grandmother Of": "ex:isGrandmotherOf",
    "Grandson Of": "ex:isGrandSonOf",
    "Granddaughter Of": "ex:isGrandDaughterOf",

    "Great Grandfather Of": "ex:isGreatGrandfatherOf",
    "Great Grandmother Of": "ex:isGreatGrandmotherOf",
    "Great Grandson Of": "ex:isGreatGrandSonOf",
    "Great Granddaughter Of": "ex:isGreatGrandDaughterOf",

    # EXTENDED
    "Uncle Of": "ex:isUncleOf",
    "Aunt Of": "ex:isAuntOf",
    "Nephew Of": "ex:isNephewOf",
    "Niece Of": "ex:isNieceOf",

    # COUSINS
    "Cousin Of": "ex:isCousinOf",

    # SOCIAL
    "Friend": "ex:isFriendOf",
    "Enemy Of": "ex:isEnemyOf",

    # LEARNING
    "Student Of": "ex:isDiscipleOf",
    "Teacher Of": "ex:isMasterOf",

    # POWER
    "King Of": "ex:isKingOf",
    "Ruler Of": "ex:isRulerOf",
    "Servant Of": "ex:isServantOf",

    # OTHER
    "Ancestor Of": "ex:isAncestorOf",
    "Descendant Of": "ex:isDescendantOf",
    "Killed": "ex:isKillerOf",
    "Killed By": "ex:hasKiller",
    "Devotee Of": "ex:isDevoteeOf"
}

# -------------------------------
# ❌ Noise filter
# -------------------------------
IGNORE_IS = {
    "associated", "mentioned", "connected", "related", "linked"
}

# -------------------------------
# 🧠 Parser
# -------------------------------
def parse_triple(line):
    line = line.strip()

    try:
        data = json.loads(line)
        if "Subject" in data:
            return data.get("Subject"), data.get("Relation") or data.get("Is"), data.get("Object")
    except:
        pass

    try:
        if line.startswith("{") and line.endswith("}"):
            parts = line[1:-1].split('" : "')
            if len(parts) == 3:
                s = parts[0].replace('"', '').strip()
                r = parts[1].replace('"', '').strip()
                o = parts[2].replace('"', '').strip()
                return s, r, o
    except:
        pass

    return None

# -------------------------------
# 🚀 Processing
# -------------------------------
entity_triples = defaultdict(set)
entities = set()

with open(input_file, "r", encoding="utf-8") as f:
    for line in f:
        if not line.startswith("{"):
            continue

        parsed = parse_triple(line)
        if not parsed:
            continue

        s, r, o = parsed
        if not s or not r or not o:
            continue

        r = normalize_relation(r)

        assign_gender(s, r)

        s_entity = get_entity(s)
        o_entity = get_entity(o)

        entities.add(s)
        entities.add(o)

        # CLASS assignment
        if r.lower() == "is":
            if any(x in o.lower() for x in IGNORE_IS):
                continue
            entity_triples[s_entity].add(f"{s_entity} a ex:{normalize_name(o)} .")

        elif r in RELATION_MAP:
            entity_triples[s_entity].add(f"{s_entity} {RELATION_MAP[r]} {o_entity} .")

# -------------------------------
# 🧠 ADD TYPES + GENDER
# -------------------------------
for e in entities:
    entity = get_entity(e)
    entity_type = detect_type(e)

    entity_triples[entity].add(f"{entity} a ex:{entity_type} .")

    if entity_type == "Person":
        gender = gender_map.get(e, "M")
        if gender == "M":
            entity_triples[entity].add(f"{entity} ex:hasSex ex:Male .")
        else:
            entity_triples[entity].add(f"{entity} ex:hasSex ex:Female .")

# -------------------------------
# 💾 Save grouped
# -------------------------------
with open(output_file, "w", encoding="utf-8") as f:
    f.write("@prefix ex: <http://www.mytho-ontologist.org/Mythology#> .\n\n")

    for entity in sorted(entity_triples.keys()):
        for triple in sorted(entity_triples[entity]):
            f.write(triple + "\n")
        f.write("\n")

print("✅ DONE - ENTITY TYPING + ONTOLOGY ASSIGNMENT COMPLETE")