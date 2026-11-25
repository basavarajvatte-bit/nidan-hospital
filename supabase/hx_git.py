# ====================================================================== SYSTEM 3: GASTROINTESTINAL + HEPATOBILIARY
# Hutchison 24e, Ch 14 (Gastrointestinal system), p241-245; Box 14.1-14.2, Tables 14.1-14.2. Executed inside hx_bank.py.

GI = f"{H}, Ch 14"

C("dysphagia", "Gastrointestinal", "Difficulty swallowing", "निगलने में तकलीफ़", "गिळायला त्रास", "🥄", 31, f"{GI}, p241")
C("dyspepsia", "Gastrointestinal", "Acidity / heartburn / indigestion", "एसिडिटी / सीने में जलन / अपच", "ॲसिडिटी / छातीत जळजळ / अपचन", "🔥", 32, f"{GI}, p241-242")
C("gi_bleed", "Gastrointestinal", "Blood in vomit / stool, black stool", "खून की उल्टी / मल में खून / काला मल", "रक्ताची उलटी / शौचात रक्त / काळी शौच", "🩸", 33, f"{GI}, p242-243")
C("bowel_change", "Gastrointestinal", "Constipation / change in bowel habit", "कब्ज़ / पाखाने में बदलाव", "बद्धकोष्ठता / शौचात बदल", "🧻", 34, f"{GI}, p242")
C("abd_swelling", "Gastrointestinal", "Belly swelling", "पेट फूलना / पेट में सूजन", "पोट फुगणे / पोटाला सूज", "🫃", 35, f"{GI}, p242")
C("weight_loss", "Gastrointestinal", "Weight loss / poor appetite", "वज़न घटना / भूख न लगना", "वजन घटणे / भूक न लागणे", "⚖️", 36, f"{GI}, p242-243")
C("jaundice", "Hepatobiliary", "Jaundice (yellow eyes)", "पीलिया (आँखें पीली)", "कावीळ (डोळे पिवळे)", "🟡", 37, f"{GI}, p243")

ALARM = [O("wt_loss", "Weight loss", "वज़न घटना", "वजन घटणे", ["GI malignancy"]),
         O("dysphagia", "Food sticking", "खाना अटकना", "अन्न अडकणे", ["Oesophageal cancer / stricture"]),
         O("vomit_persist", "Vomiting persistently", "लगातार उल्टी", "सतत उलटी", ["Gastric outlet obstruction", "GI malignancy"]),
         O("black_stool", "Black stools / blood vomit", "काला मल / खून की उल्टी", "काळी शौच / रक्ताची उलटी", ["Peptic ulcer / gastritis", "GI malignancy"]),
         O("anaemia", "Pale / tired (anaemia)", "पीला पड़ना / थकान", "फिकट / थकवा", ["GI malignancy", "Occult GI bleeding"]),
         O("lump", "Lump in belly", "पेट में गाँठ", "पोटात गाठ", ["GI malignancy"])]

# ---------------------------------------------------------------- DYSPHAGIA  (p241)
DY = f"{GI}, p241"
Q("dy_level", "dysphagia", "hopi", 1, "choice", "Where does food stick?", "खाना कहाँ अटकता है?", "अन्न कुठे अडकते?", term="Level", opts=[
    O("throat", "In the throat (coughs/chokes when swallowing)", "गले में (निगलते समय खाँसी / ठसका)", "घशात (गिळताना खोकला / ठसका)", ["Neurological (oropharyngeal) dysphagia"]),
    O("chest", "Behind the breastbone / lower chest", "छाती की हड्डी के पीछे / नीचे", "छातीच्या हाडामागे / खाली", ["Oesophageal cancer / stricture", "Achalasia", "Reflux / GORD"])],
  src=DY)
Q("dy_solids", "dysphagia", "hopi", 2, "choice", "Difficulty with", "किसमें तकलीफ़ है?", "कशात त्रास आहे?", term="Solids vs liquids", opts=[
    O("solids_then_liquids", "Solids first, now even liquids", "पहले ठोस, अब पानी भी", "आधी घन, आता पाणीसुद्धा", ["Oesophageal cancer / stricture"]),
    O("solids", "Only solids", "सिर्फ़ ठोस खाना", "फक्त घन अन्न", ["Oesophageal cancer / stricture", "Benign stricture / ring"]),
    O("both_start", "Both solids and liquids from the start", "शुरू से ठोस और पानी दोनों", "सुरुवातीपासून घन व पाणी दोन्ही", ["Achalasia", "Neurological (oropharyngeal) dysphagia"]),
    O("liquids_more", "Liquids more than solids", "पानी ज़्यादा मुश्किल", "पाणी जास्त कठीण", ["Neurological (oropharyngeal) dysphagia"])],
  src=DY)
Q("dy_progressive", "dysphagia", "redflag", 3, "yesno", "Getting worse over weeks with weight loss?", "क्या हफ़्तों में बढ़ रही है और वज़न घटा है?",
  "आठवड्यांत वाढत आहे आणि वजन घटले आहे का?", term="Progressive dysphagia with weight loss", rf="Progressive dysphagia + weight loss — exclude oesophageal cancer (endoscopy)",
  ddx=["Oesophageal cancer / stricture"], key="wt_loss", src=DY)
Q("dy_pain", "dysphagia", "associated", 4, "yesno", "Pain while swallowing?", "क्या निगलते समय दर्द होता है?", "गिळताना दुखते का?", term="Odynophagia",
  ddx=["Oesophagitis (infective / pill)", "Candida (immunocompromised)"], src=DY)
Q("dy_regurg", "dysphagia", "associated", 5, "yesno", "Undigested food comes back up, or cough at night?", "क्या बिना पचा खाना वापस आता है या रात को खाँसी?",
  "न पचलेले अन्न परत येते का किंवा रात्री खोकला?", term="Regurgitation", ddx=["Achalasia", "Pharyngeal pouch"], src=DY)
Q("dy_neuro", "dysphagia", "associated", 6, "yesno", "Slurred speech, face/limb weakness, or nasal voice?", "क्या बोली लड़खड़ाना, चेहरे/हाथ-पैर में कमज़ोरी, नाक से आवाज़?",
  "बोलणे अडखळणे, चेहऱ्यात/हात-पायात अशक्तपणा, नाकातून आवाज?", term="Neurological features", rf="Neurological dysphagia — aspiration risk, keep nil by mouth until assessed",
  ddx=["Neurological (oropharyngeal) dysphagia", "Stroke / TIA"], src=DY)
Q("dy_heartburn", "dysphagia", "risk", 7, "yesno", "Long history of heartburn / acidity?", "क्या लंबे समय से सीने में जलन / एसिडिटी?",
  "बराच काळ छातीत जळजळ / ॲसिडिटी?", term="Chronic reflux", ddx=["Benign stricture / ring", "Reflux / GORD"], key="heartburn", src=DY)
Q("dy_tobacco", "dysphagia", "risk", 8, "yesno", "Tobacco / gutka / alcohol use?", "क्या तंबाकू / गुटखा / शराब?", "तंबाखू / गुटखा / दारू?", term="Tobacco / alcohol",
  ddx=["Oesophageal cancer / stricture"], src=DY)
Q("dy_corrosive", "dysphagia", "risk", 9, "yesno", "Ever swallowed acid / poison / chemicals?", "क्या कभी तेज़ाब / ज़हर / केमिकल पिया था?",
  "कधी ॲसिड / विष / रसायन प्यायले होते का?", term="Corrosive ingestion", ddx=["Corrosive stricture"], src="General clinical practice")

# ---------------------------------------------------------------- DYSPEPSIA / HEARTBURN  (p241-242)
DP = f"{GI}, p241-242"
Q("dp_type", "dyspepsia", "hopi", 1, "multi", "What is felt?", "क्या महसूस होता है?", "काय जाणवते?", term="Dyspeptic symptoms", opts=[
    O("burn_chest", "Burning behind breastbone", "छाती की हड्डी के पीछे जलन", "छातीच्या हाडामागे जळजळ", ["Reflux / GORD"]),
    O("sour", "Sour / bitter water in mouth", "मुँह में खट्टा / कड़वा पानी", "तोंडात आंबट / कडू पाणी", ["Reflux / GORD"]),
    O("epigastric", "Pain / burning in upper belly", "पेट के ऊपर दर्द / जलन", "पोटाच्या वर दुखणे / जळजळ", ["Peptic ulcer / gastritis", "Functional dyspepsia"]),
    O("bloating", "Bloating / gas / belching", "पेट फूलना / गैस / डकार", "पोट फुगणे / गॅस / ढेकर", ["Functional dyspepsia"]),
    O("early_full", "Full after a few bites", "थोड़ा खाते ही पेट भरना", "थोडे खाताच पोट भरणे", ["Gastric outlet obstruction", "GI malignancy", "Functional dyspepsia"])],
  src=DP)
Q("dp_timing", "dyspepsia", "hopi", 2, "multi", "When is it worse?", "कब ज़्यादा होता है?", "कधी जास्त होते?", term="Timing", opts=[
    O("lying_bend", "Lying flat / bending", "लेटने / झुकने पर", "झोपल्यावर / वाकल्यावर", ["Reflux / GORD"]),
    O("night", "Wakes at night", "रात को नींद खुलती है", "रात्री जाग येते", ["Peptic ulcer / gastritis", "Reflux / GORD"]),
    O("empty", "Empty stomach, better with food", "खाली पेट, खाने से आराम", "उपाशीपोटी, जेवल्यावर आराम", ["Peptic ulcer / gastritis"]),
    O("spicy_tea", "After spicy food / tea / alcohol", "तीखा / चाय / शराब के बाद", "तिखट / चहा / दारूनंतर", ["Reflux / GORD", "Peptic ulcer / gastritis"])],
  src=DP)
Q("dp_alarm", "dyspepsia", "redflag", 3, "multi", "Any warning signs?", "इनमें से कुछ?", "यापैकी काही?", term="Alarm features", opts=ALARM,
  src=f"{GI}, p242 (upper GI malignancy in older patients)")
Q("dp_age", "dyspepsia", "redflag", 4, "yesno", "New acidity started after age 55?", "क्या 55 की उम्र के बाद नई एसिडिटी शुरू हुई?",
  "55 वयानंतर नवीन ॲसिडिटी सुरू झाली का?", term="New-onset dyspepsia in older patient", rf="New dyspepsia >55 y — consider endoscopy",
  ddx=["GI malignancy"], applies={"min_age": 50}, src=f"{GI}, p242")
Q("dp_nsaid", "dyspepsia", "risk", 5, "yesno", "Taking painkillers often (e.g. diclofenac, ibuprofen, aspirin)?",
  "क्या दर्द की गोलियाँ अक्सर लेते हैं (जैसे डाइक्लोफेनाक, एस्पिरिन)?", "वेदनाशामक गोळ्या वारंवार घेता का (उदा. डायक्लोफेनाक, ॲस्पिरिन)?",
  term="NSAID / aspirin use", ddx=["Peptic ulcer / gastritis"], key="nsaid", src=f"{H}, Ch 1, p9")
Q("dp_lifestyle", "dyspepsia", "risk", 6, "multi", "Habits", "आदतें", "सवयी", term="Lifestyle factors", opts=[
    O("smoke", "Smoking / tobacco", "धूम्रपान / तंबाकू", "धूम्रपान / तंबाखू", ["Peptic ulcer / gastritis", "Reflux / GORD"]),
    O("alcohol", "Alcohol", "शराब", "दारू", ["Peptic ulcer / gastritis", "Reflux / GORD"]),
    O("late_meal", "Late heavy dinner", "रात को देर से भारी खाना", "रात्री उशिरा जड जेवण", ["Reflux / GORD"]),
    O("obese", "Overweight", "मोटापा", "लठ्ठपणा", ["Reflux / GORD"]),
    O("stress", "Stress", "तनाव", "ताण", ["Functional dyspepsia"])],
  src=DP)
Q("dp_cardiac", "dyspepsia", "redflag", 7, "yesno", "'Acidity' that comes on walking and goes with rest, or with sweating?",
  "क्या 'एसिडिटी' चलने पर होती है और आराम से जाती है, या पसीने के साथ?", "'ॲसिडिटी' चालताना होते आणि विश्रांतीने जाते, किंवा घामासोबत?",
  term="Exertional 'indigestion'", rf="Exertional 'acidity' — may be angina, do ECG", ddx=["Angina / ACS"], src=f"{GI}, p241; {H}, Ch 13, p191")

# ---------------------------------------------------------------- GI BLEEDING  (p242-243)
GB = f"{GI}, p242-243"
Q("gb_type", "gi_bleed", "hopi", 1, "multi", "What was seen?", "क्या दिखा?", "काय दिसले?", term="Type of bleeding", opts=[
    O("fresh_vomit", "Fresh red blood in vomit", "उल्टी में ताज़ा लाल खून", "उलटीत ताजे लाल रक्त", ["Peptic ulcer / gastritis", "Varices", "Mallory-Weiss tear"]),
    O("coffee", "Coffee-ground vomit", "कॉफ़ी जैसी उल्टी", "कॉफीसारखी उलटी", ["Peptic ulcer / gastritis"]),
    O("melaena", "Black, tarry, sticky, foul stool", "काला, तारकोल जैसा, चिपचिपा, बदबूदार मल", "काळी, डांबरासारखी, चिकट, दुर्गंधीयुक्त शौच", ["Peptic ulcer / gastritis", "Varices", "GI malignancy"]),
    O("fresh_stool", "Fresh red blood with / on stool", "मल के साथ / ऊपर ताज़ा लाल खून", "शौचासोबत / वर ताजे लाल रक्त", ["Haemorrhoids / fissure", "Colitis", "GI malignancy"]),
    O("mixed_stool", "Dark red blood mixed in stool", "मल में मिला गहरा लाल खून", "शौचात मिसळलेले गडद लाल रक्त", ["Colitis", "GI malignancy", "Diverticular bleed"])],
  src=GB)
Q("gb_shock", "gi_bleed", "redflag", 2, "yesno", "Fainting, dizziness on standing, sweating, or large amount of blood?",
  "क्या बेहोशी, खड़े होने पर चक्कर, पसीना या बहुत ज़्यादा खून?", "बेशुद्धी, उभे राहिल्यावर चक्कर, घाम किंवा खूप जास्त रक्त?",
  term="Haemodynamic compromise", rf="GI bleed with shock features — EMERGENCY (IV access, cross-match)", ddx=["Major GI haemorrhage"], src=f"{H}, Ch 9, p128")
Q("gb_liver", "gi_bleed", "redflag", 3, "yesno", "Known liver disease, heavy alcohol, or belly swelling with yellow eyes?",
  "क्या लिवर की बीमारी, ज़्यादा शराब, या पेट फूला और आँखें पीली?", "यकृताचा आजार, जास्त दारू, किंवा पोट फुगले व डोळे पिवळे?",
  term="Chronic liver disease features", rf="Possible variceal bleed — high risk", ddx=["Varices"], src=f"{GI}, p245 (Box 14.3)")
Q("gb_retch", "gi_bleed", "hopi", 4, "yesno", "Blood came only after repeated forceful vomiting?", "क्या बार-बार ज़ोर से उल्टी के बाद ही खून आया?",
  "वारंवार जोरात उलटी झाल्यानंतरच रक्त आले का?", term="Preceding retching", ddx=["Mallory-Weiss tear"],
  show={"q": "gb_type", "in_any": ["fresh_vomit", "coffee"]}, src=GB)
Q("gb_anal", "gi_bleed", "hopi", 5, "multi", "With the fresh blood", "ताज़े खून के साथ", "ताज्या रक्तासोबत", term="Anorectal features",
  show={"q": "gb_type", "has": "fresh_stool"}, opts=[
      O("drip_pan", "Drips into pan after stool, painless", "मल के बाद टपकता है, दर्द नहीं", "शौचानंतर टपकते, दुखत नाही", ["Haemorrhoids / fissure"]),
      O("pain_anus", "Sharp pain at anus while passing stool", "मल त्याग के समय गुदा में तेज़ दर्द", "शौचाच्या वेळी गुदद्वारात तीव्र दुखणे", ["Haemorrhoids / fissure"]),
      O("pile_mass", "Something comes out of anus", "गुदा से कुछ बाहर आता है", "गुदद्वारातून काही बाहेर येते", ["Haemorrhoids / fissure", "Rectal prolapse"]),
      O("habit_change", "Change in bowel habit / mucus", "पाखाने की आदत बदली / आँव", "शौचाची सवय बदलली / आव", ["GI malignancy", "Colitis"])],
  src=GB)
Q("gb_drugs", "gi_bleed", "risk", 6, "multi", "Medicines", "इनमें से कोई दवा?", "यापैकी कोणते औषध?", term="Drug history (bleeding risk)", opts=[
    O("nsaid", "Painkillers (diclofenac etc.)", "दर्द की गोली (डाइक्लोफेनाक आदि)", "वेदनाशामक (डायक्लोफेनाक इ.)", ["Peptic ulcer / gastritis"]),
    O("aspirin", "Aspirin / clopidogrel", "एस्पिरिन / क्लोपिडोग्रेल", "ॲस्पिरिन / क्लोपिडोग्रेल", ["Peptic ulcer / gastritis"]),
    O("warfarin", "Blood thinners (warfarin, etc.)", "खून पतला करने की दवा", "रक्त पातळ करण्याचे औषध", ["Anticoagulant-related bleeding"]),
    O("steroid", "Steroids", "स्टेरॉयड", "स्टिरॉइड", ["Peptic ulcer / gastritis"]),
    O("iron", "Iron tablets (make stool black)", "आयरन की गोली (मल काला करती है)", "आयर्न गोळी (शौच काळी करते)", ["Iron-induced black stool (not blood)"])],
  src=GB)
Q("gb_previous", "gi_bleed", "risk", 7, "yesno", "Similar bleeding before / ulcer before?", "क्या पहले भी ऐसा खून या अल्सर हुआ था?", "आधीही असे रक्त किंवा अल्सर झाला होता का?",
  term="Previous GI bleed / ulcer", ddx=["Peptic ulcer / gastritis"], src=GB)

# ---------------------------------------------------------------- BOWEL HABIT CHANGE  (p242)
BH = f"{GI}, p242"
Q("bh_pattern", "bowel_change", "hopi", 1, "choice", "What is the change?", "क्या बदलाव है?", "काय बदल आहे?", term="Bowel pattern", opts=[
    O("constipation", "Constipation (hard / less than 3 times a week)", "कब्ज़ (सख़्त / हफ़्ते में 3 बार से कम)", "बद्धकोष्ठता (कडक / आठवड्यात 3 पेक्षा कमी)", ["Constipation", "Hypothyroidism", "GI malignancy"]),
    O("loose", "Looser / more often", "पतला / बार-बार", "पातळ / वारंवार", ["IBD", "GI malignancy", "Thyrotoxicosis"]),
    O("alternating", "Alternating constipation and loose", "कभी कब्ज़ कभी दस्त", "कधी बद्धकोष्ठता कधी जुलाब", ["Irritable bowel syndrome", "GI malignancy"]),
    O("incomplete", "Feels not fully emptied", "पूरा साफ़ नहीं होता लगता", "पूर्ण साफ होत नाही असे वाटते", ["Rectal cancer", "Irritable bowel syndrome"])],
  src=BH)
Q("bh_duration", "bowel_change", "hopi", 2, "choice", "Since when?", "कब से?", "कधीपासून?", term="Duration", opts=[
    O("lt6w", "Less than 6 weeks", "6 हफ़्ते से कम", "6 आठवड्यांपेक्षा कमी"),
    O("gt6w", "More than 6 weeks", "6 हफ़्ते से ज़्यादा", "6 आठवड्यांपेक्षा जास्त", ["GI malignancy", "IBD", "Irritable bowel syndrome"]),
    O("years", "Years, on and off", "सालों से, रुक-रुक कर", "वर्षानुवर्षे, अधूनमधून", ["Irritable bowel syndrome", "Constipation"])],
  src=BH)
Q("bh_alarm", "bowel_change", "redflag", 3, "yesno", "Age over 50 with blood in stool, weight loss or anaemia?", "क्या 50 से ज़्यादा उम्र, मल में खून, वज़न घटना या खून की कमी?",
  "50 पेक्षा जास्त वय, शौचात रक्त, वजन घटणे किंवा रक्ताची कमतरता?", term="Colorectal red flags", rf="Change in bowel habit with alarm features — colonoscopy",
  ddx=["GI malignancy"], src=BH)
Q("bh_pain_relief", "bowel_change", "associated", 4, "yesno", "Tummy pain / bloating that eases after passing stool?", "क्या पेट दर्द / फुलाव जो मल त्याग के बाद कम हो जाता है?",
  "पोटदुखी / फुगवटा जो शौचानंतर कमी होतो?", term="Pain relieved by defaecation", ddx=["Irritable bowel syndrome"], src=f"{GI}, p243 (Box 14.2)")
Q("bh_obstruct", "bowel_change", "redflag", 5, "yesno", "No stool or gas for days with belly swelling and vomiting?", "क्या कई दिन से मल/गैस बंद, पेट फूला और उल्टी?",
  "अनेक दिवस शौच/गॅस बंद, पोट फुगले आणि उलटी?", term="Obstruction", rf="Possible bowel obstruction", ddx=["Obstruction"], src=BH)
Q("bh_steatorrhoea", "bowel_change", "associated", 6, "yesno", "Pale, bulky, oily stool that floats / hard to flush?", "क्या मल पीला, ज़्यादा, चिकना, पानी पर तैरता / बहाना मुश्किल?",
  "शौच फिकट, जास्त, तेलकट, पाण्यावर तरंगणारी / वाहवणे कठीण?", term="Steatorrhoea", ddx=["Malabsorption", "Chronic pancreatitis"], src=BH)
Q("bh_causes", "bowel_change", "risk", 7, "multi", "Possible causes", "इनमें से कुछ?", "यापैकी काही?", term="Contributing factors", opts=[
    O("low_fibre_water", "Little water / vegetables", "पानी / सब्ज़ी कम", "पाणी / भाज्या कमी", ["Constipation"]),
    O("drugs", "Iron / pain (tramadol, codeine) / calcium tablets", "आयरन / दर्द (ट्रामाडोल) / कैल्शियम की गोली", "आयर्न / वेदना (ट्रामाडॉल) / कॅल्शियम गोळी", ["Drug-induced constipation"]),
    O("hypothyroid", "Feels cold, gaining weight, slow", "ठंड लगना, वज़न बढ़ना, सुस्ती", "थंडी वाजणे, वजन वाढणे, सुस्ती", ["Hypothyroidism"]),
    O("immobile", "Bed-bound / not walking", "बिस्तर पर / चलना-फिरना कम", "अंथरुणावर / हालचाल कमी", ["Constipation"]),
    O("fh_cancer", "Bowel cancer in family", "परिवार में आँत का कैंसर", "कुटुंबात आतड्याचा कर्करोग", ["GI malignancy"])],
  src=BH)

# ---------------------------------------------------------------- ABDOMINAL SWELLING  (p242; Box 14.4 p256)
AS = f"{GI}, p242, p256 (Box 14.4)"
Q("as_type", "abd_swelling", "hopi", 1, "choice", "What kind of swelling?", "सूजन कैसी है?", "सूज कशी आहे?", term="Nature of distension", opts=[
    O("whole_gradual", "Whole belly, slowly increasing, tight", "पूरा पेट, धीरे-धीरे बढ़ता, तना हुआ", "संपूर्ण पोट, हळूहळू वाढणारे, ताणलेले", ["Ascites (liver / heart / kidney / TB / cancer)"]),
    O("comes_goes", "Comes and goes with gas / meals", "गैस / खाने के साथ आता-जाता", "गॅस / जेवणासोबत येते-जाते", ["Functional bloating", "Irritable bowel syndrome"]),
    O("lump_one_side", "A lump on one side", "एक तरफ गाँठ", "एका बाजूला गाठ", ["Organomegaly / mass"]),
    O("lower_preg", "Lower belly, periods missed", "नीचे का पेट, माहवारी रुकी", "खालचे पोट, पाळी चुकली", ["Pregnancy"])],
  src=AS)
Q("as_liver", "abd_swelling", "associated", 2, "multi", "Along with swelling", "सूजन के साथ", "सुजेसोबत", term="Associated features", opts=[
    O("jaundice", "Yellow eyes", "आँखें पीली", "डोळे पिवळे", ["Chronic liver disease / cirrhosis"]),
    O("leg_swell", "Leg swelling", "पैरों में सूजन", "पायांना सूज", ["Chronic liver disease / cirrhosis", "Heart failure", "Kidney disease"]),
    O("breathless", "Breathless lying flat", "लेटने पर साँस फूलना", "झोपल्यावर धाप", ["Heart failure"]),
    O("face_puffy", "Puffy face, frothy urine", "चेहरा सूजा, झागदार पेशाब", "चेहरा सुजलेला, फेसाळ लघवी", ["Kidney disease"]),
    O("fever_wtloss", "Evening fever / weight loss", "शाम को बुखार / वज़न घटना", "संध्याकाळी ताप / वजन घटणे", ["Abdominal TB", "GI malignancy"]),
    O("vomit_blood", "Blood vomit / black stool", "खून की उल्टी / काला मल", "रक्ताची उलटी / काळी शौच", ["Varices"])],
  src=AS)
Q("as_confusion", "abd_swelling", "redflag", 3, "yesno", "Confused, sleepy in day and awake at night, or very drowsy?", "क्या उलझन, दिन में नींद रात में जागना, या बहुत सुस्ती?",
  "गोंधळ, दिवसा झोप रात्री जाग, किंवा खूप गुंगी?", term="Encephalopathy features", rf="Possible hepatic encephalopathy", ddx=["Hepatic encephalopathy"], key="encephalopathy", src=f"{GI}, p245")
Q("as_fever_pain", "abd_swelling", "redflag", 4, "yesno", "Fever with tender swollen belly?", "क्या बुखार के साथ पेट फूला और छूने पर दर्द?", "तापासोबत पोट फुगलेले आणि स्पर्शाला दुखरे?",
  term="Fever + tender ascites", rf="Possible spontaneous bacterial peritonitis / TB peritonitis", ddx=["Spontaneous bacterial peritonitis", "Abdominal TB"], src="General clinical practice")
Q("as_alcohol", "abd_swelling", "risk", 5, "yesno", "Heavy alcohol for years?", "क्या सालों से ज़्यादा शराब?", "वर्षानुवर्षे जास्त दारू?", term="Alcohol excess",
  ddx=["Chronic liver disease / cirrhosis"], key="alcohol", src=f"{H}, Ch 1, p9-10")

# ---------------------------------------------------------------- WEIGHT LOSS / ANOREXIA  (p242-243)
WL = f"{GI}, p242-243"
Q("wl_amount", "weight_loss", "hopi", 1, "text", "Usual weight before, weight now, over how long?", "पहले वज़न कितना था, अब कितना, कितने समय में?",
  "आधी वजन किती होते, आता किती, किती काळात?", term="Weight change (kg / months)", src=f"{WL} (Nutritional assessment)")
Q("wl_intentional", "weight_loss", "hopi", 2, "yesno", "Was the weight loss on purpose (diet/exercise)?", "क्या वज़न जानबूझकर (डाइट/कसरत से) घटाया?",
  "वजन मुद्दाम (डाएट/व्यायामाने) कमी केले का?", term="Intentional weight loss", neg="Unintentional loss needs a cause", src=WL)
Q("wl_appetite", "weight_loss", "hopi", 3, "choice", "Appetite", "भूख कैसी है?", "भूक कशी आहे?", term="Appetite", opts=[
    O("poor", "Poor appetite", "भूख कम", "भूक कमी", ["GI malignancy", "Tuberculosis", "Depression", "Chronic disease"]),
    O("early_full", "Hungry but full after few bites", "भूख है पर थोड़ा खाते ही पेट भर जाता", "भूक आहे पण थोडे खाताच पोट भरते", ["Gastric outlet obstruction", "GI malignancy"]),
    O("good", "Good / increased appetite", "अच्छी / ज़्यादा भूख", "चांगली / जास्त भूक", ["Diabetes", "Thyrotoxicosis", "Malabsorption"])],
  src=WL)
Q("wl_systemic", "weight_loss", "associated", 4, "multi", "Any of these?", "इनमें से कुछ?", "यापैकी काही?", term="Systemic clues", opts=[
    O("fever_sweats", "Evening fever / night sweats / cough", "शाम को बुखार / रात को पसीना / खाँसी", "संध्याकाळी ताप / रात्री घाम / खोकला", ["Tuberculosis", "Lymphoma", "HIV"]),
    O("thirst_urine", "Very thirsty, passing lots of urine", "बहुत प्यास, बार-बार पेशाब", "खूप तहान, वारंवार लघवी", ["Diabetes"]),
    O("heat_tremor", "Heat intolerance, tremor, palpitations", "गर्मी सहन न होना, हाथ काँपना, धड़कन", "उष्णता सहन न होणे, हात थरथरणे, धडधड", ["Thyrotoxicosis"]),
    O("diarrhoea", "Loose / oily stools", "दस्त / चिकना मल", "जुलाब / तेलकट शौच", ["Malabsorption", "IBD"]),
    O("low_mood", "Low mood, no interest", "उदासी, किसी चीज़ में मन नहीं", "उदासी, कशातच मन नाही", ["Depression"]),
    O("lumps", "Lumps in neck / armpit / groin", "गर्दन / बगल / जांघ में गाँठें", "मान / काख / जांघेत गाठी", ["Lymphoma", "Tuberculosis", "Malignancy"])],
  src=WL)
Q("wl_alarm", "weight_loss", "redflag", 5, "multi", "GI warning signs", "पेट से जुड़े ख़तरे के निशान", "पोटाशी संबंधित धोक्याची चिन्हे", term="GI alarm features",
  opts=ALARM, src=WL)
Q("wl_diet", "weight_loss", "risk", 6, "multi", "Eating problems", "खाने में दिक्कत", "खाण्यात अडचण", term="Barriers to eating", opts=[
    O("teeth", "Teeth / mouth problems", "दाँत / मुँह की तकलीफ़", "दात / तोंडाचा त्रास", ["Poor intake"]),
    O("money", "Not enough food at home", "घर में खाना पूरा नहीं", "घरी पुरेसे अन्न नाही", ["Poor intake / malnutrition"]),
    O("alone", "Lives alone / no one to cook", "अकेले रहते / खाना बनाने वाला नहीं", "एकटे राहतात / स्वयंपाक करणारे नाही", ["Poor intake / malnutrition"]),
    O("alcohol", "Heavy alcohol", "ज़्यादा शराब", "जास्त दारू", ["Poor intake / malnutrition"])],
  src=f"{WL} (dietary history)")

# ---------------------------------------------------------------- JAUNDICE  (p243) — hepatobiliary
JD = f"{GI}, p243"
Q("jd_urine_stool", "jaundice", "hopi", 1, "multi", "Urine and stool colour", "पेशाब और मल का रंग", "लघवी आणि शौचाचा रंग", term="Urine / stool colour", opts=[
    O("dark_urine", "Dark yellow / tea-coloured urine", "गहरा पीला / चाय जैसा पेशाब", "गडद पिवळी / चहासारखी लघवी", ["Hepatitis", "Obstructive jaundice"]),
    O("pale_stool", "Pale / clay-coloured stool", "सफ़ेद / मिट्टी जैसा मल", "पांढरी / मातीसारखी शौच", ["Obstructive jaundice"]),
    O("normal", "Normal urine colour", "पेशाब का रंग सामान्य", "लघवीचा रंग सामान्य", ["Haemolysis", "Gilbert's syndrome"])],
  src=JD)
Q("jd_itch", "jaundice", "associated", 2, "yesno", "Itching all over the body?", "क्या पूरे शरीर में खुजली है?", "संपूर्ण अंगाला खाज येते का?", term="Pruritus",
  ddx=["Obstructive jaundice", "Cholestasis"], src=f"{GI}, p242 (Box 14.1)")
Q("jd_pain", "jaundice", "associated", 3, "choice", "Pain?", "दर्द है?", "दुखणे आहे का?", term="Pain with jaundice", opts=[
    O("none", "Painless", "दर्द नहीं", "दुखणे नाही", ["Pancreatic / periampullary cancer", "Hepatitis"]),
    O("ruq_colic", "Upper right colicky pain", "ऊपर दाईं तरफ मरोड़ वाला दर्द", "वर उजवीकडे मुरड्याचे दुखणे", ["Choledocholithiasis (CBD stone)"]),
    O("ruq_dull", "Dull ache upper right", "ऊपर दाईं तरफ हल्का दर्द", "वर उजवीकडे मंद दुखणे", ["Hepatitis"])],
  src=f"{GI}, p243 (Box 14.2)")
Q("jd_fever_rigor", "jaundice", "redflag", 4, "yesno", "High fever with shivering along with jaundice and right-side pain?",
  "क्या पीलिया और दाईं तरफ दर्द के साथ कँपकँपी वाला तेज़ बुखार?", "कावीळ आणि उजवीकडे दुखण्यासोबत थंडी वाजून तीव्र ताप?",
  term="Charcot's triad", rf="Possible cholangitis — EMERGENCY", ddx=["Cholangitis"], src="General clinical practice")
Q("jd_prodrome", "jaundice", "hopi", 5, "yesno", "Fever, nausea, loss of appetite and aversion to food a few days before yellowness?",
  "क्या पीलिया से कुछ दिन पहले बुखार, जी मिचलाना, भूख न लगना, खाने से अरुचि?", "कावीळीच्या काही दिवस आधी ताप, मळमळ, भूक न लागणे, अन्नाचा तिटकारा?",
  term="Viral prodrome", ddx=["Hepatitis"], src=JD)
Q("jd_encephalopathy", "jaundice", "redflag", 6, "yesno", "Confusion, drowsiness, or bleeding (gums/nose/vomit)?",
  "क्या उलझन, सुस्ती, या खून आना (मसूड़े/नाक/उल्टी)?", "गोंधळ, गुंगी, किंवा रक्तस्राव (हिरड्या/नाक/उलटी)?",
  term="Encephalopathy / coagulopathy", rf="Jaundice with confusion/bleeding — possible acute liver failure", ddx=["Acute liver failure", "Hepatic encephalopathy"],
  key="encephalopathy", src=f"{GI}, p245")
Q("jd_pregnant", "jaundice", "redflag", 7, "yesno", "Pregnant?", "क्या गर्भवती हैं?", "गर्भवती आहात का?", term="Jaundice in pregnancy",
  rf="Jaundice in pregnancy — high risk (Hepatitis E / pregnancy liver disease)", ddx=["Hepatitis"], key="pregnancy",
  applies={"sex": "female", "min_age": 14, "max_age": 50}, src="General clinical practice")
Q("jd_exposures", "jaundice", "risk", 8, "multi", "Exposures", "इनमें से कुछ?", "यापैकी काही?", term="Hepatitis risk factors", opts=[
    O("water_food", "Outside food / contaminated water", "बाहर का खाना / गंदा पानी", "बाहेरचे अन्न / दूषित पाणी", ["Hepatitis"]),
    O("others", "Others in area/family with jaundice", "आसपास/परिवार में और लोगों को भी पीलिया", "परिसरात/कुटुंबात इतरांनाही कावीळ", ["Hepatitis"]),
    O("transfusion", "Blood transfusion / dialysis", "खून चढ़ा / डायलिसिस", "रक्त चढवले / डायलिसिस", ["Hepatitis"]),
    O("injection", "Injections / tattoo / shared razor", "इंजेक्शन / टैटू / एक ही ब्लेड", "इंजेक्शन / टॅटू / एकच ब्लेड", ["Hepatitis"]),
    O("sexual", "Unprotected sex / multiple partners", "असुरक्षित संबंध", "असुरक्षित संबंध", ["Hepatitis"]),
    O("flood", "Flood water / animal contact with fever", "बाढ़ का पानी / जानवरों से संपर्क व बुखार", "पुराचे पाणी / जनावरांशी संपर्क व ताप", ["Leptospirosis"]),
    O("malaria_area", "Fever with chills (malaria area)", "कँपकँपी वाला बुखार (मलेरिया)", "थंडी वाजून ताप (मलेरिया)", ["Malaria"])],
  src=f"{H}, Ch 10, p146; {GI}, p243")
Q("jd_drugs", "jaundice", "risk", 9, "multi", "Medicines (last 3 months)", "पिछले 3 महीने की दवाएँ", "मागील 3 महिन्यांची औषधे", term="Hepatotoxic drugs", opts=[
    O("att", "TB medicines", "टीबी की दवा", "टीबीचे औषध", ["Drug-induced liver injury"]),
    O("paracetamol_high", "Many paracetamol tablets", "बहुत सारी पैरासिटामोल", "खूप पॅरासिटामॉल", ["Drug-induced liver injury"]),
    O("herbal", "Herbal / ayurvedic / desi medicines", "जड़ी-बूटी / आयुर्वेदिक / देसी दवा", "जडीबुटी / आयुर्वेदिक / देशी औषध", ["Drug-induced liver injury"]),
    O("antiepileptic", "Fits / psychiatric medicines", "मिर्गी / मानसिक रोग की दवा", "आकडी / मानसिक आजाराची औषधे", ["Drug-induced liver injury"]),
    O("antibiotic", "Recent antibiotics", "हाल में एंटीबायोटिक", "अलीकडे अँटिबायोटिक", ["Drug-induced liver injury"])],
  src=f"{H}, Ch 1, p9 (drug history)")
Q("jd_alcohol", "jaundice", "risk", 10, "yesno", "Heavy alcohol for years?", "क्या सालों से ज़्यादा शराब?", "वर्षानुवर्षे जास्त दारू?", term="Alcohol excess",
  ddx=["Alcoholic liver disease"], key="alcohol", src=f"{H}, Ch 1, p9-10")
Q("jd_wtloss", "jaundice", "redflag", 11, "yesno", "Weight loss, painless jaundice, age over 45?", "क्या वज़न घटना, बिना दर्द का पीलिया, उम्र 45 से ज़्यादा?",
  "वजन घटणे, दुखण्याशिवाय कावीळ, वय 45 पेक्षा जास्त?", term="Painless progressive jaundice with weight loss",
  rf="Painless obstructive jaundice + weight loss — exclude pancreatic/biliary cancer", ddx=["Pancreatic / periampullary cancer"], applies={"min_age": 40}, src=JD)
Q("jd_anaemia", "jaundice", "associated", 12, "yesno", "Very pale, tired, red/dark urine after fever or a new medicine?", "क्या बहुत पीलापन, थकान, बुखार या नई दवा के बाद लाल/काला पेशाब?",
  "खूप फिकटपणा, थकवा, ताप किंवा नवीन औषधानंतर लाल/काळी लघवी?", term="Haemolytic features", ddx=["Haemolysis"], src=JD)

# ---------------------------------------------------------------- ABDOMINAL PAIN extra red flags
Q("ab_peritonism", "abd_pain", "redflag", 15, "yesno", "Pain worse on moving / coughing, lies very still, belly hard?",
  "क्या हिलने / खाँसने पर दर्द बढ़ता है, बिल्कुल स्थिर लेटे हैं, पेट सख़्त?", "हालचाल / खोकल्याने दुखणे वाढते, अगदी स्थिर पडून आहेत, पोट कडक?",
  term="Peritonism", rf="Peritonitis signs — surgical emergency", ddx=["Peritonitis", "Perforation"], src=f"{H}, Ch 9, p138")
Q("ab_aaa", "abd_pain", "redflag", 16, "yesno", "Age over 55 with sudden back/belly pain and fainting?", "क्या 55 से ज़्यादा उम्र, अचानक पीठ/पेट दर्द और बेहोशी?",
  "55 पेक्षा जास्त वय, अचानक पाठ/पोटदुखी आणि बेशुद्धी?", term="Possible ruptured AAA", rf="Possible ruptured aortic aneurysm — EMERGENCY",
  ddx=["Aortic aneurysm"], applies={"min_age": 50}, src=f"{H}, Ch 13, p192")
Q("ab_previous", "abd_pain", "risk", 17, "multi", "Previous belly problems", "पहले पेट की कौन-सी तकलीफ़?", "आधी पोटाचा कोणता त्रास?", term="Previous abdominal history", opts=[
    O("surgery", "Belly operation", "पेट का ऑपरेशन", "पोटाचे ऑपरेशन", ["Obstruction"]),
    O("stones", "Gallstones / kidney stones", "पित्त की पथरी / किडनी की पथरी", "पित्ताशयाचे खडे / मुतखडा", ["Biliary colic / cholecystitis", "Renal colic / stone"]),
    O("ulcer", "Ulcer", "अल्सर", "अल्सर", ["Peptic ulcer / gastritis", "Perforation"]),
    O("pancreatitis", "Pancreatitis before", "पहले पैंक्रियाटाइटिस", "आधी पॅन्क्रियाटायटिस", ["Pancreatitis"])],
  src=f"{GI}, p241-243")
