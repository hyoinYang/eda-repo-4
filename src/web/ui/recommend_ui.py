"""
Recommendation UI functions
추천 시스템 UI 함수들
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from config import TIME_X_VALS, TIME_LABELS, DAY_LABELS, GENDER_LABELS
from data.query import (
    fetch_commercial_area_analysis,
    fetch_business_category_analysis,
    fetch_customer_demographics,
    fetch_category_demographics,
    fetch_population_patterns,
    fetch_time_patterns
)
from charts.map import create_kakao_map


def display_area_analysis_results(area_name, area_info, area_analysis, demographics, population_patterns, time_patterns):
    """상권 분석 결과를 표시합니다."""
    
    st.markdown("---")
    st.subheader(f"📊 '{area_name}' 상권 분석 결과")
    
    # 기본 정보
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("지역", f"{area_info['gu']} {area_info['dong']}")
    with col2:
        st.metric("위도", f"{area_info['lat']:.4f}")
    with col3:
        st.metric("경도", f"{area_info['lon']:.4f}")
    with col4:
        # Create a DataFrame for the map function
        df_area = pd.DataFrame([{
            'commercial_area_code': area_info['commercial_area_code'],
            'lat': area_info['lat'],
            'lon': area_info['lon'],
            'area_name': area_name,
            'gu': area_info['gu'],
            'dong': area_info['dong']
        }])
        
        # Create Kakao map
        map_html = create_kakao_map([area_info['commercial_area_code']], df_area)
        if map_html:
            components.html(map_html, height=300)
        else:
            st.metric("상권코드", area_info['commercial_area_code'])
    
    # 추천 업종
    if not area_analysis.empty:
        st.subheader("🎯 추천 업종")
        
        # 상위 5개 업종 표시
        top_categories = area_analysis.head(5)
        
        for idx, row in top_categories.iterrows():
            # 실제 컬럼명 사용
            category_name = row.get('service_category_name', f'업종 {idx+1}')
            total_sales = row.get('total_sales', 0)
            shop_count = row.get('shop_count', 0)
            avg_sales = row.get('avg_sales', 0)
            
            with st.expander(f"{category_name} (점포당 분기별 평균 매출: {avg_sales:,}원)"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**총 분기별 매출**: {total_sales:,}원")
                    st.write(f"**점포 수**: {int(shop_count)}개")
                with col2:
                    st.write(f"**업종명**: {category_name}")
                    if shop_count > 0:
                        st.write(f"**점포당 분기별 평균 매출**: {avg_sales:,.2f}원")
    
    # 고객 인구통계
    if not demographics.empty:
        st.subheader("👥 고객 인구통계")

        col1, col2 = st.columns(2)
        
        with col1:
            gender_data = demographics.groupby('sex')['sales_by_gender'].sum()
            if not gender_data.empty:
                st.write("**성별 매출 분포**")
                fig_gender = create_gender_sales_chart(gender_data)
                st.plotly_chart(fig_gender, use_container_width=True)
        
        with col2:
            age_data = demographics.groupby('age')['sales_by_age'].sum()
            if not age_data.empty:
                st.write("**연령대 매출 분포**")
                fig_age = create_age_sales_chart(age_data)
                st.plotly_chart(fig_age, use_container_width=True)
    
    # 인구 패턴
    if not population_patterns.empty:
        st.subheader("📈 인구 패턴 분석")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**요일별 유동인구**")
            # 실제 컬럼명 사용: mon, tue, wed, thu, fri, sat, sun
            day_columns = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
            day_data = population_patterns[day_columns].iloc[0]
            fig_day = create_day_pattern_chart(day_data)
            st.plotly_chart(fig_day, use_container_width=True)
        
        with col2:
            st.write("**성별 유동인구**")
            # 실제 컬럼명 사용: male, female
            gender_columns = ['male', 'female']
            gender_data = population_patterns[gender_columns].iloc[0]
            fig_gender = create_gender_population_chart(gender_data)
            st.plotly_chart(fig_gender, use_container_width=True)
    
    # 시간대별 유동인구 패턴
    if not time_patterns.empty:
        st.write("**시간대별 유동인구 패턴**")
        fig_time = create_time_population_chart(time_patterns)
        if fig_time:
            st.plotly_chart(fig_time, use_container_width=True)


def display_category_analysis_results(category_name, category_analysis, category_demographics, category_time_patterns):
    """업종 분석 결과를 표시합니다."""
    
    st.markdown("---")
    st.subheader(f"📊 '{category_name}' 업종 분석 결과")
    
    # 업종별 분석 결과
    if not category_analysis.empty:
        st.subheader("🎯 추천 상권")
        
        # 상위 5개 상권 표시
        top_areas = category_analysis.head(5)
        
        for idx, row in top_areas.iterrows():
            # 실제 컬럼명 사용
            area_name = row.get('commercial_area_name', f'상권 {idx+1}')
            total_sales = row.get('total_sales', 0)
            shop_count = row.get('shop_count', 0)
            gu = row.get('gu', '')
            dong = row.get('dong', '')
            avg_sales = row.get('avg_sales', 0)
            
            with st.expander(f"{area_name} (점포당 분기별 평균 매출: {avg_sales:,}원)"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**지역**: {gu} {dong}")
                    st.write(f"**총 분기별 매출**: {total_sales:,}원")
                with col2:
                    st.write(f"**점포 수**: {int(shop_count)}개")
                    if shop_count > 0:
                        st.write(f"**점포당 분기별 평균 매출**: {avg_sales:,.2f}원")
    
    # 업종별 고객 특성
    if not category_demographics.empty:
        st.subheader("👥 업종별 고객 특성")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 성별 데이터 처리
            gender_data = category_demographics.groupby('sex')['sales_by_gender'].sum()
            if not gender_data.empty:
                st.write("**성별 매출 분포**")
                fig_gender = create_gender_sales_chart(gender_data)
                st.plotly_chart(fig_gender, use_container_width=True)
        
        with col2:
            # 연령대 데이터 처리
            age_data = category_demographics.groupby('age')['sales_by_age'].sum()
            if not age_data.empty:
                st.write("**연령대 매출 분포**")
                fig_age = create_age_sales_chart(age_data)
                st.plotly_chart(fig_age, use_container_width=True)
        
    # 시간대별 유동인구 패턴
    if not category_time_patterns.empty:
        st.subheader("⏰ 시간대별 유동인구 패턴")
        st.write("**상위 상권들의 시간대별 유동인구 분석**")
        fig_time = create_time_population_chart(category_time_patterns)
        if fig_time:
            st.plotly_chart(fig_time, use_container_width=True)


def create_gender_sales_chart(gender_data):
    """성별 매출 분포 파이 차트를 생성합니다."""
    import plotly.express as px
    import pandas as pd
    
    # 데이터를 DataFrame으로 변환하고 한국어 라벨로 변경
    df = pd.DataFrame({
        '성별': gender_data.index,
        '매출': gender_data.values
    })
    
    # 성별 라벨을 한국어로 변환
    df['성별'] = df['성별'].map({'M': '남성', 'F': '여성'}).fillna(df['성별'])
    
    # 파이 차트 생성
    fig = px.pie(
        df, 
        names='성별', 
        values='매출')
    fig.update_layout(height=300)
    fig.update_traces(marker_colors=['#1f77b4', '#ff7f0e'])
    
    return fig


def create_age_sales_chart(age_data):
    """연령대 매출 분포 차트를 생성합니다."""
    import plotly.graph_objects as go
    
    # 연령대 오름차순 정렬 및 한국어 라벨 매핑
    age_mapping = {
        'TEENS': '10대', 'TWENTIES': '20대', 'THIRTIES': '30대', 'FORTIES': '40대', 'FIFTIES': '50대', 'SIXTIES_PLUS': '60대+',
        '10s': '10대', '20s': '20대', '30s': '30대', '40s': '40대', '50s': '50대', '60s': '60대+',
        '10': '10대', '20': '20대', '30': '30대', '40': '40대', '50': '50대', '60': '60대+',
        '10대': '10대', '20대': '20대', '30대': '30대', '40대': '40대', '50대': '50대', '60대': '60대+', '60대+': '60대+'
    }
    
    # 연령대 정렬을 위한 순서 매핑
    age_order = {'10대': 1, '20대': 2, '30대': 3, '40대': 4, '50대': 5, '60대+': 6}
    
    # 데이터 정리 및 정렬
    sorted_data = []
    sorted_labels = []
    
    for age, sales in age_data.items():
        # 한국어 라벨로 변환
        korean_label = age_mapping.get(age, age)
        sorted_data.append((age_order.get(korean_label, 999), korean_label, sales))
    
    # 연령대 순서로 정렬
    sorted_data.sort(key=lambda x: x[0])
    
    # 정렬된 데이터와 라벨 추출
    sorted_sales = [item[2] for item in sorted_data]
    sorted_labels = [item[1] for item in sorted_data]
    
    fig = go.Figure(data=[
        go.Bar(x=sorted_labels, y=sorted_sales, marker_color='lightblue')
    ])
    fig.update_layout(
        yaxis_title="매출(원)", 
        height=300,
        xaxis_title="연령대"
    )
    return fig


def create_gender_population_chart(gender_data):
    """성별 유동인구 파이 차트를 생성합니다."""
    import plotly.express as px
    import pandas as pd
    
    # 데이터를 DataFrame으로 변환
    df = pd.DataFrame({
        '성별': ['남성', '여성'],
        '인구수': [gender_data['male'], gender_data['female']]
    })
    
    # 파이 차트 생성
    fig = px.pie(
        df, 
        names='성별', 
        values='인구수')
    fig.update_layout(height=300)
    fig.update_traces(marker_colors=['#1f77b4', '#ff7f0e'])
    
    return fig


def create_day_pattern_chart(day_data):
    """요일별 패턴 차트를 생성합니다."""
    import plotly.graph_objects as go
    
    fig = go.Figure(data=[
        go.Bar(x=DAY_LABELS, y=day_data.values, marker_color='lightgreen')
    ])
    fig.update_layout(yaxis_title="인구수", height=300)
    return fig


def create_time_population_chart(time_data):
    """시간대별 유동인구 차트를 생성합니다."""
    import plotly.graph_objects as go
    from config import TIME_X_VALS, TIME_LABELS
    
    time_columns = ['t00_06', 't06_11', 't11_14', 't14_17', 't17_21', 't21_24']
    available_times = [col for col in time_columns if col in time_data.columns]
    
    if not available_times:
        return None
    
    # 시간대별 평균 유동인구 계산
    avg_population = time_data[available_times].mean()
    
    fig = go.Figure()
    fig.add_scatter(
        x=TIME_X_VALS[:len(available_times)], 
        y=avg_population.values, 
        mode="lines+markers",
        name="유동인구", 
        line=dict(color="#636EFA", width=3),
        hovertemplate="%{text}: %{y:,.0f}명<extra></extra>", 
        text=TIME_LABELS[:len(available_times)]
    )
    fig.update_layout(
        template="plotly_white",
        height=350,
        xaxis=dict(
            title="시간대",
            type="linear",
            tickmode="array", 
            tickvals=TIME_X_VALS[:len(available_times)], 
            ticktext=TIME_LABELS[:len(available_times)],
            range=[0, 24]  # 0~24시 고정
        ),
        yaxis=dict(title="유동인구 수"),
        showlegend=False
    )
    return fig
