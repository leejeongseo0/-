import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------------------------------------------------------
# 1. 페이지 기본 설정
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="유전자 가위 임상 적합성 스크리닝 도구",
    page_icon="🧬",
    layout="wide"
)

st.title("🧬 유전자 가위 안전성·효율성 통합 계산 및 맞춤형 후보 선별 도구")
st.markdown("""
본 시스템은 연구 목적(부작용 최소화 vs 편집 효율 극대화)에 맞춰 **gRNA의 안전성(MIT Score)과 효율성(Doench Score)**에 
가중치를 직접 부여하고, 2D 산점도를 통해 최적의 표적 후보를 선별하는 웹 기반 스크리닝 서비스입니다.
""")

# -----------------------------------------------------------------------------
# 2. 로직 및 계산 함수 정의
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
    """GC 함량 기반 Doench(효율성) 및 Seed 영역 기반 MIT(안전성) 모의 점수 계산"""
    seq = sequence.strip().upper()
    
    # 1. GC 함량 계산
    g_count = seq.count('G')
    c_count = seq.count('C')
    gc_content = ((g_count + c_count) / 20) * 100
    
    # 2. Doench Score (효율성): GC 함량이 50%에 가까울수록 높음 (40~60% 최적)
    gc_diff = abs(gc_content - 50)
    doench_score = max(10, 100 - (gc_diff * 2.8))
    
    # 3. MIT Score (안전성): Seed 영역(3' 말단 10bp)의 GC 비율 및 반복 서열 감지 모의 알고리즘
    seed_region = seq[10:]
    seed_gc = ((seed_region.count('G') + seed_region.count('C')) / 10) * 100
    mit_score = max(15, 95 - abs(seed_gc - 50) * 1.5)
    
    return {
        "GC_Ratio": round(gc_content, 1),
        "Doench_Score": round(doench_score, 1),
        "MIT_Score": round(mit_score, 1)
    }

# -----------------------------------------------------------------------------
# 3. 사이드바 - 사용자 입력 및 가중치 설정
# -----------------------------------------------------------------------------
st.sidebar.header("⚙️️ 스크리닝 조건 설정")

# 1) 가중치 슬라이더
st.sidebar.subheader("1. 평가 가중치 비율 설정")
mit_weight = st.sidebar.slider(
    "🛡️ 안전성 (MIT Score) 가중치 (%)",
    min_value=0,
    max_value=100,
    value=60,
    step=5
)
doench_weight = 100 - mit_weight
st.sidebar.caption(f"⚡ 효율성 (Doench Score) 가중치: **{doench_weight}%**")

st.sidebar.markdown("---")

# 2) gRNA 후보 서열 입력 (세션 상태 활용)
st.sidebar.subheader("2. gRNA 후보 서열 입력")
st.sidebar.caption("형식: `후보명, 20bp_DNA_서열` (한 줄에 하나씩)")

example_data = (
    "HBB_1460_rev, GACACCAACTGTCAACTGAT\n"
    "HBB_1542_fw, CCTTGCCCCACAGGGCAGTA\n"
    "HBB_Exon1_A, CTTGCCCCACAGGGCAGTAA\n"
    "HBB_Exon1_B, TGGTCTACCCTTGGACCCAG\n"
    "HBB_Exon2_C, AGTCTGCCATCACTGCCCTG"
)

# 세션 상태 초기화 (최초 실행 시 기본 데이터 적용)
if "grna_input_text" not in st.session_state:
    st.session_state["grna_input_text"] = example_data

# 예시 데이터 불러오기 버튼
if st.sidebar.button("🧬 실제 HBB 유전자 예시 데이터 불러오기", use_container_width=True):
    st.session_state["grna_input_text"] = example_data
    st.rerun()

# 텍스트 입력창 (세션 상태 연동)
user_input = st.sidebar.text_area(
    "gRNA 서열 목록",
    value=st.session_state["grna_input_text"],
    height=180,
    key="grna_input_text_area"
)
st.session_state["grna_input_text"] = user_input

# -----------------------------------------------------------------------------
# 4. 메인 화면 - 분석 실행 및 데이터 처리
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
        
        # 가중 종합 점수 산출
        weighted_score = (scores["MIT_Score"] * (mit_weight / 100)) + (scores["Doench_Score"] * (doench_weight / 100))
        
        parsed_results.append({
            "후보명": name,
            "Sequence (20bp)": seq,
            "GC 함량 (%)": scores["GC_Ratio"],
            "안전성 (MIT)": scores["MIT_Score"],
            "효율성 (Doench)": scores["Doench_Score"],
            "임상 종합 점수": round(weighted_score, 1)
        })
    
    # 예외 상황 메시지 출력 (Part 4-3 대응)
    if error_logs:
        with st.expander("⚠️️ 입력 데이터 유효성 검사 경고 메시지", expanded=True):
            for err in error_logs:
                st.warning(err)
                
    if parsed_results:
        df = pd.DataFrame(parsed_results)
        df = df.sort_values(by="임상 종합 점수", ascending=False).reset_index(drop=True)
        
        top_candidate = df.iloc[0]
        
        # TOP 1 추천 뱃지 출력
        st.success(
            f"🏆 **설정한 가중치 기준 최적 gRNA 후보:** **{top_candidate['후보명']}** "
            f"(종합 점수: {top_candidate['임상 종합 점수']}점 | "
            f"안전성: {top_candidate['안전성 (MIT)']}점 / 효율성: {top_candidate['효율성 (Doench)']}점)"
        )
        
        # 시각화 & 결과 표 탭 구성
        tab1, tab2 = st.tabs(["📊 2D 스크리닝 Map (시각화)", "📋 전체 결과 데이터"])
        
        with tab1:
            st.subheader("안전성 vs 효율성 2D 스크리닝 지도")
            st.caption("그래프의 **우상단(오른쪽 위)**에 위치할수록 안전성과 효율성을 모두 충족하는 최적의 gRNA입니다.")
            
            fig = px.scatter(
                df,
                x="효율성 (Doench)",
                y="안전성 (MIT)",
                size="임상 종합 점수",
                color="임상 종합 점수",
                hover_name="후보명",
                hover_data=["Sequence (20bp)", "GC 함량 (%)"],
                text="후보명",
                color_continuous_scale="Viridis",
                range_x=[0, 105],
                range_y=[0, 105]
            )
            fig.update_traces(textposition='top center', marker=dict(sizeref=0.1, sizemode='area'))
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
            
        with tab2:
            st.subheader("상세 계산 결과")
            st.dataframe(df, use_container_width=True)
            
            # CSV 다운로드 기능 (수행평가 제출 지원)
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
    st.info("사이드바에 gRNA 후보 서열을 입력해 주거나 [실제 HBB 유전자 예시 데이터 불러오기] 버튼을 눌러주세요.")
