rules = {
    "calculus": "Scaling and cleaning recommended",
    "gingivitis": "Scaling, brushing, mouthwash",
    "caries": "Filling ya RCT, dentist X-ray dekh kar tay karega",
    "periapical lesion": "Infection hai, dentist se jaldi milein",
}


def get_treatment(condition):
    return rules.get(condition, "Please see a dentist")


print(get_treatment("calculus"))
print(get_treatment("caries"))
print(get_treatment("periapical lesion"))
print(get_treatment("abc"))