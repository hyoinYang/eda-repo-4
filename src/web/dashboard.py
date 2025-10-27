"""
Main dashboard application
메인 대시보드 애플리케이션
"""
import streamlit as st
from config import PAGE_TITLE, PAGE_LAYOUT
from ui import render_sidebar_for_recommand, display_area_analysis_results, display_category_analysis_results
from analyzer import analyze_selected_area, analyze_selected_category
from data.query import fetch_time_patterns, fetch_areas_and_categories
from charts import create_sales_comparison_chart, create_population_chart, create_expenditure_chart
from data import load_dashboard_data, prepare_sales_data



def main():
    st.set_page_config(layout="wide")

    """상권 추천 페이지를 렌더링합니다."""
    
    st.title("🏪 상권 추천 시스템")
    
    # 사이드바 렌더링
    recommend_type, selected_area, selected_category, df_areas, categories = render_sidebar_for_recommand()
    
    # 분석 실행
    if st.session_state.get('analyze_area', False):
        st.session_state['analyze_area'] = False
        # 상권 분석
        area_name, area_info, area_analysis, demographics, population_patterns, time_patterns = analyze_selected_area(
            st.session_state['selected_area'], df_areas
        )
        
        area_code = area_info['commercial_area_code']
        additional_time_patterns = fetch_time_patterns(area_code)
        
        # 데이터 로딩 (상주/직장인구 차트용)
        _, all_categories = fetch_areas_and_categories()
        
        df_sales_chart, df_fpop_chart, df_pga_chart, df_income_chart = load_dashboard_data(
            [area_code], all_categories, f"area_{area_code}", "all_categories"
        )
        df_sales_chart = prepare_sales_data(df_sales_chart, df_areas, [area_code])
        
        # 상주/직장인구 차트 생성 (2. 상주/직장인구와 동일)
        population_chart = create_population_chart(df_pga_chart, [area_code], df_sales_chart)
        
        # 결과 표시
        display_area_analysis_results(area_name, area_info, area_analysis, demographics, population_patterns, time_patterns, population_chart)
        
        # 대시보드 차트들 추가
        st.markdown("---")
        st.subheader("📊 상권 상세 분석")
        
        # 상권명 기반 분석 차트들
        _render_area_based_charts(area_code, df_areas)
        
    elif st.session_state.get('analyze_category', False):
        st.session_state['analyze_category'] = False
        # 업종 분석
        category_name, category_analysis, category_demographics, category_time_patterns = analyze_selected_category(
            st.session_state['selected_category']
        )
        # 결과 표시
        display_category_analysis_results(category_name, category_analysis, category_demographics, category_time_patterns)
        
        # 대시보드 차트들 추가
        st.markdown("---")
        st.subheader("상세 분석")
        
        # 업종 기반 분석 차트들
        _render_category_based_charts(category_name)


def _render_area_based_charts(area_code, df_areas):
    """상권 기반 분석 차트들을 렌더링합니다."""
    
    # 카테고리 정보 가져오기
    from data.query import fetch_areas_and_categories
    _, all_categories = fetch_areas_and_categories()
    
    # 데이터 로딩
    with st.spinner("상권 분석 데이터 로딩 중..."):
        df_sales, df_fpop, df_pga, df_income = load_dashboard_data(
            [area_code], all_categories, f"area_{area_code}", "all_categories"
        )
        
        # 매출 데이터 전처리
        df_sales = prepare_sales_data(df_sales, df_areas, [area_code])
    
    # 2x2 레이아웃
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. 연간평균매출액 & 해당 상권 매출액")
        fig = create_sales_comparison_chart([area_code], all_categories, all_categories)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("매출 데이터를 불러올 수 없습니다.")
    
    with col2:
        st.subheader("2. 총지출/음식지출")
        fig, title = create_expenditure_chart(df_income, [area_code], df_areas)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("지출 데이터를 불러올 수 없습니다.")


def _render_category_based_charts(category_name):
    """업종 기반 분석 차트들을 렌더링합니다."""
    
    # 카테고리 정보 가져오기
    from data.query import fetch_areas_and_categories
    _, all_categories = fetch_areas_and_categories()
    
    # 데이터 로딩
    with st.spinner("업종 분석 데이터 로딩 중..."):
        df_sales, df_fpop, df_pga, df_income = load_dashboard_data(
            [], [category_name], "all_areas", f"category_{category_name}"
        )
    
        st.subheader("전체 외식업 평균 매출액 & 업종의 서울시 평균 매출액")
        fig = create_sales_comparison_chart([], [category_name], all_categories)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("매출 데이터를 불러올 수 없습니다.")



if __name__ == "__main__":
    main()