from matplotlib import pyplot as plt


class Global:

    def __init__(self, bg, fg, axis, style):

        self.bg = bg
        self.fg = fg
        self.axis = axis
        self.style = style
        self.dark_style()

    def dark_style(self):
        # style
        plt.style.use(self.style)
        for param in ['figure.facecolor', 'axes.facecolor', 'savefig.facecolor']:
            plt.rcParams[param] = self.bg  # bluish dark grey
        for param in ['text.color', 'xtick.color', 'grid.color', 'ytick.color', 'axes.labelcolor']:
            plt.rcParams[param] = self.axis  # very light grey

        plt.grid(color=self.fg)  # bluish dark grey, but slightly lighter than background
        # ==========================