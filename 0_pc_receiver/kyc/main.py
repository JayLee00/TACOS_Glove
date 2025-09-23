import os, sys
sys.path.append(os.getcwd())
from Tactile.tactile import Tactile
from Visualizer.matplot import Graph

if __name__ == "__main__":
    t = Tactile(port='COM12', baudrate=1_000_000)
    g = Graph(t, auto_start = True)
    while True:
        pass

