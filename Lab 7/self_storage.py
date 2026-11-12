import math


def _to_finite_float(value):
    """Return value as a finite float, or None if it can't be."""
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return number if math.isfinite(number) else None


def parse_rental(text):
    """Parse 'unit:months' into (Unit, months).

    Returns None for anything invalid (non-string, missing/extra ':',
    empty unit, non-numeric / non-finite / non-positive months).
    """
    if not isinstance(text, str):
        return None
    parts = text.split(':')
    if len(parts) != 2:
        return None
    unit = parts[0].strip()
    months = _to_finite_float(parts[1].strip())
    if not unit or months is None or months <= 0:
        return None
    return unit.title(), months


def duration_average(months_csv):
    """Average of a CSV of positive whole-number months, e.g. '3,6,12' -> 7.0.

    Returns None for anything invalid (non-string, empty, blank elements,
    non-integers, zero or negative values).
    """
    if not isinstance(months_csv, str):
        return None
    values = []
    for item in months_csv.split(','):
        try:
            value = int(item.strip())
        except (ValueError, OverflowError):
            return None
        if value <= 0:
            return None
        values.append(value)
    # split(',') always yields >=1 item, so values can't be empty here,
    # but guard anyway so a future edit can't reintroduce ZeroDivisionError.
    if not values:
        return None
    return sum(values) / len(values)


def payable_rent(text):
    """Parse 'rent|discount' and return rent + 18% tax - discount, floored at 0.

    Returns None for anything invalid (non-string, missing/extra '|',
    non-numeric, non-finite, or negative rent/discount, or overflow).
    """
    if not isinstance(text, str):
        return None
    parts = text.split('|')
    if len(parts) != 2:
        return None
    rent = _to_finite_float(parts[0].strip())
    discount = _to_finite_float(parts[1].strip())
    if rent is None or discount is None or rent < 0 or discount < 0:
        return None
    total = rent * 1.18 - discount
    if not math.isfinite(total):
        return None
    return round(max(total, 0.0), 2)


def main():
    print("==== Running parse_rental ====")
    user_input = input("Enter unit:months (e.g. medium:6): ")
    result = parse_rental(user_input)
    print("Unit and Months:", result if result is not None
          else "Invalid input (expected unit:months with months > 0)")

    print("\n==== Running duration_average ====")
    user_input = input("Enter rental months as CSV (e.g. 3,6,12): ")
    result = duration_average(user_input)
    print("Average Duration:", result if result is not None
          else "Invalid input (expected positive whole numbers, comma-separated)")

    print("\n==== Running payable_rent ====")
    user_input = input("Enter rent|discount (e.g. 2400|200): ")
    result = payable_rent(user_input)
    print("Payable Rent:", result if result is not None
          else "Invalid input (expected non-negative rent|discount)")


if __name__ == "__main__":
    main()
