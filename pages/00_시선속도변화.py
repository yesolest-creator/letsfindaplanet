import streamlit as st
import numpy as np
import plotly.graph_objects as go
import math

st.set_page_config(page_title="시선속도 변화", page_icon="🌍", layout="wide")
st.title("🌠 시선 속도 변화 시뮬레이터")

# ========= 기본 설정 =========
M_star = 1.0
M_planet = 0.1
a_total = 1.0

# 궤도 반지름 (질량중심 기준)
r_star = (M_planet / (M_star + M_planet)) * a_total
r_planet = (M_star / (M_star + M_planet)) * a_total

# 지구 / 질량중심 위치
earth_pos = np.array([-2.0, 0.0])
com_pos = np.array([0.0, 0.0])

# 기준 시선 방향: 관측자 → 질량중심 (지구에서 멀어지는 방향이 +)
los_dir = com_pos - earth_pos
n_hat = los_dir / np.linalg.norm(los_dir)

# ========= 각도 슬라이더 (관측자-질량중심-별 사이 각도 θ) =========
theta_deg = st.slider("각도 θ (관측자-질량중심-별, 도 단위)", 0, 180, 30, 1)
theta = math.radians(theta_deg)

# ========= 위치 (질량중심 기준) =========
# COM → 관측자 방향은 (-1, 0)
# COM → 별 방향은 이 벡터를 θ만큼 반시계 회전한 방향: (-cosθ, -sinθ)
R_hat = np.array([-math.cos(theta), -math.sin(theta)])

star_pos = com_pos + r_star * R_hat
planet_pos = com_pos - r_planet * R_hat  # 별과 반대편에 위치

# ========= 공전 속도 벡터 =========
# R_hat = (Rx, Ry) 일 때, 접선 방향(반시계) t_hat = (-Ry, Rx)
t_hat = np.array([-R_hat[1], R_hat[0]])

# 별과 행성의 실제 공전 속도 크기 (학생에게는 V, v로 설명)
V_mag = 1.0   # 별 속도 크기 = V
v_mag = 1.5   # 행성 속도 크기 = v (별보다 조금 빠르게)

V_vec = V_mag * t_hat         # 별 실제 속도 벡터
v_vec = -v_mag * t_hat        # 행성은 반대 방향으로 공전

# ========= 시선속도 계산 (공전속도 벡터를 LOS 방향에 정사영) =========
def line_of_sight_component(vel_vec):
    """지구에서 멀어지는 방향(관측자→질량중심)을 +로 한 시선속도 성분"""
    return float(np.dot(vel_vec, n_hat))

V_los = line_of_sight_component(V_vec)   # 별 시선속도
v_los = line_of_sight_component(v_vec)   # 행성 시선속도

# ========= 그래프 =========
fig = go.Figure()

# 궤도 (점선 원)
t_arr = np.linspace(0, 2 * math.pi, 200)
fig.add_trace(
    go.Scatter(
        x=com_pos[0] + r_star * (-np.cos(t_arr)),
        y=com_pos[1] + r_star * (-np.sin(t_arr)),
        mode="lines",
        line=dict(dash="dot", width=1),
        showlegend=False,
    )
)
fig.add_trace(
    go.Scatter(
        x=com_pos[0] + r_planet * (np.cos(t_arr)),
        y=com_pos[1] + r_planet * (np.sin(t_arr)),
        mode="lines",
        line=dict(dash="dot", width=1),
        showlegend=False,
    )
)

# 지구, 질량중심, 별, 행성 점 (텍스트 없이)
fig.add_trace(
    go.Scatter(
        x=[earth_pos[0]],
        y=[earth_pos[1]],
        mode="markers",
        marker=dict(size=10, color="green"),
        showlegend=False,
    )
)
fig.add_trace(
    go.Scatter(
        x=[com_pos[0]],
        y=[com_pos[1]],
        mode="markers",
        marker=dict(size=8, color="black"),
        showlegend=False,
    )
)
fig.add_trace(
    go.Scatter(
        x=[star_pos[0]],
        y=[star_pos[1]],
        mode="markers",
        marker=dict(size=12, color="orange"),
        showlegend=False,
    )
)
fig.add_trace(
    go.Scatter(
        x=[planet_pos[0]],
        y=[planet_pos[1]],
        mode="markers",
        marker=dict(size=9, color="blue"),
        showlegend=False,
    )
)

# 관측자-질량중심 선 (회색 점선)
fig.add_trace(
    go.Scatter(
        x=[earth_pos[0], com_pos[0]],
        y=[earth_pos[1], com_pos[1]],
        mode="lines",
        line=dict(color="gray", width=1, dash="dot"),
        showlegend=False,
    )
)

# 화살표 함수
def add_arrow(start, vec, color):
    end = start + vec
    fig.add_annotation(
        x=float(end[0]),
        y=float(end[1]),
        ax=float(start[0]),
        ay=float(start[1]),
        xref="x",
        yref="y",
        axref="x",
        ayref="y",
        showarrow=True,
        arrowhead=3,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor=color,
        text="",
    )
    return end

# ========= 길이 스케일 설정 =========
# 공전 속도 벡터와 시선 속도 벡터가 같은 스케일로 그려지도록
max_speed_mag = max(np.linalg.norm(V_vec), np.linalg.norm(v_vec), 1e-6)
base_len = 0.6  # 화면 안에서 보일 기본 길이

speed_scale = base_len / max_speed_mag  # 실제 속도 → 화면 길이 변환 계수

# 실제 속도 화살표 (둘 다 검은색, 길이 비례: V, v)
star_speed_vec_draw = V_vec * speed_scale
planet_speed_vec_draw = v_vec * speed_scale

star_tip_speed = add_arrow(star_pos, star_speed_vec_draw, "black")
planet_tip_speed = add_arrow(planet_pos, planet_speed_vec_draw, "black")

# 시선 속도 화살표 (LOS 방향에 평행, 길이 비례: V_los, v_los)
star_los_vec_draw = n_hat * (V_los * speed_scale)
planet_los_vec_draw = n_hat * (v_los * speed_scale)

star_tip_los = add_arrow(star_pos, star_los_vec_draw, "red")
planet_tip_los = add_arrow(planet_pos, planet_los_vec_draw, "blue")

# 공전속도 끝 ↔ 시선속도 끝 연결 (직각삼각형의 한 변, 회색 점선)
fig.add_trace(
    go.Scatter(
        x=[star_tip_speed[0], star_tip_los[0]],
        y=[star_tip_speed[1], star_tip_los[1]],
        mode="lines",
        line=dict(color="gray", width=1, dash="dot"),
        showlegend=False,
    )
)
fig.add_trace(
    go.Scatter(
        x=[planet_tip_speed[0], planet_tip_los[0]],
        y=[planet_tip_speed[1], planet_tip_los[1]],
        mode="lines",
        line=dict(color="gray", width=1, dash="dot"),
        showlegend=False,
    )
)

fig.update_layout(
    width=650,
    height=650,
    xaxis=dict(scaleanchor="y", scaleratio=1, visible=False),
    yaxis=dict(visible=False),
    margin=dict(l=10, r=10, t=10, b=10),
    showlegend=False,
)

st.plotly_chart(fig, use_container_width=True)

# ========= 그림 아래에 시선속도 값 출력 =========
st.markdown("### 📊 시선속도 값 (지구에서 멀어지는 방향을 +로 한 속도)")

col1, col2 = st.columns(2)
with col1:
    st.markdown(f"**별 V_los ≈ {V_los:.2f}**")
with col2:
    st.markdown(f"**행성 v_los ≈ {v_los:.2f}**")

st.markdown(
    """
- 🟢 초록 점: 관측자(지구)  
- ⚫ 검은 점: 질량중심  
- 🟠 주황 점: 별  
- 🔵 파란 점: 행성  

- **검은 화살표**: 공전 속도 벡터 (별·행성, 크기 V, v)  
- **빨간 화살표**: 별의 시선 속도 벡터 (길이 = V_los)  
- **파란 화살표**: 행성의 시선 속도 벡터 (길이 = v_los)  
- **회색 점선 (지구–질량중심)**: 시선 방향 기준선  
- **회색 점선 (두 화살표 끝 연결)**: 공전속도와 시선속도가 이루는 직각삼각형의 한 변  
"""
)
