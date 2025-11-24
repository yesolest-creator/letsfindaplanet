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

# ========= 상단: 슬라이더 + 시선속도 수식 =========
top_left, top_right = st.columns([1, 1])

with top_left:
    theta_deg = st.slider(
        "각도 θ (관측자-질량중심-별, 도 단위)",
        min_value=0,
        max_value=360,
        value=30,
        step=1,
    )
theta = math.radians(theta_deg)

# ===== 속도 크기와 시선속도 계산 (정의상 V_시선 = V sinθ, v_시선 = v sinθ) =====
V_mag = 1.0   # 별 공전 속도 크기 V
v_mag = 1.5   # 행성 공전 속도 크기 v

sin_theta = math.sin(theta)

V_sight = V_mag * sin_theta   # V_시선
v_sight = v_mag * sin_theta   # v_시선

with top_right:
    st.subheader("📊 시선 속도 (기호와 값)")
    st.latex(
        "V_{\\text{시선}} = V \\sin\\theta \\approx "
        + f"{sin_theta:.2f}"
        + " V"
    )
    st.latex(
        "v_{\\text{시선}} = v \\sin\\theta \\approx "
        + f"{sin_theta:.2f}"
        + " v"
    )

# ========= 위치 (질량중심 기준) =========
# COM → 관측자 방향은 (-1, 0)
# COM → 별 방향은 이 벡터를 θ만큼 반시계 회전한 방향: (-cosθ, -sinθ)
R_hat = np.array([-math.cos(theta), -math.sin(theta)])

star_pos = com_pos + r_star * R_hat
planet_pos = com_pos - r_planet * R_hat  # 별과 반대편에 위치

# ========= 공전 속도 벡터 =========
# R_hat = (Rx, Ry) 일 때, 접선 방향(반시계) t_hat = (-Ry, Rx)
t_hat = np.array([-R_hat[1], R_hat[0]])

V_vec = V_mag * t_hat         # 별 실제 속도 벡터
v_vec = -v_mag * t_hat        # 행성은 반대 방향으로 공전

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

# 1-1. 관측자-질량중심 선 (회색 점선)
fig.add_trace(
    go.Scatter(
        x=[earth_pos[0], com_pos[0]],
        y=[earth_pos[1], com_pos[1]],
        mode="lines",
        line=dict(color="gray", width=1, dash="dot"),
        showlegend=False,
    )
)

# 1-1. 질량중심-별 선 (회색 점선)
fig.add_trace(
    go.Scatter(
        x=[com_pos[0], star_pos[0]],
        y=[com_pos[1], star_pos[1]],
        mode="lines",
        line=dict(color="gray", width=1, dash="dot"),
        showlegend=False,
    )
)

# 1-1. 질량중심 근처에 θ 표시
fig.add_annotation(
    x=com_pos[0] - 0.2,
    y=com_pos[1] + 0.2,
    text="θ",
    showarrow=False,
    font=dict(size=16, color="gray"),
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
# 공전 속도와 시선 속도가 같은 스케일로 그려지도록
max_speed_mag = max(np.linalg.norm(V_vec), np.linalg.norm(v_vec), 1e-6)
base_len = 0.6  # 화면 안에서 보일 기본 길이

speed_scale = base_len / max_speed_mag  # 실제 속도 → 화면 길이 변환 계수

# 실제 속도 화살표 (둘 다 검은색, 길이 비례: V, v)
star_speed_vec_draw = V_vec * speed_scale
planet_speed_vec_draw = v_vec * speed_scale

star_tip_speed = add_arrow(star_pos, star_speed_vec_draw, "black")
planet_tip_speed = add_arrow(planet_pos, planet_speed_vec_draw, "black")

# 시선 속도 화살표 (LOS 방향에 평행, 길이 비례: V_시선, v_시선)
star_los_vec_draw = n_hat * (V_sight * speed_scale)
planet_los_vec_draw = n_hat * (v_sight * speed_scale)

star_tip_los = add_arrow(star_pos, star_los_vec_draw, "red")
planet_tip_los = add_arrow(planet_pos, planet_los_vec_draw, "blue")

# 2. 공전속도 끝 ↔ 시선속도 끝 연결 (직각삼각형의 한 변, 회색 점선)
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

# 1-2. 직각 표시 (별 삼각형)
def add_right_angle_marker(tip_los, tip_speed, color="gray"):
    """
    tip_los: 시선속도 끝점
    tip_speed: 공전속도 끝점
    """
    tri_vec = tip_speed - tip_los
    tri_norm = np.linalg.norm(tri_vec)
    if tri_norm < 1e-6:
        return
    tri_hat = tri_vec / tri_norm
    size = 0.08  # 직각 표시 크기

    # 직각 표시의 꼭짓점을 삼각형 안쪽으로 약간 이동
    corner = tip_los + (-n_hat - tri_hat) * (size * 0.5)

    p2 = corner + n_hat * size
    p3 = corner + tri_hat * size

    fig.add_trace(
        go.Scatter(
            x=[corner[0], p2[0]],
            y=[corner[1], p2[1]],
            mode="lines",
            line=dict(color=color, width=2),
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[corner[0], p3[0]],
            y=[corner[1], p3[1]],
            mode="lines",
            line=dict(color=color, width=2),
            showlegend=False,
        )
    )

# 별 / 행성 삼각형에 직각 표시
add_right_angle_marker(star_tip_los, star_tip_speed)
add_right_angle_marker(planet_tip_los, planet_tip_speed)

fig.update_layout(
    width=650,
    height=650,
    xaxis=dict(scaleanchor="y", scaleratio=1, visible=False),
    yaxis=dict(visible=False),
    margin=dict(l=10, r=10, t=10, b=10),
    showlegend=False,
)

st.plotly_chart(fig, use_container_width=True)

st.markdown(
    """
- 🟢 초록 점: 관측자(지구)  
- ⚫ 검은 점: 질량중심  
- 🟠 주황 점: 별  
- 🔵 파란 점: 행성  

- **검은 화살표**: 공전 속도 벡터 (별·행성, 크기 V, v) → 삼각형의 빗변  
- **빨간 화살표**: 별의 시선 속도 벡터 $V_{\\text{시선}}$  
- **파란 화살표**: 행성의 시선 속도 벡터 $v_{\\text{시선}}$  
- **회색 점선 (지구–질량중심)**: 시선 방향 기준선  
- **회색 점선 (질량중심–별)**: θ가 정의되는 선  
- **회색 점선 (두 화살표 끝 연결)**: 공전속도와 시선속도가 이루는 직각삼각형의 나머지 한 변  
- 직각 표시: 공전속도 벡터가 빗변, 시선속도와 나머지 한 변이 직각을 이루는 삼각형의 직각 부분  
"""
)
