# app.py
import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="시선 속도 시각화", page_icon="🌟", layout="wide")

st.title("🌟 시선 속도 시각화 앱")
st.caption("슬라이더로 공전 각도 θ를 조절하면서 별과 행성의 시선 속도 변화를 확인해 보세요. (＋는 지구에서 멀어지는 방향)")

# -----------------------------
# 기본 파라미터
# -----------------------------
M_star = 1.0
M_planet = 0.1
a_total = 1.0

# 궤도 반지름 (질량중심 기준)
r_star = (M_planet / (M_star + M_planet)) * a_total
r_planet = (M_star / (M_star + M_planet)) * a_total

omega = 1.0

# 관측자(지구) 위치 / 질량중심
earth_pos = np.array([-2.0, 0.0])
com_pos = np.array([0.0, 0.0])

# 시선 기준 방향: 지구 → 질량중심 (멀어지는 방향 = +)
global_los_vec = com_pos - earth_pos
n_hat = global_los_vec / np.linalg.norm(global_los_vec)

# -----------------------------
# 레이아웃
# -----------------------------
left_col, right_col = st.columns([1.0, 1.2])

with left_col:
    theta_deg = st.slider(
        "공전 각도 θ (도)",
        min_value=0,
        max_value=360,
        value=45,
        step=1,
    )
    theta = np.deg2rad(theta_deg)

    # 위치 (질량중심 기준)
    star_pos = np.array([-r_star * np.cos(theta), -r_star * np.sin(theta)])
    planet_pos = np.array([r_planet * np.cos(theta), r_planet * np.sin(theta)])

    # 접선 방향 (행성 기준, CCW)
    t_hat = np.array([-np.sin(theta), np.cos(theta)])

    # 실제 속도 (물리적으로는 |V|, |v| 이지만 화면에는 값 안 보여줌)
    V_vec = -omega * r_star * t_hat   # 별 실제 속도 벡터 (V)
    v_vec =  omega * r_planet * t_hat # 행성 실제 속도 벡터 (v)

    # 시선 속도 (지구–질량중심 직선 방향 성분)
    def radial_component(vel_vec):
        # (+): 지구에서 멀어지는 방향 (지구→질량중심 방향)
        v_los = float(np.dot(vel_vec, n_hat))
        v_mag = np.linalg.norm(vel_vec)
        cos_phi = np.clip(v_los / (v_mag + 1e-9), -1.0, 1.0)
        phi_deg = np.rad2deg(np.arccos(cos_phi))
        return v_los, phi_deg

    V_los, phi_star_deg = radial_component(V_vec)
    v_los, phi_planet_deg = radial_component(v_vec)

    # -------------------------
    # 30° / 45° / 60° 강조 (삼각비, V / v 기호 사용)
    # -------------------------
    special_angles = [30, 45, 60]
    cos_frac = {
        30: r"\frac{\sqrt{3}}{2}",
        45: r"\frac{\sqrt{2}}{2}",
        60: r"\frac{1}{2}",
    }

def show_result(label_symbol, v_los_value, phi_deg):
    # 시선 속도 수치 (소수점 첫째 자리)
    if label_symbol == "V":
        st.markdown(f"**별의 시선 속도**  \n$V_{{los}} \\approx {v_los_value:.1f}$")
    else:
        st.markdown(f"**행성의 시선 속도**  \n$v_{{los}} \\approx {v_los_value:.1f}$")

    special_angles = [30, 45, 60]
    cos_frac = {
        30: r"\frac{\sqrt{3}}{2}",
        45: r"\frac{\sqrt{2}}{2}",
        60: r"\frac{1}{2}",
    }

    diffs = [abs(phi_deg - a) for a in special_angles]
    nearest = special_angles[int(np.argmin(diffs))]
    diff = min(diffs)

    if diff < 2:
        frac = cos_frac[nearest]
        angle_str = str(nearest)

        # φ 와 cosφ 표시
        st.latex(
            r"\varphi \approx "
            + angle_str
            + r"^\circ,\quad \cos\varphi = \cos"
            + angle_str
            + r"^\circ = "
            + frac
        )

        # V_los 또는 v_los 식 표시
        if label_symbol == "V":
            st.latex(r"V_{\text{los}} = V \cos\varphi")
            st.latex(
                r"V_{\text{los}} = V \cos"
                + angle_str
                + r"^\circ = V \cdot "
                + frac
            )
        else:
            st.latex(r"v_{\text{los}} = v \cos\varphi")
            st.latex(
                r"v_{\text{los}} = v \cos"
                + angle_str
                + r"^\circ = v \cdot "
                + frac
            )


\varphi \approx {nearest}^\circ,\quad
\cos\varphi = \cos{nearest}^\circ = {frac}
"""
                )
                st.latex(
                    r"""
V_{\text{los}} = V \cos\varphi
"""
                )
                st.latex(
                    rf"""
V_{\text{los}} = V \cos{nearest}^\circ
= V \cdot {frac}
"""
                )
            else:
                st.latex(
                    rf"""
\varphi \approx {nearest}^\circ,\quad
\cos\varphi = \cos{nearest}^\circ = {frac}
"""
                )
                st.latex(
                    r"""
v_{\text{los}} = v \cos\varphi
"""
                )
                st.latex(
                    rf"""
v_{\text{los}} = v \cos{nearest}^\circ
= v \cdot {frac}
"""
                )

    st.subheader("📊 시선 속도")

    st.markdown("### 🌞 별")
    show_result("V", V_los, phi_star_deg)

    st.markdown("### 🪐 행성")
    show_result("v", v_los, phi_planet_deg)

# -----------------------------
# 오른쪽: 그림
# -----------------------------
with right_col:
    st.subheader("🔭 궤도와 속도 화살표")

    fig = go.Figure()

    # 궤도
    t_arr = np.linspace(0, 2 * np.pi, 200)
    orbit_star_x = -r_star * np.cos(t_arr)
    orbit_star_y = -r_star * np.sin(t_arr)
    orbit_planet_x = r_planet * np.cos(t_arr)
    orbit_planet_y = r_planet * np.sin(t_arr)

    fig.add_trace(
        go.Scatter(
            x=orbit_star_x,
            y=orbit_star_y,
            mode="lines",
            line=dict(dash="dot"),
            name="별 궤도"
        )
    )
    fig.add_trace(
        go.Scatter(
            x=orbit_planet_x,
            y=orbit_planet_y,
            mode="lines",
            line=dict(dash="dot"),
            name="행성 궤도"
        )
    )

    # 지구, 질량중심, 별, 행성 (텍스트 없이 점만)
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
            marker=dict(size=12, color="gold"),
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[planet_pos[0]],
            y=[planet_pos[1]],
            mode="markers",
            marker=dict(size=9, color="royalblue"),
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

    # -------------------------
    # 화살표 함수 (텍스트 없는 애너테이션)
    # -------------------------
    def add_arrow(fig, start, vec, color):
        end = start + vec
        fig.add_annotation(
            x=end[0], y=end[1],
            ax=start[0], ay=start[1],
            xref="x", yref="y", axref="x", ayref="y",
            showarrow=True,
            arrowhead=3,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor=color,
            text="",  # 그림 안 텍스트 제거
        )

    # 실제 속도 화살표: 방향만 보여주기 (길이는 임의, 행성이 별보다 약간 길게)
    V_dir = V_vec / (np.linalg.norm(V_vec) + 1e-9)
    v_dir = v_vec / (np.linalg.norm(v_vec) + 1e-9)

    V_len = 0.25
    v_len = 0.35  # 행성이 별보다 조금 더 길게

    add_arrow(fig, star_pos, V_dir * V_len, "orange")   # 별 실제 속도 V
    add_arrow(fig, planet_pos, v_dir * v_len, "green")  # 행성 실제 속도 v

    # 시선 속도 화살표: 항상 지구–질량중심 직선과 평행 (n_hat 방향)
    # 길이는 |v_los|에 비례하도록 스케일
    max_los = max(abs(V_los), abs(v_los), 1e-3)
    los_scale = 0.4 / max_los

    V_los_vec = n_hat * V_los * los_scale
    v_los_vec = n_hat * v_los * los_scale

    add_arrow(fig, star_pos, V_los_vec, "red")     # 별 시선 속도 V_los
    add_arrow(fig, planet_pos, v_los_vec, "blue")  # 행성 시선 속도 v_los

    fig.update_layout(
        width=600,
        height=600,
        xaxis=dict(scaleanchor="y", scaleratio=1, visible=False),
        yaxis=dict(visible=False),
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="rgba(255, 252, 240, 1)",
        showlegend=False,
    )

    st.plotly_chart(fig, use_container_width=True)

    # 그림 아래에 간단 설명만
    st.markdown(
        """
- 🟢 초록 점: 관측자(지구)  
- ⚫ 검은 점: 질량중심  
- 🟡 노란 점: 별  
- 🔵 파란 점: 행성  

- 🟧 주황 화살표: 별의 실제 속도 **V**  
- 🟩 초록 화살표: 행성의 실제 속도 **v**  
- 🟥 빨간 화살표: 별의 시선 속도 **Vₗₒₛ** (지구–질량중심 직선 성분)  
- 🟦 파란 화살표: 행성의 시선 속도 **vₗₒₛ**  
"""
    )
