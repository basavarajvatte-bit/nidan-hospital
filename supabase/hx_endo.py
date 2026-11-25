# ====================================================================== SYSTEM 7: ENDOCRINE + METABOLIC
# Hutchison 24e, Ch 18 (Endocrine and metabolic disorders), p379-402; Box 18.1-18.11. Executed inside hx_bank.py.

EN = f"{H}, Ch 18"

C("thirst", "Endocrine", "Excess thirst / urine (sugar symptoms)", "ज़्यादा प्यास / ज़्यादा पेशाब", "जास्त तहान / जास्त लघवी", "🥤", 71, f"{EN}, p379, p393")
C("diabetes_review", "Endocrine", "Diabetes check-up", "शुगर (डायबिटीज़) की जाँच", "मधुमेह तपासणी", "🩸", 72, f"{EN}, p393-399 (Box 18.10-18.11)")
C("thyroid", "Endocrine", "Thyroid / neck swelling", "थायराइड / गले में सूजन", "थायरॉईड / गळ्याला सूज", "🦋", 73, f"{EN}, p380-382 (Box 18.1, 18.6)")
C("weight_gain", "Endocrine", "Weight gain", "वज़न बढ़ना", "वजन वाढणे", "📈", 74, f"{EN}, p379-380 (Box 18.3)")
C("fatigue", "Endocrine", "Tiredness / weakness all over", "थकान / पूरे शरीर में कमज़ोरी", "थकवा / संपूर्ण अंगात अशक्तपणा", "🥱", 75, f"{EN}, p379-380")

# ---------------------------------------------------------------- THIRST / POLYURIA
TH = f"{EN}, p379, p393"
Q("th_features", "thirst", "hopi", 1, "multi", "Along with thirst", "प्यास के साथ", "तहानेसोबत", term="Osmotic symptoms", opts=[
    O("urine_night", "Passing a lot of urine, also at night", "बहुत पेशाब, रात को भी", "खूप लघवी, रात्रीही", ["Diabetes"]),
    O("wt_loss", "Weight loss despite eating", "खाने के बाद भी वज़न घटना", "खाऊनही वजन घटणे", ["Diabetes", "Thyrotoxicosis"]),
    O("hungry", "Always hungry", "हमेशा भूख", "नेहमी भूक", ["Diabetes", "Thyrotoxicosis"]),
    O("blurred", "Blurred vision", "धुंधला दिखना", "अंधुक दिसणे", ["Diabetes"]),
    O("infections", "Boils / fungal itch in groin / slow-healing wounds", "फोड़े / जांघ में खुजली / घाव देर से भरना", "गळू / जांघेत खाज / जखम उशिरा भरणे", ["Diabetes"]),
    O("tired", "Tiredness", "थकान", "थकवा", ["Diabetes"])],
  src=TH)
Q("th_dka", "thirst", "redflag", 2, "yesno", "Vomiting, tummy pain, fast deep breathing, fruity breath or drowsiness?",
  "क्या उल्टी, पेट दर्द, तेज़ गहरी साँस, मुँह से फल जैसी गंध या सुस्ती?", "उलटी, पोटदुखी, जलद खोल श्वास, तोंडाला फळासारखा वास किंवा गुंगी?",
  term="Features of DKA / HHS", rf="Possible diabetic ketoacidosis / HHS — check sugar & ketones NOW", ddx=["Diabetic ketoacidosis", "Hyperosmolar hyperglycaemic state"], src=f"{EN}, p393")
Q("th_young_fast", "thirst", "hopi", 3, "yesno", "Young / thin patient with rapid onset over weeks?", "क्या कम उम्र / दुबला मरीज़ और हफ़्तों में तेज़ी से शुरू?",
  "कमी वय / कृश रुग्ण आणि आठवड्यांत वेगाने सुरू?", term="Type 1 pattern", ddx=["Type 1 diabetes"], src=f"{EN}, p393 (Box 18.8)")
Q("th_risk", "thirst", "risk", 4, "multi", "Diabetes risk factors", "शुगर के कारण", "मधुमेहाची कारणे", term="Type 2 diabetes risk factors", opts=[
    O("family", "Parent / sibling with diabetes", "माता-पिता / भाई-बहन को शुगर", "आई-वडील / भावंडांना मधुमेह", ["Type 2 diabetes"]),
    O("obese", "Overweight / big belly", "मोटापा / पेट बड़ा", "लठ्ठपणा / मोठे पोट", ["Type 2 diabetes"]),
    O("gdm", "Sugar in pregnancy before / big baby (>4 kg)", "पहले गर्भ में शुगर / बड़ा बच्चा (4 किलो+)", "आधी गर्भारपणात मधुमेह / मोठे बाळ (4 किलो+)", ["Type 2 diabetes"], only={"sex": "female"}),
    O("steroid", "Steroids / desi powders (may contain steroid)", "स्टेरॉयड / देसी चूर्ण (स्टेरॉयड हो सकता)", "स्टिरॉइड / देशी चूर्ण (स्टिरॉइड असू शकते)", ["Steroid-induced diabetes"]),
    O("pancreas_alcohol", "Pancreatitis / heavy alcohol", "पैंक्रियाटाइटिस / ज़्यादा शराब", "पॅन्क्रियाटायटिस / जास्त दारू", ["Pancreatic diabetes"])],
  src=f"{EN}, p393")
Q("th_other", "thirst", "associated", 5, "multi", "If sugar is normal — other clues", "अगर शुगर ठीक है — अन्य", "साखर सामान्य असल्यास — इतर", term="Non-diabetic polyuria", opts=[
    O("lithium", "Lithium / mood medicine", "लिथियम / मूड की दवा", "लिथियम / मूडचे औषध", ["Diabetes insipidus"]),
    O("head_injury", "Head injury / brain surgery", "सिर की चोट / दिमाग़ का ऑपरेशन", "डोक्याला इजा / मेंदूची शस्त्रक्रिया", ["Diabetes insipidus"]),
    O("calcium", "Constipation, bone pain, kidney stones", "कब्ज़, हड्डी दर्द, पथरी", "बद्धकोष्ठता, हाडदुखी, मुतखडा", ["Hypercalcaemia"]),
    O("habit", "Habit of drinking lots of water", "बहुत पानी पीने की आदत", "खूप पाणी पिण्याची सवय", ["Psychogenic polydipsia"])],
  src=f"{EN}, p379")

# ---------------------------------------------------------------- DIABETES CHECK-UP  (Box 18.10-18.11)
DR = f"{EN}, p395-396 (Box 18.10-18.11)"
Q("dr_type_duration", "diabetes_review", "hopi", 1, "text", "Since when diabetic and current treatment (tablets / insulin, doses)", "कब से शुगर है और अभी क्या इलाज (गोली / इंसुलिन, मात्रा)?",
  "किती वर्षांपासून मधुमेह आणि सध्याचा उपचार (गोळ्या / इन्सुलिन, मात्रा)?", term="Duration and treatment", src=DR)
Q("dr_adherence", "diabetes_review", "hopi", 2, "choice", "Taking medicines regularly?", "क्या दवा नियमित लेते हैं?", "औषध नियमित घेता का?", term="Adherence", key="adherence", opts=[
    O("regular", "Yes, regularly", "हाँ, नियमित", "हो, नियमित"),
    O("miss", "Sometimes miss", "कभी-कभी छूट जाती", "कधी कधी चुकते", ["Poor glycaemic control"]),
    O("stopped", "Stopped / only when sugar high", "बंद कर दी / सिर्फ़ शुगर बढ़ने पर", "बंद केले / फक्त साखर वाढल्यावर", ["Poor glycaemic control"]),
    O("cost", "Can't afford / medicine finished", "पैसे नहीं / दवा ख़त्म", "पैसे नाहीत / औषध संपले", ["Poor glycaemic control"])],
  src=DR)
Q("dr_sugar", "diabetes_review", "hopi", 3, "text", "Recent sugar readings / HbA1c (if known)", "हाल की शुगर रीडिंग / HbA1c (अगर पता हो)", "अलीकडील साखर रीडिंग / HbA1c (माहीत असल्यास)",
  term="Recent glucose / HbA1c", src=DR)
Q("dr_hypo", "diabetes_review", "redflag", 4, "multi", "Low sugar episodes (sweating, shaking, hunger, confusion)", "शुगर कम होना (पसीना, काँपना, भूख, उलझन)",
  "साखर कमी होणे (घाम, थरथर, भूक, गोंधळ)", term="Hypoglycaemia", opts=[
      O("none", "Never", "कभी नहीं", "कधीच नाही"),
      O("mild", "Sometimes, managed with sugar", "कभी-कभी, चीनी लेकर ठीक", "कधी कधी, साखर घेऊन बरे", ["Hypoglycaemia"]),
      O("severe", "Fainted / needed someone's help", "बेहोश हुए / किसी की मदद लगी", "बेशुद्ध झाले / कोणाची मदत लागली", ["Severe hypoglycaemia"]),
      O("unaware", "No warning before low sugar", "कम होने से पहले कोई चेतावनी नहीं", "कमी होण्याआधी पूर्वसूचना नाही", ["Hypoglycaemia unawareness"])],
  src=f"{EN}, p396")
Q("dr_complications", "diabetes_review", "hopi", 5, "multi", "Complications check", "शुगर से होने वाली तकलीफ़ें", "मधुमेहाच्या गुंतागुंती", term="Chronic complications (Box 18.10)", opts=[
    O("eyes", "Vision reduced / last eye check >1 year", "नज़र कम / आँख की जाँच 1 साल से ज़्यादा पहले", "दृष्टी कमी / डोळे तपासणी 1 वर्षाहून आधी", ["Diabetic retinopathy"]),
    O("feet_numb", "Burning / numb feet", "पैरों में जलन / सुन्नपन", "पायांत जळजळ / बधिरपणा", ["Peripheral neuropathy (diabetes / B12 / alcohol)"]),
    O("feet_wound", "Wound / corn / colour change on foot", "पैर पर घाव / गट्टा / रंग बदलना", "पायावर जखम / घट्टा / रंग बदल", ["Diabetic foot"]),
    O("kidney", "Swelling / frothy urine / told kidney weak", "सूजन / झागदार पेशाब / किडनी कमज़ोर बताया", "सूज / फेसाळ लघवी / मूत्रपिंड कमजोर सांगितले", ["Diabetic nephropathy"]),
    O("heart", "Chest pain / breathless on walking", "चलने पर सीने में दर्द / साँस फूलना", "चालताना छातीत दुखणे / धाप", ["Angina / ACS"]),
    O("calf", "Calf pain on walking", "चलने पर पिंडली दर्द", "चालताना पोटरी दुखणे", ["Peripheral arterial disease"]),
    O("autonomic", "Dizzy on standing / vomiting after meals / diarrhoea at night / erection problem", "खड़े होने पर चक्कर / खाने के बाद उल्टी / रात को दस्त / तनाव की कमी", "उभे राहिल्यावर चक्कर / जेवणानंतर उलटी / रात्री जुलाब / ताठरता कमी", ["Autonomic neuropathy"])],
  src=DR)
Q("dr_foot_urgent", "diabetes_review", "redflag", 6, "yesno", "Foot wound that is red, swollen, smelly, black, or with fever?", "क्या पैर का घाव लाल, सूजा, बदबूदार, काला या बुखार के साथ?",
  "पायाची जखम लाल, सुजलेली, दुर्गंधीयुक्त, काळी किंवा तापासोबत?", term="Infected / ischaemic diabetic foot", rf="Diabetic foot infection / gangrene — URGENT (limb risk)",
  ddx=["Diabetic foot"], src=f"{EN}, p395 (Fig 18.18)")
Q("dr_sick_day", "diabetes_review", "redflag", 7, "yesno", "Currently ill (vomiting/fever/not eating) and still taking insulin/sugar tablets or stopped them?",
  "क्या अभी बीमार (उल्टी/बुखार/खाना नहीं) और इंसुलिन/गोली ले रहे या बंद कर दी?", "सध्या आजारी (उलटी/ताप/जेवण नाही) आणि इन्सुलिन/गोळी घेत आहात किंवा बंद केली?",
  term="Sick-day risk", rf="Diabetic who is unwell — risk of DKA / hypoglycaemia, check sugar & ketones", ddx=["Diabetic ketoacidosis", "Hypoglycaemia"], src=f"{EN}, p393-396")
Q("dr_lifestyle", "diabetes_review", "risk", 8, "multi", "Lifestyle", "रहन-सहन", "जीवनशैली", term="Lifestyle", opts=[
    O("sweets_rice", "Lots of sweets / rice / sweet tea", "बहुत मिठाई / चावल / मीठी चाय", "खूप मिठाई / भात / गोड चहा"),
    O("no_walk", "No daily walk / exercise", "रोज़ चलना / कसरत नहीं", "रोज चालणे / व्यायाम नाही"),
    O("smoke", "Smoking / tobacco", "धूम्रपान / तंबाकू", "धूम्रपान / तंबाखू"),
    O("no_monitor", "No sugar checking at home", "घर पर शुगर जाँच नहीं", "घरी साखर तपासणी नाही"),
    O("desi", "Takes desi / herbal medicine instead of prescribed", "डॉक्टर की दवा की जगह देसी दवा", "डॉक्टरांच्या औषधाऐवजी देशी औषध")],
  src=f"{EN}, p396 (Box 18.11)")
Q("dr_bp_lipid", "diabetes_review", "risk", 9, "multi", "Other conditions", "अन्य बीमारियाँ", "इतर आजार", term="Comorbidities", opts=[
    O("htn", "High BP", "हाई बीपी", "उच्च रक्तदाब"), O("lipid", "High cholesterol", "कोलेस्ट्रॉल ज़्यादा", "कोलेस्टेरॉल जास्त"),
    O("thyroid", "Thyroid", "थायराइड", "थायरॉईड"), O("pregnant", "Pregnant / planning pregnancy", "गर्भवती / गर्भ की योजना", "गर्भवती / गर्भधारणेची योजना", only={"sex": "female"})],
  src=DR)

# ---------------------------------------------------------------- THYROID / NECK SWELLING  (Box 18.1, 18.6)
TY = f"{EN}, p380-382"
Q("ty_swelling", "thyroid", "hopi", 1, "choice", "Neck swelling", "गले में सूजन", "गळ्याला सूज", term="Goitre", opts=[
    O("none", "No swelling", "सूजन नहीं", "सूज नाही"),
    O("diffuse_slow", "Whole front of neck, slowly over years", "गले का पूरा अगला हिस्सा, सालों में धीरे-धीरे", "गळ्याचा पूर्ण पुढचा भाग, वर्षांत हळूहळू", ["Simple / multinodular goitre", "Graves' disease", "Hashimoto's thyroiditis"]),
    O("single_lump", "Single lump", "एक गाँठ", "एक गाठ", ["Thyroid nodule", "Thyroid cancer"]),
    O("painful", "Painful tender swelling after a cold/fever", "सर्दी/बुखार के बाद दर्दनाक सूजन", "सर्दी/तापानंतर दुखरी सूज", ["Subacute thyroiditis"])],
  src=TY)
Q("ty_pressure", "thyroid", "redflag", 2, "yesno", "Difficulty breathing / noisy breathing, hoarse voice, or rapidly growing hard lump?",
  "क्या साँस में तकलीफ़ / आवाज़ वाली साँस, आवाज़ बैठना, या तेज़ी से बढ़ती सख़्त गाँठ?", "श्वासाचा त्रास / आवाजासह श्वास, आवाज बसणे, किंवा वेगाने वाढणारी कडक गाठ?",
  term="Compressive / suspicious goitre", rf="Goitre with airway compression or suspicious lump — urgent", ddx=["Thyroid cancer", "Retrosternal goitre"],
  show={"q": "ty_swelling", "in": ["diffuse_slow", "single_lump"]}, src=f"{EN}, p382")
Q("ty_hyper", "thyroid", "hopi", 3, "multi", "Overactive thyroid signs", "थायराइड ज़्यादा होने के लक्षण", "थायरॉईड जास्त असल्याची लक्षणे", term="Hyperthyroid features (Box 18.1)", opts=[
    O("heat", "Can't tolerate heat, sweating", "गर्मी सहन नहीं, पसीना", "उष्णता सहन होत नाही, घाम", ["Thyrotoxicosis"]),
    O("wt_loss_appetite", "Weight loss with good appetite", "अच्छी भूख के बावजूद वज़न घटना", "चांगल्या भुकेतही वजन घटणे", ["Thyrotoxicosis"]),
    O("palp", "Palpitations", "धड़कन तेज़", "धडधड", ["Thyrotoxicosis"]),
    O("tremor_anxious", "Tremor / anxious / can't sleep", "काँपना / घबराहट / नींद नहीं", "थरथर / अस्वस्थता / झोप नाही", ["Thyrotoxicosis"]),
    O("eyes", "Eyes bulging / gritty / double vision", "आँखें बाहर निकलना / किरकिरी / दोहरा दिखना", "डोळे बाहेर येणे / खुपणे / दोन-दोन दिसणे", ["Graves' disease"]),
    O("loose", "Frequent loose stools", "बार-बार पतला मल", "वारंवार पातळ शौच", ["Thyrotoxicosis"]),
    O("periods_less", "Periods scanty / irregular", "माहवारी कम / अनियमित", "पाळी कमी / अनियमित", ["Thyrotoxicosis"], only={"sex": "female"})],
  src=f"{EN}, p380 (Box 18.1)")
Q("ty_hypo", "thyroid", "hopi", 4, "multi", "Underactive thyroid signs", "थायराइड कम होने के लक्षण", "थायरॉईड कमी असल्याची लक्षणे", term="Hypothyroid features (Box 18.6)", opts=[
    O("cold", "Feels cold more than others", "दूसरों से ज़्यादा ठंड", "इतरांपेक्षा जास्त थंडी", ["Hypothyroidism"]),
    O("wt_gain", "Weight gain", "वज़न बढ़ना", "वजन वाढणे", ["Hypothyroidism"]),
    O("slow", "Slow, sleepy, poor memory", "सुस्ती, नींद, याददाश्त कम", "सुस्ती, झोप, स्मरण कमी", ["Hypothyroidism"]),
    O("skin_hair", "Dry skin, hair fall, eyebrows thinning", "सूखी त्वचा, बाल झड़ना, भौंहें पतली", "कोरडी त्वचा, केस गळणे, भुवया विरळ", ["Hypothyroidism"]),
    O("constipation", "Constipation", "कब्ज़", "बद्धकोष्ठता", ["Hypothyroidism"]),
    O("voice", "Hoarse / deep voice", "आवाज़ भारी", "आवाज जड", ["Hypothyroidism"]),
    O("heavy_periods", "Heavy periods", "ज़्यादा माहवारी", "जास्त पाळी", ["Hypothyroidism"], only={"sex": "female"}),
    O("tingling_cramps", "Tingling hands / muscle cramps", "हाथों में झुनझुनी / ऐंठन", "हातांना मुंग्या / पेटके", ["Hypothyroidism", "Carpal tunnel syndrome"])],
  src=f"{EN}, p380 (Box 18.6)")
Q("ty_storm", "thyroid", "redflag", 5, "yesno", "Very high fever, very fast heartbeat, agitation or confusion?", "क्या बहुत तेज़ बुखार, बहुत तेज़ धड़कन, बेचैनी या उलझन?",
  "खूप तीव्र ताप, खूप जलद ठोके, अस्वस्थता किंवा गोंधळ?", term="Possible thyroid storm", rf="Possible thyroid storm — EMERGENCY", ddx=["Thyroid storm"],
  show={"q": "ty_hyper", "in_any": ["heat", "palp", "tremor_anxious", "wt_loss_appetite"]}, src=f"{EN}, p380")
Q("ty_history", "thyroid", "risk", 6, "multi", "History", "पहले का", "आधीचे", term="Thyroid history", opts=[
    O("on_tablets", "On thyroid tablets (dose?)", "थायराइड की गोली चल रही (कितनी?)", "थायरॉईडची गोळी सुरू (किती?)"),
    O("family", "Thyroid in family", "परिवार में थायराइड", "कुटुंबात थायरॉईड", ["Hashimoto's thyroiditis", "Graves' disease"]),
    O("post_delivery", "Started after delivery", "डिलीवरी के बाद शुरू", "प्रसूतीनंतर सुरू", ["Postpartum thyroiditis"], only={"sex": "female"}),
    O("drugs", "Amiodarone / lithium", "एमियोडेरोन / लिथियम", "अमिओडेरोन / लिथियम", ["Drug-induced thyroid disease"]),
    O("neck_radiation", "Neck radiation / surgery before", "पहले गले पर रेडिएशन / ऑपरेशन", "आधी गळ्यावर रेडिएशन / शस्त्रक्रिया", ["Hypothyroidism", "Thyroid cancer"]),
    O("salt", "Uses non-iodised salt", "बिना आयोडीन वाला नमक", "आयोडीनशिवाय मीठ", ["Simple / multinodular goitre"])],
  src=TY)

# ---------------------------------------------------------------- WEIGHT GAIN  (Box 18.3)
WG = f"{EN}, p379-380 (Box 18.3)"
Q("wg_pattern", "weight_gain", "hopi", 1, "multi", "Type of weight gain", "वज़न कैसे बढ़ा?", "वजन कसे वाढले?", term="Pattern", opts=[
    O("gradual_eating", "Slowly over years, eating more / less activity", "सालों में धीरे-धीरे, ज़्यादा खाना / कम चलना", "वर्षांत हळूहळू, जास्त खाणे / कमी हालचाल", ["Simple obesity"]),
    O("face_belly", "Round face, belly fat but thin arms/legs, purple stretch marks", "गोल चेहरा, पेट मोटा पर हाथ-पैर पतले, बैंगनी धारियाँ", "गोल चेहरा, पोट जाड पण हात-पाय बारीक, जांभळ्या रेषा", ["Cushing's syndrome"]),
    O("swelling", "Swelling of legs / belly (fluid)", "पैर / पेट में सूजन (पानी)", "पाय / पोटाला सूज (पाणी)", ["Heart failure", "Kidney disease", "Chronic liver disease / cirrhosis"]),
    O("rapid", "Rapid gain in weeks", "हफ़्तों में तेज़ी से", "आठवड्यांत वेगाने", ["Fluid retention", "Cushing's syndrome"])],
  src=WG)
Q("wg_hypothyroid", "weight_gain", "associated", 2, "yesno", "Feeling cold, slow, constipated, dry skin?", "क्या ठंड लगना, सुस्ती, कब्ज़, सूखी त्वचा?", "थंडी वाजणे, सुस्ती, बद्धकोष्ठता, कोरडी त्वचा?",
  term="Hypothyroid features", ddx=["Hypothyroidism"], src=f"{EN}, p380 (Box 18.6)")
Q("wg_pcos", "weight_gain", "associated", 3, "yesno", "Irregular periods, facial hair, acne?", "क्या अनियमित माहवारी, चेहरे पर बाल, मुँहासे?", "अनियमित पाळी, चेहऱ्यावर केस, मुरुमे?",
  term="PCOS features", ddx=["Polycystic ovary syndrome"], applies={"sex": "female", "min_age": 12, "max_age": 50}, src="General clinical practice")
Q("wg_drugs", "weight_gain", "risk", 4, "multi", "Medicines", "दवाएँ", "औषधे", term="Drug causes", opts=[
    O("steroid", "Steroids / desi powders", "स्टेरॉयड / देसी चूर्ण", "स्टिरॉइड / देशी चूर्ण", ["Cushing's syndrome (iatrogenic)"]),
    O("psych", "Mental health / fits medicines", "मानसिक रोग / मिर्गी की दवा", "मानसिक आजार / आकडीची औषधे", ["Drug-induced weight gain"]),
    O("insulin", "Insulin / some sugar tablets", "इंसुलिन / कुछ शुगर की गोलियाँ", "इन्सुलिन / काही साखरेच्या गोळ्या", ["Drug-induced weight gain"]),
    O("contraceptive", "Hormone tablets / injection", "हार्मोन की गोली / इंजेक्शन", "हार्मोनची गोळी / इंजेक्शन", ["Drug-induced weight gain"], only={"sex": "female"})],
  src=WG)
Q("wg_osa", "weight_gain", "associated", 5, "yesno", "Loud snoring / daytime sleepiness?", "क्या ज़ोर के खर्राटे / दिन में नींद?", "मोठे घोरणे / दिवसा झोप?", term="OSA symptoms",
  ddx=["Obstructive sleep apnoea"], src=f"{H}, Ch 12, p172")
Q("wg_mood_eat", "weight_gain", "associated", 6, "yesno", "Eating more when stressed / low mood / binge eating?", "क्या तनाव / उदासी में ज़्यादा खाना / एक साथ बहुत खाना?",
  "ताण / उदासीत जास्त खाणे / एकदम खूप खाणे?", term="Emotional eating", ddx=["Depression", "Binge eating"], src="General clinical practice")

# ---------------------------------------------------------------- TIREDNESS / GENERALISED WEAKNESS
FT = f"{EN}, p379-380"
Q("ft_duration", "fatigue", "hopi", 1, "choice", "How long?", "कब से?", "कधीपासून?", term="Duration", opts=[
    O("weeks", "A few weeks (after illness?)", "कुछ हफ़्ते (बीमारी के बाद?)", "काही आठवडे (आजारानंतर?)", ["Post-viral fatigue"]),
    O("months", "Months, slowly worse", "महीनों से, धीरे-धीरे बढ़ती", "महिन्यांपासून, हळूहळू वाढणारी", ["Anaemia", "Hypothyroidism", "Diabetes", "Depression", "Chronic kidney disease"])],
  src=FT)
Q("ft_clues", "fatigue", "associated", 2, "multi", "Any of these?", "इनमें से कुछ?", "यापैकी काही?", term="Clues to cause", opts=[
    O("pale_breathless", "Pale, breathless on walking, heavy periods / black stool", "पीलापन, चलने पर साँस फूलना, ज़्यादा माहवारी / काला मल", "फिकटपणा, चालताना धाप, जास्त पाळी / काळी शौच", ["Anaemia"]),
    O("thirst", "Thirst / passing more urine", "प्यास / ज़्यादा पेशाब", "तहान / जास्त लघवी", ["Diabetes"]),
    O("cold_slow", "Feels cold, slow, weight gain", "ठंड, सुस्ती, वज़न बढ़ना", "थंडी, सुस्ती, वजन वाढ", ["Hypothyroidism"]),
    O("dark_skin_salt", "Skin/gums getting darker, salt craving, dizzy on standing, weight loss", "त्वचा/मसूड़े काले होना, नमक की चाह, खड़े होने पर चक्कर, वज़न घटना", "त्वचा/हिरड्या काळ्या होणे, मिठाची ओढ, उभे राहिल्यावर चक्कर, वजन घटणे", ["Addison's disease"]),
    O("low_mood_sleep", "Low mood, no interest, poor sleep", "उदासी, किसी में मन नहीं, नींद ख़राब", "उदासी, कशातच मन नाही, झोप खराब", ["Depression"]),
    O("fever_wtloss", "Evening fever / weight loss / night sweats", "शाम को बुखार / वज़न घटना / रात को पसीना", "संध्याकाळी ताप / वजन घटणे / रात्री घाम", ["Tuberculosis", "Malignancy", "HIV"]),
    O("snoring", "Loud snoring / sleepy in day", "ज़ोर के खर्राटे / दिन में नींद", "मोठे घोरणे / दिवसा झोप", ["Obstructive sleep apnoea"]),
    O("itch_urine", "Itching / swelling / less urine", "खुजली / सूजन / पेशाब कम", "खाज / सूज / लघवी कमी", ["Chronic kidney disease"]),
    O("jaundice", "Yellow eyes", "आँखें पीली", "डोळे पिवळे", ["Hepatitis"])],
  src=FT)
Q("ft_addisonian", "fatigue", "redflag", 3, "yesno", "Vomiting, very weak, dizzy/fainting — especially if on steroids that were stopped?",
  "क्या उल्टी, बहुत कमज़ोरी, चक्कर/बेहोशी — ख़ासकर अगर स्टेरॉयड अचानक बंद किए?", "उलटी, खूप अशक्तपणा, चक्कर/बेशुद्धी — विशेषतः स्टिरॉइड अचानक बंद केले असल्यास?",
  term="Possible adrenal crisis", rf="Possible adrenal crisis — EMERGENCY (check BP, sugar, sodium)", ddx=["Adrenal crisis"], src=f"{EN}, p379-380 (Box 18.2)")
Q("ft_sleep_work", "fatigue", "risk", 4, "multi", "Life factors", "जीवन से जुड़े कारण", "जीवनाशी संबंधित कारणे", term="Lifestyle contributors", opts=[
    O("night_shift", "Night shifts / poor sleep", "रात की ड्यूटी / नींद कम", "रात्रपाळी / झोप कमी", ["Sleep deprivation"]),
    O("overwork", "Overwork / stress", "ज़्यादा काम / तनाव", "जास्त काम / ताण", ["Stress-related fatigue"]),
    O("poor_diet", "Poor diet / fasting often", "खाना कम / अक्सर उपवास", "आहार कमी / वारंवार उपवास", ["Anaemia", "Malnutrition"]),
    O("alcohol", "Alcohol", "शराब", "दारू", ["Alcohol-related"]),
    O("new_drugs", "New medicines (BP tablets, sleeping pills, antihistamines)", "नई दवा (बीपी, नींद, एलर्जी की गोली)", "नवीन औषध (बीपी, झोप, ॲलर्जीची गोळी)", ["Drug side effect"])],
  src="General clinical practice")
