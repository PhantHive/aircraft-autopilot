from control.matlab import dcgain
from sisopy31 import *
from src.SuperStyle.ironman import IronMan
import os

class Phugoid:

    def __init__(self, A, B):
        self.Ap = A[0:2, 0:2]
        self.Bp = B[0:2, 0:1]

        self.Cpv = np.array([[1, 0]])
        self.Cpg = np.array([[0, 1]])
        self.Dp = np.array([[0]])

    def __str__(self):
        return (f"------------------- Phugoid Model ------------------- \n"
                f"A = {self.Ap} \n"
                f"B = {self.Bp} \n"
                f"Cpv = {self.Cpv} \n"
                f"Cpg = {self.Cpg} \n"
                f"Dp = {self.Dp} \n\n"
                f"Phugoid Damp = {self.compute_damp()} \n"
                f"Phugoid TF for V/δm = {self.compute_tf()} \n"
                f"Phugoid TF for γ/δm = {self.compute_tf_g()} \n"
                f"Phugoid DC Gain of γ/δm = {self.compute_dcgain()} \n")

    def compute_ss_v(self):
        TvDm_ss = control.ss(self.Ap, self.Bp, self.Cpv, self.Dp)
        return TvDm_ss

    def compute_ss_g(self):
        TgDm_ss = control.ss(self.Ap, self.Bp, self.Cpg, self.Dp)
        return TgDm_ss

    def compute_damp(self):
        TvDm_system_info = control.matlab.damp(self.compute_ss_v(), doprint=False)
        return TvDm_system_info

    def compute_tf(self):
        TvDm_tf = control.tf(self.compute_ss_v())
        return TvDm_tf

    def compute_tf_g(self):
        TgDm_ss2tf = control.ss2tf(self.compute_ss_g())
        return TgDm_ss2tf

    def compute_dcgain(self):
        TgDm_dcgain = dcgain(self.compute_tf_g())
        return TgDm_dcgain

    def plot(self):

        iron = IronMan()

        plt.figure(1)
        plt.title(r'Phugoid approximation $V/δm$ et $γ/δm$')
        plt.xlabel('Time (s)')
        plt.ylabel(r'$V$ (m/s) & $γ$ (rad)')
        Yv, Tv = control.matlab.step(self.compute_tf(), arange(0, 700, 0.1))
        Yg, Tg = control.matlab.step(self.compute_tf_g(), arange(0, 700, 0.1))
        iron.neon_curve([Tv, Tg], [Yv, Yg])

        # Plotting 5% margin around the steady-state value
        plt.plot([0, Tv[-1]], [Yv[-1], Yv[-1]], '--', lw=1, color='#C56D1C')
        plt.plot([0, Tv[-1]], [1.05 * Yv[-1], 1.05 * Yv[-1]], '--', lw=1, color='#C56D1C')
        plt.plot([0, Tv[-1]], [0.95 * Yv[-1], 0.95 * Yv[-1]], '--', lw=1, color='#C56D1C')

        plt.plot([0, Tg[-1]], [Yg[-1], Yg[-1]], '--', lw=1, color='#D4F7F9')
        plt.plot([0, Tg[-1]], [1.05 * Yg[-1], 1.05 * Yg[-1]], '--', lw=1, color='#D4F7F9')
        plt.plot([0, Tg[-1]], [0.95 * Yg[-1], 0.95 * Yg[-1]], '--', lw=1, color='#D4F7F9')

        Osv, Trv, Tsv = step_info(Tv, Yv)
        Osg, Trg, Tsg = step_info(Tg, Yg)

        # Plotting the settling time (interpolation of the step_info function) and the overshoot value
        arrow_width = 0.01
        arrow_head_length = 4
        text_offset = 2

        yyv = interp1d(Tv, Yv)
        plt.plot(Tsv, yyv(Tsv), 'D', color='#C56D1C', markersize=10)
        plt.annotate(round(Tsv, 4), xy=(Tsv, yyv(Tsv)), xytext=(Tsv + text_offset, yyv(Tsv) + text_offset),
                     arrowprops=dict(facecolor='#C56D1C', edgecolor='#C56D1C', shrink=0.05, width=arrow_width, headlength=arrow_head_length))
        yyg = interp1d(Tg, Yg)
        plt.plot(Tsg, yyg(Tsg), 'D', color='#D4F7F9', markersize=10)
        plt.annotate(round(Tsg, 4), xy=(Tsg, yyg(Tsg)), xytext=(Tsg - text_offset, yyg(Tsg) - text_offset),
                     arrowprops=dict(facecolor='#D4F7F9', edgecolor='#D4F7F9', shrink=0.05, width=arrow_width, headlength=arrow_head_length))

        print(f"V Settling time 5% = {Tsv} s")
        print(f"𝛾 Settling time 5% = {Tsg} s\n")

        plt.minorticks_on()
        plt.legend((r'$V/δm$', r'$γ/δm$'))

        path = os.path.abspath(os.getcwd())
        try:
            savefig(f"{path}\\src\\misc\\plots\\phugoid.png")
        except:
            print("Error while saving the figure")

        plt.show()


if __name__ == '__main__':
    A = np.array([[-0.034, -0.0237, -0.0361, 0, 0, 0, ],
                  [0.0461, 0, 1.2484, 0, 0, 0, ],
                  [-0.0461, 0, -1.2484, 1, 0, 0, ],
                  [0, 0, -50.2354, -0.6048, 0, 0, ],
                  [0, 0, 0, 1, 0, 0, ],
                  [0, 414.0176, 0, 0, 0, 0, ]])

    B = np.array([[0.],
                  [0.1785],
                  [-0.1785],
                  [-31.4385],
                  [0.],
                  [0.]])

    phugoid = Phugoid(A, B)
    print(phugoid)
    phugoid.plot()





