from sisopy31 import *
from matplotlib import pyplot as plt
from scipy.interpolate import interp1d
from src.SuperStyle.ironman import IronMan
import os

from src.autopilot.root_finding import RootFinding


class AutoPilot:

    def __init__(self, A, B):
        self.A = A[1:, 1:]
        self.B = B[1:]
        self.D = np.zeros((1, 1))
        self.Kr = -0.33057  # using sisopy31
        self.Kgamma = 14.30915
        self.Kz = 0.00272
        self.iron = IronMan()
        self.arrow_width = 0.01
        self.arrow_head_length = 4
        self.text_offset = 0.25

    def compute_q_feedback(self):
        Cq = np.array([[0], [0], [1], [0], [0]]).T

        Aq = self.A - self.Kr * self.B @ Cq
        Bq = self.Kr * self.B
        Dq = self.Kr * self.D

        closed_state_space = control.ss(Aq, Bq, Cq, Dq)
        closed_tf_ss_q = control.tf(closed_state_space)
        print("------------------- q feedback loop ------------------- \n")
        print(f"State space representation: {closed_state_space}")
        print(f"Transfer function: {closed_tf_ss_q}")
        eigen, damp, frequency = control.matlab.damp(closed_state_space)

        return Aq, Bq, Cq, Dq, eigen, damp, frequency, closed_tf_ss_q

    def compute_gamma_feedback(self, Aq, Bq, Cq, Dq):
        Cgamma = np.array([[1], [0], [0], [0], [0]]).T
        Agamma = Aq - self.Kgamma * Bq @ Cgamma
        Bgamma = self.Kgamma * Bq
        Dgamma = self.Kgamma * Dq
        closed_state_space = control.ss(Agamma, Bgamma, Cgamma, Dgamma)
        closed_tf_ss_gamma = control.tf(closed_state_space)
        print("\n------------------- 𝛾 feedback loop ------------------- \n")
        print(f"State space representation: {closed_state_space}")
        print(f"Transfer function: {closed_tf_ss_gamma}")
        eigen, damp, frequency = control.matlab.damp(closed_state_space)
        return Agamma, Bgamma, Cgamma, Dgamma, eigen, damp, frequency, closed_tf_ss_gamma

    def compute_z_feedback(self, Agamma, Bgamma, Cgamma, Dgamma):
        Cz = np.array([[0], [0], [0], [0], [1]]).T
        Az = Agamma - self.Kz * Bgamma @ Cz
        Bz = self.Kz * Bgamma
        Dz = self.Kz * Dgamma
        closed_state_space = control.ss(Az, Bz, Cz, Dz)
        closed_tf_ss_z = control.tf(closed_state_space)
        print("\n------------------- z feedback loop ------------------- \n")
        print(f"State space representation: {closed_state_space}")
        print(f"Transfer function: {closed_tf_ss_z}")
        eigen, damp, frequency = control.matlab.damp(closed_state_space)
        return Az, Bz, Cz, Dz, eigen, damp, frequency, closed_tf_ss_z

    def compute_gamma_max(self, Agamma, Bgamma, Cgamma, Dgamma, alpha_eq, alpha0):
        SS_sat = control.ss(Agamma, Bgamma, Cgamma, Dgamma)
        tf_ssat = control.tf(SS_sat)

        delta_nz = 3.1 # from practical work pdf (we want maximum transverse load factor)
        alpha_max = alpha_eq + (alpha_eq - alpha0) * delta_nz
        print("\n------------------- 𝛾_max computing ------------------- \n")
        print("State space representation y_csat 𝛼: ", SS_sat)
        print("Transfer function: ", tf_ssat)
        ymax_finder = RootFinding(SS_sat, alpha_max)
        ymax = ymax_finder.newton(ymax_finder.saturation, ymax_finder.derivative)
        print(f"We found 𝛾_max = {ymax[0]} rad with {ymax[1]} iterations")

    def plot_q_feedback(self, closed_tf_ss_q):
        Yqcl, Tqcl = control.matlab.step(closed_tf_ss_q, np.arange(0, 5, 0.01))
        self.iron.neon_curve([Tqcl], [Yqcl])
        plt.plot([0, Tqcl[-1]], [Yqcl[-1], Yqcl[-1]], '--', color='#C56D1C', lw=1)
        plt.plot([0, Tqcl[-1]], [1.05 * Yqcl[-1], 1.05 * Yqcl[-1]], '--', color='#C56D1C', lw=1)
        plt.plot([0, Tqcl[-1]], [0.95 * Yqcl[-1], 0.95 * Yqcl[-1]], '--', color='#C56D1C', lw=1)
        plt.minorticks_on()
        plt.title(r'Step response $q/q_c$')
        plt.xlabel('Time (s)')
        plt.ylabel(r'$q$ (rad/s)')

        Osqcl, Trqcl, Tsqcl = step_info(Tqcl, Yqcl)
        yyqcl = interp1d(Tqcl, Yqcl)
        plt.plot(Tsqcl, yyqcl(Tsqcl), 'D', color='#D4F7F9')
        plt.annotate(round(Tsqcl, 4), xy=(Tsqcl, yyqcl(Tsqcl)), xytext=(Tsqcl + self.text_offset, yyqcl(Tsqcl) - self.text_offset),
                     arrowprops=dict(facecolor='#D4F7F9', edgecolor='#D4F7F9', shrink=0.05, width=self.arrow_width, headlength=self.arrow_head_length))
        print(f'q Settling time 5% = {Tsqcl} s')

        path = os.path.abspath(os.getcwd())
        try:
            savefig(f"{path}\\src\\misc\\plots\\q_feedback.png")
        except:
            print("Error while saving the figure")
        plt.show()

    def plot_q_open_closed_loop(self, TqDm_tf):

        tau = 0.7
        tf_washout_filter = control.tf([tau, 0], [tau, 1])
        tf_washout_filter_closed = control.feedback(self.Kr, TqDm_tf * tf_washout_filter)

        C_alpha = [0, 1, 0, 0, 0]
        ss_α = control.ss(self.A, self.B, C_alpha, self.D)

        tf_α = control.tf(ss_α)
        tf_α_washout = control.series(1 / self.Kr, tf_washout_filter_closed, tf_α)
        tf_α_no_washout = control.series(1 / self.Kr, control.feedback(self.Kr, TqDm_tf), tf_α)
        t = np.arange(0, 15, 0.01)

        y, t = control.matlab.step(tf_α, t)
        plt.plot(t, y, label="Alpha α", color="#C56D1C")
        y, t = control.matlab.step(tf_α_no_washout, t)
        plt.plot(t, y, label="Alpha α no washout", color="#D4F7F9")
        y, t = control.matlab.step(tf_α_washout, t)
        plt.plot(t, y, linestyle=(0, (5, 10)), color="#C0AB19", label="Alpha α washout")
        plt.title("With/Without washout filter")
        plt.grid(alpha=0.2)
        plt.legend()
        plt.xlabel('Time (s)')
        plt.ylabel(r'$α$')

        path = os.path.abspath(os.getcwd())
        try:
            savefig(f"{path}\\src\\misc\\plots\\q_washout_filter.png")
        except:
            print("Error while saving the figure")

        plt.show()

    def plot_gamma_feedback(self, closed_tf_ss_gamma):
        Ygamma, Tgamma = control.matlab.step(closed_tf_ss_gamma, np.arange(0, 5, 0.01))
        self.iron.neon_curve([Tgamma], [Ygamma])
        plt.plot([0, Tgamma[-1]], [Ygamma[-1], Ygamma[-1]], '--', lw=1, color='#C56D1C')
        plt.plot([0, Tgamma[-1]], [1.05 * Ygamma[-1], 1.05 * Ygamma[-1]], '--', lw=1, color='#C56D1C')
        plt.plot([0, Tgamma[-1]], [0.95 * Ygamma[-1], 0.95 * Ygamma[-1]], '--', lw=1, color='#C56D1C')
        plt.minorticks_on()
        plt.title(r'Step response $𝛾/𝛾_c$')
        plt.xlabel('Time (s)')
        plt.ylabel(r'$𝛾$ (rad/s)')
        plt.grid(alpha=0.2)

        Os_gamma, Tr_gamma, Ts_gamma = step_info(Tgamma, Ygamma)
        yy_gamma = interp1d(Tgamma, Ygamma)
        plt.plot(Ts_gamma, yy_gamma(Ts_gamma), 'D', color='#D4F7F9')
        plt.annotate(round(Ts_gamma, 4), xy=(Ts_gamma, yy_gamma(Ts_gamma)), xytext=(Ts_gamma + self.text_offset, yy_gamma(Ts_gamma) - self.text_offset),
                     arrowprops=dict(facecolor='#D4F7F9', edgecolor='#D4F7F9', shrink=0.05, width=self.arrow_width, headlength=self.arrow_head_length))
        print(f'𝛾 Settling time 5% = {Ts_gamma} s')

        path = os.path.abspath(os.getcwd())
        try:
            savefig(f"{path}\\src\\misc\\plots\\gamma_feedback.png")
        except:
            print("Error while saving the figure")
        plt.show()

    def plot_z_feedback(self, closed_tf_ss_z):
        Yzcl, Tzcl = control.matlab.step(closed_tf_ss_z, np.arange(0, 10, 0.01))
        self.iron.neon_curve([Tzcl], [Yzcl])
        plt.plot([0, Tzcl[-1]], [Yzcl[-1], Yzcl[-1]], '--', lw=1, color='#C56D1C')
        plt.plot([0, Tzcl[-1]], [1.05 * Yzcl[-1], 1.05 * Yzcl[-1]], '--', lw=1, color='#C56D1C')
        plt.plot([0, Tzcl[-1]], [0.95 * Yzcl[-1], 0.95 * Yzcl[-1]], '--', lw=1, color='#C56D1C')
        plt.minorticks_on()
        plt.title(r'Step response $z/z_c$')
        plt.xlabel('Time (s)')
        plt.ylabel(r'$z$ (rad/s)')
        plt.grid(alpha=0.2)

        Oszcl, Trzcl, Tszcl = step_info(Tzcl, Yzcl)
        yyzcl = interp1d(Tzcl, Yzcl)
        plt.plot(Tszcl, yyzcl(Tszcl), 'D', color='#D4F7F9')
        plt.annotate(round(Tszcl, 4), xy=(Tszcl, yyzcl(Tszcl)),
                     xytext=(Tszcl + self.text_offset, yyzcl(Tszcl) - self.text_offset),
                     arrowprops=dict(facecolor='#D4F7F9', edgecolor='#D4F7F9', shrink=0.05, width=self.arrow_width,
                                     headlength=self.arrow_head_length))
        print('z Settling time 5%% = %f s' % Tszcl)

        path = os.path.abspath(os.getcwd())
        try:
            savefig(f"{path}\\src\\misc\\plots\\z_feedback.png")
        except:
            print("Error while saving the figure")
        plt.show()
