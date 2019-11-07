def handle_data():
    pass


import matplotlib
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(-4 * np.pi, 4 * np.pi)
y = np.sin(x)
plt.plot(x, y, ".-")
plt.show()
