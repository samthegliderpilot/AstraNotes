import sympy as sy
from astrocalc.util.units import Length, Time, Angle, Mass, Dimension
from astrocalc.util.equation_helpers import EquationDefinition

class KeplerianEquations:
    def __init__(self):
        # Define all symbols used in equations
        self.a = sy.Symbol('a', real=True)              # semi-major axis
        self.e = sy.Symbol('e', real=True, positive=True)              # eccentricity
        self.i = sy.Symbol('i', real=True)              # inclination
        self.raan = sy.Symbol('raan', real=True)        # right ascension of ascending node
        self.arg_pe = sy.Symbol('arg_pe', real=True)    # argument of periapsis
        self.true_anomaly = sy.Symbol('\nu', real=True)   # true anomaly (often ν)
        self.mu = sy.Symbol('\mu', real=True, positive=True)             # gravitational parameter
        self.r = sy.Symbol('r', real=True, positive=True)              # radial distance
        self.p = sy.Symbol('p', real=True, positive=True)              # semi-latus rectum (computed from a, e)

    def vis_viva(self) -> EquationDefinition:
        """Returns symbolic form of vis-viva equation"""
        v = sy.sqrt(self.mu * (2/self.r - 1/self.a))
        eq = sy.Eq(sy.Symbol('v'), v)
        return EquationDefinition(eq, "Vis-Viva", "The ballance of potential and kinetic energy of a satellite.", "Fundamentals of Astrodynamics and Applications: 4th Edition: Vallado: Page 27: Eq 1-22", Mass*Length*Length/(Time*Time))

    def mean_motion(self)->EquationDefinition:
        """Returns the mean motion of the orbit"""
        n = sy.sqrt(self.mu/self.a**3)
        eq = sy.Eq(sy.Symbol('n', real=True, positive=True), n)
        return EquationDefinition(eq, "Mean Motion (n)", "The rate of mean motion", "Fundamentals of Astrodynamics and Applications: 4th Edition: Vallado: Page 45: Eq 2-5", Angle/Time)
    
    def orbital_period(self)->EquationDefinition:
        """Returns symbolic form of orbital period"""
        T = 2 * sy.pi * sy.sqrt(self.a**3 / self.mu)
        eq = sy.Eq(sy.Symbol('T'), T)
        return EquationDefinition(eq, "Period (T)", "The time it takes for one orbit to go", "Fundamentals of Astrodynamics: Bates, Muler, White: Page 33: Eq 1.7-9", Time)
    
    def orbital_radius(self)->EquationDefinition:
        """Returns symbolic form of orbital radius"""
        R = self.p / (1+self.e*sy.cos(self.true_anomaly))
        eq = sy.Eq(self.r, R)
        return EquationDefinition(eq, "Radius (r)", "The true-anomaly varying radius of the orbit", "Fundamentals of Astrodynamics: Bates, Muler, White: Page 20: Eq 1.5-4", Length)
                    
    def circular_velocity(self)->EquationDefinition:
        """Returns symbolic form of circular orbit velocity"""
        v_c = sy.sqrt(self.mu / self.r)
        eq = sy.Eq(sy.Symbol('v_c'), v_c)
        return EquationDefinition(eq, "Circular Velocity ($v_{circ}$)", "The speed of a satellite in a circular orbit", "Fundamentals of Astrodynamics: Bates, Muler, White: Page 34: Eq 1.8-2", Length/Time)

    def escape_velocity(self)->EquationDefinition:
        """Returns symbolic form of escape velocity"""
        v_e = sy.sqrt(2 * self.mu / self.r)
        eq = sy.Eq(sy.Symbol('v_{esc}', real=True, positive=True), v_e)
        return EquationDefinition(eq, "Escape Velocity ($v_e$)", "The speed a satellite needs to have to escape the central body it is arround. Assumes a parabolic orbit.", "Fundamentals of Astrodynamics: Bates, Muler, White: Page 35: Eq 1.9-2", Length/Time)

    def semi_latus_rectum(self)->EquationDefinition:
        """Returns symbolic form of circular orbit velocity"""
        p = self.a * (1 - self.e**2)
        eq = sy.Eq(sy.Symbol('p'), p)
        return EquationDefinition(eq, "Semi-Latus Rectum ($p$)", "The radius of the orbit at a true anomaly of 90 and 270 degrees.", "Fundamentals of Astrodynamics: Bates, Muler, White: Page 24: Eq 1.5-6", Length)

    def velocity_elliptical(self)->EquationDefinition:
        vel = sy.sqrt(self.mu*2/self.r - self.mu/self.a)
        eq = sy.Eq(sy.Symbol('v', real=True, positive=True), vel)
        return EquationDefinition(eq, "Velocity (elliptical)", "The speed of a satellite in an elliptical orbit.", "Fundamentals of Astrodynamics and Applications: 4th Edition: Vallado: Page 2", Length/Time)

    def evaluate_orbital_equations(self, equation: sy.Eq, values_dict: dict)->float:
        """
        Evaluates symbolic equation numerically, using the values_dict
        and symbolic parameters from the OrbitalMechanics instance.
        """

        # Compute and insert p and r if needed
        values_dict[self.p] = self.semi_latus_rectum().expr.rhs.subs(values_dict).evalf()
        if self.r not in values_dict:
            values_dict[self.r] = self.orbital_radius().expr.rhs.subs(values_dict).evalf()

        result = equation.rhs.subs(values_dict).evalf()
        return result