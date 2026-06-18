# =============================================================================
# Orange Lab Results Analyzer - Reference Ranges Database
# Based on: Tietz Clinical Chemistry, Henry's Clinical Diagnosis,
#           ADA 2025, KDIGO, EASL, ACC/AHA, WHO/ICSH guidelines
# =============================================================================

REFERENCE_RANGES = {

    # =========================================================================
    # GLUCOSE & DIABETES
    # =========================================================================
    "FBG": {
        "label": "Fasting Blood Glucose",
        "label_ar": "سكر الصيام",
        "unit": "mg/dL",
        "alt_units": {"mmol/L": 0.0555},
        "ranges": {
            "normal":      (70, 99),
            "prediabetes": (100, 125),
            "diabetes":    (126, float("inf")),
            "hypoglycemia":(0, 69),
        },
        "category": "Glucose",
        "panel": "Chemistry",
    },
    "RBG": {
        "label": "Random Blood Glucose",
        "label_ar": "سكر عشوائي",
        "unit": "mg/dL",
        "alt_units": {"mmol/L": 0.0555},
        "ranges": {
            "normal":   (0, 139),
            "concern":  (140, 199),
            "diabetes": (200, float("inf")),
        },
        "category": "Glucose",
        "panel": "Chemistry",
    },
    "2hPP": {
        "label": "2-hour Post-prandial Glucose",
        "label_ar": "سكر بعد الأكل",
        "unit": "mg/dL",
        "alt_units": {"mmol/L": 0.0555},
        "ranges": {
            "normal":      (0, 139),
            "prediabetes": (140, 199),
            "diabetes":    (200, float("inf")),
        },
        "category": "Glucose",
        "panel": "Chemistry",
    },
    "HbA1c": {
        "label": "Glycated Hemoglobin A1c",
        "label_ar": "السكر التراكمي",
        "unit": "%",
        "alt_units": {"mmol/mol": 10.93},
        "ranges": {
            "normal":      (0, 5.6),
            "prediabetes": (5.7, 6.4),
            "diabetes":    (6.5, float("inf")),
        },
        "category": "Glucose",
        "panel": "Chemistry",
    },
    "Insulin": {
        "label": "Fasting Insulin",
        "label_ar": "الأنسولين الصيامي",
        "unit": "µIU/mL",
        "alt_units": {},
        "ranges": {
            "normal": (2.6, 24.9),
        },
        "category": "Glucose",
        "panel": "Chemistry",
    },

    # =========================================================================
    # KIDNEY FUNCTION
    # =========================================================================
    "Creatinine": {
        "label": "Serum Creatinine",
        "label_ar": "كرياتينين الدم",
        "unit": "mg/dL",
        "alt_units": {"µmol/L": 88.4},
        "ranges": {
            "normal_male":   (0.7, 1.2),
            "normal_female": (0.5, 1.0),
            "normal":        (0.5, 1.2),
        },
        "category": "Kidney",
        "panel": "Chemistry",
    },
    "Urea": {
        "label": "Blood Urea Nitrogen (BUN)",
        "label_ar": "يوريا الدم",
        "unit": "mg/dL",
        "alt_units": {"mmol/L": 0.357},
        "ranges": {
            "normal": (7, 20),
        },
        "category": "Kidney",
        "panel": "Chemistry",
    },
    "UricAcid": {
        "label": "Uric Acid",
        "label_ar": "حمض اليوريك",
        "unit": "mg/dL",
        "alt_units": {"µmol/L": 59.48},
        "ranges": {
            "normal_male":   (3.4, 7.0),
            "normal_female": (2.4, 6.0),
            "normal":        (2.4, 7.0),
        },
        "category": "Kidney",
        "panel": "Chemistry",
    },
    "eGFR": {
        "label": "Estimated GFR (CKD-EPI)",
        "label_ar": "معدل الترشيح الكبيبي",
        "unit": "mL/min/1.73m²",
        "alt_units": {},
        "ranges": {
            "G1_normal":    (90, float("inf")),
            "G2_mild":      (60, 89),
            "G3a_moderate": (45, 59),
            "G3b_moderate": (30, 44),
            "G4_severe":    (15, 29),
            "G5_failure":   (0, 14),
        },
        "category": "Kidney",
        "panel": "Chemistry",
    },

    # =========================================================================
    # LIVER FUNCTION
    # =========================================================================
    "ALT": {
        "label": "Alanine Aminotransferase",
        "label_ar": "إنزيم الكبد ALT",
        "unit": "U/L",
        "alt_units": {},
        "ranges": {
            "normal_male":   (7, 56),
            "normal_female": (7, 45),
            "normal":        (7, 56),
        },
        "category": "Liver",
        "panel": "Chemistry",
    },
    "AST": {
        "label": "Aspartate Aminotransferase",
        "label_ar": "إنزيم الكبد AST",
        "unit": "U/L",
        "alt_units": {},
        "ranges": {
            "normal_male":   (10, 40),
            "normal_female": (10, 35),
            "normal":        (10, 40),
        },
        "category": "Liver",
        "panel": "Chemistry",
    },
    "ALP": {
        "label": "Alkaline Phosphatase",
        "label_ar": "الفوسفاتاز القلوي",
        "unit": "U/L",
        "alt_units": {},
        "ranges": {
            "normal_adult": (44, 147),
            "normal":       (44, 147),
        },
        "category": "Liver",
        "panel": "Chemistry",
    },
    "GGT": {
        "label": "Gamma-Glutamyl Transferase",
        "label_ar": "إنزيم GGT",
        "unit": "U/L",
        "alt_units": {},
        "ranges": {
            "normal_male":   (8, 61),
            "normal_female": (5, 36),
            "normal":        (5, 61),
        },
        "category": "Liver",
        "panel": "Chemistry",
    },
    "TBili": {
        "label": "Total Bilirubin",
        "label_ar": "البيليروبين الكلي",
        "unit": "mg/dL",
        "alt_units": {"µmol/L": 17.1},
        "ranges": {
            "normal": (0.2, 1.2),
        },
        "category": "Liver",
        "panel": "Chemistry",
    },
    "DBili": {
        "label": "Direct Bilirubin",
        "label_ar": "البيليروبين المباشر",
        "unit": "mg/dL",
        "alt_units": {"µmol/L": 17.1},
        "ranges": {
            "normal": (0.0, 0.3),
        },
        "category": "Liver",
        "panel": "Chemistry",
    },
    "Albumin": {
        "label": "Serum Albumin",
        "label_ar": "الألبومين",
        "unit": "g/dL",
        "alt_units": {"g/L": 10},
        "ranges": {
            "normal": (3.5, 5.0),
        },
        "category": "Liver",
        "panel": "Chemistry",
    },
    "TotalProtein": {
        "label": "Total Protein",
        "label_ar": "البروتين الكلي",
        "unit": "g/dL",
        "alt_units": {"g/L": 10},
        "ranges": {
            "normal": (6.3, 8.2),
        },
        "category": "Liver",
        "panel": "Chemistry",
    },

    # =========================================================================
    # LIPID PANEL
    # =========================================================================
    "TC": {
        "label": "Total Cholesterol",
        "label_ar": "الكوليسترول الكلي",
        "unit": "mg/dL",
        "alt_units": {"mmol/L": 0.0259},
        "ranges": {
            "desirable":     (0, 199),
            "borderline":    (200, 239),
            "high":          (240, float("inf")),
        },
        "category": "Lipids",
        "panel": "Chemistry",
    },
    "TG": {
        "label": "Triglycerides",
        "label_ar": "الدهون الثلاثية",
        "unit": "mg/dL",
        "alt_units": {"mmol/L": 0.0113},
        "ranges": {
            "normal":      (0, 149),
            "borderline":  (150, 199),
            "high":        (200, 499),
            "very_high":   (500, float("inf")),
        },
        "category": "Lipids",
        "panel": "Chemistry",
    },
    "LDL": {
        "label": "LDL Cholesterol",
        "label_ar": "الكوليسترول الضار",
        "unit": "mg/dL",
        "alt_units": {"mmol/L": 0.0259},
        "ranges": {
            "optimal":     (0, 99),
            "near_optimal":(100, 129),
            "borderline":  (130, 159),
            "high":        (160, 189),
            "very_high":   (190, float("inf")),
        },
        "category": "Lipids",
        "panel": "Chemistry",
    },
    "HDL": {
        "label": "HDL Cholesterol",
        "label_ar": "الكوليسترول المفيد",
        "unit": "mg/dL",
        "alt_units": {"mmol/L": 0.0259},
        "ranges": {
            "low_male":    (0, 39),
            "low_female":  (0, 49),
            "normal_male": (40, 59),
            "normal_female":(50, 59),
            "high":        (60, float("inf")),
            "normal":      (40, float("inf")),
        },
        "category": "Lipids",
        "panel": "Chemistry",
    },

    # =========================================================================
    # THYROID
    # =========================================================================
    "TSH": {
        "label": "Thyroid Stimulating Hormone",
        "label_ar": "هرمون الغدة الدرقية TSH",
        "unit": "µIU/mL",
        "alt_units": {"mIU/L": 1},
        "ranges": {
            "normal": (0.4, 4.0),
        },
        "category": "Thyroid",
        "panel": "Chemistry",
    },
    "FT4": {
        "label": "Free Thyroxine",
        "label_ar": "الثيروكسين الحر FT4",
        "unit": "ng/dL",
        "alt_units": {"pmol/L": 12.87},
        "ranges": {
            "normal": (0.8, 1.8),
        },
        "category": "Thyroid",
        "panel": "Chemistry",
    },
    "FT3": {
        "label": "Free Triiodothyronine",
        "label_ar": "الثيرونين الحر FT3",
        "unit": "pg/mL",
        "alt_units": {"pmol/L": 1.54},
        "ranges": {
            "normal": (2.3, 4.2),
        },
        "category": "Thyroid",
        "panel": "Chemistry",
    },

    # =========================================================================
    # IRON STUDIES
    # =========================================================================
    "SerumFe": {
        "label": "Serum Iron",
        "label_ar": "حديد الدم",
        "unit": "µg/dL",
        "alt_units": {"µmol/L": 0.179},
        "ranges": {
            "normal_male":   (65, 175),
            "normal_female": (50, 170),
            "normal":        (50, 175),
        },
        "category": "Iron",
        "panel": "Chemistry",
    },
    "TIBC": {
        "label": "Total Iron Binding Capacity",
        "label_ar": "طاقة ربط الحديد الكلية",
        "unit": "µg/dL",
        "alt_units": {"µmol/L": 0.179},
        "ranges": {
            "normal": (250, 370),
        },
        "category": "Iron",
        "panel": "Chemistry",
    },
    "Ferritin": {
        "label": "Serum Ferritin",
        "label_ar": "فيريتين الدم",
        "unit": "ng/mL",
        "alt_units": {"µg/L": 1},
        "ranges": {
            "normal_male":   (24, 336),
            "normal_female": (11, 307),
            "normal":        (11, 336),
        },
        "category": "Iron",
        "panel": "Chemistry",
    },

    # =========================================================================
    # CBC - HEMATOLOGY
    # =========================================================================
    "Hgb": {
        "label": "Hemoglobin",
        "label_ar": "الهيموجلوبين",
        "unit": "g/dL",
        "alt_units": {"g/L": 10},
        "ranges": {
            "normal_male":   (13.5, 17.5),
            "normal_female": (12.0, 15.5),
            "normal":        (12.0, 17.5),
        },
        "category": "CBC",
        "panel": "Hematology",
    },
    "Hct": {
        "label": "Hematocrit",
        "label_ar": "الهيماتوكريت",
        "unit": "%",
        "alt_units": {},
        "ranges": {
            "normal_male":   (41, 53),
            "normal_female": (36, 46),
            "normal":        (36, 53),
        },
        "category": "CBC",
        "panel": "Hematology",
    },
    "RBC": {
        "label": "Red Blood Cell Count",
        "label_ar": "عدد كريات الدم الحمراء",
        "unit": "×10⁶/µL",
        "alt_units": {"×10¹²/L": 1},
        "ranges": {
            "normal_male":   (4.5, 5.9),
            "normal_female": (4.0, 5.2),
            "normal":        (4.0, 5.9),
        },
        "category": "CBC",
        "panel": "Hematology",
    },
    "MCV": {
        "label": "Mean Corpuscular Volume",
        "label_ar": "متوسط حجم كريات الدم",
        "unit": "fL",
        "alt_units": {},
        "ranges": {
            "normal": (80, 100),
        },
        "category": "CBC",
        "panel": "Hematology",
    },
    "MCH": {
        "label": "Mean Corpuscular Hemoglobin",
        "label_ar": "متوسط هيموجلوبين الكريات",
        "unit": "pg",
        "alt_units": {},
        "ranges": {
            "normal": (27, 33),
        },
        "category": "CBC",
        "panel": "Hematology",
    },
    "MCHC": {
        "label": "Mean Corpuscular Hgb Concentration",
        "label_ar": "تركيز هيموجلوبين الكريات",
        "unit": "g/dL",
        "alt_units": {},
        "ranges": {
            "normal": (32, 36),
        },
        "category": "CBC",
        "panel": "Hematology",
    },
    "RDW": {
        "label": "Red Cell Distribution Width",
        "label_ar": "توزيع حجم كريات الدم",
        "unit": "%",
        "alt_units": {},
        "ranges": {
            "normal": (11.5, 14.5),
        },
        "category": "CBC",
        "panel": "Hematology",
    },
    "WBC": {
        "label": "White Blood Cell Count",
        "label_ar": "كريات الدم البيضاء",
        "unit": "×10³/µL",
        "alt_units": {"×10⁹/L": 1},
        "ranges": {
            "normal": (4.5, 11.0),
        },
        "category": "CBC",
        "panel": "Hematology",
    },
    "Neutrophils": {
        "label": "Neutrophils",
        "label_ar": "النيوتروفيل",
        "unit": "%",
        "alt_units": {},
        "ranges": {
            "normal": (50, 70),
        },
        "category": "CBC",
        "panel": "Hematology",
    },
    "Lymphocytes": {
        "label": "Lymphocytes",
        "label_ar": "الليمفاويات",
        "unit": "%",
        "alt_units": {},
        "ranges": {
            "normal": (20, 40),
        },
        "category": "CBC",
        "panel": "Hematology",
    },
    "Monocytes": {
        "label": "Monocytes",
        "label_ar": "المونوسيت",
        "unit": "%",
        "alt_units": {},
        "ranges": {
            "normal": (2, 8),
        },
        "category": "CBC",
        "panel": "Hematology",
    },
    "Eosinophils": {
        "label": "Eosinophils",
        "label_ar": "الحمضات",
        "unit": "%",
        "alt_units": {},
        "ranges": {
            "normal": (1, 4),
        },
        "category": "CBC",
        "panel": "Hematology",
    },
    "Basophils": {
        "label": "Basophils",
        "label_ar": "القاعدات",
        "unit": "%",
        "alt_units": {},
        "ranges": {
            "normal": (0, 1),
        },
        "category": "CBC",
        "panel": "Hematology",
    },
    "Platelets": {
        "label": "Platelet Count",
        "label_ar": "الصفائح الدموية",
        "unit": "×10³/µL",
        "alt_units": {"×10⁹/L": 1},
        "ranges": {
            "normal": (150, 400),
        },
        "category": "CBC",
        "panel": "Hematology",
    },
    "Reticulocytes": {
        "label": "Reticulocyte Count",
        "label_ar": "الشبكيات",
        "unit": "%",
        "alt_units": {},
        "ranges": {
            "normal": (0.5, 2.5),
        },
        "category": "CBC",
        "panel": "Hematology",
    },
}

# Panel groupings for UI
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
