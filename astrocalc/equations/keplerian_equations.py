import sympy as sy
from astrocalc.util.units import Length, Time, Angle, Dimension
from astrocalc.util.equation_helpers import EquationDefinition

class KeplerianEquations:
    def __init__(self):
        # Define all symbols used in equations
        self.a = sy.Symbol('a', real=True)              # semi-major axis
        self.e = sy.Symbol('e', real=True, positive=True)              # eccentricity
        self.i = sy.Symbol('i', real=True)              # inclination
        self.raan = sy.Symbol('raan', real=True)        # right ascension of ascending node
        self.arg_pe = sy.Symbol('arg_pe', real=True)    # argument of periapsis
        self.true_anomaly = sy.Symbol('ν', real=True)   # true anomaly (often ν)
        self.mu = sy.Symbol('μ', real=True, positive=True)             # gravitational parameter
        self.r = sy.Symbol('r', real=True, positive=True)              # radial distance
        self.p = sy.Symbol('p', real=True, positive=True)              # semi-latus rectum (computed from a, e)

    def vis_viva(self) -> EquationDefinition:
        """Returns symbolic form of vis-viva equation"""
        v = sy.sqrt(self.mu * (2/self.r - 1/self.a))
        eq = sy.Eq(sy.Symbol('v'), v)
        return EquationDefinition(eq, "Vis-Viva", "The ballance of potential and kinetic energy", "BMW", Length)#TODO: This dimension is wrong

    def mean_motion(self):
        """Returns the mean motion of the orbit"""
        n = sy.sqrt(self.mu/self.a**3)
        eq = sy.Eq(sy.Symbol('n', real=True, positive=True), n)
        return EquationDefinition(eq, "Mean Motion (n)", "The rate of mean motion", "BMW", Angle/Time)
    
    def orbital_period(self):
        """Returns symbolic form of orbital period"""
        T = 2 * sy.pi * sy.sqrt(self.a**3 / self.mu)
        eq = sy.Eq(sy.Symbol('T'), T)
        return EquationDefinition(eq, "Period (P)", "The time it takes for one orbit to go", "BMW", Time)
    
    def orbital_radius(self):
        """Returns symbolic form of orbital radius"""
        R = self.p / (1+self.e*sy.cos(self.true_anomaly))
        eq = sy.Eq(self.r, R)
        return EquationDefinition(eq, "Radius (r)", "The true-anomaly varying radius of the orbit", "BMW", Length)
                    
    def circular_velocity(self):
        """Returns symbolic form of circular orbit velocity"""
        v_c = sy.sqrt(self.mu / self.r)
        eq = sy.Eq(sy.Symbol('v_c'), v_c)
        return EquationDefinition(eq, "Circular Velocity (v_{circ})", "The speed of a satellite in a circular orbit", "BMW", Length/Time)

    def escape_velocity(self):
        """Returns symbolic form of escape velocity"""
        v_e = sy.sqrt(2 * self.mu / self.r)
        eq = sy.Eq(sy.Symbol('v_e'), v_e)
        return EquationDefinition(eq, "Escape Velocity (v_e)", "The speed a satellite needs to have to escape the central body it is arround", "BMW", Length/Time)

    def evaluate_orbital_equations(self, equation: sy.Eq, values_dict: dict)->float:
        """
        Evaluates symbolic equation numerically, using the values_dict
        and symbolic parameters from the OrbitalMechanics instance.
        """

        # Compute and insert p and r if needed
        if self.p not in values_dict:
            a_val = values_dict[self.a]
            e_val = values_dict[self.e]
            values_dict[self.p] = a_val * (1 - e_val**2)
        if self.r not in values_dict:
            a_val = values_dict[self.a]
            e_val = values_dict[self.e]
            values_dict[self.r] = self.orbital_radius().expr.rhs.subs(values_dict).evalf()

        result = equation.rhs.subs(values_dict).evalf()
        return result