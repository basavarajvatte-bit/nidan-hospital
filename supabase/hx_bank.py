"""
Vatte Hospital OS — Nidan question bank, batch 1.
Generates supabase/phase6_questions.sql (run: python3 supabase/hx_bank.py).

Primary reference: Hutchison's Clinical Methods, 24th ed. (Glynn & Drake, Elsevier 2018).
Questions are original wording built from the book's clinical concepts (no textbook text copied).
Page numbers are the printed book pages. Clinical content must be reviewed by the doctor before real use.
"""
import json

H = "Hutchison 24e"
COMPLAINTS, QUESTIONS = [], []


def C(id, system, en, hi, mr, icon, ord, src):
    COMPLAINTS.append(dict(id=id, system=system, name_en=en, name_hi=hi, name_mr=mr, icon=icon, ord=ord, source=src))


def O(v, en, hi, mr, ddx=None):
    o = {"v": v, "en": en, "hi": hi, "mr": mr}
    if ddx:
        o["ddx"] = ddx
    return o


def Q(id, comp, section, ord, qtype, en, hi, mr, term=None, opts=None, key=None, show=None, applies=None,
      rf=None, pos=None, neg=None, ddx=None, src=None):
    QUESTIONS.append(dict(id=id, complaint_id=comp, section=section, ord=ord, qtype=qtype, options=opts,
                          text_en=en, text_hi=hi, text_mr=mr, clinical_term=term, dedupe_key=key, show_if=show,
                          applies_to=applies, red_flag=bool(rf), red_flag_note=rf, positive_means=pos,
                          negative_means=neg, differentials=ddx or [], source=src, active=True))


YES = lambda q: {"q": q, "eq": "yes"}

# ------------------------------------------------------------------ SAFETY SCREEN (asked first)
S9 = f"{H}, Ch 9 (Emergencies), p121-123"
Q("s_breath", None, "safety", 1, "yesno", "Severe breathlessness / struggling to breathe now?",
  "क्या अभी साँस लेने में बहुत तकलीफ़ हो रही है?", "आत्ता श्वास घ्यायला खूप त्रास होतो आहे का?",
  term="Severe respiratory distress", rf="EMERGENCY: severe breathlessness", src=S9)
Q("s_chest", None, "safety", 2, "yesno", "Severe central chest pain or pressure right now?",
  "क्या अभी छाती के बीच में तेज़ दर्द या दबाव है?", "आत्ता छातीच्या मध्यभागी तीव्र दुखणे किंवा दाब आहे का?",
  term="Acute chest pain", rf="EMERGENCY: acute chest pain", src=f"{H}, Ch 13, p189-191")
Q("s_conscious", None, "safety", 3, "yesno", "Drowsy, confused, or not responding normally?",
  "क्या मरीज़ बेहोश, सुस्त या उलझा हुआ है?", "रुग्ण बेशुद्ध, गुंगीत किंवा गोंधळलेला आहे का?",
  term="Altered consciousness", rf="EMERGENCY: altered consciousness", src=S9)
Q("s_stroke", None, "safety", 4, "yesno", "Sudden face droop, arm/leg weakness, or slurred speech?",
  "क्या अचानक चेहरा टेढ़ा, हाथ-पैर में कमज़ोरी या बोली लड़खड़ाई?",
  "अचानक चेहरा वाकडा, हात-पाय कमजोर किंवा बोलणे अडखळले का?",
  term="Suspected stroke", rf="EMERGENCY: suspected stroke", src=f"{H}, Ch 16, p309-310")
Q("s_bleed", None, "safety", 5, "yesno", "Heavy bleeding now (vomiting blood, heavy bleeding from anywhere)?",
  "क्या अभी बहुत खून बह रहा है (खून की उल्टी या कहीं से ज़्यादा खून)?",
  "आत्ता खूप रक्तस्राव होतो आहे का (रक्ताची उलटी किंवा कुठूनही जास्त रक्त)?",
  term="Active severe bleeding", rf="EMERGENCY: active bleeding", src=S9)
Q("s_seizure", None, "safety", 6, "yesno", "Fitting now, or fits that are not stopping?",
  "क्या अभी दौरा (झटके) चल रहा है या रुक नहीं रहा?", "आत्ता झटके येत आहेत का किंवा थांबत नाहीत का?",
  term="Ongoing seizure", rf="EMERGENCY: ongoing seizure", src=f"{H}, Ch 16, p310")
Q("s_allergy", None, "safety", 7, "yesno", "Sudden swelling of face/lips/throat or rash with breathing difficulty?",
  "क्या अचानक चेहरा/होंठ/गला सूजा है या दाने के साथ साँस में तकलीफ़ है?",
  "अचानक चेहरा/ओठ/घसा सुजला आहे का किंवा पुरळासोबत श्वासाचा त्रास आहे का?",
  term="Possible anaphylaxis", rf="EMERGENCY: possible anaphylaxis", src=S9)
Q("s_injury", None, "safety", 8, "yesno", "Serious injury / accident / fall from height?",
  "क्या गंभीर चोट, एक्सीडेंट या ऊँचाई से गिरना हुआ है?", "गंभीर इजा, अपघात किंवा उंचावरून पडणे झाले आहे का?",
  term="Major trauma", rf="EMERGENCY: major trauma", src=S9)
Q("s_shock", None, "safety", 9, "yesno", "Very weak, cold clammy skin, or hardly passing urine with vomiting/diarrhoea?",
  "क्या बहुत कमज़ोरी, ठंडा-पसीने वाला शरीर, या उल्टी-दस्त के साथ पेशाब बहुत कम?",
  "खूप अशक्तपणा, थंड घामट शरीर, किंवा उलटी-जुलाबासोबत लघवी खूप कमी?",
  term="Shock / severe dehydration", rf="EMERGENCY: possible shock / severe dehydration", src=f"{H}, Ch 9, p122-128")
Q("s_harm", None, "safety", 10, "yesno", "Thoughts of harming self or others right now?",
  "क्या अभी खुद को या किसी और को नुकसान पहुँचाने के विचार आ रहे हैं?",
  "आत्ता स्वतःला किंवा दुसऱ्याला इजा करण्याचे विचार येत आहेत का?",
  term="Immediate risk of harm", rf="URGENT: risk of harm — do not leave patient alone", src=f"{H}, Ch 8 (Psychiatric), p99")

# ------------------------------------------------------------------ COMPLAINTS
C("fever", "General", "Fever", "बुखार", "ताप", "🌡️", 1, f"{H}, Ch 10, p141-156")
C("chest_pain", "Cardiovascular", "Chest pain", "छाती में दर्द", "छातीत दुखणे", "💔", 2, f"{H}, Ch 13, p189-192; Ch 12, p169")
C("breathless", "Respiratory", "Breathlessness", "साँस फूलना", "धाप लागणे", "😮‍💨", 3, f"{H}, Ch 12, p167-168; Ch 13, p192-193")
C("cough", "Respiratory", "Cough", "खाँसी", "खोकला", "🤧", 4, f"{H}, Ch 12, p167-170")
C("abd_pain", "Gastrointestinal", "Abdominal pain", "पेट दर्द", "पोटदुखी", "🤢", 5, f"{H}, Ch 14, p241-243")
C("gi_upset", "Gastrointestinal", "Vomiting / loose motions", "उल्टी / दस्त", "उलटी / जुलाब", "🚽", 6, f"{H}, Ch 14, p241-243")
C("headache", "Nervous system", "Headache", "सिर दर्द", "डोकेदुखी", "🤕", 7, f"{H}, Ch 16, p309-312; Ch 10, p146")
C("neuro", "Nervous system", "Weakness / fits / fainting", "कमज़ोरी / दौरा / बेहोशी", "अशक्तपणा / झटके / बेशुद्धी", "🧠", 8, f"{H}, Ch 16, p309-310; Ch 13, p189-190")
C("joint_pain", "Locomotor", "Joint pain / swelling", "जोड़ों में दर्द / सूजन", "सांधेदुखी / सूज", "🦴", 9, f"{H}, Ch 15, p273-282")
C("urinary", "Urogenital", "Urine problems", "पेशाब की तकलीफ़", "लघवीचा त्रास", "💧", 10, f"{H}, Ch 17, p355-358")

ANY = lambda: [O("yes", "Yes", "हाँ", "हो"), O("no", "No", "नहीं", "नाही")]

# ---------- FEVER  (Ch 10, p145-146)
F = f"{H}, Ch 10, p145-146"
Q("fv_pattern", "fever", "hopi", 1, "choice", "Pattern of fever", "बुखार कैसे आता है?", "ताप कसा येतो?",
  term="Fever pattern", opts=[
      O("continuous", "Continuous (stays high)", "लगातार बना रहता है", "सतत राहतो", ["Enteric fever", "Pneumonia", "UTI"]),
      O("comes_goes", "Comes and goes daily", "रोज़ चढ़ता-उतरता है", "रोज चढतो-उतरतो", ["Tuberculosis", "Deep abscess"]),
      O("alternate", "Comes on alternate days / with gaps", "एक-दो दिन छोड़कर आता है", "एक-दोन दिवस सोडून येतो", ["Malaria"]),
      O("evening", "Mostly evening / night", "ज़्यादातर शाम या रात को", "बहुतेक संध्याकाळी / रात्री", ["Tuberculosis", "Lymphoma"])],
  src=f"{H}, Ch 10, p144-145")
Q("fv_rigor", "fever", "hopi", 2, "yesno", "Shivering with chattering teeth (rigors)?",
  "क्या बुखार के साथ तेज़ कँपकँपी (दाँत बजना) आती है?", "तापासोबत जोराची थंडी वाजून दात वाजतात का?",
  term="Rigors", pos="Rapidly rising temperature — malaria or severe bacterial infection",
  ddx=["Malaria", "Sepsis", "Pyelonephritis"], src=F)
Q("fv_antipyretic", "fever", "hopi", 3, "yesno", "Already taken paracetamol / antibiotics / painkillers?",
  "क्या बुखार की दवा, एंटीबायोटिक या दर्द की गोली पहले ले चुके हैं?",
  "तापाचे औषध, अँटिबायोटिक किंवा वेदनाशामक आधीच घेतले आहे का?",
  term="Prior antipyretic/antibiotic use", pos="May mask fever pattern; note drug names", src=F)
Q("fv_headache", "fever", "associated", 4, "yesno", "Headache with stiff neck, dislike of light or vomiting?",
  "क्या सिर दर्द के साथ गर्दन अकड़ना, रोशनी चुभना या उल्टी है?",
  "डोकेदुखीसोबत मान ताठ होणे, प्रकाश सहन न होणे किंवा उलटी आहे का?",
  term="Headache with meningism", rf="Fever with neck stiffness/photophobia — possible meningitis",
  ddx=["Meningitis"], key="meningism", src=F)
Q("fv_myalgia", "fever", "associated", 5, "yesno", "Body aches / joint pains?", "क्या बदन दर्द या जोड़ों में दर्द है?",
  "अंगदुखी किंवा सांधेदुखी आहे का?", term="Myalgia / arthralgia", ddx=["Viral fever", "Dengue", "Malaria", "Chikungunya"], src=F)
Q("fv_rash", "fever", "associated", 6, "yesno", "Any rash or spots on skin?", "क्या शरीर पर दाने या लाल धब्बे हैं?",
  "अंगावर पुरळ किंवा लाल डाग आहेत का?", term="Rash", ddx=["Dengue", "Measles", "Drug reaction", "Typhus"], key="rash", src=F)
Q("fv_bleed", "fever", "redflag", 7, "yesno", "Bleeding from gums/nose, black stools or red spots with fever?",
  "क्या बुखार के साथ मसूड़ों/नाक से खून, काला मल या लाल चकत्ते हैं?",
  "तापासोबत हिरड्या/नाकातून रक्त, काळी शौच किंवा लाल ठिपके आहेत का?",
  term="Bleeding manifestations", rf="Fever with bleeding — possible severe dengue / sepsis", ddx=["Dengue"], src=F)
Q("fv_weightloss", "fever", "associated", 8, "yesno", "Weight loss or night sweats?", "क्या वज़न घटा है या रात को पसीना आता है?",
  "वजन कमी झाले आहे का किंवा रात्री घाम येतो का?", term="Weight loss / night sweats",
  pos="Suggests chronic process", ddx=["Tuberculosis", "Malignancy", "HIV"], key="wt_loss", src=F)
Q("fv_focus", "fever", "associated", 9, "multi", "Any of these along with fever?", "बुखार के साथ इनमें से कुछ?",
  "तापासोबत यापैकी काही?", term="Focal symptoms", opts=[
      O("cough", "Cough", "खाँसी", "खोकला", ["Respiratory infection"]),
      O("burning_urine", "Burning urine", "पेशाब में जलन", "लघवीची जळजळ", ["UTI"]),
      O("loose_motions", "Loose motions", "दस्त", "जुलाब", ["Gastroenteritis", "Enteric fever"]),
      O("abd_pain", "Abdominal pain", "पेट दर्द", "पोटदुखी", ["Enteric fever", "Intra-abdominal infection"]),
      O("jaundice", "Yellow eyes", "आँखें पीली", "डोळे पिवळे", ["Hepatitis", "Leptospirosis", "Malaria"]),
      O("skin_red", "Red painful skin", "त्वचा लाल व दर्द", "त्वचा लाल व दुखरी", ["Cellulitis"]),
      O("ear_throat", "Sore throat / ear pain", "गला/कान दर्द", "घसा/कान दुखणे", ["Pharyngitis", "Otitis"])],
  src=f"{H}, Ch 10, p146")
Q("fv_travel", "fever", "risk", 10, "yesno", "Recent travel or stay away from home?", "क्या हाल में कहीं बाहर यात्रा की है?",
  "अलीकडे बाहरगावी प्रवास केला आहे का?", term="Travel history", src=F)
Q("fv_exposure", "fever", "risk", 11, "multi", "Exposures", "इनमें से कोई संपर्क?", "यापैकी कोणता संपर्क?",
  term="Exposure history", opts=[
      O("tb_contact", "Contact with TB patient", "टीबी मरीज़ से संपर्क", "टीबी रुग्णाशी संपर्क", ["Tuberculosis"]),
      O("flood_water", "Walked in flood / dirty water", "बाढ़/गंदे पानी में चले", "पूर/घाण पाण्यात चालले", ["Leptospirosis"]),
      O("mosquito", "Many mosquitoes at home", "घर में बहुत मच्छर", "घरी खूप डास", ["Malaria", "Dengue"]),
      O("outside_food", "Outside food / unsafe water", "बाहर का खाना / गंदा पानी", "बाहेरचे अन्न / अशुद्ध पाणी", ["Enteric fever", "Hepatitis A/E"]),
      O("animals", "Contact with animals / cattle", "जानवरों से संपर्क", "जनावरांशी संपर्क", ["Brucellosis", "Leptospirosis"]),
      O("sick_contact", "Others at home with fever", "घर में दूसरों को भी बुखार", "घरी इतरांनाही ताप", ["Viral fever", "Dengue"])],
  src=f"{H}, Ch 10, p146")
Q("fv_immuno", "fever", "risk", 12, "multi", "Risk factors for serious infection", "इनमें से कुछ है?", "यापैकी काही आहे का?",
  term="Host risk factors", opts=[
      O("diabetes", "Diabetes", "शुगर (डायबिटीज़)", "मधुमेह", []),
      O("steroids", "Steroids / cancer treatment", "स्टेरॉयड / कैंसर की दवा", "स्टिरॉइड / कर्करोग उपचार", []),
      O("hiv", "Known HIV", "एचआईवी", "एचआयव्ही", []),
      O("recent_hosp", "Hospital stay / operation in last month", "पिछले महीने भर्ती/ऑपरेशन", "मागील महिन्यात भरती/ऑपरेशन", []),
      O("rhd", "Heart valve disease / rheumatic fever", "दिल का वाल्व रोग / रूमेटिक बुखार", "हृदयाच्या झडपेचा आजार", ["Infective endocarditis"])],
  src=f"{H}, Ch 10, p146")

# ---------- CHEST PAIN  (Ch 13 p189-192, Ch 12 p169)
CP = f"{H}, Ch 13, p189-192"
Q("cp_site", "chest_pain", "hopi", 1, "choice", "Where is the pain?", "दर्द कहाँ है?", "दुखणे कुठे आहे?", term="Site", opts=[
    O("central", "Centre of chest (behind breastbone)", "छाती के बीच में", "छातीच्या मध्यभागी", ["Angina / ACS", "Pericarditis", "Reflux / GORD"]),
    O("side", "One side of chest", "छाती के एक तरफ", "छातीच्या एका बाजूला", ["Pleurisy", "Pneumothorax", "Musculoskeletal"]),
    O("back", "Between shoulder blades / back", "पीठ में / कंधों के बीच", "पाठीत / खांद्यांमध्ये", ["Aortic dissection"]),
    O("upper_abd", "Upper abdomen / below ribs", "पेट के ऊपरी हिस्से में", "पोटाच्या वरच्या भागात", ["Peptic ulcer", "Biliary", "Inferior MI"])],
  src=CP)
Q("cp_character", "chest_pain", "hopi", 2, "choice", "What does the pain feel like?", "दर्द कैसा है?", "दुखणे कसे आहे?",
  term="Character", opts=[
      O("heavy", "Heaviness / tightness / pressure", "भारीपन / जकड़न / दबाव", "जडपणा / आवळल्यासारखे / दाब", ["Angina / ACS"]),
      O("sharp_breath", "Sharp, worse on deep breath or cough", "चुभन, गहरी साँस या खाँसी पर बढ़े", "टोचल्यासारखे, दीर्घ श्वास/खोकल्यावर वाढते", ["Pleurisy", "Pericarditis", "Pulmonary embolism"]),
      O("tearing", "Sudden tearing pain", "अचानक फटने जैसा दर्द", "अचानक फाटल्यासारखे दुखणे", ["Aortic dissection"]),
      O("burning", "Burning", "जलन", "जळजळ", ["Reflux / GORD", "ACS (atypical)"]),
      O("pressing_spot", "Sore on pressing one spot", "एक जगह दबाने पर दर्द", "एका जागी दाबल्यावर दुखते", ["Musculoskeletal"])],
  src=CP)
Q("cp_radiation", "chest_pain", "hopi", 3, "yesno", "Does the pain spread to arm, neck, jaw or back?",
  "क्या दर्द बाँह, गर्दन, जबड़े या पीठ की तरफ जाता है?", "दुखणे हात, मान, जबडा किंवा पाठीकडे जाते का?",
  term="Radiation to arm/neck/jaw", ddx=["Angina / ACS", "Aortic dissection"], src=CP)
Q("cp_exertion", "chest_pain", "hopi", 4, "yesno", "Comes on walking/exertion and settles with rest within minutes?",
  "क्या चलने/मेहनत पर दर्द होता है और आराम करने से कुछ मिनट में ठीक हो जाता है?",
  "चालताना/श्रम केल्यावर दुखते आणि विश्रांतीने काही मिनिटांत थांबते का?",
  term="Exertional, relieved by rest", pos="Typical of angina", neg="Makes stable angina less likely",
  ddx=["Angina / ACS"], src=f"{H}, Ch 13, p190")
Q("cp_rest_long", "chest_pain", "redflag", 5, "yesno", "Pain at rest lasting more than 15–20 minutes?",
  "क्या आराम में भी दर्द 15-20 मिनट से ज़्यादा रहा?", "विश्रांतीतही दुखणे 15-20 मिनिटांपेक्षा जास्त राहिले का?",
  term="Prolonged rest pain", rf="Prolonged rest chest pain — possible acute coronary syndrome (ECG now)",
  ddx=["Angina / ACS"], src=f"{H}, Ch 13, p191")
Q("cp_sweat", "chest_pain", "redflag", 6, "yesno", "Sweating, vomiting or fainting with the pain?",
  "क्या दर्द के साथ पसीना, उल्टी या चक्कर/बेहोशी आई?", "दुखण्यासोबत घाम, उलटी किंवा चक्कर/बेशुद्धी आली का?",
  term="Autonomic features / syncope", rf="Chest pain with sweating/syncope — possible MI",
  ddx=["Angina / ACS", "Pulmonary embolism", "Aortic dissection"], src=f"{H}, Ch 13, p191")
Q("cp_posture", "chest_pain", "hopi", 7, "yesno", "Worse lying flat and better sitting forward?",
  "क्या लेटने पर दर्द बढ़ता है और आगे झुककर बैठने से कम होता है?", "आडवे झोपल्यावर वाढते आणि पुढे वाकून बसल्यावर कमी होते का?",
  term="Positional (pericarditic) pain", ddx=["Pericarditis"], show={"q": "cp_character", "in": ["sharp_breath"]}, src=f"{H}, Ch 13, p191")
Q("cp_meals", "chest_pain", "hopi", 8, "yesno", "Related to meals, lying down after food, or sour water in mouth?",
  "क्या खाने के बाद, लेटने पर या मुँह में खट्टा पानी आने के साथ दर्द होता है?",
  "जेवणानंतर, आडवे झाल्यावर किंवा तोंडात आंबट पाणी येण्यासोबत दुखते का?",
  term="Meal-related / reflux", ddx=["Reflux / GORD", "Peptic ulcer"], src=f"{H}, Ch 14, p241")
Q("cp_breathless", "chest_pain", "associated", 9, "yesno", "Breathless with the pain?", "क्या दर्द के साथ साँस फूलती है?",
  "दुखण्यासोबत धाप लागते का?", term="Associated dyspnoea", ddx=["Angina / ACS", "Pulmonary embolism", "Pneumothorax", "Heart failure"], key="dyspnoea", src=CP)
Q("cp_palp", "chest_pain", "associated", 10, "yesno", "Heart racing / pounding?", "क्या दिल तेज़ धड़कता है?",
  "छातीत धडधड होते का?", term="Palpitations", ddx=["Arrhythmia"], key="palpitations", src=f"{H}, Ch 13, p190")
Q("cp_pe_risk", "chest_pain", "risk", 11, "multi", "Clot (embolism) risk factors", "इनमें से कुछ हुआ है?", "यापैकी काही झाले आहे का?",
  term="Thromboembolic risk factors", opts=[
      O("surgery", "Recent operation", "हाल में ऑपरेशन", "अलीकडे ऑपरेशन", ["Pulmonary embolism"]),
      O("bedrest", "Bed-ridden / leg in plaster", "बिस्तर पर पड़े रहे / पैर में प्लास्टर", "अंथरुणाला खिळलेले / पायाला प्लास्टर", ["Pulmonary embolism"]),
      O("long_travel", "Long journey (>6 hours)", "लंबी यात्रा (6 घंटे से ज़्यादा)", "लांब प्रवास (6 तासांहून जास्त)", ["Pulmonary embolism"]),
      O("leg_swelling", "One leg swollen / painful", "एक पैर में सूजन/दर्द", "एका पायाला सूज/दुखणे", ["Pulmonary embolism"]),
      O("cancer", "Cancer", "कैंसर", "कर्करोग", ["Pulmonary embolism"])],
  src=f"{H}, Ch 13, p192")
Q("cp_cv_risk", "chest_pain", "risk", 12, "multi", "Heart disease risk factors", "इनमें से कुछ है?", "यापैकी काही आहे का?",
  term="Cardiovascular risk factors", key="cv_risk", opts=[
      O("htn", "High BP", "हाई बीपी", "उच्च रक्तदाब", ["Angina / ACS", "Aortic dissection"]),
      O("dm", "Diabetes", "शुगर", "मधुमेह", ["Angina / ACS"]),
      O("smoke", "Smoking / tobacco", "धूम्रपान / तंबाकू", "धूम्रपान / तंबाखू", ["Angina / ACS"]),
      O("lipids", "High cholesterol", "कोलेस्ट्रॉल ज़्यादा", "कोलेस्टेरॉल जास्त", ["Angina / ACS"]),
      O("fh", "Heart attack in family before 55–60", "परिवार में कम उम्र में हार्ट अटैक", "कुटुंबात कमी वयात हार्ट अटॅक", ["Angina / ACS"]),
      O("prev_mi", "Previous heart attack / angioplasty", "पहले हार्ट अटैक / एंजियोप्लास्टी", "आधी हार्ट अटॅक / अँजिओप्लास्टी", ["Angina / ACS"])],
  src=f"{H}, Ch 13, p189-190")

# ---------- BREATHLESSNESS  (Ch 12 p167-168, Ch 13 p192-193)
B = f"{H}, Ch 12, p167-168"
Q("br_onset", "breathless", "hopi", 1, "choice", "How did it start?", "साँस फूलना कैसे शुरू हुआ?", "धाप कशी सुरू झाली?",
  term="Onset", opts=[
      O("sudden", "Suddenly (minutes)", "अचानक (कुछ मिनट में)", "अचानक (काही मिनिटांत)", ["Pulmonary embolism", "Pneumothorax", "Acute LVF", "Anaphylaxis", "Asthma attack"]),
      O("days", "Over days", "कुछ दिनों में", "काही दिवसांत", ["Pneumonia", "COPD exacerbation", "Pleural effusion"]),
      O("months", "Slowly over months", "महीनों में धीरे-धीरे", "महिन्यांत हळूहळू", ["COPD", "Heart failure", "Anaemia", "Interstitial lung disease"])],
  src=f"{H}, Ch 12, p168 (Box 12.1)")
Q("br_grade", "breathless", "hopi", 2, "choice", "How much activity brings it on?", "कितना काम करने पर साँस फूलती है?",
  "किती श्रमाने धाप लागते?", term="MRC dyspnoea grade", opts=[
      O("1", "Only heavy exercise", "सिर्फ़ भारी मेहनत पर", "फक्त जड श्रमाने"),
      O("2", "Walking fast / uphill", "तेज़ चलने / चढ़ाई पर", "भरभर चालताना / चढावर"),
      O("3", "Slower than others on level ground", "समतल पर भी दूसरों से धीमे", "सपाट जमिनीवरही इतरांपेक्षा हळू"),
      O("4", "Stops after ~100 metres", "100 मीटर पर रुकना पड़ता है", "100 मीटरवर थांबावे लागते"),
      O("5", "Breathless dressing / at rest", "कपड़े पहनते या आराम में भी", "कपडे घालताना किंवा विश्रांतीतही")],
  src=f"{H}, Ch 12, p168 (Box 12.2)")
Q("br_orthopnoea", "breathless", "hopi", 3, "yesno", "Breathless lying flat (needs more pillows)?",
  "क्या सीधा लेटने पर साँस फूलती है (ज़्यादा तकिए चाहिए)?", "सरळ झोपल्यावर धाप लागते का (जास्त उशा लागतात)?",
  term="Orthopnoea", ddx=["Heart failure"], src=f"{H}, Ch 13, p192-193")
Q("br_pnd", "breathless", "hopi", 4, "yesno", "Wakes up at night gasping for breath?", "क्या रात को साँस फूलने से नींद खुलती है?",
  "रात्री धाप लागून जाग येते का?", term="Paroxysmal nocturnal dyspnoea", ddx=["Heart failure", "Asthma"], src=f"{H}, Ch 13, p193")
Q("br_wheeze", "breathless", "associated", 5, "yesno", "Whistling / wheezing sound in chest?", "क्या छाती से सीटी जैसी आवाज़ आती है?",
  "छातीतून शिट्टीसारखा आवाज येतो का?", term="Wheeze", ddx=["Asthma", "COPD", "Heart failure"], key="wheeze", src=B)
Q("br_ankle", "breathless", "associated", 6, "yesno", "Swelling of both ankles/feet?", "क्या दोनों पैरों/टखनों में सूजन है?",
  "दोन्ही पायांना/घोट्यांना सूज आहे का?", term="Bilateral ankle oedema", ddx=["Heart failure", "Kidney disease", "Liver disease"], src=f"{H}, Ch 13, p193")
Q("br_chestpain", "breathless", "associated", 7, "yesno", "Chest pain with breathlessness?", "क्या साँस फूलने के साथ छाती में दर्द है?",
  "धापेसोबत छातीत दुखते का?", term="Associated chest pain", ddx=["Pulmonary embolism", "Pneumothorax", "Angina / ACS"], src=B)
Q("br_speech", "breathless", "redflag", 8, "yesno", "Unable to complete a sentence / lips turning blue?",
  "क्या पूरा वाक्य नहीं बोल पा रहे / होंठ नीले पड़ रहे हैं?", "पूर्ण वाक्य बोलता येत नाही / ओठ निळे पडत आहेत का?",
  term="Severe distress / cyanosis", rf="Severe breathlessness / cyanosis — urgent oxygen & doctor", src=f"{H}, Ch 12, p171")
Q("br_day_night", "breathless", "hopi", 9, "yesno", "Worse at night / early morning?", "क्या रात या सुबह-सुबह ज़्यादा तकलीफ़ होती है?",
  "रात्री किंवा पहाटे जास्त त्रास होतो का?", term="Diurnal variation", ddx=["Asthma"], src=B)
Q("br_smoke", "breathless", "risk", 10, "yesno", "Smoker now or before (bidi/cigarette/chulha smoke)?",
  "क्या बीड़ी/सिगरेट पीते हैं या पहले पीते थे (या चूल्हे का धुआँ)?", "बिडी/सिगारेट ओढता का किंवा आधी ओढत होता (किंवा चुलीचा धूर)?",
  term="Smoking / biomass exposure", ddx=["COPD", "Lung cancer"], key="smoking", src=f"{H}, Ch 12, p169-170")
Q("br_occup", "breathless", "risk", 11, "text", "Work / dust exposure (past and present jobs)", "कौन-सा काम करते हैं / धूल-धुएँ में काम?",
  "काय काम करता / धूळ-धुरात काम?", term="Occupational history", src=f"{H}, Ch 12, p170 (Box 12.7-12.8)")

# ---------- COUGH  (Ch 12 p167-170)
CO = f"{H}, Ch 12, p167-169"
Q("co_duration", "cough", "hopi", 1, "choice", "How long has the cough been there?", "खाँसी कब से है?", "खोकला कधीपासून आहे?",
  term="Duration", opts=[
      O("lt3w", "Less than 3 weeks", "3 हफ़्ते से कम", "3 आठवड्यांपेक्षा कमी", ["Acute respiratory infection"]),
      O("3to8w", "3–8 weeks", "3 से 8 हफ़्ते", "3 ते 8 आठवडे", ["Post-viral cough", "Tuberculosis"]),
      O("gt8w", "More than 8 weeks", "8 हफ़्ते से ज़्यादा", "8 आठवड्यांपेक्षा जास्त", ["Tuberculosis", "Asthma", "COPD", "GORD", "Lung cancer"])],
  src=f"{H}, Ch 12, p167-168")
Q("co_sputum", "cough", "hopi", 2, "choice", "Phlegm (balgam)?", "बलगम आता है?", "कफ येतो का?", term="Sputum", opts=[
    O("dry", "Dry cough", "सूखी खाँसी", "कोरडा खोकला", ["Asthma", "Viral", "ACE-inhibitor"]),
    O("white", "White / clear", "सफ़ेद / साफ़", "पांढरा / स्वच्छ", ["COPD", "Viral"]),
    O("yellow_green", "Yellow / green", "पीला / हरा", "पिवळा / हिरवा", ["Bacterial infection", "Bronchiectasis"]),
    O("large_daily", "Large amount every day", "रोज़ बहुत ज़्यादा", "रोज खूप जास्त", ["Bronchiectasis"])],
  src=f"{H}, Ch 12, p168, p179")
Q("co_blood", "cough", "redflag", 3, "yesno", "Blood in the phlegm / coughing up blood?", "क्या बलगम में खून या खाँसी में खून आता है?",
  "कफात रक्त किंवा खोकल्यात रक्त येते का?", term="Haemoptysis", rf="Haemoptysis — needs chest X-ray / TB work-up",
  ddx=["Tuberculosis", "Lung cancer", "Pulmonary embolism", "Bronchiectasis"], src=f"{H}, Ch 12, p168-169 (Box 12.6)")
Q("co_time", "cough", "hopi", 4, "yesno", "Worse at night?", "क्या रात को खाँसी ज़्यादा होती है?", "रात्री खोकला जास्त होतो का?",
  term="Nocturnal cough", ddx=["Asthma", "GORD", "Heart failure"], src=f"{H}, Ch 12, p167")
Q("co_postnasal", "cough", "associated", 5, "yesno", "Runny/blocked nose or something dripping down throat?",
  "क्या नाक बहना/बंद या गले में कुछ टपकता लगता है?", "नाक वाहणे/बंद किंवा घशात काही ठिबकते असे वाटते का?",
  term="Post-nasal drip / rhinitis", ddx=["Post-nasal drip", "Allergic rhinitis"], src=f"{H}, Ch 12, p168-169")
Q("co_reflux", "cough", "associated", 6, "yesno", "Acidity / heartburn?", "क्या एसिडिटी या सीने में जलन होती है?",
  "ॲसिडिटी किंवा छातीत जळजळ होते का?", term="Heartburn", ddx=["GORD"], key="heartburn", src=f"{H}, Ch 12, p168 (Box 12.4)")
Q("co_tb", "cough", "associated", 7, "yesno", "Evening fever, weight loss or night sweats?", "क्या शाम को बुखार, वज़न घटना या रात को पसीना है?",
  "संध्याकाळी ताप, वजन घटणे किंवा रात्री घाम येतो का?", term="Constitutional symptoms", ddx=["Tuberculosis", "Lung cancer"], key="wt_loss", src=CO)
Q("co_voice", "cough", "associated", 8, "yesno", "Change / hoarseness of voice?", "क्या आवाज़ बदली या बैठ गई है?", "आवाज बदलला किंवा बसला आहे का?",
  term="Hoarseness", ddx=["Laryngitis", "Lung cancer (recurrent laryngeal nerve)"], src=f"{H}, Ch 12, p169")
Q("co_ace", "cough", "risk", 9, "yesno", "Taking BP tablet ending in '-pril' (e.g. enalapril, ramipril)?",
  "क्या बीपी की गोली (जैसे एनालाप्रिल, रामिप्रिल) लेते हैं?", "बीपीची गोळी (उदा. एनालाप्रिल, रामिप्रिल) घेता का?",
  term="ACE-inhibitor use", ddx=["ACE-inhibitor cough"], src=f"{H}, Ch 12, p168 (Box 12.3)")
Q("co_tbcontact", "cough", "risk", 10, "yesno", "Anyone at home with TB, or had TB before?", "क्या घर में किसी को टीबी है या पहले आपको टीबी हुई थी?",
  "घरी कोणाला टीबी आहे का किंवा आधी तुम्हाला टीबी झाला होता का?", term="TB contact / previous TB", ddx=["Tuberculosis"], key="tb_hist", src=f"{H}, Ch 10, p146")
Q("co_smoke", "cough", "risk", 11, "yesno", "Smoker now or before (bidi/cigarette/chulha smoke)?",
  "क्या बीड़ी/सिगरेट पीते हैं या पहले पीते थे (या चूल्हे का धुआँ)?", "बिडी/सिगारेट ओढता का किंवा आधी ओढत होता (किंवा चुलीचा धूर)?",
  term="Smoking / biomass exposure", ddx=["COPD", "Lung cancer"], key="smoking", src=f"{H}, Ch 12, p169-170")

# ---------- ABDOMINAL PAIN  (Ch 14 p242-243, Box 14.2)
A = f"{H}, Ch 14, p242-243 (Box 14.2)"
Q("ab_site", "abd_pain", "hopi", 1, "choice", "Where is the pain mainly?", "दर्द मुख्य रूप से कहाँ है?", "दुखणे मुख्यतः कुठे आहे?",
  term="Site", opts=[
      O("epigastric", "Upper middle (epigastric)", "ऊपर बीच में (नाभि के ऊपर)", "वर मध्यभागी (बेंबीच्या वर)", ["Peptic ulcer / gastritis", "Pancreatitis", "Inferior MI"]),
      O("ruq", "Upper right", "ऊपर दाईं तरफ", "वर उजवीकडे", ["Biliary colic / cholecystitis", "Hepatitis"]),
      O("periumbilical", "Around the navel", "नाभि के आसपास", "बेंबीभोवती", ["Early appendicitis", "Small bowel (midgut)"]),
      O("rif", "Lower right", "नीचे दाईं तरफ", "खाली उजवीकडे", ["Appendicitis", "Ureteric colic", "Ovarian / ectopic"]),
      O("lif", "Lower left", "नीचे बाईं तरफ", "खाली डावीकडे", ["Colitis / diverticular", "Ureteric colic", "Ovarian / ectopic"]),
      O("suprapubic", "Lower middle (above pubic bone)", "नीचे बीच में", "खाली मध्यभागी", ["Cystitis / UTI", "Urinary retention", "Pelvic"]),
      O("loin", "Side / back (loin)", "कमर के बगल में", "कमरेच्या बाजूला", ["Renal colic / stone", "Pyelonephritis"]),
      O("generalised", "All over", "पूरे पेट में", "संपूर्ण पोटात", ["Gastroenteritis", "Peritonitis", "Obstruction"])],
  src=A)
Q("ab_character", "abd_pain", "hopi", 2, "choice", "Type of pain", "दर्द कैसा है?", "दुखणे कसे आहे?", term="Character", opts=[
    O("colicky", "Comes in waves (colicky)", "लहरों में आता-जाता (मरोड़)", "लाटांसारखे येते-जाते (मुरडा)", ["Renal colic / stone", "Biliary colic / cholecystitis", "Obstruction"]),
    O("burning", "Burning / gnawing", "जलन / कुतरने जैसा", "जळजळ / कुरतडल्यासारखे", ["Peptic ulcer / gastritis"]),
    O("constant", "Constant, steady", "लगातार एक जैसा", "सतत एकसारखे", ["Appendicitis", "Pancreatitis", "Peritonitis"])],
  src=A)
Q("ab_migrate", "abd_pain", "hopi", 3, "yesno", "Did the pain start around the navel and move to lower right?",
  "क्या दर्द नाभि से शुरू होकर नीचे दाईं तरफ चला गया?", "दुखणे बेंबीपासून सुरू होऊन खाली उजवीकडे गेले का?",
  term="Migratory pain to RIF", ddx=["Appendicitis"], show={"q": "ab_site", "in": ["rif", "periumbilical"]}, src=A)
Q("ab_radiation", "abd_pain", "hopi", 4, "choice", "Does the pain go anywhere?", "क्या दर्द कहीं और जाता है?", "दुखणे दुसरीकडे जाते का?",
  term="Radiation", opts=[
      O("none", "No", "नहीं", "नाही"),
      O("back", "Straight through to back", "पीठ की तरफ आर-पार", "पाठीकडे आरपार", ["Pancreatitis", "Peptic ulcer (posterior)", "Aortic aneurysm"]),
      O("r_shoulder", "Right shoulder", "दाएँ कंधे में", "उजव्या खांद्यात", ["Biliary colic / cholecystitis"]),
      O("groin", "Loin to groin", "कमर से जांघ/अंडकोष की तरफ", "कमरेपासून जांघेकडे", ["Renal colic / stone"])],
  src=A)
Q("ab_food", "abd_pain", "hopi", 5, "choice", "Relation to food", "खाने से संबंध", "जेवणाशी संबंध", term="Relation to meals", opts=[
    O("none", "No relation", "कोई संबंध नहीं", "संबंध नाही"),
    O("hunger_relief_food", "Worse when hungry, better after food", "भूखे पेट बढ़ता, खाने से आराम", "उपाशीपोटी वाढते, जेवल्यावर आराम", ["Peptic ulcer / gastritis"]),
    O("after_food", "Worse after food (esp. oily)", "खाने के बाद (खासकर तला) बढ़ता", "जेवणानंतर (विशेषतः तेलकट) वाढते", ["Biliary colic / cholecystitis", "Pancreatitis", "Gastric ulcer"])],
  src=A)
Q("ab_vomit", "abd_pain", "associated", 6, "yesno", "Nausea or vomiting?", "क्या जी मिचलाना या उल्टी है?", "मळमळ किंवा उलटी आहे का?",
  term="Nausea / vomiting", ddx=["Appendicitis", "Biliary colic / cholecystitis", "Pancreatitis", "Obstruction", "Renal colic / stone"], key="vomiting", src=A)
Q("ab_bowel", "abd_pain", "associated", 7, "choice", "Bowel habit", "पाखाना (मल) कैसा है?", "शौच कसे होते?", term="Bowel habit", key="bowel", opts=[
    O("normal", "Normal", "सामान्य", "सामान्य"),
    O("loose", "Loose motions", "दस्त", "जुलाब", ["Gastroenteritis", "Colitis"]),
    O("constipated", "Constipation", "कब्ज़", "बद्धकोष्ठता", ["Constipation", "Obstruction"]),
    O("no_gas", "No stool and no gas passed", "न मल न गैस निकल रही", "शौच व गॅस दोन्ही बंद", ["Obstruction"])],
  src=f"{H}, Ch 14, p242")
Q("ab_obstruct", "abd_pain", "redflag", 8, "yesno", "Bloated belly with vomiting and no stool/gas?",
  "क्या पेट फूला है, उल्टी है और मल/गैस नहीं निकल रही?", "पोट फुगले आहे, उलटी आहे आणि शौच/गॅस होत नाही का?",
  term="Features of obstruction", rf="Possible intestinal obstruction", ddx=["Obstruction"], src=f"{H}, Ch 14, p242")
Q("ab_blood", "abd_pain", "redflag", 9, "yesno", "Blood vomiting, black tarry stool or blood in stool?",
  "क्या खून की उल्टी, काला चिपचिपा मल या मल में खून है?", "रक्ताची उलटी, काळी डांबरासारखी शौच किंवा शौचात रक्त आहे का?",
  term="GI bleeding", rf="GI bleeding with abdominal pain", ddx=["Peptic ulcer / gastritis", "Colitis"], key="gi_bleed", src=f"{H}, Ch 14, p242-243")
Q("ab_jaundice", "abd_pain", "associated", 10, "yesno", "Yellow eyes / dark urine / pale stools?", "क्या आँखें पीली, पेशाब गहरा या मल सफ़ेद है?",
  "डोळे पिवळे, लघवी गडद किंवा शौच पांढरी आहे का?", term="Jaundice", ddx=["Hepatitis", "Biliary colic / cholecystitis"], key="jaundice", src=f"{H}, Ch 14, p243")
Q("ab_urine", "abd_pain", "associated", 11, "yesno", "Burning urine or blood in urine?", "क्या पेशाब में जलन या खून है?",
  "लघवीत जळजळ किंवा रक्त आहे का?", term="Urinary symptoms", ddx=["Cystitis / UTI", "Renal colic / stone", "Pyelonephritis"], key="dysuria", src=f"{H}, Ch 14, p243; Ch 17")
Q("ab_lmp", "abd_pain", "associated", 12, "yesno", "Periods late / missed, or chance of pregnancy?",
  "क्या माहवारी देर से या रुकी है, या गर्भ की संभावना है?", "मासिक पाळी उशिरा/चुकली आहे का किंवा गर्भधारणेची शक्यता आहे का?",
  term="Possible pregnancy", rf="Abdominal pain + possible pregnancy — exclude ectopic", ddx=["Ovarian / ectopic"],
  applies={"sex": "female", "min_age": 12, "max_age": 55}, key="pregnancy", src=f"{H}, Ch 5 (Women), p45")
Q("ab_alcohol", "abd_pain", "risk", 13, "yesno", "Drinks alcohol regularly?", "क्या नियमित शराब पीते हैं?", "नियमित दारू पिता का?",
  term="Alcohol", ddx=["Pancreatitis", "Peptic ulcer / gastritis", "Hepatitis"], key="alcohol", src=f"{H}, Ch 1, p9-10")
Q("ab_nsaid", "abd_pain", "risk", 14, "yesno", "Taking painkillers often (e.g. diclofenac, ibuprofen)?",
  "क्या दर्द की गोलियाँ अक्सर लेते हैं (जैसे डाइक्लोफेनाक)?", "वेदनाशामक गोळ्या वारंवार घेता का (उदा. डायक्लोफेनाक)?",
  term="NSAID use", ddx=["Peptic ulcer / gastritis"], key="nsaid", src=f"{H}, Ch 1, p9")

# ---------- VOMITING / DIARRHOEA  (Ch 14 p241-243)
G = f"{H}, Ch 14, p241-242"
Q("gi_main", "gi_upset", "hopi", 1, "multi", "Main problem", "मुख्य तकलीफ़", "मुख्य त्रास", term="Main GI symptoms", opts=[
    O("vomiting", "Vomiting", "उल्टी", "उलटी"), O("loose", "Loose motions", "दस्त", "जुलाब"),
    O("nausea", "Nausea only", "सिर्फ़ जी मिचलाना", "फक्त मळमळ")], src=G)
Q("gi_freq", "gi_upset", "hopi", 2, "number", "Number of loose motions / vomits in last 24 hours",
  "पिछले 24 घंटे में कितनी बार दस्त/उल्टी हुई?", "मागील 24 तासांत किती वेळा जुलाब/उलटी झाली?", term="Frequency in 24 h", src=G)
Q("gi_stool_blood", "gi_upset", "redflag", 3, "yesno", "Blood or mucus in stool?", "क्या मल में खून या आँव है?",
  "शौचात रक्त किंवा आव आहे का?", term="Blood / mucus per rectum", rf="Bloody diarrhoea — dysentery / colitis",
  ddx=["Dysentery", "Colitis"], key="gi_bleed", show={"q": "gi_main", "has": "loose"}, src=f"{H}, Ch 14, p242")
Q("gi_watery", "gi_upset", "hopi", 4, "yesno", "Profuse watery (rice-water) stools?", "क्या बहुत ज़्यादा पानी जैसे दस्त हैं?",
  "खूप पाण्यासारखे जुलाब आहेत का?", term="Profuse watery diarrhoea", ddx=["Cholera / secretory diarrhoea", "Gastroenteritis"],
  show={"q": "gi_main", "has": "loose"}, src=G)
Q("gi_vomit_blood", "gi_upset", "redflag", 5, "yesno", "Blood or coffee-coloured material in vomit?", "क्या उल्टी में खून या कॉफ़ी जैसा रंग है?",
  "उलटीत रक्त किंवा कॉफीसारखा रंग आहे का?", term="Haematemesis", rf="Haematemesis — upper GI bleed",
  ddx=["Peptic ulcer / gastritis", "Varices"], show={"q": "gi_main", "has": "vomiting"}, src=f"{H}, Ch 14, p242")
Q("gi_dehyd", "gi_upset", "redflag", 6, "yesno", "Very thirsty, dry mouth, dizzy on standing, or very little urine?",
  "क्या बहुत प्यास, मुँह सूखना, खड़े होने पर चक्कर या पेशाब बहुत कम?", "खूप तहान, तोंड कोरडे, उभे राहिल्यावर चक्कर किंवा लघवी खूप कमी?",
  term="Dehydration", rf="Significant dehydration", src=f"{H}, Ch 9, p128")
Q("gi_food", "gi_upset", "risk", 7, "yesno", "Others who ate the same food also sick / outside food?",
  "क्या एक जैसा खाना खाने वाले और लोग भी बीमार हैं / बाहर का खाना?", "तेच अन्न खाल्लेले इतरही आजारी आहेत का / बाहेरचे अन्न?",
  term="Food exposure", ddx=["Food poisoning", "Gastroenteritis"], src=G)
Q("gi_painless_vomit", "gi_upset", "associated", 8, "yesno", "Vomiting without tummy pain, with headache or drowsiness?",
  "क्या बिना पेट दर्द के उल्टी, साथ में सिर दर्द या सुस्ती?", "पोटदुखीशिवाय उलटी, सोबत डोकेदुखी किंवा गुंगी?",
  term="Painless vomiting with neuro symptoms", rf="Vomiting with headache/drowsiness — raised intracranial pressure?",
  ddx=["Raised intracranial pressure", "Metabolic (DKA, uraemia)"], show={"q": "gi_main", "has": "vomiting"}, src=f"{H}, Ch 14, p242")
Q("gi_chronic", "gi_upset", "hopi", 9, "yesno", "Loose motions for more than 2–4 weeks?", "क्या दस्त 2-4 हफ़्ते से ज़्यादा से हैं?",
  "जुलाब 2-4 आठवड्यांपेक्षा जास्त काळ आहेत का?", term="Chronic diarrhoea", ddx=["IBD", "Malabsorption", "TB abdomen", "Giardiasis"],
  show={"q": "gi_main", "has": "loose"}, src=f"{H}, Ch 14, p242")
Q("gi_wtloss", "gi_upset", "associated", 10, "yesno", "Weight loss or poor appetite?", "क्या वज़न घटा है या भूख कम है?",
  "वजन कमी झाले आहे का किंवा भूक कमी आहे का?", term="Weight loss / anorexia", ddx=["Malignancy", "IBD", "Tuberculosis"], key="wt_loss", src=f"{H}, Ch 14, p242")

# ---------- HEADACHE  (Ch 16 p310-311, Ch 10 p146)
HD = f"{H}, Ch 16, p310-311"
Q("hd_onset", "headache", "hopi", 1, "choice", "How did it start?", "सिर दर्द कैसे शुरू हुआ?", "डोकेदुखी कशी सुरू झाली?", term="Onset", opts=[
    O("thunderclap", "Suddenly, worst ever (like a blow)", "अचानक, ज़िंदगी का सबसे तेज़ (जैसे हथौड़ा लगा)", "अचानक, आयुष्यातील सर्वात तीव्र (हातोडा मारल्यासारखे)", ["Subarachnoid haemorrhage"]),
    O("gradual", "Gradually", "धीरे-धीरे", "हळूहळू", ["Tension-type", "Migraine", "Sinusitis"]),
    O("recurrent", "Comes in attacks (has had before)", "बार-बार दौरे जैसे आता है", "पुन्हा पुन्हा झटक्यांसारखे येते", ["Migraine", "Cluster headache"])],
  src=f"{H}, Ch 1, p8; Ch 16, p310")
Q("hd_worst", "headache", "redflag", 2, "yesno", "Sudden 'worst headache of life'?", "क्या अचानक ज़िंदगी का सबसे तेज़ सिर दर्द हुआ?",
  "अचानक आयुष्यातील सर्वात तीव्र डोकेदुखी झाली का?", term="Thunderclap headache", rf="Thunderclap headache — exclude subarachnoid haemorrhage",
  ddx=["Subarachnoid haemorrhage"], src=f"{H}, Ch 1, p8")
Q("hd_meningism", "headache", "redflag", 3, "yesno", "Headache with fever, stiff neck or dislike of light?",
  "क्या सिर दर्द के साथ बुखार, गर्दन अकड़ना या रोशनी चुभना है?", "डोकेदुखीसोबत ताप, मान ताठ होणे किंवा प्रकाश सहन न होणे आहे का?",
  term="Meningism", rf="Headache with fever/neck stiffness — possible meningitis", ddx=["Meningitis"], key="meningism", src=f"{H}, Ch 10, p146")
Q("hd_neuro", "headache", "redflag", 4, "yesno", "Weakness, fits, confusion, or double vision with headache?",
  "क्या सिर दर्द के साथ कमज़ोरी, दौरा, उलझन या दोहरा दिखना?", "डोकेदुखीसोबत अशक्तपणा, झटके, गोंधळ किंवा दोन-दोन दिसणे?",
  term="Focal neurological symptoms", rf="Headache with neurological deficit", ddx=["Intracranial lesion", "Stroke"], src=f"{H}, Ch 16, p310")
Q("hd_morning", "headache", "hopi", 5, "yesno", "Worse in the morning / on coughing or bending, with vomiting?",
  "क्या सुबह, खाँसने या झुकने पर ज़्यादा, साथ में उल्टी?", "सकाळी, खोकताना किंवा वाकल्यावर जास्त, सोबत उलटी?",
  term="Features of raised ICP", rf="Possible raised intracranial pressure", ddx=["Raised intracranial pressure"], src=f"{H}, Ch 16, p310-311")
Q("hd_migraine", "headache", "hopi", 6, "multi", "Features of the attack", "सिर दर्द के साथ क्या होता है?", "डोकेदुखीसोबत काय होते?",
  term="Associated features", opts=[
      O("one_side", "One side of head", "सिर के एक तरफ", "डोक्याच्या एका बाजूला", ["Migraine"]),
      O("throbbing", "Throbbing", "धक-धक करता", "ठसठसणारे", ["Migraine"]),
      O("light", "Light/noise bother", "रोशनी/आवाज़ बुरी लगे", "प्रकाश/आवाज सहन होत नाही", ["Migraine"]),
      O("nausea", "Nausea", "जी मिचलाना", "मळमळ", ["Migraine"]),
      O("aura", "Flashing lights / zig-zag before", "पहले चमकती रोशनी / टेढ़ी लकीरें", "आधी चमकणारे प्रकाश / वाकड्या रेषा", ["Migraine"]),
      O("band", "Tight band around head", "सिर के चारों ओर पट्टी जैसा कसाव", "डोक्याभोवती पट्टा आवळल्यासारखे", ["Tension-type"]),
      O("eye_red_tears", "Eye pain, red eye, watering on one side", "एक तरफ आँख में दर्द/लाली/पानी", "एका बाजूला डोळा दुखणे/लाल/पाणी", ["Cluster headache", "Acute glaucoma"]),
      O("face_sinus", "Over cheeks/forehead with blocked nose", "गाल/माथे पर, नाक बंद के साथ", "गाल/कपाळावर, नाक बंदसोबत", ["Sinusitis"])],
  src=f"{H}, Ch 16, p310-311")
Q("hd_age_new", "headache", "redflag", 7, "yesno", "New headache after age 50, with scalp tenderness or jaw pain on chewing?",
  "क्या 50 की उम्र के बाद नया सिर दर्द, सिर छूने पर दर्द या चबाने पर जबड़ा दुखना?", "50 वयानंतर नवीन डोकेदुखी, डोक्याला स्पर्श केल्यावर दुखणे किंवा चावताना जबडा दुखणे?",
  term="New headache >50 / GCA features", rf="Possible giant cell arteritis — risk to vision", ddx=["Giant cell arteritis"],
  applies={"min_age": 50}, src=f"{H}, Ch 10, p146; Ch 16")
Q("hd_painkiller", "headache", "risk", 8, "yesno", "Taking painkillers for headache on most days?", "क्या ज़्यादातर दिन सिर दर्द की गोली लेते हैं?",
  "बहुतेक दिवस डोकेदुखीची गोळी घेता का?", term="Analgesic overuse", ddx=["Medication-overuse headache"], src=f"{H}, Ch 16")
Q("hd_bp", "headache", "risk", 9, "yesno", "Known high BP?", "क्या हाई बीपी है?", "उच्च रक्तदाब आहे का?", term="Hypertension",
  ddx=["Hypertensive headache"], key="htn", src=f"{H}, Ch 13")

# ---------- WEAKNESS / FITS / FAINTING  (Ch 16 p309-310, Ch 13 p190)
N = f"{H}, Ch 16, p309-310"
Q("nr_type", "neuro", "hopi", 1, "multi", "What happened?", "क्या हुआ?", "काय झाले?", term="Presenting neurological event", opts=[
    O("weakness", "Weakness of arm/leg/face", "हाथ/पैर/चेहरे में कमज़ोरी", "हात/पाय/चेहऱ्यात अशक्तपणा"),
    O("fit", "Fit / jerking", "दौरा / झटके", "झटके / आकडी"),
    O("faint", "Fainted / blacked out", "बेहोश हो गए", "बेशुद्ध झाले"),
    O("dizzy", "Dizziness / spinning", "चक्कर / घूमना", "चक्कर / गरगरणे"),
    O("numb", "Numbness / tingling", "सुन्नपन / झुनझुनी", "बधिरपणा / मुंग्या")], src=N)
Q("nr_sudden", "neuro", "redflag", 2, "yesno", "Did the weakness come on suddenly (within minutes)?",
  "क्या कमज़ोरी अचानक (कुछ मिनट में) आई?", "अशक्तपणा अचानक (काही मिनिटांत) आला का?", term="Sudden-onset deficit",
  rf="Sudden weakness — possible stroke (note exact time last seen well)", ddx=["Stroke / TIA"], show={"q": "nr_type", "has": "weakness"}, src=N)
Q("nr_time", "neuro", "hopi", 3, "text", "Time patient was last seen normal", "मरीज़ को आख़िरी बार कब ठीक देखा था (समय)?",
  "रुग्णाला शेवटचे सामान्य कधी पाहिले (वेळ)?", term="Last seen well", show={"q": "nr_type", "has": "weakness"}, src=N)
Q("nr_speech", "neuro", "associated", 4, "yesno", "Speech or swallowing difficulty?", "क्या बोलने या निगलने में तकलीफ़ है?",
  "बोलायला किंवा गिळायला त्रास आहे का?", term="Dysarthria / dysphasia / dysphagia", ddx=["Stroke / TIA"], src=f"{H}, Ch 16, p310 (Box 16.1)")
Q("nr_witness", "neuro", "hopi", 5, "multi", "Witness description of the episode", "देखने वाले ने क्या बताया?", "पाहणाऱ्याने काय सांगितले?",
  term="Witness account", show={"q": "nr_type", "in_any": ["fit", "faint"]}, opts=[
      O("warning_light", "Felt light-headed / sweaty before", "पहले चक्कर / पसीना आया", "आधी चक्कर / घाम आला", ["Syncope"]),
      O("quick_recovery", "Recovered within a minute", "एक मिनट में होश आ गया", "एका मिनिटात शुद्धीवर आले", ["Syncope"]),
      O("stiff_jerk", "Stiffened and jerked", "शरीर अकड़ा और झटके आए", "शरीर ताठ होऊन झटके आले", ["Seizure"]),
      O("tongue", "Tongue bite", "जीभ कटी", "जीभ चावली", ["Seizure"]),
      O("urine", "Passed urine", "पेशाब निकल गया", "लघवी झाली", ["Seizure"]),
      O("confused_after", "Confused / sleepy for long after", "बाद में देर तक उलझन / नींद", "नंतर बराच वेळ गोंधळ / झोप", ["Seizure"]),
      O("exertion", "Happened during exertion", "मेहनत करते समय हुआ", "श्रम करताना झाले", ["Cardiac syncope (arrhythmia / aortic stenosis)"])],
  src=f"{H}, Ch 16, p310 (Table 16.1); Ch 13, p190")
Q("nr_palp", "neuro", "redflag", 6, "yesno", "Palpitations or chest pain before blacking out?", "क्या बेहोश होने से पहले धड़कन तेज़ या छाती में दर्द हुआ?",
  "बेशुद्ध होण्याआधी धडधड किंवा छातीत दुखले का?", term="Cardiac prodrome", rf="Syncope with palpitations/chest pain — cardiac cause?",
  ddx=["Cardiac syncope (arrhythmia / aortic stenosis)"], key="palpitations", show={"q": "nr_type", "has": "faint"}, src=f"{H}, Ch 13, p190")
Q("nr_vertigo", "neuro", "hopi", 7, "yesno", "Room spinning, worse on moving head?", "क्या कमरा घूमता लगता है, सिर हिलाने पर बढ़ता है?",
  "खोली फिरते असे वाटते का, डोके हलवल्यावर वाढते का?", term="Vertigo", ddx=["BPPV / vestibular", "Posterior circulation stroke"],
  show={"q": "nr_type", "has": "dizzy"}, src=f"{H}, Ch 16, p310")
Q("nr_sugar", "neuro", "risk", 8, "yesno", "Diabetic on insulin/tablets, missed meal?", "क्या शुगर की दवा/इंसुलिन लेते हैं और खाना छूटा?",
  "मधुमेहाचे औषध/इन्सुलिन घेता आणि जेवण चुकले का?", term="Hypoglycaemia risk", rf="Check blood sugar now",
  ddx=["Hypoglycaemia"], src=f"{H}, Ch 9; Ch 18")
Q("nr_cv_risk", "neuro", "risk", 9, "multi", "Stroke risk factors", "इनमें से कुछ है?", "यापैकी काही आहे का?", term="Vascular risk factors",
  key="cv_risk", opts=[
      O("htn", "High BP", "हाई बीपी", "उच्च रक्तदाब", ["Stroke / TIA"]), O("dm", "Diabetes", "शुगर", "मधुमेह", ["Stroke / TIA"]),
      O("smoke", "Smoking / tobacco", "धूम्रपान / तंबाकू", "धूम्रपान / तंबाखू", ["Stroke / TIA"]),
      O("af", "Irregular heartbeat", "दिल की धड़कन अनियमित", "हृदयाचे ठोके अनियमित", ["Stroke / TIA"]),
      O("prev_stroke", "Previous stroke", "पहले लकवा", "आधी पक्षाघात", ["Stroke / TIA"])],
  src=f"{H}, Ch 13, p190")

# ---------- JOINT PAIN  (Ch 15 p278-282)
J = f"{H}, Ch 15, p278-281"
Q("jt_number", "joint_pain", "hopi", 1, "choice", "How many joints?", "कितने जोड़ों में दर्द है?", "किती सांध्यांमध्ये दुखते?",
  term="Pattern of joint involvement", opts=[
      O("one", "One joint", "एक जोड़", "एक सांधा", ["Gout", "Septic arthritis", "Injury", "Osteoarthritis"]),
      O("few", "2–4 joints", "2 से 4 जोड़", "2 ते 4 सांधे", ["Reactive arthritis", "Spondyloarthritis"]),
      O("many", "Many joints (both sides)", "कई जोड़ (दोनों तरफ)", "अनेक सांधे (दोन्ही बाजूंना)", ["Rheumatoid arthritis", "Viral arthritis (e.g. chikungunya)", "SLE"])],
  src=f"{H}, Ch 15, p280 (Box 15.3)")
Q("jt_hot", "joint_pain", "redflag", 2, "yesno", "Single hot, red, very painful swollen joint with fever?",
  "क्या एक जोड़ गर्म, लाल, बहुत दर्दनाक, सूजा है और बुखार भी?", "एक सांधा गरम, लाल, खूप दुखरा, सुजलेला आणि तापही आहे का?",
  term="Acute hot joint", rf="Hot swollen joint — exclude septic arthritis", ddx=["Septic arthritis", "Gout"], src=f"{H}, Ch 15, p280 (Box 15.6)")
Q("jt_morning", "joint_pain", "hopi", 3, "yesno", "Morning stiffness lasting more than 30 minutes?", "क्या सुबह जोड़ों की अकड़न आधे घंटे से ज़्यादा रहती है?",
  "सकाळी सांधे अर्ध्या तासापेक्षा जास्त ताठ राहतात का?", term="Prolonged early-morning stiffness", pos="Inflammatory arthritis",
  neg="Favours mechanical/degenerative", ddx=["Rheumatoid arthritis", "Spondyloarthritis"], src=f"{H}, Ch 15, p278-279")
Q("jt_use", "joint_pain", "hopi", 4, "yesno", "Pain worse with use and better with rest (knees/hips)?", "क्या चलने/काम से दर्द बढ़ता, आराम से घटता है?",
  "चालल्यावर/कामाने दुखणे वाढते आणि विश्रांतीने कमी होते का?", term="Mechanical pain", ddx=["Osteoarthritis"], src=f"{H}, Ch 15, p278")
Q("jt_bigtoe", "joint_pain", "hopi", 5, "yesno", "Sudden severe pain in big toe or one joint, can't bear touch?",
  "क्या अचानक पैर के अंगूठे या एक जोड़ में इतना दर्द कि छूना भी सहन न हो?", "अचानक पायाच्या अंगठ्यात किंवा एका सांध्यात इतके दुखणे की स्पर्शही सहन होत नाही?",
  term="Acute monoarthritis (podagra)", ddx=["Gout"], src=f"{H}, Ch 15, p280 (Box 15.4)")
Q("jt_flitting", "joint_pain", "hopi", 6, "yesno", "Pain moving from one joint to another?", "क्या दर्द एक जोड़ से दूसरे जोड़ में घूमता है?",
  "दुखणे एका सांध्यातून दुसऱ्या सांध्यात फिरते का?", term="Flitting / migratory arthritis", ddx=["Rheumatic fever", "Gonococcal arthritis"], src=f"{H}, Ch 15, p280")
Q("jt_back", "joint_pain", "hopi", 7, "yesno", "Low back pain and stiffness worse in morning, better with exercise (young person)?",
  "क्या कमर दर्द और अकड़न सुबह ज़्यादा, कसरत से आराम (कम उम्र में)?", "कंबरदुखी व ताठपणा सकाळी जास्त, व्यायामाने आराम (कमी वयात)?",
  term="Inflammatory back pain", ddx=["Spondyloarthritis"], src=f"{H}, Ch 15, p280")
Q("jt_extra", "joint_pain", "associated", 8, "multi", "Any of these too?", "इनमें से कुछ और भी?", "यापैकी काही आणखी?", term="Extra-articular features", opts=[
    O("fever", "Fever", "बुखार", "ताप", ["Viral arthritis (e.g. chikungunya)", "Septic arthritis", "Rheumatic fever"]),
    O("rash", "Rash", "दाने", "पुरळ", ["SLE", "Viral arthritis (e.g. chikungunya)", "Psoriatic arthritis"]),
    O("eye", "Red / painful eyes", "आँखें लाल/दर्द", "डोळे लाल/दुखणे", ["Reactive arthritis", "Spondyloarthritis"]),
    O("urethral", "Burning urine / discharge", "पेशाब में जलन / स्राव", "लघवीची जळजळ / स्राव", ["Reactive arthritis", "Gonococcal arthritis"]),
    O("diarrhoea", "Recent loose motions", "हाल में दस्त", "अलीकडे जुलाब", ["Reactive arthritis"]),
    O("mouth_ulcers", "Mouth ulcers / hair fall", "मुँह में छाले / बाल झड़ना", "तोंडात फोड / केस गळणे", ["SLE"])],
  src=f"{H}, Ch 15, p286 (Box 15.11)")
Q("jt_injury", "joint_pain", "hopi", 9, "yesno", "Started after injury / fall?", "क्या चोट या गिरने के बाद शुरू हुआ?", "इजा किंवा पडल्यानंतर सुरू झाले का?",
  term="Trauma", ddx=["Injury / fracture"], src=f"{H}, Ch 15, p284 (Box 15.9)")
Q("jt_night", "joint_pain", "redflag", 10, "yesno", "Bone pain at night with weight loss, or back pain with leg weakness/urine problem?",
  "क्या रात को हड्डी में दर्द और वज़न घटना, या कमर दर्द के साथ पैरों में कमज़ोरी/पेशाब की दिक्कत?",
  "रात्री हाडदुखी व वजन घटणे, किंवा कंबरदुखीसोबत पायात अशक्तपणा/लघवीचा त्रास?",
  term="Red flags for bone/back pain", rf="Night pain/weight loss or cord symptoms — malignancy/infection/cord compression?",
  ddx=["Malignancy (bone)", "Spinal TB", "Cord compression"], src=f"{H}, Ch 11, p160; Ch 15, p303 (Box 15.22)")

# ---------- URINARY  (Ch 17 p355-358)
U = f"{H}, Ch 17, p355-356"
Q("ur_symptoms", "urinary", "hopi", 1, "multi", "Which problems?", "कौन-सी तकलीफ़?", "कोणता त्रास?", term="Urinary symptoms", opts=[
    O("burning", "Burning / pain while passing urine", "पेशाब में जलन/दर्द", "लघवी करताना जळजळ/दुखणे", ["Cystitis / UTI"]),
    O("frequency", "Going very often", "बार-बार पेशाब", "वारंवार लघवी", ["Cystitis / UTI", "Diabetes", "Prostate enlargement"]),
    O("night", "Waking at night to pass urine", "रात को बार-बार उठना", "रात्री वारंवार उठणे", ["Prostate enlargement", "Diabetes", "Heart failure"]),
    O("poor_stream", "Weak stream / straining / dribbling", "धार कमज़ोर / ज़ोर लगाना / बूँद-बूँद", "धार कमकुवत / जोर लावणे / थेंब-थेंब", ["Prostate enlargement", "Urethral stricture"]),
    O("cannot_pass", "Cannot pass urine", "पेशाब बिल्कुल नहीं हो रहा", "लघवी अजिबात होत नाही", ["Acute urinary retention"]),
    O("large_amount", "Passing large amounts, very thirsty", "बहुत ज़्यादा पेशाब और प्यास", "खूप लघवी व खूप तहान", ["Diabetes", "Diabetes insipidus"]),
    O("leak", "Leaking urine", "पेशाब रिसना", "लघवी गळणे", ["Incontinence"])],
  src=f"{H}, Ch 17, p355-356")
Q("ur_blood", "urinary", "redflag", 2, "yesno", "Blood in urine?", "क्या पेशाब में खून है?", "लघवीत रक्त आहे का?", term="Haematuria",
  rf="Haematuria — needs evaluation (stone/infection/tumour)", ddx=["Renal colic / stone", "Cystitis / UTI", "Urothelial tumour", "Glomerulonephritis"],
  src=f"{H}, Ch 17, p356 (Box 17.1)")
Q("ur_loin", "urinary", "associated", 3, "yesno", "Pain in side/back (loin) or fever with shivering?", "क्या कमर के बगल में दर्द या कँपकँपी के साथ बुखार?",
  "कमरेच्या बाजूला दुखणे किंवा थंडी वाजून ताप?", term="Loin pain / fever", rf="Possible pyelonephritis / obstructed infected kidney",
  ddx=["Pyelonephritis", "Renal colic / stone"], src=f"{H}, Ch 17, p355")
Q("ur_retention", "urinary", "redflag", 4, "yesno", "Unable to pass urine with painful swollen lower belly?",
  "क्या पेशाब रुका है और नीचे पेट फूला व दर्द है?", "लघवी अडकली आहे आणि खालचे पोट फुगले व दुखते आहे का?",
  term="Acute urinary retention", rf="Acute urinary retention — catheter needed", ddx=["Acute urinary retention"],
  show={"q": "ur_symptoms", "has": "cannot_pass"}, src=f"{H}, Ch 17, p356")
Q("ur_swelling", "urinary", "associated", 5, "yesno", "Puffy face/eyes in morning or swollen feet, frothy urine?",
  "क्या सुबह चेहरा/आँखें सूजी, पैरों में सूजन या झागदार पेशाब?", "सकाळी चेहरा/डोळे सुजलेले, पायांना सूज किंवा फेसाळ लघवी?",
  term="Oedema / frothy urine", ddx=["Glomerulonephritis / nephrotic syndrome"], src=f"{H}, Ch 17, p356-358")
Q("ur_discharge", "urinary", "associated", 6, "yesno", "Discharge from urine passage / genital sores?", "क्या पेशाब की जगह से स्राव या गुप्तांग पर छाले?",
  "मूत्रमार्गातून स्राव किंवा गुप्तांगावर फोड?", term="Urethral discharge / genital ulcer", ddx=["STI"], src=f"{H}, Ch 17, p369 (Box 17.4)")
Q("ur_recurrent", "urinary", "risk", 7, "yesno", "Had urine infection or kidney stone before?", "क्या पहले पेशाब का इन्फेक्शन या पथरी हुई थी?",
  "आधी लघवीचा संसर्ग किंवा मुतखडा झाला होता का?", term="Previous UTI / stones", ddx=["Renal colic / stone", "Cystitis / UTI"], src=U)

# ------------------------------------------------------------------ GENERAL HISTORY (asked once per session)
G1 = f"{H}, Ch 1, p7-10 (Box 1.6-1.13)"
Q("pm_conditions", None, "past", 1, "multi", "Past illnesses", "पहले की बीमारियाँ", "आधीचे आजार", term="Past medical history", opts=[
    O("dm", "Diabetes", "शुगर", "मधुमेह"), O("htn", "High BP", "हाई बीपी", "उच्च रक्तदाब"),
    O("tb", "Tuberculosis", "टीबी", "क्षयरोग"), O("asthma", "Asthma / COPD", "दमा", "दमा"),
    O("heart", "Heart disease", "दिल की बीमारी", "हृदयरोग"), O("kidney", "Kidney disease", "किडनी की बीमारी", "मूत्रपिंड आजार"),
    O("liver", "Liver disease / jaundice", "लिवर / पीलिया", "यकृत / कावीळ"), O("epilepsy", "Fits / epilepsy", "मिर्गी", "आकडी / अपस्मार"),
    O("thyroid", "Thyroid", "थायराइड", "थायरॉईड"), O("stroke", "Stroke", "लकवा", "पक्षाघात"), O("cancer", "Cancer", "कैंसर", "कर्करोग")],
  src=G1)
Q("pm_surgery", None, "past", 2, "text", "Previous operations / hospital admissions (what, when)", "पहले के ऑपरेशन / भर्ती (क्या, कब)",
  "आधीची ऑपरेशन / भरती (काय, कधी)", term="Past surgical history", src=G1)
Q("dr_current", None, "drug", 3, "text", "Current medicines (name, dose, how often) — include from other doctors, chemist, ayurvedic/herbal",
  "अभी कौन-सी दवाएँ लेते हैं (नाम, कितनी, कितनी बार) — दूसरे डॉक्टर, केमिस्ट, आयुर्वेदिक भी",
  "सध्या कोणती औषधे घेता (नाव, किती, किती वेळा) — इतर डॉक्टर, केमिस्ट, आयुर्वेदिकसुद्धा", term="Drug history", src=f"{H}, Ch 1, p9 (Box 1.9)")
Q("dr_stopped", None, "drug", 4, "yesno", "Any medicine started or stopped recently?", "क्या हाल में कोई दवा शुरू या बंद की?",
  "अलीकडे कोणते औषध सुरू किंवा बंद केले का?", term="Recent medication change", src=f"{H}, Ch 1, p9 (Box 1.9)")
Q("al_drug", None, "allergy", 5, "text", "Allergy to any medicine / food — and what happened?", "किसी दवा/खाने से एलर्जी — क्या हुआ था?",
  "कोणत्या औषध/अन्नाची ॲलर्जी — काय झाले होते?", term="Allergies and reaction", src=G1)
Q("fh_conditions", None, "family", 6, "multi", "Illness in family (parents, brothers, sisters, children)", "परिवार में बीमारी (माता-पिता, भाई-बहन, बच्चे)",
  "कुटुंबातील आजार (आई-वडील, भावंडे, मुले)", term="Family history", opts=[
      O("dm", "Diabetes", "शुगर", "मधुमेह"), O("htn", "High BP", "हाई बीपी", "उच्च रक्तदाब"),
      O("heart", "Heart attack / sudden death", "हार्ट अटैक / अचानक मृत्यु", "हार्ट अटॅक / अचानक मृत्यू"),
      O("cancer", "Cancer", "कैंसर", "कर्करोग"), O("tb", "TB", "टीबी", "टीबी"), O("other", "Other", "अन्य", "इतर")],
  src=f"{H}, Ch 1, p9 (Box 1.10)")
Q("ps_tobacco", None, "personal", 7, "choice", "Tobacco", "तंबाकू / बीड़ी / सिगरेट", "तंबाखू / बिडी / सिगारेट", term="Tobacco", key="smoking", opts=[
    O("never", "Never", "कभी नहीं", "कधीच नाही"), O("current_smoke", "Smokes now", "अभी पीते हैं", "सध्या ओढतात"),
    O("ex", "Stopped", "छोड़ दिया", "सोडले"), O("chew", "Chews tobacco / gutka", "तंबाकू / गुटखा खाते हैं", "तंबाखू / गुटखा खातात")],
  src=f"{H}, Ch 1; Ch 12, p169")
Q("ps_alcohol", None, "personal", 8, "choice", "Alcohol", "शराब", "दारू", term="Alcohol", key="alcohol", opts=[
    O("never", "Never", "कभी नहीं", "कधीच नाही"), O("occasional", "Occasionally", "कभी-कभी", "कधी कधी"),
    O("daily", "Daily / heavy", "रोज़ / ज़्यादा", "रोज / जास्त"), O("stopped", "Stopped", "छोड़ दी", "सोडली")],
  src=f"{H}, Ch 1, p9-10 (Box 1.11)")
Q("ps_cage", None, "personal", 9, "multi", "CAGE screen", "शराब के बारे में", "दारूबद्दल", term="CAGE",
  show={"q": "ps_alcohol", "in": ["daily", "occasional"]}, opts=[
      O("cut", "Felt should Cut down", "कम करने का मन हुआ", "कमी करावी असे वाटले"),
      O("annoyed", "Annoyed by criticism", "लोग टोकें तो बुरा लगता है", "लोकांनी टोकल्यावर राग येतो"),
      O("guilty", "Felt Guilty", "पीकर पछतावा", "पिऊन अपराधी वाटते"),
      O("eye_opener", "Eye-opener (morning drink)", "सुबह उठते ही पीना", "सकाळी उठताच पिणे")],
  src=f"{H}, Ch 1, p10 (Box 1.13)")
Q("ps_occupation", None, "personal", 10, "text", "Occupation / work", "काम-धंधा", "व्यवसाय / काम", term="Occupation", src=f"{H}, Ch 1, p9")
Q("ps_diet_sleep", None, "personal", 11, "multi", "Lifestyle", "रहन-सहन", "जीवनशैली", term="Diet / sleep / activity", opts=[
    O("veg", "Vegetarian", "शाकाहारी", "शाकाहारी"), O("poor_sleep", "Poor sleep", "नींद कम", "झोप कमी"),
    O("no_exercise", "No exercise", "कोई व्यायाम नहीं", "व्यायाम नाही"), O("lives_alone", "Lives alone", "अकेले रहते हैं", "एकटे राहतात")],
  src=f"{H}, Ch 1, p7 (Box 1.5)")
Q("ice_ideas", None, "ice", 12, "text", "Ideas: what does the patient think is causing this?", "आपको क्या लगता है, यह किस वजह से हो रहा है?",
  "तुम्हाला काय वाटते, हे कशामुळे होत आहे?", term="Ideas (ICE)", src=f"{H}, Ch 1, p7")
Q("ice_concerns", None, "ice", 13, "text", "Concerns: what worries the patient most?", "आपको सबसे ज़्यादा किस बात की चिंता है?",
  "तुम्हाला सर्वात जास्त कशाची काळजी वाटते?", term="Concerns (ICE)", src=f"{H}, Ch 1, p7")
Q("ice_expect", None, "ice", 14, "text", "Expectations: what does the patient hope for today?", "आज आप डॉक्टर से क्या उम्मीद करते हैं?",
  "आज तुम्ही डॉक्टरांकडून काय अपेक्षा करता?", term="Expectations (ICE)", src=f"{H}, Ch 1, p7")
Q("ros_general", None, "ros", 15, "multi", "Review of systems — any of these recently?", "हाल में इनमें से कुछ?", "अलीकडे यापैकी काही?",
  term="Review of systems", opts=[
      O("fever", "Fever", "बुखार", "ताप"), O("wt_loss", "Weight loss", "वज़न घटना", "वजन कमी"), O("wt_gain", "Weight gain", "वज़न बढ़ना", "वजन वाढ"),
      O("appetite", "Poor appetite", "भूख कम", "भूक कमी"), O("night_sweats", "Night sweats", "रात को पसीना", "रात्री घाम"),
      O("fatigue", "Tiredness", "थकान", "थकवा"), O("cough", "Cough", "खाँसी", "खोकला"), O("breathless", "Breathlessness", "साँस फूलना", "धाप"),
      O("chest_pain", "Chest pain", "छाती में दर्द", "छातीत दुखणे"), O("palpitation", "Palpitations", "धड़कन तेज़", "धडधड"),
      O("ankle", "Ankle swelling", "पैरों में सूजन", "पायांना सूज"), O("abd_pain", "Abdominal pain", "पेट दर्द", "पोटदुखी"),
      O("bowel", "Change in bowel habit", "पाखाने में बदलाव", "शौचात बदल"), O("urine", "Urine problems", "पेशाब की तकलीफ़", "लघवीचा त्रास"),
      O("joint", "Joint pain", "जोड़ों में दर्द", "सांधेदुखी"), O("headache", "Headache", "सिर दर्द", "डोकेदुखी"),
      O("dizzy", "Dizziness / fainting", "चक्कर / बेहोशी", "चक्कर / बेशुद्धी"), O("vision", "Vision problem", "नज़र की दिक्कत", "दृष्टीचा त्रास"),
      O("skin", "Skin rash", "त्वचा पर दाने", "त्वचेवर पुरळ"), O("mood", "Low mood / anxiety", "उदासी / घबराहट", "उदासी / चिंता")],
  src=f"{H}, Ch 1, p8 (Box 1.7)")
Q("ob_lmp", None, "obstetric", 16, "text", "Last menstrual period (date) and cycle regularity", "आख़िरी माहवारी कब हुई थी? नियमित है?",
  "शेवटची मासिक पाळी कधी आली होती? नियमित आहे का?", term="LMP / cycle", applies={"sex": "female", "min_age": 11, "max_age": 55},
  src=f"{H}, Ch 5 (Women), p45-48")
Q("ob_pregnant", None, "obstetric", 17, "choice", "Pregnancy status", "क्या गर्भवती हैं?", "गर्भवती आहात का?", term="Pregnancy status",
  key="pregnancy", applies={"sex": "female", "min_age": 11, "max_age": 55}, opts=[
      O("no", "No", "नहीं", "नाही"), O("yes", "Yes", "हाँ", "हो"), O("not_sure", "Not sure", "पता नहीं", "माहीत नाही")],
  src=f"{H}, Ch 5 (Women), p45")


# ------------------------------------------------------------------ SYSTEM MODULES (one file per body system)
import pathlib as _pl
for _f in ["hx_cvs.py"]:
    exec((_pl.Path(__file__).parent / _f).read_text(encoding="utf-8"))

# Questions replaced by better ones (never deleted, only switched off)
RETIRED = {"cp_exertion": "replaced by cp_triggers + cp_relief (CVS phase)",
           "cp_meals": "replaced by cp_triggers + cp_relief (CVS phase)",
           "cp_posture": "replaced by cp_triggers/cp_relief options (CVS phase)"}
for _q in QUESTIONS:
    if _q["id"] in RETIRED:
        _q["active"] = False

# One name per condition so the doctor's "possibilities" list adds up correctly
DDX_ALIAS = {"Peptic ulcer": "Peptic ulcer / gastritis", "Gastric ulcer": "Peptic ulcer / gastritis",
             "Anxiety": "Anxiety / panic", "Syncope": "Vasovagal syncope", "Stroke": "Stroke / TIA",
             "GORD": "Reflux / GORD", "UTI": "Cystitis / UTI", "Biliary": "Biliary colic / cholecystitis",
             "ACE-inhibitor": "ACE-inhibitor cough", "Injury": "Injury / fracture", "Acute LVF": "Heart failure",
             "Heart failure (alcoholic cardiomyopathy)": "Heart failure", "Viral": "Viral fever",
             "Chikungunya": "Viral arthritis (e.g. chikungunya)", "Asthma attack": "Asthma", "COPD exacerbation": "COPD"}
_n = lambda L: list(dict.fromkeys(DDX_ALIAS.get(d, d) for d in L))
for _q in QUESTIONS:
    _q["differentials"] = _n(_q["differentials"])
    for _o in (_q["options"] or []):
        if "ddx" in _o:
            _o["ddx"] = _n(_o["ddx"])

# Clinical order inside each complaint (ord) — re-sequenced after adding system modules
REORDER = {"chest_pain": ["cp_site", "cp_character", "cp_onset_sudden", "cp_episode", "cp_radiation", "cp_triggers", "cp_relief"]}
for _c, _ids in REORDER.items():
    for _i, _id in enumerate(_ids, 1):
        next(q for q in QUESTIONS if q["id"] == _id)["ord"] = _i

# ------------------------------------------------------------------ SQL output
def lit(v):
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, (dict, list)):
        return "'" + json.dumps(v, ensure_ascii=False).replace("'", "''") + "'::jsonb"
    return "'" + str(v).replace("'", "''") + "'"


def arr(v):
    return "array[" + ",".join("'" + x.replace("'", "''") + "'" for x in v) + "]::text[]" if v else "'{}'::text[]"


def build():
    out = ["-- AUTO-GENERATED by supabase/hx_bank.py — do not edit by hand.",
           "-- Nidan question bank batch 1 (Hutchison's Clinical Methods 24e + standard history-taking).", ""]
    cols = "id, system, name_en, name_hi, name_mr, icon, ord, source"
    for c in COMPLAINTS:
        out.append(f"insert into public.hx_complaints({cols}) values ({', '.join(lit(c[k]) for k in cols.split(', '))})"
                   f" on conflict (id) do update set system=excluded.system, name_en=excluded.name_en, name_hi=excluded.name_hi,"
                   f" name_mr=excluded.name_mr, icon=excluded.icon, ord=excluded.ord, source=excluded.source;")
    qcols = ["id", "complaint_id", "section", "ord", "qtype", "options", "text_en", "text_hi", "text_mr", "clinical_term",
             "dedupe_key", "show_if", "applies_to", "red_flag", "red_flag_note", "positive_means", "negative_means",
             "differentials", "source", "active"]
    ids = set()
    for q in QUESTIONS:
        assert q["id"] not in ids, q["id"]
        ids.add(q["id"])
        if q["qtype"] in ("choice", "multi"):
            assert q["options"], q["id"]
        vals = [arr(q[k]) if k == "differentials" else lit(q[k]) for k in qcols]
        upd = ", ".join(f"{k}=excluded.{k}" for k in qcols[1:])
        out.append(f"insert into public.hx_questions({', '.join(qcols)}) values ({', '.join(vals)})"
                   f" on conflict (id) do update set {upd}, reviewed_on=current_date;")
    for q in QUESTIONS:  # show_if must point to an existing question
        if q["show_if"]:
            assert q["show_if"]["q"] in ids, q["id"]
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    import pathlib
    p = pathlib.Path(__file__).with_name("phase6_questions.sql")
    p.write_text(build(), encoding="utf-8")
    print(f"{len(COMPLAINTS)} complaints, {len(QUESTIONS)} questions, "
          f"{sum(q['red_flag'] for q in QUESTIONS)} red flags -> {p}")


def build_json():
    return json.dumps({"complaints": COMPLAINTS, "questions": QUESTIONS}, ensure_ascii=False, separators=(",", ":"))


if __name__ == "__main__":
    pathlib.Path(__file__).with_name("hx_bank.json").write_text(build_json(), encoding="utf-8")
    print("json written")
