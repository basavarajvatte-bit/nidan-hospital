# ====================================================================== SYSTEM 13: GYNAECOLOGY + OBSTETRICS (women)
# Hutchison 24e, Ch 5 (Women), p45-62; Box 5.1 (menstrual history), 5.2 (bleeding / menopause), 5.3 (prolapse),
# 5.4 (dyspareunia), 5.5 (obstetric history), 5.6-5.7. Executed inside hx_bank.py.
# Ask with tact and privacy; offer a female chaperone. Pregnancy danger signs follow standard Indian ANC practice (marked).

WM = f"{H}, Ch 5"
FEM = {"sex": "female", "min_age": 10}
REPRO = {"sex": "female", "min_age": 12, "max_age": 55}
ANC = "Standard antenatal danger signs (MoHFW India / WHO ANC) — general clinical practice"

C("periods", "Women", "Period problems (heavy / irregular / painful / missed)", "माहवारी की तकलीफ़ (ज़्यादा / अनियमित / दर्द / रुकी)", "पाळीचा त्रास (जास्त / अनियमित / दुखणे / चुकली)", "📅", 131, f"{WM}, p46-47 (Box 5.1-5.2)")
C("pmb", "Women", "Bleeding after menopause", "माहवारी बंद होने के बाद ख़ून", "रजोनिवृत्तीनंतर रक्तस्राव", "🩸", 132, f"{WM}, p47 (Box 5.2)")
C("vaginal_discharge", "Women", "White discharge / itching (vaginal)", "सफ़ेद पानी / खुजली (योनि)", "पांढरे पाणी / खाज (योनी)", "💧", 133, f"{WM}, p46-47")
C("pelvic_pain", "Women", "Lower abdominal / pelvic pain (women)", "नीचे पेट दर्द (महिला)", "ओटीपोटात दुखणे (महिला)", "⚡", 134, f"{WM}, p46")
C("prolapse", "Women", "Something coming down (prolapse)", "नीचे कुछ उतरना (बच्चेदानी)", "खाली काही उतरणे (गर्भाशय)", "⬇️", 135, f"{WM}, p47 (Box 5.3)")
C("pregnancy", "Women", "Pregnancy check-up / problem", "गर्भावस्था जाँच / तकलीफ़", "गर्भावस्था तपासणी / त्रास", "🤰", 136, f"{WM}, p48 (Box 5.5); {ANC}")
C("postpartum", "Women", "Problem after delivery", "डिलीवरी के बाद तकलीफ़", "प्रसूतीनंतरचा त्रास", "👶", 137, ANC)
C("infertility", "Women", "Not conceiving (infertility)", "गर्भ नहीं ठहरना", "गर्भधारणा न होणे", "🌱", 138, f"{WM}, p48")
C("breast", "Women", "Breast pain / lump / discharge", "स्तन में दर्द / गाँठ / स्राव", "स्तनात दुखणे / गाठ / स्राव", "🎗️", 139, f"{H}, Ch 2, p20; {WM}")

# ---------------------------------------------------------------- PERIODS  (Box 5.1-5.2)
MN = f"{WM}, p46-47 (Box 5.1-5.2)"
Q("pd_problem", "periods", "hopi", 1, "multi", "What is the problem?", "माहवारी में क्या तकलीफ़?", "पाळीत काय त्रास?", term="Menstrual complaint", applies=FEM, opts=[
    O("heavy", "Heavy (clots / changing pad every 1–2 h / 'double protection')", "ज़्यादा (थक्के / 1–2 घंटे में पैड बदलना)", "जास्त (गुठळ्या / 1–2 तासांत पॅड बदलणे)", ["Menorrhagia", "Fibroid", "Adenomyosis", "Bleeding disorder", "Hypothyroidism"]),
    O("long", "Bleeding more than 7 days", "7 दिन से ज़्यादा ख़ून", "7 दिवसांपेक्षा जास्त रक्त", ["Menorrhagia", "Fibroid"]),
    O("irregular", "Irregular / unpredictable", "अनियमित / अंदाज़ा नहीं", "अनियमित / अंदाज नाही", ["Polycystic ovary syndrome", "Thyroid disorder", "Perimenopause"]),
    O("missed", "Missed periods", "माहवारी रुकी", "पाळी चुकली", ["Pregnancy", "Polycystic ovary syndrome", "Thyroid disorder", "Hyperprolactinaemia"]),
    O("painful", "Very painful periods", "बहुत दर्दनाक माहवारी", "खूप दुखरी पाळी", ["Primary dysmenorrhoea", "Endometriosis", "Adenomyosis"]),
    O("between", "Bleeding between periods", "दो माहवारी के बीच ख़ून", "दोन पाळ्यांमध्ये रक्त", ["Cervical lesion / polyp", "Hormonal contraception", "Endometrial pathology"]),
    O("after_sex", "Bleeding after intercourse", "संभोग के बाद ख़ून", "संभोगानंतर रक्त", ["Cervical lesion / polyp", "Cervical cancer"]),
    O("pms", "Mood / bloating / breast pain before periods", "माहवारी से पहले चिड़चिड़ापन / फूलना / स्तन दर्द", "पाळीआधी चिडचिड / फुगणे / स्तनदुखी", ["Premenstrual syndrome"])],
  src=MN)
Q("pd_cycle", "periods", "hopi", 2, "text", "Age at first period, cycle length (days) and bleeding days, last period date",
  "पहली माहवारी की उम्र, कितने दिन में आती, कितने दिन रहती, आख़िरी कब?", "पहिल्या पाळीचे वय, किती दिवसांनी येते, किती दिवस राहते, शेवटची कधी?",
  term="Menstrual formula (menarche, cycle, LMP)", applies=FEM, src=f"{WM}, p46 (Box 5.1)")
Q("pd_pregnancy_test", "periods", "redflag", 3, "yesno", "Period missed and sexually active (pregnancy possible)?", "माहवारी रुकी और संभोग हुआ है (गर्भ संभव)?",
  "पाळी चुकली आणि संभोग झाला आहे (गर्भधारणा शक्य)?", term="Possible pregnancy", rf="Possible pregnancy — urine pregnancy test before X-ray / drugs", ddx=["Pregnancy"], key="pregnancy",
  applies=REPRO, show={"q": "pd_problem", "in_any": ["missed", "irregular", "between"]}, src=MN)
Q("pd_anaemia", "periods", "redflag", 4, "yesno", "Very heavy bleeding with dizziness, breathlessness, or fainting?", "क्या बहुत ज़्यादा ख़ून के साथ चक्कर, साँस फूलना या बेहोशी?",
  "खूप जास्त रक्तस्रावासोबत चक्कर, धाप किंवा बेशुद्धी?", term="Heavy bleeding with haemodynamic symptoms", rf="Heavy menstrual bleeding with anaemia/shock symptoms — urgent Hb", ddx=["Severe anaemia", "Menorrhagia"],
  applies=FEM, show={"q": "pd_problem", "in_any": ["heavy", "long"]}, src=MN)
Q("pd_impact", "periods", "hopi", 5, "multi", "Effect on life", "ज़िंदगी पर असर", "जीवनावर परिणाम", term="Impact", applies=FEM, opts=[
    O("miss_work_school", "Misses school / work", "स्कूल / काम छूटता", "शाळा / काम बुडते"),
    O("painkillers", "Needs painkillers every month", "हर महीने दर्द की गोली", "प्रत्येक महिन्याला वेदनाशामक"),
    O("pain_sex", "Pain during intercourse (deep)", "संभोग में (अंदर) दर्द", "संभोगात (आत) दुखणे", ["Endometriosis", "Pelvic inflammatory disease"]),
    O("bowel_urine_pain", "Pain passing stool / urine during periods", "माहवारी में मल / पेशाब करते दर्द", "पाळीत शौच / लघवी करताना दुखणे", ["Endometriosis"])],
  src=f"{WM}, p46-47 (Box 5.4)")
Q("pd_causes", "periods", "associated", 6, "multi", "Other clues", "अन्य संकेत", "इतर संकेत", term="Endocrine / systemic clues", applies=FEM, opts=[
    O("pcos", "Facial / body hair, acne, weight gain", "चेहरे / शरीर पर बाल, मुँहासे, वज़न बढ़ना", "चेहऱ्यावर / अंगावर केस, मुरुमे, वजन वाढ", ["Polycystic ovary syndrome"]),
    O("thyroid", "Thyroid symptoms", "थायराइड के लक्षण", "थायरॉईडची लक्षणे", ["Thyroid disorder"]),
    O("milk", "Milky discharge from breasts (not breastfeeding)", "स्तन से दूध जैसा स्राव (स्तनपान नहीं)", "स्तनातून दुधासारखा स्राव (स्तनपान नाही)", ["Hyperprolactinaemia"]),
    O("weight_loss_sport", "Big weight loss / heavy exercise / stress", "बहुत वज़न घटा / भारी कसरत / तनाव", "खूप वजन घटले / जड व्यायाम / ताण", ["Hypothalamic amenorrhoea"]),
    O("bruising", "Easy bruising / bleeding gums", "आसानी से नील / मसूड़ों से ख़ून", "सहज काळे-निळे / हिरड्यांतून रक्त", ["Bleeding disorder"]),
    O("hot_flushes", "Hot flushes / age 45+", "गर्मी की लहरें / 45+ उम्र", "उष्णतेच्या लाटा / 45+ वय", ["Perimenopause"])],
  src=MN)
Q("pd_contraception", "periods", "risk", 7, "choice", "Contraception", "गर्भनिरोधक", "गर्भनिरोधक", term="Contraception", applies=REPRO, opts=[
    O("none", "None", "कुछ नहीं", "काही नाही"), O("copper_t", "Copper-T / IUCD", "कॉपर-टी", "कॉपर-टी", ["IUCD-related bleeding"]),
    O("pills", "Pills (Mala-D / Chhaya)", "गोली (माला-डी / छाया)", "गोळी (माला-डी / छाया)", ["Hormonal contraception"]),
    O("injection", "Injection (Antara)", "इंजेक्शन (अंतरा)", "इंजेक्शन (अंतरा)", ["Hormonal contraception"]),
    O("condom", "Condom", "कंडोम", "कंडोम"), O("sterilised", "Operation (tubectomy) / husband vasectomy", "ऑपरेशन (नसबंदी)", "ऑपरेशन (नसबंदी)")],
  src=f"{WM}, p47 (Box 5.2)")
Q("pd_smear", "periods", "risk", 8, "choice", "Cervical screening (Pap / VIA test) done?", "क्या बच्चेदानी के मुँह की जाँच (पैप / VIA) हुई है?", "गर्भाशयमुखाची तपासणी (पॅप / VIA) झाली आहे का?",
  term="Cervical cytology history", applies={"sex": "female", "min_age": 25}, opts=[
      O("lt3y", "Within 3 years, normal", "3 साल के अंदर, सामान्य", "3 वर्षांच्या आत, सामान्य"),
      O("abnormal", "Abnormal result before", "पहले असामान्य रिपोर्ट", "आधी असामान्य रिपोर्ट", ["Cervical lesion / polyp", "Cervical cancer"]),
      O("never", "Never / don't know", "कभी नहीं / पता नहीं", "कधीच नाही / माहीत नाही")],
  src=f"{WM}, p47 (cervical cytology history)")

# ---------------------------------------------------------------- POST-MENOPAUSAL BLEEDING
PM = f"{WM}, p47 (Box 5.2)"
Q("pmb_flag", "pmb", "redflag", 1, "yesno", "Any bleeding / spotting more than 12 months after periods stopped?", "क्या माहवारी बंद होने के 12 महीने बाद कोई ख़ून / धब्बा?",
  "पाळी थांबल्यानंतर 12 महिन्यांनी कोणताही रक्तस्राव / डाग?", term="Post-menopausal bleeding", rf="Post-menopausal bleeding — exclude endometrial / cervical cancer (urgent USG / biopsy)",
  ddx=["Endometrial cancer", "Cervical cancer", "Atrophic vaginitis", "Endometrial polyp"], applies={"sex": "female", "min_age": 40}, src=PM)
Q("pmb_details", "pmb", "hopi", 2, "multi", "Details", "विवरण", "तपशील", term="Associated features", applies={"sex": "female", "min_age": 40}, opts=[
    O("after_sex", "After intercourse", "संभोग के बाद", "संभोगानंतर", ["Cervical cancer", "Atrophic vaginitis"]),
    O("smelly_discharge", "Foul-smelling / blood-stained discharge", "बदबूदार / ख़ून वाला स्राव", "दुर्गंधीयुक्त / रक्तमिश्रित स्राव", ["Cervical cancer", "Endometrial cancer"]),
    O("dryness", "Dryness / pain with intercourse", "सूखापन / संभोग में दर्द", "कोरडेपणा / संभोगात दुखणे", ["Atrophic vaginitis"]),
    O("hrt_tamoxifen", "On hormone tablets / tamoxifen", "हार्मोन की गोली / टैमोक्सीफ़ेन", "हार्मोन गोळी / टॅमॉक्सिफेन", ["Endometrial pathology"]),
    O("risk", "Overweight / diabetes / never pregnant", "मोटापा / शुगर / कभी गर्भ नहीं", "लठ्ठपणा / मधुमेह / कधी गर्भधारणा नाही", ["Endometrial cancer"]),
    O("wt_loss_mass", "Weight loss / belly swelling", "वज़न घटना / पेट फूलना", "वजन घटणे / पोट फुगणे", ["Ovarian cancer", "Endometrial cancer"])],
  src=PM)

# ---------------------------------------------------------------- VAGINAL DISCHARGE
VD = f"{WM}, p46-47; {H}, Ch 17, p369 (Box 17.4)"
Q("vd_type", "vaginal_discharge", "hopi", 1, "choice", "What is it like?", "स्राव कैसा है?", "स्राव कसा आहे?", term="Character", applies=FEM, opts=[
    O("white_curd_itch", "Thick white, curd-like, very itchy", "गाढ़ा सफ़ेद, दही जैसा, बहुत खुजली", "दाट पांढरा, दह्यासारखा, खूप खाज", ["Candida (thrush)"]),
    O("grey_fishy", "Thin grey, fishy smell (worse after sex)", "पतला स्लेटी, मछली जैसी गंध (संभोग के बाद ज़्यादा)", "पातळ करडा, माशासारखा वास (संभोगानंतर जास्त)", ["Bacterial vaginosis"]),
    O("yellow_green_frothy", "Yellow-green, frothy, itchy, sore", "पीला-हरा, झागदार, खुजली, जलन", "पिवळा-हिरवा, फेसाळ, खाज, जळजळ", ["Trichomoniasis"]),
    O("pus_pain", "Pus-like with lower belly pain / fever", "मवाद जैसा, नीचे पेट दर्द / बुखार", "पूसारखा, ओटीपोटात दुखणे / ताप", ["Pelvic inflammatory disease", "Gonorrhoea / chlamydia (urethritis)"]),
    O("clear_normal", "Clear / white, no itch or smell (varies with cycle)", "साफ़ / सफ़ेद, न खुजली न गंध (चक्र के साथ बदलता)", "स्वच्छ / पांढरा, खाज-वास नाही (चक्रासोबत बदलतो)", ["Physiological discharge"]),
    O("blood_stained", "Blood-stained / foul (older woman)", "ख़ून वाला / बदबूदार (बड़ी उम्र)", "रक्तमिश्रित / दुर्गंधीयुक्त (जास्त वय)", ["Cervical cancer"])],
  src=VD)
Q("vd_pid_flag", "vaginal_discharge", "redflag", 2, "yesno", "Discharge with fever, lower belly pain, or pain during intercourse?", "क्या स्राव के साथ बुखार, नीचे पेट दर्द, या संभोग में दर्द?",
  "स्रावासोबत ताप, ओटीपोटात दुखणे, किंवा संभोगात दुखणे?", term="Features of PID", rf="Possible pelvic inflammatory disease — examine & treat promptly (exclude ectopic)", ddx=["Pelvic inflammatory disease"], applies=REPRO, src=VD)
Q("vd_risk", "vaginal_discharge", "risk", 3, "multi", "Risk factors", "जोखिम", "जोखीम", term="Risk factors", applies=FEM, opts=[
    O("dm", "Diabetes / recent antibiotics", "शुगर / हाल में एंटीबायोटिक", "मधुमेह / अलीकडे अँटिबायोटिक", ["Candida (thrush)"]),
    O("pregnant", "Pregnant", "गर्भवती", "गर्भवती", ["Candida (thrush)", "Bacterial vaginosis"]),
    O("partner", "New partner / partner has symptoms", "नया साथी / साथी को लक्षण", "नवीन जोडीदार / जोडीदाराला लक्षणे", ["Trichomoniasis", "Gonorrhoea / chlamydia (urethritis)"]),
    O("douching_cloth", "Douching / reusing cloth pads", "अंदर धोना / कपड़े का पैड दोबारा", "आत धुणे / कापडी पॅड पुन्हा वापरणे", ["Bacterial vaginosis"]),
    O("copper_t", "Copper-T", "कॉपर-टी", "कॉपर-टी", ["Pelvic inflammatory disease"]),
    O("recent_procedure", "Recent abortion / delivery / D&C", "हाल में गर्भपात / डिलीवरी / सफ़ाई", "अलीकडे गर्भपात / प्रसूती / सफाई", ["Pelvic inflammatory disease", "Puerperal sepsis"])],
  src=VD)

# ---------------------------------------------------------------- PELVIC PAIN
PP = f"{WM}, p46"
Q("pp_emergency", "pelvic_pain", "redflag", 1, "yesno", "Sudden severe lower belly pain with missed period, fainting, or shoulder-tip pain?",
  "क्या अचानक तेज़ नीचे पेट दर्द, साथ में माहवारी रुकी, बेहोशी, या कंधे के सिरे में दर्द?", "अचानक तीव्र ओटीपोटात दुखणे, सोबत पाळी चुकली, बेशुद्धी, किंवा खांद्याच्या टोकाला दुखणे?",
  term="Possible ruptured ectopic / torsion", rf="Possible ruptured ectopic pregnancy / ovarian torsion — EMERGENCY (UPT, IV access, gynae)",
  ddx=["Ovarian / ectopic", "Ovarian torsion"], applies=REPRO, src=f"{PP}; {H}, Ch 9")
Q("pp_pattern", "pelvic_pain", "hopi", 2, "choice", "Pattern", "दर्द का तरीका", "दुखण्याचा प्रकार", term="Pattern", applies=FEM, opts=[
    O("cyclical", "With every period", "हर माहवारी के साथ", "प्रत्येक पाळीसोबत", ["Primary dysmenorrhoea", "Endometriosis", "Adenomyosis"]),
    O("mid_cycle", "Mid-cycle, one side, short", "माहवारी के बीच में, एक तरफ, थोड़ी देर", "पाळीच्या मध्ये, एका बाजूला, थोडा वेळ", ["Mittelschmerz (ovulation pain)"]),
    O("cyclical_then_constant", "Started with periods, now constant", "माहवारी के साथ शुरू, अब लगातार", "पाळीसोबत सुरू, आता सतत", ["Pelvic adhesions", "Endometriosis"]),
    O("acute_fever", "Sudden with fever / discharge", "अचानक, बुखार / स्राव के साथ", "अचानक, ताप / स्रावासोबत", ["Pelvic inflammatory disease"]),
    O("acute_one_side_vomit", "Sudden one-sided with vomiting", "अचानक एक तरफ, उल्टी के साथ", "अचानक एका बाजूला, उलटीसोबत", ["Ovarian torsion", "Ovarian cyst rupture", "Appendicitis"]),
    O("chronic", "Long-standing, months", "लंबे समय से, महीनों से", "बराच काळ, महिन्यांपासून", ["Chronic pelvic pain", "Pelvic inflammatory disease", "Irritable bowel syndrome"])],
  src=f"{PP} (cyclical pain = endometriosis; becoming continuous = adhesions)")
Q("pp_other_systems", "pelvic_pain", "associated", 3, "multi", "Bowel / bladder (always ask)", "पाखाना / पेशाब (ज़रूर पूछें)", "शौच / लघवी (नक्की विचारा)", term="Bowel & bladder symptoms", applies=FEM, opts=[
    O("burning_urine", "Burning / frequent urine", "पेशाब में जलन / बार-बार", "लघवीची जळजळ / वारंवार", ["Cystitis / UTI"]),
    O("bowel_change", "Constipation / loose / bloating relieved by stool", "कब्ज़ / दस्त / मल के बाद आराम", "बद्धकोष्ठता / जुलाब / शौचानंतर आराम", ["Irritable bowel syndrome"]),
    O("blood_stool_period", "Blood in stool / urine during periods", "माहवारी में मल / पेशाब में ख़ून", "पाळीत शौच / लघवीत रक्त", ["Endometriosis"])],
  src=f"{PP} (bowel & bladder history)")

# ---------------------------------------------------------------- PROLAPSE  (Box 5.3)
PR = f"{WM}, p47 (Box 5.3)"
Q("pr_symptoms", "prolapse", "hopi", 1, "multi", "Symptoms", "लक्षण", "लक्षणे", term="Prolapse symptoms (Box 5.3)", applies=FEM, opts=[
    O("dragging", "Feeling of something coming down / dragging", "नीचे कुछ उतरने / खिंचाव का एहसास", "खाली काही उतरल्याची / ओढल्याची भावना", ["Uterovaginal prolapse"]),
    O("lump", "Lump at vaginal opening", "योनि के मुँह पर गाँठ", "योनीच्या तोंडाशी गाठ", ["Uterovaginal prolapse"]),
    O("better_lying", "Better when lying down / in morning", "लेटने पर / सुबह बेहतर", "झोपल्यावर / सकाळी बरे", ["Uterovaginal prolapse"]),
    O("leak_cough", "Urine leaks on cough / sneeze", "खाँसने / छींकने पर पेशाब निकलना", "खोकल्यावर / शिंकल्यावर लघवी गळणे", ["Stress incontinence"]),
    O("incomplete_urine", "Has to push lump back to pass urine / stool", "पेशाब / मल के लिए गाँठ अंदर करनी पड़ती", "लघवी / शौचासाठी गाठ आत ढकलावी लागते", ["Uterovaginal prolapse"]),
    O("ulcer_bleed", "Sore / bleeding on the lump", "गाँठ पर घाव / ख़ून", "गाठीवर जखम / रक्त", ["Decubitus ulcer of prolapse"])],
  src=PR)
Q("pr_risk", "prolapse", "risk", 2, "multi", "Risk factors", "जोखिम", "जोखीम", term="Risk factors", applies=FEM, opts=[
    O("many_deliveries", "Many / home / difficult deliveries", "कई / घर पर / कठिन डिलीवरी", "अनेक / घरी / कठीण प्रसूती", ["Uterovaginal prolapse"]),
    O("heavy_work", "Heavy lifting / farm work soon after delivery", "डिलीवरी के तुरंत बाद भारी काम / खेती", "प्रसूतीनंतर लगेच जड काम / शेती", ["Uterovaginal prolapse"]),
    O("cough_constipation", "Chronic cough / constipation", "पुरानी खाँसी / कब्ज़", "जुना खोकला / बद्धकोष्ठता", ["Uterovaginal prolapse"]),
    O("menopause", "After menopause", "माहवारी बंद होने के बाद", "रजोनिवृत्तीनंतर", ["Uterovaginal prolapse"])],
  src=PR)
Q("pr_retention", "prolapse", "redflag", 3, "yesno", "Unable to pass urine at all / kidney swelling noted?", "क्या पेशाब बिल्कुल नहीं हो रहा?", "लघवी अजिबात होत नाही?",
  term="Urinary retention with prolapse", rf="Prolapse with urinary retention — urgent (risk to kidneys)", ddx=["Acute urinary retention"], applies=FEM, src=PR)

# ---------------------------------------------------------------- PREGNANCY  (Box 5.5 + ANC danger signs)
PG = f"{WM}, p48 (Box 5.5)"
Q("pg_details", "pregnancy", "hopi", 1, "text", "LMP, weeks of pregnancy, number of pregnancies / deliveries / abortions (G P A L)", "आख़िरी माहवारी, कितने हफ़्ते, कितनी बार गर्भ / डिलीवरी / गर्भपात",
  "शेवटची पाळी, किती आठवडे, किती वेळा गर्भ / प्रसूती / गर्भपात", term="Obstetric formula (GPAL), gestational age", applies=REPRO, src=PG)
Q("pg_danger", "pregnancy", "redflag", 2, "multi", "Danger signs now", "अभी ख़तरे के निशान", "आता धोक्याची चिन्हे", term="Pregnancy danger signs", applies=REPRO, opts=[
    O("bleeding", "Bleeding from vagina", "योनि से ख़ून", "योनीतून रक्त", ["Antepartum haemorrhage / miscarriage"]),
    O("pain", "Severe belly pain", "तेज़ पेट दर्द", "तीव्र पोटदुखी", ["Placental abruption", "Ovarian / ectopic"]),
    O("headache_vision", "Severe headache / blurred vision / swelling of face-hands", "तेज़ सिर दर्द / धुंधला दिखना / चेहरे-हाथ पर सूजन", "तीव्र डोकेदुखी / अंधुक दिसणे / चेहरा-हात सुजणे", ["Pre-eclampsia"]),
    O("fits", "Fits / unconscious", "दौरा / बेहोशी", "झटके / बेशुद्धी", ["Eclampsia"]),
    O("leaking", "Water leaking", "पानी निकलना", "पाणी जाणे", ["Premature rupture of membranes"]),
    O("less_movement", "Baby moving less / not moving", "बच्चे की हलचल कम / नहीं", "बाळाची हालचाल कमी / नाही", ["Fetal distress"]),
    O("fever", "High fever", "तेज़ बुखार", "तीव्र ताप", ["Infection in pregnancy (malaria / UTI / sepsis)"]),
    O("breathless", "Breathlessness / palpitations", "साँस फूलना / धड़कन", "धाप / धडधड", ["Severe anaemia", "Heart disease in pregnancy"]),
    O("vomiting", "Vomiting everything, can't keep water down", "सब उल्टी, पानी भी नहीं रुकता", "सगळे उलटून पडते, पाणीही टिकत नाही", ["Hyperemesis gravidarum"])],
  src=ANC)
Q("pg_danger_flag", "pregnancy", "redflag", 3, "yesno", "Any danger sign: bleeding, severe pain, headache / blurred vision, fits, leaking, less baby movement, fever?",
  "क्या कोई ख़तरे का निशान: ख़ून, तेज़ दर्द, सिर दर्द / धुंधला दिखना, दौरा, पानी निकलना, हलचल कम, बुखार?",
  "कोणतेही धोक्याचे चिन्ह: रक्त, तीव्र दुखणे, डोकेदुखी / अंधुक दिसणे, झटके, पाणी जाणे, हालचाल कमी, ताप?",
  term="Obstetric emergency", rf="PREGNANCY DANGER SIGN — check BP, FHS, urine protein; obstetric review NOW / refer to FRU", ddx=["Pre-eclampsia", "Antepartum haemorrhage / miscarriage", "Eclampsia"],
  applies=REPRO, src=ANC)
Q("pg_high_risk", "pregnancy", "risk", 4, "multi", "High-risk factors", "हाई-रिस्क बातें", "उच्च-धोक्याच्या गोष्टी", term="High-risk pregnancy factors", applies=REPRO, opts=[
    O("prev_cs", "Previous caesarean", "पहले सिज़ेरियन", "आधी सिझेरियन", ["High-risk pregnancy"]),
    O("prev_loss", "Previous stillbirth / miscarriages / baby died", "पहले मृत शिशु / गर्भपात / बच्चे की मौत", "आधी मृत बाळ / गर्भपात / बाळाचा मृत्यू", ["High-risk pregnancy"]),
    O("bp_sugar", "High BP / sugar (before or in pregnancy)", "हाई बीपी / शुगर (पहले या गर्भ में)", "उच्च रक्तदाब / साखर (आधी किंवा गर्भात)", ["Pre-eclampsia", "Gestational diabetes"]),
    O("age", "Age under 18 or over 35", "उम्र 18 से कम या 35 से ज़्यादा", "वय 18 पेक्षा कमी किंवा 35 पेक्षा जास्त", ["High-risk pregnancy"]),
    O("twins", "Twins", "जुड़वाँ", "जुळे", ["High-risk pregnancy"]),
    O("anaemia", "Low Hb / not taking iron tablets", "Hb कम / आयरन की गोली नहीं", "Hb कमी / आयर्न गोळी नाही", ["Severe anaemia"]),
    O("heart_thyroid_epilepsy", "Heart / thyroid / epilepsy / TB / HIV", "दिल / थायराइड / मिर्गी / टीबी / एचआईवी", "हृदय / थायरॉईड / आकडी / टीबी / एचआयव्ही", ["High-risk pregnancy"]),
    O("rh_neg", "Rh-negative blood group", "आरएच-नेगेटिव ब्लड ग्रुप", "आरएच-निगेटिव्ह रक्तगट", ["Rh isoimmunisation risk"])],
  src=f"{PG}; {ANC}")
Q("pg_care", "pregnancy", "hopi", 5, "multi", "Antenatal care so far", "अब तक की जाँच", "आतापर्यंतची तपासणी", term="ANC received", applies=REPRO, opts=[
    O("registered", "Registered (MCP card)", "रजिस्ट्रेशन (MCP कार्ड)", "नोंदणी (MCP कार्ड)"),
    O("tt", "TT / Td injections", "टीटी / टीडी इंजेक्शन", "टीटी / टीडी इंजेक्शन"),
    O("ifa", "Iron & folic acid tablets", "आयरन और फ़ोलिक एसिड की गोली", "आयर्न व फॉलिक ॲसिड गोळी"),
    O("usg", "Ultrasound done", "सोनोग्राफ़ी हुई", "सोनोग्राफी झाली"),
    O("tests", "Blood tests (Hb, sugar, HIV, HBsAg, blood group)", "ख़ून की जाँच (Hb, शुगर, एचआईवी, HBsAg, ब्लड ग्रुप)", "रक्त तपासणी (Hb, साखर, एचआयव्ही, HBsAg, रक्तगट)")],
  src=ANC)
Q("pg_drugs", "pregnancy", "risk", 6, "yesno", "Taking any medicines / desi medicines / X-ray done in pregnancy?", "क्या गर्भ में कोई दवा / देसी दवा / एक्स-रे?", "गर्भात कोणते औषध / देशी औषध / एक्स-रे?",
  term="Drug / radiation exposure in pregnancy", applies=REPRO, src="General clinical practice")

# ---------------------------------------------------------------- AFTER DELIVERY (postpartum, first 6 weeks)
PN = ANC
Q("pn_when", "postpartum", "hopi", 1, "text", "Date and type of delivery (normal / caesarean, home / hospital)", "डिलीवरी कब और कैसे (नॉर्मल / सिज़ेरियन, घर / अस्पताल)?",
  "प्रसूती कधी आणि कशी (नॉर्मल / सिझेरियन, घरी / रुग्णालयात)?", term="Delivery details", applies=REPRO, src=PN)
Q("pn_danger", "postpartum", "redflag", 2, "multi", "Danger signs", "ख़तरे के निशान", "धोक्याची चिन्हे", term="Postpartum danger signs", applies=REPRO, opts=[
    O("heavy_bleed", "Heavy bleeding (soaking pad in an hour) / clots", "बहुत ख़ून (एक घंटे में पैड भीगना) / थक्के", "खूप रक्त (एका तासात पॅड भिजणे) / गुठळ्या", ["Postpartum haemorrhage"]),
    O("fever_smell", "Fever / foul-smelling discharge / belly pain", "बुखार / बदबूदार स्राव / पेट दर्द", "ताप / दुर्गंधीयुक्त स्राव / पोटदुखी", ["Puerperal sepsis"]),
    O("headache_fits", "Severe headache / blurred vision / fits", "तेज़ सिर दर्द / धुंधला दिखना / दौरा", "तीव्र डोकेदुखी / अंधुक / झटके", ["Pre-eclampsia", "Eclampsia", "Cerebral venous thrombosis"]),
    O("breathless_calf", "Breathless / chest pain / one leg swollen", "साँस फूलना / सीने में दर्द / एक पैर सूजा", "धाप / छातीत दुखणे / एक पाय सुजला", ["Pulmonary embolism", "Deep vein thrombosis"]),
    O("wound", "Stitches / caesarean wound red, painful, pus", "टाँके / ऑपरेशन का घाव लाल, दर्द, मवाद", "टाके / ऑपरेशनची जखम लाल, दुखरी, पू", ["Wound infection"]),
    O("mood", "Very low / confused / strange thoughts / thoughts of harming self or baby", "बहुत उदास / उलझन / अजीब विचार / ख़ुद को या बच्चे को नुक़सान के विचार", "खूप उदास / गोंधळ / विचित्र विचार / स्वतःला किंवा बाळाला इजेचे विचार", ["Postpartum psychosis", "Postnatal depression"])],
  src=PN)
Q("pn_danger_flag", "postpartum", "redflag", 3, "yesno", "Heavy bleeding, fever, fits / severe headache, breathlessness, or thoughts of harming self / baby?",
  "क्या बहुत ख़ून, बुखार, दौरा / तेज़ सिर दर्द, साँस फूलना, या ख़ुद को / बच्चे को नुक़सान के विचार?", "खूप रक्त, ताप, झटके / तीव्र डोकेदुखी, धाप, किंवा स्वतःला / बाळाला इजेचे विचार?",
  term="Postpartum emergency", rf="POSTPARTUM DANGER SIGN — EMERGENCY (PPH / sepsis / eclampsia / PE / psychosis)", ddx=["Postpartum haemorrhage", "Puerperal sepsis", "Postpartum psychosis"],
  applies=REPRO, src=PN)
Q("pn_breast", "postpartum", "associated", 4, "multi", "Breastfeeding", "स्तनपान", "स्तनपान", term="Breastfeeding issues", applies=REPRO, opts=[
    O("painful_red", "Painful red hard area in breast, fever", "स्तन में दर्दनाक लाल सख़्त जगह, बुखार", "स्तनात दुखरा लाल कडक भाग, ताप", ["Mastitis / breast abscess"]),
    O("cracked", "Cracked / sore nipples", "निप्पल फटे / दर्द", "स्तनाग्र फाटले / दुखणे", ["Poor latch"]),
    O("low_milk", "Feels milk is less / baby not gaining", "दूध कम लगता / बच्चे का वज़न नहीं बढ़ता", "दूध कमी वाटते / बाळाचे वजन वाढत नाही", ["Breastfeeding difficulty"])],
  src=PN)
Q("pn_baby", "postpartum", "associated", 5, "multi", "Baby (if with mother)", "बच्चा", "बाळ", term="Newborn danger signs", applies=REPRO, opts=[
    O("not_feeding", "Not feeding / very sleepy", "दूध नहीं पीता / बहुत सुस्त", "दूध पीत नाही / खूप सुस्त", ["Neonatal sepsis"]),
    O("yellow_early", "Yellow on day 1 or yellow palms/soles", "पहले दिन पीला या हथेली/तलवे पीले", "पहिल्या दिवशी पिवळे किंवा तळहात/तळपाय पिवळे", ["Neonatal jaundice (severe)"]),
    O("fever_cold", "Fever or very cold", "बुखार या बहुत ठंडा", "ताप किंवा खूप थंड", ["Neonatal sepsis"]),
    O("fast_breath", "Fast breathing / chest indrawing", "तेज़ साँस / पसलियाँ धँसना", "जलद श्वास / बरगड्या आत ओढल्या जाणे", ["Neonatal sepsis / pneumonia"]),
    O("cord", "Red / pus at umbilical cord", "नाल पर लाली / मवाद", "नाळेवर लाली / पू", ["Omphalitis"])],
  src="IMNCI newborn danger signs — general clinical practice")

# ---------------------------------------------------------------- INFERTILITY
IF = f"{WM}, p48"
Q("if_duration", "infertility", "hopi", 1, "choice", "Trying to conceive for how long (regular unprotected intercourse)?", "कितने समय से गर्भ के लिए कोशिश (नियमित, बिना गर्भनिरोधक)?",
  "किती काळापासून गर्भधारणेचा प्रयत्न (नियमित, गर्भनिरोधकाशिवाय)?", term="Duration of infertility", applies=REPRO, opts=[
      O("lt1y", "Less than 1 year", "1 साल से कम", "1 वर्षापेक्षा कमी"),
      O("1to3y", "1–3 years", "1–3 साल", "1–3 वर्षे", ["Infertility"]),
      O("gt3y", "More than 3 years", "3 साल से ज़्यादा", "3 वर्षांपेक्षा जास्त", ["Infertility"])],
  src=IF)
Q("if_type", "infertility", "hopi", 2, "choice", "Ever been pregnant before?", "क्या पहले कभी गर्भ ठहरा?", "आधी कधी गर्भधारणा झाली?", term="Primary vs secondary", applies=REPRO, opts=[
    O("never", "Never (primary)", "कभी नहीं", "कधीच नाही", ["Primary infertility"]),
    O("before", "Yes, before (secondary)", "हाँ, पहले", "हो, आधी", ["Secondary infertility"])],
  src=IF)
Q("if_female_factors", "infertility", "associated", 3, "multi", "Woman's factors", "महिला के कारण", "महिलेची कारणे", term="Female factors", applies=REPRO, opts=[
    O("irregular", "Irregular / no periods", "अनियमित / माहवारी नहीं", "अनियमित / पाळी नाही", ["Polycystic ovary syndrome", "Ovulatory dysfunction"]),
    O("painful", "Painful periods / pain with sex", "दर्दनाक माहवारी / संभोग में दर्द", "दुखरी पाळी / संभोगात दुखणे", ["Endometriosis"]),
    O("pid_tb", "Past PID / pelvic TB / abortion with infection", "पहले PID / पेट की टीबी / इन्फेक्शन वाला गर्भपात", "आधी PID / ओटीपोटाचा टीबी / संसर्गासह गर्भपात", ["Tubal factor", "Genital TB"]),
    O("surgery", "Previous pelvic / tube surgery", "पहले पेट / नली का ऑपरेशन", "आधी ओटीपोट / नलिकेचे ऑपरेशन", ["Tubal factor"]),
    O("thyroid_prolactin", "Thyroid / milky breast discharge", "थायराइड / स्तन से दूध जैसा स्राव", "थायरॉईड / स्तनातून दुधासारखा स्राव", ["Thyroid disorder", "Hyperprolactinaemia"]),
    O("weight", "Very over / under weight", "बहुत ज़्यादा / कम वज़न", "खूप जास्त / कमी वजन", ["Ovulatory dysfunction"])],
  src=IF)
Q("if_male", "infertility", "associated", 4, "multi", "Husband / partner (both must be assessed)", "पति / साथी (दोनों की जाँच ज़रूरी)", "पती / जोडीदार (दोघांची तपासणी आवश्यक)",
  term="Male factor", applies=REPRO, opts=[
      O("semen_test", "Semen test done", "वीर्य जाँच हुई", "वीर्य तपासणी झाली"),
      O("mumps_surgery", "Mumps / hernia or testis surgery", "गलसुआ / हर्निया या अंडकोष का ऑपरेशन", "गालगुंड / हर्निया किंवा अंडकोष ऑपरेशन", ["Male factor infertility"]),
      O("alcohol_smoke", "Alcohol / smoking / tobacco", "शराब / धूम्रपान / तंबाकू", "दारू / धूम्रपान / तंबाखू", ["Male factor infertility"]),
      O("dm_erectile", "Diabetes / erection problems", "शुगर / तनाव की कमी", "मधुमेह / ताठरता कमी", ["Male factor infertility"]),
      O("away", "Works away / infrequent intercourse", "बाहर काम / संभोग कम", "बाहेर काम / संभोग कमी", [])],
  src=IF)

# ---------------------------------------------------------------- BREAST
BR = f"{H}, Ch 2, p20"
Q("bs_type", "breast", "hopi", 1, "multi", "Breast problem", "स्तन की तकलीफ़", "स्तनाचा त्रास", term="Breast symptoms", applies=FEM, opts=[
    O("lump", "Lump", "गाँठ", "गाठ", ["Fibroadenoma", "Breast cancer", "Breast cyst"]),
    O("pain_cyclical", "Pain before periods, both breasts", "माहवारी से पहले दोनों स्तनों में दर्द", "पाळीआधी दोन्ही स्तनांत दुखणे", ["Cyclical mastalgia"]),
    O("pain_one_hot", "One breast red, hot, painful (breastfeeding)", "एक स्तन लाल, गर्म, दर्दनाक (स्तनपान)", "एक स्तन लाल, गरम, दुखरा (स्तनपान)", ["Mastitis / breast abscess"]),
    O("bloody_discharge", "Blood-stained nipple discharge", "निप्पल से ख़ून वाला स्राव", "स्तनाग्रातून रक्तमिश्रित स्राव", ["Duct papilloma", "Breast cancer"]),
    O("milky", "Milky discharge (not breastfeeding)", "दूध जैसा स्राव (स्तनपान नहीं)", "दुधासारखा स्राव (स्तनपान नाही)", ["Hyperprolactinaemia"]),
    O("skin_nipple", "Skin dimpling / orange-peel / nipple pulled in (new)", "त्वचा में गड्ढा / संतरे के छिलके जैसी / निप्पल अंदर (नया)", "त्वचेत खड्डा / संत्र्याच्या सालीसारखी / स्तनाग्र आत (नवीन)", ["Breast cancer"])],
  src=BR)
Q("bs_flag", "breast", "redflag", 2, "yesno", "Hard / fixed lump, bloody discharge, skin dimpling, nipple pulled in, or armpit lump?",
  "क्या सख़्त / चिपकी गाँठ, ख़ून वाला स्राव, त्वचा में गड्ढा, निप्पल अंदर, या बगल में गाँठ?", "कडक / चिकटलेली गाठ, रक्तमिश्रित स्राव, त्वचेत खड्डा, स्तनाग्र आत, किंवा काखेत गाठ?",
  term="Suspicious breast features", rf="Suspicious breast lump — urgent triple assessment (exam, imaging, biopsy)", ddx=["Breast cancer"], applies=FEM, src=BR)
Q("bs_risk", "breast", "risk", 3, "multi", "Risk factors", "जोखिम", "जोखीम", term="Breast cancer risk factors", applies=FEM, opts=[
    O("family", "Breast / ovary cancer in mother / sister", "माँ / बहन को स्तन / अंडाशय का कैंसर", "आई / बहिणीला स्तन / अंडाशय कर्करोग", ["Breast cancer"]),
    O("age_over40", "Age over 40", "उम्र 40 से ज़्यादा", "वय 40 पेक्षा जास्त", ["Breast cancer"]),
    O("no_breastfeed", "Never breastfed / first child after 30", "कभी स्तनपान नहीं / पहला बच्चा 30 के बाद", "कधी स्तनपान नाही / पहिले बाळ 30 नंतर", ["Breast cancer"]),
    O("hrt", "Hormone therapy", "हार्मोन थेरेपी", "हार्मोन थेरपी", ["Breast cancer"])],
  src=BR)
