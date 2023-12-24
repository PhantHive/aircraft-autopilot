from control.matlab import dcgain
from sisopy31 import *
from src.SuperStyle.ironman import IronMan
import os

class ShortPeriod:

    def __init__(self, A, B):
        self.As = A[2:4, 2:4]
        self.Bs = B[2:4, 0:1]

        self.Csa = np.array([[1, 0]])
        self.Csq = np.array([[0, 1]])
        self.Ds = np.array([[0]])

    def __str__(self):
        return (f"------------------- Short Period Model ------------------- \n"
                f"A = {self.As} \n"
                f"B = {self.Bs} \n"
                f"Csa = {self.Csa} \n"
                f"Csq = {self.Csq} \n"
                f"Ds = {self.Ds} \n\n"
                f"Short Period Damp = {self.compute_damp()} \n"
                f"Short Period TF for α/δm = {self.compute_tf()} \n"
                f"Short Period TF for q/δm = {self.compute_tf_q()} \n"
                f"Short Period DC Gain of q/δm = {self.compute_dcgain()} \n")

    def compute_ss_a(self):
        TaDm_ss = control.ss(self.As, self.Bs, self.Csa, self.Ds)
        return TaDm_ss

    def compute_ss_q(self):
        TqDm_ss = control.ss(self.As, self.Bs, self.Csq, self.Ds)
        return TqDm_ss

    def compute_damp(self):
        TaDm_system_info = control.matlab.damp(self.compute_ss_a(), doprint=False)
        return TaDm_system_info

    def compute_tf(self):
        TaDm_tf = control.tf(self.compute_ss_a())
        return TaDm_tf

    def compute_tf_q(self):
        TqDm_ss2tf = control.ss2tf(self.compute_ss_q())
        return TqDm_ss2tf

    def compute_dcgain(self):
        TqDm_dcgain = dcgain(self.compute_tf_q())
        return TqDm_dcgain

    def plot(self):

        iron = IronMan()

        plt.figure(1)
        plt.title(r'Short Period approximation $α/δm$ et $q/δm$')
        plt.xlabel('Time (s)')
        plt.ylabel(r'$α$ (rad) & $q$ (rad/s)')
        Ya, Ta = control.matlab.step(self.compute_tf(), arange(0, 10, 0.1))
        Yq, Tq = control.matlab.step(self.compute_tf_q(), arange(0, 10, 0.1))
        iron.neon_curve([Ta, Tq], [Ya, Yq])

        # Plotting 5% of margin around the steady-state value
        plt.plot([0, Ta[-1]], [Ya[-1], Ya[-1]], '--', lw=1, color='#C56D1C')
        plt.plot([0, Ta[-1]], [1.05 * Ya[-1], 1.05 * Ya[-1]], '--', lw=1, color='#C56D1C')
        plt.plot([0, Ta[-1]], [0.95 * Ya[-1], 0.95 * Ya[-1]], '--', lw=1, color='#C56D1C')

        plt.plot([0, Tq[-1]], [Yq[-1], Yq[-1]], '--', lw=1, color='#D4F7F9')
        plt.plot([0, Tq[-1]], [1.05 * Yq[-1], 1.05 * Yq[-1]], '--', lw=1, color='#D4F7F9')
        plt.plot([0, Tq[-1]], [0.95 * Yq[-1], 0.95 * Yq[-1]], '--', lw=1, color='#D4F7F9')

        # Plotting the settling time (interpolation of the step_info function) and the overshoot value
        arrow_width = 0.01
        arrow_head_length = 4
        text_offset = 1.5

        Osa, Tra, Tsa = step_info(Ta, Ya)
        Osq, Trq, Tsq = step_info(Tq, Yq)
        yya = interp1d(Ta, Ya)
        plt.plot(Tsa, yya(Tsa), "D", color="#C56D1C", markersize=10)
        plt.annotate(round(Tsa, 4), xy=(Tsa, yya(Tsa)), xytext=(Tsa + text_offset, yya(Tsa) + text_offset),
                     arrowprops=dict(facecolor='#C56D1C', edgecolor='#C56D1C', shrink=0.05, width=arrow_width, headlength=arrow_head_length))
        yyq = interp1d(Tq, Yq)
        plt.plot(Tsq, yyq(Tsq), "D", color="#D4F7F9", markersize=10)
        plt.annotate(round(Tsq, 4), xy=(Tsq, yyq(Tsq)), xytext=(Tsq - text_offset, yyq(Tsq) - text_offset),
                     arrowprops=dict(facecolor='#D4F7F9', edgecolor='#D4F7F9', shrink=0.05, width=arrow_width, headlength=arrow_head_length))

        plt.minorticks_on()
        plt.legend((r'$α/δm$', r'$q/δm$'))

        print(f"α Settling time 5% = {Tsa} s")
        print(f"q Settling time 5% = {Tsq} s \n")

        # get current dir absolute path
        path = os.path.abspath(os.getcwd())
        try:
            savefig(f"{path}\\src\\pdf\\shortperiod.png")
        except:
            print("Error while saving the figure")
        plt.show()


if __name__ == '__main__':
    A = np.array([[-0.034, -0.0237, -0.0361, 0, 0, 0, ],
                  [0.0461, 0, 1.2484, 0, 0, 0,],
                  [-0.0461, 0, -1.2484, 1, 0, 0,],
                  [0, 0, -50.2354, -0.6048, 0, 0,],
                  [0, 0, 0, 1, 0, 0,],
                  [0, 414.0176, 0, 0, 0, 0,]])

    B = np.array([[0.],
                  [0.1785],
                  [-0.1785],
                  [-31.4385],
                  [0.],
                  [0.]])

    short_period = ShortPeriod(A, B)
    print(short_period.__str__())
    short_period.plot()
