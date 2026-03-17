"""
=============================================================
🗺️ Step 3: 지도 시각화 컴포넌트 (map_view.py)
=============================================================

이 파일은 Folium 라이브러리를 사용하여
선박 위치를 지도 위에 마커로 표시하는 기능을 담당합니다.

📌 Folium이란?
   - Python에서 Leaflet.js 기반의 인터랙티브 지도를 만드는 라이브러리
   - HTML 지도를 생성하므로 Streamlit 내에서도 표시 가능

📌 핵심 개념:
   - CircleMarker: 원형 마커 (선박 위치 표시용)
   - Popup: 마커 클릭 시 나타나는 정보창
   - PolyLine: 두 점을 잇는 선 (경로 표시용)

📌 선종별 색상:
   여객선=파랑, 화물선=초록, 유조선=빨강 등으로 구분하여
   한눈에 선박 종류를 파악할 수 있게 합니다.
=============================================================
"""

import folium       # 지도 생성 라이브러리
import pandas as pd


# ─── 선종별 마커 색상 설정 ──────────────────────────
# 선종 이름(한글)을 키로, 마커 색상을 값으로 매핑
SHIP_TYPE_COLORS = {
    "여객선":     "blue",        # 🔵
    "화물선":     "green",       # 🟢
    "유조선":     "red",         # 🔴
    "수색구조선": "orange",      # 🟠
    "범선":       "purple",      # 🟣
    "예인선":     "darkblue",    # 🔵 (진한)
    "고속선":     "cadetblue",   # 🔵 (연한)
    "기타":       "gray",        # ⚪
}


def create_vessel_map(
    df: pd.DataFrame,
    center_lat: float = 60.0,
    center_lon: float = 24.0,
    zoom: int = 6,
) -> folium.Map:
    """
    🗺️ 선박 위치가 표시된 Folium 지도를 생성합니다.

    매개변수:
        df: 선박 데이터 DataFrame
            (latitude, longitude, name, sog, cog, shipTypeName 등 포함)
        center_lat: 지도의 초기 중심 위도 (기본값: 60.0 = 핀란드 부근)
        center_lon: 지도의 초기 중심 경도 (기본값: 24.0 = 헬싱키 부근)
        zoom: 초기 줌 레벨 (숫자가 클수록 확대, 기본값: 6)

    반환값:
        folium.Map: 마커가 추가된 지도 객체
    """

    # ── 1. 빈 지도 생성 ──
    m = folium.Map(
        location=[center_lat, center_lon],   # 중심 좌표
        zoom_start=zoom,                     # 줌 레벨
        tiles="CartoDB positron",            # 지도 스타일 (밝은 배경)
    )

    # ── 2. 각 선박을 마커로 추가 ──
    for _, row in df.iterrows():  # DataFrame의 각 행을 순회

        lat = row.get("latitude")
        lon = row.get("longitude")

        # 좌표가 없으면 건너뜀
        if pd.isna(lat) or pd.isna(lon):
            continue

        # 선박 정보 꺼내기
        name = row.get("name", "UNKNOWN")
        sog = row.get("sog", 0)
        cog = row.get("cog", 0)
        destination = row.get("destination", "")
        ship_type_name = row.get("shipTypeName", "기타")

        # 선종에 따른 마커 색상 결정
        color = SHIP_TYPE_COLORS.get(ship_type_name, "gray")

        # 팝업에 표시할 HTML (마커 클릭 시 나타남)
        popup_html = f"""
        <div style="font-family: sans-serif; font-size: 13px; min-width: 160px;">
            <b>🚢 {name}</b><br>
            <b>MMSI:</b> {row.get('mmsi', '')}<br>
            <b>선종:</b> {ship_type_name}<br>
            <b>속력:</b> {sog} knots<br>
            <b>침로:</b> {cog}°<br>
            <b>목적지:</b> {destination}
        </div>
        """

        # 원형 마커 추가
        folium.CircleMarker(
            location=[lat, lon],          # ⚠️ Folium은 [위도, 경도] 순서!
            radius=5,                     # 원의 크기 (픽셀)
            color=color,                  # 테두리 색
            fill=True,                    # 내부 채우기
            fill_color=color,             # 채우기 색
            fill_opacity=0.8,             # 투명도 (0~1)
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"{name} ({sog} kn)", # 마우스 올리면 보이는 텍스트
        ).add_to(m)

    return m


def add_route_line(
    m: folium.Map,
    coordinates: list,
    vessel_name: str = "Route",
    color: str = "blue",
) -> folium.Map:
    """
    📍 지도 위에 선박 이동 경로(선)를 추가합니다.

    매개변수:
        m: 기존 Folium 지도 객체
        coordinates: [(위도, 경도), (위도, 경도), ...] 형태의 리스트
        vessel_name: 경로에 표시할 선박 이름
        color: 경로 선의 색상

    반환값:
        folium.Map: 경로가 추가된 지도 객체
    """
    # 좌표가 2개 미만이면 선을 그을 수 없음
    if len(coordinates) < 2:
        return m

    # 경로 선 추가 (PolyLine)
    folium.PolyLine(
        locations=coordinates,    # 좌표 리스트
        color=color,              # 선 색상
        weight=3,                 # 선 두께
        opacity=0.7,              # 선 투명도
        tooltip=f"📍 {vessel_name} 이동 경로",
    ).add_to(m)

    # 출발점 마커 (초록색 ▶)
    folium.Marker(
        location=coordinates[0],
        icon=folium.Icon(color="green", icon="play", prefix="fa"),
        tooltip="출발",
    ).add_to(m)

    # 도착점 마커 (빨간색 🚩)
    folium.Marker(
        location=coordinates[-1],
        icon=folium.Icon(color="red", icon="flag", prefix="fa"),
        tooltip="현재 위치",
    ).add_to(m)

    return m
