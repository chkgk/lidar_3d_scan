from pprint import pprint
import pickle

import numpy as np 
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def load_coordinates(filename):
    return pickle.load(open(filename, "rb" ))


def scatter(coordinates):

    np_arr = np.array(coordinates)
    perc = np.percentile(np_arr, 90)
    limit = perc + 10

    fig = plt.figure(figsize=(6,6), dpi=144)
    ax = fig.add_subplot(111, projection='3d')

    ax.set_xlim3d(-limit, limit)
    ax.set_ylim3d(-limit, limit)
    ax.set_zlim3d(-limit, limit)

    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')

    ax.azim = -145
    ax.elev = 15

    ax.scatter(*zip(*coordinates), s=1)
    #fig.savefig('scan.png')
    plt.show()


coordinates = load_coordinates('last.p')
# pprint(coordinates)


scatter(coordinates)