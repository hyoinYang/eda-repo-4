"""
Data loading functions for the dashboard
대시보드 데이터 로딩 관련 함수들
"""

import streamlit as st
from src.web.data.query import (
    fetch_sales_2024, fetch_floating_by_area_2024,
    fetch_population_ga_2024, fetch_income_2024
)
from src.web.config import ALL_YQ


def load_dashboard_data(selected_area_codes, sel_cats, areas_key, cats_key):
    """
    대시보드에 필요한 모든 데이터를 로드합니다.
    
    Args:
        selected_area_codes: 선택된 상권 코드 리스트
        sel_cats: 선택된 카테고리 리스트
        areas_key: 상권 키
        cats_key: 카테고리 키
        
    Returns:
        tuple: (df_sales, df_fpop, df_pga, df_income)
    """
    with st.spinner("데이터 로딩 중…"):
        df_sales = fetch_sales_2024(selected_area_codes, sel_cats, cache_key=("sales", areas_key, cats_key))
        df_fpop = fetch_floating_by_area_2024(selected_area_codes, cache_key=("fpop", areas_key))
        df_pga = fetch_population_ga_2024(selected_area_codes, cache_key=("pga", areas_key))
        df_income = fetch_income_2024(cache_key=("income", ALL_YQ))

    return df_sales, df_fpop, df_pga, df_income


def prepare_sales_data(df_sales, df_areas, selected_area_codes):
    """
    매출 데이터를 전처리합니다.
    
    Args:
        df_sales: 매출 데이터
        df_areas: 상권 데이터
        selected_area_codes: 선택된 상권 코드 리스트
        
    Returns:
        pd.DataFrame: 전처리된 매출 데이터
    """
    # Join area metadata
    df_sales = df_sales.merge(df_areas, on="commercial_area_code", how="left")

    # If area not selected (aggregate view), we still want area-level rows for mapping/averages by cat
    if not selected_area_codes:
        # Join with df_areas to keep all areas; fill NaN sales as 0
        df_sales = df_areas[["commercial_area_code","area_name","gu","dong","lon","lat","dong_code"]] \
            .merge(df_sales, on=["commercial_area_code","area_name","gu","dong","lon","lat","dong_code"], how="left")
        df_sales["sales_sum_2024"] = df_sales["sales_sum_2024"].fillna(0)

    return df_sales
