import streamlit as st
import streamlit.components.v1 as components

# -----------------------------------------------------------------------------
# 1. 페이지 기본 설정
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="CRISPR Drag & Drop Lab",
    page_icon="🖐️",
    layout="wide"
)

# -----------------------------------------------------------------------------
# 2. Custom CSS (실습실 분위기 연출)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_two@1.0/NanumSquareRound.woff');
    
    * {
        font-family: 'NanumSquareRound', sans-serif !important;
    }

    .stApp {
        background-color: #E6F4F9;
        color: #1E293B;
    }
    
    h1 {
        color: #0F172A !important;
        font-weight: 800;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. 타이틀 및 데이터 수신
# -----------------------------------------------------------------------------
st.title("🖐️ 인터랙티브 드래그 앤 드롭 유전자 가위 실습")
st.markdown("🧬 1페이지에서 선별된 gRNA를 가지고, **마우스로 도구를 직접 드래그하여** 유전자 편집 과정을 직접 체험해봐요!")
st.markdown("---")

top_cand = st.session_state.get("selected_top_grna", None)

if top_cand is None:
    st.warning("⚠️ 연동된 gRNA 데이터가 없습니다. 1페이지(스크리닝 도구)로 돌아가서 후보를 선별하고 '게임 시작' 버튼을 눌러주세요!")
    st.info("👈 사이드바 메뉴에서 메인 스크리닝 페이지로 이동하실 수 있습니다.")
else:
    seq = top_cand['Sequence']
    
    st.markdown(f"""
    <div style="background-color: #D1FAE5; border: 3px solid #059669; border-radius: 16px; padding: 15px; margin-bottom: 20px; text-align: center;">
        <h3 style="margin: 0; color: #065F46;">🔬 실습 대상: {top_cand['후보명']} ({seq})</h3>
        <p style="margin: 5px 0 0 0; color: #047857; font-weight: bold;">안전성: {top_cand['안전성 (MIT)']}점 | 효율성: {top_cand['효율성 (Doench)']}점</p>
    </div>
    """, unsafe_allow_html=True)

    # -----------------------------------------------------------------------------
    # HTML5 Drag and Drop 컴포넌트 삽입
    # -----------------------------------------------------------------------------
    drag_drop_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{
            font-family: 'NanumSquareRound', sans-serif;
            background-color: #E6F4F9;
            margin: 0;
            padding: 10px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .lab-bench {{
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
        .instruction {{
            font-size: 1.25rem;
            font-weight: 800;
            color: #1E3A8A;
            margin-bottom: 20px;
            background: #EFF6FF;
            padding: 10px 20px;
            border-radius: 15px;
            border: 2px solid #BFDBFE;
        }}
        .dna-box {{
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
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        }}
        .draggable-tool {{
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
            transition: transform 0.1s ease;
        }}
        .draggable-tool:active {{
            cursor: grabbing;
            transform: scale(1.05);
        }}
        #grna-tool {{
            top: 40px;
            left: 40px;
            background-color: #FB923C;
            color: white;
            border: 3px solid #EA580C;
        }}
        #cas9-tool {{
            top: 40px;
            right: 40px;
            background-color: #64748B;
            color: white;
            border: 3px solid #475569;
            display: none;
        }}
        .success-banner {{
            margin-top: 20px;
            font-size: 1.3rem;
            font-weight: 800;
            color: #059669;
            display: none;
        }}
    </style>
    </head>
    <body>

    <div class="instruction" id="instruction-text">🎯 1단계: 주황색 [🧬 gRNA] 박스를 마우스로 잡아 중앙의 DNA 위에 올려놓으세요!</div>

    <div class="lab-bench" id="workbench" ondragover="allowDrop(event)" ondrop="drop(event)">
        <!-- 드래그할 도구들 -->
        <div class="draggable-tool" id="grna-tool" draggable="true" ondragstart="drag(event)">🧬 gRNA</div>
        <div class="draggable-tool" id="cas9-tool" draggable="true" ondragstart="drag(event)">✂️ Cas9 가위</div>

        <!-- 중앙 DNA 표적 -->
        <div class="dna-box" id="dna-target">
            5'- {seq} -3'
        </div>
    </div>

    <div class="success-banner" id="success-msg">🎉 대성공! 유전자 가위 실습을 완벽하게 마쳤습니다!</div>

    <script>
        const targetSeq = "{seq}";

        function allowDrop(ev) {
            ev.preventDefault();
        }

        function drag(ev) {
            ev.dataTransfer.setData("text", ev.target.id);
        }

        function drop(ev) {
            ev.preventDefault();
            var data = ev.dataTransfer.getData("text");
            let instruction = document.getElementById("instruction-text");
            let dnaBox = document.getElementById("dna-target");
            let grnaTool = document.getElementById("grna-tool");
            let cas9Tool = document.getElementById("cas9-tool");
            let successMsg = document.getElementById("success-msg");

            if (data === "grna-tool" && grnaTool.style.display !== "none") {
                // gRNA 결합 완료
                grnaTool.style.display = "none";
                dnaBox.innerHTML = "5'- <span style='color:#EA580C;'>" + targetSeq + "</span> -3'<br><span style='font-size:0.95rem; color:#059669;'>✨ [gRNA 가이드 결합 성공!]</span>";
                dnaBox.style.borderColor = "#FB923C";
                
                instruction.innerHTML = "✂️ 2단계 완료! 이제 나타난 [회색 Cas9 가위]를 드래그해서 DNA 중앙으로 가져가세요!";
                cas9Tool.style.display = "flex";

            } else if (data === "cas9-tool" && cas9Tool.style.display !== "none") {
                // Cas9 절단 완료
                cas9Tool.style.display = "none";
                let half = Math.floor(targetSeq.length / 2);
                let p1 = targetSeq.substring(0, half);
                let p2 = targetSeq.substring(half);

                dnaBox.innerHTML = "5'- " + p1 + " <span style='color:red; font-size:1.8rem;'>⚡</span> " + p2 + " -3'<br><span style='font-size:0.95rem; color:red;'>✂️ [DNA 이중나선 절단(DSB) 완료!]</span>";
                dnaBox.style.borderColor = "#DC2626";
                
                instruction.innerHTML = "🏆 유전자 편집 실습 완벽 성공!";
                success.style.display = "block";
            }
        }
    </script>

    </body>
    </html>
    """

    components.html(drag_drop_html, height=520)
