import { useState, useMemo } from "react";

// ═══════════════════════════════════════════════════════════════
// REFERENCE RANGES DATABASE — Tietz 7th, Henry's 23rd, ADA 2025,
// KDIGO, EASL, ACC/AHA, WHO/ICSH, AACE, ATA 2024
// ═══════════════════════════════════════════════════════════════

const REF = {
  // ── GLUCOSE & DIABETES ──────────────────────────────────────
  FBG:        { label:"Fasting Blood Glucose",          ar:"سكر الصيام",                unit:"mg/dL",         lo:70,   hi:99,    loM:null, hiM:null, loF:null, hiF:null, cat:"Glucose" },
  RBG:        { label:"Random Blood Glucose",           ar:"سكر عشوائي",                unit:"mg/dL",         lo:0,    hi:139,   cat:"Glucose" },
  PP2h:       { label:"2h Post-prandial Glucose",       ar:"سكر ما بعد الأكل",          unit:"mg/dL",         lo:0,    hi:139,   cat:"Glucose" },
  HbA1c:      { label:"Glycated Hemoglobin A1c",        ar:"السكر التراكمي",             unit:"%",             lo:0,    hi:5.6,   cat:"Glucose" },
  Insulin:    { label:"Fasting Insulin",                ar:"الأنسولين الصيامي",          unit:"µIU/mL",        lo:2.6,  hi:24.9,  cat:"Glucose" },
  HOMA_IR:    { label:"HOMA-IR (Insulin Resistance)",   ar:"مؤشر مقاومة الأنسولين",      unit:"index",         lo:0,    hi:2.5,   cat:"Glucose" },
  Fructosamine:{ label:"Fructosamine",                  ar:"فركتوزامين",                 unit:"µmol/L",        lo:190,  hi:280,   cat:"Glucose" },
  Cpeptide:   { label:"C-Peptide",                      ar:"الببتيد C",                  unit:"ng/mL",         lo:0.8,  hi:3.1,   cat:"Glucose" },
  GAD65:      { label:"GAD-65 Antibodies",              ar:"أجسام مضادة GAD-65",         unit:"U/mL",          lo:0,    hi:5,     cat:"Glucose" },

  // ── KIDNEY FUNCTION ──────────────────────────────────────────
  Creatinine: { label:"Serum Creatinine",               ar:"كرياتينين الدم",             unit:"mg/dL",         lo:0.7,  hi:1.2,   loM:0.7,hiM:1.2,loF:0.5,hiF:1.0, cat:"Kidney" },
  Urea:       { label:"Blood Urea Nitrogen (BUN)",      ar:"يوريا الدم",                unit:"mg/dL",         lo:7,    hi:20,    cat:"Kidney" },
  UricAcid:   { label:"Uric Acid",                      ar:"حمض اليوريك",               unit:"mg/dL",         lo:2.4,  hi:7.0,   loM:3.4,hiM:7.0,loF:2.4,hiF:6.0, cat:"Kidney" },
  eGFR:       { label:"Estimated GFR (CKD-EPI)",        ar:"معدل الترشيح الكبيبي",       unit:"mL/min/1.73m²", lo:90,   hi:999,   cat:"Kidney" },
  Cystatin_C: { label:"Cystatin C",                     ar:"سيستاتين C",                 unit:"mg/L",          lo:0.53, hi:0.95,  cat:"Kidney" },
  BetaTMG:    { label:"β2-Microglobulin",               ar:"بيتا-2 ميكروجلوبيولين",     unit:"mg/L",          lo:0,    hi:2.0,   cat:"Kidney" },
  uACR:       { label:"Urine Albumin:Creatinine Ratio", ar:"نسبة الألبومين/كرياتينين بول",unit:"mg/g",         lo:0,    hi:30,    cat:"Kidney" },
  uProtein:   { label:"Urine Total Protein (24h)",      ar:"بروتين البول الكلي (24 ساعة)",unit:"mg/24h",       lo:0,    hi:150,   cat:"Kidney" },
  PhosphorusS:{ label:"Serum Phosphorus",               ar:"فوسفور الدم",               unit:"mg/dL",         lo:2.5,  hi:4.5,   cat:"Kidney" },
  PTH:        { label:"Parathyroid Hormone (iPTH)",     ar:"هرمون الجارة الدرقية",       unit:"pg/mL",         lo:15,   hi:65,    cat:"Kidney" },

  // ── LIVER FUNCTION ───────────────────────────────────────────
  ALT:        { label:"Alanine Aminotransferase (ALT)", ar:"إنزيم الكبد ALT",           unit:"U/L",           lo:7,    hi:56,    loM:7,hiM:56,loF:7,hiF:45,    cat:"Liver" },
  AST:        { label:"Aspartate Aminotransferase (AST)",ar:"إنزيم الكبد AST",          unit:"U/L",           lo:10,   hi:40,    loM:10,hiM:40,loF:10,hiF:35,   cat:"Liver" },
  ALP:        { label:"Alkaline Phosphatase (ALP)",     ar:"الفوسفاتاز القلوي",          unit:"U/L",           lo:44,   hi:147,   cat:"Liver" },
  GGT:        { label:"Gamma-GT (GGT)",                 ar:"إنزيم GGT",                 unit:"U/L",           lo:5,    hi:61,    loM:8,hiM:61,loF:5,hiF:36,    cat:"Liver" },
  TBili:      { label:"Total Bilirubin",                ar:"البيليروبين الكلي",          unit:"mg/dL",         lo:0.2,  hi:1.2,   cat:"Liver" },
  DBili:      { label:"Direct Bilirubin",               ar:"البيليروبين المباشر",        unit:"mg/dL",         lo:0.0,  hi:0.3,   cat:"Liver" },
  IBili:      { label:"Indirect Bilirubin",             ar:"البيليروبين غير المباشر",    unit:"mg/dL",         lo:0.2,  hi:0.9,   cat:"Liver" },
  Albumin:    { label:"Serum Albumin",                  ar:"الألبومين",                 unit:"g/dL",          lo:3.5,  hi:5.0,   cat:"Liver" },
  TotalProt:  { label:"Total Protein",                  ar:"البروتين الكلي",             unit:"g/dL",          lo:6.3,  hi:8.2,   cat:"Liver" },
  LDH:        { label:"Lactate Dehydrogenase (LDH)",    ar:"إنزيم LDH",                 unit:"U/L",           lo:140,  hi:280,   cat:"Liver" },
  PT:         { label:"Prothrombin Time (PT)",          ar:"وقت البروثرومبين",           unit:"sec",           lo:11,   hi:13.5,  cat:"Liver" },
  INR:        { label:"INR",                            ar:"INR",                       unit:"ratio",         lo:0.8,  hi:1.2,   cat:"Liver" },
  APTT:       { label:"aPTT",                           ar:"aPTT",                      unit:"sec",           lo:25,   hi:35,    cat:"Liver" },
  AFP:        { label:"Alpha-Fetoprotein (AFP)",        ar:"الفيتوبروتين ألفا",          unit:"ng/mL",         lo:0,    hi:8.5,   cat:"Liver" },
  AMA:        { label:"Antimitochondrial Ab (AMA)",     ar:"أجسام مضادة ميتوكوندريا",    unit:"U/mL",          lo:0,    hi:20,    cat:"Liver" },
  ASMA:       { label:"Anti-Smooth Muscle Ab (ASMA)",   ar:"أجسام مضادة العضلات الملساء",unit:"U/mL",         lo:0,    hi:20,    cat:"Liver" },

  // ── LIPIDS ───────────────────────────────────────────────────
  TC:         { label:"Total Cholesterol",              ar:"الكوليسترول الكلي",          unit:"mg/dL",         lo:0,    hi:199,   cat:"Lipids" },
  TG:         { label:"Triglycerides",                  ar:"الدهون الثلاثية",            unit:"mg/dL",         lo:0,    hi:149,   cat:"Lipids" },
  LDL:        { label:"LDL Cholesterol",                ar:"الكوليسترول الضار (LDL)",    unit:"mg/dL",         lo:0,    hi:99,    cat:"Lipids" },
  HDL:        { label:"HDL Cholesterol",                ar:"الكوليسترول المفيد (HDL)",   unit:"mg/dL",         lo:40,   hi:999,   loM:40,hiM:999,loF:50,hiF:999, cat:"Lipids" },
  nonHDL:     { label:"Non-HDL Cholesterol",            ar:"كوليسترول غير HDL",          unit:"mg/dL",         lo:0,    hi:130,   cat:"Lipids" },
  VLDL:       { label:"VLDL Cholesterol",               ar:"كوليسترول VLDL",             unit:"mg/dL",         lo:2,    hi:30,    cat:"Lipids" },
  Lpa:        { label:"Lipoprotein(a)",                 ar:"ليبوبروتين (أ)",             unit:"mg/dL",         lo:0,    hi:30,    cat:"Lipids" },
  ApoA1:      { label:"Apolipoprotein A-I",             ar:"أبوليبوبروتين A-I",           unit:"mg/dL",         lo:119,  hi:240,   loM:119,hiM:240,loF:140,hiF:260, cat:"Lipids" },
  ApoB:       { label:"Apolipoprotein B",               ar:"أبوليبوبروتين B",             unit:"mg/dL",         lo:52,   hi:109,   cat:"Lipids" },
  hsCRP:      { label:"hs-CRP (Cardiac)",               ar:"البروتين التفاعلي C (قلبي)", unit:"mg/L",          lo:0,    hi:1.0,   cat:"Lipids" },

  // ── THYROID ──────────────────────────────────────────────────
  TSH:        { label:"TSH",                            ar:"هرمون الغدة الدرقية TSH",    unit:"µIU/mL",        lo:0.4,  hi:4.0,   cat:"Thyroid" },
  FT4:        { label:"Free T4 (FT4)",                  ar:"الثيروكسين الحر FT4",        unit:"ng/dL",         lo:0.8,  hi:1.8,   cat:"Thyroid" },
  FT3:        { label:"Free T3 (FT3)",                  ar:"الثيرونين الحر FT3",         unit:"pg/mL",         lo:2.3,  hi:4.2,   cat:"Thyroid" },
  TT4:        { label:"Total T4",                       ar:"الثيروكسين الكلي",           unit:"µg/dL",         lo:5.0,  hi:12.0,  cat:"Thyroid" },
  TT3:        { label:"Total T3",                       ar:"الثيرونين الكلي",            unit:"ng/dL",         lo:80,   hi:200,   cat:"Thyroid" },
  TRAb:       { label:"TSH Receptor Antibodies (TRAb)", ar:"أجسام مضادة مستقبلات TSH",  unit:"IU/L",          lo:0,    hi:1.75,  cat:"Thyroid" },
  AntiTPO:    { label:"Anti-TPO Antibodies",            ar:"أجسام مضادة TPO",            unit:"IU/mL",         lo:0,    hi:34,    cat:"Thyroid" },
  AntiTG:     { label:"Anti-Thyroglobulin Ab",          ar:"أجسام مضادة ثيروجلوبيولين",  unit:"IU/mL",         lo:0,    hi:115,   cat:"Thyroid" },
  Thyroglobulin:{ label:"Thyroglobulin (TG marker)",   ar:"ثيروجلوبيولين",              unit:"ng/mL",         lo:1.4,  hi:29.2,  cat:"Thyroid" },

  // ── IRON STUDIES ─────────────────────────────────────────────
  SerumFe:    { label:"Serum Iron",                     ar:"حديد الدم",                 unit:"µg/dL",         lo:50,   hi:175,   loM:65,hiM:175,loF:50,hiF:170, cat:"Iron" },
  TIBC:       { label:"Total Iron Binding Capacity",    ar:"طاقة ربط الحديد الكلية",     unit:"µg/dL",         lo:250,  hi:370,   cat:"Iron" },
  UIBC:       { label:"Unsaturated Iron Binding Capacity",ar:"طاقة ربط الحديد غير المشبعة",unit:"µg/dL",      lo:110,  hi:370,   cat:"Iron" },
  TfSat:      { label:"Transferrin Saturation (%)",     ar:"نسبة تشبع الترانسفيرين",     unit:"%",             lo:20,   hi:50,    cat:"Iron" },
  Ferritin:   { label:"Serum Ferritin",                 ar:"فيريتين الدم",               unit:"ng/mL",         lo:11,   hi:336,   loM:24,hiM:336,loF:11,hiF:307, cat:"Iron" },
  Transferrin:{ label:"Serum Transferrin",              ar:"ترانسفيرين الدم",            unit:"mg/dL",         lo:200,  hi:360,   cat:"Iron" },
  SolTfR:     { label:"Soluble Transferrin Receptor",   ar:"مستقبل الترانسفيرين الذائب", unit:"mg/L",          lo:0.83, hi:1.76,  cat:"Iron" },

  // ── BONE METABOLISM ──────────────────────────────────────────
  CalciumT:   { label:"Total Calcium",                  ar:"الكالسيوم الكلي",            unit:"mg/dL",         lo:8.5,  hi:10.5,  cat:"Bone" },
  CalciumI:   { label:"Ionized Calcium",                ar:"الكالسيوم المتأين",           unit:"mg/dL",         lo:4.65, hi:5.28,  cat:"Bone" },
  Phosphorus: { label:"Phosphorus",                     ar:"الفوسفور",                   unit:"mg/dL",         lo:2.5,  hi:4.5,   cat:"Bone" },
  Magnesium:  { label:"Magnesium",                      ar:"المغنيسيوم",                  unit:"mg/dL",         lo:1.7,  hi:2.4,   cat:"Bone" },
  VitD25:     { label:"25-OH Vitamin D",                ar:"فيتامين د",                  unit:"ng/mL",         lo:30,   hi:100,   cat:"Bone" },
  VitD125:    { label:"1,25-(OH)₂ Vitamin D (Calcitriol)",ar:"الكالسيتريول",             unit:"pg/mL",         lo:18,   hi:72,    cat:"Bone" },
  Osteocalcin:{ label:"Osteocalcin (Bone Gla Protein)", ar:"أوستيوكالسين",              unit:"ng/mL",         lo:3.1,  hi:13.7,  loM:3.1,hiM:13.7,loF:0.4,hiF:7.9, cat:"Bone" },
  bALP:       { label:"Bone-Specific ALP",              ar:"الفوسفاتاز القلوي العظمي",    unit:"µg/L",          lo:3.7,  hi:20.9,  cat:"Bone" },
  CTX:        { label:"CTX (C-Terminal Telopeptide)",   ar:"علامة ارتشاف العظام CTX",    unit:"ng/mL",         lo:0,    hi:0.573, cat:"Bone" },
  NTX:        { label:"NTX (N-Terminal Telopeptide)",   ar:"علامة ارتشاف العظام NTX",    unit:"nM BCE/L",      lo:0,    hi:65,    cat:"Bone" },
  PTH_bone:   { label:"PTH (intact)",                   ar:"هرمون الجارة الدرقية",       unit:"pg/mL",         lo:15,   hi:65,    cat:"Bone" },

  // ── ELECTROLYTES ─────────────────────────────────────────────
  Sodium:     { label:"Serum Sodium (Na⁺)",             ar:"صوديوم الدم",               unit:"mEq/L",         lo:136,  hi:145,   cat:"Electrolytes" },
  Potassium:  { label:"Serum Potassium (K⁺)",           ar:"بوتاسيوم الدم",              unit:"mEq/L",         lo:3.5,  hi:5.0,   cat:"Electrolytes" },
  Chloride:   { label:"Serum Chloride (Cl⁻)",           ar:"كلوريد الدم",               unit:"mEq/L",         lo:98,   hi:106,   cat:"Electrolytes" },
  Bicarbonate:{ label:"Serum Bicarbonate (HCO₃⁻)",      ar:"بيكربونات الدم",             unit:"mEq/L",         lo:22,   hi:29,    cat:"Electrolytes" },
  AnionGap:   { label:"Anion Gap (AG)",                  ar:"فجوة الأنيون",              unit:"mEq/L",         lo:8,    hi:16,    cat:"Electrolytes" },
  Osmolality: { label:"Serum Osmolality",               ar:"أسمولالية الدم",             unit:"mOsm/kg",       lo:275,  hi:295,   cat:"Electrolytes" },

  // ── CARDIAC MARKERS ──────────────────────────────────────────
  cTnI:       { label:"Cardiac Troponin I (cTnI)",      ar:"تروبونين القلب I",           unit:"ng/mL",         lo:0,    hi:0.04,  cat:"Cardiac" },
  cTnT:       { label:"Cardiac Troponin T (cTnT)",      ar:"تروبونين القلب T",           unit:"ng/mL",         lo:0,    hi:0.01,  cat:"Cardiac" },
  hsTnT:      { label:"High-Sensitivity Troponin T",    ar:"تروبونين عالي الحساسية",     unit:"ng/L",          lo:0,    hi:14,    cat:"Cardiac" },
  BNP:        { label:"BNP (Brain Natriuretic Peptide)", ar:"الببتيد الناتريوريتيكي",     unit:"pg/mL",         lo:0,    hi:100,   cat:"Cardiac" },
  NTproBNP:   { label:"NT-proBNP",                      ar:"NT-proBNP",                  unit:"pg/mL",         lo:0,    hi:125,   cat:"Cardiac" },
  CKtotal:    { label:"Total CK (Creatine Kinase)",     ar:"كرياتين كيناز الكلي",        unit:"U/L",           lo:30,   hi:200,   loM:39,hiM:308,loF:26,hiF:192, cat:"Cardiac" },
  CKMB:       { label:"CK-MB",                          ar:"كرياتين كيناز MB",           unit:"U/L",           lo:0,    hi:25,    cat:"Cardiac" },
  Myoglobin:  { label:"Myoglobin",                      ar:"الميوجلوبين",                unit:"ng/mL",         lo:0,    hi:90,    cat:"Cardiac" },
  hs_CRP:     { label:"hs-CRP",                         ar:"البروتين التفاعلي C عالي الحساسية",unit:"mg/L",    lo:0,    hi:1.0,   cat:"Cardiac" },
  Homocysteine:{ label:"Homocysteine",                  ar:"هوموسيستين",                 unit:"µmol/L",        lo:5,    hi:15,    cat:"Cardiac" },
  D_Dimer:    { label:"D-Dimer",                        ar:"D-ثنائي",                    unit:"µg/mL FEU",     lo:0,    hi:0.5,   cat:"Cardiac" },
  Fibrinogen: { label:"Fibrinogen",                     ar:"الفيبرينوجين",               unit:"mg/dL",         lo:200,  hi:400,   cat:"Cardiac" },

  // ── HORMONES — REPRODUCTIVE ──────────────────────────────────
  LH:         { label:"LH",                             ar:"الهرمون اللوتيني",           unit:"mIU/mL",        lo:1.7,  hi:8.6,   loM:1.7,hiM:8.6,loF:2.4,hiF:12.6, cat:"Reproductive" },
  FSH:        { label:"FSH",                            ar:"الهرمون المحفز للجريب",       unit:"mIU/mL",        lo:1.5,  hi:12.4,  loM:1.5,hiM:12.4,loF:3.5,hiF:12.5, cat:"Reproductive" },
  Estradiol:  { label:"Estradiol (E2)",                 ar:"الإستراديول",                unit:"pg/mL",         lo:19,   hi:160,   cat:"Reproductive" },
  Progesterone:{ label:"Progesterone",                  ar:"البروجيسترون",               unit:"ng/mL",         lo:0.1,  hi:0.9,   cat:"Reproductive" },
  Testosterone:{ label:"Total Testosterone",            ar:"التستوستيرون الكلي",          unit:"ng/dL",         lo:300,  hi:1000,  loM:300,hiM:1000,loF:15,hiF:70, cat:"Reproductive" },
  SHBG:       { label:"SHBG",                           ar:"بروتين ربط الهرمونات الجنسية",unit:"nmol/L",       lo:16.5, hi:55.9,  loM:16.5,hiM:55.9,loF:24.6,hiF:122.0, cat:"Reproductive" },
  Prolactin:  { label:"Prolactin (PRL)",                ar:"البرولاكتين",                unit:"ng/mL",         lo:2,    hi:18,    loM:2,hiM:18,loF:2,hiF:29, cat:"Reproductive" },
  DHEAS:      { label:"DHEA-S",                         ar:"DHEA-S",                     unit:"µg/dL",         lo:65,   hi:380,   loM:280,hiM:640,loF:65,hiF:380, cat:"Reproductive" },
  AMH:        { label:"Anti-Müllerian Hormone (AMH)",   ar:"هرمون AMH",                  unit:"ng/mL",         lo:1.0,  hi:3.5,   cat:"Reproductive" },
  hCG:        { label:"β-hCG",                          ar:"هرمون الحمل β-hCG",           unit:"mIU/mL",        lo:0,    hi:5,     cat:"Reproductive" },

  // ── ADRENAL & PITUITARY ──────────────────────────────────────
  Cortisol8am:{ label:"Cortisol (8 AM)",                ar:"الكورتيزول (8 صباحاً)",      unit:"µg/dL",         lo:6,    hi:23,    cat:"Adrenal" },
  Cortisol4pm:{ label:"Cortisol (4 PM)",                ar:"الكورتيزول (4 مساءً)",       unit:"µg/dL",         lo:2,    hi:11,    cat:"Adrenal" },
  ACTH:       { label:"ACTH",                           ar:"الهرمون الموجه لقشر الكظر",   unit:"pg/mL",         lo:10,   hi:60,    cat:"Adrenal" },
  Aldosterone:{ label:"Aldosterone",                    ar:"الألدوستيرون",               unit:"ng/dL",         lo:1,    hi:16,    cat:"Adrenal" },
  Renin:      { label:"Plasma Renin Activity",          ar:"نشاط الرينين البلازمي",       unit:"ng/mL/h",       lo:0.2,  hi:1.6,   cat:"Adrenal" },
  GrowthH:    { label:"Growth Hormone (GH)",            ar:"هرمون النمو",                unit:"ng/mL",         lo:0,    hi:0.97,  cat:"Adrenal" },
  IGF1:       { label:"IGF-1 (Somatomedin C)",          ar:"عامل النمو الشبيه بالإنسولين", unit:"ng/mL",        lo:116,  hi:358,   cat:"Adrenal" },
  Metanephrines:{ label:"Plasma Metanephrines",         ar:"ميتانفرين البلازما",          unit:"nmol/L",        lo:0,    hi:0.5,   cat:"Adrenal" },

  // ── TUMOR MARKERS ────────────────────────────────────────────
  CEA:        { label:"CEA",                            ar:"المستضد الجنيني السرطاني",    unit:"ng/mL",         lo:0,    hi:5,     cat:"TumorMarkers" },
  CA125:      { label:"CA-125",                         ar:"مؤشر سرطان CA-125",           unit:"U/mL",          lo:0,    hi:35,    cat:"TumorMarkers" },
  CA199:      { label:"CA 19-9",                        ar:"مؤشر سرطان CA 19-9",          unit:"U/mL",          lo:0,    hi:37,    cat:"TumorMarkers" },
  CA153:      { label:"CA 15-3",                        ar:"مؤشر سرطان الثدي CA 15-3",    unit:"U/mL",          lo:0,    hi:31,    cat:"TumorMarkers" },
  PSA:        { label:"PSA (Total)",                    ar:"مستضد البروستاتا النوعي",      unit:"ng/mL",         lo:0,    hi:4,     cat:"TumorMarkers" },
  fPSA:       { label:"Free PSA",                       ar:"PSA الحر",                    unit:"ng/mL",         lo:0,    hi:1.0,   cat:"TumorMarkers" },
  AFP_tumor:  { label:"AFP (Tumor Marker)",             ar:"الفيتوبروتين ألفا",           unit:"ng/mL",         lo:0,    hi:8.5,   cat:"TumorMarkers" },
  B2MG:       { label:"Beta-2 Microglobulin",           ar:"بيتا-2 ميكروجلوبيولين",      unit:"mg/L",          lo:0.8,  hi:2.4,   cat:"TumorMarkers" },
  NSE:        { label:"Neuron-Specific Enolase (NSE)",  ar:"إنولاز الخلايا العصبية",      unit:"ng/mL",         lo:0,    hi:16.3,  cat:"TumorMarkers" },
  Chromogranin:{ label:"Chromogranin A (CgA)",          ar:"كروموجرانين A",               unit:"ng/mL",         lo:0,    hi:100,   cat:"TumorMarkers" },
  CYFRA211:   { label:"CYFRA 21-1",                     ar:"سيتوكيراتين 21-1",            unit:"ng/mL",         lo:0,    hi:3.3,   cat:"TumorMarkers" },
  SCC:        { label:"SCC Antigen",                    ar:"مستضد سرطانة الخلايا الحرشفية",unit:"ng/mL",        lo:0,    hi:1.5,   cat:"TumorMarkers" },
  HE4:        { label:"HE4 (Human Epididymis Protein 4)",ar:"بروتين HE4 للمبيض",         unit:"pmol/L",        lo:0,    hi:70,    cat:"TumorMarkers" },

  // ── INFLAMMATION / AUTOIMMUNE ────────────────────────────────
  CRP:        { label:"C-Reactive Protein (CRP)",       ar:"البروتين التفاعلي C",         unit:"mg/L",          lo:0,    hi:5,     cat:"Inflammation" },
  ESR:        { label:"ESR (Westergren)",               ar:"سرعة ترسيب الدم",             unit:"mm/hr",         lo:0,    hi:20,    loM:0,hiM:15,loF:0,hiF:20, cat:"Inflammation" },
  Procalcitonin:{ label:"Procalcitonin (PCT)",          ar:"بروكالسيتونين",               unit:"ng/mL",         lo:0,    hi:0.1,   cat:"Inflammation" },
  IL6:        { label:"Interleukin-6 (IL-6)",           ar:"الإنترلوكين-6",               unit:"pg/mL",         lo:0,    hi:7,     cat:"Inflammation" },
  SAA:        { label:"Serum Amyloid A (SAA)",          ar:"الأميلويد A المصلي",           unit:"mg/L",          lo:0,    hi:10,    cat:"Inflammation" },
  RF:         { label:"Rheumatoid Factor (RF)",         ar:"عامل الروماتويد",             unit:"IU/mL",         lo:0,    hi:14,    cat:"Inflammation" },
  AntiCCP:    { label:"Anti-CCP Antibodies",            ar:"أجسام مضادة CCP",             unit:"U/mL",          lo:0,    hi:17,    cat:"Inflammation" },
  ANA:        { label:"ANA Titer",                      ar:"الأجسام المضادة النووية",      unit:"titer",         lo:0,    hi:40,    cat:"Inflammation" },
  AntiDS_DNA: { label:"Anti-dsDNA Antibodies",          ar:"أجسام مضادة DNA ثنائي السلسلة",unit:"IU/mL",        lo:0,    hi:7,     cat:"Inflammation" },
  Complement3:{ label:"Complement C3",                  ar:"مكمل C3",                    unit:"mg/dL",         lo:90,   hi:180,   cat:"Inflammation" },
  Complement4:{ label:"Complement C4",                  ar:"مكمل C4",                    unit:"mg/dL",         lo:16,   hi:47,    cat:"Inflammation" },

  // ── VITAMINS & NUTRITION ─────────────────────────────────────
  VitB12:     { label:"Vitamin B12",                    ar:"فيتامين B12",                 unit:"pg/mL",         lo:200,  hi:900,   cat:"Vitamins" },
  Folate:     { label:"Serum Folate (B9)",              ar:"حمض الفوليك",                 unit:"ng/mL",         lo:3.0,  hi:17.0,  cat:"Vitamins" },
  VitA:       { label:"Vitamin A (Retinol)",            ar:"فيتامين أ",                   unit:"µg/dL",         lo:30,   hi:65,    cat:"Vitamins" },
  VitE:       { label:"Vitamin E (α-Tocopherol)",       ar:"فيتامين هـ",                  unit:"mg/L",          lo:5,    hi:18,    cat:"Vitamins" },
  Zinc:       { label:"Serum Zinc",                     ar:"الزنك",                       unit:"µg/dL",         lo:70,   hi:120,   cat:"Vitamins" },
  Copper:     { label:"Serum Copper",                   ar:"النحاس",                      unit:"µg/dL",         lo:70,   hi:140,   cat:"Vitamins" },
  Selenium:   { label:"Serum Selenium",                 ar:"السيلينيوم",                  unit:"µg/L",          lo:70,   hi:150,   cat:"Vitamins" },
  Ceruloplasmin:{ label:"Ceruloplasmin",                ar:"سيرولوبلازمين",               unit:"mg/dL",         lo:20,   hi:50,    cat:"Vitamins" },

  // ── PANCREAS ─────────────────────────────────────────────────
  Amylase:    { label:"Serum Amylase",                  ar:"أميلاز الدم",                 unit:"U/L",           lo:30,   hi:110,   cat:"Pancreas" },
  Lipase:     { label:"Serum Lipase",                   ar:"ليباز الدم",                  unit:"U/L",           lo:7,    hi:60,    cat:"Pancreas" },
  CA199_p:    { label:"CA 19-9 (Pancreatic)",           ar:"CA 19-9 (بنكرياسي)",          unit:"U/mL",          lo:0,    hi:37,    cat:"Pancreas" },
  Glucagon:   { label:"Glucagon",                       ar:"الجلوكاجون",                  unit:"pg/mL",         lo:50,   hi:100,   cat:"Pancreas" },
  VIP:        { label:"Vasoactive Intestinal Peptide",  ar:"الببتيد المعوي الفعال بالأوعية",unit:"pg/mL",       lo:0,    hi:30,    cat:"Pancreas" },

  // ── INFECTIOUS DISEASE SEROLOGY ──────────────────────────────
  HBsAg:      { label:"HBsAg (Hepatitis B Surface Ag)", ar:"مستضد سطح التهاب B",          unit:"qualitative",   lo:0,    hi:0,     cat:"Serology", qualitative:true, negLabel:"Non-reactive", posLabel:"Reactive" },
  AntiHBs:    { label:"Anti-HBs (Hepatitis B Ab)",      ar:"أجسام مضادة التهاب B",        unit:"mIU/mL",        lo:10,   hi:999,   cat:"Serology" },
  AntiHCV:    { label:"Anti-HCV (Hepatitis C Ab)",       ar:"أجسام مضادة التهاب C",        unit:"qualitative",   lo:0,    hi:0,     cat:"Serology", qualitative:true },
  AntiHIV:    { label:"Anti-HIV 1+2",                   ar:"أجسام مضادة HIV",             unit:"qualitative",   lo:0,    hi:0,     cat:"Serology", qualitative:true },
  HCV_RNA:    { label:"HCV RNA (Viral Load)",           ar:"الحمل الفيروسي لالتهاب C",    unit:"IU/mL",         lo:0,    hi:0,     cat:"Serology", qualitative:true },
  HBV_DNA:    { label:"HBV DNA (Viral Load)",           ar:"الحمل الفيروسي لالتهاب B",    unit:"IU/mL",         lo:0,    hi:0,     cat:"Serology", qualitative:true },
};

// ── PANELS ────────────────────────────────────────────────────
const PANELS = {
  "🩺 Glucose & Diabetes":    { keys:["FBG","RBG","PP2h","HbA1c","Insulin","HOMA_IR","Fructosamine","Cpeptide"], icon:"🩺", color:"#f39c12" },
  "🫘 Kidney Function":       { keys:["Creatinine","Urea","UricAcid","eGFR","Cystatin_C","uACR","uProtein","PhosphorusS","PTH"], icon:"🫘", color:"#3498db" },
  "🫀 Liver Function":        { keys:["ALT","AST","ALP","GGT","TBili","DBili","IBili","Albumin","TotalProt","LDH","PT","INR","AFP"], icon:"🫀", color:"#e74c3c" },
  "💊 Lipid Panel":           { keys:["TC","TG","LDL","HDL","nonHDL","VLDL","Lpa","ApoA1","ApoB","hsCRP"], icon:"💊", color:"#9b59b6" },
  "🦋 Thyroid":               { keys:["TSH","FT4","FT3","TT4","TT3","AntiTPO","AntiTG","TRAb","Thyroglobulin"], icon:"🦋", color:"#1abc9c" },
  "🔩 Iron Studies":          { keys:["SerumFe","TIBC","UIBC","TfSat","Ferritin","Transferrin","SolTfR"], icon:"🔩", color:"#e67e22" },
  "🦴 Bone Metabolism":       { keys:["CalciumT","CalciumI","Phosphorus","Magnesium","VitD25","VitD125","PTH_bone","Osteocalcin","bALP","CTX","NTX"], icon:"🦴", color:"#7f8c8d" },
  "⚡ Electrolytes":          { keys:["Sodium","Potassium","Chloride","Bicarbonate","AnionGap","Osmolality"], icon:"⚡", color:"#27ae60" },
  "❤️ Cardiac Markers":      { keys:["cTnI","cTnT","hsTnT","BNP","NTproBNP","CKtotal","CKMB","Myoglobin","D_Dimer","Fibrinogen","Homocysteine","hs_CRP"], icon:"❤️", color:"#c0392b" },
  "🔬 Inflammation":          { keys:["CRP","ESR","Procalcitonin","IL6","RF","AntiCCP","ANA","AntiDS_DNA","Complement3","Complement4","SAA"], icon:"🔬", color:"#d35400" },
  "⚗️ Hormones":             { keys:["LH","FSH","Estradiol","Progesterone","Testosterone","SHBG","Prolactin","DHEAS","AMH","hCG","Cortisol8am","ACTH","Aldosterone","GrowthH","IGF1"], icon:"⚗️", color:"#8e44ad" },
  "🧬 Tumor Markers":         { keys:["CEA","CA125","CA199","CA153","PSA","fPSA","AFP_tumor","B2MG","NSE","Chromogranin","CYFRA211","SCC","HE4"], icon:"🧬", color:"#2c3e50" },
  "💊 Vitamins & Nutrition":  { keys:["VitB12","Folate","VitD25","VitA","VitE","Zinc","Copper","Selenium","Ceruloplasmin"], icon:"💊", color:"#16a085" },
  "🫁 Pancreas":              { keys:["Amylase","Lipase","CA199_p","Glucagon"], icon:"🫁", color:"#f1c40f" },
};

// ── CLINICAL INSIGHTS ENGINE ─────────────────────────────────
function getStatus(key, val, sex = "unspecified") {
  const r = REF[key];
  if (!r) return { status: "unknown", lo: null, hi: null };
  let lo = r.lo, hi = r.hi;
  if (sex === "male" && r.loM != null) { lo = r.loM; hi = r.hiM; }
  else if (sex === "female" && r.loF != null) { lo = r.loF; hi = r.hiF; }
  if (r.qualitative) return { status: "qualitative", lo, hi };
  if (val < lo) return { status: "low", lo, hi };
  if (val > hi) return { status: "high", lo, hi };
  return { status: "normal", lo, hi };
}

function runInsights(vals, sex, age) {
  const insights = [];
  const has = (...keys) => keys.every(k => vals[k] != null && vals[k] > 0);
  const v = k => vals[k];

  // ─ Glucose cross-checks ─
  if (has("FBG", "HbA1c")) {
    const fbg = v("FBG"), h = v("HbA1c");
    const eag = h * 28.7 - 46.7;
    if (fbg >= 126 && h < 5.7)
      insights.push({ sev:"warning", cat:"Glucose", title:"⚠️ FBG مرتفع — HbA1c منخفض كاذب؟", en:`FBG ${fbg} (diabetic range) but HbA1c ${h}% (normal). Consider hemoglobin variants (HbS, thalassemia), hemolytic anemia, or recent transfusion. Recommend: CBC, reticulocytes, Hb electrophoresis, fructosamine.`, ar:`سكر الصيام في نطاق السكري لكن HbA1c طبيعي — تناقض. محتمل: هيموجلوبين غير طبيعي أو فقر دم انحلالي.`, refs:["ADA 2025","IFCC"] });
    else if (fbg < 100 && h >= 6.5)
      insights.push({ sev:"warning", cat:"Glucose", title:"⚠️ HbA1c مرتفع — سكر الصيام طبيعي (كاذب؟)", en:`HbA1c ${h}% (diabetic) but FBG ${fbg} (normal). Iron deficiency, B12 deficiency, or splenectomy may falsely elevate HbA1c. Recommend: iron studies, B12, renal function.`, ar:`HbA1c في نطاق السكري مع سكر صيام طبيعي — نقص الحديد أو B12 يرفع HbA1c كاذباً.`, refs:["ADA 2025"] });
    if (Math.abs(fbg - eag) > 50)
      insights.push({ sev:"info", cat:"Glucose", title:"ℹ️ تباين FBG و HbA1c", en:`Estimated avg glucose from HbA1c ${h}%: ~${eag.toFixed(0)} mg/dL vs measured FBG ${fbg}. Difference ${Math.abs(fbg-eag).toFixed(0)} mg/dL — may indicate glucose variability or post-meal spikes.`, ar:`فرق ${Math.abs(fbg-eag).toFixed(0)} بين المتوسط المقدر وسكر الصيام — تذبذب محتمل.`, refs:["ADA 2025"] });
  }

  if (has("Insulin","FBG")) {
    const homa = (v("Insulin") * v("FBG")) / 405;
    if (homa > 2.5)
      insights.push({ sev:"warning", cat:"Glucose", title:"⚠️ مقاومة الإنسولين — HOMA-IR مرتفع", en:`Calculated HOMA-IR = ${homa.toFixed(2)} (>2.5 = insulin resistance). Associated with metabolic syndrome, PCOS, NAFLD. Recommend: lipid panel, liver enzymes, waist circumference.`, ar:`HOMA-IR = ${homa.toFixed(2)} — مقاومة إنسولين. مرتبط بالمتلازمة الأيضية، PCOS، كبد دهني.`, refs:["ADA 2025"] });
  }

  // ─ BUN/Creatinine Ratio ─
  if (has("Urea","Creatinine")) {
    const ratio = v("Urea") / v("Creatinine");
    if (ratio > 40)
      insights.push({ sev:"critical", cat:"Kidney", title:"🔴 نسبة BUN/كرياتينين > 40 — نزيف هضمي علوي محتمل", en:`BUN:Cr ratio = ${ratio.toFixed(1)}. Ratio >40 strongly suggests upper GI bleeding. Also: severe dehydration, high protein. Urgent clinical assessment.`, ar:`النسبة = ${ratio.toFixed(1)} — تشير بقوة لنزيف في الجهاز الهضمي العلوي.`, refs:["NEJM","Henry's 23rd"] });
    else if (ratio > 20)
      insights.push({ sev:"warning", cat:"Kidney", title:"⚠️ BUN/كرياتينين > 20 — أزوتيميا ما قبل الكلوي", en:`BUN:Cr ratio = ${ratio.toFixed(1)}. Suggests pre-renal: dehydration, HF, low perfusion, high protein, GI bleed.`, ar:`نسبة ${ratio.toFixed(1)} — جفاف، قصور قلب، أو نزيف هضمي.`, refs:["KDIGO 2024"] });
  }

  // ─ Liver patterns ─
  if (has("ALT","AST")) {
    const alt = v("ALT"), ast = v("AST");
    const dr = ast / alt;
    if ((alt > 56 || ast > 40) && dr >= 2)
      insights.push({ sev:"warning", cat:"Liver", title:"⚠️ نسبة De Ritis ≥ 2 — نمط الكبد الكحولي", en:`AST/ALT (De Ritis) = ${dr.toFixed(1)}. Ratio ≥2 strongly suggests alcoholic liver disease or cirrhosis. Correlate with GGT, clinical history.`, ar:`نسبة AST/ALT = ${dr.toFixed(1)} — نمط مرض الكبد الكحولي. قارن مع GGT والتاريخ الإكلينيكي.`, refs:["EASL 2023"] });
    if (alt > 1000 || ast > 1000)
      insights.push({ sev:"critical", cat:"Liver", title:"🔴 ارتفاع حاد جداً في إنزيمات الكبد (>1000)", en:`ALT ${alt} / AST ${ast} U/L — extreme elevation. Top differential: acute viral hepatitis, ischemic hepatitis (shock liver), paracetamol overdose, autoimmune hepatitis. Urgent: PT/INR, renal function, viral serology.`, ar:`ALT/AST أكثر من 1000 — أسباب أولى: التهاب كبد فيروسي حاد، كبد الصدمة، سمية الباراسيتامول.`, refs:["EASL 2023","AASLD 2024"] });
    if (has("ALP")) {
      const alp = v("ALP");
      const altx = alt/56, alpx = alp/147;
      const rr = altx / (alpx || 1);
      const pat = rr >= 5 ? "Hepatocellular" : rr <= 2 ? "Cholestatic" : "Mixed";
      const patAr = rr >= 5 ? "تلف خلوي كبدي" : rr <= 2 ? "انسدادي/ركود صفراوي" : "مختلط";
      if (alt > 56 || ast > 40 || alp > 147)
        insights.push({ sev:"info", cat:"Liver", title:`ℹ️ نمط إصابة الكبد: ${pat}`, en:`R-ratio = ${rr.toFixed(1)} → ${pat} pattern.\nALT: ${alt} (${(alt/56).toFixed(1)}× ULN), ALP: ${alp} (${(alp/147).toFixed(1)}× ULN).\nCauses: ${pat==="Hepatocellular"?"Viral hepatitis, drugs, ischemia, autoimmune":pat==="Cholestatic"?"Bile duct obstruction, PBC, PSC, drug-induced cholestasis":"Drug-induced, overlap syndrome"}.`, ar:`نمط الإصابة: ${patAr} (R-ratio = ${rr.toFixed(1)}).`, refs:["EASL DILI 2023"] });
    }
  }

  if (has("TBili","DBili")) {
    const tb = v("TBili"), db = v("DBili");
    const ib = tb - db;
    const pctDirect = (db/tb)*100;
    if (tb > 1.2) {
      if (pctDirect > 50)
        insights.push({ sev:"warning", cat:"Liver", title:"⚠️ يرقان انسدادي — البيليروبين المباشر مهيمن", en:`Direct bilirubin ${db} mg/dL (${pctDirect.toFixed(0)}% of total). Predominantly direct = conjugated hyperbilirubinemia → cholestasis, bile duct obstruction, hepatitis, Dubin-Johnson syndrome.`, ar:`البيليروبين المباشر ${pctDirect.toFixed(0)}% من الكلي — ركود صفراوي أو انسداد.`, refs:["Henry's 23rd"] });
      else
        insights.push({ sev:"info", cat:"Liver", title:"ℹ️ يرقان ما قبل الكبد — البيليروبين غير المباشر مهيمن", en:`Indirect bilirubin = ${ib.toFixed(1)} mg/dL predominates. Suggests pre-hepatic cause: hemolysis, Gilbert syndrome, neonatal jaundice.`, ar:`البيليروبين غير المباشر مهيمن — فقر دم انحلالي أو متلازمة جيلبرت.`, refs:["Tietz 7th"] });
    }
  }

  // ─ Lipids ─
  if (has("TC","TG","LDL","HDL")) {
    const tc = v("TC"), tg = v("TG"), ldl = v("LDL"), hdl = v("HDL");
    const friedewald = tc - hdl - (tg/5);
    if (tg > 400)
      insights.push({ sev:"critical", cat:"Lipids", title:"🔴 TG > 400 — معادلة Friedewald غير صالحة", en:`TG = ${tg} mg/dL. Friedewald LDL formula is INVALID when TG >400. Reported LDL may be grossly underestimated. Order direct LDL measurement.`, ar:`الدهون الثلاثية ${tg} — LDL المحسوب غير موثوق. يجب قياس Direct LDL.`, refs:["ACC/AHA 2024"] });
    if (tg > 150 && hdl < 40)
      insights.push({ sev:"warning", cat:"Lipids", title:"⚠️ دسليبيدميا أثيرية (↑TG + ↓HDL)", en:`TG ${tg} + HDL ${hdl} — classic atherogenic dyslipidemia, high CV risk. Strongly associated with insulin resistance and metabolic syndrome.`, ar:`دهون ثلاثية مرتفعة + HDL منخفض = خطر قلبي وعائي. مرتبط بمقاومة الإنسولين.`, refs:["ACC/AHA 2024","IDF"] });
    const tc_hdl = tc/hdl;
    if (tc_hdl > 5)
      insights.push({ sev:"warning", cat:"Lipids", title:"⚠️ نسبة TC/HDL > 5 — خطر قلبي وعائي مرتفع", en:`TC/HDL ratio = ${tc_hdl.toFixed(1)} (target <5). High ratio is an independent CV risk predictor. Combined with LDL ${ldl} mg/dL.`, ar:`نسبة الكوليسترول الكلي/HDL = ${tc_hdl.toFixed(1)} — مؤشر خطر قلبي مرتفع.`, refs:["ACC/AHA 2024"] });
    if (has("ApoB","ApoA1")) {
      const ratio = v("ApoB")/v("ApoA1");
      if (ratio > 0.9)
        insights.push({ sev:"warning", cat:"Lipids", title:"⚠️ نسبة ApoB/ApoA-I مرتفعة — خطر قلبي وعائي", en:`ApoB/ApoA-I = ${ratio.toFixed(2)} (>0.9 = elevated risk). Better CV predictor than LDL alone, especially with high TG.`, ar:`نسبة ApoB/ApoA-I = ${ratio.toFixed(2)} — مؤشر خطر أمراض القلب والأوعية.`, refs:["ACC/AHA 2024"] });
    }
  }

  // ─ Thyroid axis ─
  if (has("TSH","FT4")) {
    const tsh = v("TSH"), ft4 = v("FT4");
    if (tsh > 4 && ft4 < 0.8)
      insights.push({ sev:"warning", cat:"Thyroid", title:"⚠️ قصور الغدة الدرقية الأولي", en:`TSH ${tsh} ↑ + FT4 ${ft4} ↓ = Primary hypothyroidism. Causes: Hashimoto's, post-thyroidectomy, iodine deficiency, drugs (amiodarone, lithium). Recommend: Anti-TPO, Anti-Tg.`, ar:`TSH مرتفع + FT4 منخفض = قصور درقي أولي. الأكثر شيوعاً: هاشيموتو.`, refs:["ATA 2024"] });
    else if (tsh < 0.4 && ft4 > 1.8)
      insights.push({ sev:"warning", cat:"Thyroid", title:"⚠️ فرط نشاط الغدة الدرقية الأولي", en:`TSH ${tsh} ↓ + FT4 ${ft4} ↑ = Primary hyperthyroidism. Causes: Graves' disease, toxic nodular goiter, thyroiditis. Recommend: TRAb, thyroid scan.`, ar:`TSH منخفض + FT4 مرتفع = فرط نشاط درقي. الأسباب: جريفز، عقيدات سامة.`, refs:["ATA 2024"] });
    else if (tsh < 0.4 && ft4 < 0.8)
      insights.push({ sev:"warning", cat:"Thyroid", title:"⚠️ قصور درقي مركزي (نخامية/تحت المهاد)", en:`TSH ${tsh} ↓ + FT4 ${ft4} ↓ = Central hypothyroidism. Caused by pituitary or hypothalamic dysfunction. Recommend: MRI pituitary, prolactin, cortisol.`, ar:`TSH منخفض + FT4 منخفض = قصور درقي مركزي. يُنصح: MRI نخامية.`, refs:["ETA 2023"] });
    else if (tsh > 4 && ft4 >= 0.8 && ft4 <= 1.8)
      insights.push({ sev:"info", cat:"Thyroid", title:"ℹ️ قصور درقي تحت إكلينيكي", en:`TSH ${tsh} ↑ + FT4 ${ft4} (normal). Monitor 6–12 months. Treat if TSH >10 or symptomatic. Check Anti-TPO.`, ar:`TSH مرتفع مع FT4 طبيعي = قصور درقي تحت إكلينيكي. متابعة كل 6-12 شهر.`, refs:["ATA 2024"] });
    if (has("FT3")) {
      const ft3 = v("FT3");
      if (tsh < 0.4 && ft4 >= 0.8 && ft4 <= 1.8 && ft3 > 4.2)
        insights.push({ sev:"warning", cat:"Thyroid", title:"⚠️ سُمية T3 (T3 Toxicosis)", en:`TSH suppressed with normal FT4 but elevated FT3 ${ft3} pg/mL = T3 toxicosis. Seen with toxic multinodular goiter or early Graves'. Recommend: thyroid scan.`, ar:`TSH منخفض + FT4 طبيعي + FT3 مرتفع = سُمية T3. يُنصح: مسح الغدة الدرقية.`, refs:["ATA 2024"] });
    }
  }

  // ─ Iron ─
  if (has("SerumFe","TIBC","Ferritin")) {
    const fe = v("SerumFe"), tibc = v("TIBC"), ferr = v("Ferritin");
    const sat = (fe/tibc)*100;
    if (fe < 60 && tibc > 370 && ferr < 12)
      insights.push({ sev:"warning", cat:"Iron", title:"⚠️ نقص الحديد الكلاسيكي", en:`Fe ↓(${fe}) + TIBC ↑(${tibc}) + Ferritin ↓(${ferr}) + Sat ${sat.toFixed(0)}% = Classic IDA. Identify and treat underlying cause (blood loss, malabsorption).`, ar:`حديد منخفض + TIBC مرتفع + فيريتين منخفض = نقص الحديد. ابحث عن سبب فقدان الدم.`, refs:["WHO 2023","BSH"] });
    else if (fe < 60 && tibc < 250 && ferr > 100)
      insights.push({ sev:"warning", cat:"Iron", title:"⚠️ فقر دم الأمراض المزمنة", en:`Fe ↓(${fe}) + TIBC ↓(${tibc}) + Ferritin ↑(${ferr}) = Anemia of chronic disease (ACD). Common in: chronic infection, malignancy, autoimmune, CKD.`, ar:`حديد منخفض + TIBC منخفض + فيريتين مرتفع = فقر دم الأمراض المزمنة.`, refs:["ASH 2023"] });
    else if (fe > 170 && sat > 45 && ferr > 300)
      insights.push({ sev:"critical", cat:"Iron", title:"🔴 تراكم الحديد — استبعد داء ترسب الأصبغة", en:`Fe ↑(${fe}) + Sat ${sat.toFixed(0)}% (>45%) + Ferritin ↑(${ferr}) = Iron overload. Rule out hereditary hemochromatosis (HFE gene). Recommend: HFE genetics, liver MRI, LFTs.`, ar:`حديد مرتفع + تشبع مرتفع + فيريتين مرتفع = تراكم الحديد. استبعد داء ترسب الأصبغة.`, refs:["EASL 2022"] });
    else if (ferr > 300 && fe <= 170)
      insights.push({ sev:"info", cat:"Iron", title:"ℹ️ فيريتين مرتفع — بروتين الطور الحاد", en:`Ferritin ${ferr} elevated but serum iron ${fe} normal. Isolated elevated ferritin ≠ iron overload. Ferritin rises in: infection, inflammation, liver disease, malignancy, metabolic syndrome. Check CRP/ESR.`, ar:`فيريتين مرتفع مع حديد طبيعي — بروتين مرحلة حادة. تحقق من CRP وESR.`, refs:["BSH 2023"] });
  }

  // ─ Electrolytes ─
  if (has("Sodium")) {
    const na = v("Sodium");
    if (na < 120)
      insights.push({ sev:"critical", cat:"Electrolytes", title:"🔴 نقص صوديوم حاد (<120) — خطر وذمة دماغية", en:`Sodium ${na} mEq/L — severe hyponatremia. Risk of cerebral edema, seizures. Urgent correction (max 6-8 mEq/L per day to prevent ODS).`, ar:`صوديوم ${na} — نقص شديد جداً. خطر وذمة دماغية وتشنجات. تصحيح عاجل بحذر.`, refs:["EFNS 2014"] });
    else if (na > 155)
      insights.push({ sev:"critical", cat:"Electrolytes", title:"🔴 فرط صوديوم حاد (>155) — جفاف شديد", en:`Sodium ${na} mEq/L — severe hypernatremia. Usually reflects severe dehydration or diabetes insipidus. Urgent fluid resuscitation.`, ar:`صوديوم ${na} — ارتفاع شديد. جفاف حاد أو داء السكري الكاذب.`, refs:["KDIGO 2024"] });
  }

  if (has("Potassium")) {
    const k = v("Potassium");
    if (k < 2.5)
      insights.push({ sev:"critical", cat:"Electrolytes", title:"🔴 نقص بوتاسيوم حاد (<2.5) — خطر اضطراب قلبي", en:`Potassium ${k} mEq/L — severe hypokalemia. Risk of cardiac arrhythmias, muscle weakness. Urgent IV/oral replacement with monitoring.`, ar:`بوتاسيوم ${k} — نقص شديد. خطر اضطرابات قلبية. تعويض عاجل مع مراقبة.`, refs:["AHA 2024"] });
    else if (k > 6.0)
      insights.push({ sev:"critical", cat:"Electrolytes", title:"🔴 فرط بوتاسيوم (>6.0) — طارئ قلبي", en:`Potassium ${k} mEq/L — severe hyperkalemia. Life-threatening cardiac arrhythmia risk. Urgent ECG, calcium gluconate, insulin-dextrose, consider dialysis.`, ar:`بوتاسيوم ${k} — خطر توقف القلب. طارئ طبي.`, refs:["KDIGO 2024"] });
    else if (k > 5.5)
      insights.push({ sev:"warning", cat:"Electrolytes", title:"⚠️ فرط بوتاسيوم (5.5-6.0)", en:`Potassium ${k} mEq/L. Causes: AKI/CKD, ACE inhibitors, potassium-sparing diuretics, acidosis, hemolysis. ECG monitoring advised.`, ar:`بوتاسيوم ${k} — مرتفع. أسباب: فشل كلوي، ACEi، حموضة. راقب بـ ECG.`, refs:["KDIGO 2024"] });
  }

  if (has("Sodium","Potassium","Chloride","Bicarbonate")) {
    const ag = v("Sodium") - (v("Chloride") + v("Bicarbonate"));
    if (ag > 16)
      insights.push({ sev:"warning", cat:"Electrolytes", title:"⚠️ فجوة أنيون مرتفعة — حماض استقلابي", en:`Calculated anion gap = ${ag.toFixed(0)} mEq/L (>16 = high gap metabolic acidosis). MUDPILES: Methanol, Uremia, DKA, Propylene glycol, Isoniazid, Lactic acidosis, Ethylene glycol, Salicylates.`, ar:`فجوة الأنيون = ${ag.toFixed(0)} — حماض استقلابي عالي الفجوة. أسباب: MUDPILES (بولينا، حماض كيتوني، حماض لاكتيكي).`, refs:["Tietz 7th"] });
  }

  // ─ Cardiac ─
  if (has("cTnI") && v("cTnI") > 0.04)
    insights.push({ sev:"critical", cat:"Cardiac", title:"🔴 تروبونين I مرتفع — احتشاء عضلة القلب المحتمل", en:`cTnI ${v("cTnI")} ng/mL (>0.04 = elevated). URGENT: Rule out NSTEMI/STEMI. Serial troponins at 0h, 3h, 6h. ECG, cardiac referral immediately.`, ar:`تروبونين I مرتفع — احتمال احتشاء قلبي. سلسلة تروبونين وECG عاجل.`, refs:["ESC 2023","ACC/AHA 2024"] });

  if (has("hsTnT") && v("hsTnT") > 14)
    insights.push({ sev:"critical", cat:"Cardiac", title:"🔴 High-Sensitivity Troponin T مرتفع", en:`hs-TnT ${v("hsTnT")} ng/L (>14 = elevated). Use ESC 0h/1h or 0h/2h algorithm for rapid rule-in/rule-out of AMI. Also elevated in: myocarditis, PE, sepsis, CKD.`, ar:`hs-TnT مرتفع — استخدم خوارزمية 0h/1h لاستبعاد/تأكيد الاحتشاء.`, refs:["ESC 2023"] });

  if (has("BNP") && v("BNP") > 100)
    insights.push({ sev:"warning", cat:"Cardiac", title:"⚠️ BNP مرتفع — قصور قلب محتمل", en:`BNP ${v("BNP")} pg/mL (>100 = elevated). Sensitive marker for heart failure. Also elevated in: AF, PE, CKD, sepsis. Combine with Echo for diagnosis.`, ar:`BNP ${v("BNP")} — قصور قلب محتمل. قارن مع إيكو القلب.`, refs:["ESC HF 2023"] });

  if (has("D_Dimer") && v("D_Dimer") > 0.5)
    insights.push({ sev:"warning", cat:"Cardiac", title:"⚠️ D-Dimer مرتفع — استبعد الجلطة الوريدية أو الرئوية", en:`D-Dimer ${v("D_Dimer")} µg/mL FEU (>0.5). Sensitive but not specific for DVT/PE. High D-dimer + clinical probability → CT pulmonary angiography or Doppler US. Also elevated in: infection, pregnancy, malignancy.`, ar:`D-Dimer مرتفع — حساس لكن غير نوعي. مع احتمالية سريرية: CTA أو إيكو.`, refs:["ESC PE 2023"] });

  // ─ Calcium/Bone ─
  if (has("CalciumT","Albumin")) {
    const corrCa = v("CalciumT") + 0.8*(4.0 - v("Albumin"));
    if (corrCa > 10.5)
      insights.push({ sev:"warning", cat:"Bone", title:"⚠️ فرط كالسيوم مُصحَّح بالألبومين", en:`Corrected calcium = ${corrCa.toFixed(1)} mg/dL (measured ${v("CalciumT")}, albumin ${v("Albumin")}). Causes of hypercalcemia: primary hyperparathyroidism (PTH), malignancy (PTHrP), vitamin D toxicity, sarcoidosis.`, ar:`الكالسيوم المُصحَّح = ${corrCa.toFixed(1)} — فرط كالسيوم. أسباب: فرط جارة الدرقية، أورام.`, refs:["AACE 2022"] });
    else if (corrCa < 8.5)
      insights.push({ sev:"warning", cat:"Bone", title:"⚠️ نقص كالسيوم مُصحَّح", en:`Corrected calcium = ${corrCa.toFixed(1)} mg/dL. Causes: hypoparathyroidism, vitamin D deficiency, hypomagnesemia, CKD. Check PTH, Mg, Vitamin D.`, ar:`الكالسيوم المُصحَّح = ${corrCa.toFixed(1)} — نقص كالسيوم. تحقق من PTH، فيتامين د، ومغنيسيوم.`, refs:["AACE 2022"] });
  }

  if (has("VitD25")) {
    const d = v("VitD25");
    if (d < 10)
      insights.push({ sev:"critical", cat:"Bone", title:"🔴 عوز شديد في فيتامين د (<10 ng/mL)", en:`25-OH Vitamin D = ${d} ng/mL — severe deficiency. Risk of osteomalacia, secondary hyperparathyroidism, bone pain. High-dose replenishment required.`, ar:`فيتامين د ${d} — عوز شديد جداً. خطر لين العظام وارتفاع PTH ثانوي.`, refs:["Endocrine Society 2024"] });
    else if (d < 20)
      insights.push({ sev:"warning", cat:"Bone", title:"⚠️ نقص فيتامين د (10-20 ng/mL)", en:`25-OH Vitamin D = ${d} ng/mL — deficient. Supplement with Vitamin D3 (1000-4000 IU/day). Recheck in 3 months.`, ar:`فيتامين د ${d} — نقص. تكملة بـ D3 وإعادة الفحص بعد 3 أشهر.`, refs:["Endocrine Society 2024"] });
    else if (d < 30)
      insights.push({ sev:"info", cat:"Bone", title:"ℹ️ فيتامين د غير كافٍ (20-30 ng/mL)", en:`25-OH Vitamin D = ${d} ng/mL — insufficient. Moderate supplementation recommended.`, ar:`فيتامين د ${d} — غير كافٍ. يُنصح بجرعة تكميلية معتدلة.`, refs:["Endocrine Society 2024"] });
  }

  // ─ Inflammation / Sepsis ─
  if (has("Procalcitonin")) {
    const pct = v("Procalcitonin");
    if (pct > 2)
      insights.push({ sev:"critical", cat:"Inflammation", title:"🔴 بروكالسيتونين مرتفع جداً (>2) — إنتان جرثومي شديد", en:`PCT ${pct} ng/mL — likely severe bacterial infection or sepsis. Initiate broad-spectrum antibiotics. Reassess at 48-72h for de-escalation.`, ar:`PCT ${pct} — إنتان جرثومي شديد/إنتان الدم. بادر بالمضادات الحيوية الواسعة الطيف.`, refs:["IDSA 2024","Surviving Sepsis 2021"] });
    else if (pct > 0.5)
      insights.push({ sev:"warning", cat:"Inflammation", title:"⚠️ بروكالسيتونين 0.5–2 — محتمل عدوى جرثومية", en:`PCT ${pct} ng/mL — possible bacterial infection. Clinical assessment and blood cultures advised.`, ar:`PCT ${pct} — عدوى جرثومية محتملة. تقييم إكلينيكي وزراعة دم.`, refs:["IDSA 2024"] });
    else if (pct > 0.1 && pct <= 0.5)
      insights.push({ sev:"info", cat:"Inflammation", title:"ℹ️ بروكالسيتونين منخفض — ميّز العدوى الفيروسية", en:`PCT ${pct} ng/mL — low range. Bacterial infection unlikely; may be viral or systemic inflammatory condition.`, ar:`PCT ${pct} — منخفض. العدوى الجرثومية غير محتملة. محتمل فيروسي.`, refs:["IDSA 2024"] });
  }

  if (has("CRP","ESR")) {
    const crp = v("CRP"), esr = v("ESR");
    if (crp > 100 && esr > 80)
      insights.push({ sev:"warning", cat:"Inflammation", title:"⚠️ CRP وESR مرتفعان جداً — التهاب شديد", en:`CRP ${crp} mg/L + ESR ${esr} mm/hr — both markedly elevated. Suggests significant systemic inflammation: sepsis, autoimmune (vasculitis, polymyalgia), malignancy, major infection.`, ar:`CRP و ESR مرتفعان بشكل ملحوظ — التهاب جهازي شديد. أسباب: إنتان، أمراض مناعة ذاتية، أورام.`, refs:["ACR 2024"] });
    if (crp > 5 && esr < 20)
      insights.push({ sev:"info", cat:"Inflammation", title:"ℹ️ CRP مرتفع مع ESR طبيعي — التهاب حديث", en:`CRP rises faster (6-12h) and falls faster than ESR. Elevated CRP with normal ESR suggests acute/recent inflammation. ESR may not have risen yet.`, ar:`CRP يرتفع أسرع من ESR. CRP مرتفع مع ESR طبيعي = التهاب حديث النشأة.`, refs:["Tietz 7th"] });
  }

  // ─ Multi-organ ─
  if (has("ALT","Creatinine")) {
    const alt = v("ALT"), cr = v("Creatinine");
    if (alt > 56 && cr > 1.5)
      insights.push({ sev:"warning", cat:"Multi-organ", title:"⚠️ خلل كبدي-كلوي مشترك", en:`Elevated ALT (${alt}) + Creatinine (${cr}). Consider: hepatorenal syndrome, sepsis-related multi-organ dysfunction, ischemic hepatitis + AKI, drug/toxin (paracetamol, NSAIDs, aminoglycosides).`, ar:`ارتفاع ALT + كرياتينين = خلل كبدي-كلوي. فكر في: HRS، صدمة، سمية دواء.`, refs:["EASL 2023","KDIGO 2024"] });
  }

  if (has("HbA1c","Creatinine")) {
    const h = v("HbA1c"), cr = v("Creatinine");
    if (h >= 6.5 && cr > 1.2)
      insights.push({ sev:"warning", cat:"Multi-organ", title:"⚠️ خطر اعتلال الكلى السكري", en:`HbA1c ${h}% (diabetic) + Creatinine ${cr} mg/dL. High risk of diabetic nephropathy. Essential: urine ACR, eGFR trend, BP control, fundoscopy, SGLT2 inhibitor consideration.`, ar:`HbA1c مرتفع + كرياتينين مرتفع = خطر اعتلال الكلى السكري. ACR في البول عاجل.`, refs:["ADA 2025","KDIGO 2024"] });
  }

  if (has("TSH","Hgb") && has("MCV")) {
    const tsh = v("TSH"), hgb = v("Hgb"), mcv = v("MCV");
    const hgbLow = (sex==="male" && hgb < 13.5) || (sex==="female" && hgb < 12) || (sex==="unspecified" && hgb < 12);
    if (tsh > 4 && hgbLow && mcv > 100)
      insights.push({ sev:"info", cat:"Multi-organ", title:"ℹ️ قصور الدرق + فقر دم كبير الكريات", en:`TSH ${tsh} (hypothyroid) + Hgb ${hgb} g/dL + MCV ${mcv} fL (macrocytic). Hypothyroidism can cause macrocytic anemia. Also check B12 and folate (often co-deficient in autoimmune thyroiditis).`, ar:`قصور الدرق + فقر دم كبير الكريات — الدرق يسبب فقر دم كبير الكريات. تحقق من B12 وفولات.`, refs:["ATA 2024","BSH 2024"] });
  }

  return insights.sort((a,b) => {
    const o = {critical:0,warning:1,info:2};
    return o[a.sev] - o[b.sev];
  });
}

// ═══════════════════════════════════════════════════════════════
// UI COMPONENTS
// ═══════════════════════════════════════════════════════════════

const SEV_STYLES = {
  critical: { bg:"#1a0505", border:"#ff4444", icon:"🔴", label:"Critical" },
  warning:  { bg:"#1a1200", border:"#ffaa00", icon:"⚠️", label:"Warning" },
  info:     { bg:"#001a2d", border:"#0088ff", icon:"ℹ️", label:"Info" },
};

function StatusBadge({ status }) {
  const cfg = {
    high:    { bg:"#3d1515", color:"#ff6b6b", text:"↑ High" },
    low:     { bg:"#0d1f35", color:"#74b9ff", text:"↓ Low" },
    normal:  { bg:"#0d2d1a", color:"#55efc4", text:"✓ Normal" },
    unknown: { bg:"#1a1a1a", color:"#888",    text:"—" },
  };
  const s = cfg[status] || cfg.unknown;
  return (
    <span style={{ background:s.bg, color:s.color, padding:"2px 10px", borderRadius:20, fontSize:12, fontWeight:700, whiteSpace:"nowrap" }}>
      {s.text}
    </span>
  );
}

function InsightCard({ ins, defaultOpen }) {
  const [open, setOpen] = useState(defaultOpen);
  const st = SEV_STYLES[ins.sev];
  return (
    <div style={{ border:`1px solid ${st.border}`, borderLeft:`5px solid ${st.border}`, borderRadius:10, marginBottom:10, background:st.bg, overflow:"hidden" }}>
      <button onClick={() => setOpen(!open)} style={{ width:"100%", textAlign:"left", padding:"12px 16px", background:"transparent", border:"none", cursor:"pointer", display:"flex", justifyContent:"space-between", alignItems:"center" }}>
        <span style={{ color:"#eee", fontWeight:700, fontSize:14 }}>{ins.title}</span>
        <span style={{ color:st.border, fontSize:18 }}>{open ? "▲" : "▼"}</span>
      </button>
      {open && (
        <div style={{ padding:"0 16px 14px" }}>
          <p style={{ color:"#ddd", fontSize:13, lineHeight:1.7, margin:"0 0 8px", whiteSpace:"pre-wrap" }}>{ins.en}</p>
          <div style={{ direction:"rtl", textAlign:"right", fontSize:12, color:"#aaa", borderTop:"1px solid #333", paddingTop:8, marginTop:8 }}>
            {ins.ar}
          </div>
          {ins.refs && <div style={{ fontSize:11, color:"#666", marginTop:6 }}>📚 {ins.refs.join(" | ")}</div>}
        </div>
      )}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════
// MAIN APP
// ═══════════════════════════════════════════════════════════════

export default function App() {
  const [sex, setSex] = useState("unspecified");
  const [age, setAge] = useState("");
  const [patName, setPatName] = useState("");
  const [selectedPanels, setSelectedPanels] = useState([]);
  const [inputs, setInputs] = useState({});
  const [analyzed, setAnalyzed] = useState(false);
  const [activeTab, setActiveTab] = useState("panels");

  const togglePanel = (p) => {
    setSelectedPanels(prev => prev.includes(p) ? prev.filter(x=>x!==p) : [...prev, p]);
    setAnalyzed(false);
  };

  const setVal = (key, val) => {
    setInputs(prev => ({ ...prev, [key]: val === "" ? undefined : parseFloat(val) }));
    setAnalyzed(false);
  };

  const activeVals = useMemo(() => {
    const out = {};
    Object.entries(inputs).forEach(([k,v]) => { if (v != null && !isNaN(v) && v > 0) out[k] = v; });
    return out;
  }, [inputs]);

  const flags = useMemo(() => {
    return Object.entries(activeVals).map(([k,v]) => {
      if (!REF[k]) return null;
      const r = REF[k];
      const { status, lo, hi } = getStatus(k, v, sex);
      return { key:k, label:r.label, ar:r.ar, unit:r.unit, value:v, status, lo, hi, cat:r.cat };
    }).filter(Boolean);
  }, [activeVals, sex]);

  const insights = useMemo(() => analyzed ? runInsights(activeVals, sex, age ? parseInt(age) : null) : [], [analyzed, activeVals, sex, age]);

  const nHigh = flags.filter(f=>f.status==="high").length;
  const nLow  = flags.filter(f=>f.status==="low").length;
  const nNorm = flags.filter(f=>f.status==="normal").length;
  const nCrit = insights.filter(i=>i.sev==="critical").length;
  const nWarn = insights.filter(i=>i.sev==="warning").length;
  const nInfo = insights.filter(i=>i.sev==="info").length;

  const catGroups = useMemo(() => {
    const g = {};
    flags.forEach(f => { (g[f.cat] = g[f.cat] || []).push(f); });
    return g;
  }, [flags]);

  return (
    <div style={{ fontFamily:"'Segoe UI',system-ui,sans-serif", background:"#0d0e12", minHeight:"100vh", color:"#e0e0e0" }}>
      {/* ── Header ── */}
      <div style={{ background:"linear-gradient(135deg,#c0390a,#e85d10,#f39c12)", padding:"20px 24px", textAlign:"center" }}>
        <div style={{ fontSize:28, fontWeight:900, color:"#fff", letterSpacing:-0.5 }}>🧬 Orange Lab Results Analyzer</div>
        <div style={{ fontSize:13, color:"rgba(255,255,255,0.85)", marginTop:4 }}>Clinical Intelligence Engine — Cross-Validation & Pattern Recognition</div>
        <div style={{ fontSize:11, color:"rgba(255,255,255,0.6)", marginTop:2 }}>6th October City • Giza • Egypt</div>
      </div>

      <div style={{ maxWidth:1100, margin:"0 auto", padding:"20px 16px" }}>

        {/* ── Patient Info ── */}
        <div style={{ background:"#16181f", border:"1px solid #2a2d38", borderRadius:12, padding:"16px 20px", marginBottom:16, display:"flex", flexWrap:"wrap", gap:12, alignItems:"flex-end" }}>
          <div style={{ flex:"2 1 180px" }}>
            <label style={{ fontSize:12, color:"#888", display:"block", marginBottom:4 }}>👤 Patient Name</label>
            <input value={patName} onChange={e=>setPatName(e.target.value)} placeholder="Optional"
              style={{ width:"100%", padding:"8px 12px", background:"#0d0e12", border:"1px solid #333", borderRadius:8, color:"#eee", fontSize:13, boxSizing:"border-box" }} />
          </div>
          <div style={{ flex:"1 1 120px" }}>
            <label style={{ fontSize:12, color:"#888", display:"block", marginBottom:4 }}>⚥ Sex</label>
            <select value={sex} onChange={e=>setSex(e.target.value)}
              style={{ width:"100%", padding:"8px 12px", background:"#0d0e12", border:"1px solid #333", borderRadius:8, color:"#eee", fontSize:13 }}>
              <option value="unspecified">Unspecified</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
            </select>
          </div>
          <div style={{ flex:"1 1 100px" }}>
            <label style={{ fontSize:12, color:"#888", display:"block", marginBottom:4 }}>📅 Age</label>
            <input type="number" value={age} onChange={e=>setAge(e.target.value)} min={0} max={120} placeholder="yrs"
              style={{ width:"100%", padding:"8px 12px", background:"#0d0e12", border:"1px solid #333", borderRadius:8, color:"#eee", fontSize:13, boxSizing:"border-box" }} />
          </div>
        </div>

        {/* ── Tabs ── */}
        <div style={{ display:"flex", gap:4, marginBottom:16, background:"#16181f", padding:4, borderRadius:10, border:"1px solid #2a2d38" }}>
          {[["panels","📋 Select Panels"],["entry","✏️ Enter Results"],["results","📊 Analysis"]].map(([k,label])=>(
            <button key={k} onClick={()=>{if(k==="results"){setAnalyzed(true);}setActiveTab(k);}}
              style={{ flex:1, padding:"10px 4px", borderRadius:8, border:"none", cursor:"pointer", fontWeight:700, fontSize:13,
                background: activeTab===k ? "linear-gradient(135deg,#c0390a,#e85d10)" : "transparent",
                color: activeTab===k ? "#fff" : "#888" }}>
              {label}
            </button>
          ))}
        </div>

        {/* ── PANEL SELECTION ── */}
        {activeTab==="panels" && (
          <div>
            <div style={{ fontSize:13, color:"#888", marginBottom:12 }}>Select the panels you want to enter results for:</div>
            <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fill,minmax(220px,1fr))", gap:8 }}>
              {Object.entries(PANELS).map(([name, cfg]) => {
                const sel = selectedPanels.includes(name);
                return (
                  <div key={name} onClick={()=>togglePanel(name)}
                    style={{ padding:"12px 14px", borderRadius:10, cursor:"pointer", transition:"all .15s",
                      border: sel ? `2px solid ${cfg.color}` : "2px solid #2a2d38",
                      background: sel ? `${cfg.color}18` : "#16181f",
                      display:"flex", alignItems:"center", gap:10 }}>
                    <span style={{ fontSize:22 }}>{cfg.icon}</span>
                    <div>
                      <div style={{ fontSize:13, fontWeight:700, color: sel ? cfg.color : "#ccc" }}>{name.replace(/^[^\s]+ /,"")}</div>
                      <div style={{ fontSize:11, color:"#555" }}>{cfg.keys.length} tests</div>
                    </div>
                    <div style={{ marginLeft:"auto", width:18, height:18, borderRadius:"50%", border:`2px solid ${sel ? cfg.color : "#444"}`, background: sel ? cfg.color : "transparent", display:"flex", alignItems:"center", justifyContent:"center", fontSize:11, color:"#fff", flexShrink:0 }}>{sel?"✓":""}</div>
                  </div>
                );
              })}
            </div>
            {selectedPanels.length > 0 && (
              <button onClick={()=>setActiveTab("entry")}
                style={{ marginTop:16, width:"100%", padding:"14px", background:"linear-gradient(135deg,#c0390a,#e85d10)", border:"none", borderRadius:10, color:"#fff", fontWeight:800, fontSize:15, cursor:"pointer" }}>
                ✏️ Enter Results for {selectedPanels.length} Panel(s) →
              </button>
            )}
          </div>
        )}

        {/* ── DATA ENTRY ── */}
        {activeTab==="entry" && (
          <div>
            {selectedPanels.length === 0 && (
              <div style={{ textAlign:"center", padding:40, color:"#555" }}>No panels selected. Go to "Select Panels" first.</div>
            )}
            {selectedPanels.map(panelName => {
              const cfg = PANELS[panelName];
              return (
                <div key={panelName} style={{ marginBottom:20 }}>
                  <div style={{ background:`linear-gradient(90deg,${cfg.color}22,transparent)`, borderLeft:`4px solid ${cfg.color}`, padding:"8px 14px", borderRadius:"0 8px 8px 0", marginBottom:10, fontWeight:800, fontSize:14, color:cfg.color }}>
                    {panelName}
                  </div>
                  <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fill,minmax(240px,1fr))", gap:8 }}>
                    {cfg.keys.map(key => {
                      if (!REF[key]) return null;
                      const r = REF[key];
                      const curVal = inputs[key];
                      const hasVal = curVal != null && curVal > 0;
                      const { status } = hasVal ? getStatus(key, curVal, sex) : { status:"unknown" };
                      const borderColor = hasVal ? (status==="high"?"#ff6b6b":status==="low"?"#74b9ff":"#55efc4") : "#2a2d38";
                      return (
                        <div key={key} style={{ background:"#16181f", border:`1px solid ${borderColor}`, borderRadius:10, padding:"10px 12px", transition:"border .2s" }}>
                          <div style={{ fontSize:11, color:"#666", marginBottom:2 }}>{r.ar}</div>
                          <div style={{ fontSize:13, fontWeight:600, color:"#ccc", marginBottom:6 }}>{r.label}</div>
                          <div style={{ display:"flex", gap:8, alignItems:"center" }}>
                            <input type="number" min={0} step="any"
                              value={inputs[key] ?? ""}
                              onChange={e=>setVal(key, e.target.value)}
                              placeholder="0.00"
                              style={{ flex:1, padding:"6px 10px", background:"#0d0e12", border:"1px solid #333", borderRadius:6, color:"#eee", fontSize:14, minWidth:0 }} />
                            <span style={{ fontSize:11, color:"#555", whiteSpace:"nowrap" }}>{r.unit}</span>
                          </div>
                          {hasVal && (
                            <div style={{ marginTop:6, fontSize:11, color:status==="high"?"#ff6b6b":status==="low"?"#74b9ff":"#55efc4" }}>
                              {status==="high"?"↑ High":status==="low"?"↓ Low":"✓ Normal"}
                              {r.lo!=null && <span style={{ color:"#555" }}> (ref: {r.lo}–{r.hi} {r.unit})</span>}
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })}
            {Object.keys(activeVals).length > 0 && (
              <button onClick={()=>{setAnalyzed(true);setActiveTab("results");}}
                style={{ marginTop:8, width:"100%", padding:"14px", background:"linear-gradient(135deg,#c0390a,#e85d10)", border:"none", borderRadius:10, color:"#fff", fontWeight:800, fontSize:15, cursor:"pointer" }}>
                🚀 Run Clinical Analysis ({Object.keys(activeVals).length} tests) →
              </button>
            )}
          </div>
        )}

        {/* ── RESULTS ── */}
        {activeTab==="results" && (
          <div>
            {!analyzed || flags.length === 0 ? (
              <div style={{ textAlign:"center", padding:60, color:"#555" }}>
                <div style={{ fontSize:40, marginBottom:12 }}>🧬</div>
                Enter lab values and click "Run Clinical Analysis" to see results.
              </div>
            ) : (
              <>
                {/* Patient header */}
                {(patName || sex!=="unspecified" || age) && (
                  <div style={{ background:"#16181f", border:"1px solid #2a2d38", borderRadius:10, padding:"10px 16px", marginBottom:16, fontSize:13, color:"#aaa" }}>
                    {patName && <strong style={{color:"#eee"}}>{patName}</strong>}
                    {sex!=="unspecified" && <span> • {sex.charAt(0).toUpperCase()+sex.slice(1)}</span>}
                    {age && <span> • Age {age}</span>}
                  </div>
                )}

                {/* KPI cards */}
                <div style={{ display:"grid", gridTemplateColumns:"repeat(4,1fr)", gap:8, marginBottom:16 }}>
                  {[
                    { n:flags.length, label:"Tests", color:"#aaa" },
                    { n:nHigh, label:"High ↑", color:"#ff6b6b" },
                    { n:nLow,  label:"Low ↓",  color:"#74b9ff" },
                    { n:nNorm, label:"Normal ✓",color:"#55efc4" },
                  ].map(({n,label,color})=>(
                    <div key={label} style={{ background:"#16181f", border:"1px solid #2a2d38", borderRadius:10, padding:"12px", textAlign:"center" }}>
                      <div style={{ fontSize:28, fontWeight:900, color }}>{n}</div>
                      <div style={{ fontSize:11, color:"#666", marginTop:2 }}>{label}</div>
                    </div>
                  ))}
                </div>

                {/* Individual results by category */}
                <div style={{ marginBottom:20 }}>
                  <div style={{ fontWeight:800, fontSize:15, color:"#eee", marginBottom:10 }}>🔬 Individual Test Results</div>
                  {Object.entries(catGroups).map(([cat, catFlags]) => (
                    <div key={cat} style={{ marginBottom:12 }}>
                      <div style={{ fontSize:13, fontWeight:700, color:"#FF8C5A", marginBottom:6, borderBottom:"1px solid #2a2d38", paddingBottom:4 }}>{cat}</div>
                      <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fill,minmax(260px,1fr))", gap:6 }}>
                        {catFlags.map(f => {
                          const statusColor = f.status==="high"?"#ff6b6b":f.status==="low"?"#74b9ff":"#55efc4";
                          const borderC = f.status==="high"?"#3d1515":f.status==="low"?"#0d1f35":"#0d2d1a";
                          return (
                            <div key={f.key} style={{ background:borderC, border:`1px solid ${statusColor}44`, borderRadius:8, padding:"8px 12px", display:"flex", justifyContent:"space-between", alignItems:"center", gap:8 }}>
                              <div>
                                <div style={{ fontSize:11, color:"#666" }}>{f.ar}</div>
                                <div style={{ fontSize:12, fontWeight:600, color:"#ccc" }}>{f.label}</div>
                              </div>
                              <div style={{ textAlign:"right", flexShrink:0 }}>
                                <div style={{ fontSize:16, fontWeight:800, color:statusColor }}>{f.value}</div>
                                <div style={{ fontSize:10, color:"#555" }}>{f.unit}</div>
                                <StatusBadge status={f.status} />
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  ))}
                </div>

                {/* Clinical Intelligence */}
                <div style={{ borderTop:"1px solid #2a2d38", paddingTop:16 }}>
                  <div style={{ fontWeight:800, fontSize:15, color:"#eee", marginBottom:4 }}>🧠 Clinical Intelligence — Cross-Validation Insights</div>
                  {insights.length === 0 ? (
                    <div style={{ background:"#0d2d1a", border:"1px solid #55efc4", borderRadius:10, padding:"16px", color:"#55efc4", textAlign:"center", marginTop:10 }}>
                      ✅ No significant cross-validation alerts. Results appear internally consistent.
                    </div>
                  ) : (
                    <>
                      <div style={{ fontSize:13, color:"#888", marginBottom:10 }}>
                        {insights.length} insight(s): 🔴 {nCrit} Critical | ⚠️ {nWarn} Warning | ℹ️ {nInfo} Info
                      </div>
                      {insights.map((ins, i) => <InsightCard key={i} ins={ins} defaultOpen={ins.sev==="critical"} />)}
                    </>
                  )}
                </div>

                {/* Disclaimer */}
                <div style={{ marginTop:20, padding:"12px 16px", background:"#16181f", border:"1px solid #2a2d38", borderRadius:8, fontSize:11, color:"#555", textAlign:"center" }}>
                  ⚕️ Clinical decision support only — interpret in context by a qualified physician.<br/>
                  📚 ADA 2025 | KDIGO 2024 | EASL 2023 | ACC/AHA 2024 | ATA 2024 | Tietz 7th | Henry's 23rd | WHO/ICSH
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
