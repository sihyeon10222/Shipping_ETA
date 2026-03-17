"""
=============================================================
📋 Step 2: 데이터 테이블 컴포넌트 (data_table.py)
=============================================================

이 파일은 선박 데이터를 Streamlit의 표(테이블)로 보여주고,
사용자가 이름 검색이나 선종 필터로 원하는 선박을 찾을 수 있게 합니다.

📌 사용된 Streamlit 기능:
   - st.text_input(): 텍스트 입력 상자
   - st.selectbox(): 드롭다운 선택 상자
   - st.dataframe(): 인터랙티브 데이터 테이블
   - st.columns(): 가로로 나란히 배치
   - st.caption(): 작은 글씨의 설명문
=============================================================
"""

import streamlit as st
import pandas as pd


# ─── 테이블에 표시할 컬럼 설정 ──────────────────────
# 딕셔너리의 키 = DataFrame 컬럼명, 값 = 화면에 표시할 한글 이름
DISPLAY_COLUMNS = {
    "name":         "선박명",
    "mmsi":         "MMSI",
    "shipTypeName": "선종",
    "sog":          "속력(kn)",
    "cog":          "침로(°)",
    "heading":      "선수방향(°)",
    "destination":  "목적지",
    "latitude":     "위도",
    "longitude":    "경도",
    "draught":      "흘수(m)",
    "callSign":     "호출부호",
}


def show_vessel_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    📋 선박 데이터 테이블을 표시하고, 필터링 기능을 제공합니다.

    매개변수:
        df (pd.DataFrame): 병합된 선박 데이터

    반환값:
        pd.DataFrame: 필터링이 적용된 DataFrame

    💡 동작 흐름:
       1. 선박 이름 검색 + 선종 필터 UI 표시
       2. 입력에 따라 DataFrame 필터링
       3. 필터된 결과를 테이블로 표시
    """
    st.subheader("📋 선박 데이터 테이블")

    # ── 필터 UI 만들기 (가로 2칸 배치) ──
    col1, col2 = st.columns(2)

    with col1:
        # 선박 이름 검색 입력창
        search_name = st.text_input(
            "🔍 선박 이름 검색",
            placeholder="예: NORD SUPERIOR",
            key="search_name",
        )

    with col2:
        # 선종 드롭다운 필터
        ship_types = ["전체"] + sorted(
            df["shipTypeName"].dropna().unique().tolist()
        )
        selected_type = st.selectbox(
            "⛴️ 선종 필터",
            ship_types,
            key="ship_type",
        )

    # ── 필터 적용 ──
    filtered_df = df.copy()   # 원본 데이터를 보존하기 위해 복사

    # 이름 검색 필터
    if search_name:
        filtered_df = filtered_df[
            filtered_df["name"]
            .str.contains(search_name.upper(), case=False, na=False)
        ]

    # 선종 필터
    if selected_type != "전체":
        filtered_df = filtered_df[
            filtered_df["shipTypeName"] == selected_type
        ]

    # ── 표시할 컬럼만 골라서 한글 이름으로 변경 ──
    available_cols = [c for c in DISPLAY_COLUMNS if c in filtered_df.columns]
    display_df = filtered_df[available_cols].rename(columns=DISPLAY_COLUMNS)

    # ── 통계 표시 ──
    st.caption(f"총 **{len(display_df)}**척 표시 중 (전체 {len(df)}척)")

    # ── 테이블 출력 ──
    st.dataframe(
        display_df,
        use_container_width=True,   # 화면 너비에 맞춤
        hide_index=True,            # 인덱스 번호 숨기기
        height=400,                 # 테이블 높이 (픽셀)
    )

    return filtered_df
