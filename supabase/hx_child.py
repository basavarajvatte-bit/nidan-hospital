# ====================================================================== SYSTEM 14: PAEDIATRIC (children 0-14 y)
# Hutchison 24e, Ch 6 (Children and adolescents), p63-80: Box 6.1 (structure), 6.2 (pregnancy & infancy),
# 6.3 (general questions), Table 6.1 (milestones), Box 6.9 (abuse/neglect alerts). History is taken from the carer.
# Danger signs follow IMNCI (MoHFW India / WHO) — marked as general clinical practice. Executed inside hx_bank.py.

CH = f"{H}, Ch 6"
IMNCI = "IMNCI danger signs (MoHFW India / WHO) — general clinical practice"
KID = {"max_age": 14}
BABY = {"max_age": 0}          # under 1 year (age stored in whole years)
UNDER5 = {"max_age": 5}

C("child_fever", "Child", "Child: fever / unwell", "बच्चा: बुखार / तबीयत ख़राब", "मूल: ताप / बरे नाही", "🧒", 141, f"{CH}, p64-65; {IMNCI}")
C("child_cough", "Child", "Child: cough / fast breathing", "बच्चा: खाँसी / तेज़ साँस", "मूल: खोकला / जलद श्वास", "🫁", 142, f"{CH}, p64; {IMNCI}")
C("child_diarrhoea", "Child", "Child: loose motions / vomiting", "बच्चा: दस्त / उल्टी", "मूल: जुलाब / उलटी", "🚼", 143, f"{CH}, p65; {IMNCI}")
C("newborn", "Child", "Baby under 2 months: problem", "2 महीने से छोटा बच्चा: तकलीफ़", "2 महिन्यांपेक्षा लहान बाळ: त्रास", "👶", 144, f"{CH}, p65 (Box 6.2); {IMNCI}")
C("child_growth", "Child", "Child: low weight / not eating / not growing", "बच्चा: वज़न कम / खाना नहीं / बढ़ नहीं रहा", "मूल: वजन कमी / खात नाही / वाढ नाही", "📏", 145, f"{CH}, p73-75; {IMNCI}")
C("child_development", "Child", "Child: late sitting / walking / talking", "बच्चा: बैठना / चलना / बोलना देर से", "मूल: बसणे / चालणे / बोलणे उशिरा", "🧩", 146, f"{CH}, p65-66 (Table 6.1)")
C("child_fits", "Child", "Child: fits (with or without fever)", "बच्चा: दौरा / झटके (बुखार के साथ या बिना)", "मूल: झटके (तापासह किंवा शिवाय)", "⚡", 147, f"{CH}; {H}, Ch 16; {IMNCI}")
C("child_checkup", "Child", "Child check-up / vaccines / behaviour", "बच्चे की जाँच / टीके / व्यवहार", "मुलाची तपासणी / लसी / वर्तन", "💉", 148, f"{CH}, p64-65 (Box 6.1-6.3)")

# ---------------------------------------------------------------- shared background (Box 6.1-6.2), asked once per session
def child_background(p, comp, base):
    Q(f"{p}_birth", comp, "pmh", base, "multi", "Birth history", "जन्म का इतिहास", "जन्माचा इतिहास", term="Perinatal history (Box 6.2)", key="child_birth", applies=KID, opts=[
        O("term_normal", "Born on time, normal, cried at once", "समय पर, नॉर्मल, तुरंत रोया", "वेळेवर, नॉर्मल, लगेच रडले"),
        O("preterm_lbw", "Premature / low birth weight (<2.5 kg)", "समय से पहले / कम वज़न (<2.5 किलो)", "अकाली / कमी वजन (<2.5 किलो)", ["Prematurity / low birth weight"]),
        O("nicu", "Did not cry at birth / NICU / oxygen", "जन्म पर नहीं रोया / NICU / ऑक्सीजन", "जन्मतः रडले नाही / NICU / ऑक्सिजन", ["Birth asphyxia"]),
        O("nb_jaundice_fits", "Jaundice / fits / feeding problem after birth", "जन्म के बाद पीलिया / दौरे / दूध पीने में तकलीफ़", "जन्मानंतर कावीळ / झटके / दूध पिण्यास त्रास", ["Neonatal complication"]),
        O("mother_illness", "Mother ill / on medicines / alcohol in pregnancy", "गर्भ में माँ बीमार / दवा / शराब", "गर्भात आई आजारी / औषध / दारू", ["Antenatal exposure"]),
        O("caesarean", "Caesarean / forceps / home delivery", "सिज़ेरियन / चिमटा / घर पर डिलीवरी", "सिझेरियन / चिमटा / घरी प्रसूती")],
      src=f"{CH}, p65 (Box 6.2)")
    Q(f"{p}_vacc", comp, "pmh", base + 1, "choice", "Vaccines up to date for age (check MCP card)?", "उम्र के हिसाब से सारे टीके लगे हैं (MCP कार्ड देखें)?",
      "वयानुसार सर्व लसी झाल्या आहेत का (MCP कार्ड पाहा)?", term="Immunisation status", key="child_vaccines", applies=KID, opts=[
          O("full", "Yes, all", "हाँ, सारे", "हो, सर्व"),
          O("partial", "Some missed", "कुछ छूटे", "काही राहिल्या", ["Incomplete immunisation"]),
          O("none", "None / don't know", "कोई नहीं / पता नहीं", "एकही नाही / माहीत नाही", ["Incomplete immunisation"])],
      src=f"{CH}, p65")
    Q(f"{p}_family", comp, "family", base + 2, "multi", "Family", "परिवार", "कुटुंब", term="Family history", key="child_family", applies=KID, opts=[
        O("consang", "Parents are relatives (cousin marriage)", "माता-पिता रिश्तेदार (मामा/बुआ के बच्चे)", "आई-वडील नातेवाईक (मामा/आत्याची मुले)", ["Genetic disorder"]),
        O("sib_death", "Sibling died / stillbirths / miscarriages", "भाई-बहन की मौत / मृत शिशु / गर्भपात", "भावंडाचा मृत्यू / मृत बाळ / गर्भपात", ["Genetic disorder"]),
        O("inherited", "Thalassaemia / sickle / fits / delay in family", "परिवार में थैलेसीमिया / सिकल / दौरे / देरी", "कुटुंबात थॅलेसेमिया / सिकल / झटके / उशीर", ["Genetic disorder"]),
        O("tb_home", "Someone at home has TB / long cough", "घर में किसी को टीबी / लंबी खाँसी", "घरी कोणाला टीबी / जुना खोकला", ["Tuberculosis"])],
      src=f"{CH}, p65 (family history)")

# ---------------------------------------------------------------- general danger signs (IMNCI), shared via key
def general_danger(p, comp):
    Q(f"{p}_gds", comp, "redflag", 1, "yesno", "Child unable to drink / breastfeed, vomits everything, had fits, or is very sleepy / hard to wake?",
      "क्या बच्चा पी / स्तनपान नहीं कर पा रहा, सब उल्टी कर देता, दौरा आया, या बहुत सुस्त / जगाना मुश्किल?",
      "मूल पिऊ / स्तनपान करू शकत नाही, सगळे उलटून टाकते, झटके आले, किंवा खूप सुस्त / उठवणे कठीण?",
      term="IMNCI general danger sign", rf="CHILD GENERAL DANGER SIGN — urgent doctor review / refer (IMNCI)", ddx=["Severe illness (sepsis / meningitis / severe pneumonia)"],
      key="child_gds", applies=UNDER5, src=IMNCI)

# ---------------------------------------------------------------- FEVER
general_danger("chf", "child_fever")
Q("chf_details", "child_fever", "hopi", 2, "multi", "About the fever", "बुखार के बारे में", "तापाबद्दल", term="Fever details", applies=KID, opts=[
    O("gt7d", "More than 7 days", "7 दिन से ज़्यादा", "7 दिवसांपेक्षा जास्त", ["Enteric fever", "Tuberculosis", "UTI", "Kawasaki disease"]),
    O("rash", "Rash", "दाने", "पुरळ", ["Measles", "Dengue", "Viral exanthem"]),
    O("ear_throat", "Ear pain / sore throat", "कान दर्द / गले में ख़राश", "कान दुखणे / घसा खवखव", ["Otitis media", "Tonsillitis"]),
    O("urine_cry", "Crying while passing urine / smelly urine", "पेशाब करते रोना / बदबूदार पेशाब", "लघवी करताना रडणे / वास येणारी लघवी", ["UTI"]),
    O("chills_area", "Chills / malaria or dengue in area", "कँपकँपी / इलाक़े में मलेरिया या डेंगू", "थंडी वाजणे / परिसरात मलेरिया किंवा डेंग्यू", ["Malaria", "Dengue"]),
    O("cough_fast", "Cough / fast breathing", "खाँसी / तेज़ साँस", "खोकला / जलद श्वास", ["Pneumonia"]),
    O("red_eyes_lips", "Red eyes, cracked lips, swollen hands-feet (>5 days)", "लाल आँखें, फटे होंठ, हाथ-पैर सूजे (>5 दिन)", "लाल डोळे, फुटलेले ओठ, हात-पाय सुजले (>5 दिवस)", ["Kawasaki disease"])],
  src=f"{CH}, p64; {IMNCI}")
Q("chf_mening", "child_fever", "redflag", 3, "yesno", "Stiff neck, bulging soft spot (baby), purple spots that don't fade, or bleeding?",
  "क्या गर्दन अकड़ी, सिर का नरम हिस्सा उभरा (शिशु), बैंगनी दाने जो दबाने पर नहीं मिटते, या ख़ून आना?",
  "मान ताठ, टाळू फुगलेली (बाळ), दाबल्यावर न जाणारे जांभळे पुरळ, किंवा रक्तस्राव?",
  term="Meningitis / severe dengue signs", rf="Possible meningitis / meningococcaemia / severe dengue — EMERGENCY", ddx=["Meningitis", "Meningococcal sepsis", "Dengue (severe)"],
  applies=KID, src=f"{IMNCI}; {H}, Ch 16")
child_background("chf", "child_fever", 10)

# ---------------------------------------------------------------- COUGH / BREATHING
general_danger("chc", "child_cough")
Q("chc_signs", "child_cough", "redflag", 2, "multi", "Breathing signs (count breaths for 1 minute)", "साँस के लक्षण (1 मिनट साँस गिनें)", "श्वासाची लक्षणे (1 मिनिट श्वास मोजा)",
  term="Respiratory signs (IMNCI)", applies=KID, opts=[
      O("fast", "Fast breathing (≥60 <2 mo, ≥50 2–12 mo, ≥40 1–5 y)", "तेज़ साँस (≥60 <2 माह, ≥50 2–12 माह, ≥40 1–5 साल)", "जलद श्वास (≥60 <2 म, ≥50 2–12 म, ≥40 1–5 वर्षे)", ["Pneumonia"]),
      O("indrawing", "Lower chest pulls in with each breath", "हर साँस पर छाती नीचे से अंदर धँसती", "प्रत्येक श्वासाला छाती खालून आत ओढली जाते", ["Severe pneumonia"]),
      O("stridor", "Harsh noise when breathing in, while calm", "शांत रहते साँस लेते कर्कश आवाज़", "शांत असताना श्वास घेताना कर्कश आवाज", ["Croup", "Foreign body", "Diphtheria"]),
      O("wheeze", "Whistling sound", "सीटी जैसी आवाज़", "शिट्टीसारखा आवाज", ["Asthma", "Bronchiolitis"]),
      O("blue", "Blue lips / grunting", "होंठ नीले / कराहना", "ओठ निळे / कण्हणे", ["Severe pneumonia", "Respiratory failure"])],
  src=IMNCI)
Q("chc_severe", "child_cough", "redflag", 3, "yesno", "Chest indrawing, noisy breathing at rest, blue lips, or sudden choking on something?",
  "क्या छाती धँसना, आराम में आवाज़ वाली साँस, नीले होंठ, या अचानक कुछ अटकना?", "छाती आत ओढणे, विश्रांतीत आवाजाचा श्वास, निळे ओठ, किंवा अचानक काहीतरी अडकणे?",
  term="Severe respiratory distress / foreign body", rf="Severe pneumonia / airway obstruction — EMERGENCY (oxygen, refer)", ddx=["Severe pneumonia", "Foreign body"], applies=KID, src=IMNCI)
Q("chc_hopi", "child_cough", "hopi", 4, "multi", "Cough details", "खाँसी का विवरण", "खोकल्याचा तपशील", term="Cough history", applies=KID, opts=[
    O("gt14d", "More than 2 weeks", "2 हफ़्ते से ज़्यादा", "2 आठवड्यांपेक्षा जास्त", ["Tuberculosis", "Asthma", "Pertussis"]),
    O("whoop", "Bouts of cough with whoop / vomiting after cough", "खाँसी के दौरे, 'हूप' आवाज़ / खाँसी के बाद उल्टी", "खोकल्याचे झटके, 'हूप' आवाज / खोकल्यानंतर उलटी", ["Pertussis"]),
    O("night_exercise", "At night / with play / with dust or cold", "रात में / खेलने पर / धूल या ठंड से", "रात्री / खेळताना / धूळ किंवा थंडीने", ["Asthma"]),
    O("after_feed", "After feeds / spits up", "दूध पीने के बाद / दूध उलटता", "दूध पिल्यानंतर / दूध उलटते", ["Gastro-oesophageal reflux"]),
    O("wt_loss", "Weight loss / night sweats / TB contact", "वज़न घटना / रात को पसीना / टीबी संपर्क", "वजन घटणे / रात्री घाम / टीबी संपर्क", ["Tuberculosis"]),
    O("smoke", "Smoke at home (chulha / smoking)", "घर में धुआँ (चूल्हा / बीड़ी)", "घरी धूर (चूल / बिडी)", ["Recurrent respiratory infection"])],
  src=f"{CH}, p64; {IMNCI}")
child_background("chc", "child_cough", 10)

# ---------------------------------------------------------------- DIARRHOEA / VOMITING
general_danger("chd", "child_diarrhoea")
Q("chd_dehyd", "child_diarrhoea", "redflag", 2, "multi", "Dehydration signs", "पानी की कमी के लक्षण", "पाण्याची कमतरता लक्षणे", term="Dehydration (IMNCI)", applies=KID, opts=[
    O("sunken", "Sunken eyes", "आँखें धँसी", "डोळे खोल गेले", ["Dehydration"]),
    O("thirsty", "Drinks eagerly / very thirsty", "लालच से पीता / बहुत प्यास", "आतुरतेने पिते / खूप तहान", ["Some dehydration"]),
    O("poor_drink", "Drinks poorly / cannot drink", "ठीक से नहीं पीता / पी नहीं पाता", "नीट पीत नाही / पिऊ शकत नाही", ["Severe dehydration"]),
    O("skin_slow", "Skin pinch goes back slowly", "चुटकी ली त्वचा धीरे लौटती", "चिमटा घेतलेली त्वचा हळू परत जाते", ["Severe dehydration"]),
    O("no_urine", "No urine for 6+ hours / no tears", "6+ घंटे पेशाब नहीं / आँसू नहीं", "6+ तास लघवी नाही / अश्रू नाहीत", ["Severe dehydration"]),
    O("restless", "Restless, irritable / very sleepy", "बेचैन, चिड़चिड़ा / बहुत सुस्त", "अस्वस्थ, चिडचिडे / खूप सुस्त", ["Dehydration"])],
  src=IMNCI)
Q("chd_flag", "child_diarrhoea", "redflag", 3, "yesno", "Cannot drink, skin pinch very slow, very sleepy, or no urine for 6+ hours?",
  "क्या पी नहीं पाता, चुटकी वाली त्वचा बहुत धीरे लौटती, बहुत सुस्त, या 6+ घंटे पेशाब नहीं?", "पिऊ शकत नाही, त्वचा खूप हळू परत जाते, खूप सुस्त, किंवा 6+ तास लघवी नाही?",
  term="Severe dehydration", rf="SEVERE DEHYDRATION — start IV / ORS plan C now", ddx=["Severe dehydration"], applies=KID, src=IMNCI)
Q("chd_hopi", "child_diarrhoea", "hopi", 4, "multi", "Details", "विवरण", "तपशील", term="Diarrhoea / vomiting history", applies=KID, opts=[
    O("blood", "Blood in stool", "मल में ख़ून", "शौचात रक्त", ["Dysentery (Shigella)", "Intussusception"]),
    O("gt14d", "More than 14 days", "14 दिन से ज़्यादा", "14 दिवसांपेक्षा जास्त", ["Persistent diarrhoea", "Malabsorption"]),
    O("green_vomit", "Green (bile) vomiting / belly swollen", "हरी (पित्त) उल्टी / पेट फूला", "हिरवी (पित्त) उलटी / पोट फुगले", ["Intestinal obstruction"]),
    O("colic_jelly", "Episodes of screaming, legs drawn up, 'jelly' stool", "चीखने के दौरे, पैर ऊपर, जेली जैसा मल", "किंचाळण्याचे झटके, पाय पोटाशी, जेलीसारखी शौच", ["Intussusception"]),
    O("rice_water", "Large watery 'rice-water' stools", "बहुत ज़्यादा पानी जैसे 'चावल के पानी' दस्त", "खूप पाण्यासारखे 'तांदळाच्या पाण्यासारखे' जुलाब", ["Cholera"]),
    O("ors_zinc", "ORS / zinc already given", "ORS / ज़िंक पहले दिया", "ORS / झिंक आधी दिले"),
    O("water", "Unsafe drinking water / others in family sick", "असुरक्षित पानी / परिवार में और भी बीमार", "असुरक्षित पाणी / कुटुंबात इतरही आजारी", ["Acute gastroenteritis"])],
  src=f"{CH}, p65; {IMNCI}")
child_background("chd", "child_diarrhoea", 10)

# ---------------------------------------------------------------- NEWBORN (< 2 months)
NB = f"{CH}, p65 (Box 6.2); {IMNCI} (young infant)"
Q("nbn_danger", "newborn", "redflag", 1, "multi", "Danger signs", "ख़तरे के निशान", "धोक्याची चिन्हे", term="Young infant danger signs", applies=BABY, opts=[
    O("not_feeding", "Not feeding well / stopped feeding", "ठीक से दूध नहीं पीता / बंद", "नीट दूध पीत नाही / बंद", ["Neonatal sepsis"]),
    O("fits", "Fits", "दौरा", "झटके", ["Neonatal seizures", "Neonatal sepsis"]),
    O("fast_breath", "Fast breathing (≥60/min) / chest indrawing", "तेज़ साँस (≥60/मिनट) / छाती धँसना", "जलद श्वास (≥60/मिनिट) / छाती आत ओढणे", ["Neonatal sepsis / pneumonia"]),
    O("temp", "Fever (≥37.5°C) or cold (<35.5°C)", "बुखार (≥37.5°C) या ठंडा (<35.5°C)", "ताप (≥37.5°C) किंवा थंड (<35.5°C)", ["Neonatal sepsis", "Hypothermia"]),
    O("no_move", "Moves only when touched / not moving", "छूने पर ही हिलता / नहीं हिलता", "स्पर्श केल्यावरच हलते / हलत नाही", ["Neonatal sepsis"]),
    O("jaundice", "Yellow on day 1, or palms / soles yellow", "पहले दिन पीला, या हथेली / तलवे पीले", "पहिल्या दिवशी पिवळे, किंवा तळहात / तळपाय पिवळे", ["Neonatal jaundice (severe)"]),
    O("cord_skin", "Pus / redness at cord, many skin pustules", "नाल पर मवाद / लाली, त्वचा पर कई फुंसियाँ", "नाळेवर पू / लाली, त्वचेवर अनेक फोड", ["Omphalitis", "Skin infection"])],
  src=NB)
Q("nbn_flag", "newborn", "redflag", 2, "yesno", "Not feeding, fits, fast breathing / indrawing, fever or cold, not moving, or yellow palms / soles?",
  "क्या दूध नहीं पीता, दौरा, तेज़ साँस / छाती धँसना, बुखार या ठंडा, नहीं हिलता, या हथेली / तलवे पीले?",
  "दूध पीत नाही, झटके, जलद श्वास / छाती आत ओढणे, ताप किंवा थंड, हलत नाही, किंवा तळहात / तळपाय पिवळे?",
  term="Possible serious bacterial infection", rf="NEWBORN DANGER SIGN — keep warm, first dose antibiotic, refer to SNCU NOW", ddx=["Neonatal sepsis", "Neonatal jaundice (severe)"],
  applies=BABY, src=NB)
Q("nbn_feed", "newborn", "hopi", 3, "multi", "Feeding", "दूध पिलाना", "दूध पाजणे", term="Feeding history (Box 6.2)", applies=BABY, opts=[
    O("exclusive", "Only breast milk", "सिर्फ़ माँ का दूध", "फक्त आईचे दूध"),
    O("other_milk", "Gives cow / formula milk, water, honey, ghutti", "गाय / डिब्बे का दूध, पानी, शहद, घुट्टी देते", "गाय / डब्याचे दूध, पाणी, मध, घुटी देतात", ["Feeding problem", "Infection risk"]),
    O("poor_latch", "Not attaching well / sucking weakly", "ठीक से नहीं चिपकता / कमज़ोर चूसता", "नीट लागत नाही / कमजोर चोखते", ["Feeding problem"]),
    O("lt8", "Fewer than 8 feeds in 24 h", "24 घंटे में 8 बार से कम", "24 तासांत 8 पेक्षा कमी वेळा", ["Feeding problem"]),
    O("wt_loss", "Not gaining weight / less wet nappies", "वज़न नहीं बढ़ता / कम गीले कपड़े", "वजन वाढत नाही / कमी ओले कपडे", ["Feeding problem", "Low weight"])],
  src=NB)
child_background("nbn", "newborn", 10)

# ---------------------------------------------------------------- GROWTH / FEEDING
GR = f"{CH}, p73-75 (height, weight, growth charts); {IMNCI}"
Q("chg_sam", "child_growth", "redflag", 1, "yesno", "Very thin (visible wasting), swelling of both feet, or MUAC red (<11.5 cm, 6 mo–5 y)?",
  "क्या बहुत दुबला (हड्डियाँ दिखें), दोनों पैरों में सूजन, या MUAC लाल (<11.5 सेमी, 6 माह–5 साल)?",
  "खूप बारीक (हाडे दिसतात), दोन्ही पायांना सूज, किंवा MUAC लाल (<11.5 सेमी, 6 म–5 वर्षे)?",
  term="Severe acute malnutrition", rf="SEVERE ACUTE MALNUTRITION — refer to NRC (check sugar, temperature, infection)", ddx=["Severe acute malnutrition"], applies=UNDER5, src=GR)
Q("chg_diet", "child_growth", "hopi", 2, "multi", "Feeding / diet", "खान-पान", "आहार", term="Dietary history", applies=KID, opts=[
    O("late_solids", "Solids started late (after 6 months) / only milk", "ठोस खाना देर से (6 माह के बाद) / सिर्फ़ दूध", "घन आहार उशिरा (6 महिन्यांनंतर) / फक्त दूध", ["Undernutrition", "Iron deficiency anaemia"]),
    O("few_meals", "Eats less than 3 meals a day / small portions", "दिन में 3 बार से कम / थोड़ा खाता", "दिवसातून 3 पेक्षा कमी वेळा / थोडे खाते", ["Undernutrition"]),
    O("junk_tea", "Mostly biscuits / tea / packaged food", "ज़्यादातर बिस्किट / चाय / पैकेट वाला खाना", "बहुतेक बिस्किटे / चहा / पॅकेट अन्न", ["Undernutrition", "Iron deficiency anaemia"]),
    O("picky_pica", "Eats mud / chalk", "मिट्टी / चॉक खाता", "माती / खडू खाते", ["Iron deficiency anaemia", "Worm infestation"]),
    O("bottle", "Bottle feeding", "बोतल से दूध", "बाटलीने दूध", ["Recurrent diarrhoea"])],
  src=f"{CH}, p65 (Box 6.2-6.3)")
Q("chg_causes", "child_growth", "associated", 3, "multi", "Other clues", "अन्य संकेत", "इतर संकेत", term="Causes of faltering growth", applies=KID, opts=[
    O("recurrent_inf", "Frequent diarrhoea / chest infections", "बार-बार दस्त / छाती का इन्फेक्शन", "वारंवार जुलाब / छातीचा संसर्ग", ["Recurrent infection", "HIV", "Immunodeficiency"]),
    O("tb", "Long cough / fever / TB contact", "लंबी खाँसी / बुखार / टीबी संपर्क", "जुना खोकला / ताप / टीबी संपर्क", ["Tuberculosis"]),
    O("worms", "Worms in stool / no deworming", "मल में कीड़े / कीड़े की दवा नहीं दी", "शौचात जंत / जंताचे औषध नाही", ["Worm infestation"]),
    O("pale", "Pale / tired", "पीला / थका", "फिकट / थकलेले", ["Iron deficiency anaemia", "Thalassaemia"]),
    O("bulky_stool", "Bulky, oily, smelly stools", "भारी, चिकना, बदबूदार मल", "जड, तेलकट, वास येणारी शौच", ["Coeliac disease", "Malabsorption"]),
    O("short_only", "Short but well (parents also short)", "ठिगना पर स्वस्थ (माता-पिता भी ठिगने)", "बुटके पण निरोगी (आई-वडीलही बुटके)", ["Familial short stature"]),
    O("home_stress", "Problems at home / main carer away", "घर में परेशानी / देखभाल करने वाला दूर", "घरी अडचणी / सांभाळणारी व्यक्ती दूर", ["Psychosocial deprivation"])],
  src=GR)
child_background("chg", "child_growth", 10)

# ---------------------------------------------------------------- DEVELOPMENT  (Table 6.1)
DV = f"{CH}, p65-66 (Table 6.1 milestones)"
Q("chv_area", "child_development", "hopi", 1, "multi", "Which area is late?", "कौनसा काम देर से?", "कोणते काम उशिरा?", term="Developmental domains", applies=KID, opts=[
    O("motor", "Head holding / sitting / walking", "गर्दन सँभालना / बैठना / चलना", "मान धरणे / बसणे / चालणे", ["Cerebral palsy", "Global developmental delay", "Muscular disorder"]),
    O("speech", "Talking (no words by 18 months)", "बोलना (18 माह तक कोई शब्द नहीं)", "बोलणे (18 महिन्यांपर्यंत शब्द नाही)", ["Hearing loss", "Autism spectrum disorder", "Speech delay"]),
    O("social", "Poor eye contact / doesn't respond to name / repetitive play", "आँख नहीं मिलाता / नाम पर ध्यान नहीं / एक ही खेल बार-बार", "नजर मिळवत नाही / नावाला प्रतिसाद नाही / एकच खेळ पुन्हा-पुन्हा", ["Autism spectrum disorder"]),
    O("fine_vision", "Hand use / doesn't follow objects with eyes", "हाथ का उपयोग / चीज़ों को आँख से नहीं देखता", "हाताचा वापर / वस्तूंकडे डोळ्यांनी पाहत नाही", ["Visual impairment", "Cerebral palsy"]),
    O("hearing", "Doesn't turn to sounds", "आवाज़ की तरफ़ नहीं मुड़ता", "आवाजाकडे वळत नाही", ["Hearing loss"]),
    O("school", "Learning difficulty at school", "स्कूल में पढ़ाई में कठिनाई", "शाळेत शिकण्यात अडचण", ["Learning disability", "ADHD", "Visual / hearing impairment"])],
  src=DV)
Q("chv_milestones", "child_development", "hopi", 2, "text", "Age when child: smiled, held head, sat, walked, said first words", "किस उम्र में: मुस्कुराया, गर्दन सँभाली, बैठा, चला, पहले शब्द बोले",
  "कोणत्या वयात: हसले, मान धरली, बसले, चालले, पहिले शब्द बोलले", term="Milestones", applies=KID, src=DV)
Q("chv_regression", "child_development", "redflag", 3, "yesno", "Child is LOSING skills already learnt (stopped talking / walking)?", "क्या बच्चा सीखी हुई चीज़ें भूल रहा है (बोलना / चलना बंद)?",
  "मूल शिकलेल्या गोष्टी विसरत आहे का (बोलणे / चालणे बंद)?", term="Developmental regression", rf="Developmental regression — needs prompt paediatric neurology review",
  ddx=["Neurodegenerative disorder", "Autism spectrum disorder (regression)", "Epileptic encephalopathy"], applies=KID, src=DV)
Q("chv_head", "child_development", "associated", 4, "multi", "Other features", "अन्य बातें", "इतर गोष्टी", term="Associated features", applies=KID, opts=[
    O("small_big_head", "Head very small or very big", "सिर बहुत छोटा या बहुत बड़ा", "डोके खूप लहान किंवा खूप मोठे", ["Microcephaly", "Hydrocephalus"]),
    O("fits", "Fits", "दौरे", "झटके", ["Epilepsy", "Cerebral palsy"]),
    O("stiff_floppy", "Stiff or floppy limbs / toe walking", "हाथ-पैर अकड़े या ढीले / पंजों पर चलना", "हात-पाय ताठ किंवा सैल / चवड्यांवर चालणे", ["Cerebral palsy", "Muscular disorder"]),
    O("features", "Unusual face features / heart problem", "चेहरे की अलग बनावट / दिल की समस्या", "चेहऱ्याची वेगळी ठेवण / हृदय समस्या", ["Down syndrome / genetic syndrome"]),
    O("thyroid", "Constipation, dry skin, big tongue, slow", "कब्ज़, रूखी त्वचा, बड़ी जीभ, सुस्त", "बद्धकोष्ठता, कोरडी त्वचा, मोठी जीभ, सुस्त", ["Congenital hypothyroidism"])],
  src=f"{CH}, p75 (Box 6.10); {DV}")
child_background("chv", "child_development", 10)

# ---------------------------------------------------------------- FITS
FT = f"{IMNCI}; {H}, Ch 16"
Q("chs_type", "child_fits", "hopi", 1, "multi", "About the fit", "दौरे के बारे में", "झटक्यांबद्दल", term="Seizure description", applies=KID, opts=[
    O("with_fever", "With fever, age 6 months–5 years, whole body, < 15 min", "बुखार के साथ, 6 माह–5 साल, पूरा शरीर, <15 मिनट", "तापासह, 6 म–5 वर्षे, संपूर्ण शरीर, <15 मिनिटे", ["Simple febrile seizure"]),
    O("long_focal", "Longer than 15 min / one side only / more than once in a day", "15 मिनट से लंबा / एक तरफ / दिन में एक से ज़्यादा बार", "15 मिनिटांपेक्षा जास्त / एकाच बाजूला / दिवसात एकापेक्षा जास्त", ["Complex febrile seizure", "Meningitis / encephalitis", "Epilepsy"]),
    O("no_fever", "Without fever / repeated", "बिना बुखार / बार-बार", "तापाशिवाय / वारंवार", ["Epilepsy"]),
    O("staring", "Staring spells / jerks on waking", "एकटक घूरना / जागने पर झटके", "एकटक पाहणे / उठल्यावर झटके", ["Absence epilepsy", "Myoclonic epilepsy"]),
    O("breath_holding", "After crying, holds breath and goes blue / limp", "रोने के बाद साँस रोककर नीला / ढीला", "रडल्यानंतर श्वास रोखून निळे / सैल", ["Breath-holding spell"]),
    O("head_injury_poison", "After head injury / possible poisoning", "सिर की चोट / ज़हर के बाद", "डोक्याला मार / विषबाधेनंतर", ["Head injury", "Poisoning"])],
  src=FT)
Q("chs_flag", "child_fits", "redflag", 2, "yesno", "Fit lasting > 5 min / still fitting, not waking up after fit, stiff neck, or after head injury?",
  "क्या दौरा 5 मिनट से ज़्यादा / अभी भी, दौरे के बाद होश नहीं, गर्दन अकड़ी, या सिर की चोट के बाद?",
  "झटके 5 मिनिटांपेक्षा जास्त / अजूनही, झटक्यानंतर शुद्ध नाही, मान ताठ, किंवा डोक्याला मारानंतर?",
  term="Status / meningitis / head injury", rf="CHILD SEIZURE EMERGENCY — airway, check sugar, give anticonvulsant per protocol", ddx=["Status epilepticus", "Meningitis / encephalitis", "Hypoglycaemia"],
  applies=KID, src=FT)
Q("chs_hist", "child_fits", "risk", 3, "multi", "Background", "पृष्ठभूमि", "पार्श्वभूमी", term="Seizure risk factors", applies=KID, opts=[
    O("prev_febrile", "Had fits with fever before", "पहले भी बुखार में दौरा", "आधीही तापात झटके", ["Febrile seizure (recurrent)"]),
    O("family", "Fits in family", "परिवार में दौरे", "कुटुंबात झटके", ["Epilepsy", "Febrile seizure"]),
    O("delay", "Developmental delay / birth asphyxia", "विकास में देरी / जन्म पर नहीं रोया", "विकासात उशीर / जन्मतः रडले नाही", ["Epilepsy", "Cerebral palsy"]),
    O("on_drugs", "Already on fit medicine (missed doses?)", "पहले से दौरे की दवा (ख़ुराक छूटी?)", "आधीपासून झटक्यांचे औषध (डोस चुकला?)", ["Epilepsy (poor adherence)"])],
  src=FT)
child_background("chs", "child_fits", 10)

# ---------------------------------------------------------------- CHECK-UP / BEHAVIOUR / SAFEGUARDING  (Box 6.3, 6.9)
Q("chk_habits", "child_checkup", "hopi", 1, "multi", "Habits and behaviour (Box 6.3)", "आदतें और व्यवहार", "सवयी व वर्तन", term="General questions", applies=KID, opts=[
    O("sleep", "Sleep problem / snoring", "नींद की समस्या / खर्राटे", "झोपेची समस्या / घोरणे", ["Adenotonsillar hypertrophy", "Sleep problem"]),
    O("bedwetting", "Bed-wetting after age 5", "5 साल के बाद बिस्तर गीला", "5 वर्षांनंतर अंथरूण ओले", ["Nocturnal enuresis", "UTI", "Diabetes"]),
    O("constipation", "Hard stools / soiling", "सख़्त मल / कपड़ों में मल", "कडक शौच / कपड्यात शौच", ["Functional constipation"]),
    O("hyperactive", "Very restless / can't sit / poor attention", "बहुत चंचल / बैठ नहीं पाता / ध्यान नहीं", "खूप चंचल / बसू शकत नाही / लक्ष नाही", ["ADHD"]),
    O("tantrums", "Severe tantrums / aggression", "बहुत ज़िद / गुस्सा / मारपीट", "खूप हट्ट / राग / मारामारी", ["Behavioural problem"]),
    O("school_refusal", "Refuses school / misses much school", "स्कूल नहीं जाना / बहुत छुट्टी", "शाळेला नकार / खूप गैरहजर", ["Anxiety", "Bullying", "Learning disability"]),
    O("screen", "Screen time > 2 h / mobile habit", "स्क्रीन 2 घंटे से ज़्यादा / मोबाइल की आदत", "स्क्रीन 2 तासांपेक्षा जास्त / मोबाइलची सवय", ["Behavioural problem"])],
  src=f"{CH}, p65 (Box 6.3)")
Q("chk_teen", "child_checkup", "hopi", 2, "yesno", "Teenager: offered a few minutes alone with doctor (confidential: alcohol, drugs, relationships)?",
  "किशोर: क्या डॉक्टर के साथ कुछ मिनट अकेले बात का मौका दिया (गोपनीय)?", "किशोर: डॉक्टरसोबत काही मिनिटे एकट्याने बोलण्याची संधी दिली का (गोपनीय)?",
  term="Adolescent confidential time", applies={"min_age": 11, "max_age": 14}, src=f"{CH}, p64")
Q("chk_safeguard", "child_checkup", "redflag", 3, "yesno", "Sister's observation: injury with no clear explanation, unusual bruises / burns / bites, very fearful child, or clear neglect?",
  "सिस्टर का अवलोकन: बिना ठीक कारण की चोट, अजीब नील / जलन / काटने के निशान, बहुत डरा बच्चा, या साफ़ लापरवाही?",
  "सिस्टरचे निरीक्षण: नीट कारण नसलेली इजा, विचित्र काळे-निळे / भाजणे / चावण्याच्या खुणा, खूप घाबरलेले मूल, किंवा स्पष्ट दुर्लक्ष?",
  term="Safeguarding concern (Box 6.9)", rf="SAFEGUARDING CONCERN — inform doctor privately; do not confront carer; follow hospital child-protection policy",
  ddx=["Possible child maltreatment"], applies=KID, src=f"{CH}, p74 (Box 6.9)")
child_background("chk", "child_checkup", 10)
