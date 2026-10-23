import streamlit as st
import plotly.graph_objects as go
import time

# -----------------------------------------------------------------------------
# 1. 페이지 기본 설정
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="CRISPR Clinical VR Simulator",
    page_icon="🏥",
    layout="wide"
)

# -----------------------------------------------------------------------------
# 2. Custom CSS (의료 시뮬레이션 테마)
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
    
    h1 {
        color: #4A154B !important;
        font-weight: 800;
        font-size: 2.2rem !important;
    }
    
    .patient-card {
        background-color: #FFFFFF;
        border: 2px solid #FBCFE8;
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 8px 16px rgba(244, 114, 182, 0.15);
    }
    
    .step-box {
        background-color: #FFFFFF;
        border-left: 5px solid #EC4899;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }

    .stButton>button {
        background-color: #EC4899 !important;
        color: #FFFFFF !important;
        border-radius: 14px !important;
        border: none !important;
        font-weight: 700 !important;
        padding: 12px 24px !important;
        font-size: 1.05rem !important;
        box-shadow: 0 4px 10px rgba(236, 72, 153, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. 타이틀 & 세션 데이터 확인
# -----------------------------------------------------------------------------
st.title("🏥 CRISPR 임상 유전자 치료 시뮬레이터")
st.markdown("👨‍⚕️ **주치의 선생님 환영합니다.** 1페이지에서 선별된 gRNA를 기반으로 유전자 치료 프로토콜을 수행하세요.")
st.markdown("---")

top_cand = st.session_state.get("selected_top_grna", None)

if top_cand is None:
    st.warning("⚠️ 1페이지(스크리닝 도구)에서 먼저 gRNA 분석을 실행하여 최적 후보를 선별해주세요!")
    st.info("👈 사이드바 메뉴에서 메인 스크리닝 페이지로 이동하실 수 있습니다.")
else:
    # -----------------------------------------------------------------------------
    # 환자 차트 & 치료 물질 정보
    # -----------------------------------------------------------------------------
    st.markdown(f"""
    <div class="patient-card">
        <h3 style="margin: 0 0 10px 0; color: #4A154B;">📋 임상 치료 수술/투여 차트</h3>
        <p style="margin:0; font-size:1rem;">
            <b>환자 대상 유전자:</b> {st.session_state.get('current_gene_name', 'HBB 유전자 질환')} &nbsp;|&nbsp; 
            <b>선정된 표적 gRNA:</b> <span style="color:#EC4899; font-weight:800;">{top_cand['후보명']}</span> ({top_cand['Sequence']})<br>
            <b>gRNA 기본 성능:</b> 안전성 점수 <b>{top_cand['안전성 (MIT)']}점</b> / 효율성 점수 <b>{top_cand['효율성 (Doench)']}점</b>
        </p>
    </div>
    """, unsafe_allow_html=True)

    # -----------------------------------------------------------------------------
    # 게임 단계 구성 (3-Step 인터랙티브 프로토콜)
    # -----------------------------------------------------------------------------
    st.subheader("🔬 유전자 치료 프로토콜 진행")
    
    tab_step1, tab_step2, tab_step3 = st.tabs([
        "STEP 1. 치료 방식 선택 (현실 반영)", 
        "STEP 2. 약물 정량 계산 & 수술/투여 준비", 
        "STEP 3. 세포 내 편집 및 모니터링"
    ])

    # -----------------------------------------------------------------------------
    # STEP 1: 치료 방식 결정
    # -----------------------------------------------------------------------------
    with tab_step1:
        st.markdown("""
        <div class="step-box">
            <b>👨‍⚕️ 의료진 가이드:</b> 유전자 치료는 실제 수술실 절개보다는 <b>체외(Ex vivo) 세포 편집 후 재주입</b> 방식 또는 <b>체내(In vivo) 특수 주사</b> 방식을 주로 사용합니다.
        </div>
        """, unsafe_allow_html=True)
        
        therapy_method = st.radio(
            "유전자 전달 방식을 선택하세요:",
            [
                "💉 체외 편집 (Ex vivo): 환자 혈액에서 줄기세포를 채취하여 외부에서 유전자 편집 후 혈관 재주입 (가장 안전함)",
                "🧬 체내 주사 (In vivo - LNP): 유전자 가위를 나노입자(LNP)로 감싸 환자 표적 장기에 표적 주사 (효율 높음)",
                "🔬 체내 바이러스 주입 (In vivo - AAV): 안전성이 검증된 바이러스 전달체에 탑재하여 혈관 투여 (지속성 높음)"
            ]
        )
        st.info("💡 팁: 환자의 상태와 표적 장기에 따라 적절한 전달체를 선택하는 것이 치료 성공의 핵심입니다.")

    # -----------------------------------------------------------------------------
    # STEP 2: 수술/투여 세팅
    # -----------------------------------------------------------------------------
    with tab_step2:
        col_s2_1, col_s2_2 = st.columns(2)
        with col_s2_1:
            dosage = st.slider("💉 gRNA-Cas9 정밀 투여 농도 (nM)", 10, 200, 50, step=10)
            st.caption("농도가 너무 낮으면 효과가 없고, 너무 높으면 오프타겟 독성이 발생합니다.")
        with col_s2_2:
            incubation_time = st.slider("⏱️ 반응/배양 시간 (Hours)", 12, 72, 24, step=6)
            st.caption("충분한 시간이 확보되어야 목표 유전자가 안정적으로 절단/수정됩니다.")

    # -----------------------------------------------------------------------------
    # STEP 3: 수술/투여 시뮬레이션 실행 및 모니터링
    # -----------------------------------------------------------------------------
    with tab_step3:
        st.markdown("수술실/투여실 상태: **준비 완료**")
        
        if st.button("💉 유전자 치료 수술/투여 시작", use_container_width=True):
            status_box = st.empty()
            progress_bar = st.progress(0)
            
            # 실시간 연출 모션
            steps_text = [
                "1. 환자로부터 세포 채취 / 표적 장기 투여 준비 중...",
                "2. gRNA-Cas9 유전자 가위 복합체 주입 중...",
                "3. 표적 DNA 염기 서열 탐색 및 가이드 바인딩 진행 중...",
                "4. 목표 DNA 쌍사슬 절단(DSB) 및 유전자 교정 수행 중...",
                "5. 환자 바이탈 모니터링 및 세포 생존율 측정 중..."
            ]
            
            for idx, text in enumerate(steps_text):
                status_box.markdown(f"⏳ **[임상 진행 중]** {text}")
                progress_bar.progress((idx + 1) * 20)
                time.sleep(0.4)
                
            status_box.success("✅ 유전자 치료 프로토콜 및 모니터링 완료!")
            
            # -----------------------------------------------------------------------------
            # 데이터 시뮬레이션 계산 로직
            # -----------------------------------------------------------------------------
            base_eff = top_cand["효율성 (Doench)"]
            base_safety = top_cand["안전성 (MIT)"]
            
            method_mult = 1.0
            tox_risk = 0
            if "LNP" in therapy_method:
                method_mult = 1.15
                tox_risk = 6
            elif "Ex vivo" in therapy_method:
                method_mult = 0.95
                tox_risk = 1
            elif "AAV" in therapy_method:
                method_mult = 1.05
                tox_risk = 3
                
            dosage_factor = dosage / 50.0
            time_factor = incubation_time / 24.0
            
            cut_rate = min(99.9, base_eff * method_mult * (0.6 + (dosage_factor * 0.4)) * (time_factor ** 0.5))
            offtarget_risk = max(0, (100 - base_safety) * (dosage_factor * 0.8) + tox_risk)
            cell_viability = max(10, 100 - (offtarget_risk * 0.4) - (tox_risk * 1.2))
            
            cut_rate = round(cut_rate, 1)
            offtarget_risk = round(offtarget_risk, 1)
            cell_viability = round(cell_viability, 1)

            st.markdown("---")
            st.subheader("📊 환자 치료 결과 리포트 (Vitals & Efficacy)")
            
            res_col1, res_col2, res_col3 = st.columns(3)
            res_col1.metric("🎯 목표 유전자 절단/교정율", f"{cut_rate}%")
            res_col2.metric("⚠️ 오프타겟 부작용 위험도", f"{offtarget_risk}%")
            res_col3.metric("🧪 환자 세포 생존율", f"{cell_viability}%")
            
            # 게이지 차트
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = cut_rate,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "유전자 편집 치료 성공률 (%)", 'font': {'size': 18, 'color': '#4A154B'}},
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
            fig_gauge.update_layout(height=280, paper_bgcolor='#FFF0F5', margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_gauge, use_container_width=True)

            # 치료 종합 최종 임상 판정
            if cut_rate >= 80 and cell_viability >= 75 and offtarget_risk < 25:
                st.balloons()
                st.success("🎉 **임상 성공 (Clinical Success)!** 환자의 목표 유전자가 안전하게 교정되었으며 완치 가능성이 매우 높습니다.")
            elif cut_rate < 80:
                st.warning("⚠️ **치료 효과 미달:** 유전자 교정 비율이 낮아 질환 완치 기준에 미달했습니다. 농도나 반응 시간을 재조정하세요.")
            else:
                st.error("🚨 **임상 부작용 발생:** 오프타겟 절단 및 세포 독성으로 환자 세포 손상이 심각합니다. 더 안전한 gRNA를 선택하거나 농도를 낮추세요.")
