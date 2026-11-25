# ====================================================================== SYSTEM 8: HAEMATOLOGY (blood)
# Hutchison 24e has no separate blood chapter; sources: Ch 2 (general examination: pallor, lymph nodes, purpura), p19-27;
# Ch 14 Table 14.1 (deficiency syndromes), p244; Ch 10 (fever), Ch 17 Box 17.1. Rest = general clinical practice (marked).
# Executed inside hx_bank.py.

G2 = f"{H}, Ch 2, p19-27"
DEF = f"{H}, Ch 14, p244 (Table 14.1)"
GCP = "General clinical practice"

C("anaemia", "Haematology", "Pale / low haemoglobin", "ख़ून की कमी / पीलापन", "रक्ताची कमतरता / फिकटपणा", "🩸", 81, f"{G2}; {DEF}")
C("bleeding", "Haematology", "Easy bleeding / bruising", "आसानी से ख़ून बहना / नील पड़ना", "सहज रक्तस्राव / काळे-निळे पडणे", "🩹", 82, f"{G2}")
C("lumps_nodes", "Haematology", "Lumps / swollen glands", "गाँठें / गिल्टियाँ", "गाठी / ग्रंथी सुजणे", "🔵", 83, f"{H}, Ch 2, p19-22 (lymph nodes)")
C("infections", "Haematology", "Frequent infections / mouth ulcers", "बार-बार इन्फेक्शन / मुँह में छाले", "वारंवार संसर्ग / तोंडात फोड", "🦠", 84, GCP)

# ---------------------------------------------------------------- ANAEMIA
Q("an_severity", "anaemia", "redflag", 1, "yesno", "Breathless at rest, chest pain, fainting or very fast heartbeat?",
  "क्या आराम में साँस फूलना, सीने में दर्द, बेहोशी या बहुत तेज़ धड़कन?", "विश्रांतीत धाप, छातीत दुखणे, बेशुद्धी किंवा खूप जलद ठोके?",
  term="Symptomatic severe anaemia", rf="Severe symptomatic anaemia — urgent Hb, consider transfusion", ddx=["Severe anaemia"], src=G2)
Q("an_symptoms", "anaemia", "hopi", 2, "multi", "Symptoms", "लक्षण", "लक्षणे", term="Symptoms of anaemia", opts=[
    O("tired", "Tired / weak", "थकान / कमज़ोरी", "थकवा / अशक्तपणा", ["Anaemia"]),
    O("breathless_walk", "Breathless on walking / stairs", "चलने / सीढ़ी पर साँस फूलना", "चालताना / जिना चढताना धाप", ["Anaemia"]),
    O("dizzy", "Dizzy / headache", "चक्कर / सिर दर्द", "चक्कर / डोकेदुखी", ["Anaemia"]),
    O("pica", "Craving to eat mud / chalk / ice / raw rice", "मिट्टी / चॉक / बर्फ़ / कच्चे चावल खाने की इच्छा", "माती / खडू / बर्फ / कच्चे तांदूळ खाण्याची इच्छा", ["Iron deficiency anaemia"]),
    O("mouth", "Sore tongue / cracks at mouth corners", "जीभ में छाले / होंठों के कोने फटना", "जिभेला फोड / ओठांचे कोपरे फाटणे", ["Iron deficiency anaemia", "B12 / folate deficiency"]),
    O("nails_spoon", "Spoon-shaped / brittle nails", "चम्मच जैसे / भुरभुरे नाखून", "चमच्यासारखी / ठिसूळ नखे", ["Iron deficiency anaemia"]),
    O("numb_feet", "Numb / tingling feet, unsteady", "पैर सुन्न / झुनझुनी, लड़खड़ाहट", "पाय बधिर / मुंग्या, डगमग", ["B12 / folate deficiency"])],
  src=DEF)
Q("an_blood_loss", "anaemia", "hopi", 3, "multi", "Possible blood loss", "ख़ून जाने के रास्ते", "रक्त जाण्याचे मार्ग", term="Sources of blood loss", opts=[
    O("heavy_periods", "Heavy / long periods, clots", "ज़्यादा / लंबी माहवारी, थक्के", "जास्त / लांब पाळी, गुठळ्या", ["Iron deficiency anaemia", "Menorrhagia"], only={"sex": "female"}),
    O("black_stool", "Black stool / blood in stool / piles", "काला मल / मल में ख़ून / बवासीर", "काळी शौच / शौचात रक्त / मूळव्याध", ["Iron deficiency anaemia", "GI malignancy", "Peptic ulcer / gastritis"]),
    O("worms", "Worms in stool / walks barefoot", "मल में कीड़े / नंगे पैर चलना", "शौचात जंत / अनवाणी चालणे", ["Hookworm infestation", "Iron deficiency anaemia"]),
    O("nose_gum", "Nose / gum bleeding", "नाक / मसूड़ों से ख़ून", "नाक / हिरड्यांतून रक्त", ["Bleeding disorder"]),
    O("painkillers", "Painkillers / aspirin regularly", "दर्द की गोली / एस्पिरिन नियमित", "वेदनाशामक / ॲस्पिरिन नियमित", ["Peptic ulcer / gastritis"]),
    O("blood_donor", "Frequent blood donation", "बार-बार ख़ून दान", "वारंवार रक्तदान", ["Iron deficiency anaemia"])],
  src=f"{H}, Ch 14, p242-243; {GCP}")
Q("an_gi_alarm", "anaemia", "redflag", 4, "yesno", "Age over 50 (or man / post-menopausal woman) with anaemia and weight loss or change in bowel habit?",
  "क्या 50 से ज़्यादा उम्र (या पुरुष / माहवारी बंद महिला) में ख़ून की कमी, वज़न घटना या पाखाने में बदलाव?",
  "50 पेक्षा जास्त वय (किंवा पुरुष / रजोनिवृत्त महिला) रक्ताची कमतरता, वजन घटणे किंवा शौचात बदल?",
  term="Iron deficiency with GI alarm features", rf="Unexplained iron-deficiency in man/older woman — exclude GI cancer (endoscopy)", ddx=["GI malignancy"],
  applies={"min_age": 40}, src=f"{H}, Ch 14, p242")
Q("an_diet", "anaemia", "risk", 5, "multi", "Diet", "खाना", "आहार", term="Nutritional factors", opts=[
    O("veg_strict", "Strict vegetarian (no milk/eggs)", "शुद्ध शाकाहारी (दूध/अंडा नहीं)", "पूर्ण शाकाहारी (दूध/अंडी नाही)", ["B12 / folate deficiency", "Iron deficiency anaemia"]),
    O("tea_meals", "Tea with / right after meals", "खाने के साथ / तुरंत बाद चाय", "जेवणासोबत / लगेच चहा", ["Iron deficiency anaemia"]),
    O("poor_food", "Little green vegetables / pulses / fruit", "हरी सब्ज़ी / दाल / फल कम", "हिरव्या भाज्या / डाळ / फळे कमी", ["Iron deficiency anaemia", "B12 / folate deficiency"]),
    O("alcohol", "Heavy alcohol", "ज़्यादा शराब", "जास्त दारू", ["B12 / folate deficiency"]),
    O("acidity_tabs", "Acidity tablets / metformin for years", "सालों से एसिडिटी की गोली / मेटफ़ॉर्मिन", "वर्षानुवर्षे ॲसिडिटीची गोळी / मेटफॉर्मिन", ["B12 / folate deficiency"])],
  src=DEF)
Q("an_haemolysis", "anaemia", "associated", 6, "multi", "Breakdown of blood (haemolysis) clues", "ख़ून टूटने के निशान", "रक्त तुटण्याची चिन्हे", term="Haemolytic features", opts=[
    O("jaundice", "Yellow eyes (with normal urine)", "आँखें पीली (पेशाब सामान्य)", "डोळे पिवळे (लघवी सामान्य)", ["Haemolysis"]),
    O("dark_urine_drug", "Dark / red urine after a new medicine, fava beans or fever", "नई दवा, बाकला या बुखार के बाद गहरा / लाल पेशाब", "नवीन औषध, पावटा किंवा तापानंतर गडद / लाल लघवी", ["G6PD deficiency", "Haemolysis"]),
    O("gallstones_young", "Gallstones at young age", "कम उम्र में पित्त की पथरी", "कमी वयात पित्ताशयाचे खडे", ["Haemolysis"]),
    O("malaria", "Recent malaria / fever with chills", "हाल में मलेरिया / कँपकँपी वाला बुखार", "अलीकडे मलेरिया / थंडी वाजून ताप", ["Malaria"])],
  src=f"{H}, Ch 14, p243; {G2}")
Q("an_inherited", "anaemia", "risk", 7, "multi", "Family / inherited", "परिवार / जन्म से", "कुटुंब / जन्मापासून", term="Inherited haemoglobin disorders", opts=[
    O("thal", "Thalassaemia / regular transfusions in family", "परिवार में थैलेसीमिया / नियमित ख़ून चढ़ना", "कुटुंबात थॅलेसेमिया / नियमित रक्त चढवणे", ["Thalassaemia trait / major"]),
    O("sickle", "Sickle cell (incl. tribal community history)", "सिकल सेल (आदिवासी समुदाय भी)", "सिकल सेल (आदिवासी समाजसुद्धा)", ["Sickle cell disease"]),
    O("lifelong", "Low Hb since childhood, iron didn't help", "बचपन से Hb कम, आयरन से फ़ायदा नहीं", "लहानपणापासून Hb कमी, आयर्नने फायदा नाही", ["Thalassaemia trait / major"]),
    O("consanguineous", "Parents related (same family marriage)", "माता-पिता रिश्तेदार (परिवार में शादी)", "आई-वडील नातेवाईक (कुटुंबात लग्न)", ["Thalassaemia trait / major", "Sickle cell disease"])],
  src=GCP + " (India)")
Q("an_chronic", "anaemia", "risk", 8, "multi", "Other conditions", "अन्य बीमारियाँ", "इतर आजार", term="Anaemia of chronic disease", opts=[
    O("ckd", "Kidney disease", "किडनी रोग", "मूत्रपिंड आजार", ["Chronic kidney disease"]),
    O("tb_ra", "TB / rheumatoid arthritis / long infection", "टीबी / आर्थराइटिस / पुराना इन्फेक्शन", "टीबी / संधिवात / जुना संसर्ग", ["Anaemia of chronic disease"]),
    O("pregnant", "Pregnant / recent delivery / breastfeeding", "गर्भवती / हाल में डिलीवरी / स्तनपान", "गर्भवती / अलीकडे प्रसूती / स्तनपान", ["Iron deficiency anaemia"], only={"sex": "female"}),
    O("bone_pain_fever", "Bone pain / fevers / weight loss", "हड्डी दर्द / बुखार / वज़न घटना", "हाडदुखी / ताप / वजन घटणे", ["Haematological malignancy"])],
  src=GCP)

# ---------------------------------------------------------------- EASY BLEEDING / BRUISING
BL = f"{G2} (purpura, petechiae)"
Q("bl_type", "bleeding", "hopi", 1, "multi", "What kind of bleeding?", "कैसे ख़ून बहता है?", "रक्तस्राव कसा होतो?", term="Bleeding pattern", opts=[
    O("pinpoint", "Tiny red dots on skin (don't fade on pressing)", "त्वचा पर छोटे लाल बिंदु (दबाने पर नहीं मिटते)", "त्वचेवर लहान लाल ठिपके (दाबल्यावर जात नाहीत)", ["Low platelets (ITP / dengue / leukaemia)"]),
    O("bruises", "Big bruises without injury", "बिना चोट बड़े नील", "इजा न होता मोठे काळे-निळे डाग", ["Bleeding disorder", "Low platelets (ITP / dengue / leukaemia)"]),
    O("gums_nose", "Gum / nose bleeds", "मसूड़ों / नाक से ख़ून", "हिरड्या / नाकातून रक्त", ["Low platelets (ITP / dengue / leukaemia)", "Bleeding disorder"]),
    O("prolonged", "Long bleeding after tooth removal / cut / operation", "दाँत निकालने / कटने / ऑपरेशन के बाद देर तक ख़ून", "दात काढल्यावर / कापल्यावर / ऑपरेशननंतर बराच वेळ रक्त", ["Bleeding disorder"]),
    O("joints", "Swollen painful joints after small injury", "मामूली चोट के बाद जोड़ सूजकर दर्द", "किरकोळ इजेनंतर सांधे सुजून दुखणे", ["Haemophilia"]),
    O("heavy_periods", "Heavy periods since first period", "पहली माहवारी से ही ज़्यादा माहवारी", "पहिल्या पाळीपासूनच जास्त पाळी", ["Bleeding disorder"], only={"sex": "female"})],
  src=BL)
Q("bl_fever", "bleeding", "redflag", 2, "yesno", "Bleeding / red spots WITH fever, or very pale and tired?", "क्या बुखार के साथ ख़ून / लाल दाने, या बहुत पीलापन और थकान?",
  "तापासोबत रक्तस्राव / लाल ठिपके, किंवा खूप फिकटपणा व थकवा?", term="Bleeding with fever / pancytopenia features",
  rf="Bleeding with fever — dengue / sepsis / leukaemia, urgent platelet count", ddx=["Dengue", "Low platelets (ITP / dengue / leukaemia)", "Leukaemia", "Sepsis"], src=f"{H}, Ch 10, p146")
Q("bl_serious", "bleeding", "redflag", 3, "multi", "Serious bleeding", "गंभीर ख़ून बहना", "गंभीर रक्तस्राव", term="Major bleeding sites", opts=[
    O("black_stool_vomit", "Black stool / blood vomit", "काला मल / ख़ून की उल्टी", "काळी शौच / रक्ताची उलटी", ["Major GI haemorrhage"]),
    O("head", "Severe headache / head injury", "तेज़ सिर दर्द / सिर की चोट", "तीव्र डोकेदुखी / डोक्याला इजा", ["Intracranial haemorrhage"]),
    O("urine", "Blood in urine", "पेशाब में ख़ून", "लघवीत रक्त", ["Anticoagulant-related bleeding"]),
    O("nonstop", "Bleeding that won't stop", "रुक न रहा ख़ून", "न थांबणारा रक्तस्राव", ["Bleeding disorder"])],
  src=BL)
Q("bl_drugs", "bleeding", "risk", 4, "multi", "Medicines", "दवाएँ", "औषधे", term="Drugs affecting bleeding", opts=[
    O("warfarin", "Warfarin / acitrom / other blood thinners", "वारफ़ेरिन / एसिट्रोम / ख़ून पतला करने की दवा", "वॉरफेरिन / ॲसिट्रॉम / रक्त पातळ करणारी औषधे", ["Anticoagulant-related bleeding"]),
    O("antiplatelet", "Aspirin / clopidogrel", "एस्पिरिन / क्लोपिडोग्रेल", "ॲस्पिरिन / क्लोपिडोग्रेल", ["Anticoagulant-related bleeding"]),
    O("nsaid", "Painkillers", "दर्द की गोली", "वेदनाशामक", ["Anticoagulant-related bleeding"]),
    O("steroid", "Steroids (thin skin bruises)", "स्टेरॉयड (पतली त्वचा पर नील)", "स्टिरॉइड (पातळ त्वचेवर काळे-निळे)", ["Steroid-related skin fragility"]),
    O("new_drug", "New medicine in last weeks", "पिछले हफ़्तों में नई दवा", "मागील आठवड्यांत नवीन औषध", ["Drug-induced thrombocytopenia"])],
  src=GCP)
Q("bl_family", "bleeding", "risk", 5, "yesno", "Bleeding problem in family (esp. maternal uncles / brothers)?", "क्या परिवार में ख़ून बहने की बीमारी (ख़ासकर मामा / भाई)?",
  "कुटुंबात रक्तस्रावाचा आजार (विशेषतः मामा / भाऊ)?", term="Family history of bleeding disorder", ddx=["Haemophilia", "Bleeding disorder"], src=GCP)
Q("bl_liver", "bleeding", "associated", 6, "yesno", "Liver disease / heavy alcohol / yellow eyes?", "क्या लिवर रोग / ज़्यादा शराब / आँखें पीली?", "यकृत आजार / जास्त दारू / डोळे पिवळे?",
  term="Liver disease (coagulopathy)", ddx=["Chronic liver disease / cirrhosis"], src=f"{H}, Ch 14, p245")
Q("bl_clots", "bleeding", "risk", 7, "yesno", "Blood clot in leg / lung before, or miscarriages (3 or more)?", "क्या पहले पैर / फेफड़े में थक्का, या 3 या ज़्यादा गर्भपात?",
  "आधी पायात / फुफ्फुसात गुठळी, किंवा 3 किंवा जास्त गर्भपात?", term="Thrombotic history", ddx=["Thrombophilia / antiphospholipid syndrome"], src=GCP)

# ---------------------------------------------------------------- LUMPS / SWOLLEN GLANDS  (Ch 2 lymph nodes)
LN = f"{H}, Ch 2, p19-22"
Q("ln_site", "lumps_nodes", "hopi", 1, "multi", "Where?", "कहाँ?", "कुठे?", term="Site", opts=[
    O("neck", "Neck", "गर्दन", "मान", ["Reactive lymphadenopathy", "TB lymphadenitis", "Lymphoma"]),
    O("above_collarbone", "Just above the collarbone", "हँसली की हड्डी के ठीक ऊपर", "गळपट्टीच्या हाडाच्या अगदी वर", ["Malignancy (metastatic)", "Lymphoma", "TB lymphadenitis"]),
    O("armpit", "Armpit", "बगल", "काख", ["Reactive lymphadenopathy", "Breast cancer", "Lymphoma"]),
    O("groin", "Groin", "जांघ", "जांघ", ["Reactive lymphadenopathy", "STI", "Filariasis"]),
    O("many", "Many places", "कई जगह", "अनेक ठिकाणी", ["Lymphoma", "HIV", "Leukaemia", "TB lymphadenitis"]),
    O("breast", "Breast lump", "स्तन में गाँठ", "स्तनात गाठ", ["Breast cancer", "Fibroadenoma"]),
    O("skin_lump", "Lump under the skin (not gland)", "त्वचा के नीचे गाँठ (गिल्टी नहीं)", "त्वचेखाली गाठ (ग्रंथी नाही)", ["Lipoma / sebaceous cyst"])],
  src=LN)
Q("ln_character", "lumps_nodes", "hopi", 2, "multi", "What is it like?", "गाँठ कैसी है?", "गाठ कशी आहे?", term="Character", opts=[
    O("painful_recent", "Painful, came with sore throat / infection", "दर्दनाक, गला ख़राब / इन्फेक्शन के साथ आई", "दुखरी, घसा खवखव / संसर्गासोबत आली", ["Reactive lymphadenopathy"]),
    O("painless_hard", "Painless, hard, growing", "बिना दर्द, सख़्त, बढ़ती हुई", "न दुखणारी, कडक, वाढणारी", ["Malignancy (metastatic)", "Lymphoma"]),
    O("matted_pus", "Several stuck together / pus discharge", "कई आपस में चिपकी / मवाद निकलना", "अनेक एकमेकांना चिकटलेल्या / पू येणे", ["TB lymphadenitis"]),
    O("rubbery", "Rubbery, painless, several", "रबर जैसी, बिना दर्द, कई", "रबरासारख्या, न दुखणाऱ्या, अनेक", ["Lymphoma"]),
    O("soft_moves", "Soft, moves easily, years old", "नरम, आसानी से हिलती, सालों पुरानी", "मऊ, सहज हलणारी, वर्षानुवर्षे जुनी", ["Lipoma / sebaceous cyst"])],
  src=LN)
Q("ln_duration", "lumps_nodes", "hopi", 3, "choice", "How long?", "कब से?", "कधीपासून?", term="Duration", opts=[
    O("lt2w", "Less than 2 weeks", "2 हफ़्ते से कम", "2 आठवड्यांपेक्षा कमी", ["Reactive lymphadenopathy"]),
    O("2to6w", "2–6 weeks", "2 से 6 हफ़्ते", "2 ते 6 आठवडे", ["TB lymphadenitis", "Lymphoma"]),
    O("gt6w", "More than 6 weeks / growing", "6 हफ़्ते से ज़्यादा / बढ़ रही", "6 आठवड्यांपेक्षा जास्त / वाढते", ["TB lymphadenitis", "Lymphoma", "Malignancy (metastatic)"])],
  src=LN)
Q("ln_b_symptoms", "lumps_nodes", "redflag", 4, "yesno", "Fever, drenching night sweats or weight loss along with the lumps?", "क्या गाँठों के साथ बुखार, रात को भीगने वाला पसीना या वज़न घटना?",
  "गाठींसोबत ताप, रात्री भिजवणारा घाम किंवा वजन घटणे?", term="B symptoms", rf="Lymph nodes with B symptoms — TB / lymphoma, biopsy needed",
  ddx=["Lymphoma", "TB lymphadenitis", "HIV"], key="wt_loss", src=f"{H}, Ch 10, p146")
Q("ln_breast_flag", "lumps_nodes", "redflag", 5, "yesno", "Breast lump that is hard / fixed, or nipple discharge / skin dimpling?", "क्या स्तन की गाँठ सख़्त / चिपकी, या निप्पल से स्राव / त्वचा में गड्ढा?",
  "स्तनातील गाठ कडक / चिकटलेली, किंवा स्तनाग्रातून स्राव / त्वचेत खड्डा?", term="Suspicious breast lump", rf="Suspicious breast lump — urgent triple assessment",
  ddx=["Breast cancer"], show={"q": "ln_site", "has": "breast"}, src=f"{H}, Ch 2, p20")
Q("ln_assoc", "lumps_nodes", "associated", 6, "multi", "Other clues", "अन्य", "इतर", term="Associated features", opts=[
    O("left_fullness", "Fullness / lump in upper left belly", "पेट के ऊपर बाईं तरफ भारीपन / गाँठ", "पोटाच्या वर डावीकडे जडपणा / गाठ", ["Splenomegaly"]),
    O("itch", "Itching all over (esp. after bath)", "पूरे शरीर में खुजली (ख़ासकर नहाने के बाद)", "संपूर्ण अंगाला खाज (विशेषतः आंघोळीनंतर)", ["Lymphoma", "Polycythaemia"]),
    O("cough", "Long cough", "लंबी खाँसी", "दीर्घ खोकला", ["Tuberculosis", "Lung cancer"]),
    O("throat_mouth", "Sore throat / mouth or tooth infection / ulcer", "गला ख़राब / मुँह या दाँत का इन्फेक्शन / छाला", "घसा खवखव / तोंड किंवा दाताचा संसर्ग / फोड", ["Reactive lymphadenopathy", "Oral cancer"]),
    O("tobacco", "Chews tobacco / gutka (neck lump)", "तंबाकू / गुटखा खाते हैं (गर्दन की गाँठ)", "तंबाखू / गुटखा खातात (मानेची गाठ)", ["Oral cancer", "Malignancy (metastatic)"]),
    O("hiv_risk", "HIV risk / known HIV", "एचआईवी का ख़तरा / एचआईवी है", "एचआयव्हीचा धोका / एचआयव्ही आहे", ["HIV"])],
  src=LN)

# ---------------------------------------------------------------- FREQUENT INFECTIONS / MOUTH ULCERS
FI = GCP
Q("fi_pattern", "infections", "hopi", 1, "multi", "Which infections?", "कौन-से इन्फेक्शन?", "कोणते संसर्ग?", term="Infection pattern", opts=[
    O("mouth_ulcers", "Repeated mouth ulcers", "बार-बार मुँह में छाले", "वारंवार तोंडात फोड", ["Neutropenia", "Behçet's / aphthous", "Vitamin deficiency"]),
    O("white_mouth", "White patches in mouth (thrush)", "मुँह में सफ़ेद परत", "तोंडात पांढरा थर", ["HIV", "Diabetes", "Steroid / inhaler use"]),
    O("chest", "Repeated pneumonia / chest infections", "बार-बार निमोनिया / छाती का इन्फेक्शन", "वारंवार न्यूमोनिया / छातीचा संसर्ग", ["Immunodeficiency", "Bronchiectasis", "HIV"]),
    O("skin_boils", "Repeated boils / skin infections", "बार-बार फोड़े / त्वचा का इन्फेक्शन", "वारंवार गळू / त्वचेचा संसर्ग", ["Diabetes", "Immunodeficiency"]),
    O("shingles", "Shingles (herpes zoster) at young age", "कम उम्र में हर्पीज़ ज़ोस्टर", "कमी वयात नागीण", ["HIV"]),
    O("diarrhoea", "Long diarrhoea / weight loss", "लंबे दस्त / वज़न घटना", "दीर्घ जुलाब / वजन घटणे", ["HIV", "Malabsorption"])],
  src=FI)
Q("fi_neutropenic", "infections", "redflag", 2, "yesno", "On chemotherapy / cancer treatment and now has fever?", "क्या कीमोथेरेपी / कैंसर का इलाज चल रहा और अब बुखार है?",
  "केमोथेरपी / कर्करोग उपचार सुरू आहे आणि आता ताप आहे?", term="Fever on chemotherapy", rf="Possible neutropenic sepsis — EMERGENCY (antibiotics within 1 hour)",
  ddx=["Neutropenic sepsis"], src=FI)
Q("fi_risk", "infections", "risk", 3, "multi", "Possible causes of low immunity", "रोग-प्रतिरोधक शक्ति कम होने के कारण", "रोगप्रतिकारशक्ती कमी होण्याची कारणे", term="Immunosuppression risk", opts=[
    O("dm", "Diabetes", "शुगर", "मधुमेह", ["Diabetes"]),
    O("steroid_immuno", "Steroids / immune-lowering drugs (e.g. for arthritis, transplant)", "स्टेरॉयड / प्रतिरोधक शक्ति घटाने वाली दवा", "स्टिरॉइड / प्रतिकारशक्ती कमी करणारी औषधे", ["Drug-induced immunosuppression"]),
    O("hiv_risk", "HIV risk (unsafe sex, injections, transfusion)", "एचआईवी का ख़तरा (असुरक्षित संबंध, इंजेक्शन, ख़ून चढ़ा)", "एचआयव्हीचा धोका (असुरक्षित संबंध, इंजेक्शन, रक्त)", ["HIV"]),
    O("malnutrition", "Very thin / poor food", "बहुत दुबला / खाना कम", "खूप कृश / आहार कमी", ["Malnutrition"]),
    O("spleen", "Spleen removed", "तिल्ली निकाली गई", "प्लीहा काढली", ["Post-splenectomy"]),
    O("child_recurrent", "(Child) infections since infancy, poor growth", "(बच्चा) बचपन से इन्फेक्शन, विकास कम", "(मूल) लहानपणापासून संसर्ग, वाढ कमी", ["Primary immunodeficiency"])],
  src=FI)
Q("fi_blood_counts", "infections", "associated", 4, "yesno", "Also pale / easy bruising / bleeding gums?", "क्या साथ में पीलापन / आसानी से नील / मसूड़ों से ख़ून?",
  "सोबत फिकटपणा / सहज काळे-निळे / हिरड्यांतून रक्त?", term="Features of marrow failure", rf="Infections + anaemia + bleeding — possible leukaemia / marrow failure, urgent CBC",
  ddx=["Leukaemia", "Aplastic anaemia"], src=FI)
