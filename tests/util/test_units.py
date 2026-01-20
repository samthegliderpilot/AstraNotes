import math
import pytest

from astrocalc.util.units import (
    SimpleUnit,
    CompositeUnit,
    Dimension,
    UnitRegistry,
    unit_registry,
    Length,
    Time,
    Angle,
    Mass,
    Dimensionless,
)


def test_simpleunit_roundtrip_km_m():
    km = unit_registry.get_unit_by_abbreviation(Length, "km")
    m = unit_registry.get_unit_by_abbreviation(Length, "m")

    # 7 km -> 7000 m (native should be meters)
    native = km.to_native(7.0)
    assert native == pytest.approx(7000.0)

    # back to km
    back = km.from_native(native)
    assert back == pytest.approx(7.0)

    # 500 m native -> 0.5 km
    assert km.from_native(500.0) == pytest.approx(0.5)
    assert m.from_native(500.0) == pytest.approx(500.0)


def test_simpleunit_roundtrip_deg_rad():
    deg = unit_registry.get_unit_by_abbreviation(Angle, "deg")
    rad = unit_registry.get_unit_by_abbreviation(Angle, "rad")

    # 180 deg == pi rad
    native = deg.to_native(180.0)
    assert native == pytest.approx(math.pi)

    # round-trip
    assert deg.from_native(native) == pytest.approx(180.0)

    # rad is native scale 1
    assert rad.to_native(1.23) == pytest.approx(1.23)
    assert rad.from_native(1.23) == pytest.approx(1.23)


def test_compositeunit_scale_to_native_km3_s2():
    km = unit_registry.get_unit_by_abbreviation(Length, "km")
    s = unit_registry.get_unit_by_abbreviation(Time, "s")

    # km^3 / s^2 should scale by (1000^3)/(1^2) = 1e9 to native (m^3 / s^2)
    cu = CompositeUnit([km, km, km], [s, s])

    assert cu.to_native(1.0) == pytest.approx(1e9)
    assert cu.from_native(1e9) == pytest.approx(1.0)


def test_compositeunit_pretty_abbreviation_exponents():
    km = unit_registry.get_unit_by_abbreviation(Length, "km")
    s = unit_registry.get_unit_by_abbreviation(Time, "s")

    cu = CompositeUnit([km, km, km], [s, s])
    assert cu.pretty_abbreviation() == "km³/s²"


def test_compositeunit_pretty_abbreviation_denominator_only():
    s = unit_registry.get_unit_by_abbreviation(Time, "s")

    cu = CompositeUnit([], [s, s])
    # numerator should show as 1
    assert cu.pretty_abbreviation() == "1/s²"


def test_dimension_mul_div_and_hash_equality():
    L = Dimension({"LENGTH": 1})
    T = Dimension({"TIME": 1})

    # L^3 / T^2
    dim = L * L * L / (T * T)
    assert dim == Dimension({"LENGTH": 3, "TIME": -2})

    # hash/equality should work structurally
    assert hash(dim) == hash(Dimension({"TIME": -2, "LENGTH": 3}))


def test_unitregistry_get_unit_for_dimension_base_and_composite():
    # base: Length should return currently selected length unit
    km = unit_registry.get_unit_by_abbreviation(Length, "km")
    s = unit_registry.get_unit_by_abbreviation(Time, "s")
    env = {
        unit_registry.LENGTH: km,
        unit_registry.TIME: s,
        unit_registry.ANGLE: unit_registry.get_unit_by_abbreviation(Angle, "rad"),
        unit_registry.MASS: unit_registry.get_unit_by_abbreviation(Mass, "kg"),
        unit_registry.DIMENSIONLESS: unit_registry.get_unit_by_abbreviation(Dimensionless, ""),
    }

    assert unit_registry.get_unit_for_dimension(Length, env) == km
    assert unit_registry.get_unit_for_dimension(Time, env) == s

    # composite dimension: L^3 / T^2 should produce CompositeUnit with pretty km³/s²
    mu_dim = Length * Length * Length / (Time * Time)
    mu_unit = unit_registry.get_unit_for_dimension(mu_dim, env)
    assert isinstance(mu_unit, CompositeUnit)
    assert mu_unit.pretty_abbreviation() == "km³/s²"


def test_dimensionless_unit_abbreviation_is_empty_string():
    u = unit_registry.get_unit_by_abbreviation(Dimensionless, "")
    assert u.abbreviation == ""
    assert u.pretty_abbreviation() == ""

    # no-op conversion
    assert u.to_native(3.14) == pytest.approx(3.14)
    assert u.from_native(3.14) == pytest.approx(3.14)
