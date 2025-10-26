"""
Recommendation analysis functions
추천 시스템 분석 함수들
"""

import streamlit as st
from src.web.data.query import (
    fetch_commercial_area_analysis,
    fetch_business_category_analysis,
    fetch_customer_demographics,
    fetch_category_demographics,
    fetch_population_patterns,
    fetch_time_patterns,
    fetch_category_time_patterns
)


def analyze_selected_area(area_name, df_areas):
    """선택된 상권을 분석합니다."""
    
    # 상권 코드 찾기
    area_info = df_areas[df_areas['area_name'] == area_name].iloc[0]
    area_code = area_info['commercial_area_code']
    
    # 분석 데이터 로드
    with st.spinner("분석 데이터를 불러오는 중..."):
        # 상권별 분석 데이터
        area_analysis = fetch_commercial_area_analysis(area_code)
        
        # 고객 인구통계
        demographics = fetch_customer_demographics(area_code)
        
        # 인구 패턴
        population_patterns = fetch_population_patterns(area_code)
        
        # 시간대별 패턴
        time_patterns = fetch_time_patterns(area_code)
    
    return area_name, area_info, area_analysis, demographics, population_patterns, time_patterns


def analyze_selected_category(category_name):
    """선택된 업종을 분석합니다."""

    # 분석 데이터 로드
    with st.spinner("분석 데이터를 불러오는 중..."):
        # 업종별 분석 데이터
        category_analysis = fetch_business_category_analysis(category_name)
        
        # 업종별 고객 특성
        category_demographics = fetch_category_demographics(category_name)
        
        # 업종별 시간대별 유동인구 패턴
        category_time_patterns = fetch_category_time_patterns(category_name)
    
    return category_name, category_analysis, category_demographics, category_time_patterns
