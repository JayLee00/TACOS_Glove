import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
import threading

class Graph:
    def __init__(self):
        self.x = np.arange(21)
        self.values = np.zeros(21)

        self.fig, self.ax = plt.subplots()
        self.bars = self.ax.bar(self.x, self.values, color="skyblue", edgecolor="black")

        self.ax.set_ylim(-100, 100)
        self.ax.set_xlabel("Index")
        self.ax.set_ylabel("Value")

        self.data_list = [[0]*21]
        
    def show(self):
        self.ani = FuncAnimation(self.fig, self.update, interval=100)  # 100ms마다 실행
        plt.show()

    def update(self, frame):
        new_values = np.array(self.data_list, dtype=int)  # 센서값 대신 랜덤
        for bar, val in zip(self.bars, new_values):
            bar.set_height(val)
        return self.bars
    
    def start_show(self): #show Thread 함수 시작
        self.thread = threading.Thread(target=self.show)#, daemon=True)
        self.thread.start()
        
    def __del__(self):
        if getattr(self, "thread", None) is not None:
            self.thread.join(timeout=0.1)

if __name__ == "__main__":
    g = Graph()
    g.show()