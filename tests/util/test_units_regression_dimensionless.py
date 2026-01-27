import pytest

from astranotes.util.units import (
    unit_registry,
    Length,
    Time,
    Angle,
    Mass,
    Dimensionless,
    CompositeUnit,
)


def test_dimensionless_selected_unit_is_blank_not_one():
    """
    Regression: Dimensionless should map to the dedicated 'unitless' unit
    whose abbreviation is '', not to a CompositeUnit that pretty-prints as '1'.
    """
    km = unit_registry.get_unit_by_abbreviation(Length, "km")
    s = unit_registry.get_unit_by_abbreviation(Time, "s")
    rad = unit_registry.get_unit_by_abbreviation(Angle, "rad")
    kg = unit_registry.get_unit_by_abbreviation(Mass, "kg")
    dimless = unit_registry.get_unit_by_abbreviation(Dimensionless, "")

    env = {
        unit_registry.LENGTH: km,
        unit_registry.TIME: s,
        unit_registry.ANGLE: rad,
        unit_registry.MASS: kg,
        unit_registry.DIMENSIONLESS: dimless,
    }

    u = unit_registry.get_unit_for_dimension(Dimensionless, env)
    assert u.abbreviation == ""
    assert u.pretty_abbreviation() == ""


def test_compositeunit_dimensionless_pretty_is_one_but_not_used_for_dimensionless():
    """
    Regression guardrail: CompositeUnit([], []) is mathematically dimensionless
    and pretty_abbreviation() returns '1' (fine), but the Dimensionless dimension
    should be represented by the dedicated unit with empty abbreviation.

    This test makes the distinction explicit so future refactors don't accidentally
    "simplify" Dimensionless into CompositeUnit([], []) and reintroduce '1'.
    """
    cu = CompositeUnit([], [])
    assert cu.pretty_abbreviation() == "1"

    dimless = unit_registry.get_unit_by_abbreviation(Dimensionless, "")
    assert dimless.pretty_abbreviation() == ""
