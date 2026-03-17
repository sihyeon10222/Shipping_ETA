"""
=============================================================
⏱️ Step 4: ETA 계산 모듈 (eta_calculator.py)
=============================================================

이 파일은 선박의 현재 위치와 목적지 사이의 거리를 계산하고,
현재 속력(SOG)을 바탕으로 예상 도착 시간(ETA)을 산출합니다.

📌 ETA란?
   Estimated Time of Arrival (예상 도착 시간)

📌 핵심 공식:
   1. Haversine 공식 → 지구 위 두 점 사이의 거리 계산 (해리 단위)
   2. ETA = 거리(해리) ÷ 속력(노트)

📌 단위 설명:
   - 해리 (Nautical Mile, NM): 해상에서 사용하는 거리 단위 (1NM ≈ 1.852km)
   - 노트 (Knot, kn): 해상 속력 단위 (1kn = 1해리/시간)
   - 따라서 거리(해리) ÷ 속력(노트) = 시간(시간)

📌 Haversine 공식이란?
   지구가 둥글기 때문에, 두 좌표 사이의 거리를 직선이 아닌
   구면(球面) 위의 호(弧)로 계산하는 공식입니다.
=============================================================
"""

import math
from datetime import datetime, timedelta


def haversine_distance(
    lat1: float, lon1: float,
    lat2: float, lon2: float,
) -> float:
    """
    📏 두 좌표 사이의 거리를 Haversine 공식으로 계산합니다.

    매개변수:
        lat1, lon1: 출발지의 위도, 경도 (도 단위)
        lat2, lon2: 목적지의 위도, 경도 (도 단위)

    반환값:
        float: 두 점 사이의 거리 (해리, Nautical Miles)

    예시:
        >>> haversine_distance(60.17, 24.94, 59.44, 24.75)
        44.36  # 헬싱키 → 탈린 약 44해리
    """

    # 지구의 반지름 (해리 단위)
    R_NM = 3440.065

    # 도(degree) → 라디안(radian) 변환
    # 삼각함수는 라디안 단위를 사용하기 때문
    lat1_r = math.radians(lat1)
    lat2_r = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)   # 위도 차이
    dlon = math.radians(lon2 - lon1)   # 경도 차이

    # Haversine 공식 핵심 계산
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # 최종 거리 = 반지름 × 호의 각도
    distance = R_NM * c
    return distance


def calculate_eta(
    lat: float, lon: float,
    dest_lat: float, dest_lon: float,
    sog: float,
) -> dict:
    """
    ⏱️ 현재 위치에서 목적지까지의 ETA를 계산합니다.

    매개변수:
        lat, lon: 선박의 현재 위치 (위도, 경도)
        dest_lat, dest_lon: 목적지 좌표 (위도, 경도)
        sog: 현재 속력 (노트, knots)

    반환값:
        dict: {
            "distance_nm":   거리 (해리),
            "sog_knots":     속력 (노트),
            "travel_hours":  예상 소요 시간 (시간) 또는 None,
            "eta_datetime":  예상 도착 시각 (datetime) 또는 None,
        }

    ⚠️ 주의:
       - SOG가 0이면 (정지 상태) ETA를 계산할 수 없습니다
       - 이 계산은 직선 거리 기반의 간단한 추정치입니다
       - 실제 항해는 해류, 항로, 기상 등의 영향을 받습니다
    """

    # 1. 거리 계산 (해리)
    distance = haversine_distance(lat, lon, dest_lat, dest_lon)

    # 2. 속력이 0이면 계산 불가
    if sog <= 0:
        return {
            "distance_nm":  round(distance, 2),
            "sog_knots":    sog,
            "travel_hours": None,         # 계산 불가
            "eta_datetime": None,         # 계산 불가
        }

    # 3. 소요 시간 = 거리 ÷ 속력
    #    예: 100해리 ÷ 10노트 = 10시간
    travel_hours = distance / sog

    # 4. 예상 도착 시각 = 현재 시각 + 소요 시간
    eta_dt = datetime.utcnow() + timedelta(hours=travel_hours)

    return {
        "distance_nm":  round(distance, 2),
        "sog_knots":    sog,
        "travel_hours": round(travel_hours, 2),
        "eta_datetime": eta_dt,
    }


# ─── 이 파일을 직접 실행하여 테스트하기 ──────────────
if __name__ == "__main__":
    print("📏 Haversine 거리 계산 테스트")
    print("=" * 40)

    # 테스트: 헬싱키(60.17, 24.94) → 탈린(59.44, 24.75)
    dist = haversine_distance(60.17, 24.94, 59.44, 24.75)
    print(f"헬싱키 → 탈린 거리: {dist:.2f} 해리 ({dist * 1.852:.2f} km)")

    print()
    print("⏱️ ETA 계산 테스트")
    print("=" * 40)

    # 속력 15노트로 항행 중
    result = calculate_eta(60.17, 24.94, 59.44, 24.75, sog=15)
    print(f"거리: {result['distance_nm']} NM")
    print(f"속력: {result['sog_knots']} knots")
    print(f"예상 소요: {result['travel_hours']}시간")
    print(f"도착 예정: {result['eta_datetime']}")
