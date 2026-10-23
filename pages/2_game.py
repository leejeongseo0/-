import streamlit as st
import streamlit.components.v1 as components

# 1. 페이지 설정
st.set_page_config(
    page_title="CRISPR Drag & Drop Lab",
    page_icon="🖐️",
    layout="wide"
)

# 2. 스타일 설정
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_two@1.0/NanumSquareRound.woff');
    * { font-family: 'NanumSquareRound', sans-serif !important; }
    .stApp { background-color: #E6F4F9; color: #1E293B; }
    h1 { color: #0F172A !important; font-weight: 800; }
</style>
""", unsafe_allow_html=True)

# 3. 타이틀 및 데이터 수신
st.title("🖐️ 인터랙티브 드래그 앤 드롭 유전자 가위 실습")
st.markdown("🧬 1페이지에서 선별된 gRNA를 가지고, **마우스로 도구를 직접 드래그하여** 유전자 편집 과정을 직접 체험해봐요!")
st.markdown("---")

top_cand = st.session_state.get("selected_top_grna", None)

if top_cand is None:
    st.warning("⚠️ 연동된 gRNA 데이터가 없습니다. 1페이지(스크리닝 도구)로 돌아가서 후보를 선별하고 '게임 시작' 버튼을 눌러주세요!")
    st.info("👈 사이드바 메뉴에서 메인 스크리닝 페이지로 이동하실 수 있습니다.")
else:
    seq = top_cand['Sequence']
    cand_name = top_cand['후보명']
    mit_score = top_cand['안전성 (MIT)']
    doench_score = top_cand['효율성 (Doench)']
    
    st.markdown(f"""
    <div style="background-color: #D1FAE5; border: 3px solid #059669; border-radius: 16px; padding: 15px; margin-bottom: 20px; text-align: center;">
        <h3 style="margin: 0; color: #065F46;">🔬 실습 대상: {cand_name} ({seq})</h3>
        <p style="margin: 5px 0 0 0; color: #047857; font-weight: bold;">안전성: {mit_score}점 | 효율성: {doench_score}점</p>
    </div>
    """, unsafe_allow_html=True)

    # 파이썬 f-string 중괄호 에러 방지를 위한 HTML 분리 조합
    html_part1 = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
        body {
            font-family: sans-serif;
            background-color: #E6F4F9;
            margin: 0;
            padding: 10px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .bench {
            background: #FFFFFF;
            border: 4px dashed #3B82F6;
            border-radius: 25px;
            width: 100%;
            max-width: 900px;
            height: 380px;
            position: relative;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            box-shadow: 0 10px 25px rgba(59, 130, 246, 0.15);
        }
        .guide-box {
            font-size: 1.2rem;
            font-weight: bold;
            color: #1E3A8A;
            margin-bottom: 20px;
            background: #EFF6FF;
            padding: 10px 20px;
            border-radius: 15px;
            border: 2px solid #BFDBFE;
            text-align: center;
        }
        .dna-display {
            background: #F8FAFC;
            border: 3px solid #64748B;
            border-radius: 16px;
            padding: 20px 30px;
            font-family: monospace;
            font-size: 1.3rem;
            font-weight: bold;
            color: #334155;
            letter-spacing: 2px;
            z-index: 2;
        }
        .tool {
            width: 130px;
            height: 65px;
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 1.1rem;
            cursor: grab;
            position: absolute;
            z-index: 10;
            user-select: none;
            box-shadow: 0 6px 15px rgba(0,0,0,0.15);
        }
        #grna {
            top: 30px;
            left: 30px;
            background-color: #FB923C;
            color: white;
            border: 3px solid #EA580C;
        }
        #cas9 {
            top: 30px;
            right: 30px;
            background-color: #64748B;
            color: white;
            border: 3px solid #475569;
            display: none;
        }
        .success-text {
            margin-top: 15px;
            font-size: 1.2rem;
            font-weight: bold;
            color: #059669;
            display: none;
        }
    </style>
    </head>
    <body>

    <div class="guide-box" id="guide">🎯 1단계: 주황색 [🧬 gRNA]를 마우스로 잡아 중앙의 DNA 위에 올려놓으세요!</div>

    <div class="bench" ondragover="event.preventDefault()" ondrop="dropItem(event)">
        <div class="tool" id="grna" draggable="true" ondragstart="event.dataTransfer.setData('text', 'grna')">🧬 gRNA</div>
        <div class="tool" id="cas9" draggable="true" ondragstart="event.dataTransfer.setData('text', 'cas9')">✂️ Cas9 가위</div>

        <div class="dna-display" id="dna">
            5'- """

    html_part2 = """ -3'
        </div>
    </div>

    <div class="success-text" id="success">🎉 유전자 편집 실습 완료!</div>

    <script>
        const targetSeq = '"""

    html_part3 = """';

        function dropItem(ev) {
            ev.preventDefault();
            let data = ev.dataTransfer.getData("text");
            let guide = document.getElementById("guide");
            let dna = document.getElementById("dna");
            let grna = document.getElementById("grna");
            let cas9 = document.getElementById("cas9");
            let success = document.getElementById("success");

            if (data === "grna" && grna.style.display !== "none") {
                grna.style.display = "none";
                dna.innerHTML = "5'- <span style='color:#EA580C;'>" + targetSeq + "</span> -3'<br><span style='font-size:0.9rem; color:#059669;'>✨ [gRNA 결합 성공!]</span>";
                dna.style.borderColor = "#FB923C";
                
                guide.innerHTML = "✂️ 2단계: 나타난 [회색 Cas9 가위]를 드래그해서 DNA 중앙으로 가져가세요!";
                cas9.style.display = "flex";

            } else if (data === "cas9" && cas9.style.display !== "none") {
                cas9.style.display = "none";
                let half = Math.floor(targetSeq.length / 2);
                let p1 = targetSeq.substring(0, half);
                let p2 = targetSeq.substring(half);

                dna.innerHTML = "5'- " + p1 + " <span style='color:red; font-size:1.6rem;'>⚡</span> " + p2 + " -3'<br><span style='font-size:0.9rem; color:red;'>✂️ [DNA 이중나선 절단 완료!]</span>";
                dna.style.borderColor = "#DC2626";
                
                guide.innerHTML = "🏆 완벽합니다! 유전자 가위 실습 성공!";
                success.style.display = "block";
            }
        }
    </script>
    </body>
    </html>
    """

    final_html = html_part1 + seq + html_part2 + seq + html_part3
    components.html(final_html, height=520)
