import control
import numpy as np


class RootFinding:

    def __init__(self, SS_sat, alpha_max):
        self.SS_sat = SS_sat
        self.alpha_max = alpha_max

    def saturation(self, gamma):
        alpha, t = control.matlab.step(gamma * self.SS_sat)
        diff = np.max(alpha) - self.alpha_max
        return diff

    def derivative(self, f, x0, h):
        df = (f(x0 + h) - f(x0)) / h
        return df

    def newton(self, f, df):
        count = 0
        x0 = 0
        x1 = np.pi / 6
        eps = 1e-10
        while np.abs(x1 - x0) > eps:
            x0 = x1
            x1 = x0 - f(x0) / df(f, x0, eps)
            count += 1
        return x1, count