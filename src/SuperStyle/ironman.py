# https://github.com/PhantHive/super-curves/blob/master/src/super_curves/SuperStyle/ironman.py

from matplotlib import pyplot as plt
from src.SuperStyle.main_style import Global


class IronMan(Global):

    def __init__(self):

        super(IronMan, self).__init__("#352713", "#D6D2C4", "white", "dark_background")
        self.colors = [
            "#C56D1C",
            "#D4F7F9",
            "#FAC672",
            "#C0AB19",
            "#41080F"
        ]

    def neon_curve(self, x_list, y_list):
        n_lines = 10
        diff_linewidth = 0.1
        alpha_value = 0.2

        for n in range(1, n_lines + 1):
            for i in range(len(y_list)):
                plt.plot(x_list[i], y_list[i], linewidth=2 + (diff_linewidth * n),
                         alpha=alpha_value, color=self.colors[i])
