import json
import warnings
from sisopy31 import *
import math

from src.flight_dynamics.ShortPeriod import ShortPeriod


class Params:
    with open('src/assets/params.json') as f:
        p = json.load(f)


class AircraftStability(Params):

    def __init__(self):
        # ------------------- Import aircraft parameters   -------------------
        super().__init__()
        # ------------------- Initialization -------------------
        self.Veq = self.p['Mach']['value'] * 340.29
        self.Q = 1 / 2 * 0.702 * self.Veq ** 2
        self.eps = 10 ** -5

        # ------------------- Aircraft X and Y -------------------
        Xf = - self.p['f']['value'] * self.p['lt']['value']
        Xg = - self.p['c']['value'] * self.p['lt']['value']
        Xf_delta = - self.p['f_delta']['value'] * self.p['lt']['value']

        self.X = Xf - Xg
        self.Y = Xf_delta - Xg

        # ------------------- Loop init -------------------
        self.alpha_eq_prev = 0
        self.alpha_eq = 1
        self.Fpx_eq = 0

        # ------------------- Aircraft Cz, Cx -------------------
        self.Cz_eq = None
        self.Cx_eq = None
        self.Cx_delta_m = None




    def compute_equilibrium(self):
        count = 0
        while abs(self.alpha_eq - self.alpha_eq_prev) >= self.eps:
            self.Cz_eq = (1 / (self.Q * self.p['S']['value'])) * (
                    self.p['m']['value'] * self.p['g']['value'] - math.sin(self.alpha_eq_prev) * self.Fpx_eq)
            self.Cx_eq = self.p['Cx0']['value'] + self.p['k']['value'] * (self.Cz_eq ** 2)
            self.Cx_delta_m = 2 * self.p['k']['value'] * self.Cz_eq * self.p['Cz_delta_m']['value']
            delta_m_eq = self.p['delta_m0']['value'] - (
                    (self.Cx_eq * math.sin(self.alpha_eq_prev) + self.Cz_eq * math.cos(self.alpha_eq_prev)) / (
                    self.Cx_delta_m * math.sin(self.alpha_eq_prev) + self.p['Cz_delta_m']['value'] * math.cos(
                self.alpha_eq_prev))) * (
                                 self.X / (self.Y - self.X))

            self.alpha_eq_prev = self.alpha_eq
            self.alpha_eq = self.p['alpha_0']['value'] + (self.Cz_eq / self.p['Cz_alpha']['value']) - (
                    self.p['Cz_delta_m']['value'] / self.p['Cz_alpha']['value']) * delta_m_eq
            self.Fpx_eq = self.Q * self.p['S']['value'] * self.Cx_eq / math.cos(self.alpha_eq)
            count += 1

        print("Equilibrium point found in {} iterations:\n> {}".format(count, self.alpha_eq))
        return self.alpha_eq


class StateSpaceModel(Params):

    def __init__(self, aircraft: AircraftStability):

        self.aircraft = aircraft
        if self.aircraft.Cz_eq is None:
            raise Exception("The compute_equilibrium method must be called before creating a StateSpaceModel instance.")
        self.Iyy = self.p['m']['value'] * self.p['rg']['value'] ** 2  # Initial tensor in y
        self.gamma_eq = 0
        self.Cz = self.aircraft.Cz_eq
        self.Cx_alpha = 2 * self.p['k']['value'] * self.p['Cz_alpha']['value']
        self.F_tau = 0
        self.Cm_alpha = (self.aircraft.X / self.p['lref']['value']) * (self.Cx_alpha * math.sin(self.aircraft.alpha_eq) - self.p['Cz_alpha']['value'] * math.cos(self.aircraft.alpha_eq))
        self.Cm_delta_m = (self.aircraft.Y / self.p['lref']['value']) * (self.aircraft.Cx_delta_m * math.sin(self.aircraft.alpha_eq) - self.p['Cz_delta_m']['value'] * math.cos(self.aircraft.alpha_eq))

        # ------------------- State space model final parameters of our matrices -------------------
        self.Xv = (2 * self.aircraft.Q * self.p['S']['value'] * self.aircraft.Cx_eq) / (self.p['m']['value'] * self.aircraft.Veq)
        self.Xalpha = (self.aircraft.Fpx_eq / (self.p['m']['value'] * self.aircraft.Veq)) * math.sin(self.aircraft.alpha_eq) + (self.aircraft.Q * self.p['S']['value'] * self.Cx_alpha) / (self.p['m']['value'] * self.aircraft.Veq)
        self.Xgamma = self.p['g']['value'] * math.cos(self.gamma_eq) / self.aircraft.Veq
        self.Xdelta_m = (self.aircraft.Q * self.p['S']['value'] * self.aircraft.Cx_delta_m) / (self.p['m']['value'] * self.aircraft.Veq)
        self.Xtau = - (self.F_tau * math.cos(self.aircraft.alpha_eq)) / (self.aircraft.p['m']['value'] * self.aircraft.Veq)
        self.mv = 0
        self.m_alpha = (self.aircraft.Q * self.p['S']['value'] * self.p['lref']['value'] * self.Cm_alpha) / self.Iyy
        self.m_q = (self.aircraft.Q * self.p['S']['value'] * (self.p['lref']['value']**2) * self.p['Cm_q']['value']) / (self.aircraft.Veq* self.Iyy)
        self.m_delta_m = (self.aircraft.Q * self.p['S']['value'] * self.p['lref']['value'] * self.Cm_delta_m) / self.Iyy
        self.Zv = (2 * self.aircraft.Q * self.p['S']['value'] * self.aircraft.Cz_eq) / (self.p['m']['value'] * self.aircraft.Veq)
        self.Zalpha = (self.aircraft.Fpx_eq * math.cos(self.aircraft.alpha_eq)) / (self.p['m']['value'] * self.aircraft.Veq) + (self.aircraft.Q * self.p['S']['value'] * self.p['Cz_alpha']['value']) / (self.p['m']['value'] * self.aircraft.Veq)
        self.Zgamma = (self.p['g']['value'] * math.sin(self.gamma_eq)) / self.aircraft.Veq
        self.Zdelta_m = (self.aircraft.Q * self.p['S']['value'] * self.p['Cz_delta_m']['value']) / (self.p['m']['value'] * self.aircraft.Veq)
        self.Ztau = - (self.F_tau * math.sin(self.aircraft.alpha_eq)) / (self.p['m']['value'] * self.aircraft.Veq)

        # ------------------- State space model -------------------
        self.A, self.B, self.C, self.D = None, None, None, None

    def model(self):
        self.A = np.array(
            [[-self.Xv, -self.Xgamma, -self.Xalpha, 0, 0, 0],
             [self.Zv, 0, self.Zalpha, 0, 0, 0],
             [-self.Zv, 0, -self.Zalpha, 1, 0, 0],
             [0, 0, self.m_alpha, self.m_q, 0, 0],
             [0, 0, 0, 1, 0, 0],
             [0, self.aircraft.Veq, 0, 0, 0, 0]]
        )
        self.B = np.array(
            [[0],
             [self.Zdelta_m],
             [-self.Zdelta_m],
             [self.m_delta_m],
             [0],
             [0]]
        )
        self.C = np.eye(6)
        self.D = np.zeros((6, 1))

        print("------------------- State space model -------------------")
        print("A = \n", self.A)
        print("B = \n", self.B)
        print("C = \n", self.C)
        print("D = \n", self.D)
        print("------------------- Eigen Values -------------------")
        eigen_values = np.linalg.eig(self.A)[0]
        print(f"Eigen values = {eigen_values}")

        return self.A, self.B, self.C, self.D, eigen_values

    def control(self):

        sys = ss(self.A, self.B, self.C, self.D)
        dmp = control.matlab.damp(sys)
        return sys, dmp

if __name__ == '__main__':
    aircraft = AircraftStability()
    alpha_eq = aircraft.compute_equilibrium()

    model = StateSpaceModel(aircraft)
    A, B, C, D, eigen_values = model.model()

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        sys, damping = model.control()



    # ------------------- Generate report -------------------
    # write = GenerateReport(A, B, C, D, eigen_values, damping, sys)
    # write.write()
    # --------------------------------------------------------

    # ------------------- Short Period Response -------------------
    short_period = ShortPeriod(A, B)
    print(short_period.__str__())
    short_period.plot()
    # --------------------------------------------------------

