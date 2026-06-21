"""
╔══════════════════════════════════════════════════════════════════╗
║         Orange Lab Results Analyzer v2.0                        ║
║         Clinical Intelligence Engine for Lab Reports            ║
║         © Orange Lab — 6th October City, Giza, Egypt            ║
╚══════════════════════════════════════════════════════════════════╝

References:
  - Tietz Clinical Chemistry & Molecular Diagnostics, 7th Ed.
  - Henry's Clinical Diagnosis and Management, 23rd Ed.
  - ADA Standards of Medical Care 2025
  - KDIGO CKD/AKI Guidelines 2024
  - EASL Clinical Practice Guidelines 2023
  - ACC/AHA Cardiovascular Guidelines 2024
  - ATA Thyroid Guidelines 2024
  - ESC Heart Failure/ACS Guidelines 2023
  - IDSA Infectious Disease Guidelines 2024
  - WHO/ICSH Hematology Standards
  - Endocrine Society Vitamin D Guidelines 2024
  - AACE Calcium/Bone Guidelines 2022
"""

import streamlit as st
import pandas as pd

# =============================================================================
# SECTION 1: REFERENCE RANGES DATABASE
# =============================================================================
# Structure per key:
#   label       : English name
#   label_ar    : Arabic name
#   unit        : reporting unit
#   lo / hi     : general reference range (used if no sex-specific)
#   lo_m / hi_m : male-specific range (optional)
#   lo_f / hi_f : female-specific range (optional)
#   category    : display grouping
# =============================================================================

REF = {
    # ── GLUCOSE & DIABETES ───────────────────────────────────────────────────
    "FBG":          {"label":"Fasting Blood Glucose",               "label_ar":"سكر الصيام",                          "unit":"mg/dL",          "lo":70,    "hi":99,    "category":"Glucose"},
    "RBG":          {"label":"Random Blood Glucose",                "label_ar":"سكر عشوائي",                          "unit":"mg/dL",          "lo":0,     "hi":139,   "category":"Glucose"},
    "PP2h":         {"label":"2h Post-prandial Glucose",            "label_ar":"سكر ما بعد الأكل (2 ساعة)",           "unit":"mg/dL",          "lo":0,     "hi":139,   "category":"Glucose"},
    "HbA1c":        {"label":"Glycated Hemoglobin A1c",             "label_ar":"السكر التراكمي HbA1c",                "unit":"%",              "lo":0,     "hi":5.6,   "category":"Glucose"},
    "Insulin":      {"label":"Fasting Insulin",                     "label_ar":"الأنسولين الصيامي",                   "unit":"µIU/mL",         "lo":2.6,   "hi":24.9,  "category":"Glucose"},
    "Fructosamine": {"label":"Fructosamine",                        "label_ar":"فركتوزامين",                           "unit":"µmol/L",         "lo":190,   "hi":280,   "category":"Glucose"},
    "Cpeptide":     {"label":"C-Peptide",                           "label_ar":"الببتيد C",                            "unit":"ng/mL",          "lo":0.8,   "hi":3.1,   "category":"Glucose"},
    "GAD65":        {"label":"GAD-65 Antibodies",                   "label_ar":"أجسام مضادة GAD-65",                  "unit":"U/mL",           "lo":0,     "hi":5,     "category":"Glucose"},

    # ── KIDNEY FUNCTION ──────────────────────────────────────────────────────
    "Creatinine":   {"label":"Serum Creatinine",                    "label_ar":"كرياتينين الدم",                      "unit":"mg/dL",          "lo":0.5,   "hi":1.2,   "lo_m":0.7, "hi_m":1.2, "lo_f":0.5, "hi_f":1.0, "category":"Kidney"},
    "Urea":         {"label":"Blood Urea Nitrogen (BUN)",           "label_ar":"يوريا الدم (BUN)",                    "unit":"mg/dL",          "lo":7,     "hi":20,    "category":"Kidney"},
    "UricAcid":     {"label":"Uric Acid",                           "label_ar":"حمض اليوريك",                         "unit":"mg/dL",          "lo":2.4,   "hi":7.0,   "lo_m":3.4, "hi_m":7.0, "lo_f":2.4, "hi_f":6.0, "category":"Kidney"},
    "eGFR":         {"label":"Estimated GFR (CKD-EPI)",             "label_ar":"معدل الترشيح الكبيبي",               "unit":"mL/min/1.73m²",  "lo":90,    "hi":999,   "category":"Kidney"},
    "CystatinC":    {"label":"Cystatin C",                          "label_ar":"سيستاتين C",                           "unit":"mg/L",           "lo":0.53,  "hi":0.95,  "category":"Kidney"},
    "uACR":         {"label":"Urine Albumin:Creatinine Ratio",      "label_ar":"نسبة ألبومين/كرياتينين البول",        "unit":"mg/g",           "lo":0,     "hi":30,    "category":"Kidney"},
    "uProtein24h":  {"label":"Urine Total Protein (24h)",           "label_ar":"بروتين البول الكلي (24 ساعة)",        "unit":"mg/24h",         "lo":0,     "hi":150,   "category":"Kidney"},
    "Beta2MG_k":    {"label":"β2-Microglobulin (Kidney)",           "label_ar":"بيتا-2 ميكروجلوبيولين (كلوي)",       "unit":"mg/L",           "lo":0,     "hi":2.0,   "category":"Kidney"},
    "Phosphorus_k": {"label":"Serum Phosphorus",                    "label_ar":"فوسفور الدم",                          "unit":"mg/dL",          "lo":2.5,   "hi":4.5,   "category":"Kidney"},
    "PTH_k":        {"label":"Parathyroid Hormone (iPTH)",          "label_ar":"هرمون الجارة الدرقية (iPTH)",         "unit":"pg/mL",          "lo":15,    "hi":65,    "category":"Kidney"},

    # ── LIVER FUNCTION ───────────────────────────────────────────────────────
    "ALT":          {"label":"Alanine Aminotransferase (ALT)",      "label_ar":"إنزيم الكبد ALT",                     "unit":"U/L",            "lo":7,     "hi":56,    "lo_m":7,   "hi_m":56,  "lo_f":7,   "hi_f":45,  "category":"Liver"},
    "AST":          {"label":"Aspartate Aminotransferase (AST)",    "label_ar":"إنزيم الكبد AST",                     "unit":"U/L",            "lo":10,    "hi":40,    "lo_m":10,  "hi_m":40,  "lo_f":10,  "hi_f":35,  "category":"Liver"},
    "ALP":          {"label":"Alkaline Phosphatase (ALP)",          "label_ar":"الفوسفاتاز القلوي",                   "unit":"U/L",            "lo":44,    "hi":147,   "category":"Liver"},
    "GGT":          {"label":"Gamma-GT (GGT)",                      "label_ar":"إنزيم GGT",                           "unit":"U/L",            "lo":5,     "hi":61,    "lo_m":8,   "hi_m":61,  "lo_f":5,   "hi_f":36,  "category":"Liver"},
    "TBili":        {"label":"Total Bilirubin",                     "label_ar":"البيليروبين الكلي",                   "unit":"mg/dL",          "lo":0.2,   "hi":1.2,   "category":"Liver"},
    "DBili":        {"label":"Direct Bilirubin",                    "label_ar":"البيليروبين المباشر",                 "unit":"mg/dL",          "lo":0.0,   "hi":0.3,   "category":"Liver"},
    "IBili":        {"label":"Indirect Bilirubin",                  "label_ar":"البيليروبين غير المباشر",             "unit":"mg/dL",          "lo":0.2,   "hi":0.9,   "category":"Liver"},
    "Albumin":      {"label":"Serum Albumin",                       "label_ar":"الألبومين",                           "unit":"g/dL",           "lo":3.5,   "hi":5.0,   "category":"Liver"},
    "TotalProt":    {"label":"Total Protein",                       "label_ar":"البروتين الكلي",                      "unit":"g/dL",           "lo":6.3,   "hi":8.2,   "category":"Liver"},
    "LDH":          {"label":"Lactate Dehydrogenase (LDH)",         "label_ar":"إنزيم LDH",                           "unit":"U/L",            "lo":140,   "hi":280,   "category":"Liver"},
    "PT":           {"label":"Prothrombin Time (PT)",               "label_ar":"وقت البروثرومبين",                    "unit":"sec",            "lo":11,    "hi":13.5,  "category":"Liver"},
    "INR":          {"label":"INR",                                 "label_ar":"النسبة الدولية المعيارية INR",         "unit":"ratio",          "lo":0.8,   "hi":1.2,   "category":"Liver"},
    "APTT":         {"label":"Activated Partial Thromboplastin Time","label_ar":"aPTT",                               "unit":"sec",            "lo":25,    "hi":35,    "category":"Liver"},
    "AFP_liver":    {"label":"Alpha-Fetoprotein (AFP)",             "label_ar":"ألفا فيتوبروتين",                     "unit":"ng/mL",          "lo":0,     "hi":8.5,   "category":"Liver"},

    # ── LIPIDS ───────────────────────────────────────────────────────────────
    "TC":           {"label":"Total Cholesterol",                   "label_ar":"الكوليسترول الكلي",                   "unit":"mg/dL",          "lo":0,     "hi":199,   "category":"Lipids"},
    "TG":           {"label":"Triglycerides",                       "label_ar":"الدهون الثلاثية",                     "unit":"mg/dL",          "lo":0,     "hi":149,   "category":"Lipids"},
    "LDL":          {"label":"LDL Cholesterol",                     "label_ar":"الكوليسترول الضار LDL",               "unit":"mg/dL",          "lo":0,     "hi":99,    "category":"Lipids"},
    "HDL":          {"label":"HDL Cholesterol",                     "label_ar":"الكوليسترول المفيد HDL",              "unit":"mg/dL",          "lo":40,    "hi":999,   "lo_m":40,  "hi_m":999, "lo_f":50,  "hi_f":999, "category":"Lipids"},
    "nonHDL":       {"label":"Non-HDL Cholesterol",                 "label_ar":"كوليسترول غير HDL",                   "unit":"mg/dL",          "lo":0,     "hi":130,   "category":"Lipids"},
    "VLDL":         {"label":"VLDL Cholesterol",                    "label_ar":"كوليسترول VLDL",                      "unit":"mg/dL",          "lo":2,     "hi":30,    "category":"Lipids"},
    "Lpa":          {"label":"Lipoprotein(a)",                      "label_ar":"ليبوبروتين (أ)",                       "unit":"mg/dL",          "lo":0,     "hi":30,    "category":"Lipids"},
    "ApoA1":        {"label":"Apolipoprotein A-I",                  "label_ar":"أبوليبوبروتين A-I",                   "unit":"mg/dL",          "lo":119,   "hi":240,   "lo_m":119, "hi_m":240, "lo_f":140, "hi_f":260, "category":"Lipids"},
    "ApoB":         {"label":"Apolipoprotein B",                    "label_ar":"أبوليبوبروتين B",                     "unit":"mg/dL",          "lo":52,    "hi":109,   "category":"Lipids"},

    # ── THYROID ──────────────────────────────────────────────────────────────
    "TSH":          {"label":"TSH",                                 "label_ar":"هرمون الغدة الدرقية TSH",             "unit":"µIU/mL",         "lo":0.4,   "hi":4.0,   "category":"Thyroid"},
    "FT4":          {"label":"Free T4 (FT4)",                       "label_ar":"الثيروكسين الحر FT4",                 "unit":"ng/dL",          "lo":0.8,   "hi":1.8,   "category":"Thyroid"},
    "FT3":          {"label":"Free T3 (FT3)",                       "label_ar":"الثيرونين الحر FT3",                  "unit":"pg/mL",          "lo":2.3,   "hi":4.2,   "category":"Thyroid"},
    "TT4":          {"label":"Total T4",                            "label_ar":"الثيروكسين الكلي TT4",                "unit":"µg/dL",          "lo":5.0,   "hi":12.0,  "category":"Thyroid"},
    "TT3":          {"label":"Total T3",                            "label_ar":"الثيرونين الكلي TT3",                 "unit":"ng/dL",          "lo":80,    "hi":200,   "category":"Thyroid"},
    "AntiTPO":      {"label":"Anti-TPO Antibodies",                 "label_ar":"أجسام مضادة TPO",                     "unit":"IU/mL",          "lo":0,     "hi":34,    "category":"Thyroid"},
    "AntiTG":       {"label":"Anti-Thyroglobulin Antibodies",       "label_ar":"أجسام مضادة ثيروجلوبيولين",           "unit":"IU/mL",          "lo":0,     "hi":115,   "category":"Thyroid"},
    "TRAb":         {"label":"TSH Receptor Antibodies (TRAb)",      "label_ar":"أجسام مضادة مستقبلات TSH",            "unit":"IU/L",           "lo":0,     "hi":1.75,  "category":"Thyroid"},
    "Thyroglobulin":{"label":"Thyroglobulin",                       "label_ar":"ثيروجلوبيولين",                        "unit":"ng/mL",          "lo":1.4,   "hi":29.2,  "category":"Thyroid"},

    # ── IRON STUDIES ─────────────────────────────────────────────────────────
    "SerumFe":      {"label":"Serum Iron",                          "label_ar":"حديد الدم",                           "unit":"µg/dL",          "lo":50,    "hi":175,   "lo_m":65,  "hi_m":175, "lo_f":50,  "hi_f":170, "category":"Iron"},
    "TIBC":         {"label":"Total Iron Binding Capacity (TIBC)",  "label_ar":"طاقة ربط الحديد الكلية TIBC",        "unit":"µg/dL",          "lo":250,   "hi":370,   "category":"Iron"},
    "UIBC":         {"label":"Unsaturated Iron Binding Capacity",   "label_ar":"طاقة ربط الحديد غير المشبعة",        "unit":"µg/dL",          "lo":110,   "hi":370,   "category":"Iron"},
    "TfSat":        {"label":"Transferrin Saturation (%)",          "label_ar":"نسبة تشبع الترانسفيرين",             "unit":"%",              "lo":20,    "hi":50,    "category":"Iron"},
    "Ferritin":     {"label":"Serum Ferritin",                      "label_ar":"فيريتين الدم",                        "unit":"ng/mL",          "lo":11,    "hi":336,   "lo_m":24,  "hi_m":336, "lo_f":11,  "hi_f":307, "category":"Iron"},
    "Transferrin":  {"label":"Serum Transferrin",                   "label_ar":"ترانسفيرين الدم",                     "unit":"mg/dL",          "lo":200,   "hi":360,   "category":"Iron"},
    "sTfR":         {"label":"Soluble Transferrin Receptor",        "label_ar":"مستقبل الترانسفيرين الذائب",          "unit":"mg/L",           "lo":0.83,  "hi":1.76,  "category":"Iron"},

    # ── BONE METABOLISM ──────────────────────────────────────────────────────
    "CalciumT":     {"label":"Total Calcium",                       "label_ar":"الكالسيوم الكلي",                     "unit":"mg/dL",          "lo":8.5,   "hi":10.5,  "category":"Bone"},
    "CalciumI":     {"label":"Ionized Calcium",                     "label_ar":"الكالسيوم المتأين",                   "unit":"mg/dL",          "lo":4.65,  "hi":5.28,  "category":"Bone"},
    "Phosphorus":   {"label":"Serum Phosphorus",                    "label_ar":"الفوسفور",                            "unit":"mg/dL",          "lo":2.5,   "hi":4.5,   "category":"Bone"},
    "Magnesium":    {"label":"Serum Magnesium",                     "label_ar":"المغنيسيوم",                          "unit":"mg/dL",          "lo":1.7,   "hi":2.4,   "category":"Bone"},
    "VitD25":       {"label":"25-OH Vitamin D",                     "label_ar":"فيتامين د 25-OH",                     "unit":"ng/mL",          "lo":30,    "hi":100,   "category":"Bone"},
    "VitD125":      {"label":"1,25-(OH)₂ Vitamin D (Calcitriol)",   "label_ar":"الكالسيتريول",                        "unit":"pg/mL",          "lo":18,    "hi":72,    "category":"Bone"},
    "PTH_bone":     {"label":"Parathyroid Hormone (intact PTH)",    "label_ar":"هرمون الجارة الدرقية iPTH",           "unit":"pg/mL",          "lo":15,    "hi":65,    "category":"Bone"},
    "Osteocalcin":  {"label":"Osteocalcin",                         "label_ar":"أوستيوكالسين",                        "unit":"ng/mL",          "lo":3.1,   "hi":13.7,  "lo_m":3.1, "hi_m":13.7,"lo_f":0.4, "hi_f":7.9, "category":"Bone"},
    "CTX":          {"label":"CTX (C-Terminal Telopeptide)",        "label_ar":"علامة ارتشاف العظام CTX",             "unit":"ng/mL",          "lo":0,     "hi":0.573, "category":"Bone"},
    "NTX":          {"label":"NTX (N-Terminal Telopeptide)",        "label_ar":"علامة ارتشاف العظام NTX",             "unit":"nM BCE/L",       "lo":0,     "hi":65,    "category":"Bone"},

    # ── ELECTROLYTES ─────────────────────────────────────────────────────────
    "Sodium":       {"label":"Serum Sodium (Na⁺)",                 "label_ar":"صوديوم الدم",                         "unit":"mEq/L",          "lo":136,   "hi":145,   "category":"Electrolytes"},
    "Potassium":    {"label":"Serum Potassium (K⁺)",               "label_ar":"بوتاسيوم الدم",                       "unit":"mEq/L",          "lo":3.5,   "hi":5.0,   "category":"Electrolytes"},
    "Chloride":     {"label":"Serum Chloride (Cl⁻)",               "label_ar":"كلوريد الدم",                         "unit":"mEq/L",          "lo":98,    "hi":106,   "category":"Electrolytes"},
    "Bicarbonate":  {"label":"Serum Bicarbonate (HCO₃⁻)",          "label_ar":"بيكربونات الدم",                      "unit":"mEq/L",          "lo":22,    "hi":29,    "category":"Electrolytes"},
    "Osmolality":   {"label":"Serum Osmolality",                   "label_ar":"أسمولالية الدم",                       "unit":"mOsm/kg",        "lo":275,   "hi":295,   "category":"Electrolytes"},

    # ── CARDIAC MARKERS ──────────────────────────────────────────────────────
    "cTnI":         {"label":"Cardiac Troponin I (cTnI)",           "label_ar":"تروبونين القلب I",                    "unit":"ng/mL",          "lo":0,     "hi":0.04,  "category":"Cardiac"},
    "cTnT":         {"label":"Cardiac Troponin T (cTnT)",           "label_ar":"تروبونين القلب T",                    "unit":"ng/mL",          "lo":0,     "hi":0.01,  "category":"Cardiac"},
    "hsTnT":        {"label":"High-Sensitivity Troponin T",         "label_ar":"تروبونين T عالي الحساسية",            "unit":"ng/L",           "lo":0,     "hi":14,    "category":"Cardiac"},
    "BNP":          {"label":"BNP (Brain Natriuretic Peptide)",     "label_ar":"الببتيد الناتريوريتيكي BNP",          "unit":"pg/mL",          "lo":0,     "hi":100,   "category":"Cardiac"},
    "NTproBNP":     {"label":"NT-proBNP",                           "label_ar":"NT-proBNP",                           "unit":"pg/mL",          "lo":0,     "hi":125,   "category":"Cardiac"},
    "CKtotal":      {"label":"Total CK (Creatine Kinase)",          "label_ar":"كرياتين كيناز الكلي",                 "unit":"U/L",            "lo":30,    "hi":200,   "lo_m":39,  "hi_m":308, "lo_f":26,  "hi_f":192, "category":"Cardiac"},
    "CKMB":         {"label":"CK-MB",                               "label_ar":"كرياتين كيناز MB",                    "unit":"U/L",            "lo":0,     "hi":25,    "category":"Cardiac"},
    "Myoglobin":    {"label":"Myoglobin",                           "label_ar":"الميوجلوبين",                          "unit":"ng/mL",          "lo":0,     "hi":90,    "category":"Cardiac"},
    "DDimer":       {"label":"D-Dimer",                             "label_ar":"D-ثنائي",                             "unit":"µg/mL FEU",      "lo":0,     "hi":0.5,   "category":"Cardiac"},
    "Fibrinogen":   {"label":"Fibrinogen",                          "label_ar":"الفيبرينوجين",                         "unit":"mg/dL",          "lo":200,   "hi":400,   "category":"Cardiac"},
    "Homocysteine": {"label":"Homocysteine",                        "label_ar":"هوموسيستين",                           "unit":"µmol/L",         "lo":5,     "hi":15,    "category":"Cardiac"},
    "hsCRP":        {"label":"hs-CRP (Cardiac)",                    "label_ar":"البروتين التفاعلي C القلبي",          "unit":"mg/L",           "lo":0,     "hi":1.0,   "category":"Cardiac"},

    # ── INFLAMMATION / AUTOIMMUNE ────────────────────────────────────────────
    "CRP":          {"label":"C-Reactive Protein (CRP)",            "label_ar":"البروتين التفاعلي C",                 "unit":"mg/L",           "lo":0,     "hi":5,     "category":"Inflammation"},
    "ESR":          {"label":"ESR (Westergren)",                    "label_ar":"سرعة ترسيب الدم",                     "unit":"mm/hr",          "lo":0,     "hi":20,    "lo_m":0,   "hi_m":15,  "lo_f":0,   "hi_f":20,  "category":"Inflammation"},
    "Procalcitonin":{"label":"Procalcitonin (PCT)",                 "label_ar":"بروكالسيتونين",                        "unit":"ng/mL",          "lo":0,     "hi":0.1,   "category":"Inflammation"},
    "IL6":          {"label":"Interleukin-6 (IL-6)",                "label_ar":"الإنترلوكين-6",                        "unit":"pg/mL",          "lo":0,     "hi":7,     "category":"Inflammation"},
    "RF":           {"label":"Rheumatoid Factor (RF)",              "label_ar":"عامل الروماتويد",                     "unit":"IU/mL",          "lo":0,     "hi":14,    "category":"Inflammation"},
    "AntiCCP":      {"label":"Anti-CCP Antibodies",                 "label_ar":"أجسام مضادة CCP",                     "unit":"U/mL",           "lo":0,     "hi":17,    "category":"Inflammation"},
    "ANA":          {"label":"ANA Titer",                           "label_ar":"الأجسام المضادة النووية ANA",          "unit":"titer",          "lo":0,     "hi":40,    "category":"Inflammation"},
    "AntiDsDNA":    {"label":"Anti-dsDNA Antibodies",               "label_ar":"أجسام مضادة dsDNA",                   "unit":"IU/mL",          "lo":0,     "hi":7,     "category":"Inflammation"},
    "Complement3":  {"label":"Complement C3",                       "label_ar":"مكمل C3",                             "unit":"mg/dL",          "lo":90,    "hi":180,   "category":"Inflammation"},
    "Complement4":  {"label":"Complement C4",                       "label_ar":"مكمل C4",                             "unit":"mg/dL",          "lo":16,    "hi":47,    "category":"Inflammation"},
    "SAA":          {"label":"Serum Amyloid A (SAA)",               "label_ar":"الأميلويد A المصلي",                  "unit":"mg/L",           "lo":0,     "hi":10,    "category":"Inflammation"},

    # ── HORMONES — REPRODUCTIVE ──────────────────────────────────────────────
    "LH":           {"label":"LH",                                  "label_ar":"الهرمون اللوتيني LH",                 "unit":"mIU/mL",         "lo":1.7,   "hi":8.6,   "lo_m":1.7, "hi_m":8.6, "lo_f":2.4, "hi_f":12.6,"category":"Hormones"},
    "FSH":          {"label":"FSH",                                 "label_ar":"الهرمون المحفز للجريب FSH",            "unit":"mIU/mL",         "lo":1.5,   "hi":12.4,  "lo_m":1.5, "hi_m":12.4,"lo_f":3.5, "hi_f":12.5,"category":"Hormones"},
    "Estradiol":    {"label":"Estradiol (E2)",                      "label_ar":"الإستراديول E2",                       "unit":"pg/mL",          "lo":19,    "hi":160,   "category":"Hormones"},
    "Progesterone": {"label":"Progesterone",                        "label_ar":"البروجيسترون",                         "unit":"ng/mL",          "lo":0.1,   "hi":0.9,   "category":"Hormones"},
    "Testosterone": {"label":"Total Testosterone",                  "label_ar":"التستوستيرون الكلي",                  "unit":"ng/dL",          "lo":300,   "hi":1000,  "lo_m":300, "hi_m":1000,"lo_f":15,  "hi_f":70,  "category":"Hormones"},
    "SHBG":         {"label":"SHBG",                                "label_ar":"بروتين ربط الهرمونات الجنسية SHBG",   "unit":"nmol/L",         "lo":16.5,  "hi":55.9,  "lo_m":16.5,"hi_m":55.9,"lo_f":24.6,"hi_f":122, "category":"Hormones"},
    "Prolactin":    {"label":"Prolactin (PRL)",                     "label_ar":"البرولاكتين",                          "unit":"ng/mL",          "lo":2,     "hi":18,    "lo_m":2,   "hi_m":18,  "lo_f":2,   "hi_f":29,  "category":"Hormones"},
    "DHEAS":        {"label":"DHEA-S",                              "label_ar":"DHEA-S",                              "unit":"µg/dL",          "lo":65,    "hi":380,   "lo_m":280, "hi_m":640, "lo_f":65,  "hi_f":380, "category":"Hormones"},
    "AMH":          {"label":"Anti-Müllerian Hormone (AMH)",        "label_ar":"هرمون AMH",                           "unit":"ng/mL",          "lo":1.0,   "hi":3.5,   "category":"Hormones"},
    "hCG":          {"label":"β-hCG",                               "label_ar":"هرمون الحمل β-hCG",                   "unit":"mIU/mL",         "lo":0,     "hi":5,     "category":"Hormones"},

    # ── ADRENAL & PITUITARY ──────────────────────────────────────────────────
    "Cortisol8am":  {"label":"Cortisol (8 AM)",                     "label_ar":"الكورتيزول (8 صباحاً)",              "unit":"µg/dL",          "lo":6,     "hi":23,    "category":"Adrenal"},
    "Cortisol4pm":  {"label":"Cortisol (4 PM)",                     "label_ar":"الكورتيزول (4 مساءً)",               "unit":"µg/dL",          "lo":2,     "hi":11,    "category":"Adrenal"},
    "ACTH":         {"label":"ACTH",                                "label_ar":"الهرمون الموجه لقشر الكظر ACTH",     "unit":"pg/mL",          "lo":10,    "hi":60,    "category":"Adrenal"},
    "Aldosterone":  {"label":"Aldosterone",                         "label_ar":"الألدوستيرون",                        "unit":"ng/dL",          "lo":1,     "hi":16,    "category":"Adrenal"},
    "Renin":        {"label":"Plasma Renin Activity",               "label_ar":"نشاط الرينين البلازمي",               "unit":"ng/mL/h",        "lo":0.2,   "hi":1.6,   "category":"Adrenal"},
    "GrowthH":      {"label":"Growth Hormone (GH)",                 "label_ar":"هرمون النمو GH",                      "unit":"ng/mL",          "lo":0,     "hi":0.97,  "category":"Adrenal"},
    "IGF1":         {"label":"IGF-1 (Somatomedin C)",               "label_ar":"عامل النمو IGF-1",                    "unit":"ng/mL",          "lo":116,   "hi":358,   "category":"Adrenal"},

    # ── TUMOR MARKERS ────────────────────────────────────────────────────────
    "CEA":          {"label":"CEA",                                 "label_ar":"المستضد الجنيني السرطاني CEA",        "unit":"ng/mL",          "lo":0,     "hi":5,     "category":"TumorMarkers"},
    "CA125":        {"label":"CA-125",                              "label_ar":"مؤشر سرطان CA-125",                   "unit":"U/mL",           "lo":0,     "hi":35,    "category":"TumorMarkers"},
    "CA199":        {"label":"CA 19-9",                             "label_ar":"مؤشر سرطان CA 19-9",                  "unit":"U/mL",           "lo":0,     "hi":37,    "category":"TumorMarkers"},
    "CA153":        {"label":"CA 15-3",                             "label_ar":"مؤشر سرطان الثدي CA 15-3",            "unit":"U/mL",           "lo":0,     "hi":31,    "category":"TumorMarkers"},
    "PSA":          {"label":"PSA (Total)",                         "label_ar":"مستضد البروستاتا PSA",                "unit":"ng/mL",          "lo":0,     "hi":4,     "category":"TumorMarkers"},
    "fPSA":         {"label":"Free PSA",                            "label_ar":"PSA الحر",                            "unit":"ng/mL",          "lo":0,     "hi":1.0,   "category":"TumorMarkers"},
    "AFP_tumor":    {"label":"AFP (Tumor Marker)",                  "label_ar":"ألفا فيتوبروتين (ورمي)",              "unit":"ng/mL",          "lo":0,     "hi":8.5,   "category":"TumorMarkers"},
    "Beta2MG_t":    {"label":"Beta-2 Microglobulin (Tumor)",        "label_ar":"بيتا-2 ميكروجلوبيولين (ورمي)",       "unit":"mg/L",           "lo":0.8,   "hi":2.4,   "category":"TumorMarkers"},
    "NSE":          {"label":"Neuron-Specific Enolase (NSE)",       "label_ar":"إنولاز الخلايا العصبية NSE",          "unit":"ng/mL",          "lo":0,     "hi":16.3,  "category":"TumorMarkers"},
    "Chromogranin": {"label":"Chromogranin A (CgA)",                "label_ar":"كروموجرانين A",                        "unit":"ng/mL",          "lo":0,     "hi":100,   "category":"TumorMarkers"},
    "CYFRA211":     {"label":"CYFRA 21-1",                          "label_ar":"سيتوكيراتين CYFRA 21-1",              "unit":"ng/mL",          "lo":0,     "hi":3.3,   "category":"TumorMarkers"},
    "SCC":          {"label":"SCC Antigen",                         "label_ar":"مستضد سرطانة الخلايا الحرشفية SCC",   "unit":"ng/mL",          "lo":0,     "hi":1.5,   "category":"TumorMarkers"},
    "HE4":          {"label":"HE4 (Human Epididymis Protein 4)",    "label_ar":"بروتين HE4",                          "unit":"pmol/L",         "lo":0,     "hi":70,    "category":"TumorMarkers"},

    # ── VITAMINS & NUTRITION ─────────────────────────────────────────────────
    "VitB12":       {"label":"Vitamin B12 (Cobalamin)",             "label_ar":"فيتامين B12",                         "unit":"pg/mL",          "lo":200,   "hi":900,   "category":"Vitamins"},
    "Folate":       {"label":"Serum Folate (Vitamin B9)",           "label_ar":"حمض الفوليك",                         "unit":"ng/mL",          "lo":3.0,   "hi":17.0,  "category":"Vitamins"},
    "VitA":         {"label":"Vitamin A (Retinol)",                 "label_ar":"فيتامين أ",                           "unit":"µg/dL",          "lo":30,    "hi":65,    "category":"Vitamins"},
    "VitE":         {"label":"Vitamin E (α-Tocopherol)",            "label_ar":"فيتامين هـ",                          "unit":"mg/L",           "lo":5,     "hi":18,    "category":"Vitamins"},
    "Zinc":         {"label":"Serum Zinc",                          "label_ar":"الزنك",                               "unit":"µg/dL",          "lo":70,    "hi":120,   "category":"Vitamins"},
    "Copper":       {"label":"Serum Copper",                        "label_ar":"النحاس",                              "unit":"µg/dL",          "lo":70,    "hi":140,   "category":"Vitamins"},
    "Selenium":     {"label":"Serum Selenium",                      "label_ar":"السيلينيوم",                           "unit":"µg/L",           "lo":70,    "hi":150,   "category":"Vitamins"},
    "Ceruloplasmin":{"label":"Ceruloplasmin",                       "label_ar":"سيرولوبلازمين",                        "unit":"mg/dL",          "lo":20,    "hi":50,    "category":"Vitamins"},

    # ── PANCREAS ─────────────────────────────────────────────────────────────
    "Amylase":      {"label":"Serum Amylase",                       "label_ar":"أميلاز الدم",                         "unit":"U/L",            "lo":30,    "hi":110,   "category":"Pancreas"},
    "Lipase":       {"label":"Serum Lipase",                        "label_ar":"ليباز الدم",                          "unit":"U/L",            "lo":7,     "hi":60,    "category":"Pancreas"},
    "Glucagon":     {"label":"Glucagon",                            "label_ar":"الجلوكاجون",                           "unit":"pg/mL",          "lo":50,    "hi":100,   "category":"Pancreas"},

    # ── CBC ──────────────────────────────────────────────────────────────────
    "Hgb":          {"label":"Hemoglobin",                          "label_ar":"الهيموجلوبين",                        "unit":"g/dL",           "lo":12.0,  "hi":17.5,  "lo_m":13.5,"hi_m":17.5,"lo_f":12.0,"hi_f":15.5,"category":"CBC"},
    "Hct":          {"label":"Hematocrit",                          "label_ar":"الهيماتوكريت",                        "unit":"%",              "lo":36,    "hi":53,    "lo_m":41,  "hi_m":53,  "lo_f":36,  "hi_f":46,  "category":"CBC"},
    "RBC":          {"label":"Red Blood Cell Count",                "label_ar":"كريات الدم الحمراء",                  "unit":"×10⁶/µL",        "lo":4.0,   "hi":5.9,   "lo_m":4.5, "hi_m":5.9, "lo_f":4.0, "hi_f":5.2, "category":"CBC"},
    "MCV":          {"label":"Mean Corpuscular Volume",             "label_ar":"متوسط حجم الكريات MCV",               "unit":"fL",             "lo":80,    "hi":100,   "category":"CBC"},
    "MCH":          {"label":"Mean Corpuscular Hemoglobin",         "label_ar":"متوسط هيموجلوبين الكريات MCH",        "unit":"pg",             "lo":27,    "hi":33,    "category":"CBC"},
    "MCHC":         {"label":"MCHC",                                "label_ar":"تركيز هيموجلوبين الكريات MCHC",       "unit":"g/dL",           "lo":32,    "hi":36,    "category":"CBC"},
    "RDW":          {"label":"Red Cell Distribution Width",         "label_ar":"توزيع حجم الكريات RDW",               "unit":"%",              "lo":11.5,  "hi":14.5,  "category":"CBC"},
    "WBC":          {"label":"White Blood Cell Count",              "label_ar":"كريات الدم البيضاء",                  "unit":"×10³/µL",        "lo":4.5,   "hi":11.0,  "category":"CBC"},
    "Neutrophils":  {"label":"Neutrophils (%)",                     "label_ar":"النيوتروفيل",                          "unit":"%",              "lo":50,    "hi":70,    "category":"CBC"},
    "Lymphocytes":  {"label":"Lymphocytes (%)",                     "label_ar":"الليمفاويات",                          "unit":"%",              "lo":20,    "hi":40,    "category":"CBC"},
    "Monocytes":    {"label":"Monocytes (%)",                       "label_ar":"المونوسيت",                           "unit":"%",              "lo":2,     "hi":8,     "category":"CBC"},
    "Eosinophils":  {"label":"Eosinophils (%)",                     "label_ar":"الحمضات",                             "unit":"%",              "lo":1,     "hi":4,     "category":"CBC"},
    "Basophils":    {"label":"Basophils (%)",                       "label_ar":"القاعدات",                            "unit":"%",              "lo":0,     "hi":1,     "category":"CBC"},
    "Platelets":    {"label":"Platelet Count",                      "label_ar":"الصفائح الدموية",                     "unit":"×10³/µL",        "lo":150,   "hi":400,   "category":"CBC"},
    "Reticulocytes":{"label":"Reticulocyte Count",                  "label_ar":"الشبكيات",                            "unit":"%",              "lo":0.5,   "hi":2.5,   "category":"CBC"},
}

# =============================================================================
# PANELS DEFINITION
# =============================================================================

PANELS = {
    "🩺 Glucose & Diabetes":   ["FBG","RBG","PP2h","HbA1c","Insulin","Fructosamine","Cpeptide","GAD65"],
    "🫘 Kidney Function":      ["Creatinine","Urea","UricAcid","eGFR","CystatinC","uACR","uProtein24h","Beta2MG_k","Phosphorus_k","PTH_k"],
    "🫀 Liver Function":       ["ALT","AST","ALP","GGT","TBili","DBili","IBili","Albumin","TotalProt","LDH","PT","INR","APTT","AFP_liver"],
    "💊 Lipid Panel":          ["TC","TG","LDL","HDL","nonHDL","VLDL","Lpa","ApoA1","ApoB"],
    "🦋 Thyroid":              ["TSH","FT4","FT3","TT4","TT3","AntiTPO","AntiTG","TRAb","Thyroglobulin"],
    "🔩 Iron Studies":         ["SerumFe","TIBC","UIBC","TfSat","Ferritin","Transferrin","sTfR"],
    "🦴 Bone Metabolism":      ["CalciumT","CalciumI","Phosphorus","Magnesium","VitD25","VitD125","PTH_bone","Osteocalcin","CTX","NTX"],
    "⚡ Electrolytes":         ["Sodium","Potassium","Chloride","Bicarbonate","Osmolality"],
    "❤️ Cardiac Markers":      ["cTnI","cTnT","hsTnT","BNP","NTproBNP","CKtotal","CKMB","Myoglobin","DDimer","Fibrinogen","Homocysteine","hsCRP"],
    "🔬 Inflammation":         ["CRP","ESR","Procalcitonin","IL6","RF","AntiCCP","ANA","AntiDsDNA","Complement3","Complement4","SAA"],
    "⚗️ Hormones":             ["LH","FSH","Estradiol","Progesterone","Testosterone","SHBG","Prolactin","DHEAS","AMH","hCG"],
    "🧪 Adrenal & Pituitary":  ["Cortisol8am","Cortisol4pm","ACTH","Aldosterone","Renin","GrowthH","IGF1"],
    "🧬 Tumor Markers":        ["CEA","CA125","CA199","CA153","PSA","fPSA","AFP_tumor","Beta2MG_t","NSE","Chromogranin","CYFRA211","SCC","HE4"],
    "🥦 Vitamins & Nutrition": ["VitB12","Folate","VitD25","VitA","VitE","Zinc","Copper","Selenium","Ceruloplasmin"],
    "🫁 Pancreas":             ["Amylase","Lipase","Glucagon"],
    "🩸 CBC":                  ["Hgb","Hct","RBC","MCV","MCH","MCHC","RDW","WBC","Neutrophils","Lymphocytes","Monocytes","Eosinophils","Basophils","Platelets","Reticulocytes"],
}

# =============================================================================
# SECTION 2: STATUS ENGINE
# =============================================================================

def get_status(key, value, sex="unspecified"):
    if key not in REF:
        return "unknown", None, None
    r = REF[key]
    if sex == "male" and "lo_m" in r:
        lo, hi = r["lo_m"], r["hi_m"]
    elif sex == "female" and "lo_f" in r:
        lo, hi = r["lo_f"], r["hi_f"]
    else:
        lo, hi = r["lo"], r["hi"]
    if value < lo:
        return "low", lo, hi
    elif value > hi:
        return "high", lo, hi
    else:
        return "normal", lo, hi

# =============================================================================
# SECTION 3: CLINICAL INTELLIGENCE ENGINE
# =============================================================================

def run_cross_validation(results: dict, sex="unspecified", age=None) -> list:
    insights = []
    has = lambda *keys: all(k in results and results[k] > 0 for k in keys)
    v   = lambda k: results.get(k, 0)

    # ── 1. Glucose & Diabetes ────────────────────────────────────────────────
    if has("FBG", "HbA1c"):
        fbg, h = v("FBG"), v("HbA1c")
        eag = h * 28.7 - 46.7
        if fbg >= 126 and h < 5.7:
            insights.append({"cat":"Glucose","sev":"warning",
                "title":"⚠️ FBG مرتفع — HbA1c منخفض كاذب؟",
                "en":f"FBG {fbg} mg/dL (diabetic range) but HbA1c {h}% (normal). Expected avg glucose: ~{eag:.0f} mg/dL.\n"
                     "Causes: Hemoglobin variants (HbS, HbC, thalassemia), hemolytic anemia, recent transfusion.\n"
                     "Recommend: CBC, reticulocytes, Hb electrophoresis, fructosamine.",
                "ar":f"سكر الصيام {fbg} في نطاق السكري لكن HbA1c طبيعي {h}% — تناقض.\nالأسباب: هيموجلوبين غير طبيعي أو فقر دم انحلالي.",
                "refs":["ADA 2025","IFCC"]})
        elif fbg < 100 and h >= 6.5:
            insights.append({"cat":"Glucose","sev":"warning",
                "title":"⚠️ HbA1c مرتفع كاذب — سكر الصيام طبيعي",
                "en":f"HbA1c {h}% (diabetic) but FBG {fbg} mg/dL (normal). Iron deficiency, B12 deficiency, splenectomy may falsely elevate HbA1c.\nRecommend: iron studies, B12, renal function.",
                "ar":"نقص الحديد أو B12 يرفع HbA1c كاذباً مع سكر صيام طبيعي.",
                "refs":["ADA 2025","Tietz 7th"]})
        elif abs(fbg - eag) > 50:
            insights.append({"cat":"Glucose","sev":"info",
                "title":"ℹ️ تباين بين FBG و HbA1c",
                "en":f"Estimated avg glucose from HbA1c {h}%: ~{eag:.0f} mg/dL vs FBG {fbg} mg/dL (diff {abs(fbg-eag):.0f}). May indicate glucose variability.",
                "ar":f"فرق {abs(fbg-eag):.0f} بين المتوسط المقدر والسكر المقيس — تذبذب محتمل.",
                "refs":["ADA 2025"]})

    if has("Insulin","FBG"):
        homa = (v("Insulin") * v("FBG")) / 405
        if homa > 2.5:
            insights.append({"cat":"Glucose","sev":"warning",
                "title":"⚠️ مقاومة الإنسولين — HOMA-IR مرتفع",
                "en":f"Calculated HOMA-IR = {homa:.2f} (>2.5 = insulin resistance). Associated with metabolic syndrome, PCOS, NAFLD.\nRecommend: lipid panel, liver enzymes, waist circumference.",
                "ar":f"HOMA-IR = {homa:.2f} — مقاومة إنسولين. مرتبط بالمتلازمة الأيضية وكبد دهني.",
                "refs":["ADA 2025","EASL NAFLD 2023"]})

    # ── 2. Kidney ────────────────────────────────────────────────────────────
    if has("Urea","Creatinine"):
        ratio = v("Urea") / v("Creatinine")
        if ratio > 40:
            insights.append({"cat":"Kidney","sev":"critical",
                "title":"🔴 نسبة BUN/كرياتينين > 40 — نزيف هضمي علوي محتمل",
                "en":f"BUN:Creatinine ratio = {ratio:.1f} (normal 10–20). >40 strongly suggests upper GI bleeding. Also: severe dehydration, high protein diet.\nUrgent clinical assessment.",
                "ar":f"نسبة يوريا/كرياتينين = {ratio:.1f} — تشير بقوة لنزيف في الجهاز الهضمي العلوي.",
                "refs":["NEJM","Henry's 23rd"]})
        elif ratio > 20:
            insights.append({"cat":"Kidney","sev":"warning",
                "title":"⚠️ BUN/كرياتينين > 20 — أزوتيميا ما قبل الكلوي",
                "en":f"BUN:Cr ratio = {ratio:.1f}. Pre-renal: dehydration, heart failure, low perfusion, GI bleed.",
                "ar":f"نسبة {ratio:.1f} — جفاف، قصور قلب، أو نزيف هضمي.",
                "refs":["KDIGO 2024"]})
        elif ratio < 10 and v("Urea") < 7:
            insights.append({"cat":"Kidney","sev":"info",
                "title":"ℹ️ BUN/كرياتينين منخفض — مرض كبدي أو نقص بروتين",
                "en":f"BUN:Cr ratio = {ratio:.1f} (low). Consider: liver disease, low protein diet, SIADH, malnutrition.",
                "ar":f"نسبة {ratio:.1f} منخفضة — مرض كبدي أو نظام غذائي منخفض البروتين.",
                "refs":["Tietz 7th"]})

    if has("eGFR"):
        gfr = v("eGFR")
        if gfr < 15:
            insights.append({"cat":"Kidney","sev":"critical",
                "title":"🔴 GFR < 15 — فشل كلوي (CKD G5)",
                "en":f"eGFR {gfr} mL/min/1.73m² — Kidney failure (CKD stage G5). Immediate nephrology referral. Consider dialysis.",
                "ar":f"GFR = {gfr} — فشل كلوي مرحلة G5. إحالة فورية لأمراض الكلى.",
                "refs":["KDIGO CKD 2024"]})
        elif gfr < 30:
            insights.append({"cat":"Kidney","sev":"warning",
                "title":"⚠️ GFR 15–29 — اعتلال كلوي شديد (CKD G4)",
                "en":f"eGFR {gfr} — Severely decreased kidney function (G4). Nephrology referral, dose-adjust medications.",
                "ar":f"GFR = {gfr} — ضعف كلوي شديد G4. مراجعة جرعات الأدوية.",
                "refs":["KDIGO CKD 2024"]})
        elif gfr < 60:
            insights.append({"cat":"Kidney","sev":"info",
                "title":"ℹ️ GFR 30–59 — اعتلال كلوي معتدل (CKD G3)",
                "en":f"eGFR {gfr} — Moderately decreased (G3). Monitor BP, avoid NSAIDs, adjust medications.",
                "ar":f"GFR = {gfr} — اعتلال كلوي معتدل. تجنب NSAIDs ومراقبة ضغط الدم.",
                "refs":["KDIGO CKD 2024"]})

    # ── 3. Liver ─────────────────────────────────────────────────────────────
    if has("ALT","AST"):
        alt, ast = v("ALT"), v("AST")
        dr = ast / alt if alt > 0 else 0
        if (alt > 56 or ast > 40) and dr >= 2:
            insights.append({"cat":"Liver","sev":"warning",
                "title":"⚠️ نسبة De Ritis ≥ 2 — نمط الكبد الكحولي",
                "en":f"AST/ALT (De Ritis) = {dr:.1f}. Ratio ≥2 suggests alcoholic liver disease or cirrhosis. Correlate with GGT.",
                "ar":f"نسبة De Ritis = {dr:.1f} — نمط مرض الكبد الكحولي أو تليف.",
                "refs":["EASL 2023"]})
        if alt > 1000 or ast > 1000:
            insights.append({"cat":"Liver","sev":"critical",
                "title":"🔴 إنزيمات الكبد > 1000 — ارتفاع حاد جداً",
                "en":f"ALT {alt} / AST {ast} U/L — extreme elevation.\nTop: acute viral hepatitis, ischemic hepatitis (shock liver), paracetamol overdose, autoimmune hepatitis.\nUrgent: PT/INR, renal function, viral serology.",
                "ar":"ALT/AST أكثر من 1000 — التهاب كبد فيروسي حاد، كبد الصدمة، سمية الباراسيتامول.",
                "refs":["EASL 2023","AASLD 2024"]})
        if has("ALP") and (alt > 56 or ast > 40 or v("ALP") > 147):
            alp = v("ALP")
            rr  = (alt/56) / ((alp/147) if alp > 0 else 1)
            pat    = "Hepatocellular" if rr >= 5 else "Cholestatic" if rr <= 2 else "Mixed"
            pat_ar = "تلف خلوي كبدي" if rr >= 5 else "انسدادي/ركود صفراوي" if rr <= 2 else "مختلط"
            desc = {"Hepatocellular":"Viral hepatitis, drugs, ischemia, autoimmune.",
                    "Cholestatic":"Bile duct obstruction, PBC, PSC, drug-induced cholestasis.",
                    "Mixed":"Drug-induced overlap or mixed syndrome."}
            insights.append({"cat":"Liver","sev":"info",
                "title":f"ℹ️ نمط إصابة الكبد: {pat}",
                "en":f"R-ratio = {rr:.1f} → {pat} pattern.\nALT: {alt} ({alt/56:.1f}× ULN) | ALP: {alp} ({alp/147:.1f}× ULN)\nCauses: {desc[pat]}",
                "ar":f"نمط الإصابة: {pat_ar} (R-ratio = {rr:.1f}).",
                "refs":["EASL DILI 2023"]})

    if has("TBili","DBili"):
        tb, db = v("TBili"), v("DBili")
        if tb > 1.2:
            pct = (db/tb)*100 if tb > 0 else 0
            if pct > 50:
                insights.append({"cat":"Liver","sev":"warning",
                    "title":"⚠️ يرقان انسدادي — بيليروبين مباشر مهيمن",
                    "en":f"Direct bilirubin {db} mg/dL ({pct:.0f}% of total) → conjugated hyperbilirubinemia. Cholestasis, bile duct obstruction, hepatitis, Dubin-Johnson.",
                    "ar":f"البيليروبين المباشر {pct:.0f}% — ركود صفراوي أو انسداد.",
                    "refs":["Henry's 23rd"]})
            else:
                ib = tb - db
                insights.append({"cat":"Liver","sev":"info",
                    "title":"ℹ️ يرقان ما قبل الكبد — بيليروبين غير مباشر مهيمن",
                    "en":f"Indirect bilirubin {ib:.1f} mg/dL predominates. Consider: hemolysis, Gilbert syndrome, neonatal jaundice.",
                    "ar":"البيليروبين غير المباشر مهيمن — فقر دم انحلالي أو متلازمة جيلبرت.",
                    "refs":["Tietz 7th"]})

    if has("Albumin","PT") or has("Albumin","INR"):
        alb = v("Albumin")
        if alb < 3.0:
            insights.append({"cat":"Liver","sev":"warning",
                "title":"⚠️ ألبومين منخفض جداً — خلل وظيفي كبدي شديد",
                "en":f"Albumin {alb} g/dL (severely low). Suggests significant hepatic synthetic dysfunction. Also consider malnutrition, nephrotic syndrome, protein-losing enteropathy.",
                "ar":f"ألبومين {alb} منخفض جداً — خلل توليفي كبدي شديد أو سوء تغذية أو اعتلال كلوي.",
                "refs":["EASL 2023"]})

    # ── 4. Lipids ────────────────────────────────────────────────────────────
    if has("TC","TG","LDL","HDL"):
        tc, tg, ldl, hdl = v("TC"), v("TG"), v("LDL"), v("HDL")
        if tg > 400:
            insights.append({"cat":"Lipids","sev":"critical",
                "title":"🔴 TG > 400 — معادلة Friedewald غير صالحة",
                "en":f"TG = {tg} mg/dL. Friedewald LDL formula INVALID when TG >400. Reported LDL may be grossly underestimated. Order direct LDL measurement.",
                "ar":f"الدهون الثلاثية {tg} — LDL المحسوب غير موثوق. يجب قياس Direct LDL.",
                "refs":["ACC/AHA 2024"]})
        elif tg > 500:
            insights.append({"cat":"Lipids","sev":"critical",
                "title":"🔴 TG > 500 — خطر التهاب البنكرياس",
                "en":f"TG {tg} mg/dL — severe hypertriglyceridemia. Risk of acute pancreatitis. Urgent treatment: fibrates, omega-3, strict low-fat diet.",
                "ar":f"دهون ثلاثية {tg} — خطر التهاب بنكرياس حاد. علاج فوري.",
                "refs":["ACC/AHA 2024","Endocrine Society"]})
        if tg > 150 and hdl < 40:
            insights.append({"cat":"Lipids","sev":"warning",
                "title":"⚠️ دسليبيدميا أثيرية (↑TG + ↓HDL)",
                "en":f"TG {tg} + HDL {hdl} mg/dL — classic atherogenic dyslipidemia. High CV risk. Strongly associated with insulin resistance and metabolic syndrome.",
                "ar":f"دهون ثلاثية مرتفعة + HDL منخفض = خطر قلبي وعائي. مقاومة الإنسولين.",
                "refs":["ACC/AHA 2024","IDF"]})
        tc_hdl = tc/hdl if hdl > 0 else 0
        if tc_hdl > 5:
            insights.append({"cat":"Lipids","sev":"warning",
                "title":"⚠️ نسبة TC/HDL > 5 — خطر قلبي وعائي مرتفع",
                "en":f"TC/HDL ratio = {tc_hdl:.1f} (target <5). Independent CV risk predictor.",
                "ar":f"نسبة الكوليسترول الكلي/HDL = {tc_hdl:.1f} — مؤشر خطر قلبي مرتفع.",
                "refs":["ACC/AHA 2024"]})

    if has("ApoB","ApoA1") and v("ApoA1") > 0:
        ratio = v("ApoB")/v("ApoA1")
        if ratio > 0.9:
            insights.append({"cat":"Lipids","sev":"warning",
                "title":"⚠️ نسبة ApoB/ApoA-I مرتفعة — خطر قلبي وعائي",
                "en":f"ApoB/ApoA-I = {ratio:.2f} (>0.9 = elevated risk). Better CV risk predictor than LDL alone, especially in high-TG patients.",
                "ar":f"نسبة ApoB/ApoA-I = {ratio:.2f} — مؤشر دقيق للخطر القلبي الوعائي.",
                "refs":["ACC/AHA 2024"]})

    # ── 5. Thyroid ───────────────────────────────────────────────────────────
    if has("TSH","FT4"):
        tsh, ft4 = v("TSH"), v("FT4")
        if tsh > 4 and ft4 < 0.8:
            insights.append({"cat":"Thyroid","sev":"warning",
                "title":"⚠️ قصور الغدة الدرقية الأولي",
                "en":f"TSH {tsh} ↑ + FT4 {ft4} ↓ = Primary hypothyroidism. Causes: Hashimoto's, post-thyroidectomy, iodine deficiency, drugs (amiodarone, lithium). Recommend: Anti-TPO, Anti-Tg.",
                "ar":"TSH مرتفع + FT4 منخفض = قصور درقي أولي. الأكثر شيوعاً: هاشيموتو.",
                "refs":["ATA 2024"]})
        elif tsh < 0.4 and ft4 > 1.8:
            insights.append({"cat":"Thyroid","sev":"warning",
                "title":"⚠️ فرط نشاط الغدة الدرقية الأولي",
                "en":f"TSH {tsh} ↓ + FT4 {ft4} ↑ = Primary hyperthyroidism. Causes: Graves' disease, toxic nodular goiter, thyroiditis. Recommend: TRAb, thyroid scan.",
                "ar":"TSH منخفض + FT4 مرتفع = فرط نشاط درقي. الأسباب: جريفز، عقيدات سامة.",
                "refs":["ATA 2024"]})
        elif tsh < 0.4 and ft4 < 0.8:
            insights.append({"cat":"Thyroid","sev":"warning",
                "title":"⚠️ قصور درقي مركزي (نخامية/تحت المهاد)",
                "en":f"TSH {tsh} ↓ + FT4 {ft4} ↓ = Central hypothyroidism. Recommend: MRI pituitary, prolactin, cortisol.",
                "ar":"TSH منخفض + FT4 منخفض = قصور درقي مركزي. يُنصح: MRI نخامية.",
                "refs":["ETA 2023"]})
        elif tsh > 4 and 0.8 <= ft4 <= 1.8:
            insights.append({"cat":"Thyroid","sev":"info",
                "title":"ℹ️ قصور درقي تحت إكلينيكي",
                "en":f"TSH {tsh} ↑ + FT4 {ft4} (normal) = Subclinical hypothyroidism. Monitor 6–12 months. Treat if TSH >10 or symptomatic. Check Anti-TPO.",
                "ar":"TSH مرتفع مع FT4 طبيعي = قصور درقي تحت إكلينيكي. متابعة كل 6-12 شهر.",
                "refs":["ATA 2024"]})
        elif tsh < 0.4 and 0.8 <= ft4 <= 1.8 and has("FT3") and v("FT3") > 4.2:
            insights.append({"cat":"Thyroid","sev":"warning",
                "title":"⚠️ سُمية T3 (T3 Toxicosis)",
                "en":f"TSH suppressed + FT4 normal + FT3 {v('FT3')} ↑ = T3 toxicosis. Toxic multinodular goiter or early Graves'. Recommend: thyroid scan.",
                "ar":"TSH منخفض + FT4 طبيعي + FT3 مرتفع = سُمية T3. يُنصح: مسح الغدة الدرقية.",
                "refs":["ATA 2024"]})

    # ── 6. Iron ──────────────────────────────────────────────────────────────
    if has("SerumFe","TIBC","Ferritin"):
        fe, tibc, ferr = v("SerumFe"), v("TIBC"), v("Ferritin")
        sat = (fe/tibc)*100 if tibc > 0 else 0
        if fe < 60 and tibc > 370 and ferr < 12:
            insights.append({"cat":"Iron","sev":"warning",
                "title":"⚠️ نقص الحديد الكلاسيكي",
                "en":f"Fe ↓({fe}) + TIBC ↑({tibc}) + Ferritin ↓({ferr}) + Sat {sat:.0f}% = Classic IDA. Identify and treat underlying cause (blood loss, malabsorption).",
                "ar":"حديد منخفض + TIBC مرتفع + فيريتين منخفض = نقص الحديد. ابحث عن سبب فقدان الدم.",
                "refs":["WHO 2023","BSH"]})
        elif fe < 60 and tibc < 250 and ferr > 100:
            insights.append({"cat":"Iron","sev":"warning",
                "title":"⚠️ فقر دم الأمراض المزمنة",
                "en":f"Fe ↓({fe}) + TIBC ↓({tibc}) + Ferritin ↑({ferr}) = Anemia of chronic disease. Common in: chronic infection, malignancy, autoimmune, CKD.",
                "ar":"حديد منخفض + TIBC منخفض + فيريتين مرتفع = فقر دم الأمراض المزمنة.",
                "refs":["ASH 2023"]})
        elif fe > 170 and sat > 45 and ferr > 300:
            insights.append({"cat":"Iron","sev":"critical",
                "title":"🔴 تراكم الحديد — استبعد داء ترسب الأصبغة الدموية",
                "en":f"Fe ↑({fe}) + Sat {sat:.0f}% (>45%) + Ferritin ↑({ferr}) = Iron overload. Rule out hereditary hemochromatosis (HFE gene). Recommend: HFE genetics, liver MRI, LFTs.",
                "ar":"حديد مرتفع + تشبع مرتفع + فيريتين مرتفع = تراكم الحديد. استبعد داء ترسب الأصبغة.",
                "refs":["EASL 2022"]})
        elif ferr > 300 and fe <= 170:
            insights.append({"cat":"Iron","sev":"info",
                "title":"ℹ️ فيريتين مرتفع — بروتين الطور الحاد",
                "en":f"Ferritin {ferr} elevated but serum iron {fe} normal. Isolated elevated ferritin ≠ iron overload. Rises in: infection, inflammation, liver disease, malignancy. Check CRP/ESR.",
                "ar":f"فيريتين {ferr} مع حديد طبيعي = بروتين مرحلة حادة. تحقق من CRP وESR.",
                "refs":["BSH 2023"]})

    # ── 7. Bone & Calcium ────────────────────────────────────────────────────
    if has("CalciumT","Albumin"):
        corr_ca = v("CalciumT") + 0.8 * (4.0 - v("Albumin"))
        if corr_ca > 10.5:
            insights.append({"cat":"Bone","sev":"warning",
                "title":"⚠️ فرط الكالسيوم المُصحَّح بالألبومين",
                "en":f"Corrected Ca = {corr_ca:.1f} mg/dL (measured {v('CalciumT')}, albumin {v('Albumin')}).\nCauses: primary hyperparathyroidism (PTH), malignancy (PTHrP), Vit D toxicity, sarcoidosis.",
                "ar":f"الكالسيوم المُصحَّح = {corr_ca:.1f} — فرط كالسيوم. أسباب: فرط جارة الدرقية، أورام.",
                "refs":["AACE 2022"]})
        elif corr_ca < 8.5:
            insights.append({"cat":"Bone","sev":"warning",
                "title":"⚠️ نقص الكالسيوم المُصحَّح",
                "en":f"Corrected Ca = {corr_ca:.1f} mg/dL. Causes: hypoparathyroidism, Vit D deficiency, hypomagnesemia, CKD. Check PTH, Mg, Vit D.",
                "ar":f"الكالسيوم المُصحَّح = {corr_ca:.1f} — نقص. تحقق من PTH، فيتامين د، مغنيسيوم.",
                "refs":["AACE 2022"]})

    if has("VitD25"):
        d = v("VitD25")
        if d < 10:
            insights.append({"cat":"Bone","sev":"critical",
                "title":"🔴 عوز شديد في فيتامين د (<10 ng/mL)",
                "en":f"25-OH Vit D = {d} — severe deficiency. Risk: osteomalacia, secondary hyperparathyroidism, bone pain, muscle weakness. High-dose replenishment required.",
                "ar":f"فيتامين د {d} — عوز شديد جداً. خطر لين العظام وارتفاع PTH ثانوي.",
                "refs":["Endocrine Society 2024"]})
        elif d < 20:
            insights.append({"cat":"Bone","sev":"warning",
                "title":"⚠️ نقص فيتامين د (10–20 ng/mL)",
                "en":f"25-OH Vit D = {d} — deficient. Supplement D3 (1000–4000 IU/day). Recheck in 3 months.",
                "ar":f"فيتامين د {d} — نقص. تكملة D3 وإعادة الفحص بعد 3 أشهر.",
                "refs":["Endocrine Society 2024"]})
        elif d < 30:
            insights.append({"cat":"Bone","sev":"info",
                "title":"ℹ️ فيتامين د غير كافٍ (20–30 ng/mL)",
                "en":f"25-OH Vit D = {d} — insufficient. Moderate supplementation recommended.",
                "ar":f"فيتامين د {d} — غير كافٍ. جرعة تكميلية معتدلة.",
                "refs":["Endocrine Society 2024"]})

    if has("Magnesium") and v("Magnesium") < 1.5:
        insights.append({"cat":"Bone","sev":"warning",
            "title":"⚠️ نقص مغنيسيوم — يُعيق تصحيح الكالسيوم والبوتاسيوم",
            "en":f"Magnesium {v('Magnesium')} mg/dL. Hypomagnesemia impairs PTH secretion and end-organ resistance → refractory hypocalcemia and hypokalemia. Correct Mg first.",
            "ar":f"مغنيسيوم منخفض {v('Magnesium')} — يُعيق تصحيح الكالسيوم والبوتاسيوم. صحّح المغنيسيوم أولاً.",
            "refs":["Tietz 7th"]})

    # ── 8. Electrolytes ──────────────────────────────────────────────────────
    if has("Sodium"):
        na = v("Sodium")
        if na < 120:
            insights.append({"cat":"Electrolytes","sev":"critical",
                "title":"🔴 نقص صوديوم حاد (<120 mEq/L) — خطر وذمة دماغية",
                "en":f"Sodium {na} mEq/L — severe hyponatremia. Risk: cerebral edema, seizures. Urgent correction (max 6–8 mEq/L per 24h to prevent osmotic demyelination).",
                "ar":f"صوديوم {na} — نقص شديد جداً. خطر وذمة دماغية وتشنجات. تصحيح حذر عاجل.",
                "refs":["EFNS 2014","Tietz 7th"]})
        elif na < 130:
            insights.append({"cat":"Electrolytes","sev":"warning",
                "title":"⚠️ نقص صوديوم (130–135 mEq/L)",
                "en":f"Sodium {na} mEq/L. Causes: SIADH, heart failure, cirrhosis, hypothyroidism, diuretics. Assess volume status.",
                "ar":f"صوديوم {na} — نقص. أسباب: SIADH، قصور قلب، تليف كبد.",
                "refs":["KDIGO 2024"]})
        elif na > 155:
            insights.append({"cat":"Electrolytes","sev":"critical",
                "title":"🔴 فرط صوديوم حاد (>155 mEq/L) — جفاف شديد",
                "en":f"Sodium {na} mEq/L — severe hypernatremia. Usually severe dehydration or diabetes insipidus. Urgent fluid resuscitation.",
                "ar":f"صوديوم {na} — ارتفاع شديد. جفاف حاد أو داء السكري الكاذب.",
                "refs":["KDIGO 2024"]})

    if has("Potassium"):
        k = v("Potassium")
        if k < 2.5:
            insights.append({"cat":"Electrolytes","sev":"critical",
                "title":"🔴 نقص بوتاسيوم حاد (<2.5 mEq/L) — خطر اضطراب قلبي",
                "en":f"Potassium {k} mEq/L — severe hypokalemia. Risk: cardiac arrhythmias, paralysis. Urgent IV/oral replacement with cardiac monitoring.",
                "ar":f"بوتاسيوم {k} — نقص شديد. خطر اضطرابات قلبية. تعويض عاجل مع مراقبة.",
                "refs":["AHA 2024"]})
        elif k < 3.5:
            insights.append({"cat":"Electrolytes","sev":"warning",
                "title":"⚠️ نقص بوتاسيوم (3.0–3.5 mEq/L)",
                "en":f"Potassium {k} mEq/L. Causes: diuretics, diarrhea, vomiting, Conn's syndrome. Oral KCl supplementation.",
                "ar":f"بوتاسيوم {k} — نقص. أسباب: مدرات البول، إسهال، متلازمة كون.",
                "refs":["Tietz 7th"]})
        elif k > 6.0:
            insights.append({"cat":"Electrolytes","sev":"critical",
                "title":"🔴 فرط بوتاسيوم (>6.0 mEq/L) — طارئ قلبي",
                "en":f"Potassium {k} mEq/L — severe hyperkalemia. Life-threatening: cardiac arrest risk. Urgent ECG, calcium gluconate, insulin-dextrose, consider dialysis.",
                "ar":f"بوتاسيوم {k} — خطر توقف القلب. طارئ طبي.",
                "refs":["KDIGO 2024"]})
        elif k > 5.5:
            insights.append({"cat":"Electrolytes","sev":"warning",
                "title":"⚠️ فرط بوتاسيوم (5.5–6.0 mEq/L)",
                "en":f"Potassium {k} mEq/L. Causes: AKI/CKD, ACE inhibitors, K-sparing diuretics, acidosis, hemolysis. ECG monitoring advised.",
                "ar":f"بوتاسيوم {k} — مرتفع. أسباب: فشل كلوي، ACEi، حموضة.",
                "refs":["KDIGO 2024"]})

    if has("Sodium","Chloride","Bicarbonate"):
        ag = v("Sodium") - (v("Chloride") + v("Bicarbonate"))
        if ag > 16:
            insights.append({"cat":"Electrolytes","sev":"warning",
                "title":"⚠️ فجوة أنيون مرتفعة — حماض استقلابي",
                "en":f"Anion gap = {ag:.0f} mEq/L (>16 = high-gap metabolic acidosis).\nMUDPILES: Methanol, Uremia, DKA, Propylene glycol, Isoniazid, Lactic acidosis, Ethylene glycol, Salicylates.",
                "ar":f"فجوة الأنيون = {ag:.0f} — حماض استقلابي عالي الفجوة. أسباب: MUDPILES (بولينا، DKA، حماض لاكتيكي).",
                "refs":["Tietz 7th"]})

    # ── 9. Cardiac ───────────────────────────────────────────────────────────
    if has("cTnI") and v("cTnI") > 0.04:
        insights.append({"cat":"Cardiac","sev":"critical",
            "title":"🔴 تروبونين I مرتفع — احتشاء عضلة القلب محتمل",
            "en":f"cTnI {v('cTnI')} ng/mL (>0.04). URGENT: Rule out NSTEMI/STEMI. Serial troponins at 0h, 3h, 6h. ECG + cardiology referral immediately.",
            "ar":"تروبونين I مرتفع — احتمال احتشاء قلبي. سلسلة تروبونين وECG عاجل.",
            "refs":["ESC 2023","ACC/AHA 2024"]})

    if has("hsTnT") and v("hsTnT") > 14:
        insights.append({"cat":"Cardiac","sev":"critical",
            "title":"🔴 High-Sensitivity Troponin T مرتفع",
            "en":f"hs-TnT {v('hsTnT')} ng/L (>14). Use ESC 0h/1h algorithm for rapid AMI rule-in/out. Also elevated in: myocarditis, PE, sepsis, CKD.",
            "ar":"hs-TnT مرتفع — استخدم خوارزمية ESC 0h/1h لاستبعاد/تأكيد الاحتشاء.",
            "refs":["ESC 2023"]})

    if has("BNP") and v("BNP") > 100:
        insights.append({"cat":"Cardiac","sev":"warning",
            "title":"⚠️ BNP مرتفع — قصور قلب محتمل",
            "en":f"BNP {v('BNP')} pg/mL (>100). Sensitive HF marker. Also elevated in: AF, PE, CKD, sepsis. Combine with echocardiography.",
            "ar":f"BNP {v('BNP')} — قصور قلب محتمل. قارن مع إيكو القلب.",
            "refs":["ESC HF 2023"]})

    if has("NTproBNP") and v("NTproBNP") > 125:
        insights.append({"cat":"Cardiac","sev":"warning",
            "title":"⚠️ NT-proBNP مرتفع — قصور قلب محتمل",
            "en":f"NT-proBNP {v('NTproBNP')} pg/mL (>125 general cutoff, age-adjusted). Elevated suggests HF; consider echo, clinical assessment.",
            "ar":f"NT-proBNP {v('NTproBNP')} — قصور قلب محتمل. يُنصح: إيكو القلب.",
            "refs":["ESC HF 2023"]})

    if has("DDimer") and v("DDimer") > 0.5:
        insights.append({"cat":"Cardiac","sev":"warning",
            "title":"⚠️ D-Dimer مرتفع — استبعد الجلطة الوريدية/الرئوية",
            "en":f"D-Dimer {v('DDimer')} µg/mL FEU (>0.5). Sensitive but non-specific for VTE. With clinical probability: CT pulmonary angiography or Doppler US. Also elevated in: infection, pregnancy, malignancy, post-op.",
            "ar":"D-Dimer مرتفع — حساس لكن غير نوعي. مع احتمالية سريرية: CTA أو إيكو.",
            "refs":["ESC PE 2023"]})

    # ── 10. Inflammation / Sepsis ────────────────────────────────────────────
    if has("Procalcitonin"):
        pct = v("Procalcitonin")
        if pct > 2:
            insights.append({"cat":"Inflammation","sev":"critical",
                "title":"🔴 PCT > 2 — إنتان جرثومي شديد/إنتان الدم",
                "en":f"PCT {pct} ng/mL — likely severe bacterial infection or sepsis. Initiate broad-spectrum antibiotics. Reassess at 48–72h for de-escalation. Blood cultures before antibiotics.",
                "ar":f"PCT {pct} — إنتان جرثومي شديد. بادر بالمضادات واسعة الطيف. زراعة دم قبل البدء.",
                "refs":["IDSA 2024","Surviving Sepsis 2021"]})
        elif pct > 0.5:
            insights.append({"cat":"Inflammation","sev":"warning",
                "title":"⚠️ PCT 0.5–2 — عدوى جرثومية محتملة",
                "en":f"PCT {pct} ng/mL — possible bacterial infection. Clinical assessment and blood cultures advised.",
                "ar":f"PCT {pct} — عدوى جرثومية محتملة. تقييم إكلينيكي وزراعة دم.",
                "refs":["IDSA 2024"]})
        elif pct > 0.1:
            insights.append({"cat":"Inflammation","sev":"info",
                "title":"ℹ️ PCT 0.1–0.5 — العدوى الجرثومية غير محتملة",
                "en":f"PCT {pct} ng/mL — low range. Bacterial infection unlikely; may be viral or local inflammation.",
                "ar":f"PCT {pct} — منخفض. العدوى الجرثومية غير محتملة. محتمل فيروسي.",
                "refs":["IDSA 2024"]})

    if has("CRP","ESR"):
        crp, esr = v("CRP"), v("ESR")
        if crp > 100 and esr > 80:
            insights.append({"cat":"Inflammation","sev":"warning",
                "title":"⚠️ CRP وESR مرتفعان جداً — التهاب جهازي شديد",
                "en":f"CRP {crp} mg/L + ESR {esr} mm/hr — both markedly elevated. Suggests: sepsis, vasculitis, polymyalgia rheumatica, malignancy, major infection.",
                "ar":"CRP وESR مرتفعان — التهاب جهازي شديد. أسباب: إنتان، أمراض مناعة ذاتية، أورام.",
                "refs":["ACR 2024"]})
        if crp > 5 and esr < 20:
            insights.append({"cat":"Inflammation","sev":"info",
                "title":"ℹ️ CRP مرتفع مع ESR طبيعي — التهاب حديث",
                "en":f"CRP rises faster (6–12h) than ESR. CRP {crp} elevated + ESR {esr} normal = acute/recent inflammation. ESR may not have risen yet.",
                "ar":"CRP يرتفع أسرع من ESR. CRP مرتفع مع ESR طبيعي = التهاب حديث النشأة.",
                "refs":["Tietz 7th"]})

    if has("RF","AntiCCP") and v("RF") > 14 and v("AntiCCP") > 17:
        insights.append({"cat":"Inflammation","sev":"warning",
            "title":"⚠️ RF و Anti-CCP إيجابيان — التهاب مفاصل رثياني محتمل",
            "en":f"RF {v('RF')} IU/mL + Anti-CCP {v('AntiCCP')} U/mL — both elevated. Highly specific for Rheumatoid Arthritis (RA). Clinical correlation required.",
            "ar":f"RF وAnti-CCP إيجابيان — شديد الخصوصية للتهاب المفاصل الرثياني (RA).",
            "refs":["ACR/EULAR 2022"]})

    # ── 11. CBC ──────────────────────────────────────────────────────────────
    if has("Hgb","MCV"):
        hgb, mcv = v("Hgb"), v("MCV")
        hgb_low = (sex=="male" and hgb < 13.5) or (sex=="female" and hgb < 12.0) or (sex=="unspecified" and hgb < 12.0)
        if hgb_low and mcv < 80:
            if has("RDW"):
                rdw = v("RDW")
                if rdw > 14.5:
                    insights.append({"cat":"CBC","sev":"warning",
                        "title":"⚠️ فقر دم صغير الكريات + RDW مرتفع — نقص الحديد",
                        "en":f"Hgb {hgb} ↓ + MCV {mcv} fL (microcytic) + RDW {rdw}% ↑.\nHigh RDW = IDA pattern. Thalassemia trait typically has NORMAL RDW.\nRecommend: iron studies (Fe, TIBC, Ferritin).",
                        "ar":"Hgb منخفض + MCV صغير + RDW مرتفع = فقر دم بنقص الحديد. دراسات الحديد.",
                        "refs":["Bessman Index","WHO 2023"]})
                else:
                    insights.append({"cat":"CBC","sev":"info",
                        "title":"ℹ️ فقر دم صغير الكريات + RDW طبيعي — ثلاسيميا الحاملة؟",
                        "en":f"Hgb {hgb} ↓ + MCV {mcv} fL + RDW {rdw}% (normal). Normal RDW with microcytosis suggests thalassemia trait.\nRecommend: Hb electrophoresis, iron studies.",
                        "ar":"Hgb منخفض + MCV صغير + RDW طبيعي = محتمل ثلاسيميا الحاملة. كهربة الهيموجلوبين.",
                        "refs":["Mentzer Index","BSH 2023"]})
        if hgb_low and mcv > 100:
            insights.append({"cat":"CBC","sev":"warning",
                "title":"⚠️ فقر دم كبير الكريات — نقص B12/فولات؟",
                "en":f"Hgb {hgb} ↓ + MCV {mcv} fL (macrocytic).\nDiff: B12 def, folate def, alcohol, hypothyroidism, methotrexate, hydroxyurea, MDS.\nRecommend: B12, folate, reticulocytes, peripheral film.",
                "ar":"Hgb منخفض + MCV كبير = فقر دم كبير الكريات. أسباب: نقص B12 أو فولات.",
                "refs":["BSH B12/Folate 2024"]})

    if has("WBC","Neutrophils","Lymphocytes"):
        wbc = v("WBC")
        anc  = wbc * v("Neutrophils")  / 100
        alc  = wbc * v("Lymphocytes") / 100
        if wbc > 11 and anc > 7.5:
            insights.append({"cat":"CBC","sev":"info",
                "title":"ℹ️ نيوتروفيليا — عدوى جرثومية / استجابة إجهاد",
                "en":f"WBC {wbc} ×10³ ↑, ANC {anc:.1f}.\nCauses: bacterial infection, physiologic stress, corticosteroids, smoking.\nIf WBC >30: consider leukemoid reaction or CML.",
                "ar":f"نيوتروفيل مرتفع ({anc:.1f} ×10³) — عدوى جرثومية أو استجابة إجهاد.",
                "refs":["Henry's 23rd"]})
        if wbc < 4.5 and anc < 1.8:
            sev  = "critical" if anc < 0.5 else "warning"
            grade = "شديد جداً (فقدان المحببات)" if anc < 0.5 else "معتدل" if anc < 1.0 else "خفيف"
            insights.append({"cat":"CBC","sev":sev,
                "title":f"{'🔴' if sev=='critical' else '⚠️'} نقص النيوتروفيل — {grade}",
                "en":f"ANC = {anc:.2f} ×10³. Grade: {grade}.\nCauses: viral, drug-induced (chemo, carbimazole, clozapine), B12/folate def.\n" +
                     ("⚠️ URGENT: Life-threatening infection risk. Reverse isolation!" if anc < 0.5 else "Monitor closely, review medications."),
                "ar":f"ANC = {anc:.2f} — نقص نيوتروفيل ({grade})." + (" خطر عدوى شديد جداً — عزل عكسي!" if anc < 0.5 else ""),
                "refs":["CTCAE Grading","IDSA 2024"]})
        if wbc > 11 and alc > 4.0:
            insights.append({"cat":"CBC","sev":"info",
                "title":"ℹ️ لمفاويات مرتفعة — عدوى فيروسية / CLL؟",
                "en":f"ALC = {alc:.1f} ×10³ ↑.\nCauses: viral (EBV, CMV, COVID-19), pertussis, CLL (if persistent >5.0).\nRecommend: peripheral film, flow cytometry if persistent.",
                "ar":f"لمفاويات مرتفعة ({alc:.1f} ×10³) — عدوى فيروسية أو CLL.",
                "refs":["WHO CLL Guidelines"]})

    if has("Platelets"):
        plt = v("Platelets")
        if plt < 20:
            insights.append({"cat":"CBC","sev":"critical",
                "title":"🔴 نقص صفيحات شديد (<20 ×10³) — خطر نزيف تلقائي",
                "en":f"Platelets {plt} ×10³/µL — severe thrombocytopenia. Risk of spontaneous bleeding (CNS, GI). Urgent: hematology consult, review medications, rule out ITP/TTP/DIC.",
                "ar":f"صفائح {plt} — نقص شديد. خطر نزيف تلقائي. مراجعة عاجلة للدم.",
                "refs":["ASH ITP 2023"]})
        elif plt < 50:
            insights.append({"cat":"CBC","sev":"warning",
                "title":"⚠️ نقص صفيحات معتدل (50–100 ×10³)",
                "en":f"Platelets {plt} ×10³/µL. Risk of bleeding with procedures. Causes: ITP, drug-induced, liver disease, bone marrow suppression, DIC.",
                "ar":f"صفائح {plt} — نقص معتدل. خطر نزيف مع الإجراءات.",
                "refs":["ASH 2023"]})
        elif plt > 600:
            insights.append({"cat":"CBC","sev":"warning",
                "title":"⚠️ فرط الصفيحات (>600 ×10³)",
                "en":f"Platelets {plt} ×10³/µL. Causes: reactive (infection, iron def, post-splenectomy) or essential thrombocythemia (ET). If >1000: risk of thrombosis and paradoxical bleeding.",
                "ar":f"صفائح {plt} — مرتفعة. أسباب: تفاعلية (عدوى، نقص حديد) أو essential thrombocythemia.",
                "refs":["WHO Myeloid Neoplasms 2022"]})

    # ── 12. Multi-organ ──────────────────────────────────────────────────────
    if has("ALT","Creatinine") and v("ALT") > 56 and v("Creatinine") > 1.5:
        insights.append({"cat":"Multi-organ","sev":"warning",
            "title":"⚠️ خلل كبدي-كلوي مشترك",
            "en":f"ALT {v('ALT')} ↑ + Creatinine {v('Creatinine')} ↑. Consider: hepatorenal syndrome (HRS), sepsis-related MOD, ischemic hepatitis + AKI, drug/toxin (paracetamol, NSAIDs, aminoglycosides).",
            "ar":"ارتفاع إنزيمات الكبد + كرياتينين = خلل كبدي-كلوي مشترك. فكر في: HRS، صدمة، سمية دواء.",
            "refs":["EASL 2023","KDIGO 2024"]})

    if has("HbA1c","Creatinine") and v("HbA1c") >= 6.5 and v("Creatinine") > 1.2:
        insights.append({"cat":"Multi-organ","sev":"warning",
            "title":"⚠️ خطر اعتلال الكلى السكري",
            "en":f"HbA1c {v('HbA1c')}% (diabetic) + Creatinine {v('Creatinine')} ↑. High risk of diabetic nephropathy. Essential: urine ACR, eGFR trend, BP control, fundoscopy, SGLT2i consideration.",
            "ar":f"HbA1c مرتفع + كرياتينين مرتفع = خطر اعتلال الكلى السكري. ACR في البول عاجل.",
            "refs":["ADA 2025","KDIGO 2024"]})

    if has("TSH","Hgb","MCV"):
        hgb_low = (sex=="male" and v("Hgb") < 13.5) or (v("Hgb") < 12.0)
        if v("TSH") > 4 and hgb_low and v("MCV") > 100:
            insights.append({"cat":"Multi-organ","sev":"info",
                "title":"ℹ️ قصور الدرق + فقر دم كبير الكريات",
                "en":f"TSH {v('TSH')} (hypothyroid) + Hgb {v('Hgb')} ↓ + MCV {v('MCV')} fL (macrocytic). Hypothyroidism can cause macrocytic anemia. Also check B12/folate (co-deficient in autoimmune thyroiditis).",
                "ar":"قصور الدرق + فقر دم كبير الكريات — الدرق يسبب فقر دم. تحقق من B12 وفولات.",
                "refs":["ATA 2024","BSH 2024"]})

    # Sort: critical → warning → info
    order = {"critical": 0, "warning": 1, "info": 2}
    insights.sort(key=lambda x: order.get(x["sev"], 3))
    return insights

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
    background: linear-gradient(135deg, #c0390a 0%, #e85d10 50%, #f39c12 100%);
    padding: 1.5rem 2rem; border-radius: 16px; margin-bottom: 1.5rem;
    text-align: center; box-shadow: 0 4px 20px rgba(200,60,10,0.4);
  }
  .main-header h1 { color: white; font-size: 2rem; font-weight: 900; margin: 0; }
  .main-header p  { color: rgba(255,255,255,0.88); margin: 0.3rem 0 0; font-size: 0.95rem; }

  .insight-critical { background: linear-gradient(135deg,#1a0505,#2d0a0a); border:1px solid #ff4444;
                       border-left:5px solid #ff4444; border-radius:10px; padding:1rem 1.2rem; margin:0.5rem 0; }
  .insight-warning  { background: linear-gradient(135deg,#1a1200,#2d1f00); border:1px solid #ffaa00;
                       border-left:5px solid #ffaa00; border-radius:10px; padding:1rem 1.2rem; margin:0.5rem 0; }
  .insight-info     { background: linear-gradient(135deg,#001a2d,#002d4d); border:1px solid #0088ff;
                       border-left:5px solid #0088ff; border-radius:10px; padding:1rem 1.2rem; margin:0.5rem 0; }

  .summary-box  { background:#1a1d24; border:1px solid #2a2d35; border-radius:12px;
                   padding:1rem; margin-bottom:1rem; text-align:center; }
  .kpi-number   { font-size:2.2rem; font-weight:900; }
  .kpi-label    { font-size:0.8rem; color:#888; margin-top:-0.3rem; }

  .panel-header { background:linear-gradient(90deg,rgba(230,93,16,0.18),transparent);
                   border-left:4px solid #e85d10; padding:0.45rem 0.9rem;
                   border-radius:0 8px 8px 0; margin:1.2rem 0 0.6rem;
                   font-weight:800; font-size:1rem; color:#f39c12; }
  .arabic-note  { direction:rtl; text-align:right; font-size:0.85rem; color:#aaa;
                   border-top:1px solid #333; margin-top:0.5rem; padding-top:0.5rem; }

  .stTabs [data-baseweb="tab-list"] { background:#1a1d24; border-radius:10px; gap:4px; padding:4px; }
  .stTabs [data-baseweb="tab"]      { border-radius:8px; font-weight:600; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <h1>🧬 Orange Lab Results Analyzer</h1>
  <p>Clinical Intelligence Engine — Cross-Validation & Pattern Recognition</p>
  <p style="font-size:0.8rem;color:rgba(255,255,255,0.65);">6th October City • Giza • Egypt | No API required — Fully offline</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 👤 بيانات المريض")
    patient_name = st.text_input("Patient Name / اسم المريض", placeholder="اختياري")
    c1, c2 = st.columns(2)
    with c1:
        sex = st.selectbox("الجنس", ["unspecified","male","female"],
                           format_func=lambda x: {"unspecified":"غير محدد","male":"ذكر","female":"أنثى"}[x])
    with c2:
        age_val = st.number_input("العمر", 0, 120, 0, 1)
        age = age_val if age_val > 0 else None

    st.markdown("---")
    st.markdown("### 📋 اختر البانلات")
    selected_panels = [p for p in PANELS if st.checkbox(p, value=False, key=f"panel_{p}")]

    if selected_panels:
        n_tests = sum(len(PANELS[p]) for p in selected_panels)
        st.caption(f"✅ {len(selected_panels)} بانل — {n_tests} تحليل")

    st.markdown("---")
    st.caption("📚 ADA 2025 | KDIGO 2024 | EASL 2023\nACC/AHA 2024 | ATA 2024 | ESC 2023\nTietz 7th | Henry's 23rd | WHO/ICSH")

# ── Main Input ────────────────────────────────────────────────────────────────
results = {}

if not selected_panels:
    st.info("👈 اختر البانلات من الشريط الجانبي للبدء في إدخال النتائج.")
else:
    for panel_name in selected_panels:
        st.markdown(f'<div class="panel-header">🔬 {panel_name}</div>', unsafe_allow_html=True)
        keys  = PANELS[panel_name]
        cols  = st.columns(3)
        for i, key in enumerate(keys):
            if key not in REF:
                continue
            ref = REF[key]
            # Determine reference hint for placeholder
            lo_show = ref.get("lo_m" if sex=="male" else "lo_f" if sex=="female" else "lo", ref["lo"])
            hi_show = ref.get("hi_m" if sex=="male" else "hi_f" if sex=="female" else "hi", ref["hi"])
            with cols[i % 3]:
                v_entered = st.number_input(
                    label=f"{ref['label']} ({ref['unit']})",
                    min_value=0.0, max_value=99999.0, value=0.0,
                    step=0.01, format="%.2f",
                    key=f"inp_{key}",
                    help=f"عربي: {ref['label_ar']} | المرجع: {lo_show}–{hi_show} {ref['unit']}"
                )
                if v_entered > 0:
                    results[key] = v_entered

# ── Run Button ────────────────────────────────────────────────────────────────
st.markdown("---")
col_btn, col_clr = st.columns([4, 1])
with col_btn:
    run = st.button(
        f"🚀 تحليل النتائج ({len(results)} تحليل مُدخل)",
        type="primary", use_container_width=True,
        disabled=(len(results) == 0)
    )
with col_clr:
    if st.button("🗑️ مسح الكل", use_container_width=True):
        st.rerun()

# ── Results Display ───────────────────────────────────────────────────────────
if run and results:
    st.markdown("---")
    pt = f"**{patient_name}**" if patient_name else "المريض"
    sx = f" | {'ذكر' if sex=='male' else 'أنثى' if sex=='female' else ''}"
    ag = f" | العمر: {age}" if age else ""
    st.markdown(f"## 📊 نتائج التحليل — {pt}{sx}{ag}")

    # ── KPI Cards ─────────────────────────────────────────────────────────────
    flagged = []
    for k, val in results.items():
        if k not in REF:
            continue
        ref   = REF[k]
        stat, lo, hi = get_status(k, val, sex)
        flagged.append({"key":k, "label":ref["label"], "label_ar":ref["label_ar"],
                         "value":val, "unit":ref["unit"], "status":stat,
                         "lo":lo, "hi":hi, "category":ref["category"]})

    n_hi   = sum(1 for f in flagged if f["status"]=="high")
    n_lo   = sum(1 for f in flagged if f["status"]=="low")
    n_norm = sum(1 for f in flagged if f["status"]=="normal")

    k1, k2, k3, k4 = st.columns(4)
    for col, num, label, color in [
        (k1, len(flagged), "إجمالي التحاليل", "#aaa"),
        (k2, n_hi,         "مرتفع ↑",         "#ff6b6b"),
        (k3, n_lo,         "منخفض ↓",         "#74b9ff"),
        (k4, n_norm,       "طبيعي ✓",         "#55efc4"),
    ]:
        col.markdown(
            f'<div class="summary-box">'
            f'<div class="kpi-number" style="color:{color}">{num}</div>'
            f'<div class="kpi-label">{label}</div></div>',
            unsafe_allow_html=True
        )

    # ── Results Table by Category ─────────────────────────────────────────────
    st.markdown("### 🔬 النتائج الفردية")
    cats = {}
    for f in flagged:
        cats.setdefault(f["category"], []).append(f)

    for cat_name, cat_flags in cats.items():
        with st.expander(f"**{cat_name}** — {len(cat_flags)} تحليل", expanded=True):
            rows = []
            for f in cat_flags:
                icon = "🔴" if f["status"]=="high" else "🔵" if f["status"]=="low" else "🟢"
                ref_str = f"{f['lo']}–{f['hi']} {f['unit']}" if f["lo"] is not None else "—"
                rows.append({
                    "التحليل": f["label"],
                    "بالعربي": f["label_ar"],
                    "القيمة":  f"{f['value']:.2f}",
                    "الوحدة":  f["unit"],
                    "الحالة":  f"{icon} {'مرتفع' if f['status']=='high' else 'منخفض' if f['status']=='low' else 'طبيعي'}",
                    "المرجع":  ref_str,
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # ── Clinical Intelligence ─────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🧠 التحليل الإكلينيكي — Cross-Validation Insights")
    insights = run_cross_validation(results, sex=sex, age=age)

    if not insights:
        st.success("✅ لا توجد تنبيهات cross-validation مهمة. النتائج تبدو متسقة داخلياً.")
    else:
        nc = sum(1 for i in insights if i["sev"]=="critical")
        nw = sum(1 for i in insights if i["sev"]=="warning")
        ni = sum(1 for i in insights if i["sev"]=="info")
        st.markdown(f"**{len(insights)} تنبيه:** 🔴 {nc} حرج | ⚠️ {nw} تحذير | ℹ️ {ni} معلومة")

        for ins in insights:
            with st.expander(ins["title"], expanded=(ins["sev"]=="critical")):
                st.markdown(f'<div class="insight-{ins["sev"]}">', unsafe_allow_html=True)
                st.markdown("**📋 التفسير الإكلينيكي:**")
                st.markdown(ins["en"])
                st.markdown(f'<div class="arabic-note">📝 {ins["ar"]}</div>', unsafe_allow_html=True)
                if ins.get("refs"):
                    st.markdown(f"<small>📚 {' | '.join(ins['refs'])}</small>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

    # ── Disclaimer ────────────────────────────────────────────────────────────
    st.markdown("---")
    st.caption("⚕️ تنبيه إكلينيكي: هذا البرنامج للدعم القراري فقط — يجب تفسير النتائج في السياق الإكلينيكي من قِبل طبيب مختص.")
    st.caption("📚 ADA 2025 | KDIGO 2024 | EASL 2023 | ACC/AHA 2024 | ATA 2024 | ESC 2023 | Tietz 7th Ed | Henry's 23rd Ed | WHO/ICSH | Endocrine Society 2024")

st.markdown("---")
st.markdown(
    '<div style="text-align:center;color:#555;font-size:0.8rem;">'
    '🧡 Orange Lab Results Analyzer v2.0 | 6th October City, Giza, Egypt'
    '</div>',
    unsafe_allow_html=True
)
