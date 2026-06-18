# =============================================================================
# Orange Lab Results Analyzer - OCR Module (Claude Vision)
# Extracts lab values from uploaded images
# =============================================================================

import anthropic
import base64
import json
import re
import streamlit as st
from PIL import Image
import io

def encode_image(image_bytes: bytes) -> str:
    """Encode image to base64."""
    return base64.b64encode(image_bytes).decode("utf-8")


def extract_results_from_image(image_bytes: bytes, api_key: str) -> dict:
    """
    Use Claude Vision to extract lab results from an image.
    Returns dict of {test_key: value} matching our REFERENCE_RANGES keys.
    """
    client = anthropic.Anthropic(api_key=api_key)

    system_prompt = """You are an expert clinical laboratory scientist. 
Extract ALL numerical lab results from the provided lab report image.
Return ONLY a valid JSON object — no preamble, no markdown, no backticks.

Map results to these EXACT keys (use only matching keys, skip unknowns):
Glucose: FBG, RBG, 2hPP, HbA1c, Insulin
Kidney: Creatinine, Urea, UricAcid, eGFR
Liver: ALT, AST, ALP, GGT, TBili, DBili, Albumin, TotalProtein
Lipids: TC, TG, LDL, HDL
Thyroid: TSH, FT4, FT3
Iron: SerumFe, TIBC, Ferritin
CBC: Hgb, Hct, RBC, MCV, MCH, MCHC, RDW, WBC, Neutrophils, Lymphocytes, Monocytes, Eosinophils, Basophils, Platelets, Reticulocytes

UNIT CONVERSION RULES - always convert to standard units:
- Glucose in mmol/L → multiply by 18.0 → mg/dL
- Creatinine in µmol/L → divide by 88.4 → mg/dL  
- Urea in mmol/L → divide by 0.357 → mg/dL (BUN)
- Bilirubin in µmol/L → divide by 17.1 → mg/dL
- Iron in µmol/L → divide by 0.179 → µg/dL
- TSH: keep as is (µIU/mL)
- If Urea reported as blood urea (not BUN): multiply by 0.467 to get BUN equivalent

Return format example:
{"FBG": 126.0, "HbA1c": 7.2, "Creatinine": 1.1, "ALT": 45, "WBC": 8.5}

Include ONLY tests with clear numerical values. Skip any result that is unclear or flagged as invalid."""

    b64 = encode_image(image_bytes)
    
    # Detect image type
    try:
        img = Image.open(io.BytesIO(image_bytes))
        fmt = img.format.lower() if img.format else "jpeg"
        media_type_map = {"jpeg": "image/jpeg", "jpg": "image/jpeg", 
                          "png": "image/png", "gif": "image/gif", 
                          "webp": "image/webp"}
        media_type = media_type_map.get(fmt, "image/jpeg")
    except Exception:
        media_type = "image/jpeg"

    try:
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=1500,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": b64,
                            },
                        },
                        {
                            "type": "text",
                            "text": "Extract all lab results from this report image and return as JSON."
                        }
                    ],
                }
            ],
        )

        raw = response.content[0].text.strip()
        # Clean any accidental markdown
        raw = re.sub(r"```json|```", "", raw).strip()
        data = json.loads(raw)
        
        # Filter: only numeric values
        cleaned = {}
        for k, v in data.items():
            try:
                cleaned[k] = float(v)
            except (ValueError, TypeError):
                continue
        
        return cleaned

    except json.JSONDecodeError as e:
        st.error(f"⚠️ OCR JSON parse error: {e}")
        return {}
    except Exception as e:
        st.error(f"⚠️ OCR extraction error: {e}")
        return {}
