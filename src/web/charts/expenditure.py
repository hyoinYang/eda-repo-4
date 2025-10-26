"""
Expenditure chart generation functions
지출 차트 생성 함수들
"""

import plotly.graph_objects as go
import streamlit as st
from config import CHART_HEIGHT, CHART_TEMPLATE, EXPENDITURE_COLORS, EXPENDITURE_TYPES


def create_expenditure_chart(df_income, selected_area_codes, df_areas):
    """
    지출 차트를 생성합니다.
    
    Args:
        df_income: 소득/지출 데이터
        selected_area_codes: 선택된 상권 코드 리스트
        df_areas: 상권 데이터
        
    Returns:
        tuple: (차트, 제목) 또는 (None, None)
    """
    if selected_area_codes:
        # Use the first selected area's dong_code (or combine if multiple)
        pick = df_areas[df_areas["commercial_area_code"].isin(selected_area_codes)]
        if pick.empty:
            return None, None
        else:
            # If multiple areas, show top 1 by sales or list selector
            if len(pick) > 1:
                pick_name = st.selectbox("어느 상권의 소속 동을 보시겠습니까?", options=pick["area_name"].tolist())
                pick = pick[pick["area_name"] == pick_name]
            row = pick.iloc[0]
            dcode, dname = row["dong_code"], row["dong"]
            di = df_income[df_income["dong_code"] == dcode]
            if di.empty:
                return None, None
            else:
                total = float(di["total_expenditure"].sum())
                food  = float(di["food_expenditure"].sum())
                fig = go.Figure()
                fig.add_bar(
                    x=EXPENDITURE_TYPES, 
                    y=[total, food], 
                    marker_color=EXPENDITURE_COLORS,
                    hovertemplate="%{x}: %{y:,}<extra></extra>"
                )
                fig.update_layout(
                    title=f"{dname} — 2024 지출", 
                    template=CHART_TEMPLATE, 
                    height=CHART_HEIGHT,
                    yaxis=dict(title="금액(원)")
                )
                return fig, f"{dname} — 2024 지출"
    else:
        # Only category selected → 평균(해당 업종 보유 상권들의 소속 동 기준 평균)
        # 1) 상권 풀
        area_pool = df_areas["commercial_area_code"].unique().tolist()
        dpool = df_areas[df_areas["commercial_area_code"].isin(area_pool)]["dong_code"].unique().tolist()
        di = df_income[df_income["dong_code"].isin(dpool)]
        if di.empty:
            return None, None
        else:
            # 평균: 동별 합계 → 평균
            agg = di.groupby("dong_code", as_index=False).agg(
                total=("total_expenditure","sum"),
                food=("food_expenditure","sum")
            )
            total_avg = float(agg["total"].mean())
            food_avg  = float(agg["food"].mean())
            fig = go.Figure()
            fig.add_bar(
                x=["총지출(평균)","음식지출(평균)"], 
                y=[total_avg, food_avg],
                marker_color=EXPENDITURE_COLORS,
                hovertemplate="%{x}: %{y:,}<extra></extra>"
            )
            fig.update_layout(
                title="해당 업종 보유 상권의 소속 동 평균 지출 (2024)",
                template=CHART_TEMPLATE, 
                height=CHART_HEIGHT,
                yaxis=dict(title="금액(원)")
            )
            return fig, "해당 업종 보유 상권의 소속 동 평균 지출 (2024)"
    
    return None, None
