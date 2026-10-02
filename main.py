import streamlit as st
import pandas as pd
import plotly.express as px
import random

# -----------------------------------------------------------------------------
# 1. 페이지 기본 설정
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="gRNA Clinical Screening Tool",
    page_icon="🧬",
    layout="wide"
)

# -----------------------------------------------------------------------------
# 2. 연핑크 배경 & 입체감 있는 귀여운 폰트 Custom CSS
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* 웹 폰트 불러오기 (귀엽고 깔끔한 나눔스퀘어라운드) */
    @import url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_two@1.0/NanumSquareRound.woff');
    
    * {
        font-family: 'NanumSquareRound', sans-serif !important;
    }

    /* 1. 메인 배경: 따뜻하고 부드러운 연핑크 톤 */
    .stApp {
        background-color: #FFF0F5;
        color: #2D3748;
    }
    
    /* 2. 타이틀 및 헤더: 딥 바이올렛 컬러로 색상 통일 */
    h1 {
        color: #4A154B !important;
        font-weight: 800;
        font-size: 2.2rem !important;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.05);
    }
    h2, h3, h4 {
        color: #4A154B !important;
        font-weight: 700;
    }
    p, span, label {
        color: #2D3748 !important;
    }
    
    /* 3. 사이드바: 뽀얀 핑크 화이트 톤 */
    [data-testid="stSidebar"] {
        background-color: #FFF5F7 !important;
        border-right: 2px solid #FCE7F3;
    }
    
    /* 4. 입체감 있는 귀여운 커스텀 카드 */
    .custom-card {
        background-color: #FFFFFF;
        border: 2px solid #FBCFE8;
        border-radius: 20px;
        padding: 22px;
        margin-bottom: 20px;
        /* 입체감을 주는 몽글몽글한 그림자 효과 */
        box-shadow: 0 8px 16px rgba(244, 114, 182, 0.15);
    }
    
    /* 5. 뱃지 스타일 */
    .badge-best {
        background-color: #FCE7F3;
        color: #DB2777 !important;
        padding: 6px 14px;
        border-radius: 15px;
        font-size: 0.85rem;
        font-weight: 800;
        display: inline-block;
        margin-bottom: 8px;
        box-shadow: 0 2px 4px rgba(219, 39, 119, 0.1);
    }
    
    /* 6. 메트릭 카드의 수치 및 입체감 강화 */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 2px solid #FBCFE8;
        padding: 16px;
        border-radius: 18px;
        box-shadow: 0 6px 12px rgba(244, 114, 182, 0.12);
    }
    
    /* 7. 귀여운 푸시 버튼 (입체 효과) */
    .stButton>button {
        background-color: #EC4899 !important;
        color: #FFFFFF !important;
        border-radius: 14px !important;
        border: none !important;
        font-weight: 700 !important;
        padding: 10px 20px !important;
        box-shadow: 0 4px 10px rgba(236, 72, 153, 0.3);
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 14px rgba(236, 72, 153, 0.4);
        background-color: #DB2777 !important;
    }
    
    /* 8. 슬라이더 바 색상 */
    div[data-baseweb="slider"] div {
        background-color: #EC4899 !important;
    }
    
    /* 9. 입력창 라운딩 & 그림자 */
    textarea {
        border-radius: 12px !important;
        border: 1.5px solid #FBCFE8 !important;
        background-color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. 타이틀 및 안내 Banner
# -----------------------------------------------------------------------------
st.title("🧬 유전자 가위 임상 적합성 스크리닝 도구")
st.markdown("✨ **안전성(MIT)**과 **효율성(Doench)**을 한눈에 비교하고 최적의 표적 후보를 선별해보세요!")

st.markdown("---")

# -----------------------------------------------------------------------------
# 4. 예시 데이터 세트
# -----------------------------------------------------------------------------
DATA_SAMPLES = {
    "HBB (겸상적혈구빈혈증 관련 유전자)": (
        "HBB_1460_rev, GACACCAACTGTCAACTGAT\n"
        "HBB_1542_fw, CCTTGCCCCACAGGGCAGTA\n"
        "HBB_Exon1_A, CTTGCCCCACAGGGCAGTAA\n"
        "HBB_Exon1_B, TGGTCTACCCTTGGACCCAG\n"
        "HBB_Exon2_C, AGTCTGCCATCACTGCCCTG"
    ),
    "BRCA1 (유방암/난소암 관련 유전자)": (
        "BRCA1_Exon2_1, GAGTAGTCAAGAGAAAGGAC\n"
        "BRCA1_Exon11_A, GGAAGAAACCACCAAGGTCC\n"
        "BRCA1_Exon11_B, ACAGCTACCCTTCCATCATA\n"
        "BRCA1_Exon18_C, CTGATGTGCTTTGTTCTGGA\n"
        "BRCA1_Exon24_D, TTACAGTTAGGTGAACAGCA"
    ),
    "TP53 (암 억제 유전자)": (
        "TP53_Exon4_1, GTCCCCCTTGCCGTCCCAAG\n"
        "TP53_Exon5_A, CCTCAACAAGATGTTTTGCC\n"
        "TP53_Exon7_B, GCGCACTGACCACTGGATGG\n"
        "TP53_Exon8_C, CCTATCCTGAGTAGTGGTAA\n"
        "TP53_Exon10_D, CGTGTTTGTGCCTGTCCTGG"
    )
}

# -----------------------------------------------------------------------------
# 5. 계산 로직
# -----------------------------------------------------------------------------
def validate_grna(sequence: str) -> tuple[bool, str]:
    seq = sequence.strip().upper()
    if len(seq) != 20:
        return False, f"길이 오류 ({len(seq)}bp)"
    if not set(seq).issubset({'A', 'T', 'G', 'C'}):
        return False, "유효하지 않은 염기 포함"
    return True, "정상"

def calculate_scores(sequence: str) -> dict:
    seq = sequence.strip().upper()
    gc_content = ((seq.count('G') + seq.count('C')) / 20) * 100
    doench_score = max(10, 100 - (abs(gc_content - 50) * 2.8))
    
    seed_region = seq[10:]
    seed_gc = ((seed_region.count('G') + seed_region.count('C')) / 10) * 100
    mit_score = max(15, 95 - abs(seed_gc - 50) * 1.5)
    
    return {
        "GC_Ratio": round(gc_content, 1),
        "Doench_Score": round(doench_score, 1),
        "MIT_Score": round(mit_score, 1)
    }

# -----------------------------------------------------------------------------
# 6. 사이드바 - 설정 및 입력
# -----------------------------------------------------------------------------
st.sidebar.header("⚙ 스크리닝 설정")

st.sidebar.subheader("1. ⚖️ 가중치 비율 설정")
if "mit_w" not in st.session_state:
    st.session_state["mit_w"] = 60
if "doench_w" not in st.session_state:
    st.session_state["doench_w"] = 40

def on_mit_change():
    st.session_state["doench_w"] = 100 - st.session_state["mit_w"]

def on_doench_change():
    st.session_state["mit_w"] = 100 - st.session_state["doench_w"]

mit_weight = st.sidebar.slider("🛡️ 안전성 (MIT) 가중치 (%)", 0, 100, key="mit_w", on_change=on_mit_change)
doench_weight = st.sidebar.slider("⚡ 효율성 (Doench) 가중치 (%)", 0, 100, key="doench_w", on_change=on_doench_change)

st.sidebar.markdown("---")
st.sidebar.subheader("2. 🎯 최소 품질 컷오프")
min_mit_cutoff = st.sidebar.slider("최소 요구 안전성 점수", 0, 100, 50, step=5)

st.sidebar.markdown("---")
st.sidebar.subheader("3. 📝 gRNA 서열 입력")

if "grna_input_text_area" not in st.session_state:
    st.session_state["grna_input_text_area"] = DATA_SAMPLES["HBB (겸상적혈구빈혈증 관련 유전자)"]

user_input = st.sidebar.text_area("후보 목록 (`후보명, 20bp_서열`)", height=150, key="grna_input_text_area")

# -----------------------------------------------------------------------------
# 7. 메인 화면 구성
# -----------------------------------------------------------------------------
if user_input.strip():
    lines = user_input.strip().split("\n")
    parsed_results = []
    
    for idx, line in enumerate(lines, 1):
        if not line.strip() or "," not in line:
            continue
        parts = line.split(",")
        name, seq = parts[0].strip(), parts[1].strip().upper()
        
        is_valid, _ = validate_grna(seq)
        if is_valid:
            scores = calculate_scores(seq)
            weighted = (scores["MIT_Score"] * (mit_weight / 100.0)) + (scores["Doench_Score"] * (doench_weight / 100.0))
            
            if scores["MIT_Score"] >= min_mit_cutoff:
                parsed_results.append({
                    "후보명": name,
                    "Sequence": seq,
                    "GC 함량 (%)": scores["GC_Ratio"],
                    "안전성 (MIT)": scores["MIT_Score"],
                    "효율성 (Doench)": scores["Doench_Score"],
                    "종합 점수": round(weighted, 1)
                })

    if parsed_results:
        df = pd.DataFrame(parsed_results).sort_values(by="종합 점수", ascending=False).reset_index(drop=True)
        top = df.iloc[0]
        
        # 📊 요약 메트릭 상자
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("🔬 통과 후보", f"{len(df)}개")
        m2.metric("🏆 최상위 후보", top["후보명"])
        m3.metric("⭐ 최고 종합점수", f"{top['종합 점수']}점")
        m4.metric("🛡️ 평균 안전성", f"{round(df['안전성 (MIT)'].mean(), 1)}점")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 📌 최상위 1위 후보 입체 강조 카드
        st.markdown(f"""
        <div class="custom-card">
            <span class="badge-best">🏆 TOP CANDIDATE</span>
            <h3 style="margin: 6px 0 12px 0;">{top['후보명']} <span style="font-size:0.95rem; color:#64748B;">({top['Sequence']})</span></h3>
            <p style="margin:0; font-size:1rem; color:#334155;">
                <b>GC 함량:</b> {top['GC 함량 (%)']}% &nbsp;|&nbsp; 
                <b>안전성 점수:</b> {top['안전성 (MIT)']}점 &nbsp;|&nbsp; 
                <b>효율성 점수:</b> {top['효율성 (Doench)']}점 &nbsp;|&nbsp; 
                <b>최종 종합 점수:</b> <span style="color:#EC4899; font-weight:800; font-size:1.1rem;">{top['종합 점수']}점</span>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["📊 2D 스크리닝 맵", "📋 상세 결과 데이터"])
        
        with tab1:
            # 연핑크 배경에 어울리는 Soft Pink/Purple 계열 그래프
            fig = px.scatter(
                df,
                x="효율성 (Doench)",
                y="안전성 (MIT)",
                size="종합 점수",
                color="종합 점수",
                hover_name="후보명",
                text="후보명",
                color_continuous_scale="PuRd", # Soft Pink/Purple 단색 스케일
                range_x=[0, 105],
                range_y=[0, 105]
            )
            fig.update_traces(textposition='top center')
            fig.update_layout(
                height=460,
                paper_bgcolor='#FFF0F5',
                plot_bgcolor='#FFFFFF',
                margin=dict(l=20, r=20, t=20, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)
            
        with tab2:
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 스크리닝 결과 CSV 다운로드", data=csv, file_name="screening_results.csv", mime="text/csv")
    else:
        st.warning("⚠️ 최소 요구 안전성 점수를 충족하는 후보가 없습니다. 필터 기준을 낮춰보세요.")
else:
    st.info("👈 사이드바에서 gRNA 후보 서열을 입력해 주세요.")
