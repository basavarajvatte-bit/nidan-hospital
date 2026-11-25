# ====================================================================== SYSTEM 2: RESPIRATORY
# Hutchison 24e, Ch 12 (Respiratory system), p167-172; Box 12.1-12.8, 12.17. Executed inside hx_bank.py.

RS = f"{H}, Ch 12"

C("haemoptysis", "Respiratory", "Coughing up blood", "खाँसी में खून", "खोकल्यातून रक्त", "🩸", 21, f"{RS}, p168-169 (Box 12.6)")
C("wheeze", "Respiratory", "Wheezing / asthma attack", "सीटी जैसी साँस / दमे का दौरा", "शिट्टीसारखा श्वास / दम्याचा झटका", "🌬️", 22, f"{RS}, p167-169")
C("snoring", "Respiratory", "Loud snoring / daytime sleepiness", "ज़ोर के खर्राटे / दिन में नींद", "मोठे घोरणे / दिवसा झोप", "😴", 23, f"{RS}, p172")

# ---------------------------------------------------------------- COUGH (refined, Box 12.5)
Q("co_onset_cold", "cough", "hopi", 12, "yesno", "Did the cough start after a cold / sore throat / viral fever?",
  "क्या खाँसी सर्दी-ज़ुकाम, गले की ख़राश या वायरल बुखार के बाद शुरू हुई?", "खोकला सर्दी, घसा खवखवणे किंवा व्हायरल तापानंतर सुरू झाला का?",
  term="Preceding URTI", ddx=["Post-viral cough", "Acute respiratory infection"], src=f"{RS}, p168 (Box 12.5)")
Q("co_sputum_amt", "cough", "hopi", 13, "choice", "How much phlegm in a day?", "दिन भर में कितना बलगम?", "दिवसभरात किती कफ?", term="Sputum volume",
  show={"q": "co_sputum", "in": ["white", "yellow_green", "large_daily"]}, opts=[
      O("little", "A little (spoonful)", "थोड़ा (चम्मच भर)", "थोडा (चमचाभर)"),
      O("cup", "About half a cup or more", "आधा कप या ज़्यादा", "अर्धा कप किंवा जास्त", ["Bronchiectasis", "Lung abscess"])],
  src=f"{RS}, p168, p179 (Box 12.17)")
Q("co_smell", "cough", "associated", 14, "yesno", "Foul-smelling phlegm or bad taste?", "क्या बलगम से बदबू आती है या मुँह का स्वाद ख़राब?",
  "कफाला दुर्गंधी येते का किंवा तोंडाची चव खराब?", term="Foul-smelling sputum", ddx=["Lung abscess", "Bronchiectasis"],
  show={"q": "co_sputum", "in": ["yellow_green", "large_daily"]}, src=f"{RS}, p179")
Q("co_rusty", "cough", "associated", 15, "yesno", "Rusty / brown phlegm with fever and chest pain on breathing?",
  "क्या ज़ंग जैसा भूरा बलगम, बुखार और साँस लेने पर सीने में दर्द?", "गंजासारखा तपकिरी कफ, ताप आणि श्वास घेताना छातीत दुखणे?",
  term="Rusty sputum / pleuritic pain", ddx=["Pneumonia"], src=f"{RS}, p169, p179 (Box 12.17)")
Q("co_triggers", "cough", "hopi", 16, "multi", "What makes the cough worse?", "किससे खाँसी बढ़ती है?", "कशाने खोकला वाढतो?", term="Triggers", opts=[
    O("dust_smoke", "Dust / smoke / strong smells", "धूल / धुआँ / तेज़ गंध", "धूळ / धूर / उग्र वास", ["Asthma", "Allergic rhinitis"]),
    O("cold_air", "Cold air / weather change", "ठंडी हवा / मौसम बदलना", "थंड हवा / हवामान बदल", ["Asthma"]),
    O("exercise", "Exercise / running", "दौड़ना / कसरत", "धावणे / व्यायाम", ["Asthma"]),
    O("after_meals", "After meals / lying down", "खाने के बाद / लेटने पर", "जेवणानंतर / झोपल्यावर", ["Reflux / GORD"]),
    O("talking", "Talking / laughing", "बोलने / हँसने पर", "बोलताना / हसताना", ["Post-nasal drip"]),
    O("work", "At work, better on holidays", "काम पर, छुट्टी में ठीक", "कामावर, सुट्टीत बरे", ["Occupational asthma"])],
  src=f"{RS}, p168-170 (Box 12.5, 12.7)")
Q("co_breathless", "cough", "associated", 17, "yesno", "Breathless with the cough?", "क्या खाँसी के साथ साँस फूलती है?", "खोकल्यासोबत धाप लागते का?",
  term="Associated dyspnoea", ddx=["Asthma", "COPD", "Pneumonia", "Heart failure", "Interstitial lung disease"], key="dyspnoea", src=f"{RS}, p168 (Box 12.5)")
Q("co_wheeze", "cough", "associated", 18, "yesno", "Whistling / wheezing sound in chest?", "क्या छाती से सीटी जैसी आवाज़ आती है?",
  "छातीतून शिट्टीसारखा आवाज येतो का?", term="Wheeze", ddx=["Asthma", "COPD"], key="wheeze", src=f"{RS}, p169")
Q("co_tb_prev", "cough", "risk", 19, "choice", "TB treatment before?", "क्या पहले टीबी की दवा (6 महीने वाली) चली थी?", "आधी टीबीचे औषध (6 महिन्यांचे) घेतले होते का?",
  term="Previous anti-TB treatment", key="tb_treatment", opts=[
      O("never", "Never", "कभी नहीं", "कधीच नाही"),
      O("completed", "Yes, completed full course", "हाँ, पूरा कोर्स किया", "हो, पूर्ण कोर्स केला", ["Post-TB bronchiectasis", "Tuberculosis"]),
      O("incomplete", "Yes, but stopped in between", "हाँ, बीच में छोड़ दी", "हो, मध्येच सोडले", ["Tuberculosis", "Drug-resistant TB"])],
  src=f"{H}, Ch 10, p146")
Q("co_hiv_dm", "cough", "risk", 20, "multi", "Conditions that lower immunity", "इनमें से कुछ है?", "यापैकी काही आहे का?", term="Immunosuppression", opts=[
    O("dm", "Diabetes", "शुगर", "मधुमेह", ["Tuberculosis", "Pneumonia"]),
    O("hiv", "HIV", "एचआईवी", "एचआयव्ही", ["Tuberculosis", "Pneumonia"]),
    O("steroid", "Steroids / cancer medicines", "स्टेरॉयड / कैंसर की दवा", "स्टिरॉइड / कर्करोग औषधे", ["Tuberculosis", "Pneumonia"]),
    O("malnut", "Very thin / poor diet", "बहुत दुबला / खाना कम", "खूप कृश / आहार कमी", ["Tuberculosis"])],
  src=f"{H}, Ch 10, p146; Ch 9, p122")
Q("co_lungca", "cough", "redflag", 21, "yesno", "Smoker over 40 with cough changed recently, weight loss or hoarse voice?",
  "क्या 40 से ज़्यादा उम्र के धूम्रपान करने वाले में खाँसी बदली है, वज़न घटा या आवाज़ बैठी?",
  "40 पेक्षा जास्त वयाच्या धूम्रपान करणाऱ्याचा खोकला बदलला, वजन घटले किंवा आवाज बसला?",
  term="Lung cancer red flags", rf="Possible lung cancer — chest X-ray needed", ddx=["Lung cancer"], applies={"min_age": 40}, src=f"{RS}, p167-169")

# ---------------------------------------------------------------- BREATHLESSNESS: respiratory branch
Q("br_fever", "breathless", "associated", 41, "yesno", "Fever, cough with phlegm along with breathlessness?", "क्या साँस फूलने के साथ बुखार और बलगम वाली खाँसी?",
  "धापेसोबत ताप आणि कफाचा खोकला?", term="Infective features", ddx=["Pneumonia", "COPD"], src=f"{RS}, p168 (Box 12.1)")
Q("br_pleuritic", "breathless", "associated", 42, "yesno", "Sharp chest pain on one side when breathing in?", "क्या साँस अंदर लेते समय एक तरफ सीने में चुभन वाला दर्द?",
  "श्वास आत घेताना एका बाजूला छातीत टोचल्यासारखे दुखते का?", term="Pleuritic chest pain",
  ddx=["Pneumonia", "Pulmonary embolism", "Pneumothorax", "Pleurisy"], src=f"{RS}, p169")
Q("br_allergy", "breathless", "associated", 43, "yesno", "Sneezing, itchy eyes/nose, or allergy since childhood?", "क्या छींकें, आँख/नाक में खुजली या बचपन से एलर्जी?",
  "शिंका, डोळे/नाक खाजणे किंवा लहानपणापासून ॲलर्जी?", term="Atopy", ddx=["Asthma", "Allergic rhinitis"], key="atopy", src=f"{RS}, p169")
Q("br_ild", "breathless", "associated", 44, "yesno", "Dry cough with slowly worsening breathlessness over months?", "क्या सूखी खाँसी के साथ महीनों से धीरे-धीरे बढ़ती साँस की तकलीफ़?",
  "कोरड्या खोकल्यासोबत महिन्यांपासून हळूहळू वाढणारी धाप?", term="Progressive dry cough + dyspnoea", ddx=["Interstitial lung disease"],
  show={"q": "br_onset", "in": ["months"]}, src=f"{RS}, p168 (Box 12.1)")
Q("br_severe_hx", "breathless", "risk", 45, "multi", "Past severe attacks", "पहले कितनी गंभीर तकलीफ़ हुई है?", "आधी किती गंभीर त्रास झाला आहे?",
  term="Severity history", opts=[
      O("admit", "Admitted for breathing", "साँस के लिए भर्ती हुए", "श्वासासाठी भरती झाले", ["Asthma", "COPD"]),
      O("icu", "ICU / ventilator", "आईसीयू / वेंटिलेटर", "आयसीयू / व्हेंटिलेटर", ["Asthma", "COPD"]),
      O("home_o2", "Oxygen at home", "घर पर ऑक्सीजन", "घरी ऑक्सिजन", ["COPD", "Interstitial lung disease"]),
      O("steroid_tabs", "Steroid tablets often", "अक्सर स्टेरॉयड की गोली", "वारंवार स्टिरॉइड गोळ्या", ["Asthma", "COPD"])],
  src=f"{RS}, p167-168")
Q("br_inhaler", "breathless", "risk", 46, "choice", "Uses an inhaler / pump?", "क्या इनहेलर / पंप लेते हैं?", "इनहेलर / पंप घेता का?", term="Inhaler use", key="inhaler", opts=[
    O("no", "No", "नहीं", "नाही"),
    O("sometimes", "Sometimes", "कभी-कभी", "कधी कधी", ["Asthma"]),
    O("daily", "Daily", "रोज़", "रोज", ["Asthma", "COPD"]),
    O("many_times", "Many times a day / not helping", "दिन में कई बार / असर नहीं", "दिवसातून अनेकदा / उपयोग होत नाही", ["Asthma", "COPD"])],
  src=f"{RS}, p169")
Q("br_occup_list", "breathless", "risk", 47, "multi", "Work exposures (now or before)", "काम में इनमें से किसके संपर्क में रहे?", "कामात यापैकी कशाच्या संपर्कात होता?",
  term="Occupational exposure", opts=[
      O("stone_dust", "Stone / quarry / mining dust", "पत्थर / खदान की धूल", "दगड / खाण धूळ", ["Silicosis", "Interstitial lung disease"]),
      O("asbestos", "Asbestos sheets / construction / brake lining", "एस्बेस्टस शीट / निर्माण / ब्रेक लाइनिंग", "ॲस्बेस्टॉस पत्रे / बांधकाम / ब्रेक लायनिंग", ["Asbestosis / mesothelioma"]),
      O("cotton", "Cotton mill / textile", "कपास मिल / कपड़ा कारखाना", "कापूस गिरणी / कापड कारखाना", ["Byssinosis", "Occupational asthma"]),
      O("farm", "Farming / hay / grain / birds", "खेती / भूसा / अनाज / पक्षी", "शेती / भुसा / धान्य / पक्षी", ["Hypersensitivity pneumonitis", "Occupational asthma"]),
      O("paint_chem", "Paint spraying / chemicals", "पेंट स्प्रे / केमिकल", "पेंट स्प्रे / रसायने", ["Occupational asthma"]),
      O("bakery", "Bakery / flour", "बेकरी / आटा", "बेकरी / पीठ", ["Occupational asthma"]),
      O("chulha", "Wood / cow-dung chulha cooking", "लकड़ी / उपले का चूल्हा", "लाकूड / शेणाची चूल", ["COPD"])],
  src=f"{RS}, p170 (Box 12.7, 12.8)")

# ---------------------------------------------------------------- HAEMOPTYSIS  (Box 12.6, p168-169)
HM = f"{RS}, p168-169 (Box 12.6)"
Q("hm_amount", "haemoptysis", "redflag", 1, "choice", "How much blood?", "कितना खून आया?", "किती रक्त आले?", term="Volume of haemoptysis", opts=[
    O("streaks", "Streaks in phlegm", "बलगम में धागे जैसा", "कफात धाग्यासारखे", ["Bronchitis", "Tuberculosis", "Lung cancer"]),
    O("spoon", "About a spoonful", "करीब एक चम्मच", "सुमारे एक चमचा", ["Tuberculosis", "Bronchiectasis", "Lung cancer"]),
    O("cup", "Cupful or more / keeps coming", "कप भर या ज़्यादा / लगातार", "कपभर किंवा जास्त / सतत", ["Massive haemoptysis"])],
  src=HM)
Q("hm_massive", "haemoptysis", "redflag", 2, "yesno", "Cupful of blood or more, or breathless while coughing blood?",
  "क्या कप भर से ज़्यादा खून या खून के साथ साँस फूल रही है?", "कपभरापेक्षा जास्त रक्त किंवा रक्तासोबत धाप?",
  term="Massive haemoptysis", rf="Massive haemoptysis — EMERGENCY (airway risk)", ddx=["Massive haemoptysis"], src=HM)
Q("hm_source", "haemoptysis", "hopi", 3, "choice", "Where does the blood seem to come from?", "खून कहाँ से आता लगता है?", "रक्त कुठून येते असे वाटते?",
  term="Source (true haemoptysis vs mimics)", opts=[
      O("cough", "Comes up with cough, frothy, bright red", "खाँसी के साथ, झागदार, चमकीला लाल", "खोकल्यासोबत, फेसाळ, चमकदार लाल", ["Tuberculosis", "Lung cancer", "Bronchiectasis"]),
      O("vomit", "With vomiting, dark / coffee-coloured", "उल्टी के साथ, गहरा / कॉफ़ी रंग", "उलटीसोबत, गडद / कॉफी रंग", ["Upper GI bleed (haematemesis)"]),
      O("nose_gums", "From nose / gums, then spat out", "नाक / मसूड़ों से, फिर थूका", "नाक / हिरड्यांतून, मग थुंकले", ["Epistaxis / gum bleeding"])],
  src=f"{RS}, p169")
Q("hm_duration", "haemoptysis", "hopi", 4, "choice", "Since when?", "कब से?", "कधीपासून?", term="Duration", opts=[
    O("once", "Only once", "सिर्फ़ एक बार", "फक्त एकदा"),
    O("days", "Few days, with fever/cold", "कुछ दिन, बुखार/सर्दी के साथ", "काही दिवस, ताप/सर्दीसोबत", ["Bronchitis", "Pneumonia"]),
    O("weeks", "On and off for weeks / months", "हफ़्तों / महीनों से रुक-रुक कर", "आठवडे / महिने अधूनमधून", ["Tuberculosis", "Lung cancer", "Bronchiectasis"])],
  src=HM)
Q("hm_tb", "haemoptysis", "associated", 5, "yesno", "Evening fever, weight loss, night sweats, cough >2 weeks?",
  "क्या शाम को बुखार, वज़न घटना, रात को पसीना, 2 हफ़्ते से ज़्यादा खाँसी?", "संध्याकाळी ताप, वजन घटणे, रात्री घाम, 2 आठवड्यांपेक्षा जास्त खोकला?",
  term="TB symptoms", ddx=["Tuberculosis", "Lung cancer"], key="wt_loss", src=f"{H}, Ch 10, p146")
Q("hm_pe", "haemoptysis", "redflag", 6, "yesno", "Sudden breathlessness / chest pain, or swollen painful leg?",
  "क्या अचानक साँस फूलना / सीने में दर्द, या पैर में सूजन-दर्द?", "अचानक धाप / छातीत दुखणे, किंवा पायाला सूज-दुखणे?",
  term="PE features", rf="Haemoptysis with PE features — urgent", ddx=["Pulmonary embolism"], src=f"{H}, Ch 13, p192 (Box 13.8)")
Q("hm_bleeding", "haemoptysis", "risk", 7, "multi", "Bleeding risk", "इनमें से कुछ?", "यापैकी काही?", term="Bleeding risk", opts=[
    O("thinner", "Blood thinner (warfarin, etc.)", "खून पतला करने की दवा", "रक्त पातळ करण्याचे औषध", ["Anticoagulant-related bleeding"]),
    O("easy_bruise", "Easy bruising / bleeding elsewhere", "आसानी से नील पड़ना / दूसरी जगह से खून", "सहज काळे-निळे पडणे / इतर ठिकाणी रक्त", ["Bleeding disorder"]),
    O("valve", "Heart valve disease", "दिल के वाल्व की बीमारी", "हृदयाच्या झडपेचा आजार", ["Mitral stenosis"])],
  src=HM)
Q("hm_tb_prev", "haemoptysis", "risk", 8, "choice", "TB treatment before?", "क्या पहले टीबी की दवा चली थी?", "आधी टीबीचे औषध घेतले होते का?",
  term="Previous anti-TB treatment", key="tb_treatment", opts=[
      O("never", "Never", "कभी नहीं", "कधीच नाही"),
      O("completed", "Yes, completed", "हाँ, पूरा कोर्स", "हो, पूर्ण", ["Post-TB bronchiectasis", "Aspergilloma"]),
      O("incomplete", "Yes, stopped in between", "हाँ, बीच में छोड़ी", "हो, मध्येच सोडले", ["Tuberculosis", "Drug-resistant TB"])],
  src=f"{H}, Ch 10, p146")
Q("hm_smoke", "haemoptysis", "risk", 9, "yesno", "Smoker now or before (bidi/cigarette)?", "क्या बीड़ी/सिगरेट पीते हैं या पीते थे?", "बिडी/सिगारेट ओढता किंवा ओढत होता?",
  term="Smoking", ddx=["Lung cancer"], key="smoking", src=f"{RS}, p169")

# ---------------------------------------------------------------- WHEEZE / ASTHMA ATTACK
WZ = f"{RS}, p167-169"
Q("wz_severe", "wheeze", "redflag", 1, "yesno", "Can't speak full sentences, drowsy, or lips blue?", "क्या पूरा वाक्य नहीं बोल पा रहे, सुस्ती, या होंठ नीले?",
  "पूर्ण वाक्य बोलता येत नाही, गुंगी, किंवा ओठ निळे?", term="Life-threatening asthma features", rf="Severe / life-threatening asthma — EMERGENCY",
  ddx=["Asthma"], src=f"{RS}, p171")
Q("wz_stridor", "wheeze", "redflag", 2, "yesno", "Noisy breathing IN (harsh sound from throat), or something swallowed/choked?",
  "क्या साँस अंदर लेते समय गले से कर्कश आवाज़, या कुछ निगल लिया / अटक गया?", "श्वास आत घेताना घशातून कर्कश आवाज, किंवा काही गिळले / अडकले?",
  term="Stridor / foreign body", rf="Stridor — upper airway obstruction (EMERGENCY)", ddx=["Upper airway obstruction / foreign body"], src=f"{RS}, p169; Ch 21")
Q("wz_pattern", "wheeze", "hopi", 3, "choice", "Pattern", "तकलीफ़ कैसी है?", "त्रास कसा आहे?", term="Pattern of wheeze", opts=[
    O("episodic", "Comes in attacks, normal in between", "दौरे में आती है, बीच में ठीक", "झटक्यांत येतो, मधे बरे", ["Asthma"]),
    O("daily_progressive", "Every day, slowly worsening over years", "रोज़, सालों में धीरे-धीरे बढ़ती", "रोज, वर्षांत हळूहळू वाढणारी", ["COPD"]),
    O("first_time", "First time ever", "पहली बार", "पहिल्यांदा", ["Asthma", "Heart failure", "Anaphylaxis", "Upper airway obstruction / foreign body"])],
  src=f"{RS}, p167")
Q("wz_night", "wheeze", "hopi", 4, "yesno", "Worse at night / early morning?", "क्या रात या सुबह-सुबह ज़्यादा?", "रात्री किंवा पहाटे जास्त?",
  term="Nocturnal symptoms", ddx=["Asthma"], src=f"{RS}, p167")
Q("wz_childhood", "wheeze", "risk", 5, "yesno", "Asthma / allergy / eczema since childhood, or in family?", "क्या बचपन से दमा/एलर्जी/एक्ज़िमा, या परिवार में?",
  "लहानपणापासून दमा/ॲलर्जी/एक्झिमा, किंवा कुटुंबात?", term="Atopy / family history", ddx=["Asthma"], key="atopy", src=f"{RS}, p169")
Q("wz_triggers", "wheeze", "hopi", 6, "multi", "Triggers", "किससे शुरू होता है?", "कशामुळे सुरू होतो?", term="Triggers", opts=[
    O("cold", "Cold / viral infection", "सर्दी / वायरल", "सर्दी / व्हायरल", ["Asthma", "COPD"]),
    O("dust", "Dust / pollen / smoke", "धूल / पराग / धुआँ", "धूळ / परागकण / धूर", ["Asthma"]),
    O("exercise", "Exercise", "कसरत", "व्यायाम", ["Asthma"]),
    O("pets", "Pets / birds", "पालतू जानवर / पक्षी", "पाळीव प्राणी / पक्षी", ["Asthma"]),
    O("painkiller", "Aspirin / painkillers", "एस्पिरिन / दर्द की गोली", "ॲस्पिरिन / वेदनाशामक", ["Aspirin-sensitive asthma"]),
    O("bp_tablet", "BP tablets like propranolol / atenolol", "बीपी की गोली (प्रोप्रानोलोल / एटेनोलोल)", "बीपीची गोळी (प्रोप्रानोलॉल / एटेनोलॉल)", ["Beta-blocker induced bronchospasm"]),
    O("food_sting", "New food / insect sting with swelling/rash", "नया खाना / कीड़ा काटना, सूजन/दाने के साथ", "नवीन अन्न / किडा चावणे, सूज/पुरळसोबत", ["Anaphylaxis"])],
  src=f"{RS}, p167-170")
Q("wz_reliever", "wheeze", "hopi", 7, "choice", "Reliever inhaler (blue pump) use this week", "इस हफ़्ते कितनी बार पंप (इनहेलर) लेना पड़ा?",
  "या आठवड्यात किती वेळा पंप (इनहेलर) घ्यावा लागला?", term="Reliever use", key="inhaler", opts=[
      O("none", "Not using", "नहीं लेते", "घेत नाही"),
      O("lt2", "Up to 2 times", "2 बार तक", "2 वेळा पर्यंत"),
      O("daily", "Daily", "रोज़", "रोज", ["Asthma"]),
      O("no_relief", "Many times, not helping", "कई बार, असर नहीं", "अनेकदा, उपयोग नाही", ["Asthma"])],
  src=f"{RS}, p169")
Q("wz_smoke", "wheeze", "risk", 8, "yesno", "Smoker now or before (bidi/cigarette/chulha smoke)?",
  "क्या बीड़ी/सिगरेट पीते हैं या पहले पीते थे (या चूल्हे का धुआँ)?", "बिडी/सिगारेट ओढता का किंवा आधी ओढत होता (किंवा चुलीचा धूर)?",
  term="Smoking / biomass exposure", ddx=["COPD"], key="smoking", src=f"{RS}, p169-170")
Q("wz_cardiac", "wheeze", "associated", 9, "yesno", "Swollen ankles / breathless lying flat / heart disease?", "क्या पैरों में सूजन / लेटने पर साँस फूलना / दिल की बीमारी?",
  "पायांना सूज / झोपल्यावर धाप / हृदयरोग?", term="Cardiac features ('cardiac asthma')", ddx=["Heart failure"], src=f"{H}, Ch 13, p193")

# ---------------------------------------------------------------- SNORING / SLEEPINESS  (p172)
SA = f"{RS}, p172"
Q("sa_apnoea", "snoring", "hopi", 1, "yesno", "Partner noticed breathing stops / choking during sleep?", "क्या साथ सोने वाले ने देखा कि नींद में साँस रुकती / घुटती है?",
  "सोबत झोपणाऱ्याने पाहिले का की झोपेत श्वास थांबतो / गुदमरतो?", term="Witnessed apnoeas", ddx=["Obstructive sleep apnoea"], src=SA)
Q("sa_sleepy", "snoring", "hopi", 2, "yesno", "Falls asleep in the day while sitting, reading, or watching TV?", "क्या दिन में बैठे-बैठे, पढ़ते या टीवी देखते सो जाते हैं?",
  "दिवसा बसल्या बसल्या, वाचताना किंवा टीव्ही पाहताना झोप लागते का?", term="Daytime somnolence", ddx=["Obstructive sleep apnoea"], src=SA)
Q("sa_driving", "snoring", "redflag", 3, "yesno", "Drives a vehicle and feels sleepy while driving?", "क्या गाड़ी चलाते हैं और चलाते समय नींद आती है?",
  "गाडी चालवता आणि चालवताना झोप येते का?", term="Sleepiness while driving", rf="Sleepy driver — road safety risk, advise not to drive until assessed",
  ddx=["Obstructive sleep apnoea"], src=SA)
Q("sa_morning", "snoring", "associated", 4, "yesno", "Morning headache, dry mouth, poor concentration?", "क्या सुबह सिर दर्द, मुँह सूखना, ध्यान न लगना?",
  "सकाळी डोकेदुखी, तोंड कोरडे, लक्ष न लागणे?", term="Morning symptoms", ddx=["Obstructive sleep apnoea"], src=SA)
Q("sa_risk", "snoring", "risk", 5, "multi", "Risk factors", "इनमें से कुछ?", "यापैकी काही?", term="OSA risk factors", opts=[
    O("obese", "Overweight / thick neck", "मोटापा / मोटी गर्दन", "लठ्ठपणा / जाड मान", ["Obstructive sleep apnoea"]),
    O("htn", "High BP (hard to control)", "हाई बीपी (कंट्रोल नहीं)", "उच्च रक्तदाब (नियंत्रणात नाही)", ["Obstructive sleep apnoea"]),
    O("alcohol_night", "Alcohol / sleeping pills at night", "रात को शराब / नींद की गोली", "रात्री दारू / झोपेची गोळी", ["Obstructive sleep apnoea"]),
    O("hypothyroid", "Thyroid (low)", "थायराइड (कम)", "थायरॉईड (कमी)", ["Hypothyroidism"]),
    O("tonsils", "Big tonsils / blocked nose (child)", "बड़े टॉन्सिल / नाक बंद (बच्चा)", "मोठे टॉन्सिल / नाक बंद (मूल)", ["Adenotonsillar hypertrophy"])],
  src=SA)
