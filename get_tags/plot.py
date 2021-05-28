import math
import matplotlib.pyplot as plt

if __name__ == '__main__':
    x = [i for i in range(1, 2000)]
    y = [i ** (14 / 15) for i in x]
    for j in range(0, 25):
        y = [i ** ((14 + j) / (15 + j)) for i in x]
        plt.plot(x, y, 'r-', linewidth=0.1, label=j)
    plt.plot(x, x, 'g-', linewidth=2)
    plt.legend(loc='upper left')
    plt.grid(True)
    plt.xlabel('x')
    plt.ylabel('log(x)')
    plt.show()
