"""
=============================================================
🚢 eta-route-app — 메인 Streamlit 앱 (app.py)
=============================================================

이 파일은 Streamlit 웹 애플리케이션의 진입점(entry point)입니다.
모든 모듈(API, 데이터 처리, 지도, ETA)을 하나로 조합합니다.

📌 실행 방법:
   streamlit run app.py

📌 앱 구조:
   ┌──────────────────────────────────────┐
   │  사이드바 (설정)                      │
   │  - 데이터 범위 선택                   │
   │  - MMSI 번호 입력                     │
   │  - 목적지 좌표 입력                   │
   ├──────────────────────────────────────┤
   │  메인 영역 (3개 탭)                   │
   │  탭1: 🗺️ 지도 — 선박 위치 시각화      │
   │  탭2: 📋 테이블 — 선박 데이터 목록     │
   │  탭3: ⏱️ ETA — 도착 시간 계산         │
   └──────────────────────────────────────┘

📌 데이터 출처: © Fintraffic / digitraffic.fi (CC 4.0 BY)
=============================================================
"""

# ─── 라이브러리 가져오기 ────────────────────────────

import streamlit as st          # Streamlit 웹 프레임워크
import pandas as pd             # 데이터 처리
import folium                   # 지도 (마커 추가용)
from streamlit_folium import st_folium  # Streamlit 안에 Folium 지도 표시

# 우리가 만든 모듈들 가져오기
from api.ais_client import (           # Step 1: API 호출
    get_all_locations,
    get_all_vessels,
    get_vessel_location,
)
from utils.data_processing import (     # Step 1: 데이터 변환
    locations_to_dataframe,
    vessels_to_dataframe,
    merge_location_and_vessel,
)
from utils.eta_calculator import calculate_eta    # Step 4: ETA 계산
from components.map_view import (       # Step 3: 지도 시각화
    create_vessel_map,
    add_route_line,
)
from components.data_table import show_vessel_table  # Step 2: 데이터 테이블


# ═══════════════════════════════════════════════════
#  1. 페이지 기본 설정
# ═══════════════════════════════════════════════════

st.set_page_config(
    page_title="🚢 Ship Tracker & ETA",   # 브라우저 탭에 표시될 제목
    page_icon="🚢",                       # 브라우저 탭의 아이콘
    layout="wide",                        # 넓은 레이아웃 사용
    initial_sidebar_state="expanded",     # 사이드바를 열린 상태로 시작
)

# 앱 제목과 설명 표시
st.title("🚢 AIS 선박 위치 추적 & ETA 계산기")
st.caption("데이터 출처: © Fintraffic / digitraffic.fi (CC 4.0 BY)")


# ═══════════════════════════════════════════════════
#  2. 사이드바 — 설정 패널
# ═══════════════════════════════════════════════════

with st.sidebar:
    st.header("⚙️ 설정")

    # ── 데이터 새로고침 버튼 ──
    # 클릭하면 캐시를 삭제하고 앱을 다시 실행
    if st.button("🔄 데이터 새로고침", use_container_width=True):
        st.cache_data.clear()   # 캐시에 저장된 데이터 삭제
        st.rerun()              # 앱 새로고침

    st.divider()  # 구분선

    # ── 데이터 범위 선택 ──
    data_mode = st.radio(
        "📡 데이터 범위",
        ["전체 선박 (느림)", "특정 MMSI 조회"],
        index=1,   # 기본값: "특정 MMSI 조회" (두 번째 항목)
    )

    # 특정 MMSI 입력 (data_mode가 "특정 MMSI 조회"일 때만)
    target_mmsi = None
    if data_mode == "특정 MMSI 조회":
        target_mmsi = st.number_input(
            "MMSI 번호 입력",
            min_value=100000000,       # 최소 9자리
            max_value=999999999,       # 최대 9자리
            value=230935000,           # 기본값 (핀란드 선박)
            help="9자리 MMSI 번호를 입력하세요",
        )

    st.divider()

    # ── ETA 목적지 좌표 입력 ──
    st.subheader("📍 ETA 목적지 설정")
    dest_lat = st.number_input(
        "목적지 위도", value=59.44, format="%.4f"
    )
    dest_lon = st.number_input(
        "목적지 경도", value=24.75, format="%.4f"
    )
    st.caption("기본값: 에스토니아 탈린 항구")


# ═══════════════════════════════════════════════════
#  3. API에서 데이터 로드
# ═══════════════════════════════════════════════════

@st.cache_data(ttl=60)
def load_data(mode: str, mmsi: int = None):
    """
    API에서 선박 데이터를 가져와 DataFrame으로 변환합니다.

    매개변수:
        mode: "전체 선박 (느림)" 또는 "특정 MMSI 조회"
        mmsi: 특정 MMSI 번호 (mode가 특정 MMSI일 때만 사용)

    반환값:
        pd.DataFrame: 위치 + 메타데이터가 합쳐진 DataFrame
    """
    # Step 1-A: 위치 데이터 가져오기
    if mode == "특정 MMSI 조회" and mmsi:
        loc_data = get_vessel_location(mmsi)  # 한 척만
    else:
        loc_data = get_all_locations()        # 전체

    # Step 1-B: 선박 메타데이터 가져오기
    vessel_data = get_all_vessels()

    # Step 1-C: JSON → DataFrame 변환
    loc_df = locations_to_dataframe(loc_data)
    vessel_df = vessels_to_dataframe(vessel_data)

    # Step 1-D: 두 데이터를 MMSI 기준으로 합치기
    merged_df = merge_location_and_vessel(loc_df, vessel_df)

    return merged_df


# 데이터 로드 실행
try:
    with st.spinner("🔄 AIS 데이터를 불러오는 중..."):
        df = load_data(data_mode, target_mmsi)

    # 데이터가 비어있으면 경고 후 중단
    if df.empty:
        st.warning("⚠️ 조회된 선박 데이터가 없습니다.")
        st.stop()

    # 사이드바에 성공 메시지 표시
    st.sidebar.success(f"✅ {len(df)}척 로드 완료")

except Exception as e:
    # API 호출 실패 시 에러 메시지
    st.error(f"❌ API 호출 실패: {e}")
    st.info("💡 인터넷 연결을 확인하거나, 잠시 후 다시 시도해주세요.")
    st.stop()


# ═══════════════════════════════════════════════════
#  4. 메인 영역 — 3개 탭 구성
# ═══════════════════════════════════════════════════

tab_map, tab_table, tab_eta = st.tabs([
    "🗺️ 지도",          # Step 3: 지도 시각화
    "📋 데이터 테이블",   # Step 2: 데이터 테이블
    "⏱️ ETA 계산",       # Step 4: ETA 계산
])


# ─── 탭 1: 🗺️ 지도 ────────────────────────────────
with tab_map:
    st.subheader("🗺️ 선박 위치 지도")

    # 지도 중심을 데이터의 평균 좌표로 설정
    center_lat = df["latitude"].mean() if not df["latitude"].isna().all() else 60.0
    center_lon = df["longitude"].mean() if not df["longitude"].isna().all() else 24.0

    # Step 3: 선박 마커가 포함된 지도 생성
    vessel_map = create_vessel_map(df, center_lat, center_lon, zoom=7)

    # 목적지 마커 추가 (빨간 깃발)
    folium.Marker(
        location=[dest_lat, dest_lon],
        icon=folium.Icon(color="red", icon="flag", prefix="fa"),
        tooltip="🎯 ETA 목적지",
        popup=f"목적지: ({dest_lat}, {dest_lon})",
    ).add_to(vessel_map)

    # Streamlit에 지도 표시
    st_folium(vessel_map, width=None, height=500, use_container_width=True)

    # 범례 표시
    st.markdown(
        "**범례**: 🔵 여객선 | 🟢 화물선 | 🔴 유조선 | "
        "🟠 수색구조선 | 🟣 범선 | ⚪ 기타"
    )


# ─── 탭 2: 📋 데이터 테이블 ────────────────────────
with tab_table:
    # Step 2: 필터 + 테이블 표시
    show_vessel_table(df)


# ─── 탭 3: ⏱️ ETA 계산 ────────────────────────────
with tab_eta:
    st.subheader("⏱️ ETA (예상 도착 시간) 계산")

    # 목적지 정보 표시
    st.info(
        f"🎯 **목적지 좌표**: 위도 {dest_lat}°, 경도 {dest_lon}° "
        f"(사이드바에서 변경 가능)"
    )

    # ── 선박 선택 드롭다운 ──
    vessel_options = df[["mmsi", "name"]].drop_duplicates()
    vessel_options["label"] = (
        vessel_options["name"]
        + " ("
        + vessel_options["mmsi"].astype(str)
        + ")"
    )

    selected_label = st.selectbox(
        "🚢 ETA를 계산할 선박 선택",
        vessel_options["label"].tolist(),
    )

    if selected_label:
        # 선택한 선박의 MMSI 추출
        selected_mmsi = int(selected_label.split("(")[-1].replace(")", ""))
        vessel_row = df[df["mmsi"] == selected_mmsi].iloc[0]

        # 선박 정보 꺼내기
        v_lat = vessel_row["latitude"]
        v_lon = vessel_row["longitude"]
        v_sog = vessel_row["sog"]
        v_name = vessel_row["name"]

        # Step 4: ETA 계산 실행
        eta_result = calculate_eta(v_lat, v_lon, dest_lat, dest_lon, v_sog)

        # ── 선박 정보 표시 ──
        st.markdown(f"### 🚢 {v_name}")
        st.markdown(
            f"**현재 위치**: ({v_lat:.4f}°, {v_lon:.4f}°) | "
            f"**현재 속력**: {v_sog} knots"
        )

        # ── 3개 지표를 가로로 배치 ──
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("📏 거리", f"{eta_result['distance_nm']} NM")

        with col2:
            if eta_result["travel_hours"] is not None:
                hours = eta_result["travel_hours"]
                days = int(hours // 24)
                remaining = hours % 24
                if days > 0:
                    time_str = f"{days}일 {remaining:.1f}시간"
                else:
                    time_str = f"{hours:.1f}시간"
                st.metric("⏳ 예상 소요", time_str)
            else:
                st.metric("⏳ 예상 소요", "계산 불가")

        with col3:
            if eta_result["eta_datetime"] is not None:
                eta_str = eta_result["eta_datetime"].strftime(
                    "%Y-%m-%d %H:%M UTC"
                )
                st.metric("🕐 예상 도착", eta_str)
            else:
                st.metric("🕐 예상 도착", "정지 상태")

        # 정지 상태 경고
        if v_sog <= 0:
            st.warning(
                "⚠️ 선박이 정지 상태(SOG=0)이므로 ETA를 계산할 수 없습니다."
            )

        # ── 선박 → 목적지 경로 지도 ──
        st.divider()
        st.markdown("#### 🗺️ 선박 → 목적지 경로")

        route_map = create_vessel_map(
            df[df["mmsi"] == selected_mmsi],
            center_lat=(v_lat + dest_lat) / 2,
            center_lon=(v_lon + dest_lon) / 2,
            zoom=6,
        )
        route_map = add_route_line(
            route_map,
            coordinates=[(v_lat, v_lon), (dest_lat, dest_lon)],
            vessel_name=v_name,
            color="red",
        )
        st_folium(
            route_map, width=None, height=400, use_container_width=True
        )


# ═══════════════════════════════════════════════════
#  5. 푸터
# ═══════════════════════════════════════════════════

st.divider()
st.caption(
    "© Fintraffic / digitraffic.fi | Creative Commons 4.0 BY | "
    "eta-route-app student project"
)
