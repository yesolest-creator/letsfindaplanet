import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="시선속도 변화", page_icon="🌍", layout="wide")
st.title("🌠 시선 속도 변화 시뮬레이터")

# ========= 기본 설정 =========
M_star = 1.0
M_planet = 0.1
a_total = 1.0

# 궤도 반지름
r_star = (M_planet / (M_star + M_planet)) * a_total
r_planet = (M_star / (M_star + M_planet)) * a_total

omega = 1.0

# 지구 / 질량중심
earth_pos = np.array([-2.0, 0.0])
com_pos = np.array([0.0, 0.0])

# 기준 시선방향 (지구 → 질량중심)
los_base = com_pos - earth_pos
n_hat = los_base / np.linalg.norm(los_base)

# ========= 슬라이더 =========
theta_deg = st.slider("공전각 θ (도)", 0, 360, 45, 1)
theta = np.deg2rad(theta_deg)

# ========= 위치 =========
star_pos = np.array([-r_star * np.cos(theta), -r_star * np.sin(theta)])
planet_pos = np.array([r_planet * np.cos(theta), r_planet * np.sin(theta)])

# ========= 속도 =========
t_hat = np.array([-np.sin(theta), np.cos(theta)])

V_vec = -omega * r_star * t_hat
v_vec =  omega * r_planet * t_hat

# ========= 시선속도 =========
def calc_los(v):
    v_los = np.dot(v, n_hat)
    angle = np.degrees(np.arccos(np.clip(v_los / (np.linalg.norm(v) + 1e-9), -1, 1)))
    return v_los, angle

V_los, phi_star = calc_los(V_vec)
v_los, phi_planet = calc_los(v_vec)

# ========= 수치 출력 =========
col1, col2 = st.columns(2)

with col1:
    st.subheader("🌞 별")
    st.markdown(f"**$V_{{los}}$ = {V_los:.1f}**")

with col2:
    st.subheader("🪐 행성")
    st.markdown(f"**$v_{{los}}$ = {v_los:.1f}**")

# ========= 30,45,60도 강조 =========
def special_angle(phi, symbol):
    angles = [30, 45, 60]
    cos_frac = {
        30: r"\frac{\sqrt{3}}{2}",
        45: r"\frac{\sqrt{2}}{2}",
        60: r"\frac{1}{2}"
    }

    nearest = min(angles, key=lambda x: abs(x-phi))

    if abs(nearest - phi) < 2:
        st.latex(r"\varphi \approx " + str(nearest) + r"^\circ")
        st.latex(r"\cos\varphi = \cos " + str(nearest) + r"^\circ = " + cos_frac[nearest])
        st.latex(symbol + r"_{los} = " + symbol + r"\cdot" + cos_frac[nearest])

st.markdown("---")
special_angle(phi_star, "V")
special_angle(phi_planet, "v")

# ========= 그래프 =========
fig = go.Figure()

# 궤도
t = np.linspace(0, 2*np.pi, 200)

fig.add_trace(go.Scatter(x=-r_star*np.cos(t), y=-r_star*np.sin(t),
                         mode="lines", line=dict(dash="dot"), showlegend=False))
fig.add_trace(go.Scatter(x= r_planet*np.cos(t), y= r_planet*np.sin(t),
                         mode="lines", line=dict(dash="dot"), showlegend=False))

# 점
fig.add_trace(go.Scatter(x=[earth_pos[0]], y=[earth_pos[1]], mode="markers",
                         marker=dict(size=10, color="green"), showlegend=False))
fig.add_trace(go.Scatter(x=[0], y=[0], mode="markers",
                         marker=dict(size=8, color="black"), showlegend=False))
fig.add_trace(go.Scatter(x=[star_pos[0]], y=[star_pos[1]], mode="markers",
                         marker=dict(size=14, color="orange"), showlegend=False))
fig.add_trace(go.Scatter(x=[planet_pos[0]], y=[planet_pos[1]], mode="markers",
                         marker=dict(size=10, color="blue"), showlegend=False))

# ✅ 화살표 함수
def arrow(start, vec, color):
    end = start + vec
    fig.add_annotation(
        x=end[0], y=end[1],
        ax=start[0], ay=start[1],
        xref="x", yref="y", axref="x", ayref="y",
        showarrow=True, arrowhead=3, arrowwidth=2,
        arrowcolor=color,
        text=""
    )

# 실제 속도 (행성이 더 김)
V_dir = V_vec / (np.linalg.norm(V_vec)+1e-9)
v_dir = v_vec / (np.linalg.norm(v_vec)+1e-9)

arrow(star_pos, 0.25*V_dir, "orange")
arrow(planet_pos, 0.35*v_dir, "green")

# 시선 속도 (지구-질량중심 직선과 평행)
scale = 0.4 / max(abs(V_los), abs(v_los), 0.01)
arrow(star_pos, V_los * scale * n_hat, "red")
arrow(planet_pos, v_los * scale * n_hat, "blue")

fig.update_layout(
    width=600, height=600,
    xaxis=dict(scaleanchor="y", visible=False),
    yaxis=dict(visible=False),
    margin=dict(l=10, r=10, t=10, b=10),
)

st.plotly_chart(fig, use_container_width=True)
