import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import random
import os
import platform
from datetime import datetime

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
