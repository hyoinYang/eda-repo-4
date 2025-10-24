"""
Main dashboard application
메인 대시보드 애플리케이션
"""

import streamlit as st

# Import custom modules
from config import PAGE_TITLE, PAGE_LAYOUT
from ui import render_sidebar, render_all_charts
from data import load_dashboard_data, prepare_sales_data


def main():
    """메인 대시보드 애플리케이션을 실행합니다."""
    # 페이지 설정
    st.set_page_config(page_title=PAGE_TITLE, layout=PAGE_LAYOUT)
    
    # 사이드바 렌더링 및 필터 값 가져오기
    selected_area_codes, sel_cats, areas_key, cats_key, df_areas, all_categories = render_sidebar()
    
    # 데이터 로딩
    df_sales, df_fpop, df_pga, df_income = load_dashboard_data(
        selected_area_codes, sel_cats, areas_key, cats_key
    )
    
    # 매출 데이터 전처리
    df_sales = prepare_sales_data(df_sales, df_areas, selected_area_codes)
    
    # 모든 차트 렌더링
    render_all_charts(
        selected_area_codes, sel_cats, all_categories,
        df_sales, df_fpop, df_pga, df_income, df_areas
    )


if __name__ == "__main__":
    main()