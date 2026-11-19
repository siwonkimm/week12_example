"""2025년 대한민국 교통사고 통계 탐색 대시보드 (모던 UI & 모션그래픽판).

GitHub 저장소에 이 파일(app.py), requirements.txt, 그리고 아래 CSV 파일 4개를 같은 폴더에 올립니다.
- 한국도로교통공단_시군구별 월별 교통사고 통계_20251231.csv
- 한국도로교통공단_시도 시군구별 교통사고 통계_20251231.csv
- 한국도로교통공단_요일별 시간대별 교통사고 통계_20251231.csv
- 한국도로교통공단_사상자 연령층별 성별 교통사고 통계_20251231.csv

내 컴퓨터에서 실행: python -m streamlit run app.py
"""
from pathlib import Path
import unicodedata

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import streamlit as st

HERE = Path(__file__).parent

st.set_page_config(
    page_title="2025 교통사고 통계 대시보드",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 디자인 팔레트 (세련된 슬레이트·블루·코랄 계열)
PALETTE = [
    "#2563EB",  # Royal Blue
    "#F97316",  # Coral Orange
    "#0D9488",  # Teal
    "#8B5CF6",  # Violet
    "#E11D48",  # Rose
    "#0284C7",  # Sky
    "#D97706",  # Amber
    "#475569",  # Slate
]

# 전역 CSS: Pretendard 글꼴, 아담한 제목 크기, 깔끔한 카드·탭·모션그래픽
st.markdown(
    """
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

    html, body, [class*="css"], .stApp {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Apple SD Gothic Neo', sans-serif !important;
    }

    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2.5rem;
        max-width: 1320px;
    }

    @keyframes fadeInUp {
        0% { opacity: 0; transform: translateY(14px); }
        100% { opacity: 1; transform: translateY(0); }
    }

    @keyframes pulseDot {
        0%, 100% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.35); opacity: 0.55; }
    }

    /* 상단 헤더 영역 (제목 크기 축소 및 정돈) */
    .hero-box {
        padding: 18px 24px;
        border-radius: 16px;
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.07) 0%, rgba(13, 148, 136, 0.05) 100%);
        border: 1px solid rgba(37, 99, 235, 0.14);
        margin-bottom: 1.2rem;
        animation: fadeInUp 0.45s ease-out both;
    }

    .live-badge {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        padding: 3px 10px;
        border-radius: 999px;
        background: rgba(37, 99, 235, 0.10);
        color: #1D4ED8;
        font-size: 0.76rem;
        font-weight: 600;
        letter-spacing: -0.01em;
        margin-bottom: 8px;
    }

    .live-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #F97316;
        display: inline-block;
        animation: pulseDot 1.8s infinite ease-in-out;
    }

    .hero-title {
        font-size: 1.55rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.025em;
        margin: 0 0 4px 0 !important;
        line-height: 1.3;
    }

    .hero-sub {
        font-size: 0.86rem;
        opacity: 0.72;
        margin: 0;
    }

    /* 섹션 소제목 크기 정돈 */
    .section-label {
        font-size: 1.02rem;
        font-weight: 650;
        letter-spacing: -0.015em;
        margin: 0.2rem 0 0.65rem 0;
        opacity: 0.92;
    }

    /* KPI 카드 스타일 */
    div[data-testid="stMetric"] {
        background: rgba(148, 163, 184, 0.07);
        border: 1px solid rgba(148, 163, 184, 0.22);
        border-left: 4px solid #2563EB;
        border-radius: 12px;
        padding: 14px 18px;
        animation: fadeInUp 0.55s ease-out both;
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
    }

    div[data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.08);
        border-left-color: #F97316;
    }

    div[data-testid="stMetricLabel"] {
        font-size: 0.82rem !important;
        opacity: 0.78;
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.55rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }

    div[data-testid="column"]:nth-of-type(1) div[data-testid="stMetric"] { animation-delay: 0.05s; }
    div[data-testid="column"]:nth-of-type(2) div[data-testid="stMetric"] { animation-delay: 0.14s; }
    div[data-testid="column"]:nth-of-type(3) div[data-testid="stMetric"] { animation-delay: 0.23s; }

    /* 탭 바 디자인 */
    button[data-baseweb="tab"] {
        font-size: 0.92rem !important;
        font-weight: 600 !important;
        padding: 8px 16px !important;
        border-radius: 8px 8px 0 0 !important;
    }

    /* 차트 카드 페이드인 */
    div[data-testid="stPlotlyChart"],
    div[data-testid="stPyplotGlobalUse"] {
        animation: fadeInUp 0.65s ease-out both;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

FILES = {
    "monthly": "한국도로교통공단_시군구별 월별 교통사고 통계_20251231.csv",
    "region": "한국도로교통공단_시도 시군구별 교통사고 통계_20251231.csv",
    "time": "한국도로교통공단_요일별 시간대별 교통사고 통계_20251231.csv",
    "age": "한국도로교통공단_사상자 연령층별 성별 교통사고 통계_20251231.csv",
}

METRIC_OPTIONS = {
    "사고건수": ("사고건수", "건", "Accidents"),
    "사망자수": ("사망자수", "명", "Fatalities"),
    "중상자수": ("중상자수", "명", "Serious Injuries"),
    "경상자수": ("경상자수", "명", "Minor Injuries"),
    "부상신고자수": ("부상신고자수", "명", "Reported Injuries"),
}

DAY_ORDER = ["월", "화", "수", "목", "금", "토", "일"]
TIME_ORDER = [
    "00시-02시", "02시-04시", "04시-06시", "06시-08시", "08시-10시", "10시-12시",
    "12시-14시", "14시-16시", "16시-18시", "18시-20시", "20시-22시", "22시-24시",
]
AGE_ORDER = ["12세이하", "13-20세", "21-30세", "31-40세", "41-50세", "51-60세", "61-64세", "65세이상", "불명"]


def find_csv(filename: str) -> Path:
    """운영체제별 한글 파일명 정규화(NFC/NFD) 차이를 흡수해 CSV 경로를 찾습니다."""
    direct = HERE / filename
    if direct.exists():
        return direct
    target = unicodedata.normalize("NFC", filename)
    for path in HERE.glob("*.csv"):
        if unicodedata.normalize("NFC", path.name) == target:
            return path
    raise FileNotFoundError(filename)


def read_korean_csv(filename: str) -> pd.DataFrame:
    """한국 공공데이터 CSV 인코딩(cp949 / utf-8-sig / euc-kr)을 자동으로 읽어옵니다."""
    path = find_csv(filename)
    for enc in ("cp949", "utf-8-sig", "euc-kr", "utf-8"):
        try:
            return pd.read_csv(path, encoding=enc)
        except UnicodeDecodeError:
            continue
    return pd.read_csv(path)


@st.cache_data
def load_all_data() -> dict[str, pd.DataFrame]:
    return {key: read_korean_csv(name) for key, name in FILES.items()}


def korean_font():
    """Matplotlib가 쓸 수 있는 한글 글꼴 이름. 없으면 None을 반환합니다."""
    names = {f.name for f in fm.fontManager.ttflist}
    return next((f for f in ["Pretendard", "Malgun Gothic", "AppleGothic", "NanumGothic"] if f in names), None)


def style_plotly(fig, height: int | None = None):
    """모든 Plotly 차트에 통일된 모던 스타일을 적용합니다."""
    fig.update_layout(
        template="plotly_white",
        font=dict(family="Pretendard, Apple SD Gothic Neo, sans-serif", size=12),
        title=dict(font=dict(size=14), x=0.01, xanchor="left"),
        margin=dict(l=20, r=20, t=48, b=24),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hoverlabel=dict(font_family="Pretendard, sans-serif", font_size=12),
    )
    if height:
        fig.update_layout(height=height)
    return fig


def apply_smooth_animation(fig, frame_ms: int = 700, transition_ms: int = 450):
    """Plotly 애니메이션 재생 속도와 전환 효과를 부드럽게 맞춥니다."""
    if fig.layout.updatemenus:
        for button in fig.layout.updatemenus[0].buttons:
            if button.args and len(button.args) > 1 and isinstance(button.args[1], dict):
                if "frame" in button.args[1]:
                    button.args[1]["frame"]["duration"] = frame_ms
                if "transition" in button.args[1]:
                    button.args[1]["transition"]["duration"] = transition_ms
    return fig


# 상단 히어로 헤더 (작고 깔끔한 제목)
st.markdown(
    """
    <div class="hero-box">
        <div class="live-badge"><span class="live-dot"></span>2025 한국도로교통공단 공공데이터</div>
        <div class="hero-title">대한민국 교통사고 통계 대시보드</div>
        <p class="hero-sub">언제, 어디서, 누구에게 교통사고가 집중되는지 월별·지역별·시간대별·연령층별로 탐색합니다 (단위: 건 / 명)</p>
    </div>
    """,
    unsafe_allow_html=True,
)

try:
    datasets = load_all_data()
except FileNotFoundError as e:
    st.error(f"app.py와 같은 폴더에 필요한 CSV 파일이 없습니다: {e}")
    st.stop()

df_monthly = datasets["monthly"]
df_region = datasets["region"]
df_time = datasets["time"]
df_age = datasets["age"]

# 사이드바 조회 조건
st.sidebar.header("조회 조건")
all_sido = df_monthly["시도"].unique().tolist()
default_sido = [s for s in ["서울", "경기", "부산", "인천", "대구"] if s in all_sido] or all_sido[:5]
selected_sido = st.sidebar.multiselect("시도 선택", all_sido, default=default_sido)
months = st.sidebar.slider("발생월 범위", 1, 12, (1, 12))
metric_label = st.sidebar.selectbox("표시 지표", list(METRIC_OPTIONS.keys()))
metric_col, unit, metric_en = METRIC_OPTIONS[metric_label]

st.sidebar.divider()
st.sidebar.caption("출처: 한국도로교통공단 (2025.12.31 기준)")

# 선택 조건 필터링
view = df_monthly.loc[
    df_monthly["시도"].isin(selected_sido) & df_monthly["발생월"].between(months[0], months[1])
].copy()

if view.empty:
    st.warning("표시할 데이터가 없습니다. 사이드바에서 시도를 하나 이상 선택하세요.")
    st.stop()

# 상단 KPI 카드
st.markdown(
    f'<div class="section-label">{months[0]}~{months[1]}월 {metric_label} 요약 · {", ".join(selected_sido)}</div>',
    unsafe_allow_html=True,
)
c1, c2, c3 = st.columns(3)
total_accidents = view["사고건수"].sum()
total_deaths = view["사망자수"].sum()
fatality_rate = (total_deaths / total_accidents * 100) if total_accidents > 0 else 0.0

c1.metric(f"기간 {metric_label} 합계", f"{view[metric_col].sum():,.0f} {unit}")
c2.metric("분석 대상 (시군구·월)", f"{len(view):,} 행")
c3.metric("기간 치사율 (사고 100건당 사망자)", f"{fatality_rate:.2f} %")
st.caption("치사율은 선택한 기간·지역의 (사망자수 합계 ÷ 사고건수 합계 × 100)으로 계산합니다.")

# 4개 탭 구성: 원천 데이터는 마지막 탭에 깔끔하게 모아둡니다.
tab1, tab2, tab3, tab4 = st.tabs([
    "📍 지역·월별 분석",
    "⏰ 요일·시간대별 패턴",
    "👥 연령층·성별 사상자",
    "🗂️ 데이터 탐색 · 저장",
])

with tab1:
    monthly_sido = view.groupby(["시도", "발생월"], as_index=False)[metric_col].sum()

    # 모션 차트: 월별 변화 재생(▶)
    anim_df = monthly_sido.sort_values(["발생월", "시도"]).copy()
    anim_df["월표시"] = anim_df["발생월"].astype(str) + "월"
    y_max = max(anim_df[metric_col].max() * 1.18, 1)

    motion_fig = px.bar(
        anim_df,
        x="시도",
        y=metric_col,
        color="시도",
        color_discrete_sequence=PALETTE,
        animation_frame="월표시",
        animation_group="시도",
        range_y=[0, y_max],
        text_auto=",.0f",
        title=f"▶ 월별 시도 {metric_label} 변화 모션 차트",
        labels={"시도": "시도", metric_col: f"{metric_label} ({unit})", "월표시": "월"},
    )
    motion_fig.update_layout(showlegend=False)
    motion_fig.update_traces(textposition="outside", marker_line_width=0)
    style_plotly(motion_fig, height=390)
    apply_smooth_animation(motion_fig, frame_ms=700, transition_ms=450)
    st.plotly_chart(motion_fig, width="stretch")

    # 3열 핵심 차트
    trend_fig = px.line(
        monthly_sido.sort_values(["시도", "발생월"]),
        x="발생월",
        y=metric_col,
        color="시도",
        color_discrete_sequence=PALETTE,
        markers=True,
        title="시도별 월별 추이",
        labels={"발생월": "월", metric_col: f"{metric_label} ({unit})"},
    )
    trend_fig.update_xaxes(dtick=1)
    trend_fig.update_yaxes(rangemode="tozero")
    style_plotly(trend_fig, height=340)

    kfont = korean_font()
    totals = view.groupby("시도", as_index=False)[metric_col].sum().sort_values(metric_col, ascending=False)
    with plt.rc_context({"font.family": kfont or "DejaVu Sans", "axes.unicode_minus": False}):
        static_fig, ax = plt.subplots(figsize=(5.8, 3.6))
        static_fig.patch.set_alpha(0.0)
        ax.set_facecolor("none")
        x_labels = totals["시도"] if kfont else [f"R{i+1}" for i in range(len(totals))]
        bar_colors = [PALETTE[i % len(PALETTE)] for i in range(len(totals))]
        bars = ax.bar(x_labels, totals[metric_col], color=bar_colors, width=0.58)
        ax.bar_label(bars, fmt="%.0f", padding=3, fontsize=8)
        if kfont:
            ax.set_title("시도별 기간 합계", loc="left", fontsize=11, fontweight="bold", pad=10)
            ax.set(xlabel="시도", ylabel=f"{metric_label} ({unit})")
        else:
            ax.set_title("Period Total by Region", loc="left", fontsize=11, fontweight="bold", pad=10)
            ax.set(xlabel="Region (ranked)", ylabel=metric_en)
        ax.set_ylim(0, max(totals[metric_col].max() * 1.22, 1))
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", linestyle="--", alpha=0.25)
        static_fig.tight_layout()

    period = view.groupby("시도", as_index=False)[["사고건수", "사망자수"]].sum()
    period["치사율"] = period["사망자수"] / period["사고건수"] * 100
    period = period.sort_values("치사율", ascending=False)
    rate_fig = px.bar(
        period,
        x="시도",
        y="치사율",
        color="시도",
        color_discrete_sequence=PALETTE,
        title="시도별 치사율 (%)",
        labels={"시도": "시도", "치사율": "치사율 (%)"},
    )
    rate_fig.update_layout(showlegend=False)
    rate_fig.update_yaxes(rangemode="tozero")
    style_plotly(rate_fig, height=340)

    left, middle, right = st.columns(3)
    with left:
        st.plotly_chart(trend_fig, width="stretch")
    with middle:
        st.pyplot(static_fig, width="stretch")
    with right:
        st.plotly_chart(rate_fig, width="stretch")
    plt.close(static_fig)

    if not kfont:
        st.caption("이 서버에는 한글 글꼴이 없어 가운데 그림(Matplotlib)의 글자를 영어로 표시합니다.")

    # 연간 시군구 TOP 10
    region_view = df_region[df_region["시도"].isin(selected_sido)].copy()
    region_view["지역"] = region_view["시도"] + " " + region_view["시군구"]
    top10 = region_view.nlargest(10, metric_col).sort_values(metric_col, ascending=True)
    top10_fig = px.bar(
        top10,
        x=metric_col,
        y="지역",
        orientation="h",
        color=metric_col,
        color_continuous_scale="Blues",
        text_auto=",.0f",
        title=f"선택 시도 내 연간 {metric_label} 상위 10개 시군구",
        labels={metric_col: f"{metric_label} ({unit})", "지역": "시군구"},
    )
    top10_fig.update_layout(coloraxis_showscale=False)
    top10_fig.update_traces(textposition="outside")
    style_plotly(top10_fig, height=380)
    st.plotly_chart(top10_fig, width="stretch")

with tab2:
    st.caption("전국 기준 요일·시간대별 통계입니다 (사이드바의 표시 지표가 반영됩니다).")

    time_anim_df = df_time.copy()
    time_anim_df["요일"] = pd.Categorical(time_anim_df["요일"], categories=DAY_ORDER, ordered=True)
    time_anim_df["시간대"] = pd.Categorical(time_anim_df["시간대"], categories=TIME_ORDER, ordered=True)
    time_anim_df = time_anim_df.sort_values(["시간대", "요일"])
    t_max = max(time_anim_df[metric_col].max() * 1.18, 1)

    time_motion_fig = px.bar(
        time_anim_df,
        x="요일",
        y=metric_col,
        color="요일",
        color_discrete_sequence=PALETTE,
        animation_frame="시간대",
        animation_group="요일",
        category_orders={"요일": DAY_ORDER, "시간대": TIME_ORDER},
        range_y=[0, t_max],
        text_auto=",.0f",
        title=f"▶ 시간대별 요일 {metric_label} 변화 모션 차트 (00시 → 24시)",
        labels={"요일": "요일", metric_col: f"{metric_label} ({unit})", "시간대": "시간대"},
    )
    time_motion_fig.update_layout(showlegend=False)
    time_motion_fig.update_traces(textposition="outside")
    style_plotly(time_motion_fig, height=390)
    apply_smooth_animation(time_motion_fig, frame_ms=650, transition_ms=400)
    st.plotly_chart(time_motion_fig, width="stretch")

    pivot = df_time.pivot_table(index="요일", columns="시간대", values=metric_col, aggfunc="sum")
    pivot = pivot.reindex([d for d in DAY_ORDER if d in pivot.index])
    pivot = pivot[[t for t in TIME_ORDER if t in pivot.columns]]
    heat_fig = px.imshow(
        pivot,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="YlOrRd",
        title=f"요일 × 시간대별 {metric_label} 히트맵",
        labels={"x": "시간대", "y": "요일", "color": f"{metric_label} ({unit})"},
    )
    style_plotly(heat_fig, height=380)
    st.plotly_chart(heat_fig, width="stretch")

with tab3:
    st.caption("전국 기준 사상자 연령층·성별 통계입니다 (사고건수 제외, 사상자 지표 기준).")
    age_metric = metric_col if metric_col != "사고건수" else "중상자수"
    age_unit = "명"
    if metric_col == "사고건수":
        st.info("연령층·성별 통계에는 '사고건수' 열이 없어 '중상자수' 기준으로 표시합니다.")

    age_df = df_age.copy()
    age_df["사상자연령층"] = pd.Categorical(age_df["사상자연령층"], categories=AGE_ORDER, ordered=True)
    age_df = age_df.sort_values("사상자연령층")

    age_fig = px.bar(
        age_df,
        x="사상자연령층",
        y=age_metric,
        color="사상자성별",
        color_discrete_sequence=["#2563EB", "#F97316", "#94A3B8"],
        barmode="group",
        title=f"연령층·성별 {age_metric} 분포",
        labels={"사상자연령층": "연령층", age_metric: f"{age_metric} ({age_unit})", "사상자성별": "성별"},
    )
    style_plotly(age_fig, height=420)
    st.plotly_chart(age_fig, width="stretch")

with tab4:
    st.markdown('<div class="section-label">원천 데이터 통합 조회 및 CSV 저장</div>', unsafe_allow_html=True)
    st.caption("시각화 화면을 깔끔하게 유지하기 위해 4개 데이터셋의 표와 다운로드 기능을 이곳에 모았습니다.")

    dataset_choice = st.radio(
        "조회할 데이터셋 선택",
        [
            "시군구별 월별 통계 (현재 필터 적용)",
            "시도·시군구별 연간 통계 (선택 시도 적용)",
            "요일별·시간대별 통계 (전국)",
            "사상자 연령층별·성별 통계 (전국)",
        ],
        horizontal=True,
    )

    if dataset_choice.startswith("시군구별 월별"):
        export_df = view
        export_name = "filtered_monthly_traffic.csv"
    elif dataset_choice.startswith("시도·시군구별"):
        export_df = df_region[df_region["시도"].isin(selected_sido)].copy()
        export_name = "filtered_region_traffic.csv"
    elif dataset_choice.startswith("요일별"):
        export_df = df_time
        export_name = "time_traffic.csv"
    else:
        export_df = df_age
        export_name = "age_gender_traffic.csv"

    st.dataframe(export_df, hide_index=True, width="stretch", height=420)
    st.download_button(
        "선택한 데이터 CSV 저장",
        data=export_df.to_csv(index=False).encode("utf-8-sig"),
        file_name=export_name,
        mime="text/csv",
    )
    st.caption("이 자료는 집계 통계이며, 지역별 인구·통행량 차이를 고려하지 않으므로 사고 원인을 단정하지 않습니다.")
