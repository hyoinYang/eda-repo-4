"""
Utility functions for chart generation
차트 생성 유틸리티 함수들
"""

import pandas as pd
import numpy as np


def format_percent_series(s: pd.Series) -> pd.Series:
    """퍼센트 시리즈 포맷팅"""
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
