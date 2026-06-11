import os
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
import json
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)
load_dotenv(".env.local", override=True)

# Attempt imports with fallback grace
try:
    import tiktoken
except ImportError:
    tiktoken = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    import anthropic
except ImportError:
    anthropic = None

# ==========================================
# 1. DESIGN SYSTEM & CUSTOM CSS (Premium UI)
# ==========================================
st.set_page_config(
    page_title="✨ DayPlanner: 하루의 발견",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Pretendard:wght@300;400;600;800&display=swap');

    /* Warm, Emotional & Premium animated gradient background */
    .stApp {
        background: radial-gradient(circle at 90% 10%, rgba(255, 126, 95, 0.12), transparent 45%),
                    radial-gradient(circle at 10% 90%, rgba(122, 220, 180, 0.1), transparent 45%),
                    radial-gradient(circle at 50% 50%, rgba(248, 246, 242, 0.5), transparent 60%);
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
    }
    
    /* Premium Title Header with elegant multi-color gradient */
    .main-header {
        background: linear-gradient(135deg, #ff6b6b, #ff8e53, #7209b7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Outfit', 'Pretendard', sans-serif;
        font-weight: 800;
        font-size: 3.4rem;
        margin-bottom: 0.3rem;
        text-align: center;
        letter-spacing: -0.05em;
        filter: drop-shadow(0px 2px 10px rgba(255,107,107,0.1));
    }
    
    .sub-header {
        font-size: 1.15rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 2.2rem;
        font-weight: 500;
        letter-spacing: -0.03em;
        font-family: 'Pretendard', sans-serif;
    }

    /* Enhancing chat bubbles to feel premium and warm */
    [data-testid="stChatMessage"] {
        border-radius: 20px !important;
        padding: 16px 20px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
        margin-bottom: 14px !important;
        display: flex !important;
        width: fit-content !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    [data-testid="stChatMessage"]:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 24px rgba(0, 0, 0, 0.05);
    }

    /* User message styling: vibrant premium sunset gradient, aligned right */
    [data-testid="stChatMessage"][data-testid="stChatMessage-user"] {
        background: linear-gradient(135deg, #ff7b00, #ff007b) !important; /* Premium sunset gradient */
        border: none !important;
        color: white !important;
        margin-left: auto !important;
        max-width: 75% !important;
        border-radius: 20px 20px 4px 20px !important;
        box-shadow: 0 4px 15px rgba(255, 0, 123, 0.15) !important;
    }
    
    /* Hide user chat avatar to match messenger style DMs */
    [data-testid="stChatMessage-user"] [data-testid="stChatMessageAvatar"],
    [data-testid="stChatMessage-user"] [data-testid="chat-message-avatar"],
    [data-testid="stChatMessage-user"] > div:first-child {
        display: none !important;
    }
    
    /* Force user message text elements to be white */
    [data-testid="stChatMessage"][data-testid="stChatMessage-user"] p,
    [data-testid="stChatMessage"][data-testid="stChatMessage-user"] span,
    [data-testid="stChatMessage"][data-testid="stChatMessage-user"] div,
    [data-testid="stChatMessage"][data-testid="stChatMessage-user"] label,
    [data-testid="stChatMessage"][data-testid="stChatMessage-user"] h1,
    [data-testid="stChatMessage"][data-testid="stChatMessage-user"] h2,
    [data-testid="stChatMessage"][data-testid="stChatMessage-user"] h3 {
        color: #ffffff !important;
    }

    /* Assistant message styling: frosted glassmorphism, aligned left */
    [data-testid="stChatMessage"][data-testid="stChatMessage-assistant"] {
        background: rgba(255, 255, 255, 0.85) !important;
        border: 1px solid rgba(255, 255, 255, 0.6) !important;
        backdrop-filter: blur(12px) !important;
        color: #1e293b !important;
        margin-right: auto !important;
        max-width: 85% !important;
        border-radius: 20px 20px 20px 4px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.02) !important;
    }
    
    /* Center the app layout with a max-width */
    .block-container {
        max-width: 920px !important;
        padding-top: 2.5rem !important;
        padding-bottom: 7rem !important;
        margin: 0 auto !important;
    }
    
    /* Style the unified chat container box: frosted glass */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255, 255, 255, 0.45) !important;
        border: 1px solid rgba(255, 255, 255, 0.5) !important;
        border-radius: 28px !important;
        padding: 24px !important;
        box-shadow: 0 15px 35px rgba(31, 38, 135, 0.04) !important;
        backdrop-filter: blur(16px) !important;
        margin-top: 15px !important;
    }
    
    /* Sidebar text input borders */
    .stTextInput>div>div>input {
        border-radius: 12px !important;
        border: 1px solid rgba(0, 0, 0, 0.08) !important;
        padding: 10px 14px !important;
        transition: all 0.2s ease !important;
    }
    .stTextInput>div>div>input:focus {
        border-color: #ff007b !important;
        box-shadow: 0 0 0 3px rgba(255, 0, 123, 0.1) !important;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: rgba(255, 255, 255, 0.6) !important;
        border: 1px solid rgba(0, 0, 0, 0.05) !important;
        border-radius: 14px !important;
        padding: 12px !important;
        font-weight: 600 !important;
        backdrop-filter: blur(8px) !important;
        transition: all 0.2s ease !important;
    }
    .streamlit-expanderHeader:hover {
        background-color: rgba(255, 255, 255, 0.9) !important;
        border-color: rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Redefining buttons to match premium aesthetics */
    .stButton > button {
        border-radius: 16px !important;
        border: 1px solid rgba(0, 0, 0, 0.06) !important;
        background: linear-gradient(135deg, #ffffff, #f8fafc) !important;
        color: #334155 !important;
        padding: 12px 20px !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.02) !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        height: auto !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 20px rgba(255, 0, 123, 0.12) !important;
        border-color: #ff007b !important;
        color: #ff007b !important;
        background: #ffffff !important;
    }
    
    /* Chat input styling */
    .stChatInputContainer {
        border-radius: 24px !important;
        border: 1px solid rgba(0, 0, 0, 0.08) !important;
        background: rgba(255, 255, 255, 0.95) !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.05) !important;
        backdrop-filter: blur(10px) !important;
        transition: all 0.2s ease !important;
    }
    .stChatInputContainer:focus-within {
        border-color: #ff007b !important;
        box-shadow: 0 8px 32px rgba(255, 0, 123, 0.1) !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SESSION STATE INITIALIZATION
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "☕ 안녕! 난 **하루(Haru)**야. 너 이름은 뭐야? \n\n(혹시 궁금하거나 가고 싶은 곳의 사진이 있다면 아래 🖼️ 버튼을 눌러 나에게 보여줘! 바로 찾아줄게! 📸)"
        }
    ]
if "token_usage" not in st.session_state:
    st.session_state.token_usage = {"input_tokens": 0, "output_tokens": 0, "total_cost": 0.0}
if "last_audio_hash" not in st.session_state:
    st.session_state.last_audio_hash = None
if "starter_prompt" not in st.session_state:
    st.session_state.starter_prompt = None
if "generate_response" not in st.session_state:
    st.session_state.generate_response = False
if "current_prompt" not in st.session_state:
    st.session_state.current_prompt = None

def is_placeholder(key):
    if not key:
        return True
    k_lower = key.lower()
    return "your_" in k_lower or "api_key_here" in k_lower or "placeholder" in k_lower

def get_secret_safe(key, default=""):
    try:
        val = st.secrets.get(key, default)
        return default if is_placeholder(val) else val
    except Exception:
        return default

openai_api_key_env = os.getenv("OPENAI_API_KEY")
if is_placeholder(openai_api_key_env):
    openai_api_key_env = ""
if not openai_api_key_env:
    openai_api_key_env = get_secret_safe("OPENAI_API_KEY", "")

anthropic_api_key_env = os.getenv("ANTHROPIC_API_KEY")
if is_placeholder(anthropic_api_key_env):
    anthropic_api_key_env = ""
if not anthropic_api_key_env:
    anthropic_api_key_env = get_secret_safe("ANTHROPIC_API_KEY", "")

gemini_api_key_env = os.getenv("GEMINI_API_KEY")
if is_placeholder(gemini_api_key_env):
    gemini_api_key_env = ""
if not gemini_api_key_env:
    gemini_api_key_env = get_secret_safe("GEMINI_API_KEY", "")

# ==========================================
# 3. HEADER & SETTINGS LAYOUT (Top right placement)
# ==========================================
header_col, settings_col = st.columns([3, 1.2])

with header_col:
    st.markdown('<div class="main-header" style="text-align: left; font-size: 2.4rem; margin-top: 0.5rem; margin-bottom: 0.2rem;">✨ DayPlanner: 하루의 발견</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header" style="text-align: left; font-size: 1.05rem; margin-bottom: 1.5rem;">당신의 하루를 만들어 보세요.</div>', unsafe_allow_html=True)

with settings_col:
    st.markdown('<div style="margin-top: 0.8rem;"></div>', unsafe_allow_html=True)  # Spacer
    settings_expander = st.expander("⚙️ 설정 및 모델 선택", expanded=False)

with settings_expander:
    # Provider and Model selection
    provider = st.selectbox(
        "대화형 AI 프로바이더",
        ["OpenAI", "Anthropic", "Google Gemini", "Ollama (Local)"]
    )

    if provider == "OpenAI":
        model = st.selectbox("모델 선택", ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"], index=0)
        api_key_placeholder = "OPENAI_API_KEY"
        api_key_val = openai_api_key_env
    elif provider == "Anthropic":
        model = st.selectbox("모델 선택", ["claude-3-5-sonnet-latest", "claude-3-opus-latest", "claude-3-haiku-20240307"])
        api_key_placeholder = "ANTHROPIC_API_KEY"
        api_key_val = anthropic_api_key_env
    elif provider == "Google Gemini":
        model = st.selectbox("모델 선택", ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-1.5-flash", "gemini-1.5-pro"])
        api_key_placeholder = "GEMINI_API_KEY"
        api_key_val = gemini_api_key_env
    else:  # Ollama (Local)
        model = st.text_input("로컬 모델명", value="llama3")
        api_key_placeholder = "N/A"
        api_key_val = "ollama"

    # Hyperparameters
    st.markdown("### 🎛️ 하이퍼파라미터")
    temperature = st.slider("온도 (Temperature)", 0.0, 2.0, 0.7, 0.1)
    max_tokens = st.slider("최대 토큰 (Max Tokens)", 50, 4000, 2048, 50)

    # API Keys Setting Expander
    with st.expander("🔑 API 키 설정 (API Keys)", expanded=False):
        # OpenAI
        if openai_api_key_env:
            st.caption("🟢 OpenAI API Key가 환경 변수에서 감지되었습니다 (보호됨).")
            override_openai = st.checkbox("OpenAI 키 수동 입력/덮어쓰기", value=False, key="ov_openai")
            if override_openai:
                openai_key_input = st.text_input("OpenAI API Key 입력", type="password", key="key_openai")
            else:
                openai_key_input = openai_api_key_env
        else:
            openai_key_input = st.text_input("OpenAI API Key 입력", type="password", key="key_openai")
            
        # Anthropic
        if anthropic_api_key_env:
            st.caption("🟢 Anthropic API Key가 환경 변수에서 감지되었습니다 (보호됨).")
            override_anthropic = st.checkbox("Anthropic 키 수동 입력/덮어쓰기", value=False, key="ov_anthropic")
            if override_anthropic:
                anthropic_key_input = st.text_input("Anthropic API Key 입력", type="password", key="key_anthropic")
            else:
                anthropic_key_input = anthropic_api_key_env
        else:
            anthropic_key_input = st.text_input("Anthropic API Key 입력", type="password", key="key_anthropic")
            
        # Gemini
        if gemini_api_key_env:
            st.caption("🟢 Gemini API Key가 환경 변수에서 감지되었습니다 (보호됨).")
            override_gemini = st.checkbox("Gemini 키 수동 입력/덮어쓰기", value=False, key="ov_gemini")
            if override_gemini:
                gemini_key_input = st.text_input("Gemini API Key 입력", type="password", key="key_gemini")
            else:
                gemini_key_input = gemini_api_key_env
        else:
            gemini_key_input = st.text_input("Gemini API Key 입력", type="password", key="key_gemini")

        ollama_url_input = st.text_input("Ollama Base URL", value="http://localhost:11434")

    # Set active API Key
    if provider == "OpenAI":
        api_key = openai_key_input
    elif provider == "Anthropic":
        api_key = anthropic_key_input
    elif provider == "Google Gemini":
        api_key = gemini_key_input
    else:
        api_key = "ollama"

    # Custom lifestyle guide system prompt
    system_prompt_base = st.text_area(
        "🎭 시스템 프롬프트 (페르소나)",
        value="""너는 사용자의 소중한 하루를 완벽하게 가이드해 주는 라이프스타일 및 문화생활 큐레이터 '하루(Haru)'야.
사용자와 반말(혹은 매우 친근하고 편한 말투)로 대화해줘.

[대화 전개 방식 및 질문 규칙 - 중요]
1. 사용자의 정보를 **한 번에 한 가지씩만** 물어봐야 해. 절대 여러 질문을 한 번에 다 던지지 마.
2. 대화 기록을 파악하여 아직 수집되지 않은 정보를 순서대로 하나씩 유도해줘:
   - 사용자가 이름을 말하면: 이름을 부르며 반갑게 인사하고, "지금 어디에 있어?"(위치)를 물어본다.
   - 위치를 답하면: "오늘 누구랑 같이 있어?"(동행인)를 물어본다.
   - 동행인을 답하면: "얼마나 시간 있어? (여유 시간)"을 물어본다.
   - 시간을 답하면: "오늘 특별히 하고 싶은 활동이 있어?"(하고 싶은 활동)를 물어본다.
   - 활동을 답하면: "어떤 분위기나 감성을 좋아해?"(선호 분위기/취향)를 물어본다.
3. 사용자가 장소 사진을 업로드한 경우, 질문 흐름과 상관없이 즉시 해당 사진 속 장소를 알려주거나 분석하고 찾아주면서 코스를 추천해줘.
4. 사용자가 굳이 모든 질문에 대답하지 않고 바로 추천을 원하거나, 5가지 정보가 모두 모이면 최종 코스 설계를 진행해줘.
5. **[매우 중요] 답변할 때는 가독성을 위해 반드시 한 문장이 끝날 때마다 줄바꿈(줄나눔)을 두 번(\n\n) 또는 한 번(\n) 해줘. 즉, 메신저 대화처럼 한 문장에 한 줄씩 나오도록 글을 작성해줘. 절대 긴 설명문단으로 뭉쳐서 한 번에 출력하지 마.**

[답변 가이드라인 (최종 코스 추천 시)]
1. 수집된 정보를 바탕으로 조건에 딱 맞는 힙하고 감각적인 하루 코스(카페, 식당, 소품샵, 팝업스토어, 미술관 전시 등)를 제안해줘.
2. 제안할 때는 시간대별 코스(오전 -> 점심식사 -> 오후 카페 -> 문화활동 -> 저녁)를 테이블이나 타임라인 형태로 시각적으로 구조화해줘.
3. 각 추천 장소의 '선정이유', '시그니처 메뉴/체험', '힙한 포토존 꿀팁'을 반드시 포함해서 설레게 만들어줘.
4. 예산이나 위치적인 동선을 세심하게 배려해 낭비 없는 최적의 경로를 그려줘.
5. 사용자가 가고 싶은 곳이나 궁금한 장소 사진(이미지)을 업로드한 경우, 그 사진 속 장소가 어디인지(이름, 상세 주소나 대략적인 위치) 네가 가진 지식을 활용해 분석하고 식별해서 가장 먼저 알려줘. 만약 정확한 장소를 알기 힘들다면 사진의 특징(건물 스타일, 내부 인테리어, 주변 풍경 등)을 바탕으로 유추해 알려주고, 이와 비슷한 분위기의 장소를 제안해줘. 그 후 그 장소나 지역을 중심으로 근처에서 보낼 수 있는 멋진 당일 코스를 연계해 추천해줘.""",
        height=240
    )

    # ==========================================
    # 5. RAG (DOCUMENT PARSING)
    # ==========================================
    st.markdown("### 📂 RAG: 문서 기반 분석")
    uploaded_files = st.file_uploader(
        "나만의 핫플레이스 목록/문서 업로드 (PDF, TXT, MD, CSV)",
        type=["pdf", "txt", "md", "csv"],
        accept_multiple_files=True
    )

    doc_context_str = ""
    if uploaded_files:
        doc_contents = []
        for f in uploaded_files:
            name = f.name
            content = ""
            try:
                if name.endswith(".pdf"):
                    import pypdf
                    reader = pypdf.PdfReader(f)
                    text_list = [p.extract_text() for p in reader.pages if p.extract_text()]
                    content = "\n".join(text_list)
                elif name.endswith(".csv"):
                    content = f.getvalue().decode("utf-8", errors="ignore")
                else:  # txt, md
                    content = f.getvalue().decode("utf-8", errors="ignore")
                
                # Truncate each file to 25,000 characters to prevent context window overflow
                content = content[:25000]
                doc_contents.append(f"파일명: {name}\n내용:\n{content}\n")
            except Exception as e:
                st.error(f"{name} 읽기 에러: {e}")
        
        if doc_contents:
            doc_context_str = "\n\n=== [참고 문서 컨텍스트] ===\n" + "\n---\n".join(doc_contents)
            st.success(f"{len(uploaded_files)}개 문서 로드 완료!")

    use_rag = st.checkbox("문서 분석 내용 대화에 반영하기", value=True) if uploaded_files else False

    # Merge system prompt with RAG context
    if use_rag and doc_context_str:
        system_prompt = system_prompt_base + doc_context_str + "\n\n위의 참고 문서 내용을 정확히 인지하고, 사용자의 질문에 답변할 때 최대한 이 정보를 바탕으로 설명해주세요."
    else:
        system_prompt = system_prompt_base

    # ==========================================
    # 6. COST & TOKEN ESTIMATORS
    # ==========================================
    # Metrics
    st.markdown("### 📊 실시간 사용량 리포트")
    cost_col1, cost_col2 = st.columns(2)
    with cost_col1:
        st.metric("소모 토큰", f"{st.session_state.token_usage['input_tokens'] + st.session_state.token_usage['output_tokens']:,}")
    with cost_col2:
        st.metric("누적 예상 비용", f"${st.session_state.token_usage['total_cost']:.5f}")

    # ==========================================
    # 7. HISTORY MANAGEMENT (Export/Import/Reset)
    # ==========================================
    st.markdown("### 💾 대화 관리")

    # Export
    chat_history_json = json.dumps(st.session_state.messages, ensure_ascii=False, indent=2)
    st.download_button(
        label="📥 대화 내역 저장 (JSON)",
        data=chat_history_json,
        file_name="chat_history.json",
        mime="application/json",
        use_container_width=True
    )

    # Import
    uploaded_history = st.file_uploader("📤 대화 내역 가져오기 (JSON)", type=["json"], label_visibility="collapsed")
    if uploaded_history is not None:
        try:
            loaded_msgs = json.loads(uploaded_history.getvalue().decode("utf-8"))
            if isinstance(loaded_msgs, list) and all("role" in m and "content" in m for m in loaded_msgs):
                st.session_state.messages = loaded_msgs
                st.success("대화 내역을 불러왔습니다!")
                st.rerun()
            else:
                st.error("잘못된 JSON 포맷입니다.")
        except Exception as e:
            st.error(f"가져오기 에러: {e}")

    # Clear Chat
    if st.button("🧹 대화 전체 초기화", use_container_width=True):
        st.session_state.messages = []
        st.session_state.token_usage = {"input_tokens": 0, "output_tokens": 0, "total_cost": 0.0}
        st.success("대화가 초기화되었습니다.")
        st.rerun()

# ==========================================
# 8. STREAMING CHAT COMPLETIONS FUNCTION
# ==========================================
def update_usage_metrics(prompt_text, response_text, model_name):
    # Determine the number of input tokens
    input_tokens = 0
    
    # Extract text from prompt
    text_content = ""
    image_count = 0
    if isinstance(prompt_text, list):
        for part in prompt_text:
            if part.get("type") == "text":
                text_content += part.get("text", "")
            elif part.get("type") == "image":
                image_count += 1
    else:
        text_content = str(prompt_text)
        
    # Count input tokens
    if tiktoken and ("gpt" in model_name or "text-davinci" in model_name):
        try:
            encoding = tiktoken.encoding_for_model(model_name)
            input_tokens = len(encoding.encode(text_content))
        except Exception:
            input_tokens = len(text_content) // 2
    else:
        # Simple fallback estimate: 1 token per 2 characters on average
        input_tokens = len(text_content) // 2
        
    # Standard image token estimation (e.g. 258 tokens for GPT-4o detail=low)
    input_tokens += image_count * 258

    # Count output tokens
    output_tokens = 0
    if tiktoken and ("gpt" in model_name or "text-davinci" in model_name):
        try:
            encoding = tiktoken.encoding_for_model(model_name)
            output_tokens = len(encoding.encode(response_text))
        except Exception:
            output_tokens = len(response_text) // 2
    else:
        output_tokens = len(response_text) // 2

    # Calculate costs
    # Rates per 1M tokens: (input_rate, output_rate)
    rates = {
        "gpt-4o": (5.00, 15.00),
        "gpt-4o-mini": (0.15, 0.60),
        "gpt-4-turbo": (10.00, 30.00),
        "gpt-3.5-turbo": (0.50, 1.50),
        "claude-3-5-sonnet-latest": (3.00, 15.00),
        "claude-3-opus-latest": (15.00, 75.00),
        "claude-3-haiku-20240307": (0.25, 1.25),
        "gemini-2.5-flash": (0.075, 0.30),
        "gemini-2.5-pro": (1.25, 5.00),
        "gemini-1.5-flash": (0.075, 0.30),
        "gemini-1.5-pro": (1.25, 5.00),
    }

    # Fallback/wildcard matching for rates
    input_rate, output_rate = 0.0, 0.0
    for key, val in rates.items():
        if key in model_name.lower():
            input_rate, output_rate = val
            break

    cost = ((input_tokens * input_rate) + (output_tokens * output_rate)) / 1_000_000.0

    # Save to session state
    st.session_state.token_usage["input_tokens"] += input_tokens
    st.session_state.token_usage["output_tokens"] += output_tokens
    st.session_state.token_usage["total_cost"] += cost

def format_sentences_with_newlines(text):
    if not isinstance(text, str):
        return text
    
    # If the text has markdown tables or code blocks or lists, splitting could corrupt them.
    # So we skip splitting if it looks like structured markdown.
    if "|" in text or "```" in text or "- " in text or "\n1. " in text or "\n- " in text:
        return text
        
    import re
    # Split sentences by punctuation (.!?), followed by space or end of string.
    # Keep the punctuation using regex lookbehind.
    sentences = re.split(r'(?<=[.!?])\s+', text)
    valid_sentences = [s.strip() for s in sentences if s.strip()]
    return "\n\n".join(valid_sentences)

def run_llm_stream(provider, model, messages, temperature, max_tokens, api_key, ollama_url):
    system_msg = ""
    regular_msgs = []
    for m in messages:
        if m["role"] == "system":
            system_msg = m["content"]
        else:
            regular_msgs.append(m)

    # ------------------
    # OpenAI Stream
    # ------------------
    if provider == "OpenAI":
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        # Translate to OpenAI content blocks if any message is multimodal
        openai_messages = []
        if system_msg:
            openai_messages.append({"role": "system", "content": system_msg})
            
        for m in regular_msgs:
            if isinstance(m["content"], list):
                content_blocks = []
                for part in m["content"]:
                    if part["type"] == "text":
                        content_blocks.append({"type": "text", "text": part["text"]})
                    elif part["type"] == "image":
                        content_blocks.append({
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{part.get('mime', 'image/jpeg')};base64,{part['data']}"
                            }
                        })
                openai_messages.append({"role": m["role"], "content": content_blocks})
            else:
                openai_messages.append({"role": m["role"], "content": m["content"]})
                
        stream = client.chat.completions.create(
            model=model,
            messages=openai_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    # ------------------
    # Anthropic Stream
    # ------------------
    elif provider == "Anthropic":
        if not anthropic:
            st.error("anthropic 라이브러리가 로드되지 않았습니다.")
            return
        client = anthropic.Anthropic(api_key=api_key)
        
        # Translate to Anthropic content blocks
        anth_msgs = []
        for m in regular_msgs:
            if isinstance(m["content"], list):
                content_blocks = []
                for part in m["content"]:
                    if part["type"] == "text":
                        content_blocks.append({"type": "text", "text": part["text"]})
                    elif part["type"] == "image":
                        content_blocks.append({
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": part.get("mime", "image/jpeg"),
                                "data": part["data"]
                            }
                        })
                anth_msgs.append({"role": m["role"], "content": content_blocks})
            else:
                anth_msgs.append({"role": m["role"], "content": m["content"]})
                
        with client.messages.stream(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_msg,
            messages=anth_msgs
        ) as stream:
            for text in stream.text_stream:
                yield text

    # ------------------
    # Gemini Stream
    # ------------------
    elif provider == "Google Gemini":
        if not genai:
            st.error("google-generativeai 라이브러리가 로드되지 않았습니다.")
            return
        genai.configure(api_key=api_key)
        
        # Translate to Gemini format
        import io
        import base64
        try:
            from PIL import Image
        except ImportError:
            Image = None
            
        gemini_msgs = []
        for m in regular_msgs:
            role = "user" if m["role"] == "user" else "model"
            parts = []
            
            if isinstance(m["content"], list):
                for part in m["content"]:
                    if part["type"] == "text":
                        parts.append(part["text"])
                    elif part["type"] == "image":
                        if Image:
                            img_data = base64.b64decode(part["data"])
                            img = Image.open(io.BytesIO(img_data))
                            parts.append(img)
                        else:
                            parts.append("[이미지 데이터 - PIL 라이브러리 미설치]")
            else:
                parts.append(m["content"])
                
            gemini_msgs.append({"role": role, "parts": parts})
        
        model_client = genai.GenerativeModel(
            model_name=model,
            generation_config={
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            },
            system_instruction=system_msg if system_msg else None
        )
        response = model_client.generate_content(gemini_msgs, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text

    # ------------------
    # Ollama Stream
    # ------------------
    elif provider == "Ollama (Local)":
        from openai import OpenAI
        client = OpenAI(api_key="ollama", base_url=f"{ollama_url}/v1")
        
        # Ollama compatible with OpenAI content blocks
        ollama_messages = []
        if system_msg:
            ollama_messages.append({"role": "system", "content": system_msg})
            
        for m in regular_msgs:
            if isinstance(m["content"], list):
                content_blocks = []
                for part in m["content"]:
                    if part["type"] == "text":
                        content_blocks.append({"type": "text", "text": part["text"]})
                    elif part["type"] == "image":
                        content_blocks.append({
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{part.get('mime', 'image/jpeg')};base64,{part['data']}"
                            }
                        })
                ollama_messages.append({"role": m["role"], "content": content_blocks})
            else:
                ollama_messages.append({"role": m["role"], "content": m["content"]})
                
        stream = client.chat.completions.create(
            model=model,
            messages=ollama_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content



# ==========================================
# 9. CONVERSATION VIEW & AUDIO OUTPUT
# ==========================================
st.markdown("### 💬 대화 피드")

# Create a unified container for the chat history
chat_box = st.container(border=True)

with chat_box:
    for idx, msg in enumerate(st.session_state.messages):
        avatar = "👤" if msg["role"] == "user" else "☕"
        with st.chat_message(msg["role"], avatar=avatar):
            if isinstance(msg["content"], list):
                # Multimodal content block
                text_content = ""
                image_data = None
                for part in msg["content"]:
                    if part["type"] == "text":
                        text_content = part["text"]
                    elif part["type"] == "image":
                        image_data = part["data"]
                
                if image_data:
                    # Decode base64 image and display it
                    import base64
                    try:
                        img_bytes = base64.b64decode(image_data)
                        st.image(img_bytes, width=280, caption="업로드된 이미지")
                    except Exception as e:
                        st.error(f"이미지 로딩 실패: {e}")
                if text_content:
                    st.markdown(format_sentences_with_newlines(text_content))
            else:
                # Text-only content
                st.markdown(format_sentences_with_newlines(msg["content"]))
            
            # Audio playback button for Assistant responses (TTS-1)
            if msg["role"] == "assistant" and provider == "OpenAI" and api_key:
                if st.button("🔊 음성 듣기 (TTS)", key=f"tts_{idx}"):
                    with st.spinner("음성 생성 중..."):
                        try:
                            from openai import OpenAI
                            tts_client = OpenAI(api_key=api_key)
                            speech_text = msg["content"]
                            if isinstance(speech_text, list):
                                speech_text = next((part["text"] for part in speech_text if part["type"] == "text"), "")
                                
                            speech = tts_client.audio.speech.create(
                                model="tts-1",
                                voice="alloy",
                                input=speech_text[:500]  # Limit to 500 characters
                            )
                            st.audio(speech.read(), format="audio/mp3", autoplay=True)
                        except Exception as e:
                            st.error(f"TTS 생성 에러: {e}")

# ==========================================
# 11. GENERATION RESPONSE & RERUN TRIGGER
# ==========================================
# If we have a pending generation flag set, we stream the response inside the container
if st.session_state.generate_response and st.session_state.current_prompt:
    prompt_text = st.session_state.current_prompt
    
    # Reset flags immediately to prevent loop
    st.session_state.current_prompt = None
    st.session_state.generate_response = False
    
    if provider in ["OpenAI", "Anthropic", "Google Gemini"] and not api_key:
        st.info(f"계속하려면 사이드바에서 {provider} API Key를 입력해주세요.", icon="🗝️")
    else:
        with chat_box:
            # Generate Assistant response bubble inside the same container
            with st.chat_message("assistant", avatar="☕"):
                response_placeholder = st.empty()
                full_response = ""
                
                try:
                    # Build context messages array (including system prompt)
                    messages_to_send = [{"role": "system", "content": system_prompt}]
                    for m in st.session_state.messages:
                        messages_to_send.append({"role": m["role"], "content": m["content"]})
                    
                    # Fetch stream generator
                    stream = run_llm_stream(
                        provider=provider,
                        model=model,
                        messages=messages_to_send,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        api_key=api_key,
                        ollama_url=ollama_url_input
                    )
                    
                    import time
                    for chunk in stream:
                        for char in chunk:
                            full_response += char
                            response_placeholder.markdown(format_sentences_with_newlines(full_response) + "▌")
                            time.sleep(0.02)
                        
                    response_placeholder.markdown(format_sentences_with_newlines(full_response))
                    
                    # Update Metrics
                    update_usage_metrics(
                        prompt_text=prompt_text,
                        response_text=full_response,
                        model_name=model
                    )
                    
                    # Save assistant response to history
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"답변 생성 오류: {e}")

# ==========================================
# 10. INPUT INTERFACE (Bottom chat-style input)
# ==========================================
user_prompt = None

# Initialize session state variables if not present
if "user_text_input" not in st.session_state:
    st.session_state.user_text_input = ""
if "pending_photo" not in st.session_state:
    st.session_state.pending_photo = None
if "pending_photo_mime" not in st.session_state:
    st.session_state.pending_photo_mime = None
if "temp_prompt" not in st.session_state:
    st.session_state.temp_prompt = None
if "file_uploader_id" not in st.session_state:
    st.session_state.file_uploader_id = 0

# Callbacks for submit
def on_btn_submit():
    val = st.session_state.get("text_input_key", "").strip()
    if val or st.session_state.get("pending_photo") is not None:
        st.session_state.temp_prompt = val

def on_text_submit():
    val = st.session_state.get("text_input_key", "").strip()
    if val:
        st.session_state.temp_prompt = val

st.markdown("---")
st.markdown("💬 **하루에게 질문하기**")

# Text bar layout with columns: text_input (5), photo_btn (0.8), voice_btn (0.8), submit_btn (1.2)
col1, col2, col3, col4 = st.columns([5, 0.8, 0.8, 1.2])
with col1:
    input_val = st.text_input(
        "메시지 입력",
        placeholder="원하는 기분, 장소, 동행인을 질문하거나 사진을 업로드해 보세요...",
        label_visibility="collapsed",
        key="text_input_key",
        on_change=on_text_submit
    )
with col2:
    photo_btn_label = "❌" if st.session_state.get("show_photo_uploader", False) else "🖼️"
    photo_clicked = st.button(photo_btn_label, use_container_width=True, help="사진 업로드 켜기/끄기")
with col3:
    voice_btn_label = "❌" if st.session_state.get("show_voice_recorder", False) else "🎙️"
    voice_clicked = st.button(voice_btn_label, use_container_width=True, help="음성 입력 켜기/끄기")
with col4:
    st.button("전송", use_container_width=True, on_click=on_btn_submit)

# Toggle photo uploader visibility
if photo_clicked:
    st.session_state.show_photo_uploader = not st.session_state.get("show_photo_uploader", False)
    st.session_state.show_voice_recorder = False
    st.rerun()

# Toggle voice recorder visibility
if voice_clicked:
    st.session_state.show_voice_recorder = not st.session_state.get("show_voice_recorder", False)
    st.session_state.show_photo_uploader = False
    st.rerun()

# Display photo uploader below the bar if enabled
if st.session_state.get("show_photo_uploader", False):
    st.markdown("🖼️ **장소 사진 올리기**")
    uploaded_photo = st.file_uploader(
        "여기에 이미지를 드래그하거나 클릭하여 업로드해 주세요 (PNG, JPG, JPEG)",
        type=["png", "jpg", "jpeg"],
        label_visibility="collapsed",
        key=f"photo_uploader_{st.session_state.file_uploader_id}"
    )
    if uploaded_photo:
        st.session_state.pending_photo = uploaded_photo.read()
        st.session_state.pending_photo_mime = uploaded_photo.type
        st.image(st.session_state.pending_photo, caption="업로드된 이미지 미리보기", width=250)
        if st.button("❌ 사진 삭제", key="clear_photo"):
            st.session_state.pending_photo = None
            st.session_state.pending_photo_mime = None
            st.session_state.file_uploader_id += 1
            st.rerun()

# Display voice recorder below the bar if enabled
if st.session_state.get("show_voice_recorder", False):
    st.markdown("🎙️ **음성 질문 녹음하기**")
    audio_value = st.audio_input("여기에 목소리를 녹음해 주세요", label_visibility="collapsed")
    if audio_value:
        audio_bytes = audio_value.read()
        audio_hash = hash(audio_bytes)
        if st.session_state.last_audio_hash != audio_hash:
            st.session_state.last_audio_hash = audio_hash
            if provider == "OpenAI" and api_key:
                with st.spinner("음성을 텍스트로 인식 중..."):
                    try:
                        from openai import OpenAI
                        stt_client = OpenAI(api_key=api_key)
                        transcription = stt_client.audio.transcriptions.create(
                            model="whisper-1",
                            file=("audio.wav", audio_bytes, "audio/wav")
                        )
                        user_prompt = transcription.text
                        st.toast(f"🎙️ 인식된 텍스트: \"{user_prompt}\"")
                        st.session_state.show_voice_recorder = False
                    except Exception as e:
                        st.error(f"음성 STT 에러: {e}")
            else:
                st.warning("음성 인식을 하려면 프로바이더를 OpenAI로 선택하고 API Key를 등록해야 합니다.")

# Check for temp_prompt from callback
if st.session_state.get("temp_prompt") is not None:
    user_prompt = st.session_state.temp_prompt
    st.session_state.temp_prompt = None
    if "text_input_key" in st.session_state:
        st.session_state.text_input_key = ""

# Check for starter prompt selection
if "starter_prompt" in st.session_state and st.session_state.starter_prompt:
    user_prompt = st.session_state.starter_prompt
    st.session_state.starter_prompt = None

# Process user prompt (convert to multimodal if photo is present)
if user_prompt is not None or st.session_state.pending_photo is not None:
    # Handle pending photo conversions
    if st.session_state.pending_photo is not None:
        import base64
        img_base64 = base64.b64encode(st.session_state.pending_photo).decode("utf-8")
        mime_type = st.session_state.pending_photo_mime or "image/jpeg"
        
        text_prompt = user_prompt if user_prompt else "이 사진 속 장소가 어디인지 찾아서 이름과 주소를 말해줘. 그리고 이 주변 지역에서 보낼 수 있는 완벽한 하루 코스(카페, 문화생활, 명소 등)를 정성껏 추천해줘!"
        
        # Structure multimodal content block
        user_prompt = [
            {"type": "text", "text": text_prompt},
            {"type": "image", "data": img_base64, "mime": mime_type}
        ]
        
        # Reset pending photo states
        st.session_state.pending_photo = None
        st.session_state.pending_photo_mime = None
        st.session_state.show_photo_uploader = False
        st.session_state.file_uploader_id += 1

    # Prevent sending image to text-only model
    is_multimodal = False
    if isinstance(user_prompt, list):
        for part in user_prompt:
            if part["type"] == "image":
                is_multimodal = True
                
    if is_multimodal and model == "gpt-3.5-turbo":
        st.error("현재 선택된 모델(gpt-3.5-turbo)은 이미지 분석을 지원하지 않습니다. 설정에서 gpt-4o, Claude 또는 Gemini 모델로 변경해 주세요.")
    else:
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        st.session_state.current_prompt = user_prompt
        st.session_state.generate_response = True
        st.rerun()
