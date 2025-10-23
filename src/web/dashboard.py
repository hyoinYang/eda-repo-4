import os
import re
import numpy as np
import pandas as pd
import geopandas as gpd
import streamlit as st
from sqlalchemy import create_engine, text
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from streamlit_folium import st_folium
from dotenv import load_dotenv
import folium
from pathlib import Path
import streamlit.components.v1 as components

load_dotenv()

def get_secret(key, default=None):
    try:
        return st.secrets[key]
    except Exception:
        return os.environ.get(key, default)


# ===============================
# ⚙️ CONFIG
# ===============================
st.set_page_config(page_title="서울시 상권별 외식업 분석 대시보드", layout="wide")

# --- DB 연결 ---
DB_URL = os.getenv("DB_URL")
engine = create_engine(DB_URL, pool_pre_ping=True, future=True)

# --- 외식 10종 목록 ---
FOOD10 = [
    "한식음식점", "중식음식점", "일식음식점", "양식음식점",
    "제과점", "패스트푸드점", "치킨전문점", "분식전문점",
    "호프-간이주점", "커피-음료",
]
ALL_YQ = (20241, 20244)  # 2024 Q1~Q4

# --- GeoJSON 경로 (고정 사용) ---
GEOJSON_PATH = Path(__file__).parent / "../../data/서울_행정동_경계_2017.geojson"

# ===============================
# 🔧 UTILITIES
# ===============================
def norm_txt(x: str) -> str:
    if x is None:
        return ""
    s = str(x)
    s = re.sub(r"\s+", "", s)
    s = re.sub(r"[()\-]", "", s)
    return s

@st.cache_data(show_spinner=False)
def load_geojson(path: str):
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

@st.cache_data(show_spinner=False)
def fetch_areas_and_categories():
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
    # For mapping commercial_area_code → (dong_code, area metadata)
    sql = """
    SELECT ca.code AS commercial_area_code, ca.name AS area_name, ca.gu, ca.dong, ca.lon, ca.lat,
           ca.dong_code, d.name AS dong_name
    FROM Commercial_Area ca
    LEFT JOIN Dong d ON d.code = ca.dong_code
    WHERE ca.lon IS NOT NULL AND ca.lat IS NOT NULL
    """
    return pd.read_sql(text(sql), engine)


def ensure_list(x, fallback_all):
    if not x:
        return list(fallback_all)
    return x


def format_percent_series(s: pd.Series) -> pd.Series:
    return (s * 100).round(1)

def make_safe_bins(series, target_bins=7):
    """ColorBrewer 제약(최소 3색=최소 4경계) 만족하도록 안전한 bins 생성"""
    vals = pd.to_numeric(series, errors="coerce").dropna()
    if vals.empty:
        return [0, 1, 2, 3]  # 길이=4 → nb_colors=3

    vmin, vmax = float(vals.min()), float(vals.max())
    if vmin == vmax:
        # 모든 값이 동일 → 살짝만 폭을 줘서 4경계 보장
        eps = max(1.0, abs(vmin) * 1e-9)
        return [vmin, vmin + eps, vmin + 2*eps, vmin + 3*eps]

    # 분위수 기반 초안
    q = np.linspace(0, 1, target_bins + 1)  # target_bins=7 → 8개의 경계
    bins = np.quantile(vals, q).tolist()
    bins = sorted(set(bins))  # 중복 제거

    # 경계 수가 4 미만이면 선형으로 강제 생성
    if len(bins) < 4:
        bins = np.linspace(vmin, vmax, 4).tolist()

    # Folium이 bins의 양끝 밖 값을 만나면 색 계산이 어색해질 수 있어 약간 완화
    bins[0] = min(bins[0], vmin)
    bins[-1] = max(bins[-1], vmax)
    return bins


# ===============================
# LOAD BASE DATA
# ===============================
df_areas, all_categories = fetch_areas_and_categories()
df_dongmap = fetch_dong_map_for_areas()

# Sidebar Controls

st.sidebar.header("🔎 필터")

# Area select (single) — "상권이름 (구 동)" 형식
df_areas = df_areas.copy()
df_areas["gu"] = df_areas["gu"].fillna("")
df_areas["dong"] = df_areas["dong"].fillna("")
df_areas["area_label"] = df_areas["area_name"] + " (" + df_areas["gu"] + " " + df_areas["dong"] + ")"

sel_area_label = st.sidebar.selectbox(
    "상권 선택 (1개만 선택 가능)",
    options=["(선택 안 함)"] + sorted(df_areas["area_label"].unique().tolist())
)

if sel_area_label == "(선택 안 함)":
    selected_area_codes = []
else:
    selected_area_codes = df_areas.loc[
        df_areas["area_label"] == sel_area_label, "commercial_area_code"
    ].astype(int).head(1).tolist()

# Category multiselect (subset of FOOD10)
# sel_cats = st.sidebar.multiselect(
#     "업종 선택 (복수 선택 가능, 비우면 전체 10종)",
#     options=all_categories,
# )
# sel_cats = ensure_list(sel_cats, all_categories)

# areas_key = tuple(sorted(int(x) for x in (selected_area_codes or [])))
# cats_key  = tuple(sorted(sel_cats))
cat_options = ["(전체 10종)"] + list(all_categories)

selected_cat = st.sidebar.selectbox(
    "업종 선택 (단일 선택)",
    options=cat_options,
)

if selected_cat == "(전체 10종)":
    sel_cats = list(all_categories)   # 전체 선택
else:
    sel_cats = [selected_cat]         # 단일 업종만

# 기존 키 계산 유지
areas_key = tuple(sorted(int(x) for x in (selected_area_codes or [])))
cats_key  = tuple(sorted(sel_cats))

st.sidebar.info(
    "상권 필수 선택. 업종 선택 조회. 둘 다 선택 시 교차 조회합니다.\n\n"
    "- 상권만 선택 → 해당 상권의 전체 외식업 기준\n"
)

with st.sidebar.expander("⚙️ 캐시 / 디버그"):
    if st.button("캐시 비우기 & 새로고침", use_container_width=True):
        st.cache_data.clear()
        if hasattr(st, "rerun"):
            st.rerun()
        else:
            st.experimental_rerun()

# ===============================
# 📊 FETCH FILTERED DATA FOR 2024
# ===============================
with st.spinner("데이터 로딩 중…"):
    df_sales = fetch_sales_2024(selected_area_codes, sel_cats, cache_key=("sales", areas_key, cats_key))
    df_fpop  = fetch_floating_by_area_2024(selected_area_codes, cache_key=("fpop", areas_key))
    df_pga   = fetch_population_ga_2024(selected_area_codes, cache_key=("pga", areas_key))
    df_income= fetch_income_2024(cache_key=("income", ALL_YQ))

# Join area metadata
df_sales = df_sales.merge(df_areas, on="commercial_area_code", how="left")

# If area not selected (aggregate view), we still want area-level rows for mapping/averages by cat
if not selected_area_codes:
    # Join with df_areas to keep all areas; fill NaN sales as 0
    df_sales = df_areas[["commercial_area_code","area_name","gu","dong","lon","lat","dong_code"]] \
        .merge(df_sales, on=["commercial_area_code","area_name","gu","dong","lon","lat","dong_code"], how="left")
    df_sales["sales_sum_2024"] = df_sales["sales_sum_2024"].fillna(0)

# ===============================
# 📈 LAYOUT 2×3
# ===============================
st.title("📊 서울시 상권별 외식업 분석 - 대시보드")
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)
col5, col6 = st.columns(2)

# ========== 1) CHOROPLETH + PINS ===========
with col1:
    st.subheader("1. 상권별/업종별 연간 매출액")

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
        st.info("상단에서 상권 또는 업종을 선택해 주세요.")
        bars = []
        labels = []

    if bars:
        fig = go.Figure()
        # 두 번째만 빨간색(#EF553B)
        base_colors = ["#636EFA", "#EF553B"]  # 1st: 파랑, 2nd: 빨강
        fig.add_bar(
            x=labels,
            y=bars,
            marker_color=base_colors[:len(bars)],
            hovertemplate="%{x}: %{y:,.0f}원<extra></extra>"
        )
        fig.update_layout(
            template="plotly_white",
            height=350,
            yaxis=dict(title="매출(원)"),
            xaxis=dict(title=None)
        )
        st.plotly_chart(fig, use_container_width=True)
    

# ========== 2) GENDER × DAY (or avg by category) ==========
with col2:
    st.subheader("2. 성별 · 요일별 유동인구 구성비")
    # Build per-area or average across areas that match selected filters
    if selected_area_codes:
        # Single or multiple: show average across selected areas
        f = df_fpop[df_fpop["commercial_area_code"].isin(selected_area_codes)]
    else:
        # No area selected → average across all areas that have the selected categories
        # Find areas that have sales for selected cats (already in df_sales)
        area_pool = df_sales["commercial_area_code"].unique().tolist()
        f = df_fpop[df_fpop["commercial_area_code"].isin(area_pool)]

    if not f.empty:
        # Average across selected areas
        days = ["mon","tue","wed","thu","fri","sat","sun"]
        times = ["t00_06","t06_11","t11_14","t14_17","t17_21","t21_24"]
        f_days = f[days].mean()
        f_gender = f[["male","female"]].mean()
        # 100% 비중 계산
        day_pct = (f_days / f_days.sum() * 100).round(1)
        gender_pct = (f_gender / f_gender.sum() * 100).round(1)

        fig2 = go.Figure()
        # 요일별 막대
        fig2.add_bar(
            x=["월","화","수","목","금","토","일"],
            y=day_pct,
            name="요일별 구성비(%)",
            hovertemplate="%{x}: %{y:.1f}%<extra></extra>"
        )
        # 성별 막대(꺾은선 대신 막대)
        fig2.add_bar(
            x=["남성","여성"],
            y=gender_pct,
            name="성별 비중(%)",
            hovertemplate="%{x}: %{y:.1f}%<extra></extra>"
        )

        fig2.update_layout(
            template="plotly_white",
            height=350,
            showlegend=True,
            yaxis=dict(title="비중(%)", range=[0,100]),
            xaxis=dict(title=None)
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("선택 조건에 해당하는 유동인구 데이터가 없습니다.")

# ========== 3) 시간대별 유동인구 ==========
with col3:
    st.subheader("3. 시간대별 유동인구 (분기별 평균)")

    # 기준 데이터 선택
    # - 지역만 선택 시: 해당 상권
    # - 업종만/미선택 시: 서울시 전체
    if selected_area_codes:
        f = df_fpop[df_fpop["commercial_area_code"].isin(selected_area_codes)].copy()
    else:
        f = df_fpop.copy()

    if not f.empty:
        # 시간대 컬럼 및 라벨
        times   = ["t00_06","t06_11","t11_14","t14_17","t17_21","t21_24"]
        labels  = ["00-06","06-11","11-14","14-17","17-21","21-24"]
        # 숫자축(중심 시각)으로 고정: 00-06→3, 06-11→8.5, ...
        x_vals  = [3, 8.5, 12.5, 15.5, 19, 22.5]

        # 전체 시간대별 평균
        total_by_time = f[times].mean().to_numpy(dtype=float)

        # 꺾은선(검은색)
        fig3 = go.Figure()
        fig3.add_scatter(
            x=x_vals, y=total_by_time, mode="lines+markers",
            name="전체", line=dict(color="#000000", width=3),
            hovertemplate="%{text}: %{y:,}<extra></extra>", text=labels
        )
        fig3.update_layout(
            template="plotly_white", height=350,
            xaxis=dict(
                title=None, type="linear",
                tickmode="array", tickvals=x_vals, ticktext=labels,
                range=[0, 24]  # 0~24시 고정
            ),
            yaxis=dict(title="유동인구"),
            showlegend=False
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("선택 조건에 해당하는 유동인구 데이터가 없습니다.")

# ========== 4) 상주/직장 인구 ==========
with col4:
    st.subheader("4. 상주 · 직장 인구 (분기별 평균)")
    if selected_area_codes:
        p = df_pga[df_pga["commercial_area_code"].isin(selected_area_codes)]
    else:
        area_pool = df_sales["commercial_area_code"].unique().tolist()
        p = df_pga[df_pga["commercial_area_code"].isin(area_pool)]

    if not p.empty:
        vals = p[["resident","worker"]].mean()
        fig4 = go.Figure()
        fig4.add_bar(x=["상주", "직장"], y=vals.values, marker_color=["#1f77b4", "#2ca02c"],
                     hovertemplate="%{x}: %{y:,}<extra></extra>")
        fig4.update_layout(
            template="plotly_white", height=350,
            yaxis=dict(title="상주, 직장인구")
        )
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("선택 조건에 해당하는 상주/직장 인구 데이터가 없습니다.")

# ========== 5) 소속 동의 총지출 · 음식지출 ==========
with col5:
    st.subheader("5. 상권 소속 동의 연간 총지출 · 음식지출")

    if selected_area_codes:
        # Use the first selected area's dong_code (or combine if multiple)
        pick = df_areas[df_areas["commercial_area_code"].isin(selected_area_codes)]
        if pick.empty:
            st.info("선택 상권의 동 정보를 찾을 수 없습니다.")
        else:
            # If multiple areas, show top 1 by sales or list selector
            if len(pick) > 1:
                pick_name = st.selectbox("어느 상권의 소속 동을 보시겠습니까?", options=pick["area_name"].tolist())
                pick = pick[pick["area_name"] == pick_name]
            row = pick.iloc[0]
            dcode, dname = row["dong_code"], row["dong"]
            di = df_income[df_income["dong_code"] == dcode]
            if di.empty:
                st.info("해당 동의 소득·지출 데이터가 없습니다.")
            else:
                total = float(di["total_expenditure"].sum())
                food  = float(di["food_expenditure"].sum())
                fig5 = go.Figure()
                fig5.add_bar(x=["총지출","음식지출"], y=[total, food], marker_color=["#636EFA", "#EF553B"],
                             hovertemplate="%{x}: %{y:,}<extra></extra>")
                fig5.update_layout(title=f"{dname} — 2024 지출", template="plotly_white", height=350,
                                   yaxis=dict(title="금액(원)"))
                st.plotly_chart(fig5, use_container_width=True)
    else:
        # Only category selected → 평균(해당 업종 보유 상권들의 소속 동 기준 평균)
        # 1) 상권 풀
        area_pool = df_sales["commercial_area_code"].unique().tolist()
        dpool = df_areas[df_areas["commercial_area_code"].isin(area_pool)]["dong_code"].unique().tolist()
        di = df_income[df_income["dong_code"].isin(dpool)]
        if di.empty:
            st.info("해당 조건의 동 지출 데이터가 없습니다.")
        else:
            # 평균: 동별 합계 → 평균
            agg = di.groupby("dong_code", as_index=False).agg(
                total=("total_expenditure","sum"),
                food=("food_expenditure","sum")
            )
            total_avg = float(agg["total"].mean())
            food_avg  = float(agg["food"].mean())
            fig5 = go.Figure()
            fig5.add_bar(x=["총지출(평균)","음식지출(평균)"], y=[total_avg, food_avg],
                         marker_color=["#636EFA", "#EF553B"],
                         hovertemplate="%{x}: %{y:,}<extra></extra>")
            fig5.update_layout(title="해당 업종 보유 상권의 소속 동 평균 지출 (2024)",
                               template="plotly_white", height=350,
                               yaxis=dict(title="금액(원)"))
            st.plotly_chart(fig5, use_container_width=True)

# ========== 6) (Placeholder) ==========
with col6:
    st.subheader("6. 상권 위치 (Kakao Map)")

    KAKAO_JS_KEY = get_secret("KAKAO_JAVASCRIPT_KEY")
    if not KAKAO_JS_KEY:
        st.error("카카오 JavaScript 키가 없습니다. .env 또는 secrets.toml에 'KAKAO_JAVASCRIPT_KEY'를 설정하세요.")
        st.stop()

    if not selected_area_codes:
        st.info("사이드바에서 상권을 1개 선택하면 해당 위치로 지도가 표시됩니다.")
    else:
        row = df_areas.loc[df_areas["commercial_area_code"] == selected_area_codes[0]].head(1)
        if row.empty or pd.isna(row.iloc[0]["lat"]) or pd.isna(row.iloc[0]["lon"]):
            st.warning("선택한 상권의 좌표(lat/lon)를 찾을 수 없습니다.")
        else:
            lat = float(row.iloc[0]["lat"])
            lon = float(row.iloc[0]["lon"])
            area_name = str(row.iloc[0]["area_name"])
            gu = str(row.iloc[0]["gu"]) if pd.notna(row.iloc[0]["gu"]) else ""
            dong = str(row.iloc[0]["dong"]) if pd.notna(row.iloc[0]["dong"]) else ""
            label = f"{area_name} ({gu} {dong})".strip()

            # 좌표 유효성(대략 대한민국 범위) 체크
            if not (33 <= lat <= 39 and 124 <= lon <= 132):
                st.warning(f"좌표가 비정상일 수 있습니다. lat={lat}, lon={lon}")
            level = 5  # 확대

            html = f"""
<div id="kmap" style="width: 100%; height: 350px; position: relative;"></div>
<div id="kmsg" style="position:absolute;top:8px;left:8px;background:#fff8;border:1px solid #ddd;padding:4px 8px;border-radius:6px;font-size:12px;display:none;"></div>
<script>
  (function(){{
    var container = document.getElementById('kmap');
    var msg = document.getElementById('kmsg');

    function showMsg(t){{
      msg.innerText = t;
      msg.style.display = 'block';
    }}

    function init(){{
      try {{
        var center = new kakao.maps.LatLng({lat}, {lon});
        var map = new kakao.maps.Map(container, {{ center:center, level:{level} }});

        var pos = new kakao.maps.LatLng({lat}, {lon});
        var marker = new kakao.maps.Marker({{ position: pos }});
        marker.setMap(map);

        var iwContent = '<div style="padding:6px 8px; font-size:12px; white-space:nowrap;">{label}</div>';
        var infowindow = new kakao.maps.InfoWindow({{ position: pos, content: iwContent }});
        infowindow.open(map, marker);

        window.addEventListener('resize', function() {{
          var c = map.getCenter();
          setTimeout(function(){{ map.relayout(); map.setCenter(c); }}, 0);
        }});
      }} catch(e) {{
        showMsg("카카오맵 초기화 오류: " + e);
      }}
    }}

    // SDK가 없으면 로드, 있으면 바로 init
    function loadSdk(){{
      var s = document.createElement('script');
      // 프로토콜 명시 + autoload=false + 안전
      s.src = "https://dapi.kakao.com/v2/maps/sdk.js?appkey={KAKAO_JS_KEY}&autoload=false";
      s.onload = function(){{
        if (window.kakao && kakao.maps && kakao.maps.load) {{
          kakao.maps.load(init);
        }} else {{
          showMsg("SDK가 로드되었지만 kakao.maps 객체가 없습니다. (도메인 미등록 가능성)");
        }}
      }};
      s.onerror = function(){{
        showMsg("SDK 스크립트 로드 실패(네트워크/차단).");
      }};
      document.head.appendChild(s);
    }}

    // 1. 이미 kakao 객체가 있으면 사용
    if (window.kakao && kakao.maps && kakao.maps.load) {{
      kakao.maps.load(init);
    }} else {{
      loadSdk();
      // 1.5초 내 로드 실패시 안내
      setTimeout(function(){{
        if (!(window.kakao && kakao.maps)) {{
          showMsg("지도 SDK 로딩 실패. Kakao Developers에서 도메인을 등록했는지 확인하세요. (예: http://localhost:8501, 배포 도메인)");
        }}
      }}, 1500);
    }}
  }})();
</script>
"""
            components.html(html, height=350)
