def get_treatment(condition):
    if condition == "calculus":
        return "Scaling and cleaning recommended"
    elif condition == "gingivitis":
        return "Scaling, brushing, mouthwash"
    elif condition == "caries":
        return "Filling ya RCT, dentist X-ray dekh kar tay karega"
    else:
        return "Please see a dentist"

print(get_treatment("calculus"))
print(get_treatment("gingivitis"))
print(get_treatment("caries"))
print(get_treatment("xyz"))