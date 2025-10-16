LastUpdate: 2025-10-10

- force 와 센서 값 켈리브레이션 파일 만듬
- main_6_only_one_data.py -> 센서 값 matlab으로 보내기
- Optosigma_contrl.py -> 모터스테이지 제어
- matla의 DAQ simulink 파일 열어서 실행시키면 거리,힘,센서 데이터 담아둠
3번 max 까지 눌렀다 땐 데이터 3개 모아둠,
이거는 max force 0.3N 정도밖에 나오지 않음. -> 개선 필요.