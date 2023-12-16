from sisopy31 import *


class Phugoid:

    def __init__(self, A, B):
        self.As = A[2:4, 2:4]
        self.Bs = B[2:4, 0:1]

        self.Csa = np.array([[1, 0]])
        self.Csq = np.array([[0, 1]])
        self.Ds = np.array([[0]])

    def compute_ss(self):
       TaDm_ss = ss(self.As, self.Bs, self.Csa, self.Ds)
       return TaDm_ss

    def compute_eigen(self):
        TaDm_eigen = np.linalg.eig(self.As)
        return TaDm_eigen
