"""
╔══════════════════════════════════════════════════════════════════╗
║         Orange Lab Results Analyzer                              ║
║         Clinical Intelligence Engine for Lab Reports            ║
║         © Orange Lab — 6th October City, Giza, Egypt            ║
╚══════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import io
from modules.reference_ranges import REFERENCE_RANGES, PANELS
from modules.clinical_intelligence import run_cross_validation, flag_single_test, get_status
from modules.ocr_extractor import extract_results_from_image

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Orange Lab Results Analyzer",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  :root {
    --orange: #FF6B35;
    --orange-light: #FF8C5A;
    --dark-bg: #0f1117;
    --card-bg: #1a1d24;
    --card-border: #2a2d35;
  }

  .main-header {
    background: linear-gradient(135deg, #FF6B35 0%, #FF8C5A 50%, #FFB347 100%);
    padding: 1.5rem 2rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    text-align: center;
    box-shadow: 0 4px 20px rgba(255,107,53,0.35);
  }
  .main-header h1 {
    color: white;
    font-size: 2rem;
    font-weight: 800;
    margin: 0;
    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
  }
  .main-header p {
    color: rgba(255,255,255,0.9);
    margin: 0.3rem 0 0;
    font-size: 0.95rem;
  }

  .insight-critical {
    background: linear-gradient(135deg, #1a0505, #2d0a0a);
    border: 1px solid #ff4444;
    border-left: 5px solid #ff4444;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin: 0.6rem 0;
  }
  .insight-warning {
    background: linear-gradient(135deg, #1a1200, #2d1f00);
    border: 1px solid #ffaa00;
    border-left: 5px solid #ffaa00;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin: 0.6rem 0;
  }
  .insight-info {
    background: linear-gradient(135deg, #001a2d, #002d4d);
    border: 1px solid #0088ff;
    border-left: 5px solid #0088ff;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin: 0.6rem 0;
  }

  .test-high   { color: #ff6b6b; font-weight: 700; }
  .test-low    { color: #74b9ff; font-weight: 700; }
  .test-normal { color: #55efc4; font-weight: 700; }

  .summary-box {
    background: #1a1d24;
    border: 1px solid #2a2d35;
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 1rem;
    text-align: center;
  }
  .kpi-number  { font-size: 2rem; font-weight: 800; }
  .kpi-label   { font-size: 0.8rem; color: #888; margin-top: -0.3rem; }

  .panel-header {
    background: linear-gradient(90deg, rgba(255,107,53,0.15), transparent);
    border-left: 4px solid #FF6B35;
    padding: 0.4rem 0.8rem;
    border-radius: 0 8px 8px 0;
    margin: 1rem 0 0.5rem;
    font-weight: 700;
    font-size: 1rem;
    color: #FF8C5A;
  }

  .arabic-note {
    direction: rtl;
    text-align: right;
    font-size: 0.85rem;
    color: #aaa;
    border-top: 1px solid #333;
    margin-top: 0.5rem;
    padding-top: 0.5rem;
    font-family: 'Segoe UI', Arial, sans-serif;
  }

  .stTabs [data-baseweb="tab-list"] {
    background: #1a1d24;
    border-radius: 10px;
    gap: 4px;
    padding: 4px;
  }
  .stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    font-weight: 600;
  }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <h1>🧬 Orange Lab Results Analyzer</h1>
  <p>Clinical Intelligence Engine — Cross-validation & Pattern Recognition</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://via.placeholder.com/200x60/FF6B35/ffffff?text=🧡+Orange+Lab", width=200)
    st.markdown("---")

    st.markdown("### 👤 Patient Info")
    patient_name = st.text_input("Patient Name", placeholder="Optional")
    col1, col2 = st.columns(2)
    with col1:
        sex = st.selectbox("Sex", ["unspecified", "male", "female"])
    with col2:
        age = st.number_input("Age", min_value=0, max_value=120, value=0, step=1)
        age = age if age > 0 else None

    st.markdown("---")
    st.markdown("### 🔑 API Key (for OCR)")
    api_key = st.text_input("Gemini API Key", type="password",
                             placeholder="AIza...",
                             help="Free from aistudio.google.com — 1500 req/day")
    
    st.markdown("---")
    st.markdown("### 📋 Select Panels to Enter")
    selected_panels = []
    for panel_name in PANELS.keys():
        if st.checkbox(panel_name, value=False):
            selected_panels.append(panel_name)

    st.markdown("---")
    st.caption("🔬 Based on: ADA 2025, KDIGO, EASL, ACC/AHA, Tietz 7th Ed, Henry's 23rd Ed")

# ── Main area: Input Method tabs ──────────────────────────────────────────────
tab_manual, tab_ocr = st.tabs(["📝 Manual Entry", "📷 Upload Image (OCR)"])

results = {}  # Will hold {test_key: float_value}

# ── TAB 1: Manual Entry ───────────────────────────────────────────────────────
with tab_manual:
    if not selected_panels:
        st.info("👈 Select panels from the sidebar to start entering results.")
    else:
        st.markdown("Enter values below. Leave blank to skip a test.")
        
        for panel_name in selected_panels:
            st.markdown(f'<div class="panel-header">🔬 {panel_name}</div>', unsafe_allow_html=True)
            
            tests = PANELS[panel_name]
            # 3-column grid
            cols = st.columns(3)
            for i, test_key in enumerate(tests):
                ref = REFERENCE_RANGES[test_key]
                col = cols[i % 3]
                with col:
                    val = st.number_input(
                        f"{ref['label']} ({ref['unit']})",
                        min_value=0.0,
                        max_value=9999.0,
                        value=0.0,
                        step=0.1,
                        format="%.2f",
                        key=f"manual_{test_key}",
                        help=f"Arabic: {ref['label_ar']} | Unit: {ref['unit']}"
                    )
                    if val > 0:
                        results[test_key] = val

# ── TAB 2: OCR Upload ─────────────────────────────────────────────────────────
with tab_ocr:
    st.markdown("Upload a lab report image — Claude Vision will extract all values automatically.")
    
    uploaded_file = st.file_uploader(
        "Upload lab report image",
        type=["jpg", "jpeg", "png", "webp"],
        help="Clear image works best. Arabic or English reports supported."
    )

    ocr_results = {}

    if uploaded_file:
        image_bytes = uploaded_file.read()
        col_img, col_action = st.columns([2, 1])
        with col_img:
            st.image(image_bytes, caption="Uploaded Report", use_container_width=True)
        
        with col_action:
            st.markdown("### Extract Results")
            if not api_key:
                st.warning("⚠️ Enter your Gemini API key in the sidebar to use OCR.")
            else:
                if st.button("🔍 Extract with AI", type="primary", use_container_width=True):
                    with st.spinner("Claude Vision is reading the report..."):
                        ocr_results = extract_results_from_image(image_bytes, api_key)
                    
                    if ocr_results:
                        st.success(f"✅ Extracted {len(ocr_results)} test(s)!")
                        st.session_state["ocr_results"] = ocr_results
                    else:
                        st.error("Could not extract results. Try a clearer image.")

    # Show OCR extracted values (editable)
    if "ocr_results" in st.session_state and st.session_state["ocr_results"]:
        ocr_data = st.session_state["ocr_results"]
        st.markdown("### ✏️ Extracted Values — Review & Edit")
        st.caption("You can correct any value before running analysis.")
        
        ocr_cols = st.columns(3)
        for i, (key, raw_val) in enumerate(ocr_data.items()):
            if key not in REFERENCE_RANGES:
                continue
            ref = REFERENCE_RANGES[key]
            col = ocr_cols[i % 3]
            with col:
                edited = col.number_input(
                    f"{ref['label']} ({ref['unit']})",
                    min_value=0.0,
                    max_value=9999.0,
                    value=float(raw_val),
                    step=0.1,
                    format="%.2f",
                    key=f"ocr_edit_{key}"
                )
                if edited > 0:
                    results[key] = edited

# ── ANALYSIS BUTTON ───────────────────────────────────────────────────────────
st.markdown("---")

col_btn, col_clear = st.columns([3, 1])
with col_btn:
    run_analysis = st.button("🚀 Run Clinical Analysis", type="primary", 
                              use_container_width=True,
                              disabled=(len(results) == 0))
with col_clear:
    if st.button("🗑️ Clear All", use_container_width=True):
        if "ocr_results" in st.session_state:
            del st.session_state["ocr_results"]
        st.rerun()

# ── RESULTS DISPLAY ───────────────────────────────────────────────────────────
if run_analysis and results:
    st.markdown("---")
    
    # Header
    patient_display = f"**{patient_name}**" if patient_name else "Patient"
    sex_display = f" | {sex.capitalize()}" if sex != "unspecified" else ""
    age_display = f" | Age: {age}" if age else ""
    st.markdown(f"## 📊 Analysis Results — {patient_display}{sex_display}{age_display}")

    # ── Single-test flags ─────────────────────────────────────────────────────
    flags = []
    for key, value in results.items():
        flag = flag_single_test(key, value, sex)
        if flag:
            flags.append(flag)

    # KPI row
    n_high   = sum(1 for f in flags if f["status"] == "high")
    n_low    = sum(1 for f in flags if f["status"] == "low")
    n_normal = sum(1 for f in flags if f["status"] == "normal")
    n_tests  = len(flags)

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f'<div class="summary-box"><div class="kpi-number" style="color:#aaa">{n_tests}</div><div class="kpi-label">Tests Analyzed</div></div>', unsafe_allow_html=True)
    with k2:
        st.markdown(f'<div class="summary-box"><div class="kpi-number" style="color:#ff6b6b">{n_high}</div><div class="kpi-label">High</div></div>', unsafe_allow_html=True)
    with k3:
        st.markdown(f'<div class="summary-box"><div class="kpi-number" style="color:#74b9ff">{n_low}</div><div class="kpi-label">Low</div></div>', unsafe_allow_html=True)
    with k4:
        st.markdown(f'<div class="summary-box"><div class="kpi-number" style="color:#55efc4">{n_normal}</div><div class="kpi-label">Normal</div></div>', unsafe_allow_html=True)

    # ── Detailed test results table ───────────────────────────────────────────
    st.markdown("### 🔬 Individual Test Results")
    
    # Group by category
    categories = {}
    for f in flags:
        cat = f["category"]
        categories.setdefault(cat, []).append(f)

    for cat, cat_flags in categories.items():
        with st.expander(f"**{cat}** ({len(cat_flags)} tests)", expanded=True):
            rows = []
            for f in cat_flags:
                status_icon = "🔴" if f["status"] == "high" else "🔵" if f["status"] == "low" else "🟢"
                rows.append({
                    "Test": f["label"],
                    "Arabic": f["label_ar"],
                    "Value": f"{f['value']:.2f}",
                    "Unit": f["unit"],
                    "Status": f"{status_icon} {f['status'].capitalize()}",
                    "Reference": f["range_label"],
                })
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)

    # ── Cross-validation insights ─────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🧠 Clinical Intelligence — Cross-validation Insights")

    insights = run_cross_validation(results, sex=sex, age=age)

    if not insights:
        st.success("✅ No significant cross-validation alerts. Results appear internally consistent.")
    else:
        # Sort by severity
        severity_order = {"critical": 0, "warning": 1, "info": 2}
        insights.sort(key=lambda x: severity_order.get(x["severity"], 3))

        n_critical = sum(1 for i in insights if i["severity"] == "critical")
        n_warn     = sum(1 for i in insights if i["severity"] == "warning")
        n_info     = sum(1 for i in insights if i["severity"] == "info")

        st.markdown(
            f"**{len(insights)} insight(s) detected:** "
            f"🔴 {n_critical} Critical | ⚠️ {n_warn} Warning | ℹ️ {n_info} Info"
        )

        for insight in insights:
            css_class = f"insight-{insight['severity']}"
            
            with st.expander(insight["title"], expanded=(insight["severity"] == "critical")):
                st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
                
                # English body
                st.markdown("**📋 Clinical Interpretation:**")
                st.markdown(insight["body_en"])
                
                # Arabic note
                st.markdown(
                    f'<div class="arabic-note">📝 {insight["body_ar"]}</div>',
                    unsafe_allow_html=True
                )
                
                # References
                if insight.get("references"):
                    st.markdown(
                        f"<small>📚 References: {' | '.join(insight['references'])}</small>",
                        unsafe_allow_html=True
                    )
                
                st.markdown("</div>", unsafe_allow_html=True)

    # ── Disclaimer ────────────────────────────────────────────────────────────
    st.markdown("---")
    st.caption(
        "⚕️ **Clinical Disclaimer:** This tool provides decision support based on published guidelines. "
        "All results must be interpreted in clinical context by a qualified physician. "
        "Not a substitute for professional medical judgment."
    )
    st.caption(
        "📚 References: ADA 2025 | KDIGO 2024 | EASL 2023 | ACC/AHA 2024 | "
        "Tietz Clinical Chemistry 7th Ed | Henry's Clinical Diagnosis 23rd Ed | WHO/ICSH"
    )

elif not results and run_analysis:
    st.warning("⚠️ No test values entered. Please add results first.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<div style="text-align:center; color:#555; font-size:0.8rem;">'
    '🧡 Orange Lab Results Analyzer | 6th October City, Giza, Egypt'
    '</div>',
    unsafe_allow_html=True
)
