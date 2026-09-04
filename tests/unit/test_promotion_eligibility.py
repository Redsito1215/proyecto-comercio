from backend.modules.promotions.eligibility import eligible_for_segment,experimental_group


def test_assignment_is_stable():
    assert experimental_group("promotion","customer",20)==experimental_group("promotion","customer",20)


def test_at_risk_uses_individual_signal():
    assert eligible_for_segment("at_risk",{}, {"status":"at_risk"})[0]
    assert not eligible_for_segment("at_risk",{}, {"status":"on_time"})[0]


def test_loyal_segment_requires_profitability():
    assert eligible_for_segment("loyal_profitable",{"segment":"leal_rentable"},{})[0]
