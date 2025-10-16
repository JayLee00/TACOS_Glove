import os, sys
# import numpy as np

# 현재 작업 디렉토리를 시스템 경로에 추가합니다.
# 이렇게 하면 다른 폴더에 있는 파이썬 파일(모듈)을 쉽게 불러올 수 있습니다.
sys.path.append(os.getcwd())

# 우리가 만든 다른 파이썬 파일에서 필요한 클래스와 함수들을 불러옵니다.
# Tactile: 센서 하드웨어와 통신하고 데이터를 읽는 역할
# SaveTactile: 수집한 데이터를 파일로 저장하는 역할
# LoadTactile: 저장된 파일을 불러오는 역할
# Graph: 실시간으로 데이터를 그래프로 보여주는 역할 (이 파일에서는 사용되지 않음)
# SensorBrowser: 저장된 데이터를 다양한 방식으로 시각화하여 보여주는 역할
# lstsq...: 최소제곱법(least-squares) 관련 함수들 (이 파일에서는 사용되지 않음)
from Tactile import Tactile, SaveTactile, LoadTactile, Graph, SensorBrowser, lstsq_plot_overlay_all, lstsq_plot_grid, lstsq_fit_all_sensors

# 이 스크립트 파일이 직접 실행될 때만 아래의 코드가 동작하도록 합니다.
# 다른 파일에서 이 파일을 import해서 사용할 때는 아래 코드가 실행되지 않습니다.
if __name__ == "__main__":
    '''데이터 수집'''
    # --- 1. 데이터 수집 ---
    # Tactile 클래스를 이용해 센서 객체를 생성합니다.
    # port: 센서가 연결된 COM 포트 번호 (장치 관리자에서 확인 가능)
    # baudrate: 통신 속도 (보통 1,000,000 bps 사용)
    # print_en=True: 콘솔 창에 수신되는 데이터를 실시간으로 출력
    t = Tactile(port='COM6', baudrate=1_000_000, print_en=True)

    # SaveTactile 클래스를 이용해 데이터 저장 객체를 생성합니다.
    # 위에서 만든 tactile 객체(t)를 전달하여 어떤 데이터를 저장할지 알려줍니다.
    # 다른 폴더에 저장하고 싶을 경우
    # custom_path = r"D:\MySensorData"
    # s = SaveTactile(tactile=t, save_dir=custom_path)
    s = SaveTactile(tactile=t)

    # Graph 클래스를 이용해 실시간 그래프 객체를 생성합니다.
    # auto_start=True: 프로그램 시작과 동시에 그래프 창을 띄웁니다.
    # 이 코드는 사용자가 데이터 수집 과정을 시각적으로 확인하고 싶을 때 사용합니다.
    # 데이터 수집이 끝나면 그래프 창을 닫아야 다음 단계로 진행됩니다.
    g = Graph(t, auto_start = True)
    '''save+노이즈제거'''

    # --- 2. 데이터 저장 및 노이즈 제거 ---
    # 데이터 수집이 끝나면(그래프 창을 닫으면) s.save()가 호출됩니다.
    # s.save()는 지금까지 수집된 모든 센서 데이터를 가져와 파일로 저장합니다.
    # 이 과정에서 칼만 필터(Kalman Filter)를 적용하여 노이즈가 제거된 데이터도 함께 저장합니다.
    # 저장된 파일 이름(fn)을 반환받습니다. (예: "timestamp_data_240101_120000_...KTrue.npz")
    fn = s.save()
    '''데이터 확인'''
    # fn="timestamp_data_250925_160345_t(41962,)P(41962, 21)T(41962, 21)KTrue"
    # fn="timestamp_data_250926_144317_t(83977,)P(83977, 21)T(83977, 21)KTrue"

    # --- 3. 데이터 확인 ---
    # LoadTactile 클래스를 이용해 방금 저장한 파일을 불러옵니다.
    l = LoadTactile(fn)

    # 불러온 데이터에서 시간(time), 압력(pres), 온도(temp) 데이터를 각각 변수에 저장합니다.
    # 여기서는 칼만 필터(kf)가 적용된 압력(tactile_pres_kf)과 온도(tactile_temp_kf) 데이터를 사용합니다.
    # 원본 데이터를 사용하고 싶다면 아래 주석 처리된 코드를 활성화하면 됩니다.
    time = l.data["tactile_time"]
    # pres = l.data["tactile_pres"]
    # temp = l.data["tactile_temp"]
    pres = l.data["tactile_pres_kf"]
    temp = l.data["tactile_temp_kf"]
    # pres = l.data["tactile_pres_rts"]
    # temp = l.data["tactile_temp_rts"]

    # plot_pres_temp_grid(time, pres, temp)
    # SensorBrowser를 이용해 불러온 데이터를 시각화합니다.
    # layout=(3, 7): 21개 센서를 3행 7열의 그리드로 보여줍니다.
    browser = SensorBrowser(time, pres, temp, layout=(3, 7), title="21 Sensors")
    # browser.show()를 호출하면 그래프 창이 나타납니다.
    # mode="scatter": 온도-압력 관계를 보여주는 산점도 모드로 시작합니다.
    # ms=0.5, alpha=0.3: 점의 크기와 투명도를 설정합니다.
    browser.show(mode="scatter", ms=0.5, alpha=0.3)