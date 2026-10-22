import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import random
import os
import platform
from datetime import datetime, timedelta

# PDF 생성을 위한 ReportLab 모듈
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
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
# 2. 연핑크 배경 & Custom CSS
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
    "HBB (겸상적혈구빈혈증 관련 유전자)": "HBB_1460_rev, GACACCAACTGTCAACTGAT\nHBB_1542_fw, CCTTGCCCCACAGGGCAGTA\nHBB_Exon1_A, CTTGCCCCACAGGGCAGTAA\nHBB_Exon1_B, TGGTCTACCCTTGGACCCAG\nHBB_Exon2_C, AGTCTGCCATCACTGCCCTG",
    "BRCA1 (유방암/난소암 관련 유전자)": "BRCA1_Exon2_1, GAGTAGTCAAGAGAAAGGAC\nBRCA1_Exon11_A, GGAAGAAACCACCAAGGTCC\nBRCA1_Exon11_B, ACAGCTACCCTTCCATCATA\nBRCA1_Exon18_C, CTGATGTGCTTTGTTCTGGA\nBRCA1_Exon24_D, TTACAGTTAGGTGAACAGCA",
    "TP53 (암 억제 유전자)": "TP53_Exon4_1, GTCCCCCTTGCCGTCCCAAG\nTP53_Exon5_A, CCTCAACAAGATGTTTTGCC\nTP53_Exon7_B, GCGCACTGACCACTGGATGG\nTP53_Exon8_C, CCTATCCTGAGTAGTGGTAA\nTP53_Exon10_D, CGTGTTTGTGCCTGTCCTGG"
}

# -----------------------------------------------------------------------------
# 5. 계산 로직 (구문 에러 방지를 위해 단순화)
# -----------------------------------------------------------------------------
def validate_grna(sequence: str):
    seq = sequence.strip().upper()
    if len(seq) != 20:
        return False, f"길이 오류 ({len(seq)}bp)"
    for char in seq:
        if char not in ['A', 'T', 'G', 'C']:
            return False, "유효하지 않은 염기 포함"
    return True, "정상"

def calculate_scores(sequence: str):
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
    system_name = platform.system()
    linux_font_paths = [
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "/usr/share/fonts/nanum/NanumGothic.ttf",
        "/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf"
    ]
    
    if system_name == "Windows":
        font_path = "C:/Windows/Fonts/malgun.ttf"
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont("KoreanFont", font_path))
            return "KoreanFont"
    elif system_name == "Darwin":
        font_path = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont("KoreanFont", font_path))
            return "KoreanFont"
            
    for path in linux_font_paths:
        if os.path.exists(path):
            pdfmetrics.registerFont(TTFont("KoreanFont", path))
            return "KoreanFont"
            
    return "Helvetica"

def create_pdf_report(df_results, top_cand, gene_name, mit_w, doench_w, min_cutoff, fig_obj):
    pdf_filename = "gRNA_Screening_Report.pdf"
    img_filename = "temp_chart.png"
    
    fig_mat, ax = plt.subplots(figsize=(7, 3.5))
    scatter = ax.scatter(
        df_results["효율성 (Doench)"], 
        df_results["안전성 (MIT)"], 
        c=df_results["종합 점수"], 
        cmap="PuRd", 
        s=df_results["종합 점수"] * 2.5,
        alpha=0.8,
        edgecolors="#EC4899"
    )
    
    for _, row in df_results.iterrows():
        ax.annotate(row["후보명"], (row["효율성 (Doench)"], row["안전성 (MIT)"]),
                    fontsize=8, ha='center', va='bottom', color='#4A154B', fontweight='bold')
                    
    ax.set_xlim(0, 105)
    ax.set_ylim(0, 105)
    ax.set_xlabel("Doench Score (Efficiency)", fontsize=9, color='#4A154B')
    ax.set_ylabel("MIT Score (Safety)", fontsize=9, color='#4A154B')
    ax.grid(True, linestyle="--", alpha=0.4)
    plt.colorbar(scatter, ax=ax, label="Total Score")
    plt.tight_layout()
    plt.savefig(img_filename, dpi=200)
    plt.close(fig_mat)
    
    font_name = register_korean_font()
    
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontName=font_name, fontSize=20, leading=24, textColor=colors.HexColor('#4A154B'), spaceAfter=10)
    h2_style = ParagraphStyle('DocH2
