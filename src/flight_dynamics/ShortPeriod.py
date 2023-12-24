from sisopy31 import *
import os


class ShortPeriod:

    def __init__(self, A, B):
        self.As = A[2:4, 2:4]
        self.Bs = B[2:4, 0:1]

        self.Csa = np.array([[1, 0]])
        self.Csq = np.array([[0, 1]])
        self.Ds = np.array([[0]])

    def __str__(self):
        return (f"Short Period Model: \n"
                f"A = {self.As} \n"
                f"B = {self.Bs} \n"
                f"Csa = {self.Csa} \n"
                f"Csq = {self.Csq} \n"
                f"Ds = {self.Ds} \n"
                f"------------------- \n"
                f"Short Period Damp = {self.compute_damp()} \n"
                f"Short Period TF for α/δm = {self.compute_tf()} \n"
                f"Short Period TF for q/δm = {self.compute_tf_q()} \n"
                f"Short Period DC Gain of q/δm = {self.compute_dcgain()} \n"
                f"------------------- \n")

    def compute_ss_a(self):
        TaDm_ss = control.ss(self.As, self.Bs, self.Csa, self.Ds)
        return TaDm_ss

    def compute_ss_q(self):
        TqDm_ss = control.ss(self.As, self.Bs, self.Csq, self.Ds)
        return TqDm_ss

    def compute_damp(self):
        TaDm_system_info = control.matlab.damp(self.compute_ss_a())
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
        plt.figure(1)
        plt.title(r'Step Period approximation $α/δm$ et $q/δm$')
        plt.legend((r'$α/δm$', r'$q/δm$'))
        plt.xlabel('Time (s)')
        plt.ylabel(r'$α$ (rad) & $q$ (rad/s)')
        Ya, Ta = control.matlab.step(self.compute_tf(), arange(0, 10, 0.1))
        Yq, Tq = control.matlab.step(self.compute_tf_q(), arange(0, 10, 0.1))
        plt.plot(Ta, Ya, "b", Tq, Yq, "r", lw=2)
        plt.plot([0, Ta[-1]], [Ya[-1], Ya[-1]], 'k--', lw=1)
        plt.plot([0, Ta[-1]], [1.05 * Ya[-1], 1.05 * Ya[-1]], 'k--', lw=1)
        plt.plot([0, Ta[-1]], [0.95 * Ya[-1], 0.95 * Ya[-1]], 'k--', lw=1)
        plt.plot([0, Tq[-1]], [Yq[-1], Yq[-1]], 'k--', lw=1)
        plt.plot([0, Tq[-1]], [1.05 * Yq[-1], 1.05 * Yq[-1]], 'k--', lw=1)
        plt.plot([0, Tq[-1]], [0.95 * Yq[-1], 0.95 * Yq[-1]], 'k--', lw=1)

        Osa, Tra, Tsa = step_info(Ta, Ya)
        Osq, Trq, Tsq = step_info(Tq, Yq)
        yya = interp1d(Ta, Ya)
        plt.plot(Tsa, yya(Tsa), 'bs')
        plt.text(Tsa, yya(Tsa) - 0.2, Tsa)
        yyq = interp1d(Tq, Yq)
        plt.plot(Tsq, yyq(Tsq), 'rs')
        plt.text(Tsq, yyq(Tsq) - 0.2, Tsq)

        plt.minorticks_on()
        plt.grid(which='major', linestyle='-', linewidth='0.5', color='black')

        print("α Settling time 5%% = %f s" % Tsa)
        print("q Settling time 5%% = %f s" % Tsq)
        # get current dir absolute path
        path = os.path.abspath(os.getcwd())
        savefig(f"{path}\\src\\pdf\\stepalphaq.png")
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
