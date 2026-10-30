import pytest
from self_storage import rent_due, access_allowed, payment_status


# ---------- rent_due ----------
def test_within_deposit_months():
    assert rent_due("small", 1, False, False) == 0


def test_unknown_unit_size():
    with pytest.raises(ValueError):
        rent_due("huge", 3, False, False)


def test_negative_months():
    with pytest.raises(ValueError):
        rent_due("small", -1, False, False)


def test_member_gets_extra_covered_month():
    # medium=2 covered +1 member = 3; months=4 -> extra 1 * 80
    assert rent_due("medium", 4, False, True) == 80


def test_climate_rate():
    # small=1 covered; months=3 -> extra 2 * 120
    assert rent_due("small", 3, True, False) == 240


def test_standard_rate():
    # small=1 covered; months=3 -> extra 2 * 80
    assert rent_due("small", 3, False, False) == 160


def test_long_stay_climate_discount():
    # small=1 covered; months=8 -> extra 7 * (120-10-5)
    assert rent_due("small", 8, True, False) == 7 * 105


# ---------- access_allowed ----------
def test_access_allowed():
    assert access_allowed(12, 1, False) is True


def test_owner_access():
    assert access_allowed(3, 4, True) is True


def test_non_owner_outside_hours():
    assert access_allowed(2, 1, False) is False


# ---------- payment_status ----------
def test_autopay_current():
    assert payment_status(0, True, False) == "current"


def test_manual_grace():
    # cutoff 5; grace window is -10..4
    assert payment_status(0, False, False) == "grace"


def test_prior_late_lien():
    # cutoff 10; lien below -5
    assert payment_status(-20, False, True) == "lien"
