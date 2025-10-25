"""
Main dashboard application
메인 대시보드 애플리케이션
"""

import streamlit as st

from config import PAGE_TITLE, PAGE_LAYOUT
from ui import render_sidebar_for_recommand, display_area_analysis_results, display_category_analysis_results
from analyzer import analyze_selected_area, analyze_selected_category
from data.query import fetch_time_patterns



def main():
    """메인 대시보드 애플리케이션을 실행합니다."""
    
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
        
        # 결과 표시
        display_area_analysis_results(area_name, area_info, area_analysis, demographics, population_patterns, time_patterns)
        
    elif st.session_state.get('analyze_category', False):
        st.session_state['analyze_category'] = False
        # 업종 분석
        category_name, category_analysis, category_demographics, category_time_patterns = analyze_selected_category(
            st.session_state['selected_category']
        )
        # 결과 표시
        display_category_analysis_results(category_name, category_analysis, category_demographics, category_time_patterns)


if __name__ == "__main__":
    main()