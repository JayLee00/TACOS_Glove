
import os, sys
sys.path.append(os.getcwd())
from Tactile.tactile import Tactile
from visualizer.matplot import Graph

if __name__ == "__main__":
    t = Tactile()
    g = Graph(t)
    g.data_list = t.get_sensor_data()
    g.show()
    while True:
        pass
        # g.data_list = t.get_sensor_data()
        
        # print(sen)

