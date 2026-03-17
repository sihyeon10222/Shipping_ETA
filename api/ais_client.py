"""
=============================================================
📡 Step 1: AIS API 클라이언트 모듈 (ais_client.py)
=============================================================

이 파일은 핀란드 해양청(Fintraffic)의 Digitraffic AIS API를 호출하여
선박 데이터를 가져오는 함수들을 모아놓은 모듈입니다.

📌 AIS란?
   - Automatic Identification System (자동 식별 시스템)
   - 선박이 자신의 위치, 속도, 방향 등의 정보를 자동으로 송신하는 시스템

📌 사용하는 API:
   - 기본 URL: https://meri.digitraffic.fi/api/ais/v1
   - 무료 오픈 데이터 (API 키 불필요!)
   - 라이선스: Creative Commons 4.0 BY

📌 주요 엔드포인트:
   1) /locations       → 모든 선박의 현재 위치 (GeoJSON 형식)
   2) /locations/{mmsi} → 특정 선박의 위치
   3) /vessels         → 모든 선박의 상세 정보 (이름, 선종 등)
   4) /vessels/{mmsi}  → 특정 선박의 상세 정보
=============================================================
"""

# ─── 라이브러리 가져오기 ────────────────────────────
import requests      # HTTP 요청을 보내기 위한 라이브러리
import streamlit as st  # Streamlit 캐싱 기능 사용


# ─── 상수 설정 ──────────────────────────────────────

# API의 기본 주소 (모든 요청의 앞부분에 붙음)
BASE_URL = "https://meri.digitraffic.fi/api/ais/v1"

# HTTP 요청 헤더
# ⚠️ Accept-Encoding: gzip → 필수! 이 헤더가 없으면 API가 거부할 수 있음
# ⚠️ Digitraffic-User → 내 앱의 이름을 알려주는 것 (예의상 넣는 것)
HEADERS = {
    "Accept-Encoding": "gzip",
    "Digitraffic-User": "eta-route-app/student-project",
}


# ─── API 호출 함수들 ────────────────────────────────

@st.cache_data(ttl=60)  # 60초 동안 결과를 캐시 (같은 요청을 반복하지 않음)
def get_all_locations():
    """
    📍 모든 선박의 현재 위치를 가져옵니다.

    반환값:
        dict - GeoJSON FeatureCollection 형식
        예시: {
            "type": "FeatureCollection",
            "features": [
                {
                    "mmsi": 219598000,
                    "geometry": {"coordinates": [경도, 위도]},
                    "properties": {"sog": 10.5, "cog": 205.7, ...}
                }, ...
            ]
        }

    💡 주의: 전체 선박 데이터는 수천 개로 매우 큼!
       처음 테스트할 때는 get_vessel_location()으로 한 척만 조회 추천
    """
    url = f"{BASE_URL}/locations"         # 요청할 주소 완성
    response = requests.get(              # GET 요청 보내기
        url,
        headers=HEADERS,
        timeout=30                        # 30초 넘으면 타임아웃
    )
    response.raise_for_status()           # 에러 발생 시 예외 던지기 (404, 500 등)
    return response.json()                # JSON 응답을 파이썬 dict로 변환


@st.cache_data(ttl=60)
def get_vessel_location(mmsi: int):
    """
    📍 특정 선박 한 척의 현재 위치를 가져옵니다.

    매개변수:
        mmsi (int): 선박의 고유 번호 (MMSI, 9자리 숫자)
                    예시: 230935000

    반환값:
        dict - 해당 선박의 GeoJSON Feature

    💡 MMSI란?
       Maritime Mobile Service Identity의 약자로,
       모든 선박에 부여된 9자리 고유 식별번호
    """
    url = f"{BASE_URL}/locations/{mmsi}"
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=300)  # 5분 캐시 (메타데이터는 자주 변하지 않으므로)
def get_all_vessels():
    """
    🚢 모든 선박의 상세 정보(메타데이터)를 가져옵니다.

    반환값:
        list[dict] - 선박 정보가 담긴 딕셔너리의 리스트
        예시: [
            {
                "name": "NORD SUPERIOR",
                "mmsi": 219598000,
                "shipType": 80,      ← 유조선
                "destination": "NL AMS",
                "draught": 118,      ← 흘수 (1/10m 단위)
                ...
            }, ...
        ]
    """
    url = f"{BASE_URL}/vessels"
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=300)
def get_vessel_metadata(mmsi: int):
    """
    🚢 특정 선박 한 척의 상세 정보를 가져옵니다.

    매개변수:
        mmsi (int): 선박의 MMSI 번호
    """
    url = f"{BASE_URL}/vessels/{mmsi}"
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    return response.json()


# ─── 이 파일을 직접 실행하여 테스트하기 ──────────────
# 터미널에서: python api/ais_client.py
if __name__ == "__main__":
    print("🔄 AIS API 테스트 - 전체 선박 위치 가져오기...")
    try:
        # Streamlit 캐시는 직접 실행 시 작동하지 않으므로
        # requests를 직접 호출
        url = f"{BASE_URL}/locations"
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        data = response.json()

        # 처음 3개 선박만 출력
        features = data.get("features", [])
        print(f"✅ 총 {len(features)}척의 선박 데이터를 가져왔습니다!")
        print(f"📅 데이터 업데이트: {data.get('dataUpdatedTime', 'N/A')}")
        print()

        for i, ship in enumerate(features[:3]):
            coords = ship["geometry"]["coordinates"]
            props = ship["properties"]
            print(f"  [{i+1}] MMSI: {props['mmsi']}")
            print(f"      위치: 위도 {coords[1]}, 경도 {coords[0]}")
            print(f"      속력: {props['sog']} knots")
            print(f"      침로: {props['cog']}°")
            print()

    except Exception as e:
        print(f"❌ API 호출 실패: {e}")
