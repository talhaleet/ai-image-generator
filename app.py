import os
import io
import streamlit as st
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

st.set_page_config(
    page_title="PixelMind AI",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* { box-sizing: border-box; margin: 0; padding: 0; }

html, body, .stApp {
    font-family: 'Inter', sans-serif;
    background-color: #0f0c29 !important;
    background-image: linear-gradient(135deg, #0f0c29 0%, #1a1245 50%, #24243e 100%) !important;
    color: #e2e8f0;
    min-height: 100vh;
}

.stApp > header { display: none !important; }
.block-container {
    max-width: 1100px !important;
    padding-top: 2.5rem !important;
    padding-bottom: 2.5rem !important;
}

/* Page title */
.page-title {
    font-size: 2rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 0.25rem;
}
.page-sub {
    color: rgba(200, 210, 240, 0.5);
    font-size: 0.88rem;
    margin-bottom: 0;
}

/* Divider */
hr { border-color: rgba(255,255,255,0.07) !important; margin: 1.2rem 0 !important; }

/* Column panel */
.panel {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1.8rem;
    height: 100%;
}
.panel-label {
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: rgba(160,170,210,0.5);
    margin-bottom: 1rem;
}

/* Text area */
.stTextArea textarea {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(160,130,255,0.3) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
    padding: 0.85rem 1rem !important;
    resize: none !important;
}
.stTextArea textarea:focus {
    border-color: rgba(160,100,255,0.7) !important;
    box-shadow: 0 0 0 2px rgba(120,60,255,0.13) !important;
    outline: none !important;
}
.stTextArea textarea::placeholder { color: rgba(150,160,200,0.4) !important; }
.stTextArea label { display: none !important; }

/* Generate button */
.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #7c3aed, #4f46e5) !important;
    color: #fff !important;
    font-weight: 600 !important;
    font-size: 0.97rem !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.7rem !important;
    transition: opacity 0.2s ease, transform 0.2s ease !important;
    box-shadow: 0 3px 14px rgba(124,58,237,0.4) !important;
    margin-top: 0.8rem !important;
}
.stButton > button:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}

/* Download button */
.stDownloadButton > button {
    width: 100%;
    background: rgba(16,185,129,0.1) !important;
    color: #34d399 !important;
    border: 1px solid rgba(16,185,129,0.38) !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.93rem !important;
    padding: 0.65rem !important;
    transition: all 0.2s ease !important;
    margin-top: 0.75rem !important;
}
.stDownloadButton > button:hover {
    background: rgba(16,185,129,0.2) !important;
    transform: translateY(-1px) !important;
}

/* Right panel image */
.stImage {
    display: flex !important;
    justify-content: center !important;
}
.stImage img {
    width: 320px !important;
    height: 320px !important;
    object-fit: cover !important;
    border-radius: 14px !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    box-shadow: 0 8px 30px rgba(0,0,0,0.5) !important;
    display: block !important;
    margin: 0 auto !important;
}

/* Image placeholder box */
.img-placeholder {
    width: 320px;
    height: 320px;
    margin: 0 auto;
    border-radius: 14px;
    border: 1.5px dashed rgba(160,130,255,0.25);
    background: rgba(255,255,255,0.02);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    gap: 0.5rem;
    color: rgba(160,170,210,0.35);
    font-size: 0.85rem;
    text-align: center;
    line-height: 1.5;
}
.img-placeholder span { font-size: 2rem; opacity: 0.4; }

/* Alerts */
.stAlert { border-radius: 10px !important; font-size: 0.88rem !important; }
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Page Header
# ----------------------------
st.markdown('<div class="page-title">🎨 AI-Image-Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="page-sub">AI-powered image generation · Stable Diffusion 3</div>', unsafe_allow_html=True)
st.markdown("---")

# ----------------------------
# Two-Column Layout
# ----------------------------
left, right = st.columns([1, 1], gap="large")

# ---- LEFT: Input ----
with left:
    

    prompt = st.text_area(
        "prompt",
        placeholder="A futuristic city at night, neon lights, rain-soaked streets, ultra-detailed...",
        height=180,
        label_visibility="collapsed"
    )

    generate = st.button("✨  Generate Image", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---- RIGHT: Output ----
with right:
    

    output = st.empty()
    download_slot = st.empty()

    # Default empty state
    output.markdown("""
    <div class="img-placeholder">
        <span>🖼️</span>
        Your image will appear here
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------
# HuggingFace Client
# ----------------------------
client = InferenceClient(
    provider="hf-inference",
    api_key=os.environ.get("HF_API_KEY")
)

# ----------------------------
# Generation Logic
# ----------------------------
if generate:
    if not prompt.strip():
        with left:
            st.warning("Please enter a prompt first.")
        st.stop()

    with right:
        with st.spinner("Generating image..."):
            try:
                image = client.text_to_image(
                    prompt=prompt,
                    model="stabilityai/stable-diffusion-3-medium-diffusers"
                )

                output.image(image, width=320)

                img_bytes = io.BytesIO()
                image.save(img_bytes, format="PNG")
                img_bytes.seek(0)

                download_slot.download_button(
                    label="📥  Download Image",
                    data=img_bytes,
                    file_name="generated_image.png",
                    mime="image/png",
                    use_container_width=True,
                )

            except Exception as e:
                output.error(f"Error: {e}")