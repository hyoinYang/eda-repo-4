"""
Chart rendering functions for the dashboard
대시보드 차트 렌더링 관련 함수들
"""

import streamlit as st
import streamlit.components.v1 as components
from charts import (
    create_sales_comparison_chart, create_gender_day_chart, create_time_population_chart,
    create_population_chart, create_expenditure_chart, create_kakao_map
)
from utils import get_secret


def render_all_charts(selected_area_codes, sel_cats, all_categories, 
                     df_sales, df_fpop, df_pga, df_income, df_areas):
    """
    모든 차트를 렌더링합니다.
    
    Args:
        selected_area_codes: 선택된 상권 코드 리스트
        sel_cats: 선택된 카테고리 리스트
        all_categories: 전체 카테고리 리스트
        df_sales: 매출 데이터
        df_fpop: 유동인구 데이터
        df_pga: 상주/직장 인구 데이터
        df_income: 소득/지출 데이터
        df_areas: 상권 데이터
    """
    st.title("📊 서울시 상권별 외식업 분석 - 대시보드")
    
    # 2x3 레이아웃 생성
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    col5, col6 = st.columns(2)

    # 각 차트 렌더링
    with col1:
        _render_sales_chart(selected_area_codes, sel_cats, all_categories)
    
    with col2:
        _render_gender_day_chart(df_fpop, selected_area_codes, df_sales)
    
    with col3:
        _render_time_population_chart(df_fpop, selected_area_codes)
    
    with col4:
        _render_population_chart(df_pga, selected_area_codes, df_sales)
    
    with col5:
        _render_expenditure_chart(df_income, selected_area_codes, df_areas)
    
    with col6:
        _render_kakao_map(selected_area_codes, df_areas)


def _render_sales_chart(selected_area_codes, sel_cats, all_categories):
    """매출 비교 차트를 렌더링합니다."""
    st.subheader("1. 상권별/업종별 연간 매출액")
    
    fig = create_sales_comparison_chart(selected_area_codes, sel_cats, all_categories)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("상단에서 상권 또는 업종을 선택해 주세요.")


def _render_gender_day_chart(df_fpop, selected_area_codes, df_sales):
    """성별·요일별 유동인구 구성비 차트를 렌더링합니다."""
    st.subheader("2. 성별 · 요일별 유동인구 구성비")
    
    fig = create_gender_day_chart(df_fpop, selected_area_codes, df_sales)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("선택 조건에 해당하는 유동인구 데이터가 없습니다.")


def _render_time_population_chart(df_fpop, selected_area_codes):
    """시간대별 유동인구 차트를 렌더링합니다."""
    st.subheader("3. 시간대별 유동인구 (분기별 평균)")
    
    fig = create_time_population_chart(df_fpop, selected_area_codes)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("선택 조건에 해당하는 유동인구 데이터가 없습니다.")


def _render_population_chart(df_pga, selected_area_codes, df_sales):
    """상주·직장 인구 차트를 렌더링합니다."""
    st.subheader("4. 상주 · 직장 인구 (분기별 평균)")
    
    fig = create_population_chart(df_pga, selected_area_codes, df_sales)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("선택 조건에 해당하는 상주/직장 인구 데이터가 없습니다.")


def _render_expenditure_chart(df_income, selected_area_codes, df_areas):
    """지출 차트를 렌더링합니다."""
    st.subheader("5. 상권 소속 동의 연간 총지출 · 음식지출")
    
    fig, title = create_expenditure_chart(df_income, selected_area_codes, df_areas)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("해당 조건의 동 지출 데이터가 없습니다.")


def _render_kakao_map(selected_area_codes, df_areas):
    """카카오 맵을 렌더링합니다."""
    st.subheader("6. 상권 위치 (Kakao Map)")

    KAKAO_JS_KEY = get_secret("KAKAO_JAVASCRIPT_KEY")
    if not KAKAO_JS_KEY:
        st.error("카카오 JavaScript 키가 없습니다. .env 또는 secrets.toml에 'KAKAO_JAVASCRIPT_KEY'를 설정하세요.")
        st.stop()

    if not selected_area_codes:
        st.info("사이드바에서 상권을 1개 선택하면 해당 위치로 지도가 표시됩니다.")
    else:
        html = create_kakao_map(selected_area_codes, df_areas)
        if html:
            components.html(html, height=350)
        else:
            st.warning("선택한 상권의 좌표(lat/lon)를 찾을 수 없습니다.")
