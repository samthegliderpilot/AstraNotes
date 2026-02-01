import sympy as sy
from astranotes.util.units import Length, Time, Angle, Mass, Dimension, Dimensionless
from astranotes.util.equation_helpers import EquationDefinition
from astranotes.util.source_ref import SourceRef
from astranotes.cheatsheet.common_sources import vallado_4e, bates_mueller_white

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

        return EquationDefinition(eq, "Vis-Viva", "The ballance of potential and kinetic energy of a satellite.", vallado_4e("p. 27, Eq. 1-22"), Length/Time)

    def mean_motion(self)->EquationDefinition:
        """Returns the mean motion of the orbit"""
        n = sy.sqrt(self.mu/self.a**3)
        eq = sy.Eq(sy.Symbol('n', real=True, positive=True), n)
        return EquationDefinition(eq, "Mean Motion", "The rate of mean motion", vallado_4e("p. 45: Eq 2-5"), Angle/Time)

    def orbital_period(self)->EquationDefinition:
        """Returns symbolic form of orbital period"""
        T = 2 * sy.pi * sy.sqrt(self.a**3 / self.mu)
        eq = sy.Eq(sy.Symbol('T'), T)
        return EquationDefinition(eq, "Period", "The time it takes for one orbit to go", bates_mueller_white("p 33: Eq 1.7-9"), Time)

    def orbital_radius(self)->EquationDefinition:
        """Returns symbolic form of orbital radius"""
        R = self.p / (1+self.e*sy.cos(self.true_anomaly))
        eq = sy.Eq(self.r, R)
        return EquationDefinition(eq, "Radius", "The true-anomaly varying radius of the orbit", bates_mueller_white("p. 20: Eq 1.5-4"), Length)

    def circular_velocity(self)->EquationDefinition:
        """Returns symbolic form of circular orbit velocity"""
        v_c = sy.sqrt(self.mu / self.r)
        eq = sy.Eq(sy.Symbol('v_c'), v_c)
        return EquationDefinition(eq, "Velocity (circular)", "The speed of a satellite in a circular orbit", bates_mueller_white('p. 34: Eq 1.8-2'), Length/Time)

    def escape_velocity(self)->EquationDefinition:
        """Returns symbolic form of escape velocity"""
        v_e = sy.sqrt(2 * self.mu / self.r)
        eq = sy.Eq(sy.Symbol('v_{esc}', real=True, positive=True), v_e)
        return EquationDefinition(eq, "Escape Velocity", "The speed a satellite needs to have to escape the central body it is arround. Assumes a parabolic orbit.", bates_mueller_white('p. 35: Eq 1.9-2'), Length/Time)

    def semi_latus_rectum(self)->EquationDefinition:
        """Returns symbolic form of circular orbit velocity"""
        p = self.a * (1 - self.e**2)
        eq = sy.Eq(sy.Symbol('p'), p)
        return EquationDefinition(eq, "Semi-Latus Rectum", "The radius of the orbit at a true anomaly of 90 and 270 degrees.", bates_mueller_white('p. 24: Eq 1.5-6'), Length)

    def velocity_elliptical(self)->EquationDefinition:
        vel = sy.sqrt(self.mu*2/self.r - self.mu/self.a)
        eq = sy.Eq(sy.Symbol('v', real=True, positive=True), vel)
        return EquationDefinition(eq, "Velocity (elliptical)", "The speed of a satellite in an elliptical orbit.", vallado_4e('p. 2'), Length/Time)

    def sin_eccentric_anomaly_wrt_true_anomaly(self) -> EquationDefinition:
        sin_e = sy.sin(self.true_anomaly)*sy.sqrt(1-self.e**2)/(1+self.e*sy.cos(self.true_anomaly))
        sin_e_sy = sy.Symbol('sin(E)', real=True)
        return EquationDefinition(sy.Eq(sin_e_sy, sin_e), "Sin of Eccentric Anomaly", "The sin of the eccentric anomaly", vallado_4e('p. 2'), Dimensionless)

    def cos_eccentric_anomaly_wrt_true_anomaly(self) -> EquationDefinition:
        cos_e = (self.e+sy.cos(self.true_anomaly))/(1+self.e*sy.cos(self.true_anomaly))
        cos_e_sy = sy.Symbol('cos(E)', real=True)
        return EquationDefinition(sy.Eq(cos_e_sy, cos_e), "Cos of Eccentric Anomaly", "The cos of the eccentric anomaly", vallado_4e("p. 2"), Dimensionless)

    def eccentric_anomaly_wrt_true_anomaly(self) -> EquationDefinition:
        ecc_ano = sy.atan2(sy.sin(self.true_anomaly)*sy.sqrt(1-self.e**2), (self.e+sy.cos(self.true_anomaly)))
        ecc_ano_sy = sy.Symbol('E', real=True)
        return EquationDefinition(sy.Eq(ecc_ano_sy, ecc_ano), "Eccentric Anomaly", "The quadrant-checked eccentric anomaly with respect to true anomaly", vallado_4e("Simplified from other expressions"), Angle)

    def radius_of_periapsis(self)-> EquationDefinition:
        e = self.e
        a = self.a
        rp = a * (1-e)
        return EquationDefinition(sy.Eq(sy.Symbol('r_p', real=True, positive=True), rp), "Radius of Periapsis", "The minimum distance between the primary focus of the orbit and the satellite", vallado_4e("p. 2"), Length)

    def radius_of_apoapsis(self)-> EquationDefinition:
        e = self.e
        a = self.a
        ra = a * (1+e)
        return EquationDefinition(sy.Eq(sy.Symbol('r_a', real=True, positive=True), ra), "Radius of Apoapsis", "The maximum distance between the primary focus of the orbit and the satellite", vallado_4e("p. 2"), Length)

    def evaluate_orbital_equations(self, equationDef: EquationDefinition, values_dict: dict)->float:
        """
        Evaluates symbolic equation numerically, using the values_dict
        and symbolic parameters from the OrbitalMechanics instance.
        """

        # Compute and insert p and r if needed
        values_dict[self.p] = self.semi_latus_rectum().expr.rhs.subs(values_dict).evalf()
        if self.r not in values_dict:
            values_dict[self.r] = self.orbital_radius().expr.rhs.subs(values_dict).evalf()

        result = equationDef.evaluate_expr(values_dict)
        return result
