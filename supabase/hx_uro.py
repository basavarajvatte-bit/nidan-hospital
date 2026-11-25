# ====================================================================== SYSTEM 5: RENAL + UROGENITAL
# Hutchison 24e, Ch 17 (Urogenital system), p355-360, p369 (Box 17.1, 17.4). Executed inside hx_bank.py.

UR = f"{H}, Ch 17"

C("haematuria", "Urogenital", "Blood in urine", "पेशाब में खून", "लघवीत रक्त", "🩸", 51, f"{UR}, p356 (Box 17.1)")
C("loin_pain", "Urogenital", "Kidney / side pain (stone)", "कमर के बगल में दर्द (पथरी)", "कमरेच्या बाजूला दुखणे (मुतखडा)", "🪨", 52, f"{UR}, p355")
C("low_urine", "Urogenital", "Less urine / kidney problem", "पेशाब कम / किडनी की तकलीफ़", "लघवी कमी / मूत्रपिंडाचा त्रास", "🫘", 53, f"{UR}, p356-358")
C("incontinence", "Urogenital", "Urine leakage", "पेशाब रिसना / रोक न पाना", "लघवी गळणे / रोखता न येणे", "💦", 54, f"{UR}, p357")
C("scrotal", "Urogenital", "Testis / scrotal pain or swelling", "अंडकोष में दर्द / सूजन", "अंडकोषात दुखणे / सूज", "♂️", 55, f"{UR}, p369 (Box 17.4)")
C("sti", "Urogenital", "Genital discharge / sores (sexual health)", "गुप्तांग से स्राव / छाले", "गुप्तांगातून स्राव / फोड", "🔒", 56, f"{UR}, p369 (Box 17.4)")

# ---------------------------------------------------------------- URINARY (refined LUTS)
LU = f"{UR}, p355-357"
Q("ur_luts", "urinary", "hopi", 8, "multi", "Passing urine — any of these?", "पेशाब करते समय इनमें से कुछ?", "लघवी करताना यापैकी काही?", term="Lower urinary tract symptoms", opts=[
    O("urgency", "Sudden urge, can't wait", "अचानक ज़ोर, रुक नहीं सकते", "अचानक जोर, थांबता येत नाही", ["Overactive bladder", "Cystitis / UTI"]),
    O("hesitancy", "Delay before urine starts", "पेशाब शुरू होने में देर", "लघवी सुरू व्हायला वेळ", ["Prostate enlargement", "Urethral stricture"]),
    O("incomplete", "Bladder doesn't feel empty after", "बाद में भी पूरा ख़ाली नहीं लगता", "नंतरही पूर्ण रिकामे वाटत नाही", ["Prostate enlargement"]),
    O("dribble", "Dribbling at the end", "आख़िर में बूँद-बूँद", "शेवटी थेंब-थेंब", ["Prostate enlargement"]),
    O("split_stream", "Thin / split stream", "पतली / दो धार", "बारीक / दोन धारा", ["Urethral stricture"])],
  src=LU)
Q("ur_nocturia_n", "urinary", "hopi", 9, "number", "How many times do you get up at night to pass urine?", "रात में पेशाब के लिए कितनी बार उठते हैं?",
  "रात्री लघवीसाठी किती वेळा उठता?", term="Nocturia (times/night)", show={"q": "ur_symptoms", "has": "night"}, src=f"{UR}, p356")
Q("ur_uti_risk", "urinary", "risk", 10, "multi", "Risk factors", "इनमें से कुछ?", "यापैकी काही?", term="UTI / complicated UTI risk", opts=[
    O("pregnant", "Pregnant", "गर्भवती", "गर्भवती", ["Cystitis / UTI"]),
    O("dm", "Diabetes", "शुगर", "मधुमेह", ["Cystitis / UTI", "Pyelonephritis"]),
    O("catheter", "Catheter / recent urine-pipe procedure", "कैथेटर / हाल में पेशाब की नली का प्रोसीजर", "कॅथेटर / अलीकडे मूत्रनलिकेची प्रक्रिया", ["Cystitis / UTI"]),
    O("stones", "Kidney stones", "किडनी की पथरी", "मुतखडा", ["Pyelonephritis", "Renal colic / stone"]),
    O("male", "Male with urine infection (always investigate)", "पुरुष को पेशाब का इन्फेक्शन", "पुरुषाला लघवीचा संसर्ग", ["Prostatitis", "Prostate enlargement"]),
    O("menopause", "After menopause", "माहवारी बंद होने के बाद", "रजोनिवृत्तीनंतर", ["Cystitis / UTI"])],
  src=LU)
Q("ur_child_cry", "urinary", "hopi", 11, "yesno", "(Child) Cries while passing urine / fever without other cause?", "(बच्चा) पेशाब करते समय रोता है / बिना कारण बुखार?",
  "(मूल) लघवी करताना रडते / विनाकारण ताप?", term="Paediatric UTI clues", ddx=["Cystitis / UTI"], applies={"max_age": 12}, src=f"{UR}, p355")
Q("ur_prostatitis", "urinary", "associated", 12, "yesno", "(Men) Pain in perineum / back passage with fever?", "(पुरुष) अंडकोष और गुदा के बीच / गुदा में दर्द, बुखार के साथ?",
  "(पुरुष) अंडकोष व गुदद्वाराच्या मध्ये / गुदद्वारात दुखणे, तापासोबत?", term="Perineal / rectal pain", ddx=["Prostatitis"], applies={"sex": "male"}, src=f"{UR}, p355")

# ---------------------------------------------------------------- HAEMATURIA  (Box 17.1)
HU = f"{UR}, p356 (Box 17.1)"
Q("hu_pain", "haematuria", "hopi", 1, "choice", "Pain with the blood?", "खून के साथ दर्द?", "रक्तासोबत दुखणे?", term="Painful vs painless", opts=[
    O("painless", "No pain at all", "कोई दर्द नहीं", "अजिबात दुखत नाही", ["Urothelial tumour", "Renal tumour", "Glomerulonephritis", "Prostate enlargement"]),
    O("loin_groin", "Colicky side pain to groin", "कमर से जांघ तक मरोड़", "कमरेपासून जांघेपर्यंत मुरडा", ["Renal colic / stone"]),
    O("burning", "Burning / frequency", "जलन / बार-बार", "जळजळ / वारंवार", ["Cystitis / UTI"])],
  src=HU)
Q("hu_ca_risk", "haematuria", "redflag", 2, "yesno", "Painless blood in urine, age over 40, smoker / dye or rubber factory work?",
  "क्या बिना दर्द पेशाब में खून, उम्र 40 से ज़्यादा, धूम्रपान / रंग या रबर फैक्ट्री का काम?",
  "दुखण्याशिवाय लघवीत रक्त, वय 40 पेक्षा जास्त, धूम्रपान / रंग किंवा रबर कारखान्यात काम?",
  term="Urothelial cancer risk", rf="Painless haematuria >40 / smoker — cystoscopy & imaging", ddx=["Urothelial tumour"], applies={"min_age": 35}, src=HU)
Q("hu_clots", "haematuria", "redflag", 3, "yesno", "Passing clots or unable to pass urine?", "क्या खून के थक्के आ रहे या पेशाब रुक गया?",
  "रक्ताच्या गुठळ्या येत आहेत का किंवा लघवी अडकली?", term="Clot retention", rf="Clot retention — catheter / urgent urology", ddx=["Clot retention"], src=HU)
Q("hu_timing", "haematuria", "hopi", 4, "choice", "When in the stream is the blood?", "धार के किस हिस्से में खून?", "धारेच्या कोणत्या भागात रक्त?", term="Timing in stream", opts=[
    O("start", "At the start", "शुरू में", "सुरुवातीला", ["Urethral cause"]),
    O("end", "At the end", "आख़िर में", "शेवटी", ["Bladder neck / prostate cause"]),
    O("throughout", "Throughout (whole urine red/cola)", "पूरे समय (पूरा पेशाब लाल/कोला जैसा)", "पूर्ण वेळ (संपूर्ण लघवी लाल/कोलासारखी)", ["Glomerulonephritis", "Renal tumour", "Urothelial tumour"])],
  src="General clinical practice")
Q("hu_gn", "haematuria", "associated", 5, "multi", "Along with blood in urine", "पेशाब में खून के साथ", "लघवीतील रक्तासोबत", term="Nephritic features", opts=[
    O("throat_skin", "Sore throat / skin infection 1–3 weeks before", "1–3 हफ़्ते पहले गला ख़राब / त्वचा का इन्फेक्शन", "1–3 आठवडे आधी घसा खवखव / त्वचेचा संसर्ग", ["Post-infectious glomerulonephritis"]),
    O("face_puffy", "Puffy face / swollen feet", "चेहरा सूजा / पैरों में सूजन", "चेहरा सुजलेला / पायांना सूज", ["Glomerulonephritis"]),
    O("less_urine", "Passing less urine", "पेशाब कम", "लघवी कमी", ["Glomerulonephritis", "Acute kidney injury"]),
    O("rash_joints", "Rash / joint pains / cough with blood", "दाने / जोड़ों में दर्द / खाँसी में खून", "पुरळ / सांधेदुखी / खोकल्यात रक्त", ["Vasculitis", "SLE"]),
    O("high_bp", "New high BP / headache", "नया हाई बीपी / सिर दर्द", "नवीन उच्च रक्तदाब / डोकेदुखी", ["Glomerulonephritis"])],
  src=f"{UR}, p356")
Q("hu_mimics", "haematuria", "hopi", 6, "multi", "Other explanations", "दूसरे कारण", "इतर कारणे", term="Mimics / systemic causes", opts=[
    O("periods", "During periods", "माहवारी के दौरान", "पाळीच्या काळात", ["Menstrual contamination"]),
    O("beetroot_drugs", "Beetroot / rifampicin (TB medicine)", "चुकंदर / रिफ़ैम्पिसिन (टीबी दवा)", "बीट / रिफॅम्पिसिन (टीबी औषध)", ["Discoloured urine (not blood)"]),
    O("exercise", "After heavy exercise / long march", "भारी कसरत / लंबी चाल के बाद", "जड व्यायाम / लांब चालीनंतर", ["Exercise-induced haematuria / myoglobinuria"]),
    O("thinner", "Blood thinners / easy bruising", "खून पतला करने की दवा / आसानी से नील", "रक्त पातळ करण्याचे औषध / सहज काळे-निळे", ["Anticoagulant-related bleeding", "Bleeding disorder"]),
    O("sickle", "Sickle cell", "सिकल सेल", "सिकल सेल", ["Papillary necrosis (sickle)"])],
  src=HU)
Q("hu_tb", "haematuria", "associated", 7, "yesno", "Burning urine for months not cured by antibiotics, evening fever / weight loss?",
  "क्या महीनों से पेशाब में जलन जो एंटीबायोटिक से ठीक नहीं, शाम को बुखार / वज़न घटना?", "महिन्यांपासून लघवीची जळजळ जी अँटिबायोटिकने बरी होत नाही, संध्याकाळी ताप / वजन घटणे?",
  term="Sterile pyuria / constitutional symptoms", ddx=["Genitourinary TB"], src=HU)

# ---------------------------------------------------------------- LOIN PAIN / STONE  (p355)
LP = f"{UR}, p355"
Q("lp_character", "loin_pain", "hopi", 1, "choice", "Type of pain", "दर्द कैसा है?", "दुखणे कसे आहे?", term="Character", opts=[
    O("colic_groin", "Very severe waves, side to groin, can't keep still", "बहुत तेज़ लहरें, कमर से जांघ तक, चैन नहीं", "खूप तीव्र लाटा, कमरेपासून जांघेपर्यंत, स्वस्थ बसवत नाही", ["Renal colic / stone"]),
    O("constant_fever", "Constant ache with fever / shivering", "लगातार दर्द, बुखार / कँपकँपी", "सतत दुखणे, ताप / थंडी", ["Pyelonephritis", "Renal abscess"]),
    O("dull_long", "Dull ache for weeks", "हफ़्तों से हल्का दर्द", "आठवड्यांपासून मंद दुखणे", ["Renal tumour", "Hydronephrosis", "Musculoskeletal"]),
    O("movement", "Worse on movement / bending", "हिलने / झुकने पर बढ़ता", "हालचाल / वाकल्यावर वाढते", ["Musculoskeletal"])],
  src=LP)
Q("lp_obstructed_infected", "loin_pain", "redflag", 2, "yesno", "Stone pain WITH fever and shivering?", "क्या पथरी के दर्द के साथ बुखार और कँपकँपी?",
  "मुतखड्याच्या दुखण्यासोबत ताप आणि थंडी?", term="Infected obstructed kidney", rf="Obstructed infected kidney — EMERGENCY (urosepsis)",
  ddx=["Pyelonephritis", "Urosepsis"], src=LP)
Q("lp_single_kidney", "loin_pain", "redflag", 3, "yesno", "Only one kidney, or no urine at all since pain?", "क्या एक ही किडनी है, या दर्द के बाद से पेशाब बिल्कुल नहीं?",
  "एकच मूत्रपिंड आहे का, किंवा दुखण्यानंतर अजिबात लघवी नाही?", term="Solitary kidney / anuria", rf="Possible complete obstruction — urgent", ddx=["Acute kidney injury"], src=f"{UR}, p356")
Q("lp_assoc", "loin_pain", "associated", 4, "multi", "Along with the pain", "दर्द के साथ", "दुखण्यासोबत", term="Associated symptoms", opts=[
    O("vomit", "Nausea / vomiting", "जी मिचलाना / उल्टी", "मळमळ / उलटी", ["Renal colic / stone"]),
    O("blood_urine", "Blood in urine", "पेशाब में खून", "लघवीत रक्त", ["Renal colic / stone"]),
    O("frequency", "Frequent urge to pass urine", "बार-बार पेशाब की इच्छा", "वारंवार लघवीची इच्छा", ["Renal colic / stone (lower ureter)", "Cystitis / UTI"]),
    O("burning", "Burning urine", "पेशाब में जलन", "लघवीची जळजळ", ["Pyelonephritis"])],
  src=LP)
Q("lp_stone_risk", "loin_pain", "risk", 5, "multi", "Stone risk factors", "पथरी के कारण", "मुतखड्याची कारणे", term="Stone risk factors", opts=[
    O("previous", "Stone before", "पहले पथरी", "आधी मुतखडा", ["Renal colic / stone"]),
    O("low_water", "Drinks little water / hot outdoor work", "कम पानी / धूप में काम", "कमी पाणी / उन्हात काम", ["Renal colic / stone"]),
    O("family", "Family history of stones", "परिवार में पथरी", "कुटुंबात मुतखडा", ["Renal colic / stone"]),
    O("gout", "Gout / high uric acid", "गठिया / यूरिक एसिड ज़्यादा", "गाउट / युरिक ॲसिड जास्त", ["Renal colic / stone"])],
  src="General clinical practice")
Q("lp_female", "loin_pain", "redflag", 6, "yesno", "(Women) Missed period / could be pregnant?", "(महिला) माहवारी रुकी / गर्भ हो सकता है?", "(महिला) पाळी चुकली / गर्भधारणा असू शकते?",
  term="Possible pregnancy", rf="Possible pregnancy with flank/abdominal pain — exclude ectopic", ddx=["Ovarian / ectopic"], key="pregnancy",
  applies={"sex": "female", "min_age": 12, "max_age": 55}, src=f"{H}, Ch 5")

# ---------------------------------------------------------------- LOW URINE / KIDNEY FAILURE  (p356-358)
LK = f"{UR}, p356-358"
Q("lk_amount", "low_urine", "hopi", 1, "choice", "How much urine in 24 hours?", "24 घंटे में कितना पेशाब?", "24 तासांत किती लघवी?", term="Urine output", opts=[
    O("none", "None at all", "बिल्कुल नहीं", "अजिबात नाही", ["Acute kidney injury", "Urinary retention / obstruction"]),
    O("very_little", "Very little (less than 2 glasses)", "बहुत कम (2 गिलास से कम)", "खूप कमी (2 ग्लासपेक्षा कमी)", ["Acute kidney injury", "Dehydration"]),
    O("normal_but_kidney", "Normal amount, but told kidney is weak", "मात्रा ठीक, पर किडनी कमज़ोर बताया", "प्रमाण ठीक, पण मूत्रपिंड कमजोर सांगितले", ["Chronic kidney disease"])],
  src=f"{UR}, p356 (oliguria / anuria)")
Q("lk_retention", "low_urine", "redflag", 2, "yesno", "Full, painful bladder but can't pass urine?", "क्या मूत्राशय भरा, दर्द है, पर पेशाब नहीं निकल रहा?",
  "मूत्राशय भरलेले, दुखते, पण लघवी होत नाही?", term="Acute urinary retention", rf="Acute retention — catheterise", ddx=["Acute urinary retention"], src=f"{UR}, p356")
Q("lk_aki_causes", "low_urine", "hopi", 3, "multi", "In the last days / weeks", "पिछले दिनों / हफ़्तों में", "मागील दिवसांत / आठवड्यांत", term="AKI precipitants", opts=[
    O("dehydration", "Vomiting / loose motions / not drinking", "उल्टी / दस्त / पानी न पीना", "उलटी / जुलाब / पाणी न पिणे", ["Acute kidney injury"]),
    O("painkiller", "Painkillers (diclofenac etc.)", "दर्द की गोली (डाइक्लोफेनाक)", "वेदनाशामक (डायक्लोफेनाक)", ["Acute kidney injury"]),
    O("infection", "Fever / serious infection", "बुखार / गंभीर इन्फेक्शन", "ताप / गंभीर संसर्ग", ["Acute kidney injury"]),
    O("snake_bite", "Snake bite (viper) / wasp stings", "साँप काटा (वाइपर) / ततैया", "साप चावला (व्हायपर) / गांधीलमाशी", ["Acute kidney injury"]),
    O("contrast_new_drug", "CT dye / new BP medicine / herbal", "सीटी डाई / नई बीपी दवा / जड़ी-बूटी", "सीटी डाय / नवीन बीपी औषध / जडीबुटी", ["Acute kidney injury"]),
    O("cola_urine", "Muscle crush / dark cola urine", "मांसपेशी दबना / कोला जैसा पेशाब", "स्नायू दबणे / कोलासारखी लघवी", ["Rhabdomyolysis"])],
  src=f"{UR}, p356; General clinical practice")
Q("lk_uraemia", "low_urine", "redflag", 4, "multi", "Danger signs", "ख़तरे के निशान", "धोक्याची चिन्हे", term="Uraemic / fluid overload features", opts=[
    O("breathless", "Breathless / can't lie flat", "साँस फूलना / लेट नहीं पाते", "धाप / झोपता येत नाही", ["Acute kidney injury"]),
    O("confused", "Drowsy / confused / fits", "सुस्ती / उलझन / दौरा", "गुंगी / गोंधळ / झटके", ["Uraemia"]),
    O("vomit_hiccup", "Vomiting / hiccups / no appetite", "उल्टी / हिचकी / भूख नहीं", "उलटी / उचकी / भूक नाही", ["Uraemia"]),
    O("chest_pain", "Chest pain", "सीने में दर्द", "छातीत दुखणे", ["Uraemic pericarditis"]),
    O("weak_palp", "Muscle weakness / palpitations", "मांसपेशी कमज़ोर / धड़कन", "स्नायू अशक्त / धडधड", ["Hyperkalaemia"])],
  src=f"{UR}, p358 (Box 17.2)")
Q("lk_ckd_symptoms", "low_urine", "associated", 5, "multi", "Long-standing symptoms", "पुराने लक्षण", "जुनी लक्षणे", term="CKD features", opts=[
    O("itch", "Itching all over", "पूरे शरीर में खुजली", "संपूर्ण अंगाला खाज", ["Chronic kidney disease"]),
    O("pale_tired", "Pale / tired", "पीलापन / थकान", "फिकटपणा / थकवा", ["Chronic kidney disease"]),
    O("night_urine", "Passing urine at night often", "रात को बार-बार पेशाब", "रात्री वारंवार लघवी", ["Chronic kidney disease"]),
    O("swelling", "Swelling of face / feet", "चेहरा / पैर सूजे", "चेहरा / पाय सुजलेले", ["Chronic kidney disease", "Glomerulonephritis / nephrotic syndrome"]),
    O("frothy", "Frothy urine", "झागदार पेशाब", "फेसाळ लघवी", ["Glomerulonephritis / nephrotic syndrome"]),
    O("cramps_restless", "Cramps / restless legs", "ऐंठन / पैरों में बेचैनी", "पेटके / पायांत अस्वस्थता", ["Chronic kidney disease"])],
  src=f"{UR}, p357-358")
Q("lk_risk", "low_urine", "risk", 6, "multi", "Kidney disease risk factors", "किडनी रोग के कारण", "मूत्रपिंड आजाराची कारणे", term="CKD risk factors", opts=[
    O("dm", "Diabetes", "शुगर", "मधुमेह", ["Chronic kidney disease"]),
    O("htn", "High BP", "हाई बीपी", "उच्च रक्तदाब", ["Chronic kidney disease"]),
    O("stones_prostate", "Stones / prostate problem", "पथरी / प्रोस्टेट", "मुतखडा / प्रोस्टेट", ["Chronic kidney disease"]),
    O("painkillers_years", "Painkillers / desi medicines for years", "सालों से दर्द की गोली / देसी दवा", "वर्षानुवर्षे वेदनाशामक / देशी औषध", ["Chronic kidney disease"]),
    O("family", "Kidney disease / dialysis in family", "परिवार में किडनी रोग / डायलिसिस", "कुटुंबात मूत्रपिंड आजार / डायलिसिस", ["Chronic kidney disease"]),
    O("on_dialysis", "Already on dialysis", "डायलिसिस चल रहा है", "डायलिसिस सुरू आहे", ["Chronic kidney disease"])],
  src=f"{UR}, p356-358")

# ---------------------------------------------------------------- INCONTINENCE  (p357)
IN = f"{UR}, p357"
Q("in_type", "incontinence", "hopi", 1, "multi", "When does urine leak?", "पेशाब कब निकल जाता है?", "लघवी कधी गळते?", term="Type of incontinence", opts=[
    O("cough_sneeze", "On coughing / sneezing / lifting", "खाँसने / छींकने / वज़न उठाने पर", "खोकताना / शिंकताना / वजन उचलताना", ["Stress incontinence"]),
    O("urge", "Sudden urge, can't reach toilet", "अचानक ज़ोर, टॉयलेट तक नहीं पहुँच पाते", "अचानक जोर, शौचालयापर्यंत पोहोचता येत नाही", ["Urge incontinence / overactive bladder"]),
    O("dribble_constant", "Constant dribbling, bladder feels full", "लगातार बूँद-बूँद, मूत्राशय भरा लगता", "सतत थेंब-थेंब, मूत्राशय भरलेले वाटते", ["Overflow incontinence (retention)"]),
    O("constant_wet", "Always wet, day and night", "हमेशा गीला, दिन-रात", "नेहमी ओले, दिवस-रात्र", ["Fistula"]),
    O("cant_reach", "Can't get to toilet in time due to walking/memory", "चलने/याददाश्त की वजह से समय पर नहीं पहुँचते", "चालणे/स्मरणामुळे वेळेवर पोहोचत नाहीत", ["Functional incontinence"])],
  src=IN)
Q("in_neuro", "incontinence", "redflag", 2, "yesno", "New leakage with back pain, leg weakness or numbness around the anus?",
  "क्या नया रिसाव, साथ में कमर दर्द, पैरों में कमज़ोरी या गुदा के आसपास सुन्नपन?", "नवीन गळती, सोबत कंबरदुखी, पायांत अशक्तपणा किंवा गुदद्वाराभोवती बधिरपणा?",
  term="Neurogenic (cauda equina / cord)", rf="Possible cauda equina / cord compression — EMERGENCY", ddx=["Cauda equina syndrome", "Spinal cord compression"], key="cord_signs", src=f"{H}, Ch 16, p310")
Q("in_fistula", "incontinence", "redflag", 3, "yesno", "(Women) Always wet since a difficult / long delivery or operation?", "(महिला) कठिन/लंबी डिलीवरी या ऑपरेशन के बाद से हमेशा गीला?",
  "(महिला) कठीण/लांब प्रसूती किंवा ऑपरेशननंतर नेहमी ओले?", term="Possible vesico-vaginal fistula", rf="Possible obstetric fistula — refer", ddx=["Fistula"],
  applies={"sex": "female"}, src="General clinical practice")
Q("in_factors", "incontinence", "risk", 4, "multi", "Contributing factors", "इनमें से कुछ?", "यापैकी काही?", term="Contributing factors", opts=[
    O("deliveries", "Many / difficult deliveries", "कई / कठिन डिलीवरी", "अनेक / कठीण प्रसूती", ["Stress incontinence"]),
    O("diuretic", "Water tablets / lots of tea", "पेशाब की गोली / बहुत चाय", "लघवीची गोळी / खूप चहा", ["Urge incontinence / overactive bladder"]),
    O("dm", "Diabetes", "शुगर", "मधुमेह", ["Overflow incontinence (retention)", "Urge incontinence / overactive bladder"]),
    O("constipation", "Constipation", "कब्ज़", "बद्धकोष्ठता", ["Overflow incontinence (retention)"]),
    O("prostate_op", "Prostate operation", "प्रोस्टेट का ऑपरेशन", "प्रोस्टेटचे ऑपरेशन", ["Post-prostatectomy incontinence"]),
    O("stroke_dementia", "Stroke / memory loss / Parkinson's", "लकवा / भूलने की बीमारी / पार्किंसन", "पक्षाघात / विस्मरण / पार्किन्सन", ["Urge incontinence / overactive bladder", "Functional incontinence"])],
  src=IN)
Q("in_impact", "incontinence", "hopi", 5, "yesno", "Using pads / avoiding going out because of it?", "क्या पैड इस्तेमाल करते हैं / इसकी वजह से बाहर जाना बंद?",
  "पॅड वापरता का / यामुळे बाहेर जाणे टाळता का?", term="Impact on daily life", src=f"{H}, Ch 1, p7 (Box 1.5)")

# ---------------------------------------------------------------- SCROTAL PAIN / SWELLING
SC = f"{UR}, p369 (Box 17.4); General clinical practice"
Q("sc_torsion", "scrotal", "redflag", 1, "yesno", "Sudden severe testis pain (within hours), with vomiting, especially in a boy/young man?",
  "क्या अचानक (कुछ घंटों में) अंडकोष में तेज़ दर्द, उल्टी के साथ, ख़ासकर लड़के/जवान में?", "अचानक (काही तासांत) अंडकोषात तीव्र दुखणे, उलटीसोबत, विशेषतः मुलगा/तरुण?",
  term="Acute scrotum", rf="Possible testicular torsion — SURGICAL EMERGENCY (within 6 hours)", ddx=["Testicular torsion"], applies={"sex": "male"}, src=SC)
Q("sc_type", "scrotal", "hopi", 2, "choice", "What is the problem?", "क्या तकलीफ़ है?", "काय त्रास आहे?", term="Presentation", applies={"sex": "male"}, opts=[
    O("pain_fever", "Painful swollen testis over days, fever, burning urine", "दिनों में दर्दनाक सूजा अंडकोष, बुखार, पेशाब में जलन", "दिवसांत दुखरा सुजलेला अंडकोष, ताप, लघवीची जळजळ", ["Epididymo-orchitis"]),
    O("painless_lump", "Painless hard lump in testis", "अंडकोष में बिना दर्द की सख़्त गाँठ", "अंडकोषात न दुखणारी कडक गाठ", ["Testicular tumour"]),
    O("painless_swell", "Painless big soft swelling", "बिना दर्द बड़ी नरम सूजन", "न दुखणारी मोठी मऊ सूज", ["Hydrocele", "Filarial hydrocele"]),
    O("goes_up_cough", "Swelling in groin that goes back / bigger on coughing", "जांघ में सूजन जो अंदर चली जाती / खाँसने पर बढ़ती", "जांघेत सूज जी आत जाते / खोकल्यावर वाढते", ["Inguinal hernia"]),
    O("worms_bag", "Feels like bag of worms, heavy by evening", "कीड़ों की थैली जैसा, शाम तक भारी", "किड्यांच्या पिशवीसारखे, संध्याकाळपर्यंत जड", ["Varicocele"])],
  src=SC)
Q("sc_hernia_stuck", "scrotal", "redflag", 3, "yesno", "Groin swelling that won't go back, painful, with vomiting / no gas?",
  "क्या जांघ की सूजन अंदर नहीं जा रही, दर्द, उल्टी / गैस नहीं निकल रही?", "जांघेची सूज आत जात नाही, दुखते, उलटी / गॅस होत नाही?",
  term="Irreducible / strangulated hernia", rf="Possible strangulated hernia — SURGICAL EMERGENCY", ddx=["Strangulated hernia"], src=SC)
Q("sc_mumps", "scrotal", "associated", 4, "yesno", "Swelling in front of ears (mumps) in last 2 weeks?", "क्या पिछले 2 हफ़्ते में कान के सामने सूजन (गलसुआ)?",
  "मागील 2 आठवड्यांत कानासमोर सूज (गालगुंड)?", term="Recent mumps", ddx=["Mumps orchitis"], applies={"sex": "male"}, src=SC)

# ---------------------------------------------------------------- SEXUAL HEALTH / STI  (Box 17.4) — ask privately, non-judgementally
ST = f"{UR}, p369 (Box 17.4)"
Q("st_privacy", "sti", "hopi", 1, "yesno", "Patient is being asked in private, consent taken for sexual health questions?",
  "क्या मरीज़ से अकेले में पूछा जा रहा है और इन सवालों के लिए अनुमति ली है?", "रुग्णाला एकांतात विचारले जात आहे आणि या प्रश्नांसाठी परवानगी घेतली आहे का?",
  term="Privacy / consent confirmed", src=f"{ST} (confidential, non-judgemental)")
Q("st_symptoms", "sti", "hopi", 2, "multi", "Which problems?", "कौन-सी तकलीफ़?", "कोणता त्रास?", term="Genitourinary symptoms", show={"q": "st_privacy", "eq": "yes"}, opts=[
    O("discharge_urethra", "Discharge from urine pipe (men)", "पेशाब की नली से स्राव (पुरुष)", "मूत्रनलिकेतून स्राव (पुरुष)", ["Gonorrhoea / chlamydia (urethritis)"]),
    O("discharge_vagina", "Abnormal vaginal discharge / smell", "योनि से असामान्य स्राव / बदबू", "योनीतून असामान्य स्राव / दुर्गंध", ["Vaginal infection / STI", "Pelvic inflammatory disease"]),
    O("ulcer_painful", "Painful genital sore(s)", "गुप्तांग पर दर्दनाक छाले", "गुप्तांगावर दुखरे फोड", ["Genital herpes", "Chancroid"]),
    O("ulcer_painless", "Painless genital sore", "गुप्तांग पर बिना दर्द का घाव", "गुप्तांगावर न दुखणारी जखम", ["Syphilis"]),
    O("warts", "Warts / growths", "मस्से / गाँठें", "चामखीळ / गाठी", ["Genital warts"]),
    O("itch_rash", "Itching / rash in genital area", "गुप्तांग में खुजली / दाने", "गुप्तांगात खाज / पुरळ", ["Fungal infection", "Scabies / pubic lice"]),
    O("groin_nodes", "Swollen glands in groin", "जांघ में गाँठें", "जांघेत गाठी", ["Syphilis", "Chancroid", "LGV"]),
    O("pain_sex", "Pain during sex / lower belly pain", "संभोग में दर्द / नीचे पेट दर्द", "संभोगात दुखणे / खालच्या पोटात दुखणे", ["Pelvic inflammatory disease"])],
  src=ST)
Q("st_risk", "sti", "risk", 3, "multi", "Exposure (only if comfortable answering)", "संपर्क (सिर्फ़ अगर बताने में सहज हों)", "संपर्क (फक्त सांगण्यात सहज असाल तर)",
  term="Sexual risk history", show={"q": "st_privacy", "eq": "yes"}, opts=[
      O("new_partner", "New partner in last 3 months", "पिछले 3 महीने में नया साथी", "मागील 3 महिन्यांत नवीन जोडीदार"),
      O("multiple", "More than one partner", "एक से ज़्यादा साथी", "एकापेक्षा जास्त जोडीदार"),
      O("no_condom", "No condom", "कंडोम नहीं", "कंडोम नाही"),
      O("partner_symptoms", "Partner has similar symptoms", "साथी को भी ऐसे लक्षण", "जोडीदारालाही अशी लक्षणे"),
      O("previous_sti", "STI treated before", "पहले गुप्त रोग का इलाज", "आधी गुप्तरोगाचा उपचार")],
  src=ST)
Q("st_systemic", "sti", "associated", 4, "multi", "Other symptoms", "दूसरे लक्षण", "इतर लक्षणे", term="Systemic features", show={"q": "st_privacy", "eq": "yes"}, opts=[
    O("fever_rash", "Fever with body rash (incl. palms/soles)", "बुखार के साथ शरीर पर दाने (हथेली/तलवे भी)", "तापासोबत अंगावर पुरळ (तळहात/तळपायही)", ["Secondary syphilis", "Acute HIV"]),
    O("joint_pain", "Joint pains / red eyes", "जोड़ों में दर्द / आँखें लाल", "सांधेदुखी / डोळे लाल", ["Reactive arthritis", "Gonococcal arthritis"]),
    O("wt_loss", "Weight loss / long fever / thrush", "वज़न घटना / लंबा बुखार / मुँह में सफ़ेद परत", "वजन घटणे / लांब ताप / तोंडात पांढरा थर", ["HIV"])],
  src=ST)
Q("st_pid", "sti", "redflag", 5, "yesno", "(Women) Lower belly pain with fever, or missed period with pain?", "(महिला) नीचे पेट दर्द के साथ बुखार, या माहवारी रुकी और दर्द?",
  "(महिला) खालच्या पोटात दुखणे तापासोबत, किंवा पाळी चुकली व दुखणे?", term="PID / ectopic risk", rf="Pelvic pain with fever / missed period — PID or ectopic, urgent",
  ddx=["Pelvic inflammatory disease", "Ovarian / ectopic"], applies={"sex": "female", "min_age": 12, "max_age": 55}, show={"q": "st_privacy", "eq": "yes"}, src=ST)
