# app.py
import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="시선 속도 학습 앱", page_icon="🌟", layout="wide")

# -----------------------------
# 기본 설명
# -----------------------------
st.title("🌟 따뜻한 시선 속도 교실 🌍")
st.markdown(
    """
    행성과 별이 **질량중심(무게중심)**을 기준으로 서로 궤도를 도는 상황을 보면서,  
    **시선 속도(📏 line-of-sight velocity)**가 어떻게 달라지는지 이해해 보는 앱이에요.  

    아래 슬라이더로 **공전 각도(위치)**를 바꾸면서  
    👉 실제 속도 벡터와  
    👉 그중에서 **지구에서 보이는 시선 방향 성분**이  
    어떻게 변하는지 관찰해 보세요! ✨  
    """
)

# -----------------------------
# 물리 모델 설정 (단위는 모두 임의 단위)
# -----------------------------
# 질량 비 (별 : 행성)
M_star = 1.0
M_planet = 0.1  # 별보다 훨씬 작지만, 시각화를 위해 실제보다 크게 설정

# 두 천체 사이 거리 (임의)
a_total = 1.0

# 질량 중심을 원점(0,0)에 두었을 때의 궤도 반지름
r_star = (M_planet / (M_star + M_planet)) * a_total   # 별의 궤도 반지름
r_planet = (M_star / (M_star + M_planet)) * a_total   # 행성의 궤도 반지름

# 각속도 (단위 시간당 각도) – 크기만 중요
omega = 1.0

# 지구 위치 (궤도 평면 안의 왼쪽에 고정)
earth_x, earth_y = -2.0, 0.0

# -----------------------------
# 레이아웃: 왼쪽(슬라이더 + 수치), 오른쪽(그림)
# -----------------------------
left_col, right_col = st.columns([1.0, 1.3])

with left_col:
    st.subheader("🌀 공전 위치 조절하기")

    theta_deg = st.slider(
        "별과 행성이 질량중심을 기준으로 공전한 각도 θ (도)",
        min_value=0,
        max_value=360,
        value=45,
        step=1,
        help="0°에서 360°까지 공전 각도를 바꿔 보세요. 각도에 따라 속도 방향과 시선 속도가 달라집니다.",
    )
    theta = np.deg2rad(theta_deg)

    st.markdown(
        f"""
        지금은 질량중심을 기준으로  
        **θ = {theta_deg}°** 만큼 회전한 위치예요.  
        (0°에서 시계 반대방향으로 증가한다고 생각하면 됩니다. ⏱️)
        """
    )

    # -------------------------
    # 위치 / 속도 계산
    # -------------------------
    # 위치 벡터 (COM 기준, 반시계 방향)
    star_pos = np.array([-r_star * np.cos(theta), -r_star * np.sin(theta)])
    planet_pos = np.array([r_planet * np.cos(theta), r_planet * np.sin(theta)])

    # 속도 벡터 (원운동: 위치에 수직)
    # v = ω r, 방향은 반시계방향으로 90° 회전
    v_star_mag = omega * r_star
    v_planet_mag = omega * r_planet

    v_star = v_star_mag * np.array([-np.sin(theta), np.cos(theta)])
    v_planet = v_planet_mag * np.array([-np.sin(theta), np.cos(theta)])

    # 시선 방향: 각 천체 → 지구
    def line_of_sight_and_radial(pos, vel):
        los_vec = np.array([earth_x, earth_y]) - pos  # 천체에서 지구로 향하는 벡터
        los_dist = np.linalg.norm(los_vec)
        los_hat = los_vec / los_dist  # 단위벡터

        v_mag = np.linalg.norm(vel)
        v_rad_toward = np.dot(vel, los_hat)  # +면 지구 쪽, -면 지구에서 멀어짐

        # 각도 φ : 속도 벡터와 시선 방향 사이의 각
        # cos φ = (v · n) / (|v||n|) = v_rad_toward / |v|
        cos_phi = np.clip(v_rad_toward / v_mag, -1.0, 1.0)
        phi_rad = np.arccos(cos_phi)
        phi_deg = np.rad2deg(phi_rad)

        return los_hat, v_mag, v_rad_toward, phi_deg

    los_star, v_star_mag, v_star_rad, phi_star_deg = line_of_sight_and_radial(
        star_pos, v_star
    )
    los_planet, v_planet_mag, v_planet_rad, phi_planet_deg = line_of_sight_and_radial(
        planet_pos, v_planet
    )

    # -------------------------
    # 30° / 45° / 60° 강조 함수
    # -------------------------
    special_angles = [30, 45, 60]

    def highlight_special_angle(phi_deg, body_name):
        diff_list = [abs(phi_deg - a) for a in special_angles]
        closest = special_angles[int(np.argmin(diff_list))]
        diff = min(diff_list)
        if diff < 2:
            st.success(
                f"✨ {body_name}의 시선 각 φ ≈ {phi_deg:.1f}° → **{closest}°**와 거의 같아요! "
                f"삼각비 문제로 내기 딱 좋은 각도예요. 🧮",
                icon="🌈",
            )
        else:
            st.info(
                f"{body_name}의 시선 각 φ ≈ {phi_deg:.1f}°. "
                f"**30°, 45°, 60°**와 비교해 보며 cos값을 추측해 보세요! 🌟",
                icon="💡",
            )

    st.subheader("📊 별과 행성의 속도 & 시선 속도")

    st.markdown("**속도 방향과 시선 방향이 이루는 각 φ(파이)**를 함께 확인해 봅시다 😊")

    st.markdown("### 🌞 별 (Star)")
    st.write(
        f"- 실제 속도 크기 |v| ≈ **{v_star_mag:.3f} (임의 단위)**  \n"
        f"- 시선 각 φ ≈ **{phi_star_deg:.1f}°**  \n"
        f"- 시선 속도 vₗₒₛ ≈ **{v_star_rad:.3f}** (＋: 지구 쪽, －: 지구에서 멀어짐)"
    )
    highlight_special_angle(phi_star_deg, "별")

    st.markdown("### 🪐 행성 (Planet)")
    st.write(
        f"- 실제 속도 크기 |v| ≈ **{v_planet_mag:.3f} (임의 단위)**  \n"
        f"- 시선 각 φ ≈ **{phi_planet_deg:.1f}°**  \n"
        f"- 시선 속도 vₗₒₛ ≈ **{v_planet_rad:.3f}** (＋: 지구 쪽, －: 지구에서 멀어짐)"
    )
    highlight_special_angle(phi_planet_deg, "행성")

    st.markdown(
        """
        > 💡 **정리 포인트**  
        > - 시선 속도는 항상 `vₗₒₛ = |v| cos φ` 로 계산할 수 있어요.  
        > - φ가 **90°**에 가까워질수록 시선 속도는 0에 가까워지고,  
        > - φ가 **0° 또는 180°**에 가까워질수록 시선 속도는 최대(±|v|)가 됩니다.  
        """
    )

# -----------------------------
# 오른쪽: 그림 (Plotly)
# -----------------------------
with right_col:
    st.subheader("🔭 궤도와 시선 속도 벡터 보기")

    fig = go.Figure()

    # 궤도 원 그리기
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
            name="별 궤도",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=orbit_planet_x,
            y=orbit_planet_y,
            mode="lines",
            line=dict(dash="dot"),
            name="행성 궤도",
        )
    )

    # 지구 위치
    fig.add_trace(
        go.Scatter(
            x=[earth_x],
            y=[earth_y],
            mode="markers+text",
            marker=dict(size=14),
            text=["지구 🌏"],
            textposition="bottom center",
            name="지구",
        )
    )

    # 질량중심
    fig.add_trace(
        go.Scatter(
            x=[0],
            y=[0],
            mode="markers+text",
            marker=dict(size=10, color="black"),
            text=["질량중심 ⚖️"],
            textposition="top center",
            name="질량중심",
        )
    )

    # 별 & 행성 위치
    fig.add_trace(
        go.Scatter(
            x=[star_pos[0]],
            y=[star_pos[1]],
            mode="markers+text",
            marker=dict(size=20),
            text=["별 🌞"],
            textposition="top center",
            name="별",
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
            name="행성",
        )
    )

    # 시선 방향 선 (지구 → 별, 지구 → 행성)
    fig.add_trace(
        go.Scatter(
            x=[earth_x, star_pos[0]],
            y=[earth_y, star_pos[1]],
            mode="lines",
            line=dict(width=1),
            name="별 시선",
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[earth_x, planet_pos[0]],
            y=[earth_y, planet_pos[1]],
            mode="lines",
            line=dict(width=1),
            name="행성 시선",
            showlegend=False,
        )
    )

    # 화살표를 위해 길이 스케일 설정
    vel_scale = 0.7  # 실제 속도 벡터 길이 스케일
    rad_scale = 0.7  # 시선 속도 성분 스케일

    def add_arrow(fig, start, vec, scale, name, color):
        end = start + scale * vec
        fig.add_trace(
            go.Scatter(
                x=[start[0], end[0]],
                y=[start[1], end[1]],
                mode="lines+markers",
                line=dict(width=3),
                marker=dict(size=1),
                name=name,
                showlegend=True,
            )
        )

    # 별의 실제 속도 벡터 & 시선 성분
    add_arrow(
        fig,
        star_pos,
        v_star / (np.linalg.norm(v_star) + 1e-9),
        vel_scale,
        "별 실제 속도 방향",
        "orange",
    )

    v_star_rad_vec = v_star_rad * los_star / (np.linalg.norm(v_star) + 1e-9)
    add_arrow(
        fig,
        star_pos,
        v_star_rad_vec,
        rad_scale,
        "별 시선 속도 성분",
        "red",
    )

    # 행성의 실제 속도 벡터 & 시선 성분
    add_arrow(
        fig,
        planet_pos,
        v_planet / (np.linalg.norm(v_planet) + 1e-9),
        vel_scale,
        "행성 실제 속도 방향",
        "green",
    )

    v_planet_rad_vec = v_planet_rad * los_planet / (np.linalg.norm(v_planet) + 1e-9)
    add_arrow(
        fig,
        planet_pos,
        v_planet_rad_vec,
        rad_scale,
        "행성 시선 속도 성분",
        "blue",
    )

    # 축/레이아웃 설정
    fig.update_layout(
        width=600,
        height=600,
        xaxis=dict(scaleanchor="y", scaleratio=1, visible=False),
        yaxis=dict(visible=False),
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5
        ),
        plot_bgcolor="rgba(255, 252, 240, 1)",  # 따뜻한 느낌 배경 🎨
    )

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# 하단 설명
# -----------------------------
st.markdown(
    """
    ---
    ### 🧠 수업에서 이렇게 활용해 보세요

    - 학생들에게 임의의 θ를 주고,  
      1️⃣ 그림에서 **시선 각 φ**를 대략 추측하게 한 뒤  
      2️⃣ `vₗₒₛ = |v| cos φ` 를 스스로 계산해 보게 하고  
      3️⃣ 앱에서 보여주는 값과 비교하게 해 보세요.  

    - 특히 **30° / 45° / 60°** 부근에서 멈춰 놓고  
      👉 `cos 30°`, `cos 45°`, `cos 60°` 값을 활용해  
      시선 속도가 실제 속도의 몇 % 정도인지  
      감으로 파악하게 하면 좋습니다. ✨  

    - “왜 우리는 행성의 속도가 아니라, **별의 시선 속도 변화**를 관측해서 행성을 찾는지”  
      질문을 던지고, 별의 작은 궤도와 시선 속도 화살표를 함께 보며 토의해 보세요. 💬🌍
    """
)
