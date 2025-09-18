import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
import threading

class Graph:
    def __init__(self, tact):
        self.tact = tact
        self.data_list = [[10]*21]

        self.init()

    def init(self):
        self.colors = []
        for v in range(21):
            if v < 7:
                self.colors.append("skyblue")
            elif v < 14:
                self.colors.append("orange")
            else:
                self.colors.append("darkblue")

        self.x = np.arange(21)
        self.values = np.zeros(21)

        self.fig = plt.figure()
        self.ax = self.fig.add_subplot()
        self.bars = self.ax.bar(self.x, self.values, color=self.colors, edgecolor="black")

        self.ax.set_ylim(-2500, 10000)
        self.ax.set_xlabel("Index")
        self.ax.set_ylabel("Value")

    def show(self):
        self.ani = FuncAnimation(
            self.fig,
            self.update,           # update(frame) 시그니처 유지
            interval=5,          # 100 ms
            blit=False,             # 가능하면 성능 향상
            cache_frame_data=False, # 경고 제거: 프레임 캐시 끄기
            repeat=True
        )
        plt.show()

    def update(self, frame):
        self.data_list = self.tact.get_sensor_data()

        new_values = np.array(self.data_list, dtype=int)  # 센서값 대신 랜덤
        for bar, val in zip(self.bars, new_values):
            bar.set_height(val)
        return self.bars
    # def start_show(self): #show Thread 함수 시작
    #     self.thread = threading.Thread(target=self.show)#, daemon=True)
    #     self.thread.start()

    # def __del__(self):
    #     if getattr(self, "thread", None) is not None:
    #         self.thread.join(timeout=0.1)

if __name__ == "__main__":
    g = Graph()
    g.show()




'''
from threading import Thread

def threaded(func):
    def run_in_thread(*args, **kwargs):
        t = Thread(target=func, args=args, kwargs=kwargs)
        t.start()
        # t.join() # 필요하다면 스레드가 끝날 때까지 기다림
        return t
    return run_in_thread

@threaded
def my_function(name):
    print(f"Thread 시작: {name}")
    # 시간 소모적인 작업 수행
    print(f"Thread 종료: {name}")

my_function("작업1")
my_function("작업2")
'''