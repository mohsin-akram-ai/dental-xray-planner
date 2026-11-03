from detector import clean_name
from rules import DEFAULT_RULE, RULES, get_plan


def test_clean_name_makes_lowercase():
    assert clean_name("Caries") == "caries"


def test_clean_name_replaces_underscore_and_dash():
    assert clean_name("Periapical_Lesion") == "periapical lesion"
    assert clean_name("Impacted-Tooth") == "impacted tooth"


def test_clean_name_removes_extra_spaces():
    assert clean_name("  mouth   ulcer ") == "mouth ulcer"


def test_known_condition_gets_its_own_plan():
    plan = get_plan("periapical lesion")
    assert plan["urgency"] == "High"


def test_unknown_condition_gets_default_plan():
    assert get_plan("bus") == DEFAULT_RULE


def test_every_rule_has_treatment_and_valid_urgency():
    for name, plan in RULES.items():
        assert plan["treatment"], name
        assert plan["urgency"] in ("Low", "Medium", "High"), name