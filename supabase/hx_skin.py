# ====================================================================== SYSTEM 9: SKIN, NAILS, HAIR
# Hutchison 24e, Ch 19 (Skin, nails and hair), p403-418; Box 19.3 (dermatological history), 19.7 (alopecia),
# 19.9 (systemic pruritus), 19.11 (drug eruptions). Executed inside hx_bank.py.
# Skin diagnosis needs examination: the app never diagnoses from description alone (photo only with consent).

SK = f"{H}, Ch 19"
SKH = f"{SK}, p403-405 (Box 19.3)"

C("rash", "Skin", "Rash / spots / hives", "दाने / चकत्ते / पित्ती", "पुरळ / चट्टे / पित्त", "🔴", 91, SKH)
C("itching", "Skin", "Itching", "खुजली", "खाज", "🤚", 92, f"{SK}, p412 (Box 19.9)")
C("skin_patch", "Skin", "White / ring-shaped / coloured patches", "सफ़ेद / गोल (दाद) / रंगीन धब्बे", "पांढरे / गोल (गजकर्ण) / रंगीत चट्टे", "⚪", 93, SKH)
C("skin_growth", "Skin", "Mole / growth / non-healing sore", "तिल / गाँठ / न भरने वाला घाव", "तीळ / गाठ / न भरणारी जखम", "🟤", 94, f"{SK}, p415")
C("boil", "Skin", "Boil / painful red swelling", "फोड़ा / लाल दर्दनाक सूजन", "गळू / लाल दुखरी सूज", "🔥", 95, SKH)
C("hair_nail", "Skin", "Hair fall / nail problems", "बाल झड़ना / नाखून की तकलीफ़", "केस गळणे / नखांचा त्रास", "💇", 96, f"{SK}, p408 (Box 19.7), p411")

SKIN_PHOTO = "Clinician should examine the skin; take a photo only with consent."

# ---------------------------------------------------------------- RASH  (Box 19.3)
Q("rs_severe", "rash", "redflag", 1, "multi", "Danger signs with rash", "दानों के साथ ख़तरे के निशान", "पुरळासोबत धोक्याची चिन्हे", term="Rash red flags", opts=[
    O("blisters_peeling", "Blisters / skin peeling off in sheets", "छाले / त्वचा परतों में उतरना", "फोड / त्वचा थरांनी निघणे", ["Stevens-Johnson / TEN"]),
    O("mouth_eyes", "Sores in mouth, eyes or genitals", "मुँह, आँख या गुप्तांग में छाले", "तोंड, डोळे किंवा गुप्तांगात फोड", ["Stevens-Johnson / TEN"]),
    O("swelling_breath", "Lips/face swelling or breathing difficulty", "होंठ/चेहरा सूजना या साँस में तकलीफ़", "ओठ/चेहरा सुजणे किंवा श्वासाचा त्रास", ["Anaphylaxis / angioedema"]),
    O("purple_fever", "Purple spots that don't fade + fever / drowsy", "बैंगनी धब्बे जो दबाने पर नहीं मिटते + बुखार / सुस्ती", "जांभळे डाग जे दाबल्यावर जात नाहीत + ताप / गुंगी", ["Meningococcal sepsis", "Dengue"]),
    O("whole_body_red", "Whole body red and hot", "पूरा शरीर लाल और गर्म", "संपूर्ण अंग लाल व गरम", ["Erythroderma"])],
  src=f"{SK}, p415 (Box 19.11)")
Q("rs_sjs_flag", "rash", "redflag", 2, "yesno", "Any blisters, peeling, mouth/eye sores, face swelling or purple spots with fever?",
  "क्या कोई छाले, त्वचा उतरना, मुँह/आँख में छाले, चेहरे पर सूजन, या बुखार के साथ बैंगनी धब्बे?",
  "कोणतेही फोड, त्वचा निघणे, तोंड/डोळ्यात फोड, चेहऱ्यावर सूज, किंवा तापासोबत जांभळे डाग?",
  term="Dermatological emergency", rf="Severe skin reaction (SJS/TEN, anaphylaxis, purpura) — EMERGENCY, stop new drug",
  ddx=["Stevens-Johnson / TEN", "Anaphylaxis / angioedema", "Meningococcal sepsis"], src=f"{SK}, p415")
Q("rs_course", "rash", "hopi", 3, "choice", "How did it start and change?", "दाने कैसे शुरू हुए और बदले?", "पुरळ कसे सुरू झाले व बदलले?", term="Time course", opts=[
    O("hours_comes_goes", "Raised itchy welts that come and go within hours", "उभरे खुजली वाले चकत्ते जो घंटों में आते-जाते", "उठावदार खाजरे चट्टे जे तासांत येतात-जातात", ["Urticaria"]),
    O("days_fever", "Spread over a few days with fever", "बुखार के साथ कुछ दिनों में फैले", "तापासोबत काही दिवसांत पसरले", ["Viral exanthem", "Measles", "Chickenpox", "Dengue", "Drug reaction"]),
    O("weeks_months", "Weeks / months, slowly spreading", "हफ़्तों / महीनों से धीरे-धीरे फैल रहे", "आठवडे / महिन्यांपासून हळूहळू पसरत", ["Eczema", "Psoriasis", "Tinea (ringworm)", "Scabies"]),
    O("recurrent_same_spot", "Comes back at the same spot each time (after a tablet)", "हर बार उसी जगह लौटते (किसी गोली के बाद)", "प्रत्येक वेळी त्याच जागी परत येतात (गोळीनंतर)", ["Fixed drug eruption"])],
  src=SKH)
Q("rs_distribution", "rash", "hopi", 4, "multi", "Where on the body?", "शरीर में कहाँ?", "शरीरावर कुठे?", term="Distribution", opts=[
    O("web_wrist_genital", "Finger webs, wrists, waist, genitals", "उँगलियों के बीच, कलाई, कमर, गुप्तांग", "बोटांच्या मधे, मनगट, कंबर, गुप्तांग", ["Scabies"]),
    O("folds_groin", "Groin / under breasts / skin folds", "जांघ / स्तन के नीचे / त्वचा की सिलवटें", "जांघ / स्तनाखाली / त्वचेच्या घड्या", ["Tinea (ringworm)", "Candida intertrigo"]),
    O("elbows_knees_scalp", "Elbows, knees, scalp (scaly)", "कोहनी, घुटने, सिर (पपड़ी)", "कोपर, गुडघे, डोके (खपल्या)", ["Psoriasis"]),
    O("flexures_child", "Inside elbows / behind knees (since childhood)", "कोहनी के अंदर / घुटने के पीछे (बचपन से)", "कोपराच्या आत / गुडघ्यामागे (लहानपणापासून)", ["Eczema"]),
    O("sun_exposed", "Only sun-exposed parts (face, arms)", "सिर्फ़ धूप वाले हिस्से (चेहरा, हाथ)", "फक्त उन्हात येणारे भाग (चेहरा, हात)", ["Photosensitivity", "SLE", "Pellagra"]),
    O("one_band", "A band on one side of body (painful)", "शरीर के एक तरफ पट्टी (दर्दनाक)", "शरीराच्या एका बाजूला पट्टा (दुखरा)", ["Herpes zoster"]),
    O("contact_area", "Only where something touched (watch, cream, chappal)", "सिर्फ़ जहाँ कुछ छुआ (घड़ी, क्रीम, चप्पल)", "फक्त जिथे काही स्पर्श झाला (घड्याळ, क्रीम, चप्पल)", ["Contact dermatitis"]),
    O("palms_soles", "Palms and soles", "हथेली और तलवे", "तळहात व तळपाय", ["Secondary syphilis", "Hand-foot-mouth disease", "Erythema multiforme"]),
    O("shins_painful", "Painful red lumps on shins", "पिंडली पर दर्दनाक लाल गाँठें", "नडगीवर दुखऱ्या लाल गाठी", ["Erythema nodosum"])],
  src=f"{SKH}; {SK}, p413 (Box 19.10)")
Q("rs_itch", "rash", "hopi", 5, "choice", "Itchy?", "खुजली होती है?", "खाज येते का?", term="Pruritus", opts=[
    O("severe_night", "Very itchy, worse at night", "बहुत खुजली, रात को ज़्यादा", "खूप खाज, रात्री जास्त", ["Scabies", "Eczema"]),
    O("itchy", "Itchy", "खुजली", "खाज", ["Urticaria", "Tinea (ringworm)", "Eczema", "Contact dermatitis"]),
    O("painful", "Painful / burning rather than itchy", "खुजली नहीं, दर्द / जलन", "खाज नाही, दुखणे / जळजळ", ["Herpes zoster", "Cellulitis", "Stevens-Johnson / TEN"]),
    O("neither", "Neither", "न खुजली न दर्द", "ना खाज ना दुखणे", ["Secondary syphilis", "Pityriasis rosea", "Leprosy"])],
  src=SKH)
Q("rs_contacts", "rash", "risk", 6, "yesno", "Others at home / hostel itching too?", "क्या घर / हॉस्टल में दूसरों को भी खुजली है?", "घरी / वसतिगृहात इतरांनाही खाज आहे का?",
  term="Similar symptoms in contacts", ddx=["Scabies", "Tinea (ringworm)"], src=f"{SKH} (contacts)")
Q("rs_drug", "rash", "risk", 7, "multi", "New medicine in last 8 weeks", "पिछले 8 हफ़्ते में नई दवा", "मागील 8 आठवड्यांत नवीन औषध", term="Drug history (Box 19.11)", opts=[
    O("antibiotic", "Antibiotic (amoxicillin, co-trimoxazole)", "एंटीबायोटिक (एमोक्सिसिलिन, सेप्ट्रान)", "अँटिबायोटिक (अमॉक्सिसिलिन, सेप्ट्रान)", ["Drug reaction", "Stevens-Johnson / TEN"]),
    O("painkiller", "Painkiller", "दर्द की गोली", "वेदनाशामक", ["Drug reaction", "Urticaria", "Stevens-Johnson / TEN"]),
    O("fits_gout", "Fits medicine (carbamazepine, phenytoin) / gout (allopurinol)", "मिर्गी (कार्बामाज़ेपिन, फ़ेनीटोइन) / गाउट (एलोप्यूरिनॉल)", "आकडी (कार्बामाझेपिन, फेनिटॉइन) / गाउट (ॲलोप्युरिनॉल)", ["Stevens-Johnson / TEN", "DRESS"]),
    O("tb_hiv", "TB / HIV medicines", "टीबी / एचआईवी की दवा", "टीबी / एचआयव्ही औषधे", ["Drug reaction", "Stevens-Johnson / TEN"]),
    O("herbal_injection", "Desi / herbal / injection from local doctor", "देसी / जड़ी-बूटी / स्थानीय डॉक्टर का इंजेक्शन", "देशी / जडीबुटी / स्थानिक डॉक्टरांचे इंजेक्शन", ["Drug reaction"])],
  src=f"{SK}, p415 (Box 19.11)")
Q("rs_triggers", "rash", "hopi", 8, "multi", "Triggers", "किससे बढ़ते हैं?", "कशाने वाढते?", term="Provoking factors", opts=[
    O("sun", "Sunlight", "धूप", "ऊन", ["Photosensitivity", "SLE"]),
    O("food", "Certain foods (prawns, eggs, nuts)", "कुछ खाना (झींगा, अंडा, मूँगफली)", "काही अन्न (कोळंबी, अंडी, शेंगदाणे)", ["Urticaria", "Anaphylaxis / angioedema"]),
    O("work_chem", "Cement / detergents / chemicals at work", "सीमेंट / साबुन-डिटर्जेंट / केमिकल", "सिमेंट / डिटर्जंट / रसायने", ["Contact dermatitis"]),
    O("sweat_heat", "Sweat / heat / tight clothes", "पसीना / गर्मी / टाइट कपड़े", "घाम / उष्णता / घट्ट कपडे", ["Tinea (ringworm)", "Miliaria (prickly heat)"]),
    O("stress", "Stress", "तनाव", "ताण", ["Psoriasis", "Eczema", "Urticaria"])],
  src=f"{SKH} (provoking factors)")
Q("rs_steroid_cream", "rash", "risk", 9, "yesno", "Used any cream from chemist (e.g. mixed steroid creams like 'Quadriderm', 'Betnovate', fairness creams)?",
  "क्या केमिस्ट से कोई क्रीम लगाई (जैसे स्टेरॉयड वाली मिक्स क्रीम, गोरा करने की क्रीम)?", "केमिस्टकडून कोणती क्रीम लावली (उदा. स्टिरॉइड मिश्र क्रीम, गोरेपणाची क्रीम)?",
  term="Topical steroid misuse", ddx=["Steroid-modified tinea", "Topical steroid damage"], key="steroid_cream", src=f"{SKH} (previous & current treatment); General clinical practice (India)")
Q("rs_systemic", "rash", "associated", 10, "multi", "Along with rash", "दानों के साथ", "पुरळासोबत", term="Systemic features", opts=[
    O("fever", "Fever", "बुखार", "ताप", ["Viral exanthem", "Dengue", "Measles", "Drug reaction"]),
    O("joint", "Joint pains", "जोड़ों में दर्द", "सांधेदुखी", ["SLE", "Psoriatic arthritis", "Viral arthritis (e.g. chikungunya)"]),
    O("mouth_ulcer_hairfall", "Mouth ulcers / hair fall", "मुँह में छाले / बाल झड़ना", "तोंडात फोड / केस गळणे", ["SLE"]),
    O("cough_coryza", "Cough, runny nose, red eyes (child)", "खाँसी, नाक बहना, आँखें लाल (बच्चा)", "खोकला, नाक वाहणे, डोळे लाल (मूल)", ["Measles"]),
    O("genital_sore", "Genital sore in last months", "पिछले महीनों में गुप्तांग पर घाव", "मागील महिन्यांत गुप्तांगावर जखम", ["Secondary syphilis"])],
  src=SKH)
Q("rs_family", "rash", "risk", 11, "multi", "Family / personal history", "परिवार / पहले", "कुटुंब / आधी", term="Atopy / psoriasis history", key="atopy", opts=[
    O("atopy", "Asthma / allergy / eczema", "दमा / एलर्जी / एक्ज़िमा", "दमा / ॲलर्जी / एक्झिमा", ["Eczema", "Urticaria"]),
    O("psoriasis", "Psoriasis", "सोरायसिस", "सोरायसिस", ["Psoriasis"]),
    O("skin_cancer", "Skin cancer", "त्वचा का कैंसर", "त्वचेचा कर्करोग", ["Skin malignancy"])],
  src=SKH)

# ---------------------------------------------------------------- ITCHING  (Box 19.9)
IT = f"{SK}, p412 (Box 19.9)"
Q("it_rash", "itching", "hopi", 1, "choice", "Is there a rash?", "क्या दाने भी हैं?", "पुरळ पण आहे का?", term="Itch with / without rash", opts=[
    O("rash", "Yes, with rash", "हाँ, दाने हैं", "हो, पुरळ आहे", ["Scabies", "Eczema", "Urticaria", "Tinea (ringworm)"]),
    O("no_rash", "No rash, only scratch marks", "दाने नहीं, सिर्फ़ खुजलाने के निशान", "पुरळ नाही, फक्त खाजवल्याच्या खुणा", ["Systemic pruritus", "Dry skin (xerosis)"])],
  src=IT)
Q("it_scabies", "itching", "hopi", 2, "yesno", "Worse at night, between fingers, others at home itching too?", "क्या रात को ज़्यादा, उँगलियों के बीच, घर में दूसरों को भी?",
  "रात्री जास्त, बोटांच्या मधे, घरी इतरांनाही?", term="Scabies pattern", ddx=["Scabies"], src=SKH)
Q("it_systemic", "itching", "associated", 3, "multi", "Body causes (itch without rash)", "शरीर के अंदर के कारण", "शरीरातील कारणे", term="Systemic causes (Box 19.9)", opts=[
    O("jaundice", "Yellow eyes / dark urine", "आँखें पीली / गहरा पेशाब", "डोळे पिवळे / गडद लघवी", ["Cholestasis", "Obstructive jaundice"]),
    O("kidney", "Kidney disease / swelling / less urine", "किडनी रोग / सूजन / पेशाब कम", "मूत्रपिंड आजार / सूज / लघवी कमी", ["Chronic kidney disease"]),
    O("pale", "Pale / tired (low iron)", "पीलापन / थकान (आयरन कम)", "फिकटपणा / थकवा (आयर्न कमी)", ["Iron deficiency anaemia"]),
    O("thirst", "Thirst / sugar", "प्यास / शुगर", "तहान / साखर", ["Diabetes"]),
    O("thyroid", "Thyroid symptoms", "थायराइड के लक्षण", "थायरॉईडची लक्षणे", ["Thyrotoxicosis", "Hypothyroidism"]),
    O("bath_itch_sweats", "Itch after hot bath / night sweats / lumps", "गरम पानी से नहाने के बाद खुजली / रात को पसीना / गाँठें", "गरम आंघोळीनंतर खाज / रात्री घाम / गाठी", ["Lymphoma", "Polycythaemia"]),
    O("hiv", "HIV / weight loss", "एचआईवी / वज़न घटना", "एचआयव्ही / वजन घटणे", ["HIV"])],
  src=IT)
Q("it_elderly_dry", "itching", "associated", 4, "yesno", "Elderly with dry rough skin, worse in winter / after soap?", "क्या बुज़ुर्ग, रूखी त्वचा, सर्दी में / साबुन के बाद ज़्यादा?",
  "वृद्ध, कोरडी खरखरीत त्वचा, हिवाळ्यात / साबणानंतर जास्त?", term="Xerosis", ddx=["Dry skin (xerosis)"], applies={"min_age": 55}, src=f"{SK}")
Q("it_drugs", "itching", "risk", 5, "yesno", "New medicine / painkiller (opioid) recently?", "क्या हाल में नई दवा / दर्द की तेज़ दवा?", "अलीकडे नवीन औषध / तीव्र वेदनाशामक?",
  term="Drug-induced pruritus", ddx=["Drug reaction"], src=IT)

# ---------------------------------------------------------------- PATCHES (white / ring / coloured)
PT = SKH
Q("pt_type", "skin_patch", "hopi", 1, "choice", "What kind of patch?", "धब्बा कैसा है?", "चट्टा कसा आहे?", term="Patch type", opts=[
    O("milk_white", "Milky-white, no feeling loss (lips, fingers, face)", "दूध जैसा सफ़ेद, सुन्नपन नहीं (होंठ, उँगली, चेहरा)", "दुधासारखा पांढरा, बधिरपणा नाही (ओठ, बोटे, चेहरा)", ["Vitiligo"]),
    O("pale_numb", "Pale / copper patch with LESS feeling / no sweating", "फीका / ताँबे जैसा धब्बा, छूने पर कम महसूस / पसीना नहीं", "फिकट / तांब्यासारखा चट्टा, स्पर्श कमी जाणवतो / घाम नाही", ["Leprosy"]),
    O("ring_itchy", "Ring-shaped, itchy, spreading edge", "गोल छल्ला, खुजली, किनारा फैलता", "गोल कडे, खाज, कडा पसरणारी", ["Tinea (ringworm)"]),
    O("fine_scaly_trunk", "Small pale / brown scaly spots on chest/back", "छाती/पीठ पर छोटे फीके / भूरे पपड़ीदार धब्बे", "छाती/पाठीवर लहान फिकट / तपकिरी खपल्यांचे डाग", ["Pityriasis versicolor"]),
    O("child_face_pale", "Child, pale dry patches on face", "बच्चा, चेहरे पर फीके सूखे धब्बे", "मूल, चेहऱ्यावर फिकट कोरडे डाग", ["Pityriasis alba"]),
    O("dark_neck", "Dark velvety skin on neck / armpits", "गर्दन / बगल में काली मख़मली त्वचा", "मान / काखेत काळी मखमली त्वचा", ["Acanthosis nigricans (insulin resistance)"]),
    O("face_brown", "Brown patches on cheeks (women)", "गालों पर भूरे धब्बे (महिला)", "गालांवर तपकिरी डाग (महिला)", ["Melasma"], only={"sex": "female"})],
  src=PT)
Q("pt_leprosy", "skin_patch", "redflag", 2, "yesno", "Numb patch, thickened nerves, weak hands/feet, or painless wounds?", "क्या सुन्न धब्बा, नस मोटी, हाथ-पैर कमज़ोर, या बिना दर्द घाव?",
  "बधिर चट्टा, मज्जातंतू जाड, हात-पाय कमजोर, किंवा न दुखणाऱ्या जखमा?", term="Leprosy cardinal features", rf="Suspected leprosy — notify / refer for confirmation & MDT",
  ddx=["Leprosy"], src="General clinical practice (India, NLEP)")
Q("pt_tinea_spread", "skin_patch", "hopi", 3, "yesno", "Ringworm spreading despite creams / in family members too?", "क्या क्रीम लगाने के बाद भी दाद फैल रहा / परिवार में भी?",
  "क्रीम लावूनही गजकर्ण पसरत आहे / कुटुंबातही?", term="Recalcitrant tinea", ddx=["Steroid-modified tinea", "Tinea (ringworm)"], show={"q": "pt_type", "in": ["ring_itchy"]}, src="General clinical practice (India)")
Q("pt_steroid_cream", "skin_patch", "risk", 4, "yesno", "Used any cream from chemist (mixed steroid creams, fairness creams)?", "क्या केमिस्ट से कोई क्रीम लगाई (स्टेरॉयड मिक्स / गोरा करने की)?",
  "केमिस्टकडून कोणती क्रीम लावली (स्टिरॉइड मिश्र / गोरेपणाची)?", term="Topical steroid misuse", ddx=["Steroid-modified tinea", "Topical steroid damage"], key="steroid_cream", src="General clinical practice (India)")
Q("pt_autoimmune", "skin_patch", "risk", 5, "multi", "Other conditions", "अन्य बीमारियाँ", "इतर आजार", term="Associated conditions", opts=[
    O("thyroid_dm", "Thyroid / diabetes", "थायराइड / शुगर", "थायरॉईड / मधुमेह", ["Vitiligo", "Acanthosis nigricans (insulin resistance)"]),
    O("family_vitiligo", "White patches in family", "परिवार में सफ़ेद दाग", "कुटुंबात पांढरे डाग", ["Vitiligo"]),
    O("leprosy_contact", "Leprosy patient at home / village", "घर / गाँव में कुष्ठ रोगी", "घरी / गावात कुष्ठरोगी", ["Leprosy"]),
    O("obese", "Overweight", "मोटापा", "लठ्ठपणा", ["Acanthosis nigricans (insulin resistance)"])],
  src=f"{SK}, p403 (vitiligo & autoimmune disease)")

# ---------------------------------------------------------------- MOLE / GROWTH / NON-HEALING SORE
GR = f"{SK}, p415"
Q("gr_type", "skin_growth", "hopi", 1, "choice", "What is it?", "क्या है?", "काय आहे?", term="Lesion type", opts=[
    O("mole_change", "Mole that is changing", "तिल जो बदल रहा है", "तीळ जो बदलतो आहे", ["Melanoma"]),
    O("sore_not_heal", "Sore / ulcer not healing for >4 weeks", "4 हफ़्ते से ज़्यादा न भरने वाला घाव", "4 आठवड्यांहून जास्त न भरणारी जखम", ["Skin malignancy", "Diabetic foot", "Venous ulcer"]),
    O("pearly_face", "Shiny pearly lump on face, bleeds", "चेहरे पर चमकीली गाँठ, ख़ून आता", "चेहऱ्यावर चमकदार गाठ, रक्त येते", ["Basal cell carcinoma"]),
    O("warty", "Warty / rough growth", "मस्से जैसी / खुरदरी गाँठ", "चामखिळीसारखी / खरखरीत गाठ", ["Wart", "Seborrhoeic keratosis", "Squamous cell carcinoma"]),
    O("soft_lump", "Soft movable lump under skin", "त्वचा के नीचे नरम हिलती गाँठ", "त्वचेखाली मऊ हलणारी गाठ", ["Lipoma / sebaceous cyst"]),
    O("leg_ulcer", "Ulcer near ankle with swollen dark leg / varicose veins", "टखने के पास घाव, सूजा काला पैर / नसें फूली", "घोट्याजवळ जखम, सुजलेला काळा पाय / शिरा फुगलेल्या", ["Venous ulcer"]),
    O("pressure", "Sore on back/hips in bed-bound person", "बिस्तर पर पड़े व्यक्ति की पीठ/कूल्हे पर घाव", "अंथरुणाला खिळलेल्या व्यक्तीच्या पाठ/कंबरेवर जखम", ["Pressure ulcer"])],
  src=GR)
Q("gr_abcde", "skin_growth", "redflag", 2, "multi", "Mole warning signs (ABCDE)", "तिल के ख़तरे के निशान", "तीळाची धोक्याची चिन्हे", term="ABCDE features",
  show={"q": "gr_type", "in": ["mole_change"]}, opts=[
      O("asymmetric", "Uneven shape", "आकार टेढ़ा-मेढ़ा", "आकार वेडावाकडा", ["Melanoma"]),
      O("border", "Ragged edge", "किनारे उबड़-खाबड़", "कडा खडबडीत", ["Melanoma"]),
      O("colours", "Several colours", "कई रंग", "अनेक रंग", ["Melanoma"]),
      O("big", "Bigger than a pencil eraser (6 mm)", "पेंसिल रबर से बड़ा (6 मिमी)", "पेन्सिल रबरापेक्षा मोठा (6 मिमी)", ["Melanoma"]),
      O("growing_bleeding", "Growing / itching / bleeding", "बढ़ रहा / खुजली / ख़ून", "वाढतो / खाज / रक्त", ["Melanoma"])],
  src=f"{SK}, p415 (Fig 19.26)")
Q("gr_suspicious", "skin_growth", "redflag", 3, "yesno", "Growing, bleeding, ulcerated or hard lump / non-healing sore (especially in mouth or after tobacco)?",
  "क्या बढ़ती, ख़ून आती, घाव वाली या सख़्त गाँठ / न भरने वाला घाव (ख़ासकर मुँह में या तंबाकू वालों में)?",
  "वाढणारी, रक्त येणारी, जखम झालेली किंवा कडक गाठ / न भरणारी जखम (विशेषतः तोंडात किंवा तंबाखू खाणाऱ्यांत)?",
  term="Suspicious skin/mucosal lesion", rf="Suspicious lesion — biopsy / refer", ddx=["Skin malignancy", "Oral cancer"], src=GR)
Q("gr_risk", "skin_growth", "risk", 4, "multi", "Risk factors", "जोखिम", "जोखीम", term="Skin cancer / ulcer risk", opts=[
    O("sun_outdoor", "Outdoor work in sun for years", "सालों से धूप में काम", "वर्षानुवर्षे उन्हात काम", ["Skin malignancy"]),
    O("burn_scar", "Old burn scar / long-standing wound at that site", "उसी जगह पुराना जलने का निशान / पुराना घाव", "त्याच जागी जुना भाजल्याचा व्रण / जुनी जखम", ["Squamous cell carcinoma (Marjolin)"]),
    O("dm_pvd", "Diabetes / poor circulation", "शुगर / ख़ून का बहाव कम", "मधुमेह / रक्तप्रवाह कमी", ["Diabetic foot", "Peripheral arterial disease"]),
    O("arsenic_water", "Well/handpump water from arsenic area", "आर्सेनिक वाले इलाक़े का कुएँ/हैंडपंप का पानी", "आर्सेनिक भागातील विहीर/हातपंपाचे पाणी", ["Skin malignancy"]),
    O("immuno", "Immune-lowering drugs / HIV", "प्रतिरोधक शक्ति घटाने वाली दवा / एचआईवी", "प्रतिकारशक्ती कमी करणारी औषधे / एचआयव्ही", ["Skin malignancy"])],
  src=GR)

# ---------------------------------------------------------------- BOIL / CELLULITIS
BO = "General clinical practice"
Q("bo_type", "boil", "hopi", 1, "choice", "What is it?", "क्या है?", "काय आहे?", term="Presentation", opts=[
    O("boil_head", "Painful lump with pus head", "मवाद वाली दर्दनाक गाँठ", "पू असलेली दुखरी गाठ", ["Abscess / furuncle"]),
    O("spreading_red", "Spreading red, hot, swollen skin", "फैलती लाल, गर्म, सूजी त्वचा", "पसरणारी लाल, गरम, सुजलेली त्वचा", ["Cellulitis"]),
    O("armpit_groin_recurrent", "Repeated boils in armpits / groin", "बगल / जांघ में बार-बार फोड़े", "काख / जांघेत वारंवार गळू", ["Hidradenitis suppurativa", "Diabetes"]),
    O("after_bite_injury", "After bite / injury / injection", "काटने / चोट / इंजेक्शन के बाद", "चावणे / इजा / इंजेक्शननंतर", ["Cellulitis", "Abscess / furuncle"])],
  src=BO)
Q("bo_severe", "boil", "redflag", 2, "multi", "Danger signs", "ख़तरे के निशान", "धोक्याची चिन्हे", term="Severe soft-tissue infection", opts=[
    O("fever_unwell", "High fever / very unwell / low BP", "तेज़ बुखार / बहुत बीमार / बीपी कम", "तीव्र ताप / खूप आजारी / बीपी कमी", ["Sepsis"]),
    O("pain_out_of_proportion", "Pain much worse than it looks / dark, crackling skin", "जितना दिखता उससे बहुत ज़्यादा दर्द / काली, चरचराती त्वचा", "दिसते त्यापेक्षा खूप जास्त दुखणे / काळी, कुरकुरणारी त्वचा", ["Necrotising fasciitis"]),
    O("face_eye", "Around eye / nose (danger triangle)", "आँख / नाक के आसपास", "डोळा / नाकाभोवती", ["Orbital / facial cellulitis"]),
    O("rapid_spread", "Spreading fast (hours)", "तेज़ी से फैल रहा (घंटों में)", "वेगाने पसरत आहे (तासांत)", ["Necrotising fasciitis", "Cellulitis"])],
  src=BO)
Q("bo_severe_flag", "boil", "redflag", 3, "yesno", "Fever with fast-spreading redness, severe pain, or swelling near the eye?", "क्या बुखार के साथ तेज़ी से फैलती लाली, बहुत दर्द, या आँख के पास सूजन?",
  "तापासोबत वेगाने पसरणारी लाली, खूप दुखणे, किंवा डोळ्याजवळ सूज?", term="Severe soft-tissue infection", rf="Severe skin infection (necrotising / orbital / sepsis) — URGENT",
  ddx=["Necrotising fasciitis", "Orbital / facial cellulitis", "Sepsis"], src=BO)
Q("bo_risk", "boil", "risk", 4, "multi", "Risk factors", "जोखिम", "जोखीम", term="Infection risk factors", opts=[
    O("dm", "Diabetes (or not checked)", "शुगर (या जाँच नहीं हुई)", "मधुमेह (किंवा तपासणी नाही)", ["Diabetes"]),
    O("recurrent_family", "Boils keep coming / family members too", "बार-बार फोड़े / परिवार में भी", "वारंवार गळू / कुटुंबातही", ["Staphylococcal carriage"]),
    O("leg_swelling_tinea", "Leg swelling / cracks between toes", "पैर में सूजन / उँगलियों के बीच दरारें", "पायाला सूज / बोटांमध्ये भेगा", ["Cellulitis"]),
    O("immuno", "Steroids / HIV / chemotherapy", "स्टेरॉयड / एचआईवी / कीमो", "स्टिरॉइड / एचआयव्ही / केमो", ["Sepsis"])],
  src=BO)

# ---------------------------------------------------------------- HAIR FALL / NAILS  (Box 19.7)
HA = f"{SK}, p408 (Box 19.7), p411"
Q("ha_pattern", "hair_nail", "hopi", 1, "choice", "Hair fall pattern", "बाल कैसे झड़ रहे हैं?", "केस कसे गळत आहेत?", term="Pattern of alopecia", opts=[
    O("none", "No hair problem (nail only)", "बालों की तकलीफ़ नहीं (सिर्फ़ नाखून)", "केसांचा त्रास नाही (फक्त नखे)"),
    O("diffuse_after_illness", "Diffuse thinning 2–3 months after fever / delivery / surgery", "बुखार / डिलीवरी / ऑपरेशन के 2–3 महीने बाद पूरे सिर से", "ताप / प्रसूती / ऑपरेशननंतर 2–3 महिन्यांनी संपूर्ण डोक्यातून", ["Telogen effluvium"]),
    O("round_patch", "Round smooth bald patch", "गोल चिकना गंजा धब्बा", "गोल गुळगुळीत टक्कल चट्टा", ["Alopecia areata"]),
    O("scaly_patch_child", "Scaly patch with broken hairs (child)", "पपड़ी वाला धब्बा, टूटे बाल (बच्चा)", "खपल्यांचा चट्टा, तुटलेले केस (मूल)", ["Tinea capitis"]),
    O("crown_temples", "Crown / temples / central parting thinning", "सिर के ऊपर / कनपटी / माँग से पतले", "डोक्याच्या वर / कानशिले / भांगेतून विरळ", ["Androgenetic alopecia"]),
    O("tight_braids", "Along hairline (tight braids / pulling)", "माथे की लाइन पर (कसी चोटी / खींचना)", "कपाळाच्या रेषेवर (घट्ट वेणी / ओढणे)", ["Traction alopecia", "Trichotillomania"]),
    O("scarring", "Shiny scarred bald areas", "चमकदार निशान वाले गंजे हिस्से", "चमकदार व्रणांचे टक्कल भाग", ["Scarring alopecia (discoid lupus etc.)"])],
  src=f"{SK}, p408 (Box 19.7)")
Q("ha_causes", "hair_nail", "associated", 2, "multi", "Body causes", "शरीर के कारण", "शरीरातील कारणे", term="Systemic causes", show={"q": "ha_pattern", "in": ["diffuse_after_illness", "crown_temples"]}, opts=[
    O("iron", "Pale / heavy periods / vegetarian (low iron)", "पीलापन / ज़्यादा माहवारी / शाकाहारी (आयरन कम)", "फिकटपणा / जास्त पाळी / शाकाहारी (आयर्न कमी)", ["Iron deficiency anaemia"]),
    O("thyroid", "Thyroid symptoms", "थायराइड के लक्षण", "थायरॉईडची लक्षणे", ["Hypothyroidism", "Thyrotoxicosis"]),
    O("pcos", "Irregular periods, acne, facial hair", "अनियमित माहवारी, मुँहासे, चेहरे पर बाल", "अनियमित पाळी, मुरुमे, चेहऱ्यावर केस", ["Polycystic ovary syndrome"], only={"sex": "female"}),
    O("crash_diet", "Crash diet / weight loss", "तेज़ डाइटिंग / वज़न घटना", "कडक डाएट / वजन घटणे", ["Telogen effluvium"]),
    O("drugs", "Chemo / blood thinner / acne tablets", "कीमो / ख़ून पतला करने की / मुँहासे की गोली", "केमो / रक्त पातळ करणारी / मुरुमांची गोळी", ["Drug-induced alopecia"])],
  src=f"{SK}, p408 (Box 19.7)")
Q("ha_nails", "hair_nail", "hopi", 3, "multi", "Nail changes", "नाखूनों में बदलाव", "नखांमध्ये बदल", term="Nail signs", opts=[
    O("pits", "Small pits / lifting from bed", "छोटे गड्ढे / नाखून उठना", "लहान खड्डे / नख उचलणे", ["Psoriasis"]),
    O("thick_yellow", "Thick, yellow, crumbly (toenails)", "मोटे, पीले, भुरभुरे (पैर के नाखून)", "जाड, पिवळी, भुसभुशीत (पायाची नखे)", ["Onychomycosis (fungal)"]),
    O("spoon", "Spoon-shaped", "चम्मच जैसे", "चमच्यासारखी", ["Iron deficiency anaemia"]),
    O("clubbing", "Fingertips swollen, nails curved (clubbing)", "उँगलियों के सिरे मोटे, नाखून मुड़े", "बोटांची टोके जाड, नखे वाकलेली", ["Lung disease / cancer", "Cyanotic heart disease", "Chronic liver disease / cirrhosis"]),
    O("swollen_fold", "Red painful swelling around nail", "नाखून के आसपास लाल दर्दनाक सूजन", "नखाभोवती लाल दुखरी सूज", ["Paronychia"]),
    O("dark_streak", "New dark streak in one nail", "एक नाखून में नई काली लकीर", "एका नखात नवीन काळी रेषा", ["Melanoma (subungual)"])],
  src=f"{SK}, p411 (Box 19.8)")
