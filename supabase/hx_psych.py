# ====================================================================== SYSTEM 12: PSYCHIATRY (mental health)
# Hutchison 24e, Ch 8 (Psychiatric assessment), p99-120; Box 8.1 (order of history), 8.2 (depression), 8.3-8.4 (anxiety),
# 8.8-8.9 (alcohol), 8.16-8.18 (depressive thoughts, suicide risk, elevated mood), 8.19-8.23 (delusions / hallucinations).
# Executed inside hx_bank.py. Ask privately, calmly, without judgement. Asking about suicide does NOT put the idea in
# the person's mind; it helps keep them safe. Any active risk -> do not leave alone, doctor now (Tele-MANAS 14416).

PS = f"{H}, Ch 8"
SUI = f"{PS}, p111 (Box 8.16-8.17)"

C("low_mood", "Psychiatry", "Low mood / sadness / no interest", "उदासी / मन न लगना", "उदासी / मन न लागणे", "🌧️", 121, f"{PS}, p102 (Box 8.2), p111 (Box 8.16)")
C("anxiety", "Psychiatry", "Anxiety / panic / ghabrahat", "घबराहट / बेचैनी / डर", "घाबरणे / अस्वस्थता / भीती", "😰", 122, f"{PS}, p103 (Box 8.3-8.4)")
C("sleep", "Psychiatry", "Sleep problem", "नींद की तकलीफ़", "झोपेचा त्रास", "🌙", 123, f"{PS}, p102 (Box 8.2)")
C("behaviour", "Psychiatry", "Strange behaviour / hearing voices / suspicious / overactive", "अजीब व्यवहार / आवाज़ें सुनना / शक / ज़्यादा जोश", "विचित्र वागणे / आवाज ऐकू येणे / संशय / अति उत्साह", "🌀", 124, f"{PS}, p111-115 (Box 8.18-8.23)")
C("substance", "Psychiatry", "Alcohol / drugs / tobacco problem", "शराब / नशा / तंबाकू की लत", "दारू / नशा / तंबाखूचे व्यसन", "🍺", 125, f"{PS}, p106 (Box 8.8-8.9)")

# ---------------------------------------------------------------- LOW MOOD + SUICIDE RISK  (Box 8.2, 8.16, 8.17)
DP2 = f"{PS}, p102 (Box 8.2)"
Q("lm_core", "low_mood", "hopi", 1, "multi", "In the last 2 weeks, most days", "पिछले 2 हफ़्तों में, ज़्यादातर दिन", "मागील 2 आठवड्यांत, बहुतेक दिवस", term="Depressive symptoms (Box 8.2)", opts=[
    O("sad", "Sad / tearful most of the day", "दिन भर उदास / रोना आना", "दिवसभर उदास / रडू येणे", ["Depression"]),
    O("no_interest", "No interest or pleasure in things", "किसी चीज़ में मन / ख़ुशी नहीं", "कशातच मन / आनंद नाही", ["Depression"]),
    O("tired", "Tired, no energy", "थकान, ताक़त नहीं", "थकवा, ताकद नाही", ["Depression"]),
    O("sleep_early", "Waking very early, can't sleep again", "बहुत जल्दी नींद खुलना, फिर नींद नहीं", "खूप लवकर जाग, पुन्हा झोप नाही", ["Depression"]),
    O("appetite", "Appetite / weight changed", "भूख / वज़न बदला", "भूक / वजन बदलले", ["Depression"]),
    O("concentration", "Can't concentrate / decide", "ध्यान नहीं लगता / फ़ैसला नहीं कर पाते", "लक्ष लागत नाही / निर्णय घेता येत नाही", ["Depression"]),
    O("guilt_worthless", "Feels guilty / worthless / a burden", "अपराधी / बेकार / बोझ महसूस करना", "अपराधी / निरुपयोगी / ओझे वाटणे", ["Depression"]),
    O("morning_worse", "Mood worst in the morning", "सुबह सबसे ज़्यादा उदास", "सकाळी सर्वात जास्त उदास", ["Depression"]),
    O("slow_agitated", "Slowed down or very restless", "धीमे हो गए या बहुत बेचैन", "मंद झाले किंवा खूप अस्वस्थ", ["Depression"])],
  src=DP2)
Q("lm_duration", "low_mood", "hopi", 2, "choice", "Since when?", "कब से?", "कधीपासून?", term="Duration", opts=[
    O("lt2w", "Less than 2 weeks (after a sad event?)", "2 हफ़्ते से कम (किसी दुखद घटना के बाद?)", "2 आठवड्यांपेक्षा कमी (दुःखद घटनेनंतर?)", ["Adjustment / grief reaction"]),
    O("2w_6m", "2 weeks to 6 months", "2 हफ़्ते से 6 महीने", "2 आठवडे ते 6 महिने", ["Depression"]),
    O("years", "Years / keeps coming back", "सालों से / बार-बार लौटता", "वर्षानुवर्षे / पुन्हा पुन्हा येते", ["Recurrent depression", "Dysthymia"])],
  src=DP2)
Q("lm_hopeless", "low_mood", "hopi", 3, "yesno", "Feels hopeless about the future?", "क्या भविष्य से कोई उम्मीद नहीं लगती?", "भविष्याबद्दल काहीच आशा वाटत नाही का?",
  term="Hopelessness", pos="Increases suicide risk", ddx=["Depression"], src=SUI)
Q("lm_passive", "low_mood", "redflag", 4, "yesno", "Sometimes wishes not to wake up / life not worth living?", "क्या कभी लगता है कि सुबह न उठें / जीने का कोई मतलब नहीं?",
  "कधी वाटते का की सकाळी उठूच नये / जगण्यात अर्थ नाही?", term="Passive suicidal ideation", rf="Passive death wish — doctor to assess suicide risk today",
  ddx=["Depression"], key="suicide_screen", src=f"{PS}, p111 (Box 8.18)")
Q("lm_active", "low_mood", "redflag", 5, "yesno", "Thoughts of harming yourself or ending your life?", "क्या ख़ुद को नुक़सान पहुँचाने या जान देने के विचार आते हैं?",
  "स्वतःला इजा करण्याचे किंवा जीव देण्याचे विचार येतात का?", term="Active suicidal ideation",
  rf="SUICIDAL THOUGHTS — do not leave patient alone, doctor NOW (Tele-MANAS 14416)", ddx=["Depression"], show={"q": "lm_passive", "eq": "yes"}, src=SUI)
Q("lm_plan", "low_mood", "redflag", 6, "yesno", "Made any plan, or done anything towards it?", "क्या कोई योजना बनाई है या उस तरफ़ कुछ किया है?",
  "काही योजना केली आहे का किंवा त्या दिशेने काही केले आहे का?", term="Suicide plan / preparation",
  rf="SUICIDE PLAN — HIGH RISK: stay with patient, remove dangerous items, doctor immediately", ddx=["Depression"], show={"q": "lm_active", "eq": "yes"}, src=SUI)
Q("lm_risk", "low_mood", "risk", 7, "multi", "Risk factors (Box 8.17)", "जोखिम बढ़ाने वाली बातें", "धोका वाढवणाऱ्या गोष्टी", term="Suicide risk factors", opts=[
    O("past_attempt", "Tried to harm self before", "पहले ख़ुद को नुक़सान पहुँचाने की कोशिश", "आधी स्वतःला इजा करण्याचा प्रयत्न", ["High suicide risk"]),
    O("means_home", "Pesticide / poison / many tablets easily at home (to keep safely away)", "घर में कीटनाशक / ज़हर / बहुत गोलियाँ आसानी से (सुरक्षित हटाने के लिए)", "घरी कीटकनाशक / विष / खूप गोळ्या सहज (सुरक्षित दूर ठेवण्यासाठी)", ["High suicide risk"]),
    O("alone", "Lives alone / recently bereaved / divorced / separated", "अकेले रहते / हाल में किसी की मौत / तलाक़ / अलगाव", "एकटे राहतात / अलीकडे कोणाचा मृत्यू / घटस्फोट / विभक्त", ["High suicide risk"]),
    O("alcohol_drugs", "Alcohol / drugs", "शराब / नशा", "दारू / नशा", ["High suicide risk"]),
    O("pain_illness", "Long painful / disabling illness", "लंबी दर्दनाक / अपंग करने वाली बीमारी", "दीर्घ वेदनादायी / अपंग करणारा आजार", ["High suicide risk"]),
    O("debt_crop", "Debt / crop loss / job loss / exam failure", "कर्ज़ / फ़सल का नुक़सान / नौकरी गई / परीक्षा में फ़ेल", "कर्ज / पीक नुकसान / नोकरी गेली / परीक्षेत नापास", ["High suicide risk"]),
    O("family_suicide", "Suicide in family", "परिवार में आत्महत्या", "कुटुंबात आत्महत्या", ["High suicide risk"])],
  src=SUI)
Q("lm_support", "low_mood", "hopi", 8, "multi", "Support / protective factors", "सहारा", "आधार", term="Protective factors", opts=[
    O("family", "Family / friend to talk to", "बात करने के लिए परिवार / दोस्त", "बोलण्यासाठी कुटुंब / मित्र"),
    O("children", "Responsibility for children", "बच्चों की ज़िम्मेदारी", "मुलांची जबाबदारी"),
    O("faith", "Faith / reasons to live", "आस्था / जीने के कारण", "श्रद्धा / जगण्याची कारणे"),
    O("willing_help", "Willing to take help / treatment", "मदद / इलाज लेने को तैयार", "मदत / उपचार घ्यायला तयार")],
  src=f"{PS}, p106 (Box 8.6)")
Q("lm_causes", "low_mood", "associated", 9, "multi", "Possible contributing causes", "संभावित कारण", "संभाव्य कारणे", term="Contributing factors", opts=[
    O("thyroid", "Thyroid / feeling cold, slow", "थायराइड / ठंड, सुस्ती", "थायरॉईड / थंडी, सुस्ती", ["Hypothyroidism"]),
    O("postpartum", "After delivery (within 1 year)", "डिलीवरी के बाद (1 साल के अंदर)", "प्रसूतीनंतर (1 वर्षाच्या आत)", ["Postnatal depression"], only={"sex": "female"}),
    O("drugs", "Steroids / some BP / acne / TB medicines", "स्टेरॉयड / कुछ बीपी / मुँहासे / टीबी की दवा", "स्टिरॉइड / काही बीपी / मुरुम / टीबी औषधे", ["Drug-induced depression"]),
    O("high_phase", "Times of being very high / overactive before", "पहले कभी बहुत ज़्यादा जोश / अति-सक्रिय", "आधी कधी खूप जास्त उत्साह / अतिसक्रिय", ["Bipolar disorder"]),
    O("stroke_parkinson", "Stroke / Parkinson's / chronic illness", "लकवा / पार्किंसन / पुरानी बीमारी", "पक्षाघात / पार्किन्सन / दीर्घ आजार", ["Depression"]),
    O("abuse_stress", "Stress at home / violence (ask privately)", "घर में तनाव / हिंसा (अकेले में पूछें)", "घरी ताण / हिंसा (एकांतात विचारा)", ["Depression", "Domestic violence"])],
  src=f"{PS}, p102-104")

# ---------------------------------------------------------------- ANXIETY  (Box 8.3-8.4)
AX = f"{PS}, p103 (Box 8.3-8.4)"
Q("ax_pattern", "anxiety", "hopi", 1, "choice", "Pattern", "किस तरह की घबराहट?", "कशा प्रकारची अस्वस्थता?", term="Pattern of anxiety", opts=[
    O("panic", "Sudden attacks of intense fear (10–20 min), feels like dying", "अचानक तेज़ डर के दौरे (10–20 मिनट), मरने जैसा लगे", "अचानक तीव्र भीतीचे झटके (10–20 मिनिटे), मरणार असे वाटते", ["Panic disorder"]),
    O("worry_all", "Worry about everything, most days, for months", "महीनों से हर बात की चिंता, ज़्यादातर दिन", "महिन्यांपासून प्रत्येक गोष्टीची काळजी, बहुतेक दिवस", ["Generalised anxiety disorder"]),
    O("specific", "Fear of specific things (crowds, heights, injections)", "ख़ास चीज़ों का डर (भीड़, ऊँचाई, इंजेक्शन)", "विशिष्ट गोष्टींची भीती (गर्दी, उंची, इंजेक्शन)", ["Phobia"]),
    O("social", "Fear of people judging / speaking in public", "लोगों के सामने बोलने / आँकने का डर", "लोकांसमोर बोलण्याची / मूल्यमापनाची भीती", ["Social anxiety"]),
    O("after_event", "After a frightening event: flashbacks, nightmares", "डरावनी घटना के बाद: बार-बार याद, बुरे सपने", "भीतीदायक घटनेनंतर: पुन्हा आठवण, वाईट स्वप्ने", ["Post-traumatic stress disorder"]),
    O("rituals", "Repeated thoughts / checking / washing", "बार-बार विचार / जाँचना / हाथ धोना", "पुन्हा पुन्हा विचार / तपासणे / हात धुणे", ["Obsessive-compulsive disorder"])],
  src=AX)
Q("ax_somatic", "anxiety", "hopi", 2, "multi", "Body symptoms (Box 8.3)", "शरीर में लक्षण", "शरीरातील लक्षणे", term="Somatic anxiety symptoms", opts=[
    O("palp", "Palpitations", "धड़कन तेज़", "धडधड", ["Panic disorder"]),
    O("breath", "Can't get breath in / fast breathing", "साँस अंदर नहीं जाती / तेज़ साँस", "श्वास आत जात नाही / जलद श्वास", ["Panic disorder"]),
    O("tingling", "Tingling around mouth / fingers", "मुँह / उँगलियों में झुनझुनी", "तोंड / बोटांना मुंग्या", ["Panic disorder"]),
    O("chest", "Chest tightness", "सीने में जकड़न", "छातीत जडपणा", ["Panic disorder"]),
    O("tremor_sweat", "Shaking / sweating", "काँपना / पसीना", "थरथर / घाम", ["Generalised anxiety disorder"]),
    O("stomach", "Butterflies / loose motions / frequent urine", "पेट में घबराहट / दस्त / बार-बार पेशाब", "पोटात गोळा / जुलाब / वारंवार लघवी", ["Generalised anxiety disorder"]),
    O("muscle_head", "Headache / muscle tension", "सिर दर्द / मांसपेशी में तनाव", "डोकेदुखी / स्नायूंत ताण", ["Generalised anxiety disorder"])],
  src=AX)
Q("ax_physical_first", "anxiety", "redflag", 3, "yesno", "First attack ever with chest pain, age over 40, or fainting?", "क्या पहली बार दौरा और सीने में दर्द, उम्र 40+, या बेहोशी?",
  "पहिल्यांदाच झटका आणि छातीत दुखणे, वय 40+, किंवा बेशुद्धी?", term="Exclude physical cause", rf="Do not label as anxiety until heart / sugar / thyroid excluded (ECG)",
  ddx=["Angina / ACS", "Arrhythmia", "Thyrotoxicosis", "Hypoglycaemia"], src=f"{AX}; {H}, Ch 13")
Q("ax_causes", "anxiety", "risk", 4, "multi", "Possible causes", "संभावित कारण", "संभाव्य कारणे", term="Contributors", opts=[
    O("caffeine", "Lots of tea / coffee / energy drinks", "बहुत चाय / कॉफ़ी / एनर्जी ड्रिंक", "खूप चहा / कॉफी / एनर्जी ड्रिंक", ["Caffeine-related anxiety"]),
    O("alcohol_withdraw", "Shaky in the morning after drinking / stopped alcohol", "शराब के बाद सुबह काँपना / शराब छोड़ी", "दारूनंतर सकाळी थरथर / दारू सोडली", ["Alcohol withdrawal"]),
    O("thyroid", "Weight loss, heat intolerance", "वज़न घटना, गर्मी सहन नहीं", "वजन घटणे, उष्णता सहन होत नाही", ["Thyrotoxicosis"]),
    O("inhaler_drugs", "Asthma inhaler / steroids / cold medicines", "दमे का इनहेलर / स्टेरॉयड / सर्दी की दवा", "दम्याचा इनहेलर / स्टिरॉइड / सर्दीचे औषध", ["Drug-induced anxiety"]),
    O("ganja", "Ganja / other drugs", "गांजा / अन्य नशा", "गांजा / इतर नशा", ["Substance-induced anxiety"]),
    O("stress", "Exams / money / family / work stress", "परीक्षा / पैसा / परिवार / काम का तनाव", "परीक्षा / पैसा / कुटुंब / कामाचा ताण", ["Adjustment / grief reaction"])],
  src=AX)
Q("ax_impact", "anxiety", "hopi", 5, "multi", "Effect on life", "ज़िंदगी पर असर", "जीवनावर परिणाम", term="Functional impact", opts=[
    O("avoid", "Avoids going out / places", "बाहर जाना / जगहें टालना", "बाहेर जाणे / ठिकाणे टाळणे"),
    O("work_school", "Affects work / studies", "काम / पढ़ाई पर असर", "काम / अभ्यासावर परिणाम"),
    O("sleep", "Can't sleep", "नींद नहीं", "झोप नाही"),
    O("low_mood", "Also feels low / hopeless", "साथ में उदासी / निराशा", "सोबत उदासी / निराशा", ["Depression"])],
  src=AX)

# ---------------------------------------------------------------- SLEEP
SL = f"{PS}, p102 (Box 8.2); {H}, Ch 12, p172"
Q("sl_type", "sleep", "hopi", 1, "multi", "What is the sleep problem?", "नींद में क्या तकलीफ़?", "झोपेत काय त्रास?", term="Sleep complaint", opts=[
    O("falling", "Can't fall asleep (thoughts racing)", "नींद नहीं आती (विचार चलते रहते)", "झोप लागत नाही (विचार चालू राहतात)", ["Insomnia", "Anxiety / panic"]),
    O("early_wake", "Wakes very early, can't sleep again", "बहुत जल्दी नींद खुलती, फिर नहीं आती", "खूप लवकर जाग येते, पुन्हा झोप नाही", ["Depression"]),
    O("broken", "Wakes many times", "बार-बार नींद टूटती", "वारंवार झोप मोडते", ["Insomnia", "Obstructive sleep apnoea", "Nocturia / prostate"]),
    O("snore_sleepy", "Snores loudly, sleepy all day", "ज़ोर से खर्राटे, दिन भर नींद", "मोठ्याने घोरणे, दिवसभर झोप", ["Obstructive sleep apnoea"]),
    O("legs", "Restless urge to move legs at night", "रात को पैर हिलाने की बेचैनी", "रात्री पाय हलवण्याची अस्वस्थता", ["Restless legs (iron / kidney)"]),
    O("too_much", "Sleeping too much", "बहुत ज़्यादा सोना", "खूप जास्त झोपणे", ["Depression", "Hypothyroidism"]),
    O("no_need", "Doesn't feel need to sleep, full of energy", "नींद की ज़रूरत नहीं लगती, बहुत ऊर्जा", "झोपेची गरज वाटत नाही, खूप ऊर्जा", ["Mania / bipolar disorder"])],
  src=SL)
Q("sl_habits", "sleep", "risk", 2, "multi", "Habits", "आदतें", "सवयी", term="Sleep hygiene", opts=[
    O("screen", "Mobile / TV late at night", "रात को देर तक मोबाइल / टीवी", "रात्री उशिरापर्यंत मोबाईल / टीव्ही", ["Insomnia"]),
    O("tea_evening", "Tea / coffee in evening", "शाम को चाय / कॉफ़ी", "संध्याकाळी चहा / कॉफी", ["Insomnia"]),
    O("shift", "Night shift work", "रात की ड्यूटी", "रात्रपाळी", ["Shift-work sleep disorder"]),
    O("day_naps", "Long day naps", "दिन में लंबी नींद", "दिवसा लांब झोप", ["Insomnia"]),
    O("alcohol_pills", "Alcohol / sleeping pills to sleep", "सोने के लिए शराब / नींद की गोली", "झोपण्यासाठी दारू / झोपेची गोळी", ["Insomnia", "Sedative dependence"])],
  src=SL)
Q("sl_pills", "sleep", "risk", 3, "yesno", "Taking sleeping pills (e.g. alprazolam, clonazepam) daily for more than 4 weeks?", "क्या 4 हफ़्ते से ज़्यादा से रोज़ नींद की गोली (जैसे अल्प्राज़ोलम, क्लोनाज़ेपाम)?",
  "4 आठवड्यांपेक्षा जास्त काळ रोज झोपेची गोळी (उदा. अल्प्राझोलम, क्लोनाझेपाम)?", term="Benzodiazepine dependence risk", ddx=["Sedative dependence"], src="General clinical practice")
Q("sl_body", "sleep", "associated", 4, "multi", "Body causes", "शरीर के कारण", "शरीराची कारणे", term="Medical causes", opts=[
    O("pain", "Pain at night", "रात को दर्द", "रात्री दुखणे", ["Chronic pain"]),
    O("breathless", "Breathless lying flat / cough at night", "लेटने पर साँस फूलना / रात को खाँसी", "झोपल्यावर धाप / रात्री खोकला", ["Heart failure", "Asthma"]),
    O("urine", "Up to pass urine many times", "बार-बार पेशाब के लिए उठना", "वारंवार लघवीसाठी उठणे", ["Nocturia / prostate", "Diabetes"]),
    O("acidity", "Acidity at night", "रात को एसिडिटी", "रात्री ॲसिडिटी", ["Reflux / GORD"]),
    O("hot_flush", "Hot flushes (menopause)", "गर्मी की लहरें (रजोनिवृत्ति)", "उष्णतेच्या लाटा (रजोनिवृत्ती)", ["Menopause"], only={"sex": "female"})],
  src=SL)

# ---------------------------------------------------------------- STRANGE BEHAVIOUR / PSYCHOSIS / MANIA  (Box 8.18-8.23)
BH2 = f"{PS}, p111-115 (Box 8.18-8.23)"
Q("bv_informant", "behaviour", "hopi", 1, "yesno", "History is being taken from family / attendant as well?", "क्या परिवार / साथ वालों से भी जानकारी ली जा रही है?",
  "कुटुंब / सोबत असणाऱ्यांकडूनही माहिती घेतली जात आहे का?", term="Collateral history", src=f"{PS}, p101 (informant)")
Q("bv_features", "behaviour", "hopi", 2, "multi", "What has been noticed?", "क्या देखा गया?", "काय पाहिले?", term="Psychotic / manic features", opts=[
    O("voices", "Hears voices / sees things others don't", "ऐसी आवाज़ें / चीज़ें जो दूसरों को नहीं सुनतीं / दिखतीं", "इतरांना न ऐकू येणारे आवाज / न दिसणाऱ्या गोष्टी", ["Psychosis / schizophrenia", "Delirium (infection / metabolic / drugs)"]),
    O("suspicious", "Feels people are against them / poisoning / following", "लगता है लोग ख़िलाफ़ हैं / ज़हर दे रहे / पीछा कर रहे", "वाटते लोक विरोधात आहेत / विष देत आहेत / पाठलाग करत आहेत", ["Psychosis / schizophrenia"]),
    O("strange_beliefs", "Strange fixed beliefs (special powers, controlled by others)", "अजीब पक्के विश्वास (ख़ास शक्ति, कोई नियंत्रण कर रहा)", "विचित्र पक्के विश्वास (विशेष शक्ती, कोणी नियंत्रित करतो)", ["Psychosis / schizophrenia", "Mania / bipolar disorder"]),
    O("talking_to_self", "Talking / laughing to self", "ख़ुद से बात करना / हँसना", "स्वतःशी बोलणे / हसणे", ["Psychosis / schizophrenia"]),
    O("high_energy", "Very cheerful / irritable, talks fast, little sleep, spends a lot", "बहुत ख़ुश / चिड़चिड़ा, तेज़ बोलना, कम सोना, बहुत ख़र्च", "खूप आनंदी / चिडचिडा, भरभर बोलणे, कमी झोप, खूप खर्च", ["Mania / bipolar disorder"]),
    O("withdrawn", "Withdrawn, not bathing / eating, no emotion", "अलग-थलग, न नहाना / न खाना, भावना नहीं", "एकलकोंडे, आंघोळ / जेवण नाही, भावना नाहीत", ["Psychosis / schizophrenia", "Depression"]),
    O("frozen", "Stays frozen in one position / not speaking", "एक ही स्थिति में जमे रहना / न बोलना", "एकाच स्थितीत गोठलेले / न बोलणे", ["Catatonia"])],
  src=BH2)
Q("bv_danger", "behaviour", "redflag", 3, "yesno", "Violent / threatening, not eating or drinking, frozen, or talking of harming self / others?",
  "क्या हिंसक / धमकी देना, खाना-पीना बंद, जमे रहना, या ख़ुद को / दूसरों को नुक़सान की बात?", "हिंसक / धमकी देणे, खाणे-पिणे बंद, गोठलेले, किंवा स्वतःला / इतरांना इजा करण्याची भाषा?",
  term="Behavioural emergency", rf="Psychiatric emergency (risk to self/others, catatonia, not eating) — doctor NOW, keep safe", ddx=["Psychosis / schizophrenia", "Mania / bipolar disorder", "Catatonia"], src=BH2)
Q("bv_organic", "behaviour", "redflag", 4, "multi", "Could it be a body / brain cause?", "क्या शरीर / दिमाग़ की बीमारी हो सकती है?", "शरीर / मेंदूचा आजार असू शकतो का?", term="Organic red flags", opts=[
    O("sudden_days", "Started suddenly over days", "अचानक कुछ दिनों में शुरू", "अचानक काही दिवसांत सुरू", ["Delirium (infection / metabolic / drugs)", "Meningitis / encephalitis"]),
    O("fever_headache", "Fever / headache / fits", "बुखार / सिर दर्द / दौरा", "ताप / डोकेदुखी / झटके", ["Meningitis / encephalitis"]),
    O("first_over40", "First time after age 40", "40 की उम्र के बाद पहली बार", "40 वयानंतर पहिल्यांदा", ["Intracranial lesion", "Dementia"]),
    O("confused", "Confused about time / place", "समय / जगह को लेकर उलझन", "वेळ / ठिकाणाबद्दल गोंधळ", ["Delirium (infection / metabolic / drugs)"]),
    O("alcohol_stop", "Stopped heavy alcohol 2–3 days ago (shaking, seeing insects)", "2–3 दिन पहले ज़्यादा शराब छोड़ी (काँपना, कीड़े दिखना)", "2–3 दिवसांपूर्वी जास्त दारू सोडली (थरथर, किडे दिसणे)", ["Alcohol withdrawal (delirium tremens)"]),
    O("postpartum", "Within weeks of delivery", "डिलीवरी के कुछ हफ़्तों में", "प्रसूतीनंतर काही आठवड्यांत", ["Postpartum psychosis"], only={"sex": "female"}),
    O("drugs", "Ganja / steroids / new medicine", "गांजा / स्टेरॉयड / नई दवा", "गांजा / स्टिरॉइड / नवीन औषध", ["Substance-induced psychosis"])],
  src=f"{BH2}; {H}, Ch 16")
Q("bv_postpartum_flag", "behaviour", "redflag", 5, "yesno", "Mother within 6 weeks of delivery with confusion, strange beliefs or not sleeping?",
  "क्या डिलीवरी के 6 हफ़्ते के अंदर माँ में उलझन, अजीब विश्वास या नींद नहीं?", "प्रसूतीनंतर 6 आठवड्यांत आईमध्ये गोंधळ, विचित्र विश्वास किंवा झोप नाही?",
  term="Postpartum psychosis", rf="Possible postpartum psychosis — EMERGENCY (risk to mother & baby)", ddx=["Postpartum psychosis"],
  applies={"sex": "female", "min_age": 14, "max_age": 50}, src="General clinical practice")
Q("bv_history", "behaviour", "risk", 6, "multi", "History", "पहले का", "आधीचे", term="Psychiatric history", opts=[
    O("previous_episode", "Similar episode before", "पहले भी ऐसा हुआ", "आधीही असे झाले", ["Psychosis / schizophrenia", "Mania / bipolar disorder"]),
    O("stopped_meds", "Stopped psychiatric medicines", "मानसिक रोग की दवा बंद की", "मानसिक आजाराची औषधे बंद केली", ["Relapse of psychiatric illness"]),
    O("family_mental", "Mental illness in family", "परिवार में मानसिक रोग", "कुटुंबात मानसिक आजार", ["Psychosis / schizophrenia", "Mania / bipolar disorder"]),
    O("faith_healer", "Taken to faith healer / tantrik first", "पहले बाबा / तांत्रिक के पास ले गए", "आधी बाबा / मांत्रिकाकडे नेले", [])],
  src=f"{PS}, p102 (Box 8.1)")

# ---------------------------------------------------------------- ALCOHOL / DRUGS / TOBACCO  (Box 8.8-8.9)
SB = f"{PS}, p106 (Box 8.8-8.9)"
Q("sb_what", "substance", "hopi", 1, "multi", "Which substances?", "कौन-सा नशा?", "कोणता नशा?", term="Substances used", opts=[
    O("alcohol", "Alcohol (desi / country / English)", "शराब (देसी / अंग्रेज़ी)", "दारू (देशी / विदेशी)", ["Alcohol use disorder"]),
    O("tobacco_smoke", "Bidi / cigarette", "बीड़ी / सिगरेट", "बिडी / सिगारेट", ["Tobacco dependence"]),
    O("tobacco_chew", "Gutka / kharra / mawa / khaini", "गुटखा / खर्रा / मावा / खैनी", "गुटखा / खर्रा / मावा / खैनी", ["Tobacco dependence"]),
    O("ganja", "Ganja / bhang / charas", "गांजा / भांग / चरस", "गांजा / भांग / चरस", ["Cannabis use disorder"]),
    O("opioid", "Brown sugar / heroin / opium / cough syrup (codeine)", "ब्राउन शुगर / हेरोइन / अफ़ीम / खाँसी का सिरप", "ब्राऊन शुगर / हेरॉईन / अफू / खोकल्याचे सिरप", ["Opioid use disorder"]),
    O("pills", "Sleeping / pain pills without prescription", "बिना पर्चे नींद / दर्द की गोली", "प्रिस्क्रिप्शनशिवाय झोपेच्या / वेदनेच्या गोळ्या", ["Sedative dependence"]),
    O("inhalant", "Sniffing whitener / glue / petrol (young)", "व्हाइटनर / गोंद / पेट्रोल सूँघना (कम उम्र)", "व्हाइटनर / गोंद / पेट्रोल हुंगणे (कमी वय)", ["Inhalant use disorder"])],
  src=SB)
Q("sb_dependence", "substance", "hopi", 2, "multi", "Signs of dependence (Box 8.9)", "लत के निशान", "व्यसनाची चिन्हे", term="Dependence features", opts=[
    O("craving", "Strong craving", "बहुत तेज़ तलब", "तीव्र ओढ", ["Dependence syndrome"]),
    O("control", "Can't control how much / when", "कितना / कब, नियंत्रण नहीं", "किती / केव्हा, नियंत्रण नाही", ["Dependence syndrome"]),
    O("morning", "Needs it in the morning / to stop shaking", "सुबह / काँपना रोकने के लिए ज़रूरी", "सकाळी / थरथर थांबवण्यासाठी लागते", ["Dependence syndrome"]),
    O("tolerance", "Needs more for same effect", "उतने असर के लिए ज़्यादा चाहिए", "तितक्याच परिणामासाठी जास्त लागते", ["Dependence syndrome"]),
    O("neglect", "Neglecting family / work / money", "परिवार / काम / पैसे की अनदेखी", "कुटुंब / काम / पैसे याकडे दुर्लक्ष", ["Dependence syndrome"]),
    O("blackouts", "Memory blackouts / secret drinking", "याद न रहना / छुपकर पीना", "आठवण न राहणे / लपून पिणे", ["Alcohol use disorder"]),
    O("trouble", "Fights / accidents / drunk driving / police trouble", "झगड़े / एक्सीडेंट / पीकर गाड़ी / पुलिस", "भांडणे / अपघात / पिऊन गाडी / पोलीस", ["Alcohol use disorder"])],
  src=SB)
Q("sb_withdrawal", "substance", "redflag", 3, "yesno", "Stopped / reduced in last days with shaking, sweating, seeing things, confusion or fits?",
  "क्या पिछले दिनों में छोड़ा / कम किया और काँपना, पसीना, चीज़ें दिखना, उलझन या दौरा?", "मागील दिवसांत सोडले / कमी केले आणि थरथर, घाम, गोष्टी दिसणे, गोंधळ किंवा झटके?",
  term="Severe withdrawal", rf="Severe withdrawal / possible delirium tremens — URGENT (thiamine, monitoring)", ddx=["Alcohol withdrawal (delirium tremens)", "Alcohol withdrawal seizure"], src=SB)
Q("sb_inject", "substance", "redflag", 4, "yesno", "Injects drugs / shares needles?", "क्या नस में नशे का इंजेक्शन / सुई साझा करना?", "नसेतून नशेचे इंजेक्शन / सुई वाटून घेणे?",
  term="Injecting drug use", rf="Injecting drug use — test HIV / hepatitis B & C, check abscess / endocarditis", ddx=["HIV", "Hepatitis", "Infective endocarditis"], src="General clinical practice")
Q("sb_amount", "substance", "hopi", 5, "text", "How much per day / week and since how many years?", "रोज़ / हफ़्ते में कितना और कितने साल से?", "रोज / आठवड्याला किती आणि किती वर्षांपासून?",
  term="Quantity and duration", src=f"{PS}, p106; {H}, Ch 1, p10 (Box 1.12)")
Q("sb_complications", "substance", "associated", 6, "multi", "Health problems already", "पहले से सेहत की तकलीफ़", "आधीच आरोग्याचा त्रास", term="Complications", opts=[
    O("liver", "Liver / jaundice / belly swelling", "लिवर / पीलिया / पेट फूलना", "यकृत / कावीळ / पोट फुगणे", ["Alcoholic liver disease"]),
    O("vomit_blood", "Vomiting blood", "ख़ून की उल्टी", "रक्ताची उलटी", ["Varices", "Mallory-Weiss tear"]),
    O("numb_feet", "Numb feet / unsteady", "पैर सुन्न / लड़खड़ाहट", "पाय बधिर / डगमग", ["Peripheral neuropathy (diabetes / B12 / alcohol)"]),
    O("memory", "Memory problems", "याददाश्त कमज़ोर", "स्मरणशक्ती कमजोर", ["Wernicke's encephalopathy"]),
    O("mouth_patch", "Mouth patch / ulcer (tobacco)", "मुँह में धब्बा / छाला (तंबाकू)", "तोंडात डाग / फोड (तंबाखू)", ["Oral cancer"]),
    O("cough_breath", "Cough / breathlessness (smoking)", "खाँसी / साँस फूलना (धूम्रपान)", "खोकला / धाप (धूम्रपान)", ["COPD"])],
  src=SB)
Q("sb_motivation", "substance", "hopi", 7, "choice", "Wants to stop?", "क्या छोड़ना चाहते हैं?", "सोडायचे आहे का?", term="Readiness to change", opts=[
    O("ready", "Yes, ready now", "हाँ, अभी तैयार", "हो, आता तयार"),
    O("thinking", "Thinking about it", "सोच रहे हैं", "विचार करत आहेत"),
    O("no", "Not now", "अभी नहीं", "आता नाही"),
    O("tried", "Tried before and failed", "पहले कोशिश की, नहीं हुआ", "आधी प्रयत्न केला, जमले नाही")],
  src=f"{PS}, p106")
