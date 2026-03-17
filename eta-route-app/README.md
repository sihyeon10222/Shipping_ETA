# 🚢 eta-route-app

AIS 선박 데이터를 활용한 선박 위치 추적 및 ETA 계산 웹 애플리케이션

## 📋 개요

핀란드 해양청(Fintraffic)의 Digitraffic AIS API에서 선박 데이터를 가져와
지도 위에 시각화하고 목적지까지의 예상 도착 시간(ETA)을 계산합니다.

## ✨ 주요 기능

- 📡 AIS API에서 실시간 선박 위치 데이터 조회
- 📋 선박 데이터를 검색·필터 가능한 테이블로 표시
- 🗺️ 지도 위에 선종별 색상으로 선박 위치 시각화
- ⏱️ 선박→목적지 거리 및 ETA 계산

## 🚀 실행 방법

```bash
# 1. 가상환경 생성 (최초 1회)
python3 -m venv .venv

# 2. 가상환경 활성화
source .venv/bin/activate     # Mac/Linux
# .venv\Scripts\activate      # Windows

# 3. 패키지 설치
pip install -r requirements.txt

# 4. 앱 실행
streamlit run app.py
```

## 📁 프로젝트 구조

```
eta-route-app/
├── app.py                  # Streamlit 메인 앱
├── api/
│   └── ais_client.py       # AIS API 호출 모듈
├── utils/
│   ├── data_processing.py  # 데이터 변환 헬퍼
│   └── eta_calculator.py   # ETA 계산 로직
├── components/
│   ├── map_view.py         # 지도 시각화
│   └── data_table.py       # 데이터 테이블
├── requirements.txt        # 의존 패키지
├── .gitignore              # Git 제외 파일
└── README.md               # 이 파일
```

## 📡 데이터 출처

- API: [Digitraffic Marine API](https://meri.digitraffic.fi/swagger/)
- 라이선스: Creative Commons 4.0 BY
- © Fintraffic / digitraffic.fi
