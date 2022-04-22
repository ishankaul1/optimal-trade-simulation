import numpy as np
import matplotlib.pyplot as plt

#Sigmoid function of x, which uses k as a value that 'stretches' or 'shortens' the domain
#inversely to its value. Returns a value between 0 and -1.
def sig(x: float, k: float):
    return 1/(1 + np.exp(-(k * x)))

# rng = np.linspace(-50, 50, 50, True)
# k = 0.3
# plt.plot([x for x in rng], [sig(x, k) for x in rng])
# plt.show()
