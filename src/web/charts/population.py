"""
Population chart generation functions
인구 관련 차트 생성 함수들
"""

import plotly.graph_objects as go
from config import (
    CHART_HEIGHT, CHART_TEMPLATE, POPULATION_COLORS,
    TIME_PERIODS, TIME_LABELS, TIME_X_VALS, DAY_LABELS, DAY_COLUMNS,
    GENDER_LABELS, GENDER_COLUMNS, POPULATION_TYPES, POPULATION_COLUMNS
)


def create_gender_day_chart(df_fpop, selected_area_codes, df_sales):
    """
    성별·요일별 유동인구 구성비 차트를 생성합니다.
    
    Args:
        df_fpop: 유동인구 데이터
        selected_area_codes: 선택된 상권 코드 리스트
        df_sales: 매출 데이터
        
    Returns:
        plotly.graph_objects.Figure: 성별·요일별 유동인구 차트
    """
    # Build per-area or average across areas that match selected filters
    if selected_area_codes:
        # Single or multiple: show average across selected areas
        f = df_fpop[df_fpop["commercial_area_code"].isin(selected_area_codes)]
    else:
        # No area selected → average across all areas that have the selected categories
        # Find areas that have sales for selected cats (already in df_sales)
        area_pool = df_sales["commercial_area_code"].unique().tolist()
        f = df_fpop[df_fpop["commercial_area_code"].isin(area_pool)]

    if f.empty:
        return None

    # Average across selected areas
    f_days = f[DAY_COLUMNS].mean()
    f_gender = f[GENDER_COLUMNS].mean()
    # 100% 비중 계산
    day_pct = (f_days / f_days.sum() * 100).round(1)
    gender_pct = (f_gender / f_gender.sum() * 100).round(1)

    fig = go.Figure()
    # 요일별 막대
    fig.add_bar(
        x=DAY_LABELS,
        y=day_pct,
        name="요일별 구성비(%)",
        hovertemplate="%{x}: %{y:.1f}%<extra></extra>"
    )
    # 성별 막대(꺾은선 대신 막대)
    fig.add_bar(
        x=GENDER_LABELS,
        y=gender_pct,
        name="성별 비중(%)",
        hovertemplate="%{x}: %{y:.1f}%<extra></extra>"
    )

    fig.update_layout(
        template=CHART_TEMPLATE,
        height=CHART_HEIGHT,
        showlegend=True,
        yaxis=dict(title="비중(%)", range=[0,100]),
        xaxis=dict(title=None)
    )
    return fig


def create_time_population_chart(df_fpop, selected_area_codes):
    """
    시간대별 유동인구 차트를 생성합니다.
    
    Args:
        df_fpop: 유동인구 데이터
        selected_area_codes: 선택된 상권 코드 리스트
        
    Returns:
        plotly.graph_objects.Figure: 시간대별 유동인구 차트
    """
    # 기준 데이터 선택
    # - 지역만 선택 시: 해당 상권
    # - 업종만/미선택 시: 서울시 전체
    if selected_area_codes:
        f = df_fpop[df_fpop["commercial_area_code"].isin(selected_area_codes)].copy()
    else:
        f = df_fpop.copy()

    if f.empty:
        return None

    # 전체 시간대별 평균
    total_by_time = f[TIME_PERIODS].mean().to_numpy(dtype=float)

    # 꺾은선(검은색)
    fig = go.Figure()
    fig.add_scatter(
        x=TIME_X_VALS, y=total_by_time, mode="lines+markers",
        name="전체", line=dict(color="#000000", width=3),
        hovertemplate="%{text}: %{y:,}<extra></extra>", text=TIME_LABELS
    )
    fig.update_layout(
        template=CHART_TEMPLATE, height=CHART_HEIGHT,
        xaxis=dict(
            title=None, type="linear",
            tickmode="array", tickvals=TIME_X_VALS, ticktext=TIME_LABELS,
            range=[0, 24]  # 0~24시 고정
        ),
        yaxis=dict(title="유동인구"),
        showlegend=False
    )
    return fig


def create_population_chart(df_pga, selected_area_codes, df_sales):
    """
    상주·직장 인구 차트를 생성합니다.
    
    Args:
        df_pga: 상주/직장 인구 데이터
        selected_area_codes: 선택된 상권 코드 리스트
        df_sales: 매출 데이터
        
    Returns:
        plotly.graph_objects.Figure: 상주·직장 인구 차트
    """
    if selected_area_codes:
        p = df_pga[df_pga["commercial_area_code"].isin(selected_area_codes)]
    else:
        area_pool = df_sales["commercial_area_code"].unique().tolist()
        p = df_pga[df_pga["commercial_area_code"].isin(area_pool)]

    if p.empty:
        return None

    vals = p[POPULATION_COLUMNS].mean()
    fig = go.Figure()
    fig.add_bar(
        x=POPULATION_TYPES, 
        y=vals.values, 
        marker_color=POPULATION_COLORS,
        hovertemplate="%{x}: %{y:,}<extra></extra>"
    )
    fig.update_layout(
        template=CHART_TEMPLATE, 
        height=CHART_HEIGHT,
        yaxis=dict(title="상주, 직장인구")
    )
    return fig
