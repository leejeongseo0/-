import streamlit as st
import time

# -----------------------------------------------------------------------------
# 1. 페이지 기본 설정
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="CRISPR 청소년 가상 실험실",
    page_icon="🧪",
    layout="wide"
)

# -----------------------------------------------------------------------------
# 2. Custom CSS (교육용 가상 실험실 테마)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_two@1.0/NanumSquareRound.woff');
    
    * {
        font-family: 'NanumSquareRound', sans-serif !important;
    }

    .stApp {
        background-color: #F8FAFC;
        color: #1E293B;
    }
    
    h1 {
        color: #0F172A !important;
        font-weight: 800;
    }
    
    .lab-card {
        background-color: #FFFFFF;
        border: 2px solid #E2E8F0;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
    }
    
    .dna-box {
        display: inline-block;
        background-color: #F1F5F9;
        border: 2px solid #CBD5E1;
        border-radius: 8px;
        padding: 8px 12px;
        margin: 4px;
        font-family: monospace;
        font-weight: bold;
        font-size: 1.2rem;
        color: #334155;
    }
    
    .base-a { background-color: #FEE2E2; color: #991B1B; border-color: #FCA5A5; }
    .base-t { background-color: #E0E7FF; color: #3730A3; border-color: #A5B4FC; }
    .base-g { background-color: #FEF3C7; color: #92400E; border-color: #FCD34D; }
    .base-c { background-color: #DCFCE7; color: #166534; border-color: #86EFAC; }

    .stButton>button {
        background-color: #3B82F6 !important;
        color: #FFFFFF !important;
        border-radius: 12px !important;
        border: none !important;
        font-weight: 700 !important;
        padding: 12px 24px !important;
        box-shadow: 0 4px 6px rgba(59, 130, 246, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. 타이틀 & 데이터 수신
# -----------------------------------------------------------------------------
st.title("🧪 주니어 생명공학자 가상 유전자 편집실")
st.markdown("👋 환영합니다! 1페이지에서 가져온 gRNA를 가지고 **실제 유전자 가위가 어떻게 작동하는지** 눈으로 보고 직접 실험해봐요.")
st.markdown("---")

top_cand = st.session_state.get("selected_top_grna", None)

if top_cand is None:
    st.warning("⚠️ 연동된 gRNA 데이터가 없습니다. 1페이지(스크리닝 도구)로 돌아가서 후보를 선별하고 게임 시작 버튼을 눌러주세요!")
    st.info("👈 사이드바 메뉴에서 메인 스크리닝 페이지로 이동하실 수 있습니다.")
else:
    seq = top_cand['Sequence']
    
    st.markdown(f"""
    <div class="lab-card">
        <h3 style="margin: 0 0 8px 0; color: #1E293B;">🔬 현재 실험 중인 표적 서열 정보</h3>
        <p style="margin:0; font-size:1.05rem;">
            <b>후보 이름:</b> <span style="color:#3B82F6; font-weight:800;">{top_cand['후보명']}</span> &nbsp;|&nbsp; 
            <b>안전성:</b> {top_cand['안전성 (MIT)']}점 &nbsp;|&nbsp; 
            <b>효율성:</b> {top_cand['효율성 (Doench)']}점
        </p>
    </div>
    """, unsafe_allow_html=True)

    # -----------------------------------------------------------------------------
    # 단계별 실습 코너
    # -----------------------------------------------------------------------------
    tab_lab1, tab_lab2, tab_lab3 = st.tabs([
        "🧬 1단계: DNA & gRNA 염기 구조 확인", 
        "🧩 2단계: 상보적 결합 (짝꿍 맞추기)", 
        "✂️ 3단계: Cas9 유전자 가위 실시간 절단 실습"
    ])

    # -----------------------------------------------------------------------------
    # TAB 1: DNA 구조 확인
    # -----------------------------------------------------------------------------
    with tab_lab1:
        st.subheader("📌 gRNA 20개 염기 서열 시각화")
        st.markdown("유전자는 **A, T, G, C** 네 가지 염기의 조합으로 이루어져 있습니다. 아래는 선발된 gRNA의 실제 염기 구조입니다.")
        
        dna_html = "<div style='text-align: center; padding: 10px;'>"
        for char in seq:
            css_class = f"base-{char.lower()}"
            dna_html += f"<div class='dna-box {css_class}'>{char}</div>"
        dna_html += "</div>"
        
        st.markdown(dna_html, unsafe_allow_html=True)
        st.info("💡 **학습 포인트:** A는 항상 T와, G는 항상 C와 짝을 이루고 싶어 하는 성질(상보적 결합)이 있어요!")

    # -----------------------------------------------------------------------------
    # TAB 2: 상보적 결합 미니 퀴즈
    # -----------------------------------------------------------------------------
    with tab_lab2:
        st.subheader("🧩 DNA 염기 짝꿍 맞추기 퀴즈")
        st.markdown("gRNA가 목표 DNA를 정확히 찾으려면 짝꿍 염기가 올바르게 배치되어야 합니다.")
        
        sample_part = seq[:5]
        complement_map = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G'}
        correct_answer = "".join([complement_map.get(c, 'N') for c in sample_part])
        
        st.markdown(f"**목표 DNA 앞부분 5글자:** `{sample_part}`")
        user_ans = st.text_input("이 서열과 결합할 gRNA의 완벽한 짝꿍 5글자를 입력해보세요 (예: ATCGG):", max_chars=5)
        
        if user_ans:
            if user_ans.upper() == correct_answer:
                st.success(f"🎉 정답입니다! 완벽하게 결합했어요! (짝꿍 서열: {correct_answer})")
                st.balloons()
            else:
                st.error(f"❌ 아쉽네요! A↔T, G↔C 규칙을 생각하며 다시 도전해보세요. (정답: {correct_answer})")

    # -----------------------------------------------------------------------------
    # TAB 3: Cas9 유전자 가위 절단 실습
    # -----------------------------------------------------------------------------
    with tab_lab3:
        st.subheader("✂️ Cas9 유전자 가위 발사 및 절단 실습")
        st.markdown("이제 환자의 세포 속으로 유전자 가위를 투입해 목표 부위를 정확히 자르는 시뮬레이션을 시작합니다.")
        
        col_ctrl1, col_ctrl2 = st.columns(2)
        with col_ctrl1:
            delivery_mode = st.selectbox(
                "전달체 선택 (어떤 방법으로 가위를 넣을까요?)",
                ["나노입자(LNP) 주사 - 효율 높음", "바이러스(AAV) 전달 - 안전함", "전기천공법(Electroporation) - 연구실용 최고효율"]
            )
        with col_ctrl2:
            enzyme_power = st.slider("가위 활성화 에너지 조절", 50, 100, 80)

        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🚀 유전자 가위 발사 및 절단 시작!", use_container_width=True):
            status_placeholder = st.empty()
            prog_bar = st.progress(0)
            
            phases = [
                "1단계: 세포막 통과 및 핵 속으로 이동 중...",
                "2단계: gRNA가 표적 DNA 서열을 스캔하고 찾아내는 중...",
                "3단계: 완벽한 매칭 확인! Cas9 단백질 결합 완료...",
                "4단계: ✂️ 타겟 DNA 두 가닥을 정확히 절단(Cutting) 중..."
            ]
            
            for i, p_text in enumerate(phases):
                status_placeholder.markdown(f"### ⚡ {p_text}")
                prog_bar.progress((i + 1) * 25)
                time.sleep(0.6)
                
            status_placeholder.markdown("### ✅ 유전자 편집 실습 성공 완료!")
            
            # 결과 평가
            score_val = top_cand['효율성 (Doench)']
            
            st.markdown("---")
            st.subheader("📊 주니어 연구원 실습 결과표")
            
            m_col1, m_col2, m_col3 = st.columns(3)
            m_col1.metric("🎯 타겟 절단 정확도", f"{score_val}%")
            m_col2.metric("🛡️ 오프타겟(부작용) 위험", f"{100 - top_cand['안전성 (MIT)']}%")
            m_col3.metric("🌟 최종 실습 등급", "A+ (우수 연구원)" if score_val >= 70 else "B (재도전 추천)")
            
            if score_val >= 70:
                st.success("🎉 축하합니다! 완벽한 gRNA 선택과 전달체 조절로 유전자 교정에 성공하여 질병 원인을 치료했습니다!")
                st.balloons()
            else:
                st.warning("⚠️ 조금 아쉽네요! 1페이지에서 안전성과 효율성이 더 높은 gRNA 후보를 다시 골라보세요.")
