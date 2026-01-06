from typing import List, Dict
from abc import ABC, abstractmethod

class Unit(ABC):
    """
    Abstract base class for all units.
    Supports conversion to/from native (SI) units.
    """
    def __init__(self, name: str, abbreviation: str):
        self.name = name
        self.abbreviation = abbreviation

    @abstractmethod
    def to_native(self, value: float) -> float:
        pass

    @abstractmethod
    def from_native(self, value: float) -> float:
        pass

    def __repr__(self):
        return f"<Unit {self.name} ({self.abbreviation})>"

class SimpleUnit(Unit):
    """
    Unit with a multiplicative conversion factor to native units.
    """
    def __init__(self, name: str, abbreviation: str, to_native_multiple: float):
        super().__init__(name, abbreviation)
        self.to_native_multiple = to_native_multiple

    def to_native(self, value: float) -> float:
        return value * self.to_native_multiple

    def from_native(self, value: float) -> float:
        return value / self.to_native_multiple

    def get_conversion_factor_to(self, target_unit: 'Unit') -> float:
        if isinstance(target_unit, SimpleUnit):
            return self.to_native_multiple / target_unit.to_native_multiple
        else:
            raise TypeError("Incompatible unit types for conversion.")

    def __repr__(self):
        return f"<SimpleUnit {self.name} ({self.abbreviation}) ×{self.to_native_multiple}>"

#TODO: These unit types are still pretty new, once they are more settled
#- Write doc
#- Add helper functions to compose units with * and / and ** operators
#- Handle powers of units better (think acceleration and length/time**2)
class CompositeUnit(Unit):
    def __init__(self, numerator_units: List[Unit], denominator_units: List[Unit]):
        self.numerator_units = numerator_units
        self.denominator_units = denominator_units
        
        name = "·".join(u.name for u in numerator_units)
        abbr = "·".join(u.abbreviation for u in numerator_units)
        if denominator_units:
            name += " per " + "·".join(u.name for u in denominator_units)
            abbr += "/" + "·".join(u.abbreviation for u in denominator_units)

        super().__init__(name=name, abbreviation=abbr)  # Will override conversion methods

    def to_native(self, value: float) -> float:
        for u in self.numerator_units:
            value = u.to_native(value)
        for u in self.denominator_units:
            value = u.from_native(value)
        return value

    def from_native(self, value: float) -> float:
        for u in self.denominator_units:
            value = u.to_native(value)
        for u in self.numerator_units:
            value = u.from_native(value)
        return value

    def __repr__(self):
        return f"<CompositeUnit {self.abbreviation}>"


class Dimension:
    def __init__(self, components: Dict[str, int]):
        self.components = {k: v for k, v in components.items() if v != 0}
            
    def __mul__(self, other: 'Dimension') -> 'Dimension':
        result = self.components.copy()
        for dim, power in other.components.items():
            result[dim] = result.get(dim, 0) + power
        return Dimension(result)

    def __truediv__(self, other: 'Dimension') -> 'Dimension':
        # Combine components by subtracting powers
        result_components = self.components.copy()
        for dim, power in other.components.items():
            result_components[dim] = result_components.get(dim, 0) - power

        # Remove zero powers
        result_components = {k: v for k, v in result_components.items() if v != 0}

        return Dimension(result_components)

    def __eq__(self, other):
        return self.components == other.components

    def __hash__(self):
        return hash(frozenset(self.components.items()))

    def __repr__(self):
        return f"Dimension({self.components})"



class UnitRegistry:
    LENGTH = Dimension({"LENGTH": 1})
    TIME = Dimension({"TIME": 1})
    ANGLE = Dimension({"ANGLE": 1})
    MASS = Dimension({"MASS": 1})

    DIMENSIONLESS = Dimension({})  # No components
    
    def __init__(self, dim_unit_maps: Dict[Dimension, List[Unit]]):
        self.dim_unit_maps = dim_unit_maps

    def get_dropdown_options(self, base_dim: Dimension):
        """
        Return a list of (abbreviation, Unit) tuples suitable for populating a Dropdown widget.
        """
        return self.dim_unit_maps[base_dim]

    def get_unit_by_abbreviation(self, dimension, abbreviation: str) -> Unit:
        units = self.dim_unit_maps[dimension]
        for unit in units:
            if unit.abbreviation == abbreviation:
                return unit
        raise ValueError(f"No unit found with abbreviation '{abbreviation}' for dimension '{dimension}'")
        

    def _base_dim_from_str(self, s: str) -> Dimension:
        """
        Convert a base dimension name like 'LENGTH' / 'length' into the canonical
        Dimension({"LENGTH": 1}) key used in dim_unit_maps.

        Only supports base dimensions that exist in this registry.
        """
        key = s.strip().upper()
        candidate = Dimension({key: 1})

        # If exact key exists, use it
        if candidate in self.dim_unit_maps:
            return candidate

        # Otherwise, try structural match (in case your stored Dimension keys are different objects)
        for d in self.dim_unit_maps:
            if isinstance(d, Dimension) and d == candidate:
                return d

        raise KeyError(f"No units registered for base dimension string: {s!r}")


    def get_unit_for_dimension(
        self,
        dimension: Dimension,
        selected_base_units: Dict[Dimension, Unit]
    ) -> Unit:
        """
        Return the appropriate Unit (either base or composite) for a given Dimension,
        using user-selected base units where provided.
        """
        components = dimension.components

        # If this is a simple base dimension with power 1
        if len(components) == 1:
            base_key, power = next(iter(components.items()))
            if power == 1 and isinstance(base_key, str):
                base_dim = self._base_dim_from_str(base_key)
                return selected_base_units[base_dim]

        # Otherwise, it's composite or has nontrivial powers
        numerators = []
        denominators = []

        for base_dim, power in components.items():
            if isinstance(base_dim, str):
                base_dim = self._base_dim_from_str(base_dim)
            elif isinstance(base_dim, Dimension):
                base_dim = base_dim
            else:
                raise TypeError(f"Invalid dimension component key type: {type(base_dim).__name__}")

            unit = selected_base_units[base_dim]

            if power > 0:
                numerators.extend([unit] * power)
            elif power < 0:
                denominators.extend([unit] * abs(power))

        if not denominators and len(numerators) == 1:
            # Simple base dimension with power 1 (again, fallback case)
            return numerators[0]
        else:
            return CompositeUnit(numerators, denominators)
        
    def __getitem__(self, dim) -> List[Unit]:
        # Direct match (Dimension as key)
        if isinstance(dim, Dimension):
            # Exact key match
            if dim in self.dim_unit_maps:
                return self.dim_unit_maps[dim]

            # Structural match
            for d in self.dim_unit_maps:
                if isinstance(d, Dimension) and d == dim:
                    return self.dim_unit_maps[d]

            raise KeyError(f"No units registered for dimension: {dim}")

        # If passed a string like "Length" / "LENGTH"
        if isinstance(dim, str):
            base_dim = self._base_dim_from_str(dim)
            return self.dim_unit_maps[base_dim]

        raise TypeError(f"Unsupported key type for UnitRegistry: {type(dim).__name__}")

        
unit_registry = UnitRegistry({
    UnitRegistry.LENGTH: [SimpleUnit("meter", "m", 1), SimpleUnit("kilometer", "km", 1000)],
    UnitRegistry.TIME: [SimpleUnit("second", "s", 1), SimpleUnit("day", "day", 86400)],
    UnitRegistry.ANGLE: [SimpleUnit("radian", "rad", 1), SimpleUnit("degree", "deg", 3.141592653589793 / 180)],
    UnitRegistry.MASS: [SimpleUnit("kilogram", "kg", 1)],
    UnitRegistry.DIMENSIONLESS: [SimpleUnit("unitless", "", 1)],
})

Length = unit_registry.LENGTH
Time = unit_registry.TIME
Angle = unit_registry.ANGLE
Mass = unit_registry.MASS
Dimensionless = unit_registry.DIMENSIONLESS
