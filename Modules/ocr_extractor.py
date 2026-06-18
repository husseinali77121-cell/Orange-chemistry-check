# =============================================================================
# Orange Lab Results Analyzer - OCR Module (Google Gemini Vision)
# Free tier: 1500 requests/day — gemini-1.5-flash
# =============================================================================

import base64
import json
import re
import streamlit as st
from PIL import Image
import io

EXTRACTION_PROMPT = """You are an expert clinical laboratory scientist.
Extract ALL numerical lab results from this lab report image.
Return ONLY a valid JSON object — no preamble, no markdown, no backticks.

Map results to these EXACT keys (use only matching keys, skip unknowns):
Glucose: FBG, RBG, 2hPP, HbA1c, Insulin
Kidney: Creatinine, Urea, UricAcid, eGFR
Liver: ALT, AST, ALP, GGT, TBili, DBili, Albumin, TotalProtein
Lipids: TC, TG, LDL, HDL
Thyroid: TSH, FT4, FT3
Iron: SerumFe, TIBC, Ferritin
CBC: Hgb, Hct, RBC, MCV, MCH, MCHC, RDW, WBC, Neutrophils, Lymphocytes, Monocytes, Eosinophils, Basophils, Platelets, Reticulocytes

UNIT CONVERSION — always convert to standard units:
- Glucose mmol/L → × 18.0 → mg/dL
- Creatinine µmol/L → ÷ 88.4 → mg/dL
- Urea mmol/L → ÷ 0.357 → mg/dL
- Bilirubin µmol/L → ÷ 17.1 → mg/dL
- Iron µmol/L → ÷ 0.179 → µg/dL
- TSH: keep as is

Example output:
{"FBG": 126.0, "HbA1c": 7.2, "Creatinine": 1.1, "ALT": 45, "WBC": 8.5}

Include ONLY tests with clear numerical values."""


def extract_results_from_image(image_bytes: bytes, api_key: str) -> dict:
    """
    Use Gemini Vision to extract lab results from an image.
    Model: gemini-1.5-flash (free tier: 1500 req/day)
    """
    try:
        import google.generativeai as genai
    except ImportError:
        st.error("⚠️ google-generativeai not installed. Run: pip install google-generativeai")
        return {}

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        # Convert bytes to PIL Image for Gemini
        pil_image = Image.open(io.BytesIO(image_bytes))

        response = model.generate_content([EXTRACTION_PROMPT, pil_image])
        raw = response.text.strip()

        # Clean any accidental markdown fences
        raw = re.sub(r"```json|```", "", raw).strip()

        data = json.loads(raw)

        # Filter: only numeric values, only known keys
        cleaned = {}
        for k, v in data.items():
            try:
                cleaned[k] = float(v)
            except (ValueError, TypeError):
                continue

        return cleaned

    except json.JSONDecodeError as e:
        st.error(f"⚠️ JSON parse error: {e}")
        return {}
    except Exception as e:
        st.error(f"⚠️ Gemini OCR error: {e}")
        return {}
