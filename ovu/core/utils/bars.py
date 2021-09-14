import matplotlib.pyplot as plt
import numpy as np


class MyBar:
    width = 0.35

    def __init__(self, labels: list, values):
        self.labels = labels
        self.values = values
        self.fig, self.ax = plt.subplots(figsize=(15, 6), dpi=100, )

    def to_draw(self):
        rects: list = []
        counter: int = 0

        major: int = 0
        for v in self.values.values():
            temp = len(v)
            if temp > major:
                major = temp

        for key, value in self.values.items():
            print(key, value)
            x = np.arange(len(self.labels))
            if value:
                if len(value) < major:
                    for i in range(major - len(value)):
                        value.append(0)
                rects.append(self.ax.bar(x + counter * self.width, value, self.width, label=key))
                self.tendency(x=self.labels, y=value)
                counter += 1

        self.ax.set_ylabel('Scores')
        # self.ax.set_title('Scores by group and gender')
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(self.labels)
        self.ax.legend()

        for it in rects:
            self._autolabel(it)

        self.fig.tight_layout()

        return self.fig

    def tendency(self, x, y):
        # import seaborn as sns
        # data = pd.DataFrame({'year': x,
        #                      'value': y})
        # return sns.lmplot(x='year', y='value', data=data, fit_reg=True)
        x1 = np.array([x for x in range(len(x))])
        y1 = np.array(y)
        try:
            m, b = np.polyfit(x1, y1, 1)
        except:
            return 0

        return self.ax.plot(x1, m*x1 + b, )

    def to_clear(self):
        plt.close(self.fig)
        self.fig.clear()

    def _autolabel(self, rects):
        """Attach a text label above each bar in *rects*, displaying its height."""
        for rect in rects:
            height = rect.get_height()
            self.ax.annotate('{}'.format(height),
                             xy=(rect.get_x() + rect.get_width() / 2, height),
                             xytext=(0, 3),  # 3 points vertical offset
                             textcoords="offset points",
                             ha='center', va='bottom')

# labels = ['2004', '2005', '2006', '2007', '2008', '2009']
# men_means = {'Básica': [0.92, 1.05, 1.01, 1.12, 1.27], 'Adultos': [], 'Inicial': [0.07, 0.09, 0.09, 0.08, 0.11, 0.12],
#              'MESCyT3': [], 'Media': []}
# women_means = [25, 32, 34, 20, 25]
#
# p = MyBar(labels=labels, values=men_means)
# p.to_draw()
