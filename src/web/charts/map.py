"""
Map generation functions
지도 생성 함수들
"""

import pandas as pd
from config import (
    CHART_HEIGHT, KAKAO_JS_KEY, DEFAULT_MAP_LEVEL,
    KOREA_LAT_RANGE, KOREA_LON_RANGE
)


def create_kakao_map(selected_area_codes, df_areas):
    """
    카카오 맵을 생성합니다.
    
    Args:
        selected_area_codes: 선택된 상권 코드 리스트
        df_areas: 상권 데이터
        
    Returns:
        str: HTML 코드 또는 None
    """
    if not KAKAO_JS_KEY:
        return None

    if not selected_area_codes:
        return None

    row = df_areas.loc[df_areas["commercial_area_code"] == selected_area_codes[0]].head(1)
    if row.empty or pd.isna(row.iloc[0]["lat"]) or pd.isna(row.iloc[0]["lon"]):
        return None

    lat = float(row.iloc[0]["lat"])
    lon = float(row.iloc[0]["lon"])
    area_name = str(row.iloc[0]["area_name"])
    gu = str(row.iloc[0]["gu"]) if pd.notna(row.iloc[0]["gu"]) else ""
    dong = str(row.iloc[0]["dong"]) if pd.notna(row.iloc[0]["dong"]) else ""
    label = f"{area_name} ({gu} {dong})".strip()

    # 좌표 유효성(대략 대한민국 범위) 체크
    if not (KOREA_LAT_RANGE[0] <= lat <= KOREA_LAT_RANGE[1] and KOREA_LON_RANGE[0] <= lon <= KOREA_LON_RANGE[1]):
        return None

    level = DEFAULT_MAP_LEVEL  # 확대

    html = f"""
<div id="kmap" style="width:100%; height:{CHART_HEIGHT}px; position:relative;"></div>
<div id="kmsg" style="position:absolute;top:8px;left:8px;background:#fff8;border:1px solid #ddd;padding:4px 8px;border-radius:6px;font-size:12px;display:none;"></div>
<script>
(function(){{
    var container = document.getElementById('kmap');
    var msg = document.getElementById('kmsg');

    function showMsg(t){{
        msg.innerText = t;
        msg.style.display = 'block';
    }}

    function initMap(){{
        try {{
            var center = new kakao.maps.LatLng({lat}, {lon});
            var map = new kakao.maps.Map(container, {{ center:center, level:{DEFAULT_MAP_LEVEL} }});

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

    function loadSdk(){{
        if (window.kakao && kakao.maps) {{
            initMap();
            return;
        }}
        var s = document.createElement('script');
        s.src = "https://dapi.kakao.com/v2/maps/sdk.js?appkey={KAKAO_JS_KEY}&autoload=false";
        s.onload = function(){{
            if (window.kakao && kakao.maps && kakao.maps.load) {{
                kakao.maps.load(initMap);
            }} else {{
                showMsg("SDK가 로드되었지만 kakao.maps 객체가 없습니다. (도메인/키 확인 필요)");
            }}
        }};
        s.onerror = function(){{
            showMsg("SDK 스크립트 로드 실패(네트워크/차단 가능성).");
        }};
        document.head.appendChild(s);

        // 2초 내 SDK가 로드 안되면 안내
        setTimeout(function(){{
            if (!(window.kakao && kakao.maps)) {{
                showMsg("지도 SDK 로딩 실패. Kakao Developers에서 도메인과 JS 키를 확인하세요.");
            }}
        }}, 2000);
    }}

    loadSdk();
}})();
</script>
"""
    return html
