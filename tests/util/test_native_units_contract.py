import math
import pytest

from astrocalc.util.units import unit_registry, Length, Time, Angle, Mass, Dimensionless


def test_native_base_units_are_expected():
    """
    Contract test: native (SI) base units are:
      Length -> meter (m)
      Time   -> second (s)
      Angle  -> radian (rad)
      Mass   -> kilogram (kg)
      Dimensionless -> unitless ("")
    """
    m = unit_registry.get_unit_by_abbreviation(Length, "m")
    s = unit_registry.get_unit_by_abbreviation(Time, "s")
    rad = unit_registry.get_unit_by_abbreviation(Angle, "rad")
    kg = unit_registry.get_unit_by_abbreviation(Mass, "kg")
    dimless = unit_registry.get_unit_by_abbreviation(Dimensionless, "")

    # Native units should be identity conversions (factor = 1)
    assert m.to_native(1.0) == pytest.approx(1.0)
    assert m.from_native(1.0) == pytest.approx(1.0)

    assert s.to_native(1.0) == pytest.approx(1.0)
    assert s.from_native(1.0) == pytest.approx(1.0)

    assert rad.to_native(1.0) == pytest.approx(1.0)
    assert rad.from_native(1.0) == pytest.approx(1.0)

    assert kg.to_native(1.0) == pytest.approx(1.0)
    assert kg.from_native(1.0) == pytest.approx(1.0)

    assert dimless.to_native(1.0) == pytest.approx(1.0)
    assert dimless.from_native(1.0) == pytest.approx(1.0)


def test_degree_to_native_is_pi_over_180():
    """
    Contract test: degrees convert to radians via pi/180.
    This pins the angle-native-is-radians assumption explicitly.
    """
    deg = unit_registry.get_unit_by_abbreviation(Angle, "deg")
    assert deg.to_native(180.0) == pytest.approx(math.pi)
    assert deg.to_native(90.0) == pytest.approx(math.pi / 2.0)
