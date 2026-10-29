import streamlit as st
import plotly.graph_objects as go
from cinema_cad_engine import generate_cinema_dxf

st.set_page_config(page_title="시네마 CAD 자동 생성기", layout="wide")

st.title("🎬 시네마 규격 & 장비 기반 자동 CAD 도면 생성기")
st.markdown("상영관 크기와 스펙을 입력하면 **기준 청취점(RLP), 스크린, 스피커, 프로젝터**가 자동 배치된 CAD(.DXF)를 생성합니다.")

# 1. 사이드바 입력창
st.sidebar.header("1. 상영관 치수 (Dimensions)")
room_w = st.sidebar.number_input("가로 폭 (Room Width, m)", min_value=6.0, max_value=40.0, value=12.0, step=0.5)
room_l = st.sidebar.number_input("길이 (Room Length, m)", min_value=8.0, max_value=60.0, value=18.0, step=0.5)
room_h = st.sidebar.number_input("천장 높이 (Height, m)", min_value=3.5, max_value=20.0, value=6.0, step=0.5)

st.sidebar.header("2. 스크린 사양")
screen_w = st.sidebar.slider("스크린 가로 폭 (m)", min_value=4.0, max_value=float(room_w - 1.0), value=min(10.0, room_w - 2.0))

st.sidebar.header("3. 음향 & 영사 장비 선택")
spk_main = st.sidebar.selectbox("메인 스피커 (L/C/R)", ["QSC SC-423C", "QSC SC-2150", "JBL 4722N", "JBL 3732"])
spk_sub = st.sidebar.selectbox("서브우퍼 (LFE)", ["QSC SB-7218", "QSC SB-5218", "JBL 4645C", "JBL 4281F"])
spk_surr = st.sidebar.selectbox("서라운드 스피커", ["QSC SR-1030", "QSC SR-8200", "JBL 9300", "JBL 9310"])
amp_model = st.sidebar.selectbox("앰프 시리즈", ["QSC DCA Series", "QSC DPA-Q Series", "Crown DSi Series"])
proj_model = st.sidebar.selectbox("프로젝터 모델", ["Barco SP2K-7S", "Barco DP2K-10S", "Barco DP2K-20CLP", "Barco SP4K-13HC"])

# 2. 메인 대시보드 - 실시간 2D 평면도 미리보기 (Plotly)
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📐 평면 레이아웃 미리보기")
    
    half_w = room_w / 2.0
    rlp_y = room_l * (2.0 / 3.0)

    fig = go.Figure()

    # 상영관 외벽
    fig.add_shape(type="rect", x0=-half_w, y0=0, x1=half_w, y1=room_l,
                  line=dict(color="white", width=3), fillcolor="rgba(30,30,40,0.8)")

    # 스크린
    fig.add_shape(type="line", x0=-screen_w/2, y0=1.2, x1=screen_w/2, y1=1.2,
                  line=dict(color="cyan", width=5))
    fig.add_annotation(x=0, y=1.5, text="SCREEN", showarrow=False, font=dict(color="cyan"))

    # 메인 스피커 (L, C, R)
    for x, lbl in [(-screen_w*0.45, "L"), (0, "C"), (screen_w*0.45, "R")]:
        fig.add_trace(go.Scatter(x=[x], y=[0.5], mode="markers+text",
                                 marker=dict(symbol="square", size=14, color="red"),
                                 text=[lbl], textposition="bottom center", name="Main LCR"))

    # RLP (Reference Listening Position)
    fig.add_trace(go.Scatter(x=[0], y=[rlp_y], mode="markers+text",
                             marker=dict(symbol="cross", size=14, color="yellow"),
                             text=["RLP (2/3)"], textposition="top center", name="RLP"))

    fig.update_layout(
        xaxis=dict(range=[-half_w - 2, half_w + 2], title="가로 폭 (m)"),
        yaxis=dict(range=[-1, room_l + 2], title="길이 (m)", scaleanchor="x", scaleratio=1),
        showlegend=False,
        plot_bgcolor="#111",
        paper_bgcolor="#111",
        font=dict(color="white"),
        height=650
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📋 설계 요약 & BOM")
    st.write(f"**상영관 체적:** {room_w * room_l * room_h:,.1f} ㎥")
    st.write(f"**기준 청취 거리(RLP):** {rlp_y:.2f} m")
    st.write(f"**영사 거리(Throw):** 약 {room_l - 1.2:.2f} m")
    
    st.markdown("---")
    st.markdown("### 📦 장비 리스트")
    st.write(f"- 메인 채널: **{spk_main}** × 3대")
    st.write(f"- 서브우퍼: **{spk_sub}** × 2대")
    st.write(f"- 서라운드: **{spk_surr}** (자동 수량 산출)")
    st.write(f"- 파워 앰프: **{amp_model}**")
    st.write(f"- 메인 프로젝터: **{proj_model}**")

    st.markdown("---")
    # 3. DXF 파일 생성 및 다운로드 버튼
    dxf_bytes = generate_cinema_dxf(
        room_w, room_l, room_h, screen_w, spk_main, spk_sub, spk_surr, proj_model
    )

    st.download_button(
        label="📥 AutoCAD DXF 파일 다운로드",
        data=dxf_bytes,
        file_name=f"Cinema_{int(room_w)}x{int(room_l)}_{proj_model.replace(' ', '_')}.dxf",
        mime="application/dxf",
        type="primary"
    )
