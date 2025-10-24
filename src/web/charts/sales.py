"""
Sales chart generation functions
매출 차트 생성 함수들
"""

import plotly.graph_objects as go
from config import CHART_HEIGHT, CHART_TEMPLATE, BASE_COLORS
from data.query import fetch_sales_2024


def create_sales_comparison_chart(selected_area_codes, sel_cats, all_categories):
    """
    매출 비교 차트를 생성합니다.
    
    Args:
        selected_area_codes: 선택된 상권 코드 리스트
        sel_cats: 선택된 카테고리 리스트
        all_categories: 전체 카테고리 리스트
        
    Returns:
        plotly.graph_objects.Figure: 매출 비교 차트
    """
    # 상태 판정
    is_area_selected = len(selected_area_codes) == 1
    is_cats_all = set(sel_cats) == set(all_categories)  # 업종 전체 선택인지 여부

    # 헬퍼
    def get_city_avg(cats: list[str]) -> float:
        df_all = fetch_sales_2024(selected_areas=None, selected_cats=cats, cache_key=("avg", tuple(sorted(cats))))
        if df_all.empty:
            return 0.0
        return float(df_all["sales_sum_2024"].mean())

    def get_area_sum(area_codes: list[int], cats: list[str]) -> float:
        df_area = fetch_sales_2024(selected_areas=area_codes, selected_cats=cats, cache_key=("area", tuple(area_codes), tuple(sorted(cats))))
        if df_area.empty:
            return 0.0
        # 단일 상권만 선택하므로 하나면 충분
        return float(df_area["sales_sum_2024"].sum())

    bars = []
    labels = []

    if is_area_selected and is_cats_all:
        # 지역만 선택 시 -> 서울시 외식업 전체 평균 매출, 선택상권 외식업 매출
        city_avg_all = get_city_avg(all_categories)
        area_sum_all = get_area_sum(selected_area_codes, all_categories)
        labels = ["서울시 평균(전체 외식업)", "선택 상권(전체 외식업)"]
        bars = [city_avg_all, area_sum_all]

    elif (not is_area_selected) and (not is_cats_all):
        # 업종만 선택 시 -> 서울시 외식업 전체 평균 매출, 해당업종 서울시 평균 매출
        city_avg_all = get_city_avg(all_categories)
        city_avg_sel = get_city_avg(sel_cats)
        labels = ["서울시 평균(전체 외식업)", "서울시 평균(선택 업종)"]
        bars = [city_avg_all, city_avg_sel]

    elif is_area_selected and (not is_cats_all):
        # 교차선택 시 -> 해당 상권 외식업 전체 매출, 해당 업종 해당 상권 매출
        area_sum_all = get_area_sum(selected_area_codes, all_categories)
        area_sum_sel = get_area_sum(selected_area_codes, sel_cats)
        labels = ["선택 상권(전체 외식업)", "선택 상권(선택 업종)"]
        bars = [area_sum_all, area_sum_sel]

    else:
        return None

    if bars:
        fig = go.Figure()
        # 두 번째만 빨간색(#EF553B)
        fig.add_bar(
            x=labels,
            y=bars,
            marker_color=BASE_COLORS[:len(bars)],
            hovertemplate="%{x}: %{y:,.0f}원<extra></extra>"
        )
        fig.update_layout(
            template=CHART_TEMPLATE,
            height=CHART_HEIGHT,
            yaxis=dict(title="매출(원)"),
            xaxis=dict(title=None)
        )
        return fig
    
    return None
