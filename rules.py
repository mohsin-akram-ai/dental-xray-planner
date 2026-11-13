# Treatment logic engine (rule based).
# Keys are the cleaned class names that come from detector.py.

RULES = {
    # ---------- X-ray model (Model A) ----------
    "caries": {
        "treatment": "Filling or Root Canal Treatment (RCT) may be needed. The dentist will decide after examining the tooth.",
        "urgency": "Medium",
    },
    "periapical lesion": {
        "treatment": "Possible infection at the root tip. See a dentist soon. Root Canal Treatment (RCT) or other treatment may be needed.",
        "urgency": "High",
    },
    "impacted tooth": {
        "treatment": "A dentist or oral surgeon should check whether the tooth needs to be removed.",
        "urgency": "Medium",
    },
    "crown": {
        "treatment": "A crown (cap) is already present on this tooth. Regular check-ups are advised to make sure it is in good condition.",
        "urgency": "Low",
    },
    "filling": {
        "treatment": "An existing filling is present. Regular check-ups are advised to make sure it is intact.",
        "urgency": "Low",
    },
    "implant": {
        "treatment": "A dental implant is present. Keep the area clean and visit a dentist for regular check-ups.",
        "urgency": "Low",
    },
    "root canal treatment": {
        "treatment": "Root Canal Treatment (RCT) has already been done on this tooth. Regular check-ups are advised.",
        "urgency": "Low",
    },
    "missing teeth": {
        "treatment": "One or more teeth appear to be missing. A dentist may suggest a bridge, an implant or a denture.",
        "urgency": "Medium",
    },
    "retained root": {
        "treatment": "A part of a tooth root may be left in the jaw. A dentist should check whether it needs to be removed.",
        "urgency": "Medium",
    },
    "root piece": {
        "treatment": "A broken root piece may be present. A dentist should check whether it needs to be removed.",
        "urgency": "Medium",
    },
    "mandibular canal": {
        "treatment": "Normal anatomy (the nerve canal of the lower jaw). No treatment needed. A dentist keeps it in mind before procedures like extraction or implants.",
        "urgency": "Low",
    },
    "maxillary sinus": {
        "treatment": "Normal anatomy (the air space in the upper jaw). No treatment needed.",
        "urgency": "Low",
    },

    # ---------- Photo model (Model B) ----------
    "calculus": {
        "treatment": "Scaling and cleaning recommended.",
        "urgency": "Low",
    },
    "gingivitis": {
        "treatment": "Scaling, regular brushing and flossing, and an antiseptic mouthwash as advised by a dentist.",
        "urgency": "Low",
    },
    "mouth ulcer": {
        "treatment": "Keep an eye on it. If it lasts more than two weeks, see a dentist.",
        "urgency": "Low",
    },
    "discoloration": {
        "treatment": "Polishing or whitening may help. Ask a dentist which option is suitable.",
        "urgency": "Low",
    },
    "hypodontia": {
        "treatment": "Discuss orthodontic or prosthetic options with a dentist.",
        "urgency": "Medium",
    },
}

DEFAULT_RULE = {
    "treatment": "Please see a dentist for a proper examination.",
    "urgency": "Medium",
}


def get_plan(condition):
    return RULES.get(condition, DEFAULT_RULE)