import math

from hypothesis import given, settings, strategies as st
from self_storage import parse_rental, duration_average, payable_rent

# Anything a caller could plausibly hand us: text, None, numbers, lists.
anything = st.one_of(
    st.text(),
    st.none(),
    st.integers(),
    st.floats(allow_nan=True, allow_infinity=True),
    st.lists(st.integers()),
)

# Inputs that are *shaped* like valid input, so Hypothesis reaches the deeper logic.
unit_names = st.text(
    alphabet=st.characters(whitelist_categories=("L",), blacklist_characters=":|,"),
    min_size=1,
    max_size=15,
)
positive_months = st.integers(min_value=1, max_value=10_000)


# ---------------------------------------------------------------- parse_rental
@given(st.text() | st.none())
def test_parse_rental_no_crash(s):
    try:
        parse_rental(s)
    except Exception as e:
        assert False, f"parse_rental crashed with: {e!r}"


@given(anything)
def test_parse_rental_any_type_no_crash(s):
    try:
        parse_rental(s)
    except Exception as e:
        assert False, f"parse_rental crashed with: {e!r}"


@given(unit_names, positive_months)
def test_parse_rental_valid_roundtrip(unit, months):
    result = parse_rental(f" {unit} : {months} ")
    assert result is not None
    name, value = result
    assert name == unit.strip().title()
    assert value == float(months)


@given(st.text() | st.none())
def test_parse_rental_result_is_clean(s):
    result = parse_rental(s)
    if result is not None:
        name, months = result
        assert name != ""
        assert math.isfinite(months) and months > 0


# ------------------------------------------------------------ duration_average
@given(st.text() | st.none())
def test_duration_average_no_crash(s):
    try:
        duration_average(s)
    except Exception as e:
        assert False, f"duration_average crashed with: {e!r}"


@given(anything)
def test_duration_average_any_type_no_crash(s):
    try:
        duration_average(s)
    except Exception as e:
        assert False, f"duration_average crashed with: {e!r}"


@given(st.lists(positive_months, min_size=1, max_size=20))
def test_duration_average_between_min_and_max(values):
    result = duration_average(",".join(map(str, values)))
    assert result is not None
    assert min(values) <= result <= max(values)


@given(st.lists(positive_months, min_size=1, max_size=20))
def test_duration_average_is_true_mean(values):
    result = duration_average(",".join(map(str, values)))
    assert math.isclose(result, sum(values) / len(values), rel_tol=1e-9)


# ---------------------------------------------------------------- payable_rent
@given(st.text() | st.none())
def test_payable_rent_no_crash(s):
    try:
        payable_rent(s)
    except Exception as e:
        assert False, f"payable_rent crashed with: {e!r}"


@given(anything)
def test_payable_rent_any_type_no_crash(s):
    try:
        payable_rent(s)
    except Exception as e:
        assert False, f"payable_rent crashed with: {e!r}"


@given(
    st.floats(min_value=0, max_value=1e9, allow_nan=False),
    st.floats(min_value=0, max_value=1e9, allow_nan=False),
)
def test_payable_rent_never_negative_and_finite(rent, discount):
    result = payable_rent(f"{rent}|{discount}")
    assert result is not None
    assert math.isfinite(result) and result >= 0


@given(st.text() | st.none())
def test_payable_rent_result_is_clean(s):
    result = payable_rent(s)
    if result is not None:
        assert math.isfinite(result) and result >= 0


def test_known_values():
    assert parse_rental("medium:6") == ("Medium", 6.0)
    assert duration_average("3,6,12") == 7
    assert payable_rent("2400|200") == 2632.0
