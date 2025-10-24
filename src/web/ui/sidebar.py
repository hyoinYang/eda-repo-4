"""
Sidebar functions for the dashboard
대시보드 사이드바 관련 함수들
"""

import streamlit as st
from data import fetch_areas_and_categories, fetch_dong_map_for_areas


def render_sidebar():
    """
    사이드바를 렌더링하고 필터 값을 반환합니다.
    
    Returns:
        tuple: (selected_area_codes, sel_cats, areas_key, cats_key, df_areas, all_categories)
    """
    st.sidebar.header("🔎 필터")

    # 데이터 로드
    df_areas, all_categories = fetch_areas_and_categories()
    df_dongmap = fetch_dong_map_for_areas()

    # 상권 선택
    selected_area_codes = _render_area_selector(df_areas)
    
    # 업종 선택
    sel_cats = _render_category_selector(all_categories)
    
    # 캐시 키 계산
    areas_key = tuple(sorted(int(x) for x in (selected_area_codes or [])))
    cats_key = tuple(sorted(sel_cats))

    # 안내 메시지
    st.sidebar.info(
        "상권 필수 선택. 업종 선택 조회. 둘 다 선택 시 교차 조회합니다.\n\n"
        "- 상권만 선택 → 해당 상권의 전체 외식업 기준\n"
    )

    # 캐시/디버그 섹션
    _render_debug_section()

    return selected_area_codes, sel_cats, areas_key, cats_key, df_areas, all_categories

def render_sidebar_for_recommand():
    """
    추천 시스템용 사이드바를 렌더링합니다.
    
    Returns:
        tuple: (recommend_type, selected_area, selected_category, df_areas, categories)
    """
    st.sidebar.header("🎯 추천 시스템")
    
    # 추천 타입 선택
    st.sidebar.subheader("📊 추천 유형 선택")
    recommend_type = st.sidebar.radio(
        "어떤 추천을 받고 싶으신가요?",
        ["상권명 기반 분석", "업종 기반 추천"]
    )
    
    # 데이터 로드
    with st.spinner("데이터 로딩 중..."):
        df_areas, categories = fetch_areas_and_categories()
    
    selected_area = None
    selected_category = None
    
    if recommend_type == "상권명 기반 분석":
        st.sidebar.subheader("📍 상권 선택")
        selected_area = st.sidebar.selectbox(
            "추천받을 상권을 선택하세요:",
            options=df_areas['area_name'].tolist(),
        )
        
        if st.sidebar.button("🔍 상권 분석 시작", type="primary"):
            st.session_state['analyze_area'] = True
            st.session_state['selected_area'] = selected_area
    else:
        st.sidebar.subheader("🍽️ 업종 선택")
        selected_category = st.sidebar.selectbox(
            "추천받을 업종을 선택하세요:",
            options=categories,
        )
        
        if st.sidebar.button("🔍 업종 분석 시작", type="primary"):
            st.session_state['analyze_category'] = True
            st.session_state['selected_category'] = selected_category
    
    return recommend_type, selected_area, selected_category, df_areas, categories


def _render_area_selector(df_areas):
    """상권 선택 UI를 렌더링합니다."""
    # Area select (single) — "상권이름 (구 동)" 형식
    df_areas = df_areas.copy()
    df_areas["gu"] = df_areas["gu"].fillna("")
    df_areas["dong"] = df_areas["dong"].fillna("")
    df_areas["area_label"] = df_areas["area_name"] + " (" + df_areas["gu"] + " " + df_areas["dong"] + ")"

    sel_area_label = st.sidebar.selectbox(
        "상권 선택 (1개만 선택 가능)",
        options=["(선택 안 함)"] + sorted(df_areas["area_label"].unique().tolist())
    )

    if sel_area_label == "(선택 안 함)":
        selected_area_codes = []
    else:
        selected_area_codes = df_areas.loc[
            df_areas["area_label"] == sel_area_label, "commercial_area_code"
        ].astype(int).head(1).tolist()
    
    return selected_area_codes


def _render_category_selector(all_categories):
    """업종 선택 UI를 렌더링합니다."""
    cat_options = ["(전체 10종)"] + list(all_categories)

    selected_cat = st.sidebar.selectbox(
        "업종 선택 (단일 선택)",
        options=cat_options,
    )

    if selected_cat == "(전체 10종)":
        sel_cats = list(all_categories)   # 전체 선택
    else:
        sel_cats = [selected_cat]         # 단일 업종만
    
    return sel_cats


def _render_debug_section():
    """디버그/캐시 섹션을 렌더링합니다."""
    with st.sidebar.expander("⚙️ 캐시 / 디버그"):
        if st.button("캐시 비우기 & 새로고침", use_container_width=True):
            st.cache_data.clear()
            if hasattr(st, "rerun"):
                st.rerun()
            else:
                st.experimental_rerun()
