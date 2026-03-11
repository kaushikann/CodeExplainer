import streamlit as st
import anthropic
import re

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Code Explainer for Beginners",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:ital,wght@0,400;0,500;1,400&family=DM+Sans:wght@300;400;500&display=swap');

/* ── Reset & base ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background: #0d0f14;
    color: #e8e6e0;
    font-family: 'DM Sans', sans-serif;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 80% 50% at 20% -10%, rgba(255,180,50,0.08) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 110%, rgba(255,100,60,0.07) 0%, transparent 55%),
        #0d0f14;
    min-height: 100vh;
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { background: #0d0f14 !important; }
.block-container { padding: 2.5rem 3rem 4rem !important; max-width: 1300px !important; }

/* ── Hero header ── */
.hero {
    text-align: center;
    padding: 3.5rem 0 2rem;
    position: relative;
}
.hero-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: #f5a623;
    margin-bottom: 1.2rem;
    opacity: 0.85;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: clamp(2.4rem, 5vw, 4rem);
    line-height: 1.05;
    background: linear-gradient(135deg, #f5f0e8 30%, #f5a623 70%, #ff6b35 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 1rem;
}
.hero-subtitle {
    font-size: 1.05rem;
    color: #9d9b94;
    font-weight: 300;
    max-width: 520px;
    margin: 0 auto;
    line-height: 1.65;
}

/* ── Divider ── */
.divider {
    width: 60px;
    height: 2px;
    background: linear-gradient(90deg, #f5a623, #ff6b35);
    margin: 2rem auto;
    border-radius: 2px;
}

/* ── Panel cards ── */
.panel {
    background: rgba(255,255,255,0.033);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 1.6rem 1.8rem;
    backdrop-filter: blur(12px);
    position: relative;
    overflow: hidden;
}
.panel::before {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 16px;
    padding: 1px;
    background: linear-gradient(135deg, rgba(245,166,35,0.25), transparent 60%);
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
    pointer-events: none;
}
.panel-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #f5a623;
    margin-bottom: 0.9rem;
    opacity: 0.9;
}

/* ── Streamlit widget overrides ── */
.stTextArea textarea {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    color: #e8e6e0 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.88rem !important;
    line-height: 1.6 !important;
    padding: 1rem !important;
    transition: border-color 0.2s !important;
}
.stTextArea textarea:focus {
    border-color: rgba(245,166,35,0.5) !important;
    box-shadow: 0 0 0 3px rgba(245,166,35,0.07) !important;
}
.stTextArea textarea::placeholder { color: #5a5852 !important; }
.stTextArea label { display: none !important; }

.stSelectbox label,
.stSlider label { color: #9d9b94 !important; font-size: 0.85rem !important; font-weight: 400 !important; }
.stSelectbox > div > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    color: #e8e6e0 !important;
}
[data-baseweb="select"] svg { color: #f5a623 !important; }

.stSlider [data-baseweb="slider"] div[role="slider"] {
    background: #f5a623 !important;
    border-color: #f5a623 !important;
}
.stSlider [data-baseweb="slider"] [data-testid="stSliderTrackFill"] {
    background: linear-gradient(90deg, #f5a623, #ff6b35) !important;
}

/* ── Main explain button ── */
.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #f5a623 0%, #ff6b35 100%) !important;
    color: #0d0f14 !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    letter-spacing: 0.03em !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.85rem 2rem !important;
    cursor: pointer !important;
    transition: transform 0.15s, box-shadow 0.15s !important;
    box-shadow: 0 4px 20px rgba(245,166,35,0.25) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 28px rgba(245,166,35,0.38) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── Explanation output ── */
.explanation-container {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 1.8rem 2rem;
    line-height: 1.8;
    font-size: 0.97rem;
    color: #d8d5ce;
    position: relative;
}
.explanation-container h3 {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    color: #f5f0e8;
    font-size: 1.1rem;
    margin: 1.4rem 0 0.5rem;
    border-bottom: 1px solid rgba(245,166,35,0.2);
    padding-bottom: 0.4rem;
}
.explanation-container h3:first-child { margin-top: 0; }
.explanation-container code {
    background: rgba(245,166,35,0.12);
    color: #f5a623;
    font-family: 'DM Mono', monospace;
    font-size: 0.83em;
    padding: 0.15em 0.45em;
    border-radius: 5px;
    border: 1px solid rgba(245,166,35,0.15);
}
.explanation-container ul, .explanation-container ol {
    padding-left: 1.4rem;
    margin: 0.6rem 0;
}
.explanation-container li { margin-bottom: 0.35rem; }
.explanation-container strong { color: #f5f0e8; font-weight: 600; }
.explanation-container em { color: #f5a623; font-style: normal; font-weight: 500; }
.explanation-container p { margin: 0.65rem 0; }
.explanation-container blockquote {
    border-left: 3px solid #f5a623;
    padding-left: 1rem;
    color: #9d9b94;
    margin: 0.8rem 0;
    font-style: italic;
}

/* ── Examples row ── */
.example-row { display: flex; gap: 0.75rem; flex-wrap: wrap; margin-top: 0.5rem; }
.example-btn-wrapper .stButton > button {
    background: rgba(255,255,255,0.05) !important;
    color: #c9c6be !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.78rem !important;
    font-weight: 400 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
    padding: 0.45rem 1rem !important;
    box-shadow: none !important;
    letter-spacing: 0.04em !important;
}
.example-btn-wrapper .stButton > button:hover {
    background: rgba(245,166,35,0.1) !important;
    border-color: rgba(245,166,35,0.35) !important;
    color: #f5a623 !important;
    transform: none !important;
    box-shadow: none !important;
}

/* ── Badge/tag ── */
.lang-badge {
    display: inline-block;
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    background: rgba(245,166,35,0.12);
    color: #f5a623;
    border: 1px solid rgba(245,166,35,0.25);
    border-radius: 6px;
    padding: 0.2em 0.6em;
    margin-left: 0.5rem;
    vertical-align: middle;
}

/* ── Tips box ── */
.tip-box {
    background: rgba(245,166,35,0.06);
    border: 1px solid rgba(245,166,35,0.18);
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
    font-size: 0.85rem;
    color: #9d9b94;
    margin-top: 1rem;
    line-height: 1.6;
}
.tip-box b { color: #f5a623; }

/* ── Spinner override ── */
[data-testid="stSpinner"] { color: #f5a623 !important; }
.stSpinner > div { border-top-color: #f5a623 !important; }

/* ── Footer ── */
.footer {
    text-align: center;
    padding: 2.5rem 0 1rem;
    font-size: 0.78rem;
    color: #4a4843;
    font-family: 'DM Mono', monospace;
    letter-spacing: 0.05em;
}

/* ── Responsive ── */
@media (max-width: 768px) {
    .block-container { padding: 1.5rem 1.2rem 3rem !important; }
    .hero { padding: 2rem 0 1rem; }
}
</style>
""", unsafe_allow_html=True)

# ── Example snippets ──────────────────────────────────────────────────────────
EXAMPLES = {
    "Python loop": '''\
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(f"I like {fruit}!")
''',
    "JS fetch": '''\
async function getUser(id) {
  const res = await fetch(`https://api.example.com/users/${id}`);
  const data = await res.json();
  return data;
}
''',
    "SQL query": '''\
SELECT customers.name, COUNT(orders.id) AS total_orders
FROM customers
LEFT JOIN orders ON customers.id = orders.customer_id
WHERE customers.country = 'USA'
GROUP BY customers.name
HAVING total_orders > 5
ORDER BY total_orders DESC;
''',
    "Recursion": '''\
def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n - 1)

print(factorial(5))  # 120
''',
}

LEVELS = {
    "🌱 Total Beginner": "Explain this code to someone who has never programmed before. Use simple analogies, everyday language, and avoid jargon. Define every technical term you use.",
    "📚 Some Experience": "Explain this code to someone with basic programming knowledge. You can use common terms like variable, loop, and function, but explain any advanced concepts.",
    "🎓 Intermediate": "Explain this code clearly, covering how it works, why certain patterns were chosen, and any important edge cases or best practices.",
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def detect_language(code: str) -> str:
    code_lower = code.lower()
    if re.search(r'\bdef \w+\(|\bimport \w+|\bprint\(', code): return "Python"
    if re.search(r'\bfunction\b|\bconst\b|\blet\b|\bvar\b|=>\s*\{|async\b', code): return "JavaScript"
    if re.search(r'SELECT\b|FROM\b|WHERE\b|JOIN\b', code, re.I): return "SQL"
    if re.search(r'<\w+>|</\w+>|<!DOCTYPE', code, re.I): return "HTML"
    if re.search(r'\bclass\b.*\{|\bpublic\b|\bprivate\b|\bvoid\b', code): return "Java/C#"
    if re.search(r'#include|std::|cout\b|cin\b', code): return "C++"
    if re.search(r'\bfn \w+|\blet mut\b|\bimpl\b', code): return "Rust"
    if re.search(r'\bfunc\b|\bvar\b.*:=|\bpackage\b', code): return "Go"
    return "Code"


def build_prompt(code: str, level_instruction: str, detail: int) -> str:
    detail_map = {1: "very brief (2-3 sentences per section)", 2: "concise", 3: "moderate", 4: "detailed", 5: "very thorough"}
    lang = detect_language(code)
    return f"""You are a patient, encouraging coding teacher. {level_instruction}

The code is written in {lang}.

Use this structure (with ### headers):
### 🧩 What does this code do?
### 🔍 Line-by-line breakdown
### 💡 Key concepts used
### 🚀 What could you do next?

Be {detail_map.get(detail, 'moderate')} in your explanations. Use analogies and real-world comparisons wherever helpful.

Here is the code to explain:
```
{code}
```"""


def explain_code(code: str, level: str, detail: int) -> str:
    client = anthropic.Anthropic()
    prompt = build_prompt(code, LEVELS[level], detail)
    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text

# ── UI ────────────────────────────────────────────────────────────────────────

# Hero
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">✦ Powered by Claude AI ✦</div>
    <h1 class="hero-title">AI Code Explainer<br>for Beginners</h1>
    <p class="hero-subtitle">Paste any code snippet and get a clear, plain-English explanation tailored to your experience level.</p>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)

# Main layout
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-label">01 — Your Code</div>', unsafe_allow_html=True)

    # Code input
    code_input = st.text_area(
        label="code",
        placeholder="# Paste your code here…\nfor i in range(10):\n    print(i)",
        height=280,
        key="code_area",
    )

    # Quick examples
    st.markdown('<div style="margin-top:1rem; margin-bottom:0.4rem; font-size:0.78rem; color:#5a5852; font-family:\'DM Mono\',monospace; letter-spacing:0.12em; text-transform:uppercase;">Try an example</div>', unsafe_allow_html=True)

    ex_cols = st.columns(len(EXAMPLES))
    for idx, (label, snippet) in enumerate(EXAMPLES.items()):
        with ex_cols[idx]:
            st.markdown('<div class="example-btn-wrapper">', unsafe_allow_html=True)
            if st.button(label, key=f"ex_{idx}"):
                st.session_state["code_area"] = snippet
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # close panel

    # Settings panel
    st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-label">02 — Explanation Settings</div>', unsafe_allow_html=True)

    level = st.selectbox(
        "Experience level",
        options=list(LEVELS.keys()),
        index=0,
    )

    detail = st.slider(
        "Detail level",
        min_value=1,
        max_value=5,
        value=3,
        help="1 = brief summary  •  5 = thorough walkthrough",
    )

    st.markdown('</div>', unsafe_allow_html=True)

    # Explain button
    st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)
    explain_clicked = st.button("✦ Explain This Code", use_container_width=True)

with col_right:
    st.markdown('<div class="panel" style="min-height:420px">', unsafe_allow_html=True)
    st.markdown('<div class="panel-label">03 — Explanation</div>', unsafe_allow_html=True)

    # Detect language for badge
    current_code = st.session_state.get("code_area", "") or code_input or ""
    if current_code.strip():
        lang_detected = detect_language(current_code.strip())
        st.markdown(f'<span style="font-size:0.82rem;color:#9d9b94;">Detected language:</span><span class="lang-badge">{lang_detected}</span>', unsafe_allow_html=True)

    if explain_clicked:
        code_to_explain = st.session_state.get("code_area", "") or code_input
        if not code_to_explain or not code_to_explain.strip():
            st.warning("Please paste some code first!")
        else:
            with st.spinner("Thinking through your code…"):
                try:
                    result = explain_code(code_to_explain.strip(), level, detail)
                    st.session_state["last_explanation"] = result
                except anthropic.AuthenticationError:
                    st.error("❌ Invalid API key. Set your `ANTHROPIC_API_KEY` environment variable.")
                except anthropic.RateLimitError:
                    st.error("⏳ Rate limit reached. Please wait a moment and try again.")
                except Exception as e:
                    st.error(f"Something went wrong: {e}")

    if "last_explanation" in st.session_state:
        explanation_html = st.session_state["last_explanation"]
        st.markdown(f'<div class="explanation-container">', unsafe_allow_html=True)
        st.markdown(explanation_html)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="tip-box">
            <b>How to use:</b><br>
            1. Paste your code on the left (or click an example).<br>
            2. Choose your experience level and desired detail.<br>
            3. Hit <b>Explain This Code</b> — Claude will break it down for you!
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown('<div class="footer">AI Code Explainer · Built with Streamlit & Claude · © 2025</div>', unsafe_allow_html=True)
