rules = {
    "calculus": {
        "treatment": "Scaling and cleaning recommended",
        "urgency": "Low",
    },
    "gingivitis": {
        "treatment": "Scaling, brushing, mouthwash",
        "urgency": "Low",
    },
    "caries": {
        "treatment": "Filling ya RCT, dentist X-ray dekh kar tay karega",
        "urgency": "Medium",
    },
    "periapical lesion": {
        "treatment": "Infection hai, dentist se jaldi milein",
        "urgency": "High",
    },
}

default_rule = {
    "treatment": "Please see a dentist",
    "urgency": "Medium",
}


def get_plan(condition):
    return rules.get(condition, default_rule)


plan = get_plan("caries")
print(plan["treatment"])
print(plan["urgency"])

plan3 = get_plan("gingivitis")
print(plan3["treatment"])
print(plan3["urgency"])