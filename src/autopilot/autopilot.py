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

    def compute_q_feedback(self):
        Cq = np.array([[0], [0], [1], [0], [0]]).T
        Kr = -0.33057  # using sisopy31

        Aq = self.A - Kr * self.B @ Cq
        Bq = Kr * self.B
        Dq = Kr * self.D

        closed_state_space = control.ss(Aq, Bq, Cq, Dq)
        closed_tf_ss_q = control.tf(closed_state_space)
        print("------------------- q feedback loop ------------------- \n")
        print(f"State space representation: {closed_state_space}")
        print(f"Transfer function: {closed_tf_ss_q}")
        eigen, damp, frequency = control.matlab.damp(closed_state_space)

        return Aq, Bq, Cq, Dq, eigen, damp, frequency, closed_tf_ss_q

    def plot_q_feedback(self, closed_tf_ss_q):

        iron = IronMan()
        arrow_width = 0.01
        arrow_head_length = 4
        text_offset = 0.25

        Yqcl, Tqcl = control.matlab.step(closed_tf_ss_q, np.arange(0, 5, 0.01))
        iron.neon_curve([Tqcl], [Yqcl])
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
