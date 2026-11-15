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
    # These names must match the class names in the photo dataset (data.yaml).
    # Note: the dataset spells "discolation" this way, so we use the same spelling here.
    "calculus": {
        "treatment": "Scaling and cleaning recommended.",
        "urgency": "Low",
    },
    "gingivitis": {
        "treatment": "Scaling, regular brushing and flossing, and an antiseptic mouthwash as advised by a dentist.",
        "urgency": "Low",
    },
    "ulcer": {
        "treatment": "Keep an eye on it. If it lasts more than two weeks, see a dentist.",
        "urgency": "Low",
    },
    "tooth discolation": {
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


# ------------------------------------------------------------------
# How much the user can trust each finding.
# Levels come from the mAP50 score on the test images (Box):
#   Good = 75 percent or more, Fair = 45 to 75 percent, Low = below 45 percent.
# ------------------------------------------------------------------
GOOD_NOTE = "The model did well on test images for this finding."
FAIR_NOTE = "The model is only partly accurate for this finding. Please confirm with a dentist."

RELIABILITY = {
    "implant": {"level": "Good", "note": GOOD_NOTE},
    "impacted tooth": {"level": "Good", "note": GOOD_NOTE},
    "mandibular canal": {"level": "Good", "note": GOOD_NOTE},
    "crown": {"level": "Good", "note": GOOD_NOTE},
    "maxillary sinus": {"level": "Good", "note": GOOD_NOTE},
    "filling": {"level": "Fair", "note": FAIR_NOTE},
    "missing teeth": {"level": "Fair", "note": FAIR_NOTE},
    "root canal treatment": {"level": "Fair", "note": FAIR_NOTE},
    "root piece": {"level": "Fair", "note": FAIR_NOTE},
    "caries": {
        "level": "Low",
        "note": "The model often misses caries and sometimes marks healthy areas. Please check with a dentist.",
    },
    "periapical lesion": {
        "level": "Low",
        "note": "The model misses many periapical lesions. A missing result does not mean there is no infection.",
    },
    "retained root": {
        "level": "Not tested",
        "note": "The model saw very few examples of this finding and was not tested on it.",
    },
}

DEFAULT_RELIABILITY = {
    "level": "Not tested",
    "note": "No accuracy test has been done for this finding yet.",
}


def get_reliability(condition):
    return RELIABILITY.get(condition, DEFAULT_RELIABILITY)