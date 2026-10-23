import streamlit as st
import time

# -----------------------------------------------------------------------------
# 1. 페이지 기본 설정
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="CRISPR 가위 실습실",
    page_icon="✂️",
    layout="wide"
)

# -----------------------------------------------------------------------------
# 2. Custom CSS (그림 속 일러스트 스타일 구현)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_two@1.0/NanumSquareRound.woff');
    
    * {
        font-family: 'NanumSquareRound', sans-serif !important;
    }

    .stApp {
        background-color: #E6F4F9; /* 그림의 하늘색 배경 테마 */
        color: #1E293B;
    }
    
    h1, h2, h3 {
        color: #0F172A !important;
        font-weight: 800;
    }
    
    /* 일러스트 느낌의 실험실 박스 */
    .lab-stage {
        background-color: #D1FAE5; /* 그림의 연한 초록빛 단백질 느낌 */
        border: 4px solid #059669;
        border-radius: 35px;
        padding: 30px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px rgba(5, 150, 105, 0.2);
    }
    
    .rna-tag {
        background-color: #FB923C; /* 주황색 RNA 선 */
        color: white;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 15px;
        font-size: 1.1rem;
    }
    
    .dna-strand-box {
        background-color: #FFFFFF;
        border: 3px solid #3B82F6;
        border-radius: 16px;
        padding: 15px;
        margin: 15px 0;
        font-family: monospace;
        font-size: 1.4rem;
        font-weight: bold;
        letter-spacing: 2px;
        color: #1E3A8A;
    }

    .stButton>button {
        background-color: #059669 !important;
        color: #FFFFFF !important;
        border-radius: 16px !important;
        border: none !important;
        font-weight: 800 !important;
        padding: 14px 28px !important;
        font-size: 1.2rem !important;
        box-shadow: 0 6px 15px rgba(5, 150, 105, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. 타이틀 & 데이터 수신
# -----------------------------------------------------------------------------
st.title("✂️ CRISPR 유전자 가위 인터랙티브 실습실")
st.markdown("🧬 1페이지에서 가져온 gRNA를 장착하고, **Cas9 단백질 가위로 목표 DNA를 직접 절단(Cutting)하는 실습**을 진행해봐요!")
st.markdown("---")

top_cand = st.session_state.get("selected_top_grna", None)

if top_cand is None:
    st.warning("⚠️ 연동된 gRNA 데이터가 없습니다. 1페이지(스크리닝 도구)로 돌아가서 후보를 선별하고 '게임 시작' 버튼을 눌러주세요!")
    st.info("👈 사이드바 메뉴에서 메인 스크리닝 페이지로 이동하실 수 있습니다.")
else:
    seq = top_cand['Sequence']
    
    # 세션 상태로 실습 단계 관리
    if "lab_step" not in st.session_state:
        st.session_state["lab_step"] = 1

    # -----------------------------------------------------------------------------
    # 실습 메인 스테이지 (그림 시각화 영역)
    # -----------------------------------------------------------------------------
    st.markdown(f"""
    <div class="lab-stage">
        <div class="rna-tag">🧬 [RNA] gRNA: {top_cand['후보명']} ({seq[:10]}...)</div>
        <h2 style="color: #065F46; margin: 5px 0;">🟢 PROTEIN (Cas9 가위 단백질 복합체)</h2>
        <p style="color: #047857; font-weight: bold; font-size: 1.1rem;">
            안전성 점수: {top_cand['안전성 (MIT)']}점 | 효율성 점수: {top_cand['효율성 (Doench)']}점
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 현재 DNA 상태 표현
    st.subheader("🧪 타겟 DNA 이중나선 사슬")
    
    if st.session_state["lab_step"] == 1:
        st.markdown(f"""
        <div class="dna-strand-box" style="text-align: center;">
            5'- {seq} -3' <br>
            3'- {''.join([{'A':'T','T':'A','G':'C','C':'G'}.get(c,'N') for c in seq])} -5'
        </div>
        """, unsafe_allow_html=True)
        st.info("👆 **1단계:** gRNA와 Cas9 단백질이 결합하여 대상 DNA 서열을 정확히 조준하고 있습니다. 아래 버튼을 눌러 가위를 작동시키세요!")
        
        if st.button("✂️ 2단계: Cas9 가위로 DNA 절단(Cutting) 실행!", use_container_width=True):
            with st.spinner("gRNA가 서열을 인식하고 Cas9 가위가 작동하는 중..."):
                time.sleep(0.8)
            st.session_state["lab_step"] = 2
            st.rerun()

    elif st.session_state["lab_step"] == 2:
        # 절단된 모습 표현 (중간이 끊어진 형태)
        half_idx = len(seq) // 2
        part1 = seq[:half_idx]
        part2 = seq[half_idx:]
        
        comp_seq = ''.join([{'A':'T','T':'A','G':'C','C':'G'}.get(c,'N') for c in seq])
        c_part1 = comp_seq[:half_idx]
        c_part2 = comp_seq[half_idx:]
        
        st.markdown(f"""
        <div class="dna-strand-box" style="text-align: center; color: #DC2626;">
            5'- {part1} &nbsp;⚡&nbsp; {part2} -3' <br>
            3'- {c_part1} &nbsp;⚡&nbsp; {c_part2} -5'
        </div>
        """, unsafe_allow_html=True)
        
        st.success("🎉 **찰칵!** Cas9 유전자 가위가 목표 DNA 이중나선을 완벽하게 절단(DSB)했습니다!")
        st.balloons()
        
        st.markdown("---")
        st.subheader("📊 실습 최종 평가 리포트")
        col1, col2, col3 = st.columns(3)
        col1.metric("🎯 절단 성공 여부", "성공 (Success)")
        col2.metric("🛡️ 세포 안전성", f"{top_cand['안전성 (MIT)']}점")
        col3.metric("🏆 실습 등급", "A+ 수석 연구원")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 처음부터 실습 다시 하기", use_container_width=True):
            st.session_state["lab_step"] = 1
            st.rerun()
