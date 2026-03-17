"""
=============================================================
📊 Step 1: 데이터 처리 모듈 (data_processing.py)
=============================================================

이 파일은 AIS API에서 받아온 원시 데이터(JSON/GeoJSON)를
분석하기 쉬운 pandas DataFrame 형태로 변환하는 함수들을 모아놓은 모듈입니다.

📌 왜 변환이 필요한가?
   - API 응답은 복잡한 중첩 JSON 구조
   - DataFrame으로 변환하면 표 형태로 보기 쉽고, 필터링/정렬이 간단해짐

📌 좌표 순서 주의! ⚠️
   - GeoJSON 표준: [경도(longitude), 위도(latitude)] 순서
   - 일반적 지도 표기: (위도, 경도) 순서
   - 이 모듈에서 좌표를 올바르게 분리하여 저장합니다
=============================================================
"""

import pandas as pd


# ─── 선종 코드 → 한글 이름 변환 테이블 ──────────────
# AIS에서는 선박 종류를 숫자 코드로 전송합니다.
# 이 딕셔너리로 숫자를 사람이 읽을 수 있는 이름으로 바꿉니다.
SHIP_TYPE_MAP = {
    # 30번대: 특수 선박
    30: "어선",
    31: "예인선",  32: "예인선",  33: "준설선",  34: "잠수 작업선",
    35: "군함",    36: "범선",    37: "요트",
    # 40번대: 고속선
    40: "고속선",  41: "고속선",  42: "고속선",  43: "고속선",  49: "고속선",
    # 50번대: 특수 목적선
    50: "수색구조선", 51: "수색구조선", 52: "수색구조선",
    53: "해양경찰",   54: "오염방제선", 55: "경비정",
    # 60번대: 여객선 🛳️
    60: "여객선",  61: "여객선",  62: "여객선",  63: "여객선",  69: "여객선",
    # 70번대: 화물선 🚢
    70: "화물선",  71: "화물선",  72: "화물선",  73: "화물선",  79: "화물선",
    # 80번대: 유조선 ⛽
    80: "유조선",  81: "유조선",  82: "유조선",  83: "유조선",  89: "유조선",
    # 90번대: 기타
    90: "기타",    91: "기타",    99: "기타",
}


def locations_to_dataframe(geojson: dict) -> pd.DataFrame:
    """
    📍 선박 위치 GeoJSON 데이터를 DataFrame으로 변환합니다.

    매개변수:
        geojson (dict): API에서 받은 GeoJSON FeatureCollection

    반환값:
        pd.DataFrame: 아래 컬럼을 포함하는 표
        - mmsi: 선박 고유 번호 (9자리)
        - latitude: 위도 (예: 60.1234)
        - longitude: 경도 (예: 24.5678)
        - sog: Speed Over Ground, 대지 속력 (knots)
        - cog: Course Over Ground, 대지 침로 (도)
        - heading: 선수 방향 (도)
        - navStat: 항행 상태 코드 (0=항행 중, 1=정박 등)
    """
    rows = []  # 각 선박의 정보를 담을 리스트

    # features 리스트에서 선박 하나씩 꺼내기
    for feature in geojson.get("features", []):

        # 좌표 추출: GeoJSON은 [경도, 위도] 순서!
        coords = feature.get("geometry", {}).get("coordinates", [None, None])

        # 속성(properties) 추출
        props = feature.get("properties", {})

        # 딕셔너리로 정리하여 리스트에 추가
        rows.append({
            "mmsi":      props.get("mmsi"),
            "longitude": coords[0],      # 첫 번째 = 경도
            "latitude":  coords[1],      # 두 번째 = 위도
            "sog":       props.get("sog", 0),       # 속력 (기본값 0)
            "cog":       props.get("cog", 0),       # 침로
            "heading":   props.get("heading", 0),   # 선수 방향
            "navStat":   props.get("navStat", 0),   # 항행 상태
        })

    # 리스트를 DataFrame으로 변환
    return pd.DataFrame(rows)


def vessels_to_dataframe(vessels: list) -> pd.DataFrame:
    """
    🚢 선박 메타데이터 JSON 배열을 DataFrame으로 변환합니다.

    매개변수:
        vessels (list): API에서 받은 선박 정보 리스트

    반환값:
        pd.DataFrame: 아래 컬럼을 포함하는 표
        - mmsi: 선박 고유 번호
        - name: 선박 이름 (예: "NORD SUPERIOR")
        - shipType: 선종 코드 (숫자)
        - shipTypeName: 선종 이름 (한글, 예: "유조선")
        - destination: 목적지 (선박이 AIS에 직접 입력한 값)
        - imo: IMO 번호 (국제해사기구 식별번호)
        - callSign: 호출부호
        - draught: 흘수 (미터 단위로 변환됨)
    """
    rows = []

    for v in vessels:
        ship_type = v.get("shipType", 0)

        rows.append({
            "mmsi":         v.get("mmsi"),
            "name":         v.get("name", "UNKNOWN"),
            "shipType":     ship_type,
            "shipTypeName": SHIP_TYPE_MAP.get(ship_type, "기타"),  # 코드→한글
            "destination":  v.get("destination", ""),
            "imo":          v.get("imo", 0),
            "callSign":     v.get("callSign", ""),
            "draught":      v.get("draught", 0) / 10,  # API: 1/10m → 변환: m
        })

    return pd.DataFrame(rows)


def merge_location_and_vessel(
    loc_df: pd.DataFrame,
    vessel_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    🔗 위치 DataFrame과 선박 메타데이터 DataFrame을 합칩니다.

    두 테이블을 MMSI(선박 고유 번호) 기준으로 합쳐서
    "이 위치에 있는 선박의 이름과 목적지는 무엇인가?"를
    한 눈에 볼 수 있게 만듭니다.

    매개변수:
        loc_df: 위치 DataFrame (locations_to_dataframe의 결과)
        vessel_df: 메타데이터 DataFrame (vessels_to_dataframe의 결과)

    반환값:
        pd.DataFrame: 합쳐진 DataFrame
    """
    # MMSI를 기준으로 왼쪽 조인 (위치 데이터 기준으로 합치기)
    merged = pd.merge(loc_df, vessel_df, on="mmsi", how="left")

    # 이름이 없는 선박은 MMSI를 이름 대신 사용
    merged["name"] = merged["name"].fillna(merged["mmsi"].astype(str))

    return merged
