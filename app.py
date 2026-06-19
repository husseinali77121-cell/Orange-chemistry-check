"""
╔══════════════════════════════════════════════════════════════════╗
║         Orange Lab Results Analyzer                              ║
║         Clinical Intelligence Engine for Lab Reports            ║
║         © Orange Lab — 6th October City, Giza, Egypt            ║
╚══════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import base64
import json
import re
import io
from PIL import Image

# =============================================================================
# SECTION 1: REFERENCE RANGES DATABASE
# Based on: Tietz Clinical Chemistry, Henry's Clinical Diagnosis,
#           ADA 2025, KDIGO, EASL, ACC/AHA, WHO/ICSH
# =============================================================================

REFERENCE_RANGES = {
    # GLUCOSE & DIABETES
    "FBG":      {"label": "Fasting Blood Glucose",           "label_ar": "سكر الصيام",               "unit": "mg/dL",        "ranges": {"normal": (70, 99)},                  "category": "Glucose",    "panel": "Chemistry"},
    "RBG":      {"label": "Random Blood Glucose",            "label_ar": "سكر عشوائي",               "unit": "mg/dL",        "ranges": {"normal": (0, 139)},                  "category": "Glucose",    "panel": "Chemistry"},
    "2hPP":     {"label": "2h Post-prandial Glucose",        "label_ar": "سكر بعد الأكل",            "unit": "mg/dL",        "ranges": {"normal": (0, 139)},                  "category": "Glucose",    "panel": "Chemistry"},
    "HbA1c":    {"label": "Glycated Hemoglobin A1c",         "label_ar": "السكر التراكمي",            "unit": "%",            "ranges": {"normal": (0, 5.6)},                  "category": "Glucose",    "panel": "Chemistry"},
    "Insulin":  {"label": "Fasting Insulin",                 "label_ar": "الأنسولين الصيامي",         "unit": "µIU/mL",       "ranges": {"normal": (2.6, 24.9)},               "category": "Glucose",    "panel": "Chemistry"},
    # KIDNEY
    "Creatinine":{"label": "Serum Creatinine",               "label_ar": "كرياتينين الدم",            "unit": "mg/dL",        "ranges": {"normal_male": (0.7, 1.2), "normal_female": (0.5, 1.0), "normal": (0.5, 1.2)}, "category": "Kidney", "panel": "Chemistry"},
    "Urea":     {"label": "Blood Urea Nitrogen",             "label_ar": "يوريا الدم",               "unit": "mg/dL",        "ranges": {"normal": (7, 20)},                   "category": "Kidney",     "panel": "Chemistry"},
    "UricAcid": {"label": "Uric Acid",                       "label_ar": "حمض اليوريك",              "unit": "mg/dL",        "ranges": {"normal_male": (3.4, 7.0), "normal_female": (2.4, 6.0), "normal": (2.4, 7.0)}, "category": "Kidney", "panel": "Chemistry"},
    "eGFR":     {"label": "Estimated GFR",                   "label_ar": "معدل الترشيح الكبيبي",      "unit": "mL/min/1.73m²","ranges": {"normal": (90, 999)},                 "category": "Kidney",     "panel": "Chemistry"},
    # LIVER
    "ALT":      {"label": "Alanine Aminotransferase",        "label_ar": "إنزيم الكبد ALT",          "unit": "U/L",          "ranges": {"normal_male": (7, 56), "normal_female": (7, 45), "normal": (7, 56)}, "category": "Liver", "panel": "Chemistry"},
    "AST":      {"label": "Aspartate Aminotransferase",      "label_ar": "إنزيم الكبد AST",          "unit": "U/L",          "ranges": {"normal_male": (10, 40), "normal_female": (10, 35), "normal": (10, 40)}, "category": "Liver", "panel": "Chemistry"},
    "ALP":      {"label": "Alkaline Phosphatase",            "label_ar": "الفوسفاتاز القلوي",         "unit": "U/L",          "ranges": {"normal": (44, 147)},                 "category": "Liver",      "panel": "Chemistry"},
    "GGT":      {"label": "Gamma-Glutamyl Transferase",      "label_ar": "إنزيم GGT",                "unit": "U/L",          "ranges": {"normal_male": (8, 61), "normal_female": (5, 36), "normal": (5, 61)}, "category": "Liver", "panel": "Chemistry"},
    "TBili":    {"label": "Total Bilirubin",                 "label_ar": "البيليروبين الكلي",         "unit": "mg/dL",        "ranges": {"normal": (0.2, 1.2)},                "category": "Liver",      "panel": "Chemistry"},
    "DBili":    {"label": "Direct Bilirubin",                "label_ar": "البيليروبين المباشر",       "unit": "mg/dL",        "ranges": {"normal": (0.0, 0.3)},                "category": "Liver",      "panel": "Chemistry"},
    "Albumin":  {"label": "Serum Albumin",                   "label_ar": "الألبومين",                "unit": "g/dL",         "ranges": {"normal": (3.5, 5.0)},                "category": "Liver",      "panel": "Chemistry"},
    "TotalProtein":{"label":"Total Protein",                 "label_ar": "البروتين الكلي",            "unit": "g/dL",         "ranges": {"normal": (6.3, 8.2)},                "category": "Liver",      "panel": "Chemistry"},
    # LIPIDS
    "TC":       {"label": "Total Cholesterol",               "label_ar": "الكوليسترول الكلي",         "unit": "mg/dL",        "ranges": {"normal": (0, 199)},                  "category": "Lipids",     "panel": "Chemistry"},
    "TG":       {"label": "Triglycerides",                   "label_ar": "الدهون الثلاثية",           "unit": "mg/dL",        "ranges": {"normal": (0, 149)},                  "category": "Lipids",     "panel": "Chemistry"},
    "LDL":      {"label": "LDL Cholesterol",                 "label_ar": "الكوليسترول الضار",         "unit": "mg/dL",        "ranges": {"normal": (0, 99)},                   "category": "Lipids",     "panel": "Chemistry"},
    "HDL":      {"label": "HDL Cholesterol",                 "label_ar": "الكوليسترول المفيد",        "unit": "mg/dL",        "ranges": {"normal_male": (40, 999), "normal_female": (50, 999), "normal": (40, 999)}, "category": "Lipids", "panel": "Chemistry"},
    # THYROID
    "TSH":      {"label": "Thyroid Stimulating Hormone",     "label_ar": "هرمون الغدة الدرقية TSH",  "unit": "µIU/mL",       "ranges": {"normal": (0.4, 4.0)},                "category": "Thyroid",    "panel": "Chemistry"},
    "FT4":      {"label": "Free Thyroxine",                  "label_ar": "الثيروكسين الحر FT4",       "unit": "ng/dL",        "ranges": {"normal": (0.8, 1.8)},                "category": "Thyroid",    "panel": "Chemistry"},
    "FT3":      {"label": "Free Triiodothyronine",           "label_ar": "الثيرونين الحر FT3",        "unit": "pg/mL",        "ranges": {"normal": (2.3, 4.2)},                "category": "Thyroid",    "panel": "Chemistry"},
    # IRON
    "SerumFe":  {"label": "Serum Iron",                      "label_ar": "حديد الدم",                "unit": "µg/dL",        "ranges": {"normal_male": (65, 175), "normal_female": (50, 170), "normal": (50, 175)}, "category": "Iron", "panel": "Chemistry"},
    "TIBC":     {"label": "Total Iron Binding Capacity",     "label_ar": "طاقة ربط الحديد الكلية",   "unit": "µg/dL",        "ranges": {"normal": (250, 370)},                "category": "Iron",       "panel": "Chemistry"},
    "Ferritin": {"label": "Serum Ferritin",                  "label_ar": "فيريتين الدم",              "unit": "ng/mL",        "ranges": {"normal_male": (24, 336), "normal_female": (11, 307), "normal": (11, 336)}, "category": "Iron", "panel": "Chemistry"},
    # CBC
    "Hgb":      {"label": "Hemoglobin",                      "label_ar": "الهيموجلوبين",              "unit": "g/dL",         "ranges": {"normal_male": (13.5, 17.5), "normal_female": (12.0, 15.5), "normal": (12.0, 17.5)}, "category": "CBC", "panel": "Hematology"},
    "Hct":      {"label": "Hematocrit",                      "label_ar": "الهيماتوكريت",              "unit": "%",            "ranges": {"normal_male": (41, 53), "normal_female": (36, 46), "normal": (36, 53)}, "category": "CBC", "panel": "Hematology"},
    "RBC":      {"label": "Red Blood Cell Count",            "label_ar": "كريات الدم الحمراء",        "unit": "×10⁶/µL",      "ranges": {"normal_male": (4.5, 5.9), "normal_female": (4.0, 5.2), "normal": (4.0, 5.9)}, "category": "CBC", "panel": "Hematology"},
    "MCV":      {"label": "Mean Corpuscular Volume",         "label_ar": "متوسط حجم الكريات",         "unit": "fL",           "ranges": {"normal": (80, 100)},                 "category": "CBC",        "panel": "Hematology"},
    "MCH":      {"label": "Mean Corpuscular Hemoglobin",     "label_ar": "متوسط هيموجلوبين الكريات",  "unit": "pg",           "ranges": {"normal": (27, 33)},                  "category": "CBC",        "panel": "Hematology"},
    "MCHC":     {"label": "MCHC",                            "label_ar": "تركيز هيموجلوبين الكريات",  "unit": "g/dL",         "ranges": {"normal": (32, 36)},                  "category": "CBC",        "panel": "Hematology"},
    "RDW":      {"label": "Red Cell Distribution Width",     "label_ar": "توزيع حجم الكريات",         "unit": "%",            "ranges": {"normal": (11.5, 14.5)},              "category": "CBC",        "panel": "Hematology"},
    "WBC":      {"label": "White Blood Cell Count",          "label_ar": "كريات الدم البيضاء",        "unit": "×10³/µL",      "ranges": {"normal": (4.5, 11.0)},               "category": "CBC",        "panel": "Hematology"},
    "Neutrophils":{"label":"Neutrophils",                    "label_ar": "النيوتروفيل",               "unit": "%",            "ranges": {"normal": (50, 70)},                  "category": "CBC",        "panel": "Hematology"},
    "Lymphocytes":{"label":"Lymphocytes",                    "label_ar": "الليمفاويات",               "unit": "%",            "ranges": {"normal": (20, 40)},                  "category": "CBC",        "panel": "Hematology"},
    "Monocytes":  {"label":"Monocytes",                      "label_ar": "المونوسيت",                 "unit": "%",            "ranges": {"normal": (2, 8)},                    "category": "CBC",        "panel": "Hematology"},
    "Eosinophils":{"label":"Eosinophils",                    "label_ar": "الحمضات",                   "unit": "%",            "ranges": {"normal": (1, 4)},                    "category": "CBC",        "panel": "Hematology"},
    "Basophils":  {"label":"Basophils",                      "label_ar": "القاعدات",                  "unit": "%",            "ranges": {"normal": (0, 1)},                    "category": "CBC",        "panel": "Hematology"},
    "Platelets":  {"label":"Platelet Count",                 "label_ar": "الصفائح الدموية",           "unit": "×10³/µL",      "ranges": {"normal": (150, 400)},                "category": "CBC",        "panel": "Hematology"},
    "Reticulocytes":{"label":"Reticulocyte Count",           "label_ar": "الشبكيات",                  "unit": "%",            "ranges": {"normal": (0.5, 2.5)},                "category": "CBC",        "panel": "Hematology"},
}

PANELS = {
    "Glucose & Diabetes": ["FBG", "RBG", "2hPP", "HbA1c", "Insulin"],
    "Kidney Function":    ["Creatinine", "Urea", "UricAcid", "eGFR"],
    "Liver Function":     ["ALT", "AST", "ALP", "GGT", "TBili", "DBili", "Albumin", "TotalProtein"],
    "Lipid Panel":        ["TC", "TG", "LDL", "HDL"],
    "Thyroid":            ["TSH", "FT4", "FT3"],
    "Iron Studies":       ["SerumFe", "TIBC", "Ferritin"],
    "CBC":                ["Hgb", "Hct", "RBC", "MCV", "MCH", "MCHC", "RDW",
                           "WBC", "Neutrophils", "Lymphocytes", "Monocytes",
                           "Eosinophils", "Basophils", "Platelets", "Reticulocytes"],
}

# =============================================================================
# SECTION 2: CLINICAL INTELLIGENCE ENGINE
# =============================================================================

def get_status(key, value, sex="unspecified"):
    if key not in REFERENCE_RANGES:
        return "unknown", "N/A"
    ranges = REFERENCE_RANGES[key]["ranges"]
    if sex == "male" and "normal_male" in ranges:
        lo, hi = ranges["normal_male"]
    elif sex == "female" and "normal_female" in ranges:
        lo, hi = ranges["normal_female"]
    elif "normal" in ranges:
        lo, hi = ranges["normal"]
    else:
        lo, hi = list(ranges.values())[0]
    ref = REFERENCE_RANGES[key]
    if value < lo:
        return "low",    f"↓ Low  (ref: {lo}–{hi} {ref['unit']})"
    elif value > hi:
        return "high",   f"↑ High (ref: {lo}–{hi} {ref['unit']})"
    else:
        return "normal", f"✓ Normal ({lo}–{hi} {ref['unit']})"


def flag_single_test(key, value, sex="unspecified"):
    if key not in REFERENCE_RANGES:
        return {}
    ref = REFERENCE_RANGES[key]
    status, range_label = get_status(key, value, sex)
    return {
        "key": key, "label": ref["label"], "label_ar": ref["label_ar"],
        "value": value, "unit": ref["unit"],
        "status": status, "range_label": range_label, "category": ref["category"],
    }


def run_cross_validation(results: dict, sex="unspecified", age=None) -> list:
    insights = []
    r = results

    def has(*keys): return all(k in r for k in keys)
    def val(k):     return r.get(k)

    # ── 1. FBG vs HbA1c ──────────────────────────────────────────────────────
    if has("FBG", "HbA1c"):
        fbg, hba1c = val("FBG"), val("HbA1c")
        eag = (hba1c * 28.7) - 46.7  # ADA estimated average glucose

        if fbg >= 126 and hba1c < 5.7:
            insights.append({
                "category": "Glucose", "severity": "warning",
                "title": "⚠️ FBG High — HbA1c Discordant (Falsely Normal HbA1c?)",
                "body_en": (
                    f"FBG {fbg} mg/dL (diabetic range) but HbA1c {hba1c}% (normal). "
                    f"Expected average glucose from HbA1c: ~{eag:.0f} mg/dL.\n\n"
                    "Possible causes:\n"
                    "• Hemoglobin variants (HbS, HbC, thalassemia) → falsely low HbA1c\n"
                    "• Hemolytic anemia → shortened RBC lifespan\n"
                    "• Recent blood transfusion\n\n"
                    "Recommendation: CBC, reticulocytes, hemoglobin electrophoresis. "
                    "Consider fructosamine as alternative glycemic marker."
                ),
                "body_ar": (
                    f"سكر الصيام {fbg} (مستوى السكري) لكن HbA1c {hba1c}% (طبيعي) — تناقض مهم.\n"
                    "الأسباب المحتملة: هيموجلوبين غير طبيعي (الثلاسيميا، HbS) أو فقر دم انحلالي.\n"
                    "يُنصح: CBC وكهربة الهيموجلوبين."
                ),
                "references": ["ADA Standards of Care 2025", "IFCC HbA1c Standardization"]
            })
        elif fbg < 100 and hba1c >= 6.5:
            insights.append({
                "category": "Glucose", "severity": "warning",
                "title": "⚠️ HbA1c Diabetic — FBG Normal (Falsely Elevated HbA1c?)",
                "body_en": (
                    f"HbA1c {hba1c}% (diabetic) but FBG {fbg} mg/dL (normal). "
                    "Possible causes: iron deficiency anemia, B12 deficiency, splenectomy, uremia.\n"
                    "Recommendation: Iron studies, B12, renal function."
                ),
                "body_ar": (
                    f"HbA1c {hba1c}% (مستوى السكري) لكن سكر الصيام طبيعي {fbg}.\n"
                    "محتمل: نقص الحديد أو B12 يرفع HbA1c كاذباً.\n"
                    "يُنصح: فيريتين، B12، وظائف كلى."
                ),
                "references": ["ADA 2025", "Tietz Clinical Chemistry 7th Ed"]
            })
        elif abs(fbg - eag) > 50:
            insights.append({
                "category": "Glucose", "severity": "info",
                "title": "ℹ️ FBG vs HbA1c — Significant Discordance",
                "body_en": (
                    f"Estimated average glucose from HbA1c {hba1c}%: ~{eag:.0f} mg/dL. "
                    f"Measured FBG: {fbg} mg/dL. Difference: {abs(fbg-eag):.0f} mg/dL.\n"
                    "May indicate glucose variability or post-meal spikes."
                ),
                "body_ar": f"فرق {abs(fbg-eag):.0f} mg/dL بين متوسط الجلوكوز المقدر والسكر المقيس — تذبذب محتمل.",
                "references": ["ADA 2025"]
            })

    # ── 2. BUN:Creatinine Ratio ───────────────────────────────────────────────
    if has("Urea", "Creatinine"):
        urea, cr = val("Urea"), val("Creatinine")
        ratio = urea / cr if cr > 0 else 0
        if ratio > 40:
            insights.append({
                "category": "Kidney", "severity": "critical",
                "title": "🔴 BUN:Creatinine Ratio > 40 — Suspect Upper GI Bleeding",
                "body_en": (
                    f"BUN:Creatinine ratio = {ratio:.1f} (normal 10–20). "
                    "Very high ratio (>40) strongly suggests upper GI bleeding "
                    "(blood protein digested → elevated BUN without proportional Cr rise).\n"
                    "Also: severe dehydration, high protein diet.\n"
                    "Recommendation: Urgent clinical assessment for GI bleed."
                ),
                "body_ar": (
                    f"نسبة يوريا/كرياتينين = {ratio:.1f} — مرتفعة جداً.\n"
                    "تشير بقوة لنزيف في الجهاز الهضمي العلوي. تقييم إكلينيكي عاجل."
                ),
                "references": ["NEJM 2016", "Henry's Clinical Diagnosis 23rd Ed"]
            })
        elif ratio > 20:
            insights.append({
                "category": "Kidney", "severity": "warning",
                "title": "⚠️ BUN:Creatinine Ratio > 20 — Pre-renal Azotemia",
                "body_en": (
                    f"BUN:Creatinine ratio = {ratio:.1f}. "
                    "Elevated ratio suggests pre-renal causes: dehydration, heart failure, "
                    "decreased renal perfusion, high protein intake, or GI bleeding."
                ),
                "body_ar": f"نسبة يوريا/كرياتينين = {ratio:.1f} — محتمل: جفاف، قصور قلب، أو نزيف هضمي.",
                "references": ["KDIGO AKI Guidelines 2024"]
            })
        elif ratio < 10 and urea < 7:
            insights.append({
                "category": "Kidney", "severity": "info",
                "title": "ℹ️ Low BUN:Creatinine Ratio — Consider Liver Disease or Low Protein",
                "body_en": (
                    f"BUN:Creatinine ratio = {ratio:.1f} (low). "
                    "May indicate: liver disease, very low protein diet, SIADH, or malnutrition."
                ),
                "body_ar": f"نسبة يوريا/كرياتينين منخفضة = {ratio:.1f} — محتمل: مرض كبدي أو نظام غذائي منخفض البروتين.",
                "references": ["Tietz 7th Ed"]
            })

    # ── 3. Liver Patterns ─────────────────────────────────────────────────────
    if has("ALT", "AST"):
        alt, ast = val("ALT"), val("AST")
        alt_uln, ast_uln = 56, 40
        de_ritis = ast / alt if alt > 0 else 0

        if (alt > alt_uln or ast > ast_uln) and de_ritis >= 2.0:
            insights.append({
                "category": "Liver", "severity": "warning",
                "title": "⚠️ De Ritis Ratio ≥ 2 — Alcoholic Liver Disease Pattern",
                "body_en": (
                    f"AST/ALT (De Ritis) ratio = {de_ritis:.1f}. "
                    f"Ratio ≥ 2 is highly suggestive of alcoholic liver disease. "
                    f"AST {ast} U/L, ALT {alt} U/L.\n"
                    "Also consider: cirrhosis, cardiac hepatopathy.\n"
                    "Recommendation: Correlate with clinical history and GGT."
                ),
                "body_ar": f"نسبة AST/ALT (De Ritis) = {de_ritis:.1f} — تشير لمرض الكبد الكحولي.\nيُنصح: مقارنة مع GGT والتاريخ الإكلينيكي.",
                "references": ["EASL Alcohol-Related Liver Disease 2023"]
            })

        if has("ALP") and (alt > alt_uln or ast > ast_uln):
            alp = val("ALP")
            alp_uln = 147
            alt_x = alt / alt_uln
            alp_x = alp / alp_uln if alp_uln else 1
            r_ratio = alt_x / alp_x if alp_x > 0 else 0
            pattern    = "Hepatocellular" if r_ratio >= 5 else "Cholestatic" if r_ratio <= 2 else "Mixed"
            pattern_ar = "تلف خلوي كبدي"  if r_ratio >= 5 else "انسدادي / ركود صفراوي" if r_ratio <= 2 else "مختلط"
            desc_en = {
                "Hepatocellular": "Causes: viral hepatitis, drug-induced, ischemic, autoimmune.",
                "Cholestatic":    "Causes: bile duct obstruction, PBC, PSC, drug-induced cholestasis.",
                "Mixed":          "Could be drug-induced or overlap syndrome.",
            }
            insights.append({
                "category": "Liver", "severity": "info",
                "title": f"ℹ️ Liver Injury Pattern: {pattern}",
                "body_en": (
                    f"R-ratio = {r_ratio:.1f} → {pattern} pattern.\n"
                    f"• ALT: {alt} U/L ({alt/alt_uln:.1f}× ULN)\n"
                    f"• AST: {ast} U/L\n"
                    f"• ALP: {alp} U/L ({alp/alp_uln:.1f}× ULN)\n\n"
                    + desc_en[pattern]
                ),
                "body_ar": f"نمط إصابة الكبد: {pattern_ar} (R-ratio = {r_ratio:.1f}).",
                "references": ["EASL DILI Guidelines 2023", "RUCAM Scale"]
            })

        if alt > 1000 or ast > 1000:
            insights.append({
                "category": "Liver", "severity": "critical",
                "title": "🔴 Massively Elevated Transaminases (>1000 U/L)",
                "body_en": (
                    f"ALT {alt} U/L, AST {ast} U/L — extreme elevation.\n"
                    "Top differential:\n"
                    "1. Acute viral hepatitis (HAV, HBV, HEV)\n"
                    "2. Ischemic hepatitis ('shock liver') — check cardiac status\n"
                    "3. Drug/toxin-induced (paracetamol overdose)\n"
                    "4. Autoimmune hepatitis\n"
                    "Urgent: PT/INR, renal function, viral serology."
                ),
                "body_ar": (
                    f"ALT/AST أكثر من 1000 — ارتفاع شديد جداً.\n"
                    "أهم الأسباب: التهاب كبد فيروسي حاد، كبد الصدمة، سمية الدواء.\n"
                    "عاجل: PT/INR ووظائف كلى."
                ),
                "references": ["EASL 2023", "AASLD 2024"]
            })

    # ── 4. Lipid Panel ────────────────────────────────────────────────────────
    if has("TC", "TG", "HDL", "LDL"):
        tc, tg, hdl, ldl = val("TC"), val("TG"), val("HDL"), val("LDL")
        friedewald_ldl = tc - hdl - (tg / 5)

        if tg > 400:
            insights.append({
                "category": "Lipids", "severity": "critical",
                "title": "🔴 TG > 400 — Friedewald LDL Formula INVALID",
                "body_en": (
                    f"Triglycerides = {tg} mg/dL. The Friedewald equation is UNRELIABLE when TG > 400.\n"
                    "Reported LDL may be significantly underestimated.\n"
                    "Recommendation: Order direct LDL measurement or use Martin-Hopkins equation."
                ),
                "body_ar": f"الدهون الثلاثية {tg} — معادلة Friedewald لحساب LDL غير صحيحة.\nيجب قياس LDL المباشر (Direct LDL).",
                "references": ["ACC/AHA 2024 Lipid Guidelines"]
            })
        elif tg > 200 and abs(ldl - friedewald_ldl) > 20:
            insights.append({
                "category": "Lipids", "severity": "info",
                "title": "ℹ️ TG > 200 — Friedewald LDL May Be Less Accurate",
                "body_en": (
                    f"TG = {tg} mg/dL. Friedewald LDL = {friedewald_ldl:.0f} vs reported LDL = {ldl} "
                    f"(difference {abs(ldl-friedewald_ldl):.0f} mg/dL). "
                    "Consider Martin-Hopkins equation for better accuracy."
                ),
                "body_ar": f"الدهون الثلاثية {tg} — LDL المحسوب قد يكون أقل دقة.",
                "references": ["ACC/AHA 2024"]
            })

        if tg > 150 and hdl < 40:
            insights.append({
                "category": "Lipids", "severity": "warning",
                "title": "⚠️ Atherogenic Dyslipidemia (↑TG + ↓HDL)",
                "body_en": (
                    f"TG {tg} mg/dL + HDL {hdl} mg/dL — classic atherogenic dyslipidemia. "
                    "High cardiovascular risk. Commonly associated with insulin resistance / metabolic syndrome.\n"
                    "Recommendation: Assess for metabolic syndrome (FBG, BP, waist circumference)."
                ),
                "body_ar": f"دهون ثلاثية مرتفعة ({tg}) + HDL منخفض ({hdl}) = خطر قلبي وعائي.\nمرتبط بمقاومة الإنسولين.",
                "references": ["ACC/AHA 2024", "IDF Metabolic Syndrome Definition"]
            })

    # ── 5. Thyroid Axis ───────────────────────────────────────────────────────
    if has("TSH", "FT4"):
        tsh, ft4 = val("TSH"), val("FT4")
        if tsh > 4.0 and ft4 < 0.8:
            insights.append({
                "category": "Thyroid", "severity": "warning",
                "title": "⚠️ Primary Hypothyroidism Pattern",
                "body_en": (
                    f"TSH {tsh} µIU/mL (↑) + FT4 {ft4} ng/dL (↓) = Primary hypothyroidism.\n"
                    "Causes: Hashimoto's thyroiditis, post-thyroidectomy, iodine deficiency.\n"
                    "Recommendation: Anti-TPO antibodies, Anti-thyroglobulin."
                ),
                "body_ar": f"TSH مرتفع ({tsh}) + FT4 منخفض ({ft4}) = قصور الغدة الدرقية الأولي.\nالأسباب الشائعة: هاشيموتو.",
                "references": ["ATA Guidelines 2024"]
            })
        elif tsh < 0.4 and ft4 > 1.8:
            insights.append({
                "category": "Thyroid", "severity": "warning",
                "title": "⚠️ Primary Hyperthyroidism Pattern",
                "body_en": (
                    f"TSH {tsh} µIU/mL (↓) + FT4 {ft4} ng/dL (↑) = Primary hyperthyroidism.\n"
                    "Causes: Graves' disease, toxic nodular goiter, thyroiditis.\n"
                    "Recommendation: Anti-TSH receptor antibodies (TRAb), thyroid scan."
                ),
                "body_ar": f"TSH منخفض ({tsh}) + FT4 مرتفع ({ft4}) = فرط نشاط الغدة الدرقية.\nالأسباب: مرض جريفز.",
                "references": ["ATA 2024"]
            })
        elif tsh < 0.4 and ft4 < 0.8:
            insights.append({
                "category": "Thyroid", "severity": "warning",
                "title": "⚠️ Central Hypothyroidism Pattern",
                "body_en": (
                    f"TSH {tsh} µIU/mL (↓) + FT4 {ft4} ng/dL (↓) = Central hypothyroidism.\n"
                    "Caused by pituitary or hypothalamic dysfunction.\n"
                    "Recommendation: MRI pituitary, prolactin, cortisol."
                ),
                "body_ar": f"TSH منخفض + FT4 منخفض = قصور درقي مركزي (نخامية).\nيُنصح: MRI نخامية.",
                "references": ["ETA 2023"]
            })
        elif tsh > 4.0 and 0.8 <= ft4 <= 1.8:
            insights.append({
                "category": "Thyroid", "severity": "info",
                "title": "ℹ️ Subclinical Hypothyroidism",
                "body_en": (
                    f"TSH {tsh} µIU/mL (↑) + FT4 {ft4} ng/dL (normal). "
                    "Monitor every 6–12 months. Consider treatment if TSH > 10 or symptomatic."
                ),
                "body_ar": f"TSH مرتفع + FT4 طبيعي = قصور درقي تحت الإكلينيكي.\nمتابعة كل 6-12 شهر.",
                "references": ["ATA 2024"]
            })

    # ── 6. Iron Studies ───────────────────────────────────────────────────────
    if has("SerumFe", "TIBC", "Ferritin"):
        fe, tibc, ferritin = val("SerumFe"), val("TIBC"), val("Ferritin")
        sat = (fe / tibc * 100) if tibc > 0 else 0

        if fe < 60 and tibc > 370 and ferritin < 12:
            insights.append({
                "category": "Iron", "severity": "warning",
                "title": "⚠️ Classic Iron Deficiency Pattern",
                "body_en": (
                    f"Fe ↓ ({fe}) + TIBC ↑ ({tibc}) + Ferritin ↓ ({ferritin}) + Sat {sat:.0f}% = Iron deficiency.\n"
                    "Causes: blood loss (GI, menstrual), malabsorption, inadequate intake.\n"
                    "Recommendation: Identify and treat the underlying cause."
                ),
                "body_ar": f"حديد منخفض + TIBC مرتفع + فيريتين منخفض = نقص الحديد الكلاسيكي.\nأسباب: فقدان دم، سوء امتصاص.",
                "references": ["WHO Iron Deficiency 2023", "BSH Guidelines"]
            })
        elif fe < 60 and tibc < 250 and ferritin > 100:
            insights.append({
                "category": "Iron", "severity": "warning",
                "title": "⚠️ Anemia of Chronic Disease Pattern",
                "body_en": (
                    f"Fe ↓ ({fe}) + TIBC ↓ ({tibc}) + Ferritin ↑ ({ferritin}) = Anemia of chronic disease.\n"
                    "Common in: chronic infections, malignancy, autoimmune disease, CKD."
                ),
                "body_ar": f"حديد منخفض + TIBC منخفض + فيريتين مرتفع = فقر دم الأمراض المزمنة.\nشائع في: التهابات مزمنة، سرطان.",
                "references": ["ASH 2023", "KDIGO Anemia Guidelines"]
            })
        elif fe > 170 and sat > 45 and ferritin > 300:
            insights.append({
                "category": "Iron", "severity": "critical",
                "title": "🔴 Iron Overload — Rule Out Hemochromatosis",
                "body_en": (
                    f"Fe ↑ ({fe}) + Sat {sat:.0f}% (>45%) + Ferritin ↑ ({ferritin}) = Iron overload.\n"
                    "Rule out hereditary hemochromatosis (HFE gene mutation).\n"
                    "Recommendation: HFE genetic testing, liver imaging, LFTs."
                ),
                "body_ar": f"حديد مرتفع + تشبع مرتفع + فيريتين مرتفع = تراكم الحديد.\nيُشك في داء ترسب الأصبغة الدموية.",
                "references": ["EASL Hemochromatosis 2022"]
            })
        elif ferritin > 300 and fe <= 170:
            insights.append({
                "category": "Iron", "severity": "info",
                "title": "ℹ️ Elevated Ferritin — Likely Acute Phase Reactant",
                "body_en": (
                    f"Ferritin {ferritin} ng/mL elevated but serum iron {fe} is normal.\n"
                    "Ferritin rises in: infection/inflammation, liver disease, malignancy, metabolic syndrome.\n"
                    "Isolated elevated ferritin ≠ iron overload. Check CRP/ESR."
                ),
                "body_ar": f"فيريتين مرتفع ({ferritin}) مع حديد طبيعي = بروتين الطور الحاد.\nتحقق من CRP وESR.",
                "references": ["BSH Ferritin Guidelines 2023"]
            })

    # ── 7. CBC Patterns ───────────────────────────────────────────────────────
    if has("Hgb", "MCV"):
        hgb, mcv = val("Hgb"), val("MCV")
        hgb_low = (sex == "male" and hgb < 13.5) or (sex == "female" and hgb < 12.0) or (sex == "unspecified" and hgb < 12.0)

        if hgb_low and mcv < 80 and has("RDW"):
            rdw = val("RDW")
            if rdw > 14.5:
                insights.append({
                    "category": "CBC", "severity": "warning",
                    "title": "⚠️ Microcytic Anemia + High RDW — Likely Iron Deficiency",
                    "body_en": (
                        f"Hgb {hgb} g/dL (↓) + MCV {mcv} fL (microcytic) + RDW {rdw}% (↑).\n"
                        "High RDW with microcytosis = IDA pattern. "
                        "Thalassemia trait typically has NORMAL RDW.\n"
                        "Recommendation: Iron studies (Fe, TIBC, Ferritin)."
                    ),
                    "body_ar": f"Hgb منخفض + MCV صغير + RDW مرتفع = فقر دم بنقص الحديد (على الأرجح).\nيُنصح: دراسات الحديد.",
                    "references": ["Bessman Index", "WHO Anemia 2023"]
                })
            else:
                insights.append({
                    "category": "CBC", "severity": "info",
                    "title": "ℹ️ Microcytic Anemia + Normal RDW — Consider Thalassemia Trait",
                    "body_en": (
                        f"Hgb {hgb} g/dL (↓) + MCV {mcv} fL (microcytic) + RDW {rdw}% (normal).\n"
                        "Normal RDW with microcytosis suggests thalassemia trait over IDA.\n"
                        "Recommendation: Hemoglobin electrophoresis, iron studies."
                    ),
                    "body_ar": f"Hgb منخفض + MCV صغير + RDW طبيعي = محتمل الثلاسيميا الحاملة.\nيُنصح: كهربة الهيموجلوبين.",
                    "references": ["Mentzer Index", "BSH Thalassemia 2023"]
                })

        if hgb_low and mcv > 100:
            insights.append({
                "category": "CBC", "severity": "warning",
                "title": "⚠️ Macrocytic Anemia — B12/Folate Deficiency?",
                "body_en": (
                    f"Hgb {hgb} g/dL (↓) + MCV {mcv} fL (macrocytic).\n"
                    "Differential: B12 deficiency, folate deficiency, alcohol, hypothyroidism, "
                    "medications (methotrexate, hydroxyurea), MDS.\n"
                    "Recommendation: B12, folate, reticulocytes, peripheral blood film."
                ),
                "body_ar": f"Hgb منخفض + MCV كبير = فقر دم كبير الكريات.\nالأسباب: نقص B12 أو حمض الفوليك.\nيُنصح: B12، فولات، فيلم دم محيطي.",
                "references": ["BSH B12/Folate 2024"]
            })

    if has("WBC", "Neutrophils", "Lymphocytes"):
        wbc = val("WBC")
        neut_abs  = wbc * val("Neutrophils")  / 100
        lymph_abs = wbc * val("Lymphocytes") / 100

        if wbc > 11 and neut_abs > 7.5:
            insights.append({
                "category": "CBC", "severity": "info",
                "title": "ℹ️ Neutrophilia — Bacterial Infection / Stress Response",
                "body_en": (
                    f"WBC {wbc} ×10³/µL (↑), absolute neutrophils {neut_abs:.1f}.\n"
                    "Common causes: bacterial infection, physiologic stress, corticosteroids, smoking.\n"
                    "If severe (>30): consider leukemoid reaction or CML."
                ),
                "body_ar": f"WBC مرتفع مع نيوتروفيليا ({neut_abs:.1f} ×10³) = كريات بيضاء جرثومي محتمل.\nلو WBC > 30: استبعد CML.",
                "references": ["Henry's 23rd Ed"]
            })

        if wbc < 4.5 and neut_abs < 1.8:
            severity = "critical" if neut_abs < 0.5 else "warning"
            grade    = "Severe (Agranulocytosis)" if neut_abs < 0.5 else "Moderate" if neut_abs < 1.0 else "Mild"
            insights.append({
                "category": "CBC", "severity": severity,
                "title": f"{'🔴' if severity=='critical' else '⚠️'} Neutropenia — {grade}",
                "body_en": (
                    f"ANC = {neut_abs:.2f} ×10³/µL. Grade: {grade}.\n"
                    "Causes: viral infection, drug-induced (chemo, carbimazole, clozapine), B12/folate deficiency.\n"
                    + ("⚠️ URGENT: Life-threatening infection risk. Reverse isolation!" if neut_abs < 0.5 else
                       "Monitor closely, review medications.")
                ),
                "body_ar": (
                    f"ANC = {neut_abs:.2f} — نقص النيوتروفيل ({grade}).\n"
                    + ("خطر عدوى شديد جداً — عزل عكسي عاجل!" if neut_abs < 0.5 else "مراقبة دقيقة.")
                ),
                "references": ["CTCAE Grading", "IDSA Febrile Neutropenia 2024"]
            })

        if wbc > 11 and lymph_abs > 4.0:
            insights.append({
                "category": "CBC", "severity": "info",
                "title": "ℹ️ Lymphocytosis — Viral Infection / CLL?",
                "body_en": (
                    f"Absolute lymphocytes = {lymph_abs:.1f} ×10³/µL (↑).\n"
                    "Causes: viral infections (EBV, CMV, COVID-19), whooping cough, CLL (if persistent >5.0).\n"
                    "Recommendation: peripheral film, flow cytometry if persistent."
                ),
                "body_ar": f"لمفاويات مرتفعة ({lymph_abs:.1f} ×10³) = عدوى فيروسية محتملة أو CLL.",
                "references": ["WHO CLL Guidelines"]
            })

    # ── 8. Multi-organ correlations ───────────────────────────────────────────
    if has("ALT", "Creatinine"):
        alt, cr = val("ALT"), val("Creatinine")
        albumin = val("Albumin") if has("Albumin") else None
        if (alt > 56 or (albumin and albumin < 3.5)) and cr > 1.5:
            insights.append({
                "category": "Multi-organ", "severity": "warning",
                "title": "⚠️ Combined Liver + Kidney Dysfunction",
                "body_en": (
                    f"Elevated ALT ({alt} U/L) with elevated Creatinine ({cr} mg/dL).\n"
                    "Consider: hepatorenal syndrome (HRS), sepsis-related multi-organ dysfunction, "
                    "shock (ischemic hepatitis + AKI), drug/toxin (paracetamol, NSAIDs)."
                ),
                "body_ar": "ارتفاع إنزيمات الكبد مع ارتفاع الكرياتينين = خلل كبدي كلوي مشترك.\nيُشك في: HRS، صدمة، أو سمية دواء.",
                "references": ["EASL 2023", "KDIGO AKI 2024"]
            })

    if has("HbA1c", "Creatinine"):
        hba1c, cr = val("HbA1c"), val("Creatinine")
        if hba1c >= 6.5 and cr > 1.2:
            insights.append({
                "category": "Multi-organ", "severity": "warning",
                "title": "⚠️ Diabetic Nephropathy Risk — Poor Glycemic Control + Renal Impairment",
                "body_en": (
                    f"HbA1c {hba1c}% (diabetic) + Creatinine {cr} mg/dL (elevated).\n"
                    "Consider diabetic nephropathy.\n"
                    "Essential workup: urine ACR, eGFR trend, BP control, fundoscopy."
                ),
                "body_ar": f"HbA1c مرتفع ({hba1c}%) + كرياتينين مرتفع ({cr}) = خطر اعتلال الكلى السكري.\nيُنصح: نسبة ألبومين/كرياتينين في البول (ACR).",
                "references": ["ADA Microvascular Complications 2025", "KDIGO Diabetes-CKD 2024"]
            })

    return insights

# =============================================================================
# SECTION 3: GEMINI OCR
# =============================================================================

EXTRACTION_PROMPT = """You are an expert clinical laboratory scientist.
Extract ALL numerical lab results from this lab report image.
Return ONLY a valid JSON object — no preamble, no markdown, no backticks.

Map results to these EXACT keys:
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

Example output: {"FBG": 126.0, "HbA1c": 7.2, "Creatinine": 1.1, "ALT": 45}
Include ONLY tests with clear numerical values."""


def extract_results_from_image(image_bytes: bytes, api_key: str) -> dict:
    try:
        import google.generativeai as genai
    except ImportError:
        st.error("⚠️ Run: pip install google-generativeai")
        return {}
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        pil_image = Image.open(io.BytesIO(image_bytes))
        response  = model.generate_content([EXTRACTION_PROMPT, pil_image])
        raw = re.sub(r"```json|```", "", response.text.strip()).strip()
        data = json.loads(raw)
        return {k: float(v) for k, v in data.items() if isinstance(v, (int, float)) or str(v).replace('.','').isdigit()}
    except json.JSONDecodeError as e:
        st.error(f"⚠️ JSON parse error: {e}")
        return {}
    except Exception as e:
        st.error(f"⚠️ Gemini OCR error: {e}")
        return {}

# =============================================================================
# SECTION 4: STREAMLIT UI
# =============================================================================

st.set_page_config(
    page_title="Orange Lab Results Analyzer",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  .main-header {
    background: linear-gradient(135deg, #FF6B35 0%, #FF8C5A 50%, #FFB347 100%);
    padding: 1.5rem 2rem; border-radius: 16px; margin-bottom: 1.5rem;
    text-align: center; box-shadow: 0 4px 20px rgba(255,107,53,0.35);
  }
  .main-header h1 { color: white; font-size: 2rem; font-weight: 800; margin: 0; }
  .main-header p  { color: rgba(255,255,255,0.9); margin: 0.3rem 0 0; font-size: 0.95rem; }

  .insight-critical { background: linear-gradient(135deg,#1a0505,#2d0a0a); border:1px solid #ff4444; border-left:5px solid #ff4444; border-radius:10px; padding:1rem 1.2rem; margin:0.6rem 0; }
  .insight-warning  { background: linear-gradient(135deg,#1a1200,#2d1f00); border:1px solid #ffaa00; border-left:5px solid #ffaa00; border-radius:10px; padding:1rem 1.2rem; margin:0.6rem 0; }
  .insight-info     { background: linear-gradient(135deg,#001a2d,#002d4d); border:1px solid #0088ff; border-left:5px solid #0088ff; border-radius:10px; padding:1rem 1.2rem; margin:0.6rem 0; }

  .summary-box { background:#1a1d24; border:1px solid #2a2d35; border-radius:12px; padding:1rem; margin-bottom:1rem; text-align:center; }
  .kpi-number  { font-size:2rem; font-weight:800; }
  .kpi-label   { font-size:0.8rem; color:#888; margin-top:-0.3rem; }

  .panel-header { background:linear-gradient(90deg,rgba(255,107,53,0.15),transparent); border-left:4px solid #FF6B35; padding:0.4rem 0.8rem; border-radius:0 8px 8px 0; margin:1rem 0 0.5rem; font-weight:700; font-size:1rem; color:#FF8C5A; }
  .arabic-note  { direction:rtl; text-align:right; font-size:0.85rem; color:#aaa; border-top:1px solid #333; margin-top:0.5rem; padding-top:0.5rem; }

  .stTabs [data-baseweb="tab-list"] { background:#1a1d24; border-radius:10px; gap:4px; padding:4px; }
  .stTabs [data-baseweb="tab"]      { border-radius:8px; font-weight:600; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
  <h1>🧬 Orange Lab Results Analyzer</h1>
  <p>Clinical Intelligence Engine — Cross-validation & Pattern Recognition</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 👤 Patient Info")
    patient_name = st.text_input("Patient Name", placeholder="Optional")
    c1, c2 = st.columns(2)
    with c1: sex = st.selectbox("Sex", ["unspecified", "male", "female"])
    with c2:
        age = st.number_input("Age", 0, 120, 0, 1)
        age = age if age > 0 else None

    st.markdown("---")
    st.markdown("### 🔑 Gemini API Key (OCR)")
    api_key = st.text_input("API Key", type="password", placeholder="AIza...",
                             help="Free from aistudio.google.com — 1500 req/day")

    st.markdown("---")
    st.markdown("### 📋 Select Panels")
    selected_panels = [p for p in PANELS if st.checkbox(p, value=False)]

    st.markdown("---")
    st.caption("📚 ADA 2025 | KDIGO | EASL | ACC/AHA | Tietz 7th | Henry's 23rd")

# ── Input Tabs ────────────────────────────────────────────────────────────────
tab_manual, tab_ocr = st.tabs(["📝 Manual Entry", "📷 Upload Image (OCR)"])
results = {}

with tab_manual:
    if not selected_panels:
        st.info("👈 Select panels from the sidebar to start.")
    else:
        for panel_name in selected_panels:
            st.markdown(f'<div class="panel-header">🔬 {panel_name}</div>', unsafe_allow_html=True)
            cols = st.columns(3)
            for i, key in enumerate(PANELS[panel_name]):
                ref = REFERENCE_RANGES[key]
                with cols[i % 3]:
                    v = st.number_input(
                        f"{ref['label']} ({ref['unit']})",
                        min_value=0.0, max_value=9999.0, value=0.0,
                        step=0.1, format="%.2f", key=f"m_{key}",
                        help=f"عربي: {ref['label_ar']}"
                    )
                    if v > 0:
                        results[key] = v

with tab_ocr:
    st.markdown("Upload a lab report image — Gemini Vision extracts all values automatically.")
    uploaded = st.file_uploader("Upload lab report", type=["jpg","jpeg","png","webp"])

    if uploaded:
        img_bytes = uploaded.read()
        c_img, c_act = st.columns([2, 1])
        with c_img:
            st.image(img_bytes, caption="Uploaded Report", use_container_width=True)
        with c_act:
            st.markdown("### Extract Results")
            if not api_key:
                st.warning("⚠️ Enter Gemini API key in the sidebar.")
            else:
                if st.button("🔍 Extract with AI", type="primary", use_container_width=True):
                    with st.spinner("Gemini Vision is reading the report..."):
                        ocr_out = extract_results_from_image(img_bytes, api_key)
                    if ocr_out:
                        st.success(f"✅ Extracted {len(ocr_out)} test(s)!")
                        st.session_state["ocr_results"] = ocr_out
                    else:
                        st.error("Could not extract results. Try a clearer image.")

    if st.session_state.get("ocr_results"):
        ocr_data = st.session_state["ocr_results"]
        st.markdown("### ✏️ Extracted Values — Review & Edit")
        ocr_cols = st.columns(3)
        for i, (key, raw_val) in enumerate(ocr_data.items()):
            if key not in REFERENCE_RANGES:
                continue
            ref = REFERENCE_RANGES[key]
            with ocr_cols[i % 3]:
                edited = st.number_input(
                    f"{ref['label']} ({ref['unit']})",
                    min_value=0.0, max_value=9999.0,
                    value=float(raw_val), step=0.1, format="%.2f",
                    key=f"ocr_{key}"
                )
                if edited > 0:
                    results[key] = edited

# ── Analysis Button ───────────────────────────────────────────────────────────
st.markdown("---")
c_btn, c_clr = st.columns([3, 1])
with c_btn:
    run_analysis = st.button("🚀 Run Clinical Analysis", type="primary",
                              use_container_width=True, disabled=(len(results) == 0))
with c_clr:
    if st.button("🗑️ Clear All", use_container_width=True):
        st.session_state.pop("ocr_results", None)
        st.rerun()

# ── Results ───────────────────────────────────────────────────────────────────
if run_analysis and results:
    st.markdown("---")
    pt   = f"**{patient_name}**" if patient_name else "Patient"
    sx   = f" | {sex.capitalize()}" if sex != "unspecified" else ""
    ag   = f" | Age: {age}" if age else ""
    st.markdown(f"## 📊 Analysis Results — {pt}{sx}{ag}")

    # Flags
    flags = [flag_single_test(k, v, sex) for k, v in results.items() if flag_single_test(k, v, sex)]
    n_high   = sum(1 for f in flags if f["status"] == "high")
    n_low    = sum(1 for f in flags if f["status"] == "low")
    n_normal = sum(1 for f in flags if f["status"] == "normal")

    k1, k2, k3, k4 = st.columns(4)
    for col, num, label, color in [
        (k1, len(flags), "Tests Analyzed", "#aaa"),
        (k2, n_high,     "High",           "#ff6b6b"),
        (k3, n_low,      "Low",            "#74b9ff"),
        (k4, n_normal,   "Normal",         "#55efc4"),
    ]:
        col.markdown(
            f'<div class="summary-box"><div class="kpi-number" style="color:{color}">{num}</div>'
            f'<div class="kpi-label">{label}</div></div>',
            unsafe_allow_html=True
        )

    # Results table by category
    st.markdown("### 🔬 Individual Test Results")
    cats = {}
    for f in flags:
        cats.setdefault(f["category"], []).append(f)

    for cat, cat_flags in cats.items():
        with st.expander(f"**{cat}** ({len(cat_flags)} tests)", expanded=True):
            rows = []
            for f in cat_flags:
                icon = "🔴" if f["status"]=="high" else "🔵" if f["status"]=="low" else "🟢"
                rows.append({
                    "Test": f["label"], "Arabic": f["label_ar"],
                    "Value": f"{f['value']:.2f}", "Unit": f["unit"],
                    "Status": f"{icon} {f['status'].capitalize()}",
                    "Reference": f["range_label"],
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # Cross-validation insights
    st.markdown("---")
    st.markdown("### 🧠 Clinical Intelligence — Cross-validation Insights")
    insights = run_cross_validation(results, sex=sex, age=age)

    if not insights:
        st.success("✅ No significant cross-validation alerts. Results appear internally consistent.")
    else:
        sev_order = {"critical": 0, "warning": 1, "info": 2}
        insights.sort(key=lambda x: sev_order.get(x["severity"], 3))
        nc = sum(1 for i in insights if i["severity"]=="critical")
        nw = sum(1 for i in insights if i["severity"]=="warning")
        ni = sum(1 for i in insights if i["severity"]=="info")
        st.markdown(f"**{len(insights)} insight(s):** 🔴 {nc} Critical | ⚠️ {nw} Warning | ℹ️ {ni} Info")

        for ins in insights:
            with st.expander(ins["title"], expanded=(ins["severity"]=="critical")):
                st.markdown(f'<div class="insight-{ins["severity"]}">', unsafe_allow_html=True)
                st.markdown("**📋 Clinical Interpretation:**")
                st.markdown(ins["body_en"])
                st.markdown(f'<div class="arabic-note">📝 {ins["body_ar"]}</div>', unsafe_allow_html=True)
                if ins.get("references"):
                    st.markdown(f"<small>📚 {' | '.join(ins['references'])}</small>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.caption("⚕️ Clinical Disclaimer: Decision support only. Interpret in clinical context by a qualified physician.")
    st.caption("📚 ADA 2025 | KDIGO 2024 | EASL 2023 | ACC/AHA 2024 | Tietz 7th Ed | Henry's 23rd Ed | WHO/ICSH")

st.markdown("---")
st.markdown('<div style="text-align:center;color:#555;font-size:0.8rem;">🧡 Orange Lab Results Analyzer | 6th October City, Giza, Egypt</div>', unsafe_allow_html=True)
