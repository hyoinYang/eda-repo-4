"""
Data module for the dashboard
대시보드 데이터 모듈
"""

from src.web.data.query import (
    fetch_areas_and_categories, fetch_sales_2024, fetch_floating_by_area_2024,
    fetch_population_ga_2024, fetch_income_2024, fetch_dong_map_for_areas
)
from src.web.data.data_loader import load_dashboard_data, prepare_sales_data

__all__ = [
    'fetch_areas_and_categories',
    'fetch_sales_2024',
    'fetch_floating_by_area_2024',
    'fetch_population_ga_2024',
    'fetch_income_2024',
    'fetch_dong_map_for_areas',
    'load_dashboard_data',
    'prepare_sales_data'
]
