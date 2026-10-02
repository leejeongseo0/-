import streamlit as st
import pandas as pd
import plotly.express as px
import random

# -----------------------------------------------------------------------------
# 1. 페이지 기본 설정
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="유전자 가위 임상 적합성 스크리닝 도구",
    page_icon="🧬",
    layout="wide"
)

# -----------------------------------------------------------------------------
# 2. 테마 3: 차세대 바이오테크 (Modern Biotech Emerald) Custom CSS
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* 메인 배경 및 기본 폰트 색상 */
    .stApp {
        background-color: #F8FAFC;
    }
    
    /* 헤더 및 타이틀 스타일 */
    h1 {
        color: #064E3B !important;
        font-weight: 700;
    }
    h2, h3 {
        color: #047857 !important;
    }
    
    /* 사이드바 스타일링 */
    [data-testid="stSidebar"] {
        background-color: #ECFDF5 !important;
        border-right: 1px solid #A7F3D0;
    }
    
    /* 버튼 스타일링 */
    .stButton>button {
        background-color: #10B981 !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #059669 !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    }
    
    /* 슬라이더 색상 (에메랄드 톤) */
    div[data-baseweb="slider"] div {
        background-color: #10B981 !important;
    }
    
    /* 탭 디자인 Custom */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #E2E8F0;
        border-radius: 6px;
        padding: 8px 16px;
        color: #334155;
    }
    .stTabs [aria-selected="true"] {
        background-color: #10B981 !important;
        color: white !important;
    }
    
    /* 정보 안내 박스 커스텀 */
    .stAlert {
        border-radius: 10px !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🧬 유전자 가위 안전성·효율성 통합 계산 및 맞춤형 후보 선별 도구")
st.markdown("""
본 시스템은 연구 목적(부작용 최소화 vs 편집 효율 극대화)에 맞춰 **gRNA의 안전성(MIT Score)과 효율성(Doench Score)**에 
가중치를 직접 부여하고, 2D 산점도를 통해 최적의 표적 후보를 선별하는 웹 기반 스크리닝 서비스입니다.
""")

# -----------------------------------------------------------------------------
# 3. 다양한 대표 유전자 gRNA 예시 데이터 세트 정의
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
    ),
    "CFTR (낭성섬유증 관련 유전자)": (
        "CFTR_F508del_1, CACCATTAAAGAAAATATCA\n"
        "CFTR_Exon3_A, ATTAAGCACAGTGGAAGAAT\n"
        "CFTR_Exon10_B, TGATGAAGTAGAAGTAATAC\n"
        "CFTR_Exon13_C, TTGCTCGTTGACCTCCACTC\n"
        "CFTR_Exon20_D, AGAGTACTTGGAGAAGGCTC"
    ),
    "MYC (종양 유전자)": (
        "MYC_Exon1_1, GCTGCTTAGACGCTGGATTT\n"
        "MYC_Exon2_A, GTGCTCCATGAGGAGACACC\n"
        "MYC_Exon2_B, CGACTCTGAGGAGGAACAAG\n"
        "MYC_Exon3_C, TCCAGCAGAAGGTGATCCAG\n"
        "MYC_Promoter_D, GCGACGCGCCCCAAGTTGGC"
    )
}

# -----------------------------------------------------------------------------
# 4. 로직 및 계산 함수 정의
# -----------------------------------------------------------------------------

def validate_grna(sequence: str) -> tuple[bool, str]:
    """gRNA 서열 유효성 검사 (20bp, ATGC 여부)"""
    seq = sequence.strip().upper()
    if len(seq) != 20:
        return False, f"서열 길이가 20bp가 아닙니다. (현재 {len(seq)}bp)"
    valid_bases = {'A', 'T', 'G', 'C'}
    if not set(seq).issubset(valid_bases):
        invalid_chars = set(seq) - valid_bases
        return False, f"유효하지 않은 염기가 포함되어 있습니다: {', '.join(invalid_chars)}"
    return True, "정상"

def calculate_scores(sequence: str) -> dict:
    """GC 함량 기반 Doench(효율성) 및 Seed 영역 기반 MIT(안전성) 점수 계산"""
    seq = sequence.strip().upper()
    
    # 1. GC 함량 계산
    g_count = seq.count('G')
    c_count = seq.count('C')
    gc_content = ((g_count + c_count) / 20) * 100
    
    # 2. Doench Score (효율성)
    gc_diff = abs(gc_content - 50)
    doench_score = max(10, 100 - (gc_diff * 2.8))
    
    # 3. MIT Score (안전성)
    seed_region = seq[10:]
    seed_gc = ((seed_region.count('G') + seed_region.count('C')) / 10) * 100
    mit_score = max(15, 95 - abs(seed_gc - 50) * 1.5)
    
    return {
        "GC_Ratio": round(gc_content, 1),
        "Doench_Score": round(doench_score, 1),
        "MIT_Score": round(mit_score, 1)
    }

# -----------------------------------------------------------------------------
# 5. 사이드바 - 양방향 연동 가중치 슬라이더 설정
# -----------------------------------------------------------------------------
st.sidebar.header("⚙ 스크리닝 조건 설정")
st.sidebar.subheader("1. 평가 가중치 비율 설정")

# 초기 세션 상태 설정
if "mit_w" not in st.session_state:
    st.session_state["mit_w"] = 60
if "doench_w" not in st.session_state:
    st.session_state["doench_w"] = 40

def on_mit_change():
    st.session_state["doench_w"] = 100 - st.session_state["mit_w"]

def on_doench_change():
    st.session_state["mit_w"] = 100 - st.session_state["doench_w"]

mit_weight = st.sidebar.slider(
    "🛡️ 안전성 (MIT Score) 가중치 (%)",
    min_value=0,
    max_value=100,
    step=1,
    key="mit_w",
    on_change=on_mit_change
)

doench_weight = st.sidebar.slider(
    "⚡ 효율성 (Doench Score) 가중치 (%)",
    min_value=0,
    max_value=100,
    step=1,
    key="doench_w",
    on_change=on_doench_change
)

st.sidebar.caption(f"💡 가중치 합계: **{mit_weight + doench_weight}%** (안전성 {mit_weight}% : 효율성 {doench_weight}%)")
st.sidebar.markdown("---")

# -----------------------------------------------------------------------------
# 6. 사이드바 - gRNA 후보 서열 입력
# -----------------------------------------------------------------------------
st.sidebar.subheader("2. gRNA 후보 서열 입력")
st.sidebar.caption("형식: `후보명, 20bp_DNA_서열` (한 줄에 하나씩)")

if "grna_input_text_area" not in st.session_state:
    st.session_state["grna_input_text_area"] = DATA_SAMPLES["HBB (겸상적혈구빈혈증 관련 유전자)"]
    st.session_state["current_gene_name"] = "HBB (겸상적혈구빈혈증 관련 유전자)"

def change_random_example_data():
    gene_list = list(DATA_SAMPLES.keys())
    available_genes = [g for g in gene_list if g != st.session_state.get("current_gene_name")]
    selected_gene = random.choice(available_genes)
    
    st.session_state["grna_input_text_area"] = DATA_SAMPLES[selected_gene]
    st.session_state["current_gene_name"] = selected_gene

st.sidebar.button(
    "🎲 다른 유전자 예시 데이터 불러오기", 
    use_container_width=True,
    on_click=change_random_example_data
)

if "current_gene_name" in st.session_state:
    st.sidebar.caption(f"📌 현재 선택된 타깃 유전자: **{st.session_state['current_gene_name']}**")

user_input = st.sidebar.text_area(
    "gRNA 서열 목록",
    height=180,
    key="grna_input_text_area"
)

# -----------------------------------------------------------------------------
# 7. 메인 화면 - 분석 실행 및 데이터 처리
# -----------------------------------------------------------------------------
if user_input.strip():
    lines = user_input.strip().split("\n")
    parsed_results = []
    error_logs = []
    
    for idx, line in enumerate(lines, 1):
        if not line.strip():
            continue
        parts = line.split(",")
        if len(parts) != 2:
            error_logs.append(f"Line {idx}: '후보명, 서열' 형식이 아닙니다. (`{line.strip()}`)")
            continue
            
        name = parts[0].strip()
        seq = parts[1].strip().upper()
        
        is_valid, msg = validate_grna(seq)
        if not is_valid:
            error_logs.append(f"Line {idx} [{name}]: {msg}")
            continue
            
        scores = calculate_scores(seq)
        weighted_score = (scores["MIT_Score"] * (mit_weight / 100.0)) + (scores["Doench_Score"] * (doench_weight / 100.0))
        
        parsed_results.append({
            "후보명": name,
            "Sequence (20bp)": seq,
            "GC 함량 (%)": scores["GC_Ratio"],
            "안전성 (MIT)": scores["MIT_Score"],
            "효율성 (Doench)": scores["Doench_Score"],
            "임상 종합 점수": round(weighted_score, 1)
        })
    
    if error_logs:
        with st.expander("⚠ 입력 데이터 유효성 검사 경고 메시지", expanded=True):
            for err in error_logs:
                st.warning(err)
                
    if parsed_results:
        df = pd.DataFrame(parsed_results)
        df = df.sort_values(by="임상 종합 점수", ascending=False).reset_index(drop=True)
        
        top_candidate = df.iloc[0]
        
        st.success(
            f"🏆 **선택 가중치 (안전성 {mit_weight}% : 효율성 {doench_weight}%) 기준 최적 gRNA:** **{top_candidate['후보명']}** "
            f"(종합 점수: {top_candidate['임상 종합 점수']}점 | "
            f"안전성: {top_candidate['안전성 (MIT)']}점 / 효율성: {top_candidate['효율성 (Doench)']}점)"
        )
        
        tab1, tab2 = st.tabs(["📊 2D 스크리닝 Map (시각화)", "📋 전체 결과 데이터"])
        
        with tab1:
            st.subheader("안전성 vs 효율성 2D 스크리닝 지도")
            st.caption("그래프의 **우상단(오른쪽 위)**에 위치할수록 안전성과 효율성을 모두 충족하는 최적의 gRNA입니다.")
            
            # 에메랄드 테마에 맞춘 Plotly 컬러 스케일 적용 (Emerald / Mint 톤)
            fig = px.scatter(
                df,
                x="효율성 (Doench)",
                y="안전성 (MIT)",
                size="임상 종합 점수",
                color="임상 종합 점수",
                hover_name="후보명",
                hover_data=["Sequence (20bp)", "GC 함량 (%)"],
                text="후보명",
                color_continuous_scale="Emrld",  # Emerald 테마 색상 팔레트
                range_x=[0, 105],
                range_y=[0, 105]
            )
            fig.update_traces(textposition='top center', marker=dict(sizeref=0.1, sizemode='area'))
            fig.update_layout(
                height=500,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(240,253,244,0.5)'
            )
            st.plotly_chart(fig, use_container_width=True)
            
        with tab2:
            st.subheader("상세 계산 결과")
            st.dataframe(df, use_container_width=True)
            
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 스크리닝 결과 CSV 다운로드",
                data=csv,
                file_name="grna_screening_results.csv",
                mime="text/csv",
            )
    else:
        st.info("유효한 gRNA 서열이 없습니다. 올바른 20bp 서열을 입력해 주세요.")
else:
    st.info("사이드바에 gRNA 후보 서열을 입력해 주거나 [🎲 다른 유전자 예시 데이터 불러오기] 버튼을 눌러주세요.")
