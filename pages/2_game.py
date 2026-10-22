import streamlit as st
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# 페이지 기본 설정
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="CRISPR Game",
    page_icon="🎮",
    layout="wide"
)

# -----------------------------------------------------------------------------
# Custom CSS
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_two@1.0/NanumSquareRound.woff');
    
    * {
        font-family: 'NanumSquareRound', sans-serif !important;
    }

    .stApp {
        background-color: #FFF0F5;
        color: #2D3748;
    }
    
    h1, h2, h3 {
        color: #4A154B !important;
        font-weight: 800;
    }
    
    .game-card {
        background-color: #FFFFFF;
        border: 2px solid #EC4899;
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 8px 16px rgba(236, 72, 153, 0.15);
    }

    .badge-best {
        background-color: #FCE7F3;
        color: #DB2777 !important;
        padding: 6px 14px;
        border-radius: 15px;
        font-size: 0.85rem;
        font-weight: 800;
        display: inline-block;
        margin-bottom: 8px;
    }

    .stButton>button {
        background-color: #EC4899 !important;
        color: #FFFFFF !important;
        border-radius: 14px !important;
        border: none !important;
        font-weight: 700 !important;
        padding: 12px 24px !important;
        box-shadow: 0 4px 10px rgba(236, 72, 153, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 메인 게임 화면
# -----------------------------------------------------------------------------
st.title("🎮 CRISPR 유전자 편집 시뮬레이션 게임")
st.markdown("🎯 **1페이지에서 선별된 최적의 gRNA**를 가지고 세포 치료 시뮬레이션을 진행해보세요!")
st.markdown("---")

# 1페이지에서 저장된 세션 상태 가져오기
top_cand = st.session_state.get("selected_top_grna", None)

if top_cand is None:
    st.warning("⚠️ 1페이지(스크리닝 도구)에서 먼저 gRNA 분석을 완료하고 최적 후보를 선별해주세요!")
    st.info("💡 사이드바 메뉴에서 메인 페이지로 돌아가 스크리닝을 진행할 수 있습니다.")
else:
    # 1페이지 데이터 표시 카드
    st.markdown(f"""
    <div class="game-card">
        <span class="badge-best">🚀 준비된 표적 후보</span>
        <h3 style="margin: 4px 0 8px 0;">{top_cand['후보명']} <span style="font-size:0.95rem; color:#64748B;">({top_cand['Sequence']})</span></h3>
        <p style="margin:0; font-size:0.95rem;">
            <b>안전성 점수:</b> {top_cand['안전성 (MIT)']}점 &nbsp;|&nbsp; 
            <b>효율성 점수:</b> {top_cand['효율성 (Doench)']}점 &nbsp;|&nbsp; 
            <b>최종 종합 점수:</b> <span style="color:#EC4899; font-weight:800;">{top_cand['종합 점수']}점</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("🛠️ 실험 조건 세팅")
    
    col_g1, col_g2, col_g3 = st.columns(3)
    with col_g1:
        vector_type = st.selectbox(
            "1. 전달체(Vector) 선택",
            ["AAV 바이러스 (안전함/효율 보통)", "LNP 리포좀 (고효율/약간의 독성)", "Electroporation (최고효율/세포손상 위험)"]
        )
    with col_g2:
        grna_dosage = st.slider("2. gRNA 투여 농도 (nM)", 10, 200, 50, step=10)
    with col_g3:
        incubation_time = st.slider("3. 세포 배양 시간 (Hours)", 12, 72, 24, step=6)

    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🚀 유전자 편집 시뮬레이션 실행!", use_container_width=True):
        with st.spinner("세포 내 gRNA 가위 발현 및 표적 절단을 진행하고 있습니다..."):
            base_eff = top_cand["효율성 (Doench)"]
            base_safety = top_cand["안전성 (MIT)"]
            
            vec_eff_mult = 1.0
            vec_tox_risk = 0
            if "LNP" in vector_type:
                vec_eff_mult = 1.15
                vec_tox_risk = 5
            elif "Electroporation" in vector_type:
                vec_eff_mult = 1.3
                vec_tox_risk = 15
            
            dosage_factor = grna_dosage / 50.0
            cut_rate = min(99.9, base_eff * vec_eff_mult * (0.6 + (dosage_factor * 0.4)) * (incubation_time / 24.0))
            
            offtarget_risk = max(0, (100 - base_safety) * (dosage_factor * 0.8) + vec_tox_risk)
            cell_viability = max(10, 100 - (offtarget_risk * 0.5) - (vec_tox_risk * 0.8))
            
            cut_rate = round(cut_rate, 1)
            offtarget_risk = round(offtarget_risk, 1)
            cell_viability = round(cell_viability, 1)

            st.markdown("---")
            st.subheader("📊 시뮬레이션 결과 리포트")
            
            col_r1, col_r2, col_r3 = st.columns(3)
            col_r1.metric("🎯 목표 유전자 절단율", f"{cut_rate}%")
            col_r2.metric("⚠️ 오프타겟 위험도", f"{offtarget_risk}%")
            col_r3.metric("🧪 세포 생존율", f"{cell_viability}%")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # 게이지 차트
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = cut_rate,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "유전자 절단 성공률 (%)", 'font': {'size': 18, 'color': '#4A154B'}},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "#EC4899"},
                    'steps': [
                        {'range': [0, 50], 'color': "#FCE7F3"},
                        {'range': [50, 80], 'color': "#FBCFE8"},
                        {'range': [80, 100], 'color': "#F472B6"}
                    ],
                }
            ))
            fig_gauge.update_layout(height=300, paper_bgcolor='#FFF0F5', margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_gauge, use_container_width=True)

            # 성공 및 실패 판정
            if cut_rate >= 80 and cell_viability >= 70 and offtarget_risk < 30:
                st.balloons()
                st.success("🎉 **실험 성공!** 목표 유전자 절단율 80% 이상 및 안정적인 세포 생존율을 달성했습니다!")
            elif cut_rate < 80:
                st.warning("⚠️ **절단율 부족:** gRNA 농도를 높이거나 배양 시간을 늘려보세요.")
            else:
                st.error("🚨 **독성 초과:** 오프타겟 부작용으로 세포 손상이 큽니다. 농도를 낮추거나 다른 전달체를 선택하세요.")
