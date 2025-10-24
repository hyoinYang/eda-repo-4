"""
Database query functions for the Seoul Commercial Area Analysis Dashboard
서울시 상권별 외식업 분석 대시보드 데이터베이스 쿼리 함수들
"""

import pandas as pd
from sqlalchemy import create_engine, text
import streamlit as st
from config import DB_URL, FOOD10, ALL_YQ


# Database engine
engine = create_engine(DB_URL, pool_pre_ping=True, future=True)


@st.cache_data(show_spinner=False)
def fetch_areas_and_categories():
    """
    상권 정보와 카테고리 정보를 가져옵니다.
    
    Returns:
        tuple: (상권 데이터프레임, 카테고리 리스트)
    """
    q = """
    SELECT ca.code   AS commercial_area_code,
           ca.name   AS area_name,
           ca.gu, ca.dong, ca.dong_code, ca.lon, ca.lat
    FROM Commercial_Area ca
    WHERE ca.lon IS NOT NULL AND ca.lat IS NOT NULL
    ORDER BY ca.gu, ca.dong, ca.name
    """
    df_areas = pd.read_sql(text(q), engine)

    qcat = "SELECT name AS category_name FROM Service_Category WHERE name IN :names ORDER BY name"
    df_cats = pd.read_sql(text(qcat), engine, params={"names": tuple(FOOD10)})

    return df_areas, df_cats["category_name"].tolist()


@st.cache_data(show_spinner=False)
def fetch_sales_2024(selected_areas: list[int] | None, selected_cats: list[str], cache_key=None):
    """
    2024년 매출 데이터를 가져옵니다.
    
    Args:
        selected_areas: 선택된 상권 코드 리스트
        selected_cats: 선택된 카테고리 리스트
        cache_key: 캐시 키
        
    Returns:
        pd.DataFrame: 매출 데이터
    """
    # Sum 2024 Sales_Daytype by area, filtered by categories and/or areas
    where = ["sc.year_quarter BETWEEN :q1 AND :q4", "cat.name IN :cats"]
    params = {"q1": ALL_YQ[0], "q4": ALL_YQ[1], "cats": tuple(selected_cats)}
    if selected_areas:
        where.append("sc.commercial_area_code IN :areas")
        params["areas"] = tuple(int(x) for x in selected_areas)

    sql = f"""
    SELECT sc.commercial_area_code,
           SUM(sdt.sales) AS sales_sum_2024
    FROM Shop_Count sc
    JOIN Sales_Daytype sdt    ON sdt.store_id = sc.id
    JOIN Service_Category cat ON cat.code = sc.service_category_code
    WHERE {' AND '.join(where)}
    GROUP BY sc.commercial_area_code
    """
    return pd.read_sql(text(sql), engine, params=params)


@st.cache_data(show_spinner=False)
def fetch_floating_by_area_2024(selected_areas: list[int] | None, cache_key=None):
    """
    2024년 지역별 유동인구 데이터를 가져옵니다.
    
    Args:
        selected_areas: 선택된 상권 코드 리스트
        cache_key: 캐시 키
        
    Returns:
        pd.DataFrame: 유동인구 데이터
    """
    where = ["year_quarter BETWEEN :q1 AND :q4"]
    params = {"q1": ALL_YQ[0], "q4": ALL_YQ[1]}
    if selected_areas:
        where.append("commercial_area_code IN :areas")
        params["areas"] = tuple(int(x) for x in selected_areas)

    sql = f"""
    SELECT commercial_area_code,
           AVG(mon_pop) AS mon, AVG(tue_pop) AS tue, AVG(wed_pop) AS wed,
           AVG(thu_pop) AS thu, AVG(fri_pop) AS fri, AVG(sat_pop) AS sat, AVG(sun_pop) AS sun,
           AVG(t00_06_pop) AS t00_06, AVG(t06_11_pop) AS t06_11, AVG(t11_14_pop) AS t11_14,
           AVG(t14_17_pop) AS t14_17, AVG(t17_21_pop) AS t17_21, AVG(t21_24_pop) AS t21_24,
           AVG(male_pop) AS male, AVG(female_pop) AS female
    FROM Floating_Population
    WHERE {' AND '.join(where)}
    GROUP BY commercial_area_code
    """
    return pd.read_sql(text(sql), engine, params=params)


@st.cache_data(show_spinner=False)
def fetch_population_ga_2024(selected_areas: list[int] | None, cache_key=None):
    """
    2024년 상주/직장 인구 데이터를 가져옵니다.
    
    Args:
        selected_areas: 선택된 상권 코드 리스트
        cache_key: 캐시 키
        
    Returns:
        pd.DataFrame: 상주/직장 인구 데이터
    """
    # Sum by quarter then average across quarters, per area_code and pop_type
    where = ["year_quarter BETWEEN :q1 AND :q4"]
    params = {"q1": ALL_YQ[0], "q4": ALL_YQ[1]}
    if selected_areas:
        where.append("pg.commercial_area_code IN :areas")
        params["areas"] = tuple(int(x) for x in selected_areas)

    sql = f"""
    WITH agg AS (
      SELECT year_quarter, pg.commercial_area_code, pg.pop_type,
             SUM(pg.population) AS pop_sum
      FROM Population_GA pg
      WHERE {' AND '.join(where)}
      GROUP BY year_quarter, pg.commercial_area_code, pg.pop_type
    )
    SELECT commercial_area_code,
           MAX(CASE WHEN pop_type='RESIDENT' THEN pop_avg ELSE 0 END) AS resident,
           MAX(CASE WHEN pop_type='WORKING'  THEN pop_avg ELSE 0 END) AS worker
    FROM (
      SELECT commercial_area_code, pop_type, AVG(pop_sum) AS pop_avg
      FROM agg
      GROUP BY commercial_area_code, pop_type
    ) t
    GROUP BY commercial_area_code
    """
    return pd.read_sql(text(sql), engine, params=params)


@st.cache_data(show_spinner=False)
def fetch_income_2024(cache_key=None):
    """
    2024년 소득/지출 데이터를 가져옵니다.
    
    Args:
        cache_key: 캐시 키
        
    Returns:
        pd.DataFrame: 소득/지출 데이터
    """
    sql = f"""
    SELECT i.dong_code,
           d.name AS dong_name,
           SUM(i.total_expenditure) AS total_expenditure,
           SUM(i.food_expenditure)  AS food_expenditure
    FROM Income i
    JOIN Dong d ON d.code = i.dong_code
    WHERE i.year_quarter BETWEEN :q1 AND :q4
    GROUP BY i.dong_code, d.name
    """
    return pd.read_sql(text(sql), engine, params={"q1": ALL_YQ[0], "q4": ALL_YQ[1]})


@st.cache_data(show_spinner=False)
def fetch_dong_map_for_areas():
    """
    상권 코드와 동 정보 매핑 데이터를 가져옵니다.
    
    Returns:
        pd.DataFrame: 상권-동 매핑 데이터
    """
    # For mapping commercial_area_code → (dong_code, area metadata)
    sql = """
    SELECT ca.code AS commercial_area_code, ca.name AS area_name, ca.gu, ca.dong, ca.lon, ca.lat,
           ca.dong_code, d.name AS dong_name
    FROM Commercial_Area ca
    LEFT JOIN Dong d ON d.code = ca.dong_code
    WHERE ca.lon IS NOT NULL AND ca.lat IS NOT NULL
    """
    return pd.read_sql(text(sql), engine)
