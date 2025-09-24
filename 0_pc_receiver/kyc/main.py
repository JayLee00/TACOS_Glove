import os, sys
# import numpy as np
sys.path.append(os.getcwd())
from Tactile.tactile import Tactile
from Visualizer.matplot import Graph

if __name__ == "__main__":
    # np.set_printoptions(linewidth=100000, threshold=np.inf)
    t = Tactile(port='COM12', baudrate=1_000_000, print_en=True)
    g = Graph(t, auto_start = True)
    while True:
        pass

