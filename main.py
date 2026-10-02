import streamlit as st
import pandas as pd
import plotly.express as px
import random
import os
import platform
from datetime import datetime

# PDF 생성을 위한 ReportLab 모듈
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

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
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.05);
    }
    h2, h3, h4 {
        color: #4A154B !important;
        font-weight: 700;
    }
    p, span, label {
        color: #2D3748 !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: #FFF5F7 !important;
        border-right: 2px solid #FCE7F3;
    }
    
    .custom-card {
        background-color: #FFFFFF;
        border: 2px solid #FBCFE8;
        border-radius: 20px;
        padding: 22px;
        margin-bottom: 20px;
        box-shadow: 0 8px 16px rgba(244, 114, 182, 0.15);
    }

    .report-card {
        background-color: #FFFFFF;
        border: 2px dashed #EC4899;
        border-radius: 18px;
        padding: 20px;
        margin-top: 15px;
        box-shadow: 0 6px 12px rgba(236, 72, 153, 0.1);
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
        box-shadow: 0 2px 4px rgba(219, 39, 119, 0.1);
    }
    
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 2px solid #FBCFE8;
        padding: 16px;
        border-radius: 18px;
        box-shadow: 0 6px 12px rgba(244, 114, 182, 0.12);
    }
    
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
    
    div[data-baseweb="slider"] div {
        background-color: #EC4899 !important;
    }
    
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
# 4. 예시 데이터 세트 정의
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
# 6. PDF 생성용 헬퍼 함수
# -----------------------------------------------------------------------------
def register_korean_font():
    """OS 환경에 따른 한글 폰트 등록"""
    system_name = platform.system()
    font_path = None
    
    if system_name == "Windows":
        font_path = "C:/Windows/Fonts/malgun.ttf"
    elif system_name == "Darwin":
        font_path = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"
    else:
        font_path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
        
    if font_path and os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont("KoreanFont", font_path))
        return "KoreanFont"
    return "Helvetica"

def create_pdf_report(df_results, top_cand, gene_name, mit_w, doench_w, min_cutoff, fig_obj):
    pdf_filename = "gRNA_Screening_Report.pdf"
    img_filename = "temp_chart.png"
    
    # 1. Plotly 차트 이미지로 저장 (scale 조절로 해상도 확보)
    fig_obj.write_image(img_filename, width=700, height=350, scale=2)
    
    # 2. 폰트 설정
    font_name = register_korean_font()
    
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#4A154B'),
        spaceAfter=10
    )
    h2_style = ParagraphStyle(
        'DocH2',
        parent=styles['Heading2'],
        fontName=font_name,
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#EC4899'),
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#2D3748')
    )
    
    elements = []
    
    # 헤더
    elements.append(Paragraph("🧬 gRNA Clinical Screening Summary Report", title_style))
    elements.append(Paragraph(f"<b>생성 일시:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | <b>대상 유전자:</b> {gene_name}", body_style))
    elements.append(Spacer(1, 10))
    
    # 스크리닝 요약 테이블
    summary_data = [
        [Paragraph("<b>구분</b>", body_style), Paragraph("<b>설정 및 결과 값</b>", body_style)],
        [Paragraph("가중치 설정", body_style), Paragraph(f"안전성 (MIT) {mit_w}% : 효율성 (Doench) {doench_w}%", body_style)],
        [Paragraph("최소 안전성 컷오프", body_style), Paragraph(f"{min_cutoff} 점", body_style)],
        [Paragraph("스크리닝 통과 후보", body_style), Paragraph(f"총 {len(df_results)} 개", body_style)],
        [Paragraph("<b>최우수 추천 후보 (TOP 1)</b>", body_style), Paragraph(f"<b>{top_cand['후보명']}</b> ({top_cand['Sequence']}) - <b>종합 {top_cand['종합 점수']}점</b>", body_style)]
    ]
    
    t_summary = Table(summary_data, colWidths=[150, 390])
    t_summary.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FCE7F3')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#DB2777')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#FBCFE8')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(t_summary)
    
    # 2D 스크리닝 그래프 삽입
    elements.append(Paragraph("📊 2D 스크리닝 분석 맵", h2_style))
    elements.append(Image(img_filename, width=540, height=270))
    elements.append(Spacer(1, 10))
    
    # TOP 후보 상세 목록 테이블
    elements.append(Paragraph("📋 후보 리스트 (종합 점수 순)", h2_style))
    
    table_data = [[
        Paragraph("<b>순위</b>", body_style),
        Paragraph("<b>후보명</b>", body_style),
        Paragraph("<b>Sequence (20bp)</b>", body_style),
        Paragraph("<b>안전성</b>", body_style),
        Paragraph("<b>효율성</b>", body_style),
        Paragraph("<b>종합점수</b>", body_style)
    ]]
    
    for idx, row in df_results.iterrows():
        table_data.append([
            Paragraph(str(idx + 1), body_style),
            Paragraph(str(row['후보명']), body_style),
            Paragraph(str(row['Sequence']), body_style),
            Paragraph(str(row['안전성 (MIT)']), body_style),
            Paragraph(str(row['효율성 (Doench)']), body_style),
            Paragraph(f"<b>{row['종합 점수']}</b>", body_style)
        ])
        
    t_results = Table(table_data, colWidths=[35, 120, 180, 65, 65, 75])
    t_results.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FFF0F5')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#FBCFE8')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
    ]))
    
    elements.append(t_results)
    
    doc.build(elements)
    
    # 임시 차트 이미지 삭제
    if os.path.exists(img_filename):
        os.remove(img_filename)
        
    return pdf_filename

# -----------------------------------------------------------------------------
# 7. 사이드바 - 설정 및 입력
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

mit_weight = st.sidebar.slider("🛡 안전성 (MIT) 가중치 (%)", 0, 100, key="mit_w", on_change=on_mit_change)
doench_weight = st.sidebar.slider("⚡ 효율성 (Doench) 가중치 (%)", 0, 100, key="doench_w", on_change=on_doench_change)

st.sidebar.markdown("---")
st.sidebar.subheader("2. 🎯 최소 품질 컷오프")
min_mit_cutoff = st.sidebar.slider("최소 요구 안전성 점수", 0, 100, 50, step=5)

st.sidebar.markdown("---")
st.sidebar.subheader("3. 📝 gRNA 서열 입력")

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
    "🎲 다른 예시 데이터 불러오기", 
    use_container_width=True,
    on_click=change_random_example_data
)

if "current_gene_name" in st.session_state:
    st.sidebar.caption(f"📌 현재 선택된 유전자: **{st.session_state['current_gene_name']}**")

user_input = st.sidebar.text_area(
    "후보 목록 (`후보명, 20bp_서열`)", 
    height=150, 
    key="grna_input_text_area"
)

# -----------------------------------------------------------------------------
# 8. 메인 화면 구성
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
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("🔬 통과 후보", f"{len(df)}개")
        m2.metric("🏆 최상위 후보", top["후보명"])
        m3.metric("⭐ 최고 종합점수", f"{top['종합 점수']}점")
        m4.metric("🛡️ 평균 안전성", f"{round(df['안전성 (MIT)'].mean(), 1)}점")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
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
        
        # 2D 산점도 차트 생성
        fig = px.scatter(
            df,
            x="효율성 (Doench)",
            y="안전성 (MIT)",
            size="종합 점수",
            color="종합 점수",
            hover_name="후보명",
            text="후보명",
            color_continuous_scale="PuRd",
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
        
        with tab1:
            st.plotly_chart(fig, use_container_width=True)
            
        with tab2:
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 스크리닝 결과 CSV 다운로드", data=csv, file_name="screening_results.csv", mime="text/csv")
        
        # -----------------------------------------------------------------------------
        # 9. 📄 [PDF 변환] 스크리닝 리포트 다운로드 섹션
        # -----------------------------------------------------------------------------
        st.markdown("---")
        st.subheader("📄 PDF 리포트 출력")
        
        col_pdf1, col_pdf2 = st.columns([2, 5])
        with col_pdf1:
            if st.button("📑 PDF 요약 리포트 생성", use_container_width=True):
                with st.spinner("그래프 이미지 포함 PDF 리포트를 생성하는 중입니다..."):
                    gene_label = st.session_state.get("current_gene_name", "직접 입력 서열")
                    pdf_file_path = create_pdf_report(
                        df, top, gene_label, mit_weight, doench_weight, min_mit_cutoff, fig
                    )
                    
                    with open(pdf_file_path, "rb") as pdf_file:
                        pdf_bytes = pdf_file.read()
                        
                    st.session_state["pdf_bytes"] = pdf_bytes
                    st.success("PDF 생성이 완료되었습니다!")

        if "pdf_bytes" in st.session_state:
            st.download_button(
                label="📥 PDF 리포트 다운로드",
                data=st.session_state["pdf_bytes"],
                file_name=f"gRNA_Screening_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf"
            )
            
    else:
        st.warning("⚠️ 최소 요구 안전성 점수를 충족하는 후보가 없습니다. 필터 기준을 낮춰보세요.")
else:
    st.info("👈 사이드바에서 gRNA 후보 서열을 입력해 주세요.")
