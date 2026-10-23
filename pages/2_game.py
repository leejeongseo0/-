import streamlit as st
import streamlit.components.v1 as components

# 1. 페이지 설정
st.set_page_config(
    page_title="CRISPR Bio Lab Game",
    page_icon="🧬",
    layout="wide"
)

# 2. 스타일 설정
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_two@1.0/NanumSquareRound.woff');
    * { font-family: 'NanumSquareRound', sans-serif !important; }
    .stApp { background-color: #0F172A; color: #F8FAFC; }
    h1 { color: #38BDF8 !important; font-weight: 800; text-shadow: 0 2px 4px rgba(0,0,0,0.3); }
</style>
""", unsafe_allow_html=True)

# 3. 타이틀 및 데이터 수신
st.title("🎮 CRISPR 바이오 시뮬레이션 게임: 유전자 편집 실습")
st.markdown("✨ 1페이지에서 선별된 gRNA 데이터를 바탕으로, **실제 게임 그래픽 환경에서 가이드 RNA와 Cas9 가위를 직접 조작**하여 유전자 치료 미션을 완수하세요!")
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
    <div style="background: linear-gradient(135deg, #1E293B, #334155); border: 2px solid #38BDF8; border-radius: 20px; padding: 16px 24px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 8px 20px rgba(56, 189, 248, 0.15);">
        <div>
            <h3 style="margin: 0; color: #38BDF8; font-size: 1.2rem;">🔬 활성화된 미션 타겟: {cand_name}</h3>
            <p style="margin: 4px 0 0 0; color: #94A3B8; font-family: monospace; font-size: 1.05rem;">Target Sequence: {seq}</p>
        </div>
        <div style="text-align: right;">
            <span style="background: #0284C7; color: white; padding: 6px 14px; border-radius: 12px; font-weight: bold; font-size: 0.9rem;">MIT 안전성: {mit_score}점</span>
            <span style="background: #0D9488; color: white; padding: 6px 14px; border-radius: 12px; font-weight: bold; font-size: 0.9rem; margin-left: 8px;">Doench 효율: {doench_score}점</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 4. 문법 오류 방지를 위해 완전히 분리된 HTML/JS 게임 엔진
    game_html = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
        body {
            background-color: #0F172A;
            color: #F8FAFC;
            font-family: 'NanumSquareRound', sans-serif;
            margin: 0;
            padding: 10px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .game-container {
            width: 100%;
            max-width: 950px;
            background: #1E293B;
            border: 3px solid #334155;
            border-radius: 24px;
            padding: 24px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.4);
        }
        .quest-box {
            background: #0F172A;
            border-left: 6px solid #38BDF8;
            padding: 12px 18px;
            border-radius: 12px;
            font-size: 1.15rem;
            font-weight: bold;
            color: #E2E8F0;
            margin-bottom: 20px;
        }
        .lab-bench {
            background: #090D16;
            border: 3px dashed #475569;
            border-radius: 20px;
            height: 380px;
            position: relative;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }
        .game-item {
            position: absolute;
            cursor: grab;
            user-select: none;
            display: flex;
            flex-direction: column;
            align-items: center;
            z-index: 10;
        }
        .game-item:active {
            cursor: grabbing;
            transform: scale(1.1);
        }
        #grna-item { top: 30px; left: 40px; }
        #cas9-item { top: 30px; right: 40px; display: none; }
        
        .item-card {
            background: rgba(30, 41, 59, 0.95);
            border: 2px solid #64748B;
            border-radius: 16px;
            padding: 10px 16px;
            text-align: center;
            box-shadow: 0 8px 20px rgba(0,0,0,0.5);
        }
        .item-card svg {
            width: 50px;
            height: 50px;
            margin-bottom: 4px;
        }
        .item-name {
            font-size: 0.95rem;
            font-weight: bold;
        }

        .dna-core {
            background: rgba(15, 23, 42, 0.9);
            border: 3px solid #3B82F6;
            border-radius: 16px;
            padding: 20px 35px;
            text-align: center;
            z-index: 2;
        }
        .dna-seq-text {
            font-family: monospace;
            font-size: 1.35rem;
            font-weight: bold;
            letter-spacing: 3px;
            color: #93C5FD;
            margin-top: 6px;
        }
        .success-panel {
            margin-top: 20px;
            background: #064E3B;
            border: 2px solid #059669;
            padding: 15px;
            border-radius: 16px;
            text-align: center;
            font-size: 1.2rem;
            font-weight: bold;
            color: #6EE7B7;
            display: none;
        }
    </style>
    </head>
    <body>

    <div class="game-container">
        <div class="quest-box" id="quest-text">
            🎯 [미션 1] 주황색 라인의 <span style="color:#FB923C;">[🧬 가이드 RNA (gRNA)]</span>를 마우스로 잡고 중앙의 DNA 타겟 위로 드래그하여 결합시키세요!
        </div>

        <div class="lab-bench" ondragover="event.preventDefault()" ondrop="dropToBench(event)">
            
            <div class="game-item" id="grna-item" draggable="true" ondragstart="event.dataTransfer.setData('text', 'grna')">
                <div class="item-card" style="border-color: #FB923C;">
                    <svg viewBox="0 0 24 24" fill="none" stroke="#FB923C" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M2 12h4l3-9 4 18 3-9h6"></path>
                    </svg>
                    <div class="item-name" style="color: #FB923C;">gRNA (가이드)</div>
                </div>
            </div>

            <div class="game-item" id="cas9-item" draggable="true" ondragstart="event.dataTransfer.setData('text', 'cas9')">
                <div class="item-card" style="border-color: #10B981;">
                    <svg viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="6" cy="6" r="3"></circle><circle cx="6" cy="18" r="3"></circle>
                        <line x1="20" y1="4" x2="8.12" y2="15.88"></line>
                        <line x1="14.47" y1="14.48" x2="20" y2="20"></line>
                        <line x1="8.12" y1="8.12" x2="12" y2="12"></line>
                    </svg>
                    <div class="item-name" style="color: #10B981;">Cas9 가위</div>
                </div>
            </div>

            <div class="dna-core" id="dna-zone">
                <div style="font-size: 0.9rem; color: #60A5FA; font-weight: bold;">🧬 TARGET DNA DOUBLE STRAND</div>
                <div class="dna-seq-text" id="dna-text">5'- TARGET_SEQ_PLACEHOLDER -3'</div>
            </div>

        </div>

        <div class="success-panel" id="success-box">
            🎉 축하합니다! 주니어 수석 생명공학자 미션 클리어! 환자의 유전자가 완벽하게 교정되었습니다!
        </div>
    </div>

    <script>
        const targetSeq = "TARGET_SEQ_PLACEHOLDER";

        function dropToBench(ev) {
            ev.preventDefault();
            let actionType = ev.dataTransfer.getData("text");
            let questEl = document.getElementById("quest-text");
            let dnaZone = document.getElementById("dna-zone");
            let dnaText = document.getElementById("dna-text");
            let grnaItem = document.getElementById("grna-item");
            let cas9Item = document.getElementById("cas9-item");
            let successBox = document.getElementById("success-box");

            if (actionType === "grna" && grnaItem.style.display !== "none") {
                grnaItem.style.display = "none";
                dnaZone.style.borderColor = "#F59E0B";
                dnaText.innerHTML = "5'- <span style='color:#F59E0B;'>" + targetSeq + "</span> -3'<br><span style='font-size:0.85rem; color:#34D399;'>✨ [gRNA가 상보적 서열을 정확히 탐색 및 타겟팅 완료!]</span>";
                
                questEl.innerHTML = "🎯 [미션 2] 타겟팅 완료! 이제 활성화된 초록색 <span style='color:#10B981;'>[✂️ Cas9 가위 복합체]</span>를 마우스로 잡아 중앙의 타겟 위에 드래그하여 절단(Cutting)을 실행하세요!";
                cas9Item.style.display = "flex";

            } else if (actionType === "cas9" && cas9Item.style.display !== "none") {
                cas9Item.style.display = "none";
                dnaZone.style.borderColor = "#EF4444";
                
                let mid = Math.floor(targetSeq.length / 2);
                let sub1 = targetSeq.substring(0, mid);
                let sub2 = targetSeq.substring(mid);

                dnaText.innerHTML = "5'- " + sub1 + " <span style='color:#EF4444; font-size:1.6rem;'>⚡✂️</span> " + sub2 + " -3'<br><span style='font-size:0.85rem; color:#F87171;'>⚡ [Double-Strand Break (DSB) 이중나선 절단 성공!]</span>";
                
                questEl.innerHTML = "🏆 모든 유전자 편집 임상 프로토콜 실습 과정이 성공적으로 끝났습니다!";
                successBox.style.display = "block";
            }
        }
    </script>
    </body>
    </html>
    """

    # 파이썬 변수를 안전하게 HTML 내부로 주입
    final_game_html = game_html.replace("TARGET_SEQ_PLACEHOLDER", seq)
    components.html(final_game_html, height=540)
