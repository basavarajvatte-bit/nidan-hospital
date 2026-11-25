# ====================================================================== SYSTEM 1: CARDIOVASCULAR (CVS)
# Hutchison 24e, Ch 13 (Cardiovascular system), p189-197; Box 13.1-13.10; Table 13.2 (NYHA).
# Executed inside hx_bank.py (uses its C / O / Q helpers). Question IDs are permanent: never delete, set active=False.

CV = f"{H}, Ch 13"
CVR = f"{H}, Ch 13, p189-190 (Box 13.1)"

C("palpitations", "Cardiovascular", "Palpitations (heart racing)", "दिल की धड़कन तेज़ / घबराहट", "छातीत धडधड", "💓", 11, f"{CV}, p194")
C("syncope", "Cardiovascular", "Fainting / blackout", "बेहोशी / चक्कर खाकर गिरना", "बेशुद्ध पडणे / भोवळ", "😵", 12, f"{CV}, p194")
C("leg_swelling", "Cardiovascular", "Leg / ankle swelling", "पैरों / टखनों में सूजन", "पाय / घोट्यांना सूज", "🦶", 13, f"{CV}, p193, p196")
C("claudication", "Cardiovascular", "Leg pain on walking", "चलने पर पैर में दर्द", "चालताना पाय दुखणे", "🚶", 14, "Peripheral arterial history (general clinical practice)")

# ---------------------------------------------------------------- CHEST PAIN (refined)
Q("cp_episode", "chest_pain", "hopi", 3, "choice", "How long does each episode of pain last?", "हर बार दर्द कितनी देर रहता है?",
  "प्रत्येक वेळी दुखणे किती वेळ राहते?", term="Duration of episode", opts=[
      O("seconds", "A few seconds", "कुछ सेकंड", "काही सेकंद", ["Musculoskeletal", "Anxiety"]),
      O("2to10", "2–10 minutes", "2 से 10 मिनट", "2 ते 10 मिनिटे", ["Angina / ACS"]),
      O("gt20", "More than 20 minutes", "20 मिनट से ज़्यादा", "20 मिनिटांपेक्षा जास्त", ["Angina / ACS", "Pericarditis", "Aortic dissection", "Pulmonary embolism"]),
      O("constant_days", "Constant for hours / days", "घंटों / दिनों से लगातार", "तासन्तास / दिवसांपासून सतत", ["Musculoskeletal", "Pericarditis", "Reflux / GORD"])],
  src=f"{CV}, p190-191")
Q("cp_onset_sudden", "chest_pain", "hopi", 4, "yesno", "Did the pain start very suddenly at full strength?",
  "क्या दर्द एकदम अचानक पूरी ताक़त से शुरू हुआ?", "दुखणे एकदम अचानक पूर्ण तीव्रतेने सुरू झाले का?",
  term="Abrupt onset (maximal at onset)", pos="Abrupt maximal onset: dissection, PE, pneumothorax", neg="Crescendo onset is more typical of ischaemia",
  ddx=["Aortic dissection", "Pulmonary embolism", "Pneumothorax"], src=f"{CV}, p191-192")
Q("cp_triggers", "chest_pain", "hopi", 6, "multi", "What brings the pain on?", "दर्द किस चीज़ से शुरू होता है?", "दुखणे कशामुळे सुरू होते?",
  term="Provoking factors", opts=[
      O("walking", "Walking / climbing stairs", "चलना / सीढ़ी चढ़ना", "चालणे / जिना चढणे", ["Angina / ACS"]),
      O("after_meal", "After a heavy meal", "भारी खाने के बाद", "जड जेवणानंतर", ["Angina / ACS", "Reflux / GORD"]),
      O("cold", "Cold weather", "ठंड में", "थंडीत", ["Angina / ACS"]),
      O("emotion", "Anger / stress", "गुस्सा / तनाव", "राग / ताण", ["Angina / ACS", "Anxiety"]),
      O("breathing", "Deep breath / cough", "गहरी साँस / खाँसी", "दीर्घ श्वास / खोकला", ["Pleurisy", "Pericarditis", "Pulmonary embolism"]),
      O("movement", "Moving arm / twisting body", "हाथ हिलाना / शरीर मोड़ना", "हात हलवणे / शरीर वळवणे", ["Musculoskeletal"]),
      O("lying", "Lying down / bending", "लेटना / झुकना", "झोपणे / वाकणे", ["Reflux / GORD", "Pericarditis"]),
      O("rest", "Comes even at rest", "आराम में भी", "विश्रांतीतही", ["Angina / ACS"])],
  src=f"{CV}, p190-191")
Q("cp_relief", "chest_pain", "hopi", 7, "multi", "What makes it better?", "किससे आराम मिलता है?", "कशाने आराम मिळतो?",
  term="Relieving factors", opts=[
      O("rest", "Rest (within minutes)", "आराम करने से (कुछ मिनट में)", "विश्रांतीने (काही मिनिटांत)", ["Angina / ACS"]),
      O("sorbitrate", "Tablet under tongue (Sorbitrate / NTG)", "जीभ के नीचे की गोली (सॉर्बिट्रेट)", "जिभेखालची गोळी (सॉर्बिट्रेट)", ["Angina / ACS", "Oesophageal spasm"]),
      O("antacid", "Antacid / gel / food", "एंटासिड / जेल / खाना", "अँटासिड / जेल / अन्न", ["Reflux / GORD", "Peptic ulcer"]),
      O("sit_forward", "Sitting up, leaning forward", "आगे झुककर बैठना", "पुढे वाकून बसणे", ["Pericarditis"]),
      O("nothing", "Nothing helps", "किसी से आराम नहीं", "कशानेच आराम नाही", ["Angina / ACS", "Aortic dissection"])],
  src=f"{CV}, p190-191")
Q("cp_crescendo", "chest_pain", "redflag", 8, "yesno", "Known chest pain now coming more often, with less effort, or at rest?",
  "क्या पहले वाला सीने का दर्द अब जल्दी-जल्दी, कम मेहनत पर या आराम में भी आने लगा है?",
  "आधीचे छातीचे दुखणे आता वारंवार, कमी श्रमाने किंवा विश्रांतीतही येऊ लागले आहे का?",
  term="Crescendo / unstable angina", rf="Worsening angina pattern — possible unstable angina (ACS)", ddx=["Angina / ACS"], src=f"{CV}, p191 (Box 13.5)")
Q("cp_tearing_back", "chest_pain", "redflag", 9, "yesno", "Severe tearing pain going to the back, with weakness/numbness of a limb or fainting?",
  "क्या पीठ की तरफ फटने जैसा तेज़ दर्द, साथ में हाथ-पैर में कमज़ोरी/सुन्नपन या बेहोशी?",
  "पाठीकडे फाटल्यासारखे तीव्र दुखणे, सोबत हात-पायात अशक्तपणा/बधिरपणा किंवा बेशुद्धी?",
  term="Dissection features", rf="Possible aortic dissection — compare BP both arms, urgent doctor", ddx=["Aortic dissection"],
  show={"q": "cp_character", "in": ["tearing"]}, src=f"{CV}, p191-192 (Box 13.7)")
Q("cp_cocaine", "chest_pain", "risk", 14, "yesno", "Any recreational drug use (e.g. cocaine, ganja) recently?",
  "क्या हाल में कोई नशे की चीज़ (जैसे कोकीन, गांजा) ली है?", "अलीकडे कोणते नशेचे पदार्थ (उदा. कोकेन, गांजा) घेतले का?",
  term="Recreational drug use", ddx=["Angina / ACS"], key="recreational_drugs", src=f"{CV}, p189")
Q("cp_prev_cardiac", "chest_pain", "risk", 15, "multi", "Previous heart problems", "पहले दिल की कौन-सी तकलीफ़ रही है?", "आधी हृदयाचा कोणता त्रास होता?",
  term="Previous cardiac history", key="cardiac_hx", opts=[
      O("mi", "Heart attack", "हार्ट अटैक", "हार्ट अटॅक", ["Angina / ACS"]),
      O("stent", "Angioplasty / stent / bypass", "एंजियोप्लास्टी / स्टेंट / बायपास", "अँजिओप्लास्टी / स्टेंट / बायपास", ["Angina / ACS"]),
      O("hf", "Heart failure / weak heart", "दिल कमज़ोर (हार्ट फेल्योर)", "हृदय कमकुवत (हार्ट फेल्युअर)", ["Heart failure"]),
      O("valve", "Valve disease", "वाल्व की बीमारी", "झडपेचा आजार", ["Valvular heart disease"]),
      O("rheumatic", "Rheumatic fever in childhood", "बचपन में रूमेटिक बुखार", "लहानपणी र्‍ह्युमॅटिक ताप", ["Valvular heart disease"]),
      O("arrhythmia", "Irregular heartbeat", "धड़कन अनियमित", "ठोके अनियमित", ["Arrhythmia"]),
      O("stroke_tia", "Stroke / mini-stroke", "लकवा / छोटा लकवा", "पक्षाघात / लहान पक्षाघात", ["Angina / ACS"]),
      O("kidney", "Kidney disease", "किडनी की बीमारी", "मूत्रपिंड आजार", [])],
  src=CVR)

# ---------------------------------------------------------------- BREATHLESSNESS: cardiac branch
Q("br_pillows", "breathless", "hopi", 31, "number", "How many pillows needed to sleep without breathlessness?",
  "बिना साँस फूले सोने के लिए कितने तकिए लगते हैं?", "धाप न लागता झोपण्यासाठी किती उशा लागतात?",
  term="Pillow orthopnoea (number)", show={"q": "br_orthopnoea", "eq": "yes"}, src=f"{CV}, p194")
Q("br_nyha", "breathless", "hopi", 32, "choice", "Which describes daily life best?", "रोज़ की ज़िंदगी में कैसी तकलीफ़ है?", "रोजच्या जीवनात कसा त्रास आहे?",
  term="NYHA class", opts=[
      O("I", "No limitation", "कोई रुकावट नहीं", "काही अडचण नाही"),
      O("II", "Breathless on normal effort (stairs)", "आम मेहनत (सीढ़ी) पर साँस फूले", "सामान्य श्रमाने (जिना) धाप", ["Heart failure"]),
      O("III", "Breathless on little effort (dressing)", "थोड़े काम (कपड़े पहनना) पर भी", "थोड्या कामानेही (कपडे घालणे)", ["Heart failure"]),
      O("IV", "Breathless even at rest", "आराम में भी", "विश्रांतीतही", ["Heart failure"])],
  src=f"{CV}, p193 (Table 13.2)")
Q("br_frothy", "breathless", "redflag", 33, "yesno", "Coughing up frothy / pink sputum with severe breathlessness?",
  "क्या साँस बहुत फूलने के साथ झागदार या गुलाबी बलगम आ रहा है?", "खूप धाप लागून फेसाळ किंवा गुलाबी कफ येतो आहे का?",
  term="Frothy pink sputum", rf="Possible acute pulmonary oedema (acute LVF)", ddx=["Heart failure"], src=f"{CV}, p193 (Box 13.9)")
Q("br_fatigue", "breathless", "associated", 34, "yesno", "Tired easily, especially by evening?", "क्या जल्दी थकान होती है, ख़ासकर शाम तक?",
  "लवकर थकवा येतो का, विशेषतः संध्याकाळपर्यंत?", term="Exertional fatigue", ddx=["Heart failure", "Anaemia"], key="fatigue", src=f"{CV}, p194")
Q("br_weightgain", "breathless", "associated", 35, "yesno", "Weight increased quickly / belly swelling recently?", "क्या वज़न जल्दी बढ़ा या पेट फूला है?",
  "वजन पटकन वाढले किंवा पोट फुगले आहे का?", term="Fluid retention (weight gain / ascites)", ddx=["Heart failure", "Liver disease", "Kidney disease"], src=f"{CV}, p193 (Box 13.10)")
Q("br_palp", "breathless", "associated", 36, "yesno", "Heart racing / irregular heartbeat with breathlessness?", "क्या साँस फूलने के साथ धड़कन तेज़ या अनियमित?",
  "धापेसोबत धडधड किंवा अनियमित ठोके?", term="Palpitations", ddx=["Arrhythmia", "Valvular heart disease"], key="palpitations", src=f"{CV}, p194")
Q("br_cardiac_hx", "breathless", "risk", 37, "multi", "Previous heart problems", "पहले दिल की कौन-सी तकलीफ़ रही है?", "आधी हृदयाचा कोणता त्रास होता?",
  term="Previous cardiac history", key="cardiac_hx", opts=[
      O("mi", "Heart attack", "हार्ट अटैक", "हार्ट अटॅक", ["Heart failure"]),
      O("hf", "Heart failure / weak heart", "दिल कमज़ोर (हार्ट फेल्योर)", "हृदय कमकुवत (हार्ट फेल्युअर)", ["Heart failure"]),
      O("valve", "Valve disease / rheumatic fever", "वाल्व की बीमारी / रूमेटिक बुखार", "झडपेचा आजार / र्‍ह्युमॅटिक ताप", ["Valvular heart disease"]),
      O("htn", "Long-standing high BP", "पुराना हाई बीपी", "जुना उच्च रक्तदाब", ["Heart failure"]),
      O("alcohol", "Heavy alcohol for years", "सालों से ज़्यादा शराब", "वर्षानुवर्षे जास्त दारू", ["Heart failure (alcoholic cardiomyopathy)"])],
  src=f"{CV}, p189-193")

# ---------------------------------------------------------------- PALPITATIONS  (p194)
P = f"{CV}, p194"
Q("pa_rate", "palpitations", "hopi", 1, "choice", "Heartbeat during the attack", "दौरे के समय धड़कन कैसी होती है?", "त्रासाच्या वेळी ठोके कसे असतात?",
  term="Rate and rhythm", opts=[
      O("fast_regular", "Fast and regular", "तेज़ और एक-सी", "जलद आणि नियमित", ["SVT / tachyarrhythmia", "Sinus tachycardia"]),
      O("fast_irregular", "Fast and irregular (all over the place)", "तेज़ और बेतरतीब", "जलद आणि अनियमित", ["Atrial fibrillation"]),
      O("missed", "Missed / dropped beat, then a thump", "एक धड़कन छूटकर फिर ज़ोर की धक", "एक ठोका चुकून मग जोराचा ठोका", ["Ectopic beats (usually benign)"]),
      O("slow", "Slow / pounding", "धीमी और ज़ोरदार", "हळू आणि जोरदार", ["Bradycardia / heart block"])],
  src=P)
Q("pa_tap", "palpitations", "hopi", 2, "text", "Ask patient to tap the rhythm on the table — describe it", "मेज़ पर उँगली से धड़कन की ताल बजाकर दिखाने को कहें — कैसी थी?",
  "टेबलावर बोटाने ठोक्यांचा ताल वाजवून दाखवायला सांगा — कसा होता?", term="Tapped-out rhythm", src=P)
Q("pa_onset", "palpitations", "hopi", 3, "yesno", "Does it start and stop suddenly (like a switch)?", "क्या धड़कन अचानक शुरू और अचानक बंद होती है (बटन जैसे)?",
  "धडधड अचानक सुरू आणि अचानक बंद होते का (बटनासारखी)?", term="Abrupt onset and offset", pos="Re-entrant tachycardia (SVT) or VT",
  neg="Gradual onset/offset suggests sinus tachycardia (anxiety, fever, anaemia, thyroid)", ddx=["SVT / tachyarrhythmia"], src=P)
Q("pa_duration", "palpitations", "hopi", 4, "choice", "How long does each attack last?", "हर बार कितनी देर रहती है?", "प्रत्येक वेळी किती वेळ राहते?",
  term="Duration of attacks", opts=[
      O("seconds", "Seconds", "कुछ सेकंड", "काही सेकंद", ["Ectopic beats (usually benign)"]),
      O("minutes", "Minutes", "कुछ मिनट", "काही मिनिटे", ["SVT / tachyarrhythmia", "Atrial fibrillation", "Anxiety / panic"]),
      O("hours", "Hours or continuous", "घंटों या लगातार", "तासन्तास किंवा सतत", ["Atrial fibrillation", "Sinus tachycardia", "Thyrotoxicosis"])],
  src=P)
Q("pa_vagal", "palpitations", "hopi", 5, "yesno", "Stops by holding breath and straining, or splashing cold water on face?",
  "क्या साँस रोककर ज़ोर लगाने या चेहरे पर ठंडा पानी डालने से रुक जाती है?", "श्वास रोखून जोर लावल्याने किंवा चेहऱ्यावर थंड पाणी मारल्याने थांबते का?",
  term="Terminated by vagal manoeuvres", ddx=["SVT / tachyarrhythmia"], show={"q": "pa_onset", "eq": "yes"}, src="General clinical practice")
Q("pa_triggers", "palpitations", "hopi", 6, "multi", "What brings it on?", "किस चीज़ से शुरू होती है?", "कशामुळे सुरू होते?", term="Triggers", opts=[
    O("exercise", "Exercise", "कसरत / मेहनत", "व्यायाम / श्रम", ["Exercise-induced arrhythmia"]),
    O("tea_coffee", "Tea / coffee / energy drinks", "चाय / कॉफ़ी / एनर्जी ड्रिंक", "चहा / कॉफी / एनर्जी ड्रिंक", ["Ectopic beats (usually benign)", "Sinus tachycardia"]),
    O("alcohol", "Alcohol", "शराब", "दारू", ["Atrial fibrillation"]),
    O("stress", "Stress / fear", "तनाव / डर", "ताण / भीती", ["Anxiety / panic", "Sinus tachycardia"]),
    O("lying_left", "Lying down at night", "रात को लेटने पर", "रात्री झोपल्यावर", ["Ectopic beats (usually benign)"]),
    O("none", "No trigger", "बिना किसी कारण", "कोणत्याही कारणाशिवाय", ["SVT / tachyarrhythmia", "Atrial fibrillation"])],
  src=P)
Q("pa_syncope", "palpitations", "redflag", 7, "yesno", "Fainted, nearly fainted or had chest pain during palpitations?",
  "क्या धड़कन के समय बेहोशी, चक्कर या सीने में दर्द हुआ?", "धडधडीच्या वेळी बेशुद्धी, भोवळ किंवा छातीत दुखले का?",
  term="Palpitations with syncope/chest pain", rf="Palpitations with syncope/chest pain — possible serious arrhythmia (ECG now)",
  ddx=["Ventricular tachycardia", "SVT / tachyarrhythmia"], src=f"{CV}, p194-195")
Q("pa_exertion", "palpitations", "redflag", 8, "yesno", "Palpitations brought on by exercise?", "क्या धड़कन कसरत/मेहनत करते समय होती है?",
  "धडधड व्यायाम/श्रम करताना होते का?", term="Exercise-induced palpitations", rf="Exertional palpitations — exclude structural heart disease / VT",
  ddx=["Ventricular tachycardia", "Hypertrophic cardiomyopathy"], show={"q": "pa_triggers", "has": "exercise"}, src=P)
Q("pa_thyroid", "palpitations", "associated", 9, "multi", "Any of these too?", "इनमें से कुछ और भी?", "यापैकी काही आणखी?", term="Systemic features", opts=[
    O("weightloss_heat", "Weight loss, sweating, can't tolerate heat", "वज़न घटना, पसीना, गर्मी सहन न होना", "वजन घटणे, घाम, उष्णता सहन न होणे", ["Thyrotoxicosis"]),
    O("tremor", "Hand tremor", "हाथ काँपना", "हात थरथरणे", ["Thyrotoxicosis", "Anxiety / panic"]),
    O("pale_tired", "Pale, tired", "पीला पड़ना, थकान", "फिकट, थकवा", ["Anaemia"]),
    O("fear_tingling", "Fear of dying, tingling fingers, fast breathing", "मरने का डर, उँगलियों में झुनझुनी, तेज़ साँस", "मरण्याची भीती, बोटांना मुंग्या, जलद श्वास", ["Anxiety / panic"]),
    O("fever", "Fever", "बुखार", "ताप", ["Sinus tachycardia"])],
  src="General clinical practice")
Q("pa_drugs", "palpitations", "risk", 10, "multi", "Medicines / substances", "इनमें से कोई दवा / चीज़?", "यापैकी कोणते औषध / पदार्थ?", term="Drug causes", opts=[
    O("inhaler", "Asthma inhaler / salbutamol", "दमे का इनहेलर / सालबुटामोल", "दम्याचा इनहेलर / सालबुटामॉल", ["Drug-induced tachycardia"]),
    O("thyroxine", "Thyroid tablet (thyroxine)", "थायराइड की गोली (थायरॉक्सिन)", "थायरॉईडची गोळी (थायरॉक्सिन)", ["Drug-induced tachycardia"]),
    O("antidepressant", "Antidepressant tablets", "डिप्रेशन की दवा", "नैराश्याची औषधे", ["Drug-induced arrhythmia"]),
    O("decongestant", "Cold medicine / nasal decongestant", "सर्दी की दवा / नाक खोलने की दवा", "सर्दीचे औषध / नाक मोकळे करणारे", ["Drug-induced tachycardia"]),
    O("bp_slow", "BP / heart tablets that slow pulse", "बीपी / दिल की गोली (धड़कन धीमी करने वाली)", "बीपी / हृदयाची गोळी (ठोके कमी करणारी)", ["Bradycardia / heart block"]),
    O("tobacco", "Tobacco / gutka", "तंबाकू / गुटखा", "तंबाखू / गुटखा", [])],
  src=f"{CV}, p189")
Q("pa_fh_sudden", "palpitations", "redflag", 11, "yesno", "Anyone in family died suddenly young (under 40) or has heart muscle disease?",
  "क्या परिवार में किसी की 40 से कम उम्र में अचानक मौत हुई या दिल की मांसपेशी की बीमारी है?",
  "कुटुंबात कोणाचा 40 पेक्षा कमी वयात अचानक मृत्यू झाला आहे का किंवा हृदयस्नायूचा आजार आहे का?",
  term="Family history of sudden death", rf="Family history of sudden cardiac death — inherited heart disease?",
  ddx=["Hypertrophic cardiomyopathy", "Inherited arrhythmia"], key="fh_sudden_death", src=f"{CV}, p189")
Q("pa_known_heart", "palpitations", "risk", 12, "multi", "Previous heart problems", "पहले दिल की कौन-सी तकलीफ़ रही है?", "आधी हृदयाचा कोणता त्रास होता?",
  term="Previous cardiac history", key="cardiac_hx", opts=[
      O("mi", "Heart attack", "हार्ट अटैक", "हार्ट अटॅक", ["Ventricular tachycardia"]),
      O("valve", "Valve disease / rheumatic fever", "वाल्व की बीमारी / रूमेटिक बुखार", "झडपेचा आजार / र्‍ह्युमॅटिक ताप", ["Atrial fibrillation"]),
      O("hf", "Weak heart", "दिल कमज़ोर", "हृदय कमकुवत", ["Atrial fibrillation", "Ventricular tachycardia"]),
      O("thyroid", "Thyroid problem", "थायराइड", "थायरॉईड", ["Thyrotoxicosis", "Atrial fibrillation"])],
  src=CVR)

# ---------------------------------------------------------------- SYNCOPE  (p194-195; Ch 16 Table 16.1)
SY = f"{CV}, p194-195"
Q("sy_before", "syncope", "hopi", 1, "choice", "What did the patient feel just before?", "बेहोश होने से ठीक पहले क्या महसूस हुआ?",
  "बेशुद्ध होण्याआधी काय जाणवले?", term="Prodrome", opts=[
      O("nothing", "No warning at all", "कोई चेतावनी नहीं, अचानक", "काहीही पूर्वसूचना नाही, अचानक", ["Cardiac syncope (arrhythmia / aortic stenosis)"]),
      O("hot_sweaty", "Hot, sweaty, sick, vision going grey", "गर्मी, पसीना, जी मिचलाना, आँखों के आगे अँधेरा", "गरम, घाम, मळमळ, डोळ्यांसमोर अंधारी", ["Vasovagal syncope"]),
      O("palpitations", "Heart racing / chest pain", "धड़कन तेज़ / सीने में दर्द", "धडधड / छातीत दुखणे", ["Cardiac syncope (arrhythmia / aortic stenosis)"]),
      O("aura", "Strange smell / feeling / déjà vu", "अजीब गंध / एहसास", "विचित्र वास / भावना", ["Seizure"]),
      O("dizzy_stand", "Dizzy on standing up", "खड़े होते ही चक्कर", "उभे राहताच भोवळ", ["Postural hypotension"])],
  src=f"{SY}; Ch 16, p310 (Table 16.1)")
Q("sy_position", "syncope", "hopi", 2, "choice", "What was the patient doing?", "उस समय मरीज़ क्या कर रहा था?", "त्या वेळी रुग्ण काय करत होता?",
  term="Circumstances", opts=[
      O("standing_long", "Standing for a long time / hot crowded place", "देर तक खड़े / गर्म भीड़ वाली जगह", "बराच वेळ उभे / गरम गर्दीची जागा", ["Vasovagal syncope"]),
      O("getting_up", "Getting up from lying/sitting", "लेटे/बैठे से उठते समय", "झोपलेल्या/बसलेल्या स्थितीतून उठताना", ["Postural hypotension"]),
      O("exertion", "During exercise / exertion", "मेहनत / कसरत के दौरान", "श्रम / व्यायाम करताना", ["Cardiac syncope (arrhythmia / aortic stenosis)", "Hypertrophic cardiomyopathy"]),
      O("lying", "Lying down", "लेटे हुए", "झोपलेले असताना", ["Cardiac syncope (arrhythmia / aortic stenosis)", "Seizure"]),
      O("pain_fear_blood", "Pain / fear / sight of blood / injection", "दर्द / डर / खून देखकर / इंजेक्शन", "वेदना / भीती / रक्त पाहून / इंजेक्शन", ["Vasovagal syncope"]),
      O("cough_urine", "Coughing / passing urine / straining", "खाँसते / पेशाब करते / ज़ोर लगाते", "खोकताना / लघवी करताना / जोर लावताना", ["Situational syncope"]),
      O("neck_turn", "Turning head / shaving / tight collar", "गर्दन घुमाना / दाढ़ी बनाना / टाइट कॉलर", "मान वळवणे / दाढी करणे / घट्ट कॉलर", ["Carotid sinus hypersensitivity"])],
  src=SY)
Q("sy_exertion", "syncope", "redflag", 3, "yesno", "Did the blackout happen during exertion?", "क्या बेहोशी मेहनत/कसरत करते समय हुई?",
  "बेशुद्धी श्रम/व्यायाम करताना झाली का?", term="Exertional syncope", rf="Exertional syncope — aortic stenosis / cardiomyopathy / arrhythmia (urgent ECG/echo)",
  ddx=["Cardiac syncope (arrhythmia / aortic stenosis)", "Hypertrophic cardiomyopathy"], src=SY)
Q("sy_duration", "syncope", "hopi", 4, "choice", "How long unconscious and how was recovery?", "कितनी देर बेहोश रहे और होश कैसे आया?",
  "किती वेळ बेशुद्ध होते आणि शुद्ध कशी आली?", term="Duration and recovery", opts=[
      O("quick_clear", "Under a minute, clear-headed quickly", "एक मिनट से कम, जल्दी पूरा होश", "एका मिनिटापेक्षा कमी, लवकर पूर्ण शुद्ध", ["Vasovagal syncope", "Cardiac syncope (arrhythmia / aortic stenosis)"]),
      O("quick_flush", "Very pale, then face went red on waking", "बहुत पीला पड़ा, होश आने पर चेहरा लाल", "खूप फिकट, शुद्ध आल्यावर चेहरा लाल", ["Stokes-Adams attack (heart block)"]),
      O("confused_long", "Confused / sleepy for many minutes after", "बाद में कई मिनट तक उलझन / नींद", "नंतर अनेक मिनिटे गोंधळ / झोप", ["Seizure"]),
      O("not_recovered", "Still not fully recovered", "अभी तक पूरा होश नहीं", "अजून पूर्ण शुद्ध नाही", ["Stroke", "Hypoglycaemia", "Seizure"])],
  src=f"{SY} (Stokes-Adams); Ch 16, p310")
Q("sy_jerks", "syncope", "associated", 5, "multi", "What did the witness see?", "देखने वाले ने क्या देखा?", "पाहणाऱ्याने काय पाहिले?", term="Witness account", opts=[
    O("few_jerks", "A few brief jerks", "कुछ हल्के झटके", "काही हलके झटके", ["Vasovagal syncope"]),
    O("stiff_long_jerk", "Stiffening and jerking for >1 minute", "1 मिनट से ज़्यादा अकड़न और झटके", "1 मिनिटापेक्षा जास्त ताठरणे व झटके", ["Seizure"]),
    O("tongue", "Bitten side of tongue", "जीभ का किनारा कटा", "जिभेची कडा चावली", ["Seizure"]),
    O("urine", "Passed urine", "पेशाब निकल गया", "लघवी झाली", ["Seizure"]),
    O("pale", "Very pale / grey", "बहुत पीला / स्लेटी", "खूप फिकट / करडा", ["Cardiac syncope (arrhythmia / aortic stenosis)", "Vasovagal syncope"]),
    O("blue", "Blue lips", "होंठ नीले", "ओठ निळे", ["Seizure", "Cardiac syncope (arrhythmia / aortic stenosis)"])],
  src=f"{H}, Ch 16, p310 (Table 16.1)")
Q("sy_injury", "syncope", "redflag", 6, "yesno", "Injured head / face in the fall?", "क्या गिरने से सिर/चेहरे पर चोट लगी?", "पडल्याने डोक्याला/चेहऱ्याला इजा झाली का?",
  term="Injury during fall", rf="Head injury with blackout — assess for head injury", src=f"{H}, Ch 9")
Q("sy_recurrent", "syncope", "hopi", 7, "number", "How many such episodes in the last year?", "पिछले एक साल में ऐसा कितनी बार हुआ?",
  "मागील एका वर्षात असे किती वेळा झाले?", term="Number of episodes (12 months)", src=SY)
Q("sy_drugs", "syncope", "risk", 8, "multi", "Medicines that can drop BP / pulse", "इनमें से कोई दवा?", "यापैकी कोणते औषध?", term="Drug history (hypotensive/bradycardic)", opts=[
    O("bp", "BP tablets (several)", "बीपी की गोलियाँ (कई)", "बीपीच्या गोळ्या (अनेक)", ["Postural hypotension"]),
    O("diuretic", "Water tablets (diuretics)", "पेशाब बढ़ाने वाली गोली", "लघवी वाढवणारी गोळी", ["Postural hypotension"]),
    O("nitrate", "Sorbitrate / nitrates", "सॉर्बिट्रेट / नाइट्रेट", "सॉर्बिट्रेट / नायट्रेट", ["Postural hypotension"]),
    O("prostate", "Prostate tablets (tamsulosin)", "प्रोस्टेट की गोली (टैमसुलोसिन)", "प्रोस्टेटची गोळी (टॅमसुलोसिन)", ["Postural hypotension"]),
    O("beta", "Pulse-slowing heart tablets", "धड़कन धीमी करने वाली गोली", "ठोके कमी करणारी गोळी", ["Bradycardia / heart block"]),
    O("insulin", "Insulin / sugar tablets", "इंसुलिन / शुगर की गोली", "इन्सुलिन / साखरेची गोळी", ["Hypoglycaemia"])],
  src=f"{CV}, p189, p194")
Q("sy_fh", "syncope", "redflag", 9, "yesno", "Anyone in family died suddenly young (under 40)?",
  "क्या परिवार में किसी की 40 से कम उम्र में अचानक मौत हुई?", "कुटुंबात कोणाचा 40 पेक्षा कमी वयात अचानक मृत्यू झाला आहे का?",
  term="Family history of sudden death", rf="Syncope + family sudden death — inherited heart disease?",
  ddx=["Hypertrophic cardiomyopathy", "Inherited arrhythmia"], key="fh_sudden_death", src=f"{CV}, p189")
Q("sy_heart", "syncope", "risk", 10, "multi", "Previous heart problems", "पहले दिल की कौन-सी तकलीफ़ रही है?", "आधी हृदयाचा कोणता त्रास होता?",
  term="Previous cardiac history", key="cardiac_hx", opts=[
      O("mi", "Heart attack", "हार्ट अटैक", "हार्ट अटॅक", ["Cardiac syncope (arrhythmia / aortic stenosis)"]),
      O("valve", "Valve disease / murmur", "वाल्व की बीमारी / मर्मर", "झडपेचा आजार / मरमर", ["Cardiac syncope (arrhythmia / aortic stenosis)"]),
      O("hf", "Weak heart", "दिल कमज़ोर", "हृदय कमकुवत", ["Cardiac syncope (arrhythmia / aortic stenosis)"]),
      O("pacemaker", "Pacemaker", "पेसमेकर", "पेसमेकर", ["Bradycardia / heart block"])],
  src=CVR)

# ---------------------------------------------------------------- LEG / ANKLE SWELLING  (p193, p196)
LS = f"{CV}, p193 (Box 13.10), p196"
Q("ls_side", "leg_swelling", "hopi", 1, "choice", "Which leg?", "कौन-सा पैर सूजा है?", "कोणता पाय सुजला आहे?", term="Distribution", opts=[
    O("both", "Both legs", "दोनों पैर", "दोन्ही पाय", ["Heart failure", "Kidney disease", "Liver disease", "Drug-induced oedema", "Hypoproteinaemia"]),
    O("one", "Only one leg", "सिर्फ़ एक पैर", "फक्त एक पाय", ["Deep vein thrombosis", "Cellulitis", "Injury / local cause"])],
  src=LS)
Q("ls_dvt", "leg_swelling", "redflag", 2, "yesno", "One calf painful, hot, red or tight?", "क्या एक पिंडली में दर्द, गर्मी, लाली या कसाव है?",
  "एका पोटरीत दुखणे, गरमपणा, लाली किंवा ताण आहे का?", term="Painful unilateral calf swelling", rf="Possible deep vein thrombosis",
  ddx=["Deep vein thrombosis", "Cellulitis"], show={"q": "ls_side", "eq": "one"}, src=f"{CV}, p192 (Box 13.8)")
Q("ls_pe", "leg_swelling", "redflag", 3, "yesno", "Sudden breathlessness or chest pain along with leg swelling?",
  "क्या पैर की सूजन के साथ अचानक साँस फूलना या सीने में दर्द?", "पायाच्या सुजेसोबत अचानक धाप किंवा छातीत दुखणे?",
  term="Leg swelling with dyspnoea/chest pain", rf="Possible pulmonary embolism", ddx=["Pulmonary embolism"], src=f"{CV}, p192 (Box 13.8)")
Q("ls_pitting", "leg_swelling", "hopi", 4, "yesno", "Does pressing with a finger leave a pit / dent?", "क्या उँगली से दबाने पर गड्ढा बन जाता है?",
  "बोटाने दाबल्यावर खड्डा पडतो का?", term="Pitting oedema", neg="Non-pitting suggests lymphoedema / hypothyroidism",
  ddx=["Heart failure", "Kidney disease", "Liver disease"], src=f"{CV}, p196")
Q("ls_evening", "leg_swelling", "hopi", 5, "yesno", "Worse by evening, less in the morning?", "क्या शाम तक ज़्यादा, सुबह कम होती है?",
  "संध्याकाळपर्यंत जास्त, सकाळी कमी होते का?", term="Dependent oedema", ddx=["Heart failure", "Venous insufficiency", "Drug-induced oedema"], src=f"{CV}, p196")
Q("ls_face", "leg_swelling", "associated", 6, "yesno", "Puffy face / eyes in the morning, frothy urine?", "क्या सुबह चेहरा/आँखें सूजी, झागदार पेशाब?",
  "सकाळी चेहरा/डोळे सुजलेले, फेसाळ लघवी?", term="Periorbital oedema / proteinuria", ddx=["Kidney disease"], src=f"{H}, Ch 17, p356-358")
Q("ls_orthopnoea", "leg_swelling", "associated", 7, "yesno", "Breathless on lying flat or waking at night breathless?", "क्या लेटने पर या रात को साँस फूलने से नींद खुलती है?",
  "झोपल्यावर किंवा रात्री धाप लागून जाग येते का?", term="Orthopnoea / PND", ddx=["Heart failure"], src=f"{CV}, p193-194")
Q("ls_liver", "leg_swelling", "associated", 8, "yesno", "Belly swelling, yellow eyes, or heavy alcohol use?", "क्या पेट फूला, आँखें पीली या ज़्यादा शराब?",
  "पोट फुगले, डोळे पिवळे किंवा जास्त दारू?", term="Ascites / jaundice / alcohol", ddx=["Liver disease"], src=f"{H}, Ch 14, p243")
Q("ls_drugs", "leg_swelling", "risk", 9, "multi", "Medicines that cause swelling", "इनमें से कोई दवा?", "यापैकी कोणते औषध?", term="Drug-induced oedema", opts=[
    O("amlodipine", "BP tablet amlodipine / nifedipine", "बीपी की गोली (एम्लोडिपिन / निफ़ेडिपिन)", "बीपीची गोळी (अॅम्लोडिपिन / निफेडिपिन)", ["Drug-induced oedema"]),
    O("nsaid", "Painkillers regularly", "दर्द की गोली नियमित", "वेदनाशामक नियमित", ["Drug-induced oedema"]),
    O("steroid", "Steroids", "स्टेरॉयड", "स्टिरॉइड", ["Drug-induced oedema"]),
    O("pioglitazone", "Sugar tablet pioglitazone", "शुगर की गोली पायोग्लिटाज़ोन", "साखरेची गोळी पायोग्लिटाझोन", ["Drug-induced oedema", "Heart failure"])],
  src="General clinical practice")
Q("ls_thyroid", "leg_swelling", "associated", 10, "yesno", "Feeling cold, weight gain, dry skin, slowness?", "क्या ठंड ज़्यादा लगना, वज़न बढ़ना, सूखी त्वचा, सुस्ती?",
  "थंडी जास्त वाजणे, वजन वाढणे, कोरडी त्वचा, सुस्ती?", term="Hypothyroid features", ddx=["Hypothyroidism"], src=f"{H}, Ch 18")
Q("ls_pregnant", "leg_swelling", "redflag", 11, "yesno", "Pregnant with swelling plus headache / blurred vision?", "क्या गर्भावस्था में सूजन के साथ सिर दर्द / धुंधला दिखना?",
  "गर्भावस्थेत सुजेसोबत डोकेदुखी / अंधुक दिसणे?", term="Oedema in pregnancy with headache/visual symptoms",
  rf="Pregnancy with oedema + headache/visual change — check BP & urine protein (pre-eclampsia?)", ddx=["Pre-eclampsia"],
  applies={"sex": "female", "min_age": 14, "max_age": 50}, src=f"{H}, Ch 5 (Women)")

# ---------------------------------------------------------------- LEG PAIN ON WALKING (claudication)
CL = "Peripheral arterial history (general clinical practice)"
Q("cl_walk", "claudication", "hopi", 1, "yesno", "Calf / thigh / buttock pain on walking that goes away within minutes of standing still?",
  "क्या चलने पर पिंडली/जांघ/कूल्हे में दर्द होता है जो रुकने पर कुछ मिनट में चला जाता है?",
  "चालताना पोटरी/मांडी/नितंबात दुखते आणि थांबल्यावर काही मिनिटांत जाते का?",
  term="Intermittent claudication", pos="Peripheral arterial disease", ddx=["Peripheral arterial disease"], src=f"{H}, Ch 1, p8 (Box 1.7)")
Q("cl_distance", "claudication", "hopi", 2, "number", "Distance (metres) walked before pain starts", "कितने मीटर चलने पर दर्द शुरू होता है?",
  "किती मीटर चालल्यावर दुखणे सुरू होते?", term="Claudication distance (m)", show={"q": "cl_walk", "eq": "yes"}, src=CL)
Q("cl_spinal", "claudication", "hopi", 3, "yesno", "Pain eases only on sitting / bending forward, with numbness of legs?",
  "क्या दर्द सिर्फ़ बैठने या आगे झुकने पर कम होता है, पैरों में सुन्नपन के साथ?", "दुखणे फक्त बसल्यावर किंवा पुढे वाकल्यावर कमी होते, पायात बधिरपणासोबत?",
  term="Neurogenic claudication features", ddx=["Lumbar canal stenosis"], src=CL)
Q("cl_rest", "claudication", "redflag", 4, "yesno", "Foot pain at night / at rest, relieved by hanging leg down?",
  "क्या रात को या आराम में पैर में दर्द, पैर नीचे लटकाने से आराम?", "रात्री किंवा विश्रांतीत पाय दुखतो, पाय खाली सोडल्यावर आराम?",
  term="Rest pain", rf="Critical limb ischaemia — urgent vascular assessment", ddx=["Critical limb ischaemia"], src=CL)
Q("cl_ulcer", "claudication", "redflag", 5, "yesno", "Non-healing wound or black toe?", "क्या पैर का घाव भर नहीं रहा या अंगूठा काला पड़ा?",
  "पायाची जखम भरत नाही किंवा अंगठा काळा पडला आहे का?", term="Ulcer / gangrene", rf="Tissue loss / gangrene", ddx=["Critical limb ischaemia", "Diabetic foot"], src=CL)
Q("cl_acute", "claudication", "redflag", 6, "yesno", "Sudden severe leg pain, leg cold, pale and numb?", "क्या अचानक पैर में तेज़ दर्द, पैर ठंडा, पीला और सुन्न?",
  "अचानक पायात तीव्र दुखणे, पाय थंड, फिकट आणि बधिर?", term="Acute limb ischaemia (6 Ps)", rf="Acute limb ischaemia — EMERGENCY",
  ddx=["Acute limb ischaemia"], src=CL)
Q("cl_risk", "claudication", "risk", 7, "multi", "Artery disease risk factors", "इनमें से कुछ है?", "यापैकी काही आहे का?", term="Cardiovascular risk factors",
  key="cv_risk", opts=[
      O("smoke", "Smoking / bidi", "धूम्रपान / बीड़ी", "धूम्रपान / बिडी", ["Peripheral arterial disease"]),
      O("dm", "Diabetes", "शुगर", "मधुमेह", ["Peripheral arterial disease"]),
      O("htn", "High BP", "हाई बीपी", "उच्च रक्तदाब", ["Peripheral arterial disease"]),
      O("lipids", "High cholesterol", "कोलेस्ट्रॉल ज़्यादा", "कोलेस्टेरॉल जास्त", ["Peripheral arterial disease"]),
      O("heart_stroke", "Heart attack / stroke before", "पहले हार्ट अटैक / लकवा", "आधी हार्ट अटॅक / पक्षाघात", ["Peripheral arterial disease"]),
      O("af", "Irregular heartbeat", "धड़कन अनियमित", "ठोके अनियमित", ["Acute limb ischaemia"])],
  src=f"{CV}, p190 (Box 13.1)")
Q("cl_erectile", "claudication", "associated", 8, "yesno", "Erection problems (men)?", "क्या लिंग में तनाव की कमी (पुरुष)?", "लिंग ताठरतेची समस्या (पुरुष)?",
  term="Erectile dysfunction", ddx=["Peripheral arterial disease"], applies={"sex": "male", "min_age": 18}, src=CL)

# ---------------------------------------------------------------- old neuro "faint" path now has its own complaint
# (kept active; CNS phase will refine). Family sudden death / alcohol units added to general history:
Q("fh_sudden", None, "family", 6, "yesno", "Sudden unexplained death in family under 40?", "क्या परिवार में किसी की 40 से कम उम्र में अचानक मौत हुई?",
  "कुटुंबात कोणाचा 40 पेक्षा कमी वयात अचानक मृत्यू झाला आहे का?", term="Family history of sudden death",
  key="fh_sudden_death", src=f"{CV}, p189")
Q("ps_alcohol_qty", None, "personal", 9, "text", "Alcohol: type and amount per week (quarter/peg/bottles)", "शराब: कौन-सी और हफ़्ते में कितनी (क्वार्टर/पेग/बोतल)?",
  "दारू: कोणती आणि आठवड्याला किती (क्वार्टर/पेग/बाटली)?", term="Alcohol quantity (units/week)",
  show={"q": "ps_alcohol", "in": ["daily", "occasional"]}, src=f"{H}, Ch 1, p10 (Box 1.12); {CV}, p189")
