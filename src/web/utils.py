"""
Utility functions for the dashboard
대시보드 유틸리티 함수들
"""

import os
import re
import pandas as pd
import geopandas as gpd
import streamlit as st


def norm_txt(x: str) -> str:
    """
    텍스트를 정규화합니다.
    
    Args:
        x: 입력 문자열
        
    Returns:
        str: 정규화된 문자열
    """
    if x is None:
        return ""
    s = str(x)
    s = re.sub(r"\s+", "", s)
    s = re.sub(r"[()\-]", "", s)
    return s


@st.cache_data(show_spinner=False)
def load_geojson(path: str):
    """
    GeoJSON 파일을 로드하고 전처리합니다.
    
    Args:
        path: GeoJSON 파일 경로
        
    Returns:
        geopandas.GeoDataFrame: 전처리된 GeoDataFrame
    """
    gdf = gpd.read_file(path)
    gdf = gdf.copy()
    gdf["adm_cd"] = gdf["adm_cd"].astype(str)
    # split adm_nm → [시, 구, 동]
    def split_gu_dong(adm_nm: str):
        toks = str(adm_nm).split()
        gu = toks[1] if len(toks) >= 2 else None
        dong = toks[2] if len(toks) >= 3 else None
        return pd.Series({"gu": gu, "dong_geo": dong})
    gdf[["gu", "dong_geo"]] = gdf["adm_nm"].apply(split_gu_dong)
    gdf["gu_n"] = gdf["gu"].apply(norm_txt)
    gdf["dong_geo_n"] = gdf["dong_geo"].apply(norm_txt)
    return gdf


def ensure_list(x, fallback_all):
    """
    입력값이 비어있으면 fallback_all을 리스트로 반환합니다.
    
    Args:
        x: 입력값
        fallback_all: 대체값
        
    Returns:
        list: 리스트 형태의 값
    """
    if not x:
        return list(fallback_all)
    return x


def get_secret(key, default=None):
    """
    Streamlit secrets 또는 환경변수에서 값을 가져옵니다.
    
    Args:
        key: 키 이름
        default: 기본값
        
    Returns:
        str: 설정된 값 또는 기본값
    """
    try:
        return st.secrets[key]
    except Exception:
        return os.environ.get(key, default)
