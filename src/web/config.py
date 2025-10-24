"""
Configuration settings for the Seoul Commercial Area Analysis Dashboard
서울시 상권별 외식업 분석 대시보드 설정
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ===============================
# ⚙️ CONFIG
# ===============================

# Page configuration
PAGE_TITLE = "서울시 상권별 외식업 분석 대시보드"
PAGE_LAYOUT = "wide"

# Database configuration
DB_URL = os.getenv("DB_URL")

# External API keys
KAKAO_JS_KEY = os.getenv("KAKAO_JAVASCRIPT_KEY")

# --- 외식 10종 목록 ---
FOOD10 = [
    "한식음식점", "중식음식점", "일식음식점", "양식음식점",
    "제과점", "패스트푸드점", "치킨전문점", "분식전문점",
    "호프-간이주점", "커피-음료",
]

# Year-Quarter range for 2024
ALL_YQ = (20241, 20244)  # 2024 Q1~Q4

# --- GeoJSON 경로 (고정 사용) ---
GEOJSON_PATH = Path(__file__).parent / "../../data/서울_행정동_경계_2017.geojson"

# Chart configuration
CHART_HEIGHT = 350
CHART_TEMPLATE = "plotly_white"

# Color schemes
BASE_COLORS = ["#636EFA", "#EF553B"]  # 1st: 파랑, 2nd: 빨강
POPULATION_COLORS = ["#1f77b4", "#2ca02c"]  # 상주, 직장인구
EXPENDITURE_COLORS = ["#636EFA", "#EF553B"]  # 총지출, 음식지출

# Map configuration
DEFAULT_MAP_LEVEL = 5
KOREA_LAT_RANGE = (33, 39)
KOREA_LON_RANGE = (124, 132)

# Time periods for analysis
TIME_PERIODS = ["t00_06", "t06_11", "t11_14", "t14_17", "t17_21", "t21_24"]
TIME_LABELS = ["00-06", "06-11", "11-14", "14-17", "17-21", "21-24"]
TIME_X_VALS = [3, 8.5, 12.5, 15.5, 19, 22.5]  # 중심 시각

# Day labels
DAY_LABELS = ["월", "화", "수", "목", "금", "토", "일"]
DAY_COLUMNS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

# Gender labels
GENDER_LABELS = ["남성", "여성"]
GENDER_COLUMNS = ["male", "female"]

# Population types
POPULATION_TYPES = ["상주", "직장"]
POPULATION_COLUMNS = ["resident", "worker"]

# Expenditure types
EXPENDITURE_TYPES = ["총지출", "음식지출"]
EXPENDITURE_COLUMNS = ["total_expenditure", "food_expenditure"]
