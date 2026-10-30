import pytest
from self_storage import rent_due, access_allowed, payment_status


# ---------- rent_due ----------
def test_within_deposit_months():
    assert rent_due("small", 1, False, False) == 0


def test_unknown_unit_size():
    with pytest.raises(ValueError, match="unknown unit size"):
        rent_due("huge", 3, False, False)


def test_negative_months():
    with pytest.raises(ValueError, match="invalid months"):
        rent_due("small", -1, False, False)


def test_zero_months_is_valid():
    # months < 0 is False at the boundary
    assert rent_due("small", 0, False, False) == 0


@pytest.mark.parametrize("size,months,expected", [
    ("small", 1, 0),      # extra == 0 boundary -> no charge
    ("medium", 2, 0),
    ("large", 3, 0),
    ("small", 2, 80),     # extra 1
    ("large", 4, 80),     # large, non-member
])
def test_non_member_deposit_boundaries(size, months, expected):
    assert rent_due(size, months, False, False) == expected


def test_member_small_extra_month():
    # covered 1+1 = 2; months=2 -> free
    assert rent_due("small", 2, False, True) == 0


def test_member_medium_charged():
    # covered 2+1 = 3; months=4 -> 1*80
    assert rent_due("medium", 4, False, True) == 80


def test_member_large_gets_no_bonus():
    # member but large -> covered stays 3; months=4 -> 1*80
    assert rent_due("large", 4, False, True) == 80


def test_climate_vs_standard_rate():
    assert rent_due("small", 3, True, False) == 240
    assert rent_due("small", 3, False, False) == 160


def test_extra_exactly_six_no_discount():
    # extra == 6 boundary: no long-stay discount
    assert rent_due("small", 7, False, False) == 6 * 80
    assert rent_due("small", 7, True, False) == 6 * 120


def test_long_stay_discount_standard():
    # extra 7 -> rate 70
    assert rent_due("small", 8, False, False) == 7 * 70


def test_long_stay_discount_climate():
    # extra 7 -> rate 105
    assert rent_due("small", 8, True, False) == 7 * 105


# ---------- access_allowed ----------
def test_owner_within_limit():
    assert access_allowed(3, 4, True) is True


def test_owner_over_limit():
    assert access_allowed(12, 5, True) is False


def test_non_owner_normal_hours_within_limit():
    assert access_allowed(12, 1, False) is True
    assert access_allowed(12, 2, False) is True


def test_non_owner_over_visitor_limit():
    assert access_allowed(12, 3, False) is False


@pytest.mark.parametrize("hour,expected", [
    (5, False),    # hour < 6
    (6, True),     # lower boundary ok
    (22, True),    # upper boundary ok
    (23, False),   # hour > 22
])
def test_non_owner_hour_boundaries(hour, expected):
    assert access_allowed(hour, 1, False) is expected


# ---------- payment_status ----------
@pytest.mark.parametrize("days,autopay,late,expected", [
    # autopay, no late: cutoff 0
    (0, True, False, "current"),
    (-1, True, False, "grace"),
    (-15, True, False, "grace"),
    (-16, True, False, "lien"),
    # manual, no late: cutoff 5
    (5, False, False, "current"),
    (4, False, False, "grace"),
    (-10, False, False, "grace"),
    (-11, False, False, "lien"),
    # autopay + prior late: cutoff 10
    (10, True, True, "current"),
    (9, True, True, "grace"),
    (-5, True, True, "grace"),
    (-6, True, True, "lien"),
    # manual + prior late: cutoff 15
    (15, False, True, "current"),
    (14, False, True, "grace"),
    (0, False, True, "grace"),
    (-1, False, True, "lien"),
])
def test_payment_status(days, autopay, late, expected):
    assert payment_status(days, autopay, late) == expected
