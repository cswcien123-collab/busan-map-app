import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import math

# 웹 페이지 제목
st.set_page_config(page_title="부산 지하철 지도 분석", layout="wide")
st.title("🚇 부산 지하철 역별 이용객 수 분석 앱")

# 1. CSV 파일 업로드 기능
uploaded_file = st.file_uploader("busan_subway.csv 파일을 업로드하세요", type=["csv"])

if uploaded_file is not None:
    # 데이터 불러오기
    df = pd.read_csv(uploaded_file)

    st.subheader("📋 지하철 데이터 미리보기")
    st.dataframe(df.head())

    # 2. 호선별 색상 정의 (1호선 주황, 2호선 초록, 3호선 갈색, 4호선 파랑)
    line_colors = {
        "1호선": "#FF7F00",  # 주황
        "2호선": "#2CA02C",  # 초록
        "3호선": "#8C564B",  # 갈색
        "4호선": "#1F77B4"  # 파랑
    }

    # 3. multiselect로 호선 필터링
    all_lines = list(df["호선"].unique())
    selected_lines = st.multiselect("확인할 호선을 선택하세요 (여러 개 선택 가능)", options=all_lines, default=all_lines)

    # 선택된 호선만 필터링
    filtered_df = df[df["호선"].isin(selected_lines)]

    # 4. Folium 지도 생성
    st.subheader("🗺️ 호선별 이용객 수 지도")
    if not filtered_df.empty:
        # 부산 중심 위치 설정 (평균 좌표)
        center = [filtered_df["위도"].mean(), filtered_df["경도"].mean()]
        m = folium.Map(location=center, zoom_start=11)

        # 전체 이용객수 최대값 (원의 상대적 크기 계산용)
        max_val = df["이용객수"].max()

        # 역마다 CircleMarker 찍기
        for _, row in filtered_df.iterrows():
            # 면적이 값에 비례하도록 반지름은 제곱근(sqrt) 사용
            radius = 25 * math.sqrt(row["이용객수"] / max_val)
            marker_color = line_colors.get(row["호선"], "#000000")

            folium.CircleMarker(
                location=[row["위도"], row["경도"]],
                radius=max(radius, 3),  # 최소 크기 3 보장
                color=marker_color,
                fill=True,
                fill_color=marker_color,
                fill_opacity=0.6,
                tooltip=row["역명"],  # 마우스 올리면 역명
                popup=f"<b>{row['역명']}</b> ({row['호선']})<br>하루 평균 이용객: {row['이용객수']:,}명"  # 클릭 시 정보
            ).add_to(m)

        # 지도 표시
        st_folium(m, width=900, height=550)
    else:
        st.warning("선택된 호선 데이터가 없습니다.")

    # 5. 이용객 상위 5개 역 표 표시
    st.subheader("🏆 이용객 수 상위 5개 역")
    top5_df = filtered_df.sort_values(by="이용객수", ascending=False).head(5)
    st.table(top5_df[["호선", "역명", "이용객수"]])

else:
    st.info("왼쪽 상단의 파일 업로더에 busan_subway.csv 파일을 올려주세요.")
