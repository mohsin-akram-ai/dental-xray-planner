# Treatment logic engine (rule based).
# Keys are the cleaned class names that come from detector.py.

RULES = {
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