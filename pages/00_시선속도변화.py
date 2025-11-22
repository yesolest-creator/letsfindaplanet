import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="시선속도 변화", page_icon="🌍", layout="wide")
st.title("🌠 시선 속도 변화 시뮬레이터")

# ========= 기본 설정 =========
M_star = 1.0
M_planet = 0.1
a_total = 1.0

# 궤도 반지름 (질량중심 기준)
r_star = (M_planet / (M_star + M_planet)) * a_total
r_planet = (M_star / (M_star + M_planet)) * a_total

omega = 1.0

# 지구 / 질량중심 위치
earth_pos = np.array([-2.0, 0.0])
com_pos = np.array([0.0, 0.0])

# 기준 시선 방향: 지구 → 질량중심 (지구에서 멀어지는 방향이 +)
los_base = com_pos - earth_pos
n_hat = los_base / np.linalg.norm(los_base)

# ========= 슬라이더 =========
theta_deg = st.slider("공전각 θ (도)", 0, 360, 45, 1)
theta = np.deg2rad(theta_deg)

# ========= 위치 (질량중심 기준) =========
star_pos = np.array([-r_star * np.cos(theta), -r_star * np.sin(theta)])
planet_pos = np.array([r_planet * np.cos(theta), r_planet * np.sin(theta)])

# ========= 공전 속도 벡터 =========
# 접선 방향 (행성 기준, 반시계 방향)
t_hat = np.array([-np.sin(theta), np.cos(theta)]

# 별 실제 속도 V (행성과 반대 방향, 크기는 비례)
V_vec = -omega * r_star * t_hat
# 행성 실제 속도 v
v_vec =  omega * r_planet * t_hat

# ========= 시선속도 계산 (V·sinθ 방식) =========
def los_speed(pos, vel):
    """
    pos: 질량중심 기준 위치 벡터 (COM -> 물체)
    vel: 속도 벡터
    시선각 θ = (관측자-질량중심 선과, 질량중심-물체 선이 이루는 각도)
    시선속도 크기 = |v| * sin(θ)
    부호는 (지구에서 멀어지는 방향을 +)로 정함
    """
    # 질량중심 → 물체 벡터 (이미 pos가 그 역할)
    R = pos - com_pos

    # θ: LOS(n_hat)와 R 사이 각도
    cos_theta = np.dot(R, n_hat) / (np.linalg.norm(R) * np.linalg.norm(n_hat))
    cos_theta = np.clip(cos_theta, -1.0, 1.0)
    theta_rad = np.arccos(cos_theta)
    theta_deg_local = np.rad2deg(theta_rad)

    # 속도 크기
    v_mag = np.linalg.norm(vel)

    # 부호는 실제 속도의 LOS 방향 성분 부호와 같게
    sign = np.sign(np.dot(vel, n_hat))
    if sign == 0:
        sign = 1.0

    # |v_los| = |v| * sin(θ)
    v_los = sign * v_mag * np.sin(theta_rad)
    return v_los, theta_deg_local

V_los, theta_star_sight = los_speed(star_pos, V_vec)
v_los, theta_planet_sight = los_speed(planet_pos, v_vec)

# ========= 수치 출력 (시선속도만) =========
col1, col2 = st.columns(2)

with col1:
    st.subheader("🌞 별")
    st.markdown(f"**$V_{{los}}$ = {V_los:.1f}**")

with col2:
    st.subheader("🪐 행성")
    st.markdown(f"**$v_{{los}}$ = {v_los:.1f}**")

# ========= 30°, 45°, 60°일 때 삼각비 표현 (θ 기준) =========
def special_angle(theta_sight_deg, symbol):
    angles = [30, 45, 60]
    sin_frac = {
        30: r"\frac{1}{2}",
        45: r"\frac{\sqrt{2}}{2}",
        60: r"\frac{\sqrt{3}}{2}",
    }

    nearest = min(angles, key=lambda x: abs(x - theta_sight_deg))
    if abs(nearest - theta_sight_deg) < 2:
        angle_str = str(nearest)
        frac = sin_frac[nearest]

        # θ 와 sinθ
        st.latex(r"\theta \approx " + angle_str + r"^\circ")
        st.latex(r"\sin\theta = \sin " + angle_str + r"^\circ = " + frac)

        # 시선속도 식: v_los = v sinθ / V_los = V sinθ
        if symbol == "V":
            st.latex(r"V_{\text{los}} = V \sin\theta")
            st.latex(r"V_{\text{los}} = V \sin " + angle_str + r"^\circ = V \cdot " + frac)
        else:
            st.latex(r"v_{\text{los}} = v \sin\theta")
            st.latex(r"v_{\text{los}} = v \sin " + angle_str + r"^\circ = v \cdot " + frac)

st.markdown("---")
special_angle(theta_star_sight, "V")
special_angle(theta_planet_sight, "v")

# ========= 그림 =========
fig = go.Figure()

# 궤도
t_arr = np.linspace(0, 2 * np.pi, 200)
fig.add_trace(
    go.Scatter(
        x=-r_star * np.cos(t_arr),
        y=-r_star * np.sin(t_arr),
        mode="lines",
        line=dict(dash="dot"),
        showlegend=False,
    )
)
fig.add_trace(
    go.Scatter(
        x=r_planet * np.cos(t_arr),
        y=r_planet * np.sin(t_arr),
        mode="lines",
        line=dict(dash="dot"),
        showlegend=False,
    )
)

# 점들 (텍스트 없이)
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

# 지구–질량중심 직선 (시선 기준)
fig.add_trace(
    go.Scatter(
        x=[earth_pos[0], com_pos[0]],
        y=[earth_pos[1], com_pos[1]],
        mode="lines",
        line=dict(color="gray", width=1),
        showlegend=False,
    )
)

# 화살표 함수
def arrow(start, vec, color):
    end = start + vec
    fig.add_annotation(
        x=end[0],
        y=end[1],
        ax=start[0],
        ay=start[1],
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

# 실제 속도 화살표 (방향만, 행성이 조금 더 길게)
V_dir = V_vec / (np.linalg.norm(V_vec) + 1e-9)
v_dir = v_vec / (np.linalg.norm(v_vec) + 1e-9)

arrow(star_pos, 0.25 * V_dir, "orange")
arrow(planet_pos, 0.35 * v_dir, "green")

# 시선 속도 화살표 (항상 지구–질량중심 직선과 평행)
max_los = max(abs(V_los), abs(v_los), 0.01)
scale = 0.4 / max_los

arrow(star_pos, V_los * scale * n_hat, "red")
arrow(planet_pos, v_los * scale * n_hat, "blue")

fig.update_layout(
    width=600,
    height=600,
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

- 주황 화살표: 별의 실제 속도 **V**  
- 초록 화살표: 행성의 실제 속도 **v**  
- 빨간 화살표: 별의 시선 속도 **$V_{los}$**  
- 파란 화살표: 행성의 시선 속도 **$v_{los}$**  
"""
)
