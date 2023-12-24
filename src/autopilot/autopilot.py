from sisopy31 import *
from matplotlib import pyplot as plt
from scipy.interpolate import interp1d
from src.SuperStyle.ironman import IronMan
import os


class AutoPilot:

    def __init__(self, A, B):
        self.A = A[1:, 1:]
        self.B = B[1:]
        self.D = np.zeros((1, 1))
        self.Kr = -0.33057  # using sisopy31
        self.Kgamma = 14.30915
        self.iron = IronMan()

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

    def plot_q_feedback(self, closed_tf_ss_q):

        arrow_width = 0.01
        arrow_head_length = 4
        text_offset = 0.25

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
        plt.annotate(round(Tsqcl, 4), xy=(Tsqcl, yyqcl(Tsqcl)), xytext=(Tsqcl + text_offset, yyqcl(Tsqcl) - text_offset),
                     arrowprops=dict(facecolor='#D4F7F9', edgecolor='#D4F7F9', shrink=0.05, width=arrow_width, headlength=arrow_head_length))
        print(f'q Settling time 5%% = {Tsqcl} s')

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
