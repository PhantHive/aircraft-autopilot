from control.matlab import dcgain
from sisopy31 import *

class Phugoid:

    def __init__(self, A, B):
        self.Ap = A[0:2, 0:2]
        self.Bp = B[0:2, 0:1]

        self.Cpv = np.array([[1, 0]])
        self.Cpg = np.array([[0, 1]])
        self.Dp = np.array([[0]])

    def __str__(self):
        return (f"Phugoid Model: \n"
                f"A = {self.Ap} \n"
                f"B = {self.Bp} \n"
                f"Cpv = {self.Cpv} \n"
                f"Cpg = {self.Cpg} \n"
                f"Dp = {self.Dp} \n"
                f"------------------- \n"
                f"Phugoid Damp = {self.compute_damp()} \n"
                f"Phugoid TF for V/δm = {self.compute_tf()} \n"
                f"Phugoid TF for γ/δm = {self.compute_tf_g()} \n"
                f"Phugoid DC Gain of γ/δm = {self.compute_dcgain()} \n"
                f"------------------- \n")

    def compute_ss_v(self):
        TvDm_ss = control.ss(self.Ap, self.Bp, self.Cpv, self.Dp)
        return TvDm_ss

    def compute_ss_g(self):
        TgDm_ss = control.ss(self.Ap, self.Bp, self.Cpg, self.Dp)
        return TgDm_ss

    def compute_damp(self):
        TvDm_system_info = control.matlab.damp(self.compute_ss_v())
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

        plt.figure(1)
        plt.title(r'Phugoid approximation $V/δm$ et $γ/δm$')
        plt.legend((r'$V/δm$', r'$γ/δm$'))
        plt.xlabel('Time (s)')
        plt.ylabel(r'$V$ (m/s) & $γ$ (rad)')
        Yv, Tv = control.matlab.step(self.compute_tf(), arange(0, 700, 0.1))
        Yg, Tg = control.matlab.step(self.compute_tf_g(), arange(0, 700, 0.1))
        plt.plot(Tv, Yv, "b", Tg, Yg, "r", lw=2)
        plt.plot([0, Tv[-1]], [Yv[-1], Yv[-1]], 'k--', lw=1)
        plt.plot([0, Tv[-1]], [1.05 * Yv[-1], 1.05 * Yv[-1]], 'k--', lw=1)
        plt.plot([0, Tv[-1]], [0.95 * Yv[-1], 0.95 * Yv[-1]], 'k--', lw=1)
        plt.plot([0, Tg[-1]], [Yg[-1], Yg[-1]], 'k--', lw=1)

        Osv, Trv, Tsv = step_info(Tv, Yv)
        Osg, Trg, Tsg = step_info(Tg, Yg)
        yyv = interp1d(Tv, Yv)
        plt.plot(Tsv, yyv(Tsv), 'bs')
        plt.text(Tsv, yyv(Tsv) - 0.2, Tsv)
        yyg = interp1d(Tg, Yg)
        plt.plot(Tsg, yyg(Tsg), 'rs')
        plt.text(Tsg, yyg(Tsg) - 0.2, Tsg)

        print("V Settling time 5%% = %f s" % Tsv)
        print("𝛾 Settling time 5%% = %f s\n" % Tsg)

        plt.minorticks_on()
        plt.grid(which='major', linestyle='-', linewidth='0.5', color='black')
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





