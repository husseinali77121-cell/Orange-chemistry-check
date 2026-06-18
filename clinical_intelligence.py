# =============================================================================
# Orange Lab Results Analyzer - Clinical Intelligence Engine
# Cross-validation rules based on:
# ADA 2025, KDIGO, EASL, ACC/AHA, Tietz Clinical Chemistry, Henry's
# =============================================================================

def get_status(key, value, sex="unspecified"):
    """Return (status, range_label) for a test value."""
    from modules.reference_ranges import REFERENCE_RANGES
    if key not in REFERENCE_RANGES:
        return "unknown", "N/A"
    
    ref = REFERENCE_RANGES[key]
    ranges = ref["ranges"]
    
    # Pick sex-specific range if available
    if sex == "male" and "normal_male" in ranges:
        lo, hi = ranges["normal_male"]
    elif sex == "female" and "normal_female" in ranges:
        lo, hi = ranges["normal_female"]
    elif "normal" in ranges:
        lo, hi = ranges["normal"]
    else:
        lo, hi = list(ranges.values())[0]
    
    if value < lo:
        return "low", f"↓ Low (ref: {lo}–{hi})"
    elif value > hi:
        return "high", f"↑ High (ref: {lo}–{hi})"
    else:
        return "normal", f"✓ Normal ({lo}–{hi})"


def run_cross_validation(results: dict, sex="unspecified", age=None) -> list:
    """
    Main intelligence engine.
    results: dict of {test_key: float_value}
    Returns list of insight dicts with keys:
      - category, severity, title, body_en, body_ar, references
    """
    insights = []
    r = results  # shorthand

    def has(*keys):
        return all(k in r for k in keys)

    def val(k):
        return r.get(k)

    # =========================================================================
    # 1. GLUCOSE / HbA1c CROSS-CHECKS
    # =========================================================================
    if has("FBG", "HbA1c"):
        fbg = val("FBG")
        hba1c = val("HbA1c")
        estimated_avg_glucose = (hba1c * 28.7) - 46.7  # ADA formula

        discordance = abs(fbg - estimated_avg_glucose)

        if fbg >= 126 and hba1c < 5.7:
            insights.append({
                "category": "Glucose",
                "severity": "warning",
                "title": "⚠️ FBG High — HbA1c Discordant (Falsely Normal HbA1c?)",
                "body_en": (
                    f"FBG is {fbg} mg/dL (diabetic range) but HbA1c is {hba1c}% (normal). "
                    f"Expected average glucose from HbA1c: ~{estimated_avg_glucose:.0f} mg/dL.\n\n"
                    "Possible causes:\n"
                    "• Hemoglobin variants (HbS, HbC, HbE, thalassemia) → falsely low HbA1c\n"
                    "• Hemolytic anemia → shortened RBC lifespan\n"
                    "• Recent blood transfusion\n"
                    "• Iron deficiency anemia (can falsely elevate or lower HbA1c)\n\n"
                    "Recommendation: Check CBC, reticulocytes, hemoglobin electrophoresis. "
                    "Consider fructosamine as alternative glycemic marker."
                ),
                "body_ar": (
                    f"سكر الصيام {fbg} (مستوى السكري) لكن HbA1c {hba1c}% (طبيعي) — تناقض مهم.\n"
                    "الأسباب المحتملة: هيموجلوبين غير طبيعي (الثلاسيميا، HbS) أو فقر دم انحلالي.\n"
                    "يُنصح بعمل CBC وكهربة الهيموجلوبين."
                ),
                "references": ["ADA Standards of Care 2025", "IFCC HbA1c Standardization"]
            })

        elif fbg < 100 and hba1c >= 6.5:
            insights.append({
                "category": "Glucose",
                "severity": "warning",
                "title": "⚠️ HbA1c Diabetic — FBG Normal (Falsely Elevated HbA1c?)",
                "body_en": (
                    f"HbA1c {hba1c}% (diabetic) but FBG {fbg} mg/dL (normal). "
                    "Possible causes:\n"
                    "• Iron deficiency anemia → falsely elevated HbA1c\n"
                    "• Vitamin B12 deficiency\n"
                    "• Splenectomy (longer RBC lifespan)\n"
                    "• Uremia\n\n"
                    "Recommendation: Check iron studies, B12, renal function."
                ),
                "body_ar": (
                    f"HbA1c {hba1c}% (مستوى السكري) لكن سكر الصيام طبيعي {fbg}.\n"
                    "محتمل: نقص الحديد أو B12 يرفع HbA1c كاذباً.\n"
                    "يُنصح: فيريتين، B12، وظائف كلى."
                ),
                "references": ["ADA 2025", "Tietz Clinical Chemistry 7th Ed"]
            })

        elif discordance > 50:
            insights.append({
                "category": "Glucose",
                "severity": "info",
                "title": "ℹ️ FBG vs HbA1c — Significant Discordance",
                "body_en": (
                    f"Estimated average glucose from HbA1c {hba1c}%: ~{estimated_avg_glucose:.0f} mg/dL. "
                    f"Measured FBG: {fbg} mg/dL. Difference: {discordance:.0f} mg/dL.\n"
                    "This may indicate glucose variability, post-meal spikes missed by fasting glucose, "
                    "or pre-analytical issues."
                ),
                "body_ar": (
                    f"الفرق بين متوسط الجلوكوز المقدر من HbA1c والسكر المقيس = {discordance:.0f} mg/dL.\n"
                    "قد يدل على تذبذب في مستوى السكر خلال اليوم."
                ),
                "references": ["ADA 2025"]
            })

    # =========================================================================
    # 2. KIDNEY: BUN:Creatinine RATIO
    # =========================================================================
    if has("Urea", "Creatinine"):
        urea = val("Urea")
        cr = val("Creatinine")
        ratio = urea / cr if cr > 0 else 0

        if ratio > 40:
            insights.append({
                "category": "Kidney",
                "severity": "critical",
                "title": "🔴 BUN:Creatinine Ratio > 40 — Suspect Upper GI Bleeding",
                "body_en": (
                    f"BUN:Creatinine ratio = {ratio:.1f} (normal 10–20). "
                    "Very high ratio (>40) strongly suggests upper GI bleeding "
                    "(blood protein digested → elevated BUN without proportional creatinine rise). "
                    "Also consider: severe dehydration, high protein diet.\n"
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
                "category": "Kidney",
                "severity": "warning",
                "title": "⚠️ BUN:Creatinine Ratio > 20 — Pre-renal Azotemia",
                "body_en": (
                    f"BUN:Creatinine ratio = {ratio:.1f}. "
                    "Elevated ratio suggests pre-renal causes: dehydration, heart failure, "
                    "decreased renal perfusion, high protein intake, or GI bleeding.\n"
                    "Recommendation: Assess hydration status and volume."
                ),
                "body_ar": (
                    f"نسبة يوريا/كرياتينين = {ratio:.1f} — أعلى من الطبيعي.\n"
                    "محتمل: جفاف، قصور قلب، أو نزيف هضمي."
                ),
                "references": ["KDIGO AKI Guidelines 2024"]
            })
        elif ratio < 10 and urea < 7:
            insights.append({
                "category": "Kidney",
                "severity": "info",
                "title": "ℹ️ Low BUN:Creatinine Ratio — Consider Liver Disease or Low Protein",
                "body_en": (
                    f"BUN:Creatinine ratio = {ratio:.1f} (low). "
                    "Low ratio with low BUN may indicate: liver disease (reduced urea synthesis), "
                    "very low protein diet, SIADH, or malnutrition.\n"
                    "Correlate with liver function tests."
                ),
                "body_ar": (
                    f"نسبة يوريا/كرياتينين منخفضة = {ratio:.1f}.\n"
                    "محتمل: مرض كبدي أو نظام غذائي منخفض البروتين."
                ),
                "references": ["Tietz 7th Ed", "EASL Guidelines"]
            })

    # =========================================================================
    # 3. LIVER PATTERN RECOGNITION
    # =========================================================================
    if has("ALT", "AST"):
        alt = val("ALT")
        ast = val("AST")
        alt_uln = 56  # Upper limit of normal
        ast_uln = 40

        # De Ritis Ratio (AST/ALT)
        de_ritis = ast / alt if alt > 0 else 0

        if alt > alt_uln or ast > ast_uln:
            if de_ritis >= 2.0:
                insights.append({
                    "category": "Liver",
                    "severity": "warning",
                    "title": "⚠️ De Ritis Ratio ≥ 2 — Alcoholic Liver Disease Pattern",
                    "body_en": (
                        f"AST/ALT (De Ritis) ratio = {de_ritis:.1f}. "
                        "Ratio ≥ 2 is highly suggestive of alcoholic liver disease. "
                        f"AST {ast} U/L, ALT {alt} U/L.\n"
                        "Also consider: cirrhosis, cardiac hepatopathy.\n"
                        "Recommendation: Correlate with clinical history and GGT."
                    ),
                    "body_ar": (
                        f"نسبة AST/ALT (De Ritis) = {de_ritis:.1f} — تشير لمرض الكبد الكحولي.\n"
                        "يُنصح: مقارنة مع GGT والتاريخ الإكلينيكي."
                    ),
                    "references": ["EASL Alcohol-Related Liver Disease 2023", "Henry's 23rd Ed"]
                })

            if has("ALP"):
                alp = val("ALP")
                alp_uln = 147

                # Hepatocellular vs Cholestatic pattern
                alt_x = alt / alt_uln
                alp_x = alp / alp_uln
                r_ratio = alt_x / alp_x if alp_x > 0 else 0

                if r_ratio >= 5:
                    pattern = "Hepatocellular"
                    pattern_ar = "تلف خلوي كبدي"
                elif r_ratio <= 2:
                    pattern = "Cholestatic"
                    pattern_ar = "انسدادي / ركود صفراوي"
                else:
                    pattern = "Mixed"
                    pattern_ar = "مختلط"

                insights.append({
                    "category": "Liver",
                    "severity": "info",
                    "title": f"ℹ️ Liver Injury Pattern: {pattern}",
                    "body_en": (
                        f"R-ratio (ALT/ULN ÷ ALP/ULN) = {r_ratio:.1f} → {pattern} pattern.\n"
                        f"• ALT: {alt} U/L ({alt/alt_uln:.1f}× ULN)\n"
                        f"• AST: {ast} U/L\n"
                        f"• ALP: {alp} U/L ({alp/alp_uln:.1f}× ULN)\n\n"
                        + (
                            "Hepatocellular causes: viral hepatitis, drug-induced, ischemic, autoimmune."
                            if pattern == "Hepatocellular" else
                            "Cholestatic causes: bile duct obstruction, PBC, PSC, drug-induced cholestasis."
                            if pattern == "Cholestatic" else
                            "Mixed pattern: could be drug-induced or overlap syndrome."
                        )
                    ),
                    "body_ar": (
                        f"نمط إصابة الكبد: {pattern_ar} (R-ratio = {r_ratio:.1f})."
                    ),
                    "references": ["EASL DILI Guidelines 2023", "RUCAM Scale"]
                })

            # Very high transaminases
            if alt > 1000 or ast > 1000:
                insights.append({
                    "category": "Liver",
                    "severity": "critical",
                    "title": "🔴 Massively Elevated Transaminases (>1000 U/L)",
                    "body_en": (
                        f"ALT {alt} U/L, AST {ast} U/L — extreme elevation.\n"
                        "Top differential:\n"
                        "1. Acute viral hepatitis (HAV, HBV, HEV)\n"
                        "2. Ischemic hepatitis ('shock liver') — check cardiac status\n"
                        "3. Drug/toxin-induced (paracetamol overdose, mushroom poisoning)\n"
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

    # =========================================================================
    # 4. LIPID PANEL — FRIEDEWALD VALIDITY
    # =========================================================================
    if has("TC", "TG", "HDL", "LDL"):
        tc = val("TC")
        tg = val("TG")
        hdl = val("HDL")
        ldl = val("LDL")

        # Friedewald calculated LDL
        friedewald_ldl = tc - hdl - (tg / 5)

        if tg > 400:
            insights.append({
                "category": "Lipids",
                "severity": "critical",
                "title": "🔴 TG > 400 — Friedewald LDL Formula INVALID",
                "body_en": (
                    f"Triglycerides = {tg} mg/dL. The Friedewald equation (LDL = TC − HDL − TG/5) "
                    "is UNRELIABLE when TG > 400 mg/dL due to VLDL particle heterogeneity.\n"
                    "Reported LDL may be significantly underestimated.\n"
                    "Recommendation: Order direct LDL measurement or use Martin-Hopkins equation."
                ),
                "body_ar": (
                    f"الدهون الثلاثية {tg} — معادلة Friedewald لحساب LDL غير صحيحة.\n"
                    "يجب قياس LDL المباشر (Direct LDL)."
                ),
                "references": ["ACC/AHA 2024 Lipid Guidelines", "Martin-Hopkins Equation 2013"]
            })
        elif tg > 200:
            diff = abs(ldl - friedewald_ldl)
            if diff > 20:
                insights.append({
                    "category": "Lipids",
                    "severity": "info",
                    "title": "ℹ️ TG > 200 — Friedewald LDL May Be Less Accurate",
                    "body_en": (
                        f"TG = {tg} mg/dL. Friedewald-estimated LDL = {friedewald_ldl:.0f} mg/dL "
                        f"vs. reported LDL = {ldl} mg/dL (difference {diff:.0f} mg/dL). "
                        "Consider Martin-Hopkins equation for better accuracy."
                    ),
                    "body_ar": (
                        f"الدهون الثلاثية {tg} — LDL المحسوب قد يكون أقل دقة.\n"
                        "يُنصح بمعادلة Martin-Hopkins."
                    ),
                    "references": ["ACC/AHA 2024"]
                })

        # Atherogenic dyslipidemia pattern
        if tg > 150 and hdl < 40:
            insights.append({
                "category": "Lipids",
                "severity": "warning",
                "title": "⚠️ Atherogenic Dyslipidemia Pattern (↑TG + ↓HDL)",
                "body_en": (
                    f"TG {tg} mg/dL + HDL {hdl} mg/dL — classic atherogenic dyslipidemia. "
                    "High cardiovascular risk pattern, commonly associated with:\n"
                    "• Insulin resistance / metabolic syndrome\n"
                    "• Type 2 diabetes\n"
                    "• Obesity\n"
                    "Recommendation: Assess for metabolic syndrome (waist circumference, BP, FBG)."
                ),
                "body_ar": (
                    f"دهون ثلاثية مرتفعة ({tg}) + HDL منخفض ({hdl}) = نمط خطر قلبي وعائي.\n"
                    "مرتبط بمقاومة الإنسولين والسكري. يُنصح بتقييم متلازمة التمثيل الغذائي."
                ),
                "references": ["ACC/AHA 2024", "IDF Metabolic Syndrome Definition"]
            })

    # =========================================================================
    # 5. THYROID AXIS LOGIC
    # =========================================================================
    if has("TSH", "FT4"):
        tsh = val("TSH")
        ft4 = val("FT4")

        if tsh > 4.0 and ft4 < 0.8:
            insights.append({
                "category": "Thyroid",
                "severity": "warning",
                "title": "⚠️ Primary Hypothyroidism Pattern",
                "body_en": (
                    f"TSH {tsh} µIU/mL (↑) + FT4 {ft4} ng/dL (↓) = Primary hypothyroidism. "
                    "Causes: Hashimoto's thyroiditis, post-thyroidectomy, iodine deficiency, drugs (amiodarone, lithium).\n"
                    "Recommendation: Anti-TPO antibodies, Anti-thyroglobulin."
                ),
                "body_ar": (
                    f"TSH مرتفع ({tsh}) + FT4 منخفض ({ft4}) = قصور الغدة الدرقية الأولي.\n"
                    "الأسباب الشائعة: هاشيموتو، ما بعد استئصال الغدة."
                ),
                "references": ["ATA Guidelines 2024", "NICE Thyroid 2023"]
            })
        elif tsh < 0.4 and ft4 > 1.8:
            insights.append({
                "category": "Thyroid",
                "severity": "warning",
                "title": "⚠️ Primary Hyperthyroidism Pattern",
                "body_en": (
                    f"TSH {tsh} µIU/mL (↓) + FT4 {ft4} ng/dL (↑) = Primary hyperthyroidism. "
                    "Causes: Graves' disease, toxic nodular goiter, thyroiditis.\n"
                    "Recommendation: Anti-TSH receptor antibodies (TRAb), thyroid scan."
                ),
                "body_ar": (
                    f"TSH منخفض ({tsh}) + FT4 مرتفع ({ft4}) = فرط نشاط الغدة الدرقية.\n"
                    "الأسباب: مرض جريفز، عقيدات سامة."
                ),
                "references": ["ATA 2024", "ETA Guidelines"]
            })
        elif tsh < 0.4 and ft4 < 0.8:
            insights.append({
                "category": "Thyroid",
                "severity": "warning",
                "title": "⚠️ Central Hypothyroidism Pattern",
                "body_en": (
                    f"TSH {tsh} µIU/mL (↓) + FT4 {ft4} ng/dL (↓) = Central hypothyroidism. "
                    "Caused by pituitary or hypothalamic dysfunction (not thyroid itself).\n"
                    "Recommendation: MRI pituitary, prolactin, cortisol panel, other pituitary hormones."
                ),
                "body_ar": (
                    f"TSH منخفض + FT4 منخفض = قصور درقي مركزي (نخامية أو وطائية).\n"
                    "يُنصح: MRI نخامية وبروفايل هرمونات كاملة."
                ),
                "references": ["ETA 2023", "Pituitary Society Guidelines"]
            })
        elif tsh > 4.0 and 0.8 <= ft4 <= 1.8:
            insights.append({
                "category": "Thyroid",
                "severity": "info",
                "title": "ℹ️ Subclinical Hypothyroidism",
                "body_en": (
                    f"TSH {tsh} µIU/mL (↑) + FT4 {ft4} ng/dL (normal). "
                    "Subclinical hypothyroidism — monitor every 6–12 months. "
                    "Consider treatment if TSH > 10 or symptomatic."
                ),
                "body_ar": (
                    f"TSH مرتفع + FT4 طبيعي = قصور درقي تحت الإكلينيكي.\n"
                    "متابعة كل 6-12 شهر. علاج لو TSH > 10."
                ),
                "references": ["ATA 2024"]
            })

    # =========================================================================
    # 6. IRON STUDIES PATTERN
    # =========================================================================
    if has("SerumFe", "TIBC", "Ferritin"):
        fe = val("SerumFe")
        tibc = val("TIBC")
        ferritin = val("Ferritin")
        sat = (fe / tibc * 100) if tibc > 0 else 0

        fe_low = fe < 60
        fe_high = fe > 170
        tibc_high = tibc > 370
        tibc_low = tibc < 250
        ferritin_low = ferritin < 12
        ferritin_high = ferritin > 300
        sat_low = sat < 20
        sat_high = sat > 45

        if fe_low and tibc_high and ferritin_low and sat_low:
            insights.append({
                "category": "Iron",
                "severity": "warning",
                "title": "⚠️ Classic Iron Deficiency Pattern",
                "body_en": (
                    f"Fe ↓ ({fe} µg/dL) + TIBC ↑ ({tibc}) + Ferritin ↓ ({ferritin}) + "
                    f"Sat {sat:.0f}% ↓ = Iron deficiency.\n"
                    "Causes: Blood loss (GI, menstrual), malabsorption, inadequate intake.\n"
                    "Recommendation: Identify and treat the underlying cause."
                ),
                "body_ar": (
                    f"حديد منخفض + TIBC مرتفع + فيريتين منخفض = نقص الحديد الكلاسيكي.\n"
                    "أسباب: فقدان دم، سوء امتصاص."
                ),
                "references": ["WHO Iron Deficiency 2023", "BSH Guidelines"]
            })
        elif fe_low and tibc_low and ferritin_high:
            insights.append({
                "category": "Iron",
                "severity": "warning",
                "title": "⚠️ Anemia of Chronic Disease Pattern",
                "body_en": (
                    f"Fe ↓ ({fe}) + TIBC ↓ ({tibc}) + Ferritin ↑ ({ferritin}) = "
                    "Anemia of chronic disease (ACD). "
                    "Body sequesters iron in response to inflammation/infection.\n"
                    "Common in: chronic infections, malignancy, autoimmune disease, CKD.\n"
                    "Note: Ferritin is an acute phase reactant — elevated in inflammation."
                ),
                "body_ar": (
                    f"حديد منخفض + TIBC منخفض + فيريتين مرتفع = فقر دم الأمراض المزمنة.\n"
                    "شائع في: التهابات مزمنة، سرطان، أمراض كلوية."
                ),
                "references": ["ASH 2023", "KDIGO Anemia Guidelines"]
            })
        elif fe_high and sat_high and ferritin_high:
            insights.append({
                "category": "Iron",
                "severity": "critical",
                "title": "🔴 Iron Overload Pattern — Rule Out Hemochromatosis",
                "body_en": (
                    f"Fe ↑ ({fe}) + Sat {sat:.0f}% (>45%) + Ferritin ↑ ({ferritin}) = "
                    "Iron overload. Rule out hereditary hemochromatosis (HFE gene mutation).\n"
                    "Also consider: repeated transfusions, liver disease causing secondary overload.\n"
                    "Recommendation: HFE genetic testing, liver imaging, LFTs."
                ),
                "body_ar": (
                    f"حديد مرتفع + تشبع مرتفع + فيريتين مرتفع = تراكم الحديد.\n"
                    "يُشك في داء ترسب الأصبغة الدموية (Hemochromatosis). فحص جيني HFE."
                ),
                "references": ["EASL Hemochromatosis 2022", "BSH 2023"]
            })
        elif ferritin_high and not fe_high:
            insights.append({
                "category": "Iron",
                "severity": "info",
                "title": "ℹ️ Elevated Ferritin with Normal Iron — Likely Acute Phase Reactant",
                "body_en": (
                    f"Ferritin {ferritin} ng/mL elevated but serum iron {fe} is normal. "
                    "Ferritin is an acute phase protein — rises in:\n"
                    "• Infection / inflammation / sepsis\n"
                    "• Liver disease\n"
                    "• Malignancy\n"
                    "• Metabolic syndrome\n"
                    "Isolated elevated ferritin ≠ iron overload. Check CRP/ESR."
                ),
                "body_ar": (
                    f"فيريتين مرتفع ({ferritin}) مع حديد طبيعي = بروتين الطور الحاد.\n"
                    "لا يعني بالضرورة زيادة الحديد. تحقق من CRP وESR."
                ),
                "references": ["BSH Ferritin Guidelines 2023"]
            })

    # =========================================================================
    # 7. CBC PATTERN RECOGNITION
    # =========================================================================

    # Anemia classification
    if has("Hgb", "MCV"):
        hgb = val("Hgb")
        mcv = val("MCV")
        hgb_low = (sex == "male" and hgb < 13.5) or (sex == "female" and hgb < 12.0) or (sex == "unspecified" and hgb < 12.0)

        if hgb_low:
            if mcv < 80:
                if has("RDW"):
                    rdw = val("RDW")
                    if rdw > 14.5:
                        insights.append({
                            "category": "CBC",
                            "severity": "warning",
                            "title": "⚠️ Microcytic Anemia + High RDW — Likely Iron Deficiency",
                            "body_en": (
                                f"Hgb {hgb} g/dL (↓) + MCV {mcv} fL (microcytic) + RDW {rdw}% (↑). "
                                "High RDW with microcytosis = anisocytosis consistent with iron deficiency anemia (IDA). "
                                "Thalassemia trait typically has NORMAL RDW.\n"
                                "Recommendation: Iron studies (Fe, TIBC, Ferritin)."
                            ),
                            "body_ar": (
                                f"Hgb منخفض + MCV صغير + RDW مرتفع = فقر دم بنقص الحديد (على الأرجح).\n"
                                "الثلاسيميا الحاملة: RDW عادةً طبيعي.\n"
                                "يُنصح: دراسات الحديد."
                            ),
                            "references": ["Bessman Index", "WHO Anemia 2023"]
                        })
                    else:
                        insights.append({
                            "category": "CBC",
                            "severity": "info",
                            "title": "ℹ️ Microcytic Anemia + Normal RDW — Consider Thalassemia Trait",
                            "body_en": (
                                f"Hgb {hgb} g/dL (↓) + MCV {mcv} fL (microcytic) + RDW {rdw}% (normal). "
                                "Normal RDW with microcytosis suggests thalassemia trait over IDA.\n"
                                "Recommendation: Hemoglobin electrophoresis, iron studies."
                            ),
                            "body_ar": (
                                f"Hgb منخفض + MCV صغير + RDW طبيعي = محتمل الثلاسيميا الحاملة.\n"
                                "يُنصح: كهربة الهيموجلوبين."
                            ),
                            "references": ["Mentzer Index", "BSH Thalassemia 2023"]
                        })

            elif mcv > 100:
                insights.append({
                    "category": "CBC",
                    "severity": "warning",
                    "title": "⚠️ Macrocytic Anemia — B12/Folate Deficiency?",
                    "body_en": (
                        f"Hgb {hgb} g/dL (↓) + MCV {mcv} fL (macrocytic).\n"
                        "Differential:\n"
                        "• B12 deficiency (commonest, especially in elderly, vegans, metformin use)\n"
                        "• Folate deficiency\n"
                        "• Alcohol use\n"
                        "• Hypothyroidism\n"
                        "• Medications (methotrexate, hydroxyurea, azathioprine)\n"
                        "• Myelodysplastic syndrome (MDS)\n"
                        "Recommendation: B12, folate, reticulocyte count, peripheral blood film."
                    ),
                    "body_ar": (
                        f"Hgb منخفض + MCV كبير = فقر دم كبير الكريات.\n"
                        "الأسباب: نقص B12 أو حمض الفوليك، الكحول، هيبوثيرويد.\n"
                        "يُنصح: B12، فولات، فيلم دم محيطي."
                    ),
                    "references": ["BSH B12/Folate 2024", "WHO Anemia Classification"]
                })

    # WBC patterns
    if has("WBC", "Neutrophils", "Lymphocytes"):
        wbc = val("WBC")
        neut_pct = val("Neutrophils")
        lymph_pct = val("Lymphocytes")
        neut_abs = wbc * neut_pct / 100
        lymph_abs = wbc * lymph_pct / 100

        if wbc > 11 and neut_abs > 7.5:
            insights.append({
                "category": "CBC",
                "severity": "info",
                "title": "ℹ️ Neutrophilia — Bacterial Infection / Stress Response",
                "body_en": (
                    f"WBC {wbc} ×10³/µL (↑) with neutrophilia (absolute neutrophils {neut_abs:.1f}). "
                    "Common causes: bacterial infection, physiologic stress, corticosteroids, "
                    "smoking, inflammatory conditions.\n"
                    "If severe leukocytosis (>30): consider leukemoid reaction or CML (check BCR-ABL)."
                ),
                "body_ar": (
                    f"WBC مرتفع مع نيوتروفيليا ({neut_abs:.1f} ×10³) = كريات بيضاء ارتفاع جرثومي محتمل.\n"
                    "لو WBC > 30: استبعد ردة فعل الابيضاض أو CML."
                ),
                "references": ["Henry's 23rd Ed", "WHO CML Guidelines"]
            })
        elif wbc < 4.5 and neut_abs < 1.8:
            severity = "critical" if neut_abs < 0.5 else "warning"
            grade = "Severe (Agranulocytosis)" if neut_abs < 0.5 else "Moderate" if neut_abs < 1.0 else "Mild"
            insights.append({
                "category": "CBC",
                "severity": severity,
                "title": f"{'🔴' if severity=='critical' else '⚠️'} Neutropenia — {grade}",
                "body_en": (
                    f"Absolute neutrophil count (ANC) = {neut_abs:.2f} ×10³/µL. Grade: {grade}.\n"
                    "Causes: viral infection, drug-induced (chemotherapy, carbimazole, clozapine), "
                    "autoimmune, B12/folate deficiency, aplastic anemia.\n"
                    + ("⚠️ URGENT: Risk of life-threatening infection. Reverse isolation!" if neut_abs < 0.5 else
                       "Monitor closely, review medications.")
                ),
                "body_ar": (
                    f"ANC = {neut_abs:.2f} — نقص النيوتروفيل ({grade}).\n"
                    + ("خطر عدوى شديد جداً — عزل عكسي عاجل!" if neut_abs < 0.5 else
                       "مراقبة دقيقة ومراجعة الأدوية.")
                ),
                "references": ["CTCAE Grading", "IDSA Febrile Neutropenia 2024"]
            })

        if wbc > 11 and lymph_abs > 4.0:
            insights.append({
                "category": "CBC",
                "severity": "info",
                "title": "ℹ️ Lymphocytosis — Viral Infection / CLL?",
                "body_en": (
                    f"Absolute lymphocytes = {lymph_abs:.1f} ×10³/µL (↑). "
                    "Causes: viral infections (EBV, CMV, COVID-19), whooping cough, "
                    "CLL (if persistent >5.0 in adults >50).\n"
                    "Recommendation: Peripheral film, consider flow cytometry if persistent."
                ),
                "body_ar": (
                    f"لمفاويات مرتفعة ({lymph_abs:.1f} ×10³) = عدوى فيروسية محتملة أو CLL.\n"
                    "يُنصح: فيلم دم محيطي."
                ),
                "references": ["WHO CLL Guidelines", "Henry's 23rd Ed"]
            })

    # =========================================================================
    # 8. LIVER + KIDNEY CORRELATION
    # =========================================================================
    if has("ALT", "AST", "Creatinine", "Urea"):
        alt = val("ALT")
        cr = val("Creatinine")
        albumin = val("Albumin") if has("Albumin") else None

        if (alt > 56 or (albumin and albumin < 3.5)) and cr > 1.5:
            insights.append({
                "category": "Multi-organ",
                "severity": "warning",
                "title": "⚠️ Combined Liver + Kidney Dysfunction",
                "body_en": (
                    f"Elevated transaminases (ALT {alt}) with elevated creatinine ({cr} mg/dL). "
                    "Consider:\n"
                    "• Hepatorenal syndrome (HRS) — in cirrhotic patients\n"
                    "• Sepsis-related multi-organ dysfunction\n"
                    "• Shock (ischemic hepatitis + prerenal AKI)\n"
                    "• Drug/toxin (paracetamol, NSAIDs)\n"
                    "• Systemic disease (SLE, sarcoidosis, amyloidosis)"
                ),
                "body_ar": (
                    "ارتفاع إنزيمات الكبد مع ارتفاع الكرياتينين = خلل كبدي كلوي مشترك.\n"
                    "يُشك في: متلازمة هيباتو-رينال، صدمة، أو سمية دواء."
                ),
                "references": ["EASL 2023", "KDIGO AKI 2024"]
            })

    # =========================================================================
    # 9. DIABETES + KIDNEY CORRELATION
    # =========================================================================
    if has("FBG", "HbA1c", "Creatinine"):
        hba1c = val("HbA1c")
        cr = val("Creatinine")
        egfr = val("eGFR") if has("eGFR") else None

        if hba1c >= 6.5 and cr > 1.2:
            insights.append({
                "category": "Multi-organ",
                "severity": "warning",
                "title": "⚠️ Diabetic Nephropathy Risk — Poor Glycemic Control + Renal Impairment",
                "body_en": (
                    f"HbA1c {hba1c}% (diabetic) + Creatinine {cr} mg/dL (elevated). "
                    "Consider diabetic nephropathy as leading diagnosis.\n"
                    "Essential workup:\n"
                    "• Urine ACR (albumin:creatinine ratio) — microalbuminuria screening\n"
                    "• eGFR trend over time\n"
                    "• BP control assessment\n"
                    "• Fundoscopy (diabetic retinopathy correlation)"
                ),
                "body_ar": (
                    f"HbA1c مرتفع ({hba1c}%) + كرياتينين مرتفع ({cr}) = خطر اعتلال الكلى السكري.\n"
                    "يُنصح: نسبة ألبومين/كرياتينين في البول (ACR)، تتبع eGFR."
                ),
                "references": ["ADA Microvascular Complications 2025", "KDIGO Diabetes-CKD 2024"]
            })

    return insights


def flag_single_test(key, value, sex="unspecified") -> dict:
    """Return a single-test flag dict."""
    from modules.reference_ranges import REFERENCE_RANGES
    if key not in REFERENCE_RANGES:
        return {}

    ref = REFERENCE_RANGES[key]
    status, range_label = get_status(key, value, sex)

    return {
        "key": key,
        "label": ref["label"],
        "label_ar": ref["label_ar"],
        "value": value,
        "unit": ref["unit"],
        "status": status,
        "range_label": range_label,
        "category": ref["category"],
    }
