import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------------------------------------------------------
# Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="gRNA Clinical Screening Tool",
    page_icon="🧬",
    layout="wide"
)

# -----------------------------------------------------------------------------
# Helper Functions (gRNA Analysis & Scoring)
# -----------------------------------------------------------------------------
def validate_grna(sequence: str):
    """gRNA 서열의 유효성 검사 (길이 20bp, ATGC 여부)"""
    seq = sequence.upper().strip()
    if len(seq) != 20:
        return False, f"서열 길이가 20bp가 아닙니다 (현재 {len(seq)}bp)."
    if not all(base in "ATGC" for base in seq):
        invalid_bases = set(b for b in seq if b not in "ATGC")
        return False, f"유효하지 않은 염기({', '.join(invalid_bases)})가 포함되어 있습니다."
    return True, seq

def calculate_scores(seq: str):
    """
    gRNA 서열을 기반으로 Doench (효율성) 및 MIT (안전성) 점수 모의 산출
    """
    # 1. GC 함량 계산
    gc_count = seq.count('G') + seq.count('C')
    gc_ratio = (gc_count / 20) * 100

    # 2. Doench Score (효율성 모의 로직): GC 함량이 40~60% 구간일 때 높은 점수
    if 40 <= gc_ratio <= 60:
        doench_score = 75 + (10 - abs(50 - gc_ratio)) * 2
    else:
        doench_score = max(15.0, 60 - abs(50 - gc_ratio) * 2.5)

    # 3. MIT Score (안전성 모의 로직): PAM 인접 Seed 영역(11~20bp)의 GC 비율 고려
    seed_region = seq[10:]
    seed_gc = (seed_region.count('G') + seed_region.count('C')) / 10
    mit_score = 80 + (0.5 - abs(0.5 - seed_gc)) * 30

    return {
        "GC_Ratio": round(gc_ratio, 1),
        "Doench_Efficiency": round(doench_score, 1),
        "MIT_Safety": round(mit_score, 1)
    }

# -----------------------------------------------------------------------------
# Main Application UI
# -----------------------------------------------------------------------------
st.title("🧬 임상 적합성 gRNA Target / Off-Target 스크리닝 App")
st.markdown("""
본 서비스는 유전자 치료제 개발 시 **안전성(MIT Score)**과 **작동 효율성(Doench Score)**을 다각도로 평가하여, 
설정한 임상 가중치에 맞는 최적의 gRNA 후보군을 스크리닝하는 도구입니다.
""")

st.divider()

# Sidebar: Inputs & Parameters
with st.sidebar:
    st.header("⚙️ 분석 설정 및 입력")
    
    st.subheader("1. 임상 평가 가중치 설정")
    safety_weight = st.slider("안전성 (MIT Score) 가중치 (%)", min_value=0, max_value=100, value=60, step=5)
    efficiency_weight = 100 - safety_weight
    st.caption(f"💡 현재 반영 비율: **안전성 {safety_weight}% : 효율성 {efficiency_weight}%**")
    
    st.subheader("2. gRNA 후보 서열 입력")
    st.caption("형식: `후보명, 20bp_DNA_서열` (한 줄에 하나씩 입력)")
    
    # 예시 기본 데이터 제공 (세특 HBB 탐구 관련 서열 예시 포함)
    default_input = (
        "1460/rev, GACACCAACUGUCAACUGAU\n"
        "1542/fw, CCUUGCCCCACAGGGCAGUA\n"
        "Candidate_C, ATGCGATCGATCGATCGATC\n"
        "Candidate_D, GGGGGGGGGGGGGGGGGGGG\n"
        "Candidate_E, ATATATATATATATATATAT"
    ).replace("U", "T")  # DNA 변환
    
    user_input = st.text_area("gRNA 서열목록", value=default_input, height=180)
    
    run_btn = st.button("🚀 gRNA 분석 실행", type="primary", use_container_width=True)

# -----------------------------------------------------------------------------
# Execution & Results
# -----------------------------------------------------------------------------
if run_btn or "grna_df" in st.session_state:
    results = []
    errors = []
    
    lines = user_input.strip().split("\n")
    for idx, line in enumerate(lines, 1):
        if not line.strip():
            continue
        parts = line.split(",")
        if len(parts) != 2:
            errors.append(f"Line {idx}: 올바른 입력 형식(이름, 서열)이 아닙니다 -> `{line}`")
            continue
            
        name = parts[0].strip()
        raw_seq = parts[1].strip().upper().replace("U", "T")
        
        # 입력 검증 (Part 4-3 예외 처리)
        is_valid, msg = validate_grna(raw_seq)
        if not is_valid:
            errors.append(f"[{name}] {msg}")
            continue
            
        # 점수 계산
        scores = calculate_scores(raw_seq)
        
        # 가중 종합 점수 계산
        composite_score = (
            (scores["MIT_Safety"] * (safety_weight / 100.0)) +
            (scores["Doench_Efficiency"] * (efficiency_weight / 100.0))
        )
        
        results.append({
            "후보명": name,
            "Sequence": raw_seq,
            "GC 함량 (%)": scores["GC_Ratio"],
            "안전성 (MIT)": scores["MIT_Safety"],
            "효율성 (Doench)": scores["Doench_Efficiency"],
            "임상 종합 점수": round(composite_score, 1)
        })

    # 오류 메시지 출력
    if errors:
        with st.expander("⚠️ 입력 검증 경고/오류 목록", expanded=True):
            for err in errors:
                st.error(err)

    if results:
        df = pd.DataFrame(results)
        df = df.sort_values(by="임상 종합 점수", ascending=False).reset_index(drop=True)
        st.session_state["grna_df"] = df

        # 레이아웃: 2개 컬럼 (시각화 차트 / 추천 요약)
        col1, col2 = st.columns([3, 2])

        with col1:
            st.subheader("📊 2D gRNA 임상 적합성 스크리닝 Map")
            st.caption("우상단(X축·Y축 높음)에 위치할수록 효율성과 안전성을 모두 갖춘 우수한 후보입니다.")
            
            fig = px.scatter(
                df,
                x="효율성 (Doench)",
                y="안전성 (MIT)",
                text="후보명",
                size="임상 종합 점수",
                color="임상 종합 점수",
                color_continuous_scale="Viridis",
                hover_data=["Sequence", "GC 함량 (%)"],
                title="gRNA Safety vs Efficiency Scatter Plot"
            )
            fig.update_traces(textposition='top center', marker=dict(sizeref=0.1, sizemode='area'))
            fig.update_layout(height=450)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("🏆 최적 후보 TOP gRNA")
            top_candidate = df.iloc[0]
            st.success(f"**1위 추천: {top_candidate['후보명']}**")
            st.metric(label="임상 종합 점수", value=f"{top_candidate['임상 종합 점수']} 점")
            
            st.markdown(f"""
            - **Sequence**: `{top_candidate['Sequence']}`
            - **안전성 (MIT)**: {top_candidate['안전성 (MIT)']} 점
            - **효율성 (Doench)**: {top_candidate['효율성 (Doench)']} 점
            - **GC 비율**: {top_candidate['GC 함량 (%)']}%
            """)
            st.info("💡 가중치 슬라이더를 변경하면 종합 점수 순위가 실시간으로 변경됩니다.")

        st.divider()

        # 데이터 테이블 및 다운로드
        st.subheader("📋 전체 스크리닝 데이터 결과")
        st.dataframe(df, use_container_width=True)

        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 스크리닝 결과 CSV 다운로드",
            data=csv_data,
            file_name="grna_clinical_screening_results.csv",
            mime="text/csv"
        )
else:
    st.info("👈 좌측 사이드바에서 gRNA 서열을 입력하거나 설정 후 **[gRNA 분석 실행]** 버튼을 눌러주세요.")
