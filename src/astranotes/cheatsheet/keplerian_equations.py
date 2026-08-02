import sympy as sy
from typing import List, Dict
from functools import cached_property
import math
from astranotes.util.units import Length, Time, Angle, Mass, Dimension, Dimensionless
from astranotes.util.equation_helpers import EquationDefinition
from astranotes.util.source_ref import SourceRef
from astranotes.cheatsheet.common_sources import vallado_4e, bates_mueller_white, degenerate_conic_mee

class KeplerianEquations:
    def __init__(self):
        # Define all symbols used in equations
        self.a = sy.Symbol('a', real=True)              # semi-major axis
        self.e = sy.Symbol('e', real=True, positive=True)              # eccentricity
        self.i = sy.Symbol('i', real=True)              # inclination
        self.raan = sy.Symbol(r'\Omega', real=True)        # right ascension of ascending node
        self.arg_pe = sy.Symbol(r'\omega', real=True)    # argument of periapsis
        self.true_anomaly = sy.Symbol(r'\nu', real=True)   # true anomaly (often ν)
        self.mu = sy.Symbol(r'\mu', real=True, positive=True)             # gravitational parameter

        self.r_sy = sy.Symbol('r', real=True, positive=True)              # radial distance
        self.p_sy = sy.Symbol('p', real=True, positive=True)              # semi-latus rectum (computed from a, e)
        self.flight_path_angle_sy = sy.Symbol(r'\gamma', real=True) # flight path angle
        self.eccentric_anomaly_sy = sy.Symbol('E', real=True) # eccentric anomaly
        self.velocity_sy = sy.Symbol('v', real=True, positive=True)
        self.vis_viva_sy = sy.Symbol('v', real=True, positive=True) #TODO, needs to be a different letter
        self.mean_motion_sy = sy.Symbol('n', real=True, positive=True)
        self.orbital_period_sy = sy.Symbol('T', real=True, positive=True)
        self.velocity_circular_sy = sy.Symbol('v_c', real=True, positive=True)
        self.velocity_escape_sy = sy.Symbol('v_{esc}', real=True, positive=True)
        self.radius_of_periapsis_sy = sy.Symbol('r_p', real=True, positive=True)
        self.parabolic_anomaly_sy = sy.Symbol('B', real=True)
        self.hyperbolic_anomaly_sy = sy.Symbol('H', real=True)
        self.mean_anomaly_sy = sy.Symbol('M', real=True)
        self.angular_momentum_sy = sy.Symbol('h', real=True, positive=True)
        self.perifocal_radius_sy = sy.MatrixSymbol(r'\mathbf{r}_{PQW}', 3, 1)
        self.perifocal_velocity_sy = sy.MatrixSymbol(r'\mathbf{v}_{PQW}', 3, 1)
        self.peri_to_inert_mat_sy = sy.MatrixSymbol(r"[\frac{IJK}{PQW}]", 3, 3)
        self.inertial_radius_sy = sy.MatrixSymbol("r_{IJK}", 3, 1)
        self.true_anomaly_rate_sy = sy.Symbol(r'\dot{\nu}', real= True)
        self.radial_rate_sy = sy.Symbol('\dot{r}', real=True)

    @cached_property
    def vis_viva(self) -> EquationDefinition:
        """Returns symbolic form of vis-viva equation"""
        v = sy.sqrt(self.mu * (2/self.r_sy - 1/self.a))
        eq = sy.Eq(self.vis_viva_sy, v)

        return EquationDefinition(eq, "Vis-Viva", "The balance of potential and kinetic energy of a satellite.", vallado_4e("p. 27, Eq. 1-22"), Length/Time)

    @cached_property
    def orbital_energy(self) -> EquationDefinition:
        """Returns symbolic form of specific mechanical (orbital) energy"""
        lhs = sy.Symbol(r'\varepsilon', real=True)
        rhs = -1*self.mu/(2*self.a)
        form1 = (self.velocity_sy**2)/2 - self.mu/self.r_sy
        return EquationDefinition(sy.Eq(lhs, rhs), "Specific Orbital Energy", "The sum of kinetic and potential energy per unit mass; constant along the orbit.", vallado_4e("p. 2"), Length*Length/(Time*Time), (form1,))

    @cached_property
    def c3(self) -> EquationDefinition:
        """Returns symbolic form of characteristic energy"""
        lhs = sy.Symbol('C_3', real=True)
        rhs = -1*self.mu/self.a
        return EquationDefinition(sy.Eq(lhs, rhs), "Characteristic Energy", "Twice the specific orbital energy; the excess energy over escape for a hyperbolic departure.", vallado_4e("p. 27"), Length*Length/(Time*Time))

    @cached_property
    def mean_motion(self)->EquationDefinition:
        """Returns the mean motion of the orbit"""
        n = sy.sqrt(self.mu/self.a**3)
        eq = sy.Eq(self.mean_motion_sy, n)
        return EquationDefinition(eq, "Mean Motion", "The rate of mean motion", vallado_4e("p. 45: Eq 2-5"), Angle/Time)

    @cached_property
    def orbital_period(self)->EquationDefinition:
        """Returns symbolic form of orbital period"""
        T = 2 * sy.pi * sy.sqrt(self.a**3 / self.mu)
        eq = sy.Eq(self.orbital_period_sy, T)
        return EquationDefinition(eq, "Period", "The time to complete one full orbit.", bates_mueller_white("p 33: Eq 1.7-9"), Time)

    @cached_property
    def orbital_radius(self)->EquationDefinition:
        """Returns symbolic form of orbital radius"""
        R = self.p_sy / (1+self.e*sy.cos(self.true_anomaly))
        eq = sy.Eq(self.r_sy, R)
        return EquationDefinition(eq, "Radius", "The true-anomaly varying radius of the orbit", bates_mueller_white("p. 20: Eq 1.5-4"), Length)

    @cached_property
    def circular_velocity(self)->EquationDefinition:
        """Returns symbolic form of circular orbit velocity"""
        v_c = sy.sqrt(self.mu / self.r_sy)
        eq = sy.Eq(self.velocity_circular_sy, v_c)
        return EquationDefinition(eq, "Velocity (circular)", "The speed of a satellite in a circular orbit", bates_mueller_white('p. 34: Eq 1.8-2'), Length/Time)

    @cached_property
    def escape_velocity(self)->EquationDefinition:
        """Returns symbolic form of escape velocity"""
        v_e = sy.sqrt(2 * self.mu / self.r_sy)
        eq = sy.Eq(self.velocity_escape_sy, v_e)
        return EquationDefinition(eq, "Escape Velocity", "The speed a satellite needs to escape the central body. Assumes a parabolic orbit.", bates_mueller_white('p. 35: Eq 1.9-2'), Length/Time)

    @cached_property
    def hyperbolic_excess_velocity(self) -> EquationDefinition:
        lhs = sy.Symbol(r'v_{\infty}', real=True, positive=True)
        rhs = sy.sqrt(-1*self.mu/self.a) # remember for a hyperbolic orbit, a is negative
        return EquationDefinition(sy.Eq(lhs, rhs), "Hyperbolic Excess Velocity", "The speed remaining at infinite distance for a hyperbolic orbit.", vallado_4e("p. 26"), Length/Time)

    @cached_property
    def semi_latus_rectum(self)->EquationDefinition:
        """Returns symbolic form of the semi-latus rectum"""
        p = self.a * (1 - self.e**2)
        eq = sy.Eq(self.p_sy, p)
        return EquationDefinition(eq, "Semi-Latus Rectum", "The radius of the orbit at a true anomaly of 90 and 270 degrees.", bates_mueller_white('p. 24: Eq 1.5-6'), Length)

    @cached_property
    def semi_minor_axis(self)->EquationDefinition:
        b = self.a * sy.sqrt(1 - self.e**2)
        eq = sy.Eq(sy.Symbol('b', real=True, positive=True), b)
        return EquationDefinition(eq, "Semi-Minor Axis", "The half-width of the orbit ellipse, perpendicular to the major axis.", bates_mueller_white('p. 15: Eq 1.4'), Length)

    @cached_property
    def velocity_magnitude(self)->EquationDefinition:
        vel = sy.sqrt(self.mu*2/self.r_sy - self.mu/self.a)
        eq = sy.Eq(self.velocity_sy, vel)
        return EquationDefinition(eq, "Velocity (elliptical)", "The speed of a satellite in an elliptical orbit.", vallado_4e('p. 2'), Length/Time)

    @cached_property
    def sin_eccentric_anomaly_wrt_true_anomaly(self) -> EquationDefinition:
        sin_e = sy.sin(self.true_anomaly)*sy.sqrt(1-self.e**2)/(1+self.e*sy.cos(self.true_anomaly))
        sin_e_sy = sy.Symbol('sin(E)', real=True)
        return EquationDefinition(sy.Eq(sin_e_sy, sin_e), "Sin of Eccentric Anomaly", "The sin of the eccentric anomaly", vallado_4e('p. 2'), Dimensionless)

    @cached_property
    def cos_eccentric_anomaly_wrt_true_anomaly(self) -> EquationDefinition:
        cos_e = (self.e+sy.cos(self.true_anomaly))/(1+self.e*sy.cos(self.true_anomaly))
        cos_e_sy = sy.Symbol('cos(E)', real=True)
        return EquationDefinition(sy.Eq(cos_e_sy, cos_e), "Cos of Eccentric Anomaly", "The cos of the eccentric anomaly", vallado_4e("p. 2"), Dimensionless)

    @cached_property
    def eccentric_anomaly_wrt_true_anomaly(self) -> EquationDefinition:
        ecc_ano = sy.atan2(sy.sin(self.true_anomaly)*sy.sqrt(1-self.e**2), (self.e+sy.cos(self.true_anomaly)))
        return EquationDefinition(sy.Eq(self.eccentric_anomaly_sy, ecc_ano), "Eccentric Anomaly", "The quadrant-checked eccentric anomaly with respect to true anomaly", vallado_4e("Simplified from other expressions"), Angle)

    @cached_property
    def true_anomaly_wrt_eccentric_anomaly(self) -> EquationDefinition:
        true_ano = sy.atan2(sy.sin(self.eccentric_anomaly_sy)*sy.sqrt(1-self.e**2), (sy.cos(self.eccentric_anomaly_sy)-self.e))
        return EquationDefinition(sy.Eq(self.true_anomaly, true_ano), "True Anomaly", "The quadrant-checked true anomaly with respect to eccentric anomaly", vallado_4e("Simplified from other expressions"), Angle)

    @cached_property
    def parabolic_anomaly_wrt_true_anomaly(self) -> EquationDefinition:
        par_ano = sy.atan(sy.sin(self.true_anomaly/2))
        return EquationDefinition(sy.Eq(self.parabolic_anomaly_sy, par_ano), "Parabolic Anomaly", "The parabolic anomaly with respect to true anomaly", vallado_4e("p. 2"), Angle)

    @cached_property
    def sin_hyperbolic_anomaly_wrt_true_anomaly(self) -> EquationDefinition:
        sin_e = sy.sinh(self.true_anomaly)*sy.sqrt(self.e**2-1)/(1+self.e*sy.cosh(self.true_anomaly))
        sin_e_sy = sy.Symbol('sinh(H)', real=True)
        return EquationDefinition(sy.Eq(sin_e_sy, sin_e), "Sin of Hyperbolic Anomaly", "The sin of the hyperbolic anomaly", vallado_4e('p. 2'), Dimensionless)

    @cached_property
    def cos_hyperbolic_anomaly_wrt_true_anomaly(self) -> EquationDefinition:
        cos_e = (self.e+sy.cosh(self.true_anomaly))/(1+self.e*sy.cosh(self.true_anomaly))
        cos_e_sy = sy.Symbol('cosh(H)', real=True)
        return EquationDefinition(sy.Eq(cos_e_sy, cos_e), "Cos of Hyperbolic Anomaly", "The cos of the hyperbolic anomaly", vallado_4e("p. 2"), Dimensionless)

    @cached_property
    def hyperbolic_anomaly_wrt_true_anomaly(self) -> EquationDefinition:
        ecc_ano = sy.atan2(sy.sinh(self.true_anomaly)*sy.sqrt(self.e**2-1), (self.e+sy.cosh(self.true_anomaly)))
        return EquationDefinition(sy.Eq(self.hyperbolic_anomaly_sy, ecc_ano), "Hyperbolic Anomaly", "The hyperbolic anomaly with respect to true anomaly", vallado_4e("Simplified from other expressions"), Angle)


    @cached_property
    def radius_of_periapsis(self)-> EquationDefinition:
        e = self.e
        a = self.a
        rp = a * (1-e)
        return EquationDefinition(sy.Eq(self.radius_of_periapsis_sy, rp), "Radius of Periapsis", "The minimum distance between the primary focus of the orbit and the satellite", vallado_4e("p. 2"), Length)

    @cached_property
    def radius_of_apoapsis(self)-> EquationDefinition:
        e = self.e
        a = self.a
        ra = a * (1+e)
        return EquationDefinition(sy.Eq(sy.Symbol('r_a', real=True, positive=True), ra), "Radius of Apoapsis", "The maximum distance between the primary focus of the orbit and the satellite", vallado_4e("p. 2"), Length)

    @cached_property
    def sin_flight_path_angle_wrt_eccentric_anomaly(self) -> EquationDefinition:
        e = self.e
        sin_fpa = e*sy.sin(self.eccentric_anomaly_sy)/(1-(e**2)*sy.cos(self.true_anomaly)**2)
        sin_fpa_sy = sy.Symbol(r'sin(\gamma)', real=True)
        return EquationDefinition(sy.Eq(sin_fpa_sy, sin_fpa), "Sin of Flight Path Angle", "The sin of the flight path angle", vallado_4e('p. 2'), Dimensionless)

    @cached_property
    def cos_flight_path_angle_wrt_eccentric_anomaly(self) -> EquationDefinition:
        e = self.e
        cos_fpa = (1-e**2)/(1-(e**2)*sy.cos(self.true_anomaly)**2)
        cos_fla_sy = sy.Symbol(r'cos(\gamma)', real=True)
        return EquationDefinition(sy.Eq(cos_fla_sy, cos_fpa), "Cos of Flight Path Angle", "The cos of the flight path angle", vallado_4e("p. 2"), Dimensionless)

    @cached_property
    def flight_path_angle_wrt_eccentric_anomaly(self) -> EquationDefinition:
        e = self.e
        flight_path_angle = sy.atan2(e*sy.sin(self.eccentric_anomaly_sy), (1-e**2))
        fpaSy = self.flight_path_angle_sy
        return EquationDefinition(sy.Eq(fpaSy, flight_path_angle), "Flight Path Angle", "The quadrant-checked flight path angle with respect to the the eccentric anomaly", vallado_4e("Simplified from other expressions"), Angle)

    @cached_property
    def flight_path_angle_parabolic(self) -> EquationDefinition:
        lhs = self.flight_path_angle_sy
        flight_path_angle = self.true_anomaly/2
        return EquationDefinition(sy.Eq(lhs, flight_path_angle), "Flight Path Angle - Parabolic", "The flight path angle with respect to the the parabolic anomaly", vallado_4e("p. 2"), Angle)

    @cached_property
    def angular_momentum(self)-> EquationDefinition:
        expr = sy.sqrt(self.mu* self.p_sy)
        form1 = self.r_sy*self.velocity_sy*sy.cos(self.flight_path_angle_sy)
        equ_def = EquationDefinition(sy.Eq(self.angular_momentum_sy, expr), "Specific Angular Momentum", "The magnitude of the angular momentum vector", vallado_4e("p. 2"), Length*Length/Time, (form1,))
        return equ_def

    @cached_property
    def mean_anomaly_elliptical(self) -> EquationDefinition:
        return EquationDefinition(sy.Eq(self.mean_anomaly_sy, self.eccentric_anomaly_sy - self.e*sy.sin(self.eccentric_anomaly_sy)), "Mean Anomaly (Elliptical)", "The time-based angle around the orbit", vallado_4e("p. 2"), Angle)

    @cached_property
    def mean_anomaly_hyperbolic(self) -> EquationDefinition:
        return EquationDefinition(sy.Eq(self.mean_anomaly_sy, self.e*sy.sinh(self.hyperbolic_anomaly_sy) - self.hyperbolic_anomaly_sy), "Mean Anomaly (Hyperbolic)", "The time-based angle around the orbit", vallado_4e("p. 2"), Angle)

    @cached_property
    def semi_latus_rectum_parabolic(self)->EquationDefinition:
        return EquationDefinition(sy.Eq(self.p_sy, (self.angular_momentum_sy**2)/self.mu), "Semi-Latus Rectum (Parabolic)", "The semi-parameter for parabolic orbits", vallado_4e("p. 3"), Length)

    @cached_property
    def perifocal_radius_vector(self)->EquationDefinition:
        p = self.p_sy
        ta = self.true_anomaly
        e = self.e

        r_per = sy.Matrix([
            p*sy.cos(ta)/(1+e*sy.cos(ta)),
            p*sy.sin(ta)/(1+e*sy.cos(ta)),
            0
        ])
        return EquationDefinition(sy.Eq(self.perifocal_radius_sy, r_per), "Perifocal Radius", "The radius vector of the satellite in the orbit plane of the satellite", vallado_4e("2-104"), Length)

    @cached_property
    def perifocal_velocity_vector(self)->EquationDefinition:
        p = self.p_sy
        ta = self.true_anomaly
        e = self.e
        mu = self.mu

        v_per = sy.Matrix([
            -1*sy.sqrt(mu/p)*sy.sin(ta),
            sy.sqrt(mu/p)*(e+sy.cos(ta)),
            0
        ])
        return EquationDefinition(sy.Eq(self.perifocal_velocity_sy, v_per), "Perifocal Velocity", "The velocity vector of the satellite in the orbit plane of the satellite", vallado_4e("2-106"), Length/Time)

    @cached_property
    def perifocal_to_inertial_rotation_matrix(self)->EquationDefinition:
        cr = sy.cos(self.raan)
        ca = sy.cos(self.arg_pe)
        ci = sy.cos(self.i)

        sr = sy.sin(self.raan)
        sa = sy.sin(self.arg_pe)
        si = sy.sin(self.i)

        rhs = sy.Matrix([[cr*ca-sr*sa*ci, -1*cr*sa-sr*ca*ci,  sr*si],
                        [sr*ca+cr*sa*ci, -1*sr*sa+cr*ca*ci, -1*cr*si],
                        [sa*si,           ca*si,           ci]])
        return EquationDefinition(sy.Eq(self.peri_to_inert_mat_sy, rhs), "Perifocal to Inertial Rotation Matrix", "The rotation matrix to convert a vector in the perifocal coordinate system to an inertial coordinate system", vallado_4e("Algorithm 10, page 119"), Dimensionless)

    @cached_property
    def inertial_radius_vector(self)->EquationDefinition:
        lhs = self.inertial_radius_sy
        rhs = self.peri_to_inert_mat_sy * self.perifocal_radius_sy
        return EquationDefinition(sy.Eq(lhs, rhs), "Radius Vector: Inertial", "The inertial radius vector", vallado_4e("Algorithm 10, page 119"), Length)

    @cached_property
    def inertial_velocity_vector(self)->EquationDefinition:
        lhs = sy.MatrixSymbol("v_{IJK}", 3, 1)
        rhs = self.peri_to_inert_mat_sy * self.perifocal_velocity_sy
        return EquationDefinition(sy.Eq(lhs, rhs), "Velocity Vector: Inertial", "The inertial velocity vector", vallado_4e("Algorithm 10, page 119"), Length/Time)

    @cached_property
    def two_body_differential_equation(self) -> EquationDefinition:
        lhs = sy.MatrixSymbol(r'\ddot{\hat{r}}', 3, 1)
        rhs = -1*self.mu * self.inertial_radius_sy/(self.r_sy**3)
        return EquationDefinition(sy.Eq(lhs, rhs), "Two Body Differential Equation", "The inertial acceleration of a satellite in a gravity field", vallado_4e("1-14, page 23"), Length/(Time*Time))

    @cached_property
    def equinoctial_ecc_cos_term(self) -> EquationDefinition:
        lhs = sy.Symbol("f", real=True)
        rhs = self.e*sy.cos(self.arg_pe+self.raan)
        return EquationDefinition(sy.Eq(lhs, rhs), "Equinoctial Eccentrity Cosine Term", "The cosine term for the eccentricity term", degenerate_conic_mee(), Dimensionless)

    @cached_property
    def equinoctial_ecc_sin_term(self) -> EquationDefinition:
        lhs = sy.Symbol("g", real=True)
        rhs = self.e*sy.sin(self.arg_pe+self.raan)
        return EquationDefinition(sy.Eq(lhs, rhs), "Equinoctial Eccentrity Sine Term", "The sine term for the eccentricity term", degenerate_conic_mee(), Dimensionless)

    @cached_property
    def equinoctial_inc_cos_term(self) -> EquationDefinition:
        lhs = sy.Symbol("h", real=True)
        rhs = sy.tan(self.i/2)*sy.cos(self.raan)
        return EquationDefinition(sy.Eq(lhs, rhs), "Equinoctial Inclination Cosine Term", "The cosine term for the inclination term", degenerate_conic_mee(), Dimensionless)

    @cached_property
    def equinoctial_inc_sin_term(self) -> EquationDefinition:
        lhs = sy.Symbol("k", real=True)
        rhs = sy.tan(self.i/2)*sy.sin(self.raan)
        return EquationDefinition(sy.Eq(lhs, rhs), "Equinoctial Inclination Sine Term", "The sine term for the inclination term", degenerate_conic_mee(), Dimensionless)

    @cached_property
    def argument_of_latitude(self) -> EquationDefinition:
        lhs = sy.Symbol('u', real=True)
        rhs = self.arg_pe + self.true_anomaly
        return EquationDefinition(sy.Eq(lhs, rhs), "Argument of Latitude", "The angle from the ascending node to the satellite, measured in the orbit plane.", vallado_4e("2-90 p. 102"), Angle)

    @cached_property
    def mean_longitude(self) -> EquationDefinition:
        lhs = sy.Symbol('L', real=True)
        rhs = self.raan + self.arg_pe + self.true_anomaly
        return EquationDefinition(sy.Eq(lhs, rhs), "Mean Longitude", "The inertial longitude", degenerate_conic_mee(), Angle)

    @cached_property
    def true_anomaly_rate(self) -> EquationDefinition:
        lhs = self.true_anomaly_rate_sy
        rhs = self.mean_motion_sy*self.a*self.a*sy.sqrt(1-self.e**2)/(self.r_sy**2)
        return EquationDefinition(sy.Eq(lhs, rhs), "True Anomaly Rate", "The instantaneous rate of change of true anomaly", vallado_4e("p. 2"), Angle/Time)

    @cached_property
    def radial_rate(self) -> EquationDefinition:
        lhs = self.radial_rate_sy
        rhs = self.r_sy*self.true_anomaly_rate_sy*self.e*sy.sin(self.true_anomaly)/(1+self.e*sy.cos(self.true_anomaly))
        return EquationDefinition(sy.Eq(lhs, rhs), "Radial Rate", "The instantaneous rate of change of distance between the center and the satellite", vallado_4e("p. 2"), Length/Time)

    @cached_property
    def hyperbolic_turning_angle(self)->EquationDefinition:
        lhs = sy.Symbol(r'\epsilon', real=True)
        rhs = 2*sy.asin(1/self.e)
        return EquationDefinition(sy.Eq(lhs, rhs), "Hyperbolic Turning Angle", "The angle made by the asymotopes of a hyperbolic orbit", vallado_4e("2-28"), Angle)

    @cached_property
    def delaunay_l(self) -> EquationDefinition:
        lhs = sy.Symbol('L_d', real=True, positive=True)
        rhs = sy.sqrt(self.mu*self.a)
        return EquationDefinition(sy.Eq(lhs, rhs), "Delaunay L", "The L value for Delaunay elements", vallado_4e("2-102"), Length*Length/Time)

    @cached_property
    def delaunay_h(self) -> EquationDefinition:
        lhs = sy.Symbol('H_d', real=True)
        rhs = sy.sqrt(self.mu*self.a*(1-self.e**2))*sy.cos(self.i)
        return EquationDefinition(sy.Eq(lhs, rhs), "Delauny H", "The H value for Delaunay elements", vallado_4e("2-102"), Length*Length/Time)

    def evaluate_my_equations(self, initial_values_dict : Dict[sy.Symbol, float]) -> Dict[EquationDefinition, float]:
        values_dict = initial_values_dict.copy()
        evaluated_values = {}

        ecc = values_dict[self.e]

        if ecc < 0.99999 and ecc >  1.00001:
            values_dict[self.p_sy] = self.semi_latus_rectum_parabolic.evaluate_expr(values_dict)
        else:
            values_dict[self.p_sy] = self.semi_latus_rectum.evaluate_expr(values_dict)

        evaluated_values[self.semi_latus_rectum] = values_dict[self.p_sy]

        values_dict[self.r_sy] = self.orbital_radius.evaluate_expr(values_dict)
        evaluated_values[self.orbital_radius] = values_dict[self.r_sy]

        values_dict[self.eccentric_anomaly_sy] = self.eccentric_anomaly_wrt_true_anomaly.evaluate_expr(values_dict)

        values_dict[self.velocity_sy] = self.velocity_magnitude.evaluate_expr(values_dict)
        evaluated_values[self.velocity_magnitude] = values_dict[self.velocity_sy]

        values_dict[self.flight_path_angle_sy] = self.flight_path_angle_wrt_eccentric_anomaly.evaluate_expr(values_dict)


        evaluated_values[self.orbital_radius] = self.orbital_radius.evaluate_expr(values_dict)
        evaluated_values[self.circular_velocity] = self.circular_velocity.evaluate_expr(values_dict)
        evaluated_values[self.escape_velocity] = self.escape_velocity.evaluate_expr(values_dict)
        evaluated_values[self.vis_viva] = self.vis_viva.evaluate_expr(values_dict)
        evaluated_values[self.mean_motion] = self.mean_motion.evaluate_expr(values_dict)
        values_dict[self.mean_motion_sy] = evaluated_values[self.mean_motion]
        evaluated_values[self.angular_momentum] = self.angular_momentum.evaluate_expr(values_dict)
        evaluated_values[self.radius_of_periapsis] = self.radius_of_periapsis.evaluate_expr(values_dict)

        evaluated_values[self.true_anomaly_rate] = self.true_anomaly_rate.evaluate_expr(values_dict)
        values_dict[self.true_anomaly_rate_sy] = evaluated_values[self.true_anomaly_rate]
        evaluated_values[self.radial_rate] = self.radial_rate.evaluate_expr(values_dict)

        evaluated_values[self.delaunay_l] = self.delaunay_l.evaluate_expr(values_dict)
        evaluated_values[self.delaunay_h] = self.delaunay_h.evaluate_expr(values_dict)

        evaluated_values[self.orbital_energy] = self.orbital_energy.evaluate_expr(values_dict)
        evaluated_values[self.c3] = self.c3.evaluate_expr(values_dict)
        evaluated_values[self.hyperbolic_excess_velocity] = self.hyperbolic_excess_velocity.evaluate_expr(values_dict)
        evaluated_values[self.semi_minor_axis] = self.semi_minor_axis.evaluate_expr(values_dict)
        evaluated_values[self.argument_of_latitude] = self.argument_of_latitude.evaluate_expr(values_dict)
        evaluated_values[self.true_anomaly_wrt_eccentric_anomaly] = self.true_anomaly_wrt_eccentric_anomaly.evaluate_expr(values_dict)


        if ecc < 0.99999:
            evaluated_values[self.radius_of_apoapsis] = self.radius_of_apoapsis.evaluate_expr(values_dict)
            evaluated_values[self.orbital_period] = self.orbital_period.evaluate_expr(values_dict)
            evaluated_values[self.eccentric_anomaly_wrt_true_anomaly] = self.eccentric_anomaly_wrt_true_anomaly.evaluate_expr(values_dict)
            evaluated_values[self.flight_path_angle_wrt_eccentric_anomaly] = self.flight_path_angle_wrt_eccentric_anomaly.evaluate_expr(values_dict)
            evaluated_values[self.mean_anomaly_elliptical] = self.mean_anomaly_elliptical.evaluate_expr(values_dict)
        elif ecc <=0.99999 and ecc > 1.00001:
            evaluated_values[self.radius_of_apoapsis] = math.nan
            evaluated_values[self.eccentric_anomaly_wrt_true_anomaly] = self.parabolic_anomaly_wrt_true_anomaly.evaluate_expr(values_dict)
            evaluated_values[self.parabolic_anomaly_wrt_true_anomaly] = evaluated_values[self.eccentric_anomaly_wrt_true_anomaly]
            evaluated_values[self.flight_path_angle_parabolic] = self.flight_path_angle_parabolic.evaluate_expr(values_dict)

        else: # greater than 1, hyperbolic
            evaluated_values[self.radius_of_apoapsis] = math.nan

            values_dict[self.hyperbolic_anomaly_sy] = self.hyperbolic_anomaly_wrt_true_anomaly.evaluate_expr(values_dict)
            evaluated_values[self.eccentric_anomaly_wrt_true_anomaly] = values_dict[self.hyperbolic_anomaly_sy]
            evaluated_values[self.hyperbolic_anomaly_wrt_true_anomaly] = evaluated_values[self.eccentric_anomaly_wrt_true_anomaly]
            evaluated_values[self.flight_path_angle_wrt_eccentric_anomaly] = self.flight_path_angle_wrt_eccentric_anomaly.evaluate_expr(values_dict)
            evaluated_values[self.mean_anomaly_hyperbolic] = self.mean_anomaly_hyperbolic.evaluate_expr(values_dict)
            evaluated_values[self.hyperbolic_turning_angle] = self.hyperbolic_turning_angle.evaluate_expr(values_dict)

        evaluated_values[self.perifocal_radius_vector] = self.perifocal_radius_vector.evaluate_expr(values_dict)
        evaluated_values[self.perifocal_velocity_vector] = self.perifocal_velocity_vector.evaluate_expr(values_dict)
        values_dict[self.perifocal_radius_sy] = evaluated_values[self.perifocal_radius_vector]
        values_dict[self.perifocal_velocity_sy] = evaluated_values[self.perifocal_velocity_vector]
        evaluated_values[self.perifocal_to_inertial_rotation_matrix] = self.perifocal_to_inertial_rotation_matrix.evaluate_expr(values_dict)
        values_dict[self.peri_to_inert_mat_sy] = evaluated_values[self.perifocal_to_inertial_rotation_matrix]

        evaluated_values[self.inertial_radius_vector] = self.inertial_radius_vector.evaluate_expr(values_dict)
        evaluated_values[self.inertial_velocity_vector] = self.inertial_velocity_vector.evaluate_expr(values_dict)
        values_dict[self.inertial_radius_sy] = evaluated_values[self.inertial_radius_vector]

        evaluated_values[self.two_body_differential_equation] = self.two_body_differential_equation.evaluate_expr(values_dict)

        evaluated_values[self.equinoctial_ecc_cos_term] = self.equinoctial_ecc_cos_term.evaluate_expr(values_dict)
        evaluated_values[self.equinoctial_ecc_sin_term] = self.equinoctial_ecc_sin_term.evaluate_expr(values_dict)
        evaluated_values[self.equinoctial_inc_cos_term] = self.equinoctial_inc_cos_term.evaluate_expr(values_dict)
        evaluated_values[self.equinoctial_inc_sin_term] = self.equinoctial_inc_sin_term.evaluate_expr(values_dict)
        evaluated_values[self.mean_longitude] = self.mean_longitude.evaluate_expr(values_dict)

        return evaluated_values

    def evaluate_orbital_equations(self, equationDef: EquationDefinition, values_dict: Dict[sy.Symbol, float])->float:
        """
        Evaluates symbolic equation numerically, using the values_dict
        and symbolic parameters from the OrbitalMechanics instance.
        """

        result = equationDef.evaluate_expr(values_dict)
        return result
