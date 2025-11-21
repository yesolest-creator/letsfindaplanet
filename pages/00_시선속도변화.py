# app.py
import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="시선 속도 시각화", page_icon="🌟", layout="wide")

st.title("🌟 시선 속도 시각화 앱")
st.caption("슬라이더로 공전 각도 θ를 조절하면서 실제 속도와 시선 속도 변화를 확인해 보세요. (＋는 지구에서 멀어지는 방향)")

# -----------------------------
# 기본 파라미터
# -----------------------------
M_star = 1.0
M_planet = 0.1
a_total = 1.0

r_star = (M_planet / (M_star + M_planet)) * a_total
r_planet = (M_star / (M_star + M_planet)) * a_total

omega = 1.0

# 관측자(지구) 위치
earth_x, earth_y = -2.0, 0.0

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

    # 위치 벡터 (질량중심 기준)
    star_pos = np.array([-r_star * np.cos(theta), -r_star * np.sin(theta)])
    planet_pos = np.array([r_planet * np.cos(theta), r_planet * np.sin(theta)])

    # 접선 방향 단위벡터 (행성 기준)
    t_hat = np.array([-np.sin(theta), np.cos(theta)])  # CCW 접선

    # 실제 속도 (행성 / 별)
    v_planet_mag = omega * r_planet
    v_star_mag = omega * r_star

    # ✅ 행성 접선 방향, 별은 그 반대 방향
    v_planet = v_planet_mag * t_hat
    v_star = -v_star_mag * t_hat

    # -------------------------
    # 시선 방향 & 시선 속도
    #   - 시선벡터: 지구 → 물체
    #   - v_los > 0 : 지구에서 멀어지는 방향 (+)
    # -------------------------
    def los_and_radial(pos, vel):
        earth = np.array([earth_x, earth_y])
        los_vec = pos - earth                  # 지구 → 물체
        los_dist = np.linalg.norm(los_vec)
        los_hat = los_vec / los_dist

        v_mag = np.linalg.norm(vel)
        v_los = float(np.dot(vel, los_hat))    # (+): 멀어짐, (-): 가까워짐

        cos_phi = np.clip(v_los / (v_mag + 1e-9), -1.0, 1.0)
        phi_rad = np.arccos(cos_phi)
        phi_deg = np.rad2deg(phi_rad)

        return los_hat, v_mag, v_los, phi_deg

    los_star, v_star_mag, v_star_los, phi_star_deg = los_and_radial(star_pos, v_star)
    los_planet, v_planet_mag, v_planet_los, phi_planet_deg = los_and_radial(planet_pos, v_planet)

    # -------------------------
    # 30° / 45° / 60° 강조 (삼각비)
    # -------------------------
    special_angles = [30, 45, 60]
    frac_latex = {
        30: r"\\frac{\\sqrt{3}}{2}",
        45: r"\\frac{\\sqrt{2}}{2}",
        60: r"\\frac{1}{2}",
    }
    frac_value = {
        30: 0.866,
        45: 0.707,
        60: 0.5,
    }

    def highlight_angle(phi_deg, v_mag, v_los, label):
        diffs = [abs(phi_deg - a) for a in special_angles]
        nearest = special_angles[int(np.argmin(diffs))]
        diff = min(diffs)

        # 항상 수치는 소수점 1자리까지
        st.markdown(
            f"""
**{label}**  
- 공전 각도 θ = **{theta_deg}°**  
- 시선 각 φ ≈ **{phi_deg:.1f}°**  
- 실제 속도 |v| ≈ **{v_mag:.2f}**  
- 시선 속도 vₗₒₛ ≈ **{v_los:.1f}**  (＋: 지구에서 멀어짐, －: 지구로 접근)
"""
        )

        # φ가 30/45/60° 근처일 때만 분수·루트로 표시
        if diff < 2:
            cos_frac = frac_latex[nearest]
            cos_val = frac_value[nearest]
            st.latex(
                rf"""
\varphi \approx {nearest}^\circ,\quad
\cos\varphi \approx {cos_frac} \approx {cos_val:.2f}
"""
            )
            st.latex(
                rf"""
v_{{\text{{los}}}}
= |v|\cos\varphi
\approx {v_mag:.2f} \times {cos_frac}
\approx {v_los:.1f}
"""
            )

    st.subheader("📊 수치 출력")

    st.markdown("### 🌞 별")
    highlight_angle(phi_star_deg, v_star_mag, v_star_los, "별(Star)")

    st.markdown("### 🪐 행성")
    highlight_angle(phi_planet_deg, v_planet_mag, v_planet_los, "행성(Planet)")

# -----------------------------
# 오른쪽: 그림
# -----------------------------
with right_col:
    st.subheader("🔭 궤도와 속도 화살표")

    fig = go.Figure()

    # 궤도
    t = np.linspace(0, 2 * np.pi, 200)
    orbit_star_x = -r_star * np.cos(t)
    orbit_star_y = -r_star * np.sin(t)
    orbit_planet_x = r_planet * np.cos(t)
    orbit_planet_y = r_planet * np.sin(t)

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

    # 지구(관측자)
    fig.add_trace(
        go.Scatter(
            x=[earth_x],
            y=[earth_y],
            mode="markers+text",
            marker=dict(size=14),
            text=["관측자(지구) 🌍"],
            textposition="bottom center",
            name="지구"
        )
    )

    # 질량중심
    fig.add_trace(
        go.Scatter(
            x=[0],
            y=[0],
            mode="markers+text",
            marker=dict(size=10),
            text=["질량중심 ⚖️"],
            textposition="top center",
            name="질량중심"
        )
    )

    # 별 / 행성 위치
    fig.add_trace(
        go.Scatter(
            x=[star_pos[0]],
            y=[star_pos[1]],
            mode="markers+text",
            marker=dict(size=18),
            text=["별 🌞"],
            textposition="top center",
            name="별"
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[planet_pos[0]],
            y=[planet_pos[1]],
            mode="markers+text",
            marker=dict(size=14),
            text=["행성 🪐"],
            textposition="top center",
            name="행성"
        )
    )

    # 시선(지구 → 물체) 선
    fig.add_trace(
        go.Scatter(
            x=[earth_x, star_pos[0]],
            y=[earth_y, star_pos[1]],
            mode="lines",
            line=dict(width=1),
            showlegend=False
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[earth_x, planet_pos[0]],
            y=[earth_y, planet_pos[1]],
            mode="lines",
            line=dict(width=1),
            showlegend=False
        )
    )

    # -------------------------
    # 화살표(Annotation) : 실제 속도 & 시선 속도
    # -------------------------
    vel_scale = 2.0   # 실제 속도 화살표 스케일
    rad_scale = 2.0   # 시선 속도 화살표 스케일

    def add_arrow(fig, start, vec, scale, text, color):
        end = start + scale * vec
        fig.add_annotation(
            x=end[0], y=end[1],
            ax=start[0], ay=start[1],
            xref="x", yref="y", axref="x", ayref="y",
            showarrow=True,
            arrowhead=3,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor=color,
            text=text,
            bgcolor="rgba(255,255,255,0.7)",
        )

    # 별: 실제 속도(행성과 반대 방향, 짧은 화살표) & 시선 속도 성분
    add_arrow(
        fig,
        star_pos,
        v_star,
        vel_scale,
        "v (별 실제 속도)",
        "orange",
    )
    star_rad_vec = los_star * v_star_los   # 방향: 시선, 크기: v_los
    add_arrow(
        fig,
        star_pos,
        star_rad_vec,
        rad_scale,
        "v_los (별 시선 속도)",
        "red",
    )

    # 행성: 실제 속도 & 시선 속도 성분
    add_arrow(
        fig,
        planet_pos,
        v_planet,
        vel_scale,
        "v (행성 실제 속도)",
        "green",
    )
    planet_rad_vec = los_planet * v_planet_los
    add_arrow(
        fig,
        planet_pos,
        planet_rad_vec,
        rad_scale,
        "v_los (행성 시선 속도)",
        "blue",
    )

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
