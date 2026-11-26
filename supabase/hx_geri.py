# ====================================================================== SYSTEM 15: GERIATRIC (older people, 60+)
# Hutchison 24e, Ch 7 (Older people), p85-98: Box 7.1 (geriatric giants), 7.3 (observations), 7.4 (social networks),
# Table 7.2 (Barthel ADL), Box 7.5 (treatment history), 7.7 (causes of falls), 7.10 (incontinence), 7.11 (AMT),
# confusion / delirium p95-96, pressure ulcers p94-95. Executed inside hx_bank.py.
# Older people often present late and atypically (infection as confusion / falls / 'off legs'); always get a carer's account.

OP = f"{H}, Ch 7"
OLD = {"min_age": 60}

C("ger_falls", "Elderly", "Elderly: falls / unsteady walking", "बुज़ुर्ग: गिरना / चलने में लड़खड़ाना", "वृद्ध: पडणे / चालताना तोल जाणे", "🦯", 151, f"{OP}, p92-94 (Box 7.7, 7.9)")
C("ger_confusion", "Elderly", "Elderly: suddenly confused / behaving differently", "बुज़ुर्ग: अचानक उलझन / अलग बर्ताव", "वृद्ध: अचानक गोंधळ / वेगळे वागणे", "🌀", 152, f"{OP}, p95-96")
C("ger_memory", "Elderly", "Elderly: forgetfulness (slowly over months)", "बुज़ुर्ग: भूलना (महीनों से धीरे-धीरे)", "वृद्ध: विसरणे (महिन्यांपासून हळूहळू)", "🧠", 153, f"{OP}, p95 (Box 7.11)")
C("ger_decline", "Elderly", "Elderly: weak / off legs / not eating / not coping", "बुज़ुर्ग: कमज़ोर / चल नहीं पाते / खाना नहीं / सँभल नहीं रहे", "वृद्ध: अशक्त / चालता येत नाही / खात नाहीत / जमत नाही", "🛏️", 154, f"{OP}, p85-87, p93")
C("ger_meds", "Elderly", "Elderly: medicine review (many medicines)", "बुज़ुर्ग: दवाइयों की जाँच (बहुत दवाइयाँ)", "वृद्ध: औषधांची तपासणी (खूप औषधे)", "💊", 155, f"{OP}, p88-89 (Box 7.5)")
C("ger_bedsore", "Elderly", "Bedsore / bed-bound care", "बेडसोर / बिस्तर पर पड़े मरीज़", "बेडसोर / अंथरुणाला खिळलेला रुग्ण", "🩹", 156, f"{OP}, p94-95")

# ---------------------------------------------------------------- shared geriatric assessment, asked once per session
def geri_background(p, comp, base):
    Q(f"{p}_senses", comp, "geriatric", base, "multi", "Seeing / hearing / speaking (Box 7.3)", "देखना / सुनना / बोलना", "पाहणे / ऐकणे / बोलणे",
      term="Sensory & communication check", key="geri_senses", applies=OLD, opts=[
          O("poor_vision", "Poor vision / glasses broken or not worn", "कम दिखता / चश्मा टूटा या नहीं पहनते", "कमी दिसते / चष्मा तुटला किंवा घालत नाहीत", ["Cataract", "Visual impairment"]),
          O("hard_hearing", "Hard of hearing / hearing aid not used", "ऊँचा सुनते / मशीन नहीं लगाते", "कमी ऐकू येते / यंत्र वापरत नाहीत", ["Presbycusis", "Wax"]),
          O("teeth", "Teeth / denture problem, can't chew", "दाँत / बत्तीसी की तकलीफ़, चबा नहीं पाते", "दात / कवळीचा त्रास, चावता येत नाही", ["Undernutrition"]),
          O("speech", "Speech unclear / words wrong", "बोली साफ़ नहीं / ग़लत शब्द", "बोलणे अस्पष्ट / चुकीचे शब्द", ["Stroke (dysphasia / dysarthria)"])],
      src=f"{OP}, p87 (Box 7.3), p92-94")
    Q(f"{p}_adl", comp, "geriatric", base + 1, "multi", "Needs help with (now)", "अभी किस काम में मदद चाहिए", "आता कोणत्या कामात मदत लागते",
      term="Activities of daily living (Barthel items)", key="geri_adl", applies=OLD, opts=[
          O("none", "None — fully independent", "किसी में नहीं — सब ख़ुद", "कशातच नाही — सर्व स्वतः"),
          O("walking", "Walking / getting up from bed or chair", "चलना / बिस्तर या कुर्सी से उठना", "चालणे / अंथरुण किंवा खुर्चीतून उठणे", ["Immobility"]),
          O("toilet", "Toilet / bathing", "शौच / नहाना", "शौच / आंघोळ", ["Functional dependence"]),
          O("dressing_feeding", "Dressing / eating", "कपड़े पहनना / खाना खाना", "कपडे घालणे / जेवणे", ["Functional dependence"]),
          O("stairs", "Stairs / going outside", "सीढ़ी / बाहर जाना", "जिना / बाहेर जाणे", ["Immobility"]),
          O("bladder_bowel", "Control of urine / stool", "पेशाब / मल पर काबू", "लघवी / शौचावर ताबा", ["Incontinence"]),
          O("worse_recently", "Was independent before, worse in last days / weeks", "पहले सब ख़ुद करते थे, अभी कुछ दिनों / हफ़्तों में बिगड़ा", "आधी सर्व स्वतः करत, आता काही दिवस / आठवड्यांत बिघडले", ["Acute illness (atypical presentation)"])],
      src=f"{OP}, p88 (Table 7.2 Barthel ADL)")
    Q(f"{p}_social", comp, "geriatric", base + 2, "multi", "Home & support (Box 7.4)", "घर और सहारा", "घर व आधार", term="Social network", key="geri_social", applies=OLD, opts=[
        O("alone", "Lives alone", "अकेले रहते हैं", "एकटे राहतात", ["Social isolation"]),
        O("family", "Lives with family who help", "परिवार साथ, मदद करते हैं", "कुटुंबासोबत, मदत करतात"),
        O("carer_strain", "Carer is tired / struggling", "देखभाल करने वाला थका / परेशान", "सांभाळणारा थकलेला / त्रस्त", ["Carer strain"]),
        O("stairs_toilet", "Stairs at home / toilet far or outside", "घर में सीढ़ी / शौचालय दूर या बाहर", "घरात जिना / शौचालय दूर किंवा बाहेर", ["Falls risk (environmental)"]),
        O("money", "Money / pension worry", "पैसे / पेंशन की चिंता", "पैसे / पेन्शनची चिंता", ["Financial hardship"]),
        O("neglect", "Signs of neglect / ill-treatment (sister's observation)", "लापरवाही / बुरे बर्ताव के निशान (सिस्टर का अवलोकन)", "दुर्लक्ष / गैरवर्तनाची चिन्हे (सिस्टरचे निरीक्षण)", ["Elder abuse / neglect"])],
      src=f"{OP}, p88 (Box 7.4); p92 (Box 7.7 elder abuse)")
    Q(f"{p}_drugs", comp, "geriatric", base + 3, "choice", "How many different medicines daily (incl. desi / self-bought)?", "रोज़ कितनी अलग दवाइयाँ (देसी / ख़ुद ख़रीदी मिलाकर)?",
      "रोज किती वेगवेगळी औषधे (देशी / स्वतः विकत घेतलेली धरून)?", term="Polypharmacy", key="geri_drugs", applies=OLD, opts=[
          O("0_4", "0–4", "0–4", "0–4"),
          O("5_9", "5–9", "5–9", "5–9", ["Polypharmacy / adverse drug effect"]),
          O("10plus", "10 or more", "10 या ज़्यादा", "10 किंवा जास्त", ["Polypharmacy / adverse drug effect"]),
          O("dont_know", "Don't know (bring all medicines)", "पता नहीं (सारी दवाइयाँ लाएँ)", "माहीत नाही (सर्व औषधे आणा)", ["Polypharmacy / adverse drug effect"])],
      src=f"{OP}, p88-89 (Box 7.5)")

# ---------------------------------------------------------------- FALLS  (Box 7.7, 7.9)
FL = f"{OP}, p92-94 (Box 7.7)"
Q("gf_injury", "ger_falls", "redflag", 1, "yesno", "After the fall: can't stand / leg shortened or turned out, hit head, on blood thinner, or lay on floor for hours?",
  "गिरने के बाद: खड़े नहीं हो पाते / पैर छोटा या बाहर मुड़ा, सिर पर चोट, ख़ून पतला करने की दवा, या घंटों ज़मीन पर पड़े रहे?",
  "पडल्यानंतर: उभे राहता येत नाही / पाय लहान किंवा बाहेर वळला, डोक्याला मार, रक्त पातळ करण्याचे औषध, किंवा तासन्तास जमिनीवर पडून?",
  term="Serious injury after fall", rf="Fall with possible hip fracture / head injury (esp. on anticoagulant) / long lie — urgent X-ray / CT, check CK & kidneys",
  ddx=["Hip (neck of femur) fracture", "Subdural haematoma", "Rhabdomyolysis (long lie)"], applies=OLD, src=f"{FL}; p93 (impacted femoral fractures easily missed)")
Q("gf_how", "ger_falls", "hopi", 2, "multi", "How did it happen?", "कैसे गिरे?", "कसे पडले?", term="Circumstances of fall", applies=OLD, opts=[
    O("trip", "Tripped / slipped (wet floor, dark, loose chappal)", "ठोकर / फिसले (गीला फ़र्श, अँधेरा, ढीली चप्पल)", "ठेच / घसरले (ओली फरशी, अंधार, सैल चप्पल)", ["Accidental fall (environmental)"]),
    O("on_standing", "On standing up quickly / after meals / passing urine", "जल्दी उठते ही / खाने के बाद / पेशाब करते", "पटकन उठताच / जेवणानंतर / लघवी करताना", ["Postural hypotension", "Situational syncope"]),
    O("blackout", "Blacked out / no warning", "आँखों के आगे अँधेरा / बिना चेतावनी", "डोळ्यांसमोर अंधारी / इशाऱ्याशिवाय", ["Cardiac arrhythmia / heart block", "Seizure", "Carotid sinus syndrome"]),
    O("head_turn", "On turning head / looking up", "सिर घुमाने / ऊपर देखने पर", "डोके वळवताना / वर पाहताना", ["Carotid sinus syndrome", "Cervical spondylosis", "Vertebrobasilar insufficiency"]),
    O("legs_gave", "Legs suddenly gave way, no blackout", "पैर अचानक जवाब दे गए, होश में", "पाय अचानक लटपटले, शुद्धीत", ["Drop attack", "Muscle weakness"]),
    O("spinning", "Room spinning / unsteady", "चक्कर घूमना / लड़खड़ाना", "गरगरणे / तोल जाणे", ["Vestibular disorder", "Cerebellar disease"])],
  src=FL)
Q("gf_sinister", "ger_falls", "redflag", 3, "yesno", "With the fall: chest pain, palpitations, fit, new weakness of face / arm / leg, or loss of consciousness?",
  "गिरने के साथ: सीने में दर्द, धड़कन, दौरा, चेहरे / हाथ / पैर में नई कमज़ोरी, या बेहोशी?",
  "पडण्यासोबत: छातीत दुखणे, धडधड, झटके, चेहरा / हात / पायात नवीन अशक्तपणा, किंवा बेशुद्धी?",
  term="Sinister features of fall", rf="Fall with syncope / chest pain / focal deficit / seizure — ECG, neuro check, urgent doctor",
  ddx=["Cardiac arrhythmia / heart block", "Stroke / TIA", "Seizure", "Myocardial infarction"], applies=OLD, src=f"{OP}, p94")
Q("gf_risk", "ger_falls", "risk", 4, "multi", "Risk factors (Box 7.7)", "जोखिम", "जोखीम", term="Falls risk factors", key="falls", applies=OLD, opts=[
    O("previous", "Fell before (how many times this year?)", "पहले भी गिरे (इस साल कितनी बार?)", "आधीही पडले (या वर्षी किती वेळा?)", ["Recurrent falls"]),
    O("bp_sleep_drugs", "BP / sleeping / mood / Parkinson's medicines", "बीपी / नींद / मन / पार्किंसन की दवा", "बीपी / झोप / मन / पार्किन्सनचे औषध", ["Medication-related fall", "Postural hypotension"]),
    O("sugar_drugs", "Diabetes tablets / insulin (low sugar?)", "शुगर की गोली / इंसुलिन (शुगर कम?)", "मधुमेहाची गोळी / इन्सुलिन (साखर कमी?)", ["Hypoglycaemia"]),
    O("alcohol", "Alcohol", "शराब", "दारू", ["Alcohol-related fall"]),
    O("numb_feet", "Numb feet / painful feet / long nails", "पैर सुन्न / पैरों में दर्द / लंबे नाख़ून", "पाय बधिर / पाय दुखतात / लांब नखे", ["Peripheral neuropathy", "Foot problem"]),
    O("joint_weak", "Knee arthritis / weak legs", "घुटने का दर्द / पैर कमज़ोर", "गुडघेदुखी / पाय अशक्त", ["Osteoarthritis", "Muscle weakness"]),
    O("slow_shuffle", "Slow, small shuffling steps / tremor", "धीमे, छोटे घिसटते क़दम / कंपन", "हळू, लहान घसरती पावले / कंप", ["Parkinson's disease"]),
    O("fear", "Afraid of falling, stopped going out", "गिरने का डर, बाहर जाना बंद", "पडण्याची भीती, बाहेर जाणे बंद", ["Fear of falling"])],
  src=FL)
Q("gf_illness", "ger_falls", "associated", 5, "multi", "Any new illness in last few days? (falls can be first sign)", "पिछले कुछ दिनों में कोई नई बीमारी? (गिरना पहला लक्षण हो सकता है)",
  "गेल्या काही दिवसांत नवीन आजार? (पडणे पहिले लक्षण असू शकते)", term="Premonitory acute illness", applies=OLD, opts=[
      O("fever_cough", "Fever / cough", "बुखार / खाँसी", "ताप / खोकला", ["Chest infection"]),
      O("urine", "Burning / frequent urine / new incontinence", "पेशाब में जलन / बार-बार / नया रिसाव", "लघवीची जळजळ / वारंवार / नवीन गळती", ["UTI"]),
      O("eating_less", "Eating / drinking less", "खाना / पानी कम", "खाणे / पिणे कमी", ["Dehydration"]),
      O("loose_vomit", "Loose motions / vomiting", "दस्त / उल्टी", "जुलाब / उलटी", ["Dehydration"])],
  src=f"{OP}, p92 (Box 7.7 premonitory)")
geri_background("gf", "ger_falls", 10)

# ---------------------------------------------------------------- SUDDEN CONFUSION (delirium)
DL = f"{OP}, p95-96"
Q("gc_onset", "ger_confusion", "hopi", 1, "choice", "How did it start? (ask family)", "कैसे शुरू हुआ? (परिवार से पूछें)", "कसे सुरू झाले? (कुटुंबाला विचारा)",
  term="Onset of confusion", applies=OLD, opts=[
      O("hours_days", "Over hours / days, comes and goes (worse at night)", "घंटों / दिनों में, आता-जाता (रात में ज़्यादा)", "तासांत / दिवसांत, येते-जाते (रात्री जास्त)", ["Delirium"]),
      O("months", "Slowly over months / years", "महीनों / सालों में धीरे-धीरे", "महिन्यांत / वर्षांत हळूहळू", ["Dementia"]),
      O("sudden_minutes", "Suddenly within minutes, with weakness / speech change", "मिनटों में अचानक, कमज़ोरी / बोली बदलने के साथ", "मिनिटांत अचानक, अशक्तपणा / बोलणे बदलल्यासोबत", ["Stroke"]),
      O("dementia_worse", "Known memory problem, suddenly much worse", "पहले से भूलने की बीमारी, अचानक बहुत बढ़ी", "आधीपासून विसरण्याचा आजार, अचानक खूप वाढला", ["Delirium on dementia"])],
  src=DL)
Q("gc_features", "ger_confusion", "associated", 2, "multi", "What is seen?", "क्या दिख रहा है?", "काय दिसते?", term="Features", applies=OLD, opts=[
    O("drowsy", "Drowsy / very quiet (not just agitated)", "सुस्त / बहुत चुप (सिर्फ़ बेचैन नहीं)", "सुस्त / खूप शांत (फक्त अस्वस्थ नाही)", ["Hypoactive delirium"]),
    O("agitated", "Restless, pulling lines, shouting", "बेचैन, नली खींचना, चिल्लाना", "अस्वस्थ, नळ्या ओढणे, ओरडणे", ["Hyperactive delirium"]),
    O("seeing_things", "Seeing / hearing things", "चीज़ें दिखना / सुनाई देना", "गोष्टी दिसणे / ऐकू येणे", ["Delirium", "Lewy body dementia"]),
    O("not_knowing", "Doesn't know place / time / family", "जगह / समय / परिवार नहीं पहचानते", "जागा / वेळ / कुटुंब ओळखत नाहीत", ["Delirium", "Dementia"]),
    O("sleep_reversed", "Awake at night, sleepy by day", "रात को जागना, दिन में सोना", "रात्री जागणे, दिवसा झोपणे", ["Delirium"])],
  src=DL)
Q("gc_causes", "ger_confusion", "risk", 3, "multi", "Possible triggers (look for ALL)", "संभावित कारण (सब देखें)", "संभाव्य कारणे (सर्व पाहा)", term="Precipitants of delirium", applies=OLD, opts=[
    O("infection", "Fever / cough / burning urine", "बुखार / खाँसी / पेशाब में जलन", "ताप / खोकला / लघवीची जळजळ", ["UTI", "Pneumonia", "Sepsis"]),
    O("new_drug", "New / changed medicine (sleeping, pain, BP, sugar)", "नई / बदली दवा (नींद, दर्द, बीपी, शुगर)", "नवीन / बदललेले औषध (झोप, वेदना, बीपी, साखर)", ["Drug-induced delirium"]),
    O("constipation_retention", "No stool for days / not passing urine", "कई दिन मल नहीं / पेशाब नहीं", "अनेक दिवस शौच नाही / लघवी नाही", ["Constipation / faecal impaction", "Urinary retention"]),
    O("dehydration", "Drinking less / vomiting / loose motions", "पानी कम / उल्टी / दस्त", "पाणी कमी / उलटी / जुलाब", ["Dehydration", "Hyponatraemia"]),
    O("sugar", "Diabetic — sugar very low / high?", "शुगर — बहुत कम / ज़्यादा?", "मधुमेह — साखर खूप कमी / जास्त?", ["Hypoglycaemia", "Hyperglycaemic state"]),
    O("alcohol_stop", "Stopped alcohol suddenly", "शराब अचानक बंद", "दारू अचानक बंद", ["Alcohol withdrawal"]),
    O("fall_head", "Recent fall / head injury", "हाल में गिरे / सिर पर चोट", "अलीकडे पडले / डोक्याला मार", ["Subdural haematoma"]),
    O("pain", "Pain / new surgery / fracture", "दर्द / हाल में ऑपरेशन / हड्डी टूटी", "वेदना / अलीकडे ऑपरेशन / हाड मोडले", ["Delirium (pain / post-operative)"])],
  src=f"{DL} (search for treatable causes: drugs, endocrine, infection)")
Q("gc_flag", "ger_confusion", "redflag", 4, "yesno", "New confusion with fever, very drowsy, low sugar, fall / head injury, or one-sided weakness?",
  "नई उलझन के साथ बुखार, बहुत सुस्ती, शुगर कम, गिरना / सिर की चोट, या एक तरफ कमज़ोरी?",
  "नवीन गोंधळासोबत ताप, खूप सुस्ती, साखर कमी, पडणे / डोक्याला मार, किंवा एका बाजूला अशक्तपणा?",
  term="Acute confusion (delirium) — medical emergency", rf="ACUTE CONFUSION IN ELDERLY — treat as delirium: check sugar, vitals, SpO2, urine; urgent doctor",
  ddx=["Delirium", "Sepsis", "Hypoglycaemia", "Stroke", "Subdural haematoma"], applies=OLD, src=DL)
geri_background("gc", "ger_confusion", 10)

# ---------------------------------------------------------------- MEMORY (dementia screen)
MM = f"{OP}, p95 (Box 7.11 AMT); p95-96"
Q("gm_what", "ger_memory", "hopi", 1, "multi", "What is noticed (family's account)", "क्या दिखता है (परिवार के अनुसार)", "काय दिसते (कुटुंबानुसार)", term="Cognitive symptoms", applies=OLD, opts=[
    O("recent", "Forgets recent things, repeats questions", "हाल की बातें भूलते, एक ही सवाल बार-बार", "अलीकडच्या गोष्टी विसरतात, तोच प्रश्न पुन्हा-पुन्हा", ["Alzheimer's dementia"]),
    O("lost", "Gets lost in familiar places", "जानी-पहचानी जगह में भटक जाते", "ओळखीच्या ठिकाणी हरवतात", ["Dementia"]),
    O("money_tasks", "Can't manage money / cooking / medicines", "पैसे / खाना बनाना / दवा नहीं सँभाल पाते", "पैसे / स्वयंपाक / औषधे सांभाळता येत नाहीत", ["Dementia"]),
    O("stepwise", "Got worse in steps (after small strokes)", "झटकों में बिगड़ा (छोटे लकवे के बाद)", "टप्प्याटप्प्याने बिघडले (लहान पक्षाघातानंतर)", ["Vascular dementia"]),
    O("personality", "Personality / behaviour change, socially odd", "स्वभाव / बर्ताव बदला, अजीब बर्ताव", "स्वभाव / वर्तन बदलले, विचित्र वागणे", ["Frontotemporal dementia"]),
    O("visions_falls", "Sees things + stiffness / falls, fluctuates", "चीज़ें दिखना + अकड़न / गिरना, ऊपर-नीचे", "गोष्टी दिसणे + ताठरता / पडणे, कमी-जास्त", ["Lewy body dementia"]),
    O("sad_slow", "Sad, slowed, says 'I don't know'", "उदास, धीमे, कहते 'पता नहीं'", "उदास, मंद, म्हणतात 'माहीत नाही'", ["Depression (pseudodementia)"])],
  src=MM)
Q("gm_reversible", "ger_memory", "associated", 2, "multi", "Treatable causes to check", "ठीक होने वाले कारण", "बरे होणारी कारणे", term="Reversible causes", applies=OLD, opts=[
    O("thyroid_b12", "Thyroid / B12 deficiency / pure-veg diet", "थायराइड / B12 कमी / शुद्ध शाकाहारी", "थायरॉईड / B12 कमी / शुद्ध शाकाहारी", ["Hypothyroidism", "Vitamin B12 deficiency"]),
    O("hearing_vision", "Poor hearing / vision", "कम सुनना / दिखना", "कमी ऐकू / दिसणे", ["Sensory impairment"]),
    O("drugs", "Sleeping / bladder / allergy tablets", "नींद / पेशाब / एलर्जी की गोली", "झोप / लघवी / ॲलर्जीची गोळी", ["Drug-induced cognitive impairment"]),
    O("gait_urine", "Walking like feet stuck + urine leaking", "पैर चिपके जैसे चलना + पेशाब रिसना", "पाय चिकटल्यासारखे चालणे + लघवी गळणे", ["Normal pressure hydrocephalus"]),
    O("alcohol", "Heavy alcohol", "ज़्यादा शराब", "जास्त दारू", ["Alcohol-related brain damage"])],
  src=f"{MM} (depression, drugs, endocrine are treatable)")
Q("gm_amt", "ger_memory", "hopi", 3, "text", "AMT score (0–10): age, time, address recall, year, place, recognise 2 people, DOB, year of Independence, PM's name, count 20→1",
  "AMT स्कोर (0–10): उम्र, समय, पता याद, साल, जगह, 2 लोग पहचानें, जन्मतिथि, आज़ादी का साल, प्रधानमंत्री, 20 से 1 उल्टी गिनती",
  "AMT गुण (0–10): वय, वेळ, पत्ता आठवणे, वर्ष, ठिकाण, 2 व्यक्ती ओळखणे, जन्मतारीख, स्वातंत्र्याचे वर्ष, पंतप्रधान, 20 ते 1 उलटी मोजणी",
  term="Abbreviated Mental Test (≤7 = significant impairment)", applies=OLD, src=f"{OP}, p95 (Box 7.11; WW-year item adapted to Indian Independence 1947)")
Q("gm_safety", "ger_memory", "redflag", 4, "yesno", "Wanders out of home, leaves gas / fire on, not eating, or being exploited (money / property)?",
  "क्या घर से भटक कर निकल जाते, गैस / आग चालू छोड़ते, खाना नहीं खाते, या (पैसे / संपत्ति के लिए) शोषण?",
  "घरातून भटकत निघून जातात, गॅस / आग चालू ठेवतात, जेवत नाहीत, किंवा (पैसा / मालमत्तेसाठी) शोषण?",
  term="Safety risk in cognitive impairment", rf="Cognitive impairment with safety risk (wandering / fire / self-neglect / exploitation) — needs safety plan & social support",
  ddx=["Dementia"], applies=OLD, src=f"{OP}, p88; p92 (elder abuse)")
geri_background("gm", "ger_memory", 10)

# ---------------------------------------------------------------- DECLINE / OFF LEGS / NOT COPING (atypical presentation)
DC = f"{OP}, p85-87 (atypical presentation, 'acopia'), p93 (immobility)"
Q("gd_onset", "ger_decline", "hopi", 1, "choice", "How quickly?", "कितनी जल्दी?", "किती लवकर?", term="Onset of decline", applies=OLD, opts=[
    O("days", "Over days (was managing last week)", "कुछ दिनों में (पिछले हफ़्ते ठीक थे)", "काही दिवसांत (मागच्या आठवड्यात ठीक होते)", ["Acute illness (atypical presentation)", "Sepsis", "UTI", "Pneumonia"]),
    O("sudden", "Suddenly / after a fall", "अचानक / गिरने के बाद", "अचानक / पडल्यानंतर", ["Stroke", "Hip (neck of femur) fracture"]),
    O("months", "Slowly over months", "महीनों में धीरे-धीरे", "महिन्यांत हळूहळू", ["Malignancy", "Depression", "Heart failure", "Frailty", "Parkinson's disease"])],
  src=DC)
Q("gd_features", "ger_decline", "associated", 2, "multi", "Look for", "देखें", "पाहा", term="Clues to underlying illness", applies=OLD, opts=[
    O("infection", "Low fever / cough / burning urine (may be absent)", "हल्का बुखार / खाँसी / पेशाब जलन (न भी हो)", "हलका ताप / खोकला / लघवी जळजळ (नसूही शकते)", ["UTI", "Pneumonia", "Sepsis"]),
    O("weight_loss", "Weight loss / no appetite", "वज़न घटना / भूख नहीं", "वजन घटणे / भूक नाही", ["Malignancy", "Depression", "Tuberculosis", "Undernutrition"]),
    O("breathless_swelling", "Breathless / swollen legs", "साँस फूलना / पैरों में सूजन", "धाप / पाय सुजणे", ["Heart failure"]),
    O("low_mood", "Low mood / lost interest / 'want to die'", "उदासी / रुचि नहीं / 'मरना चाहता हूँ'", "उदासी / रस नाही / 'मरायचे आहे'", ["Depression"]),
    O("one_side", "One side weak / face droop", "एक तरफ कमज़ोरी / चेहरा टेढ़ा", "एका बाजूला अशक्तपणा / चेहरा वाकडा", ["Stroke"]),
    O("hip_pain", "Hip / groin pain on moving leg", "पैर हिलाने पर कूल्हे / जाँघ में दर्द", "पाय हलवताना कंबर / जांघेत दुखणे", ["Hip (neck of femur) fracture"]),
    O("back_pain", "New back pain", "नया पीठ दर्द", "नवीन पाठदुखी", ["Vertebral fracture (osteoporosis)", "Malignancy"]),
    O("thirst_urine", "Drinking little / dark urine / very thirsty", "पानी कम / गाढ़ा पेशाब / बहुत प्यास", "पाणी कमी / गडद लघवी / खूप तहान", ["Dehydration", "Hyperglycaemic state", "Hypercalcaemia"])],
  src=f"{DC}; p87 (Table 7.1)")
Q("gd_flag", "ger_decline", "redflag", 3, "yesno", "Suddenly unable to stand / walk, not drinking for 24 h, very drowsy, or breathing fast?",
  "क्या अचानक खड़े / चल नहीं पाते, 24 घंटे से पानी नहीं, बहुत सुस्त, या तेज़ साँस?",
  "अचानक उभे / चालता येत नाही, 24 तास पाणी नाही, खूप सुस्त, किंवा जलद श्वास?",
  term="Acute functional collapse", rf="ACUTE 'OFF LEGS' IN ELDERLY — not 'just old age': check vitals, sugar, SpO2, urine; look for sepsis / stroke / fracture",
  ddx=["Sepsis", "Stroke", "Hip (neck of femur) fracture", "Dehydration"], applies=OLD, src=f"{OP}, p86 (rapid deterioration with acute illness)")
Q("gd_weight", "ger_decline", "hopi", 4, "choice", "Weight change in last 6 months", "पिछले 6 महीने में वज़न", "गेल्या 6 महिन्यांत वजन", term="Weight trend (weigh every visit)", applies=OLD, opts=[
    O("stable", "Same", "उतना ही", "तेवढेच"),
    O("lost_some", "Clothes loose / lost a little", "कपड़े ढीले / थोड़ा घटा", "कपडे सैल / थोडे घटले", ["Undernutrition"]),
    O("lost_much", "Lost a lot (>5 kg)", "बहुत घटा (>5 किलो)", "खूप घटले (>5 किलो)", ["Malignancy", "Tuberculosis", "Depression"]),
    O("unknown", "Don't know", "पता नहीं", "माहीत नाही")],
  src=f"{OP}, p91 (weigh at every visit)")
geri_background("gd", "ger_decline", 10)

# ---------------------------------------------------------------- MEDICINE REVIEW  (Box 7.5)
MD = f"{OP}, p88-89 (Box 7.5)"
Q("gx_sources", "ger_meds", "hopi", 1, "multi", "Treatment history (Box 7.5)", "इलाज का इतिहास", "उपचाराचा इतिहास", term="Treatment history checklist", applies=OLD, opts=[
    O("many_doctors", "Medicines from more than one doctor", "एक से ज़्यादा डॉक्टरों की दवा", "एकापेक्षा जास्त डॉक्टरांची औषधे", ["Polypharmacy / adverse drug effect"]),
    O("self", "Self-bought from medical shop", "ख़ुद मेडिकल से ख़रीदी", "स्वतः मेडिकलमधून घेतलेली", ["Self-medication"]),
    O("desi", "Ayurvedic / homeopathy / desi", "आयुर्वेदिक / होम्योपैथी / देसी", "आयुर्वेदिक / होमिओपॅथी / देशी", ["Herbal / alternative medicine interaction"]),
    O("old_stock", "Old medicines kept at home and used", "घर में पुरानी दवा रखते और लेते", "घरात जुनी औषधे ठेवतात व घेतात", ["Medication error"]),
    O("past_reaction", "Bad reaction to a medicine before", "पहले किसी दवा से तकलीफ़", "आधी एखाद्या औषधाचा त्रास", ["Adverse drug reaction"])],
  src=MD)
Q("gx_adherence", "ger_meds", "risk", 2, "multi", "Taking them correctly?", "ठीक से लेते हैं?", "नीट घेतात का?", term="Adherence", key="adherence", applies=OLD, opts=[
    O("forget", "Forgets doses / takes double", "ख़ुराक भूलते / दो बार लेते", "डोस विसरतात / दोनदा घेतात", ["Medication error"]),
    O("cannot_read", "Can't read labels / open strips", "लेबल पढ़ नहीं पाते / पत्ता खोल नहीं पाते", "लेबल वाचता येत नाही / पाकीट उघडता येत नाही", ["Medication error"]),
    O("stopped_cost", "Stopped some due to cost / side effects", "ख़र्च / साइड इफ़ेक्ट से कुछ बंद", "खर्च / दुष्परिणामामुळे काही बंद", ["Non-adherence"]),
    O("someone_gives", "Family member gives (pill box)", "परिवार वाला देता (गोली डिब्बा)", "कुटुंबातील व्यक्ती देते (गोळी डबा)")],
  src=MD)
Q("gx_side", "ger_meds", "associated", 3, "multi", "Possible side effects now", "अभी संभावित साइड इफ़ेक्ट", "आता संभाव्य दुष्परिणाम", term="Adverse drug effects", applies=OLD, opts=[
    O("dizzy_stand", "Dizzy on standing", "उठने पर चक्कर", "उठल्यावर चक्कर", ["Postural hypotension (drug)"]),
    O("drowsy_confused", "Drowsy / confused", "सुस्ती / उलझन", "सुस्ती / गोंधळ", ["Drug-induced delirium"]),
    O("black_stool", "Black stool / stomach pain (painkillers, aspirin, blood thinner)", "काला मल / पेट दर्द (दर्द की दवा, एस्पिरिन, ख़ून पतला)", "काळी शौच / पोटदुखी (वेदनाशामक, ॲस्पिरिन, रक्त पातळ)", ["Upper GI bleed (NSAID / antiplatelet)"]),
    O("bleeding_bruise", "Bleeding / bruising", "ख़ून आना / नील पड़ना", "रक्तस्राव / काळे-निळे", ["Anticoagulant excess"]),
    O("low_sugar", "Sweating, shaky, low sugar episodes", "पसीना, काँपना, शुगर कम होना", "घाम, थरथर, साखर कमी होणे", ["Hypoglycaemia (sulfonylurea / insulin)"]),
    O("constipation_urine", "Constipation / can't pass urine", "कब्ज़ / पेशाब नहीं उतरता", "बद्धकोष्ठता / लघवी होत नाही", ["Anticholinergic side effect"])],
  src=f"{MD}; p92 (Box 7.7 medication)")
Q("gx_flag", "ger_meds", "redflag", 4, "yesno", "On blood thinner / insulin / sugar tablets with bleeding, black stool, or low-sugar episodes?",
  "ख़ून पतला करने की दवा / इंसुलिन / शुगर की गोली के साथ ख़ून आना, काला मल, या शुगर कम होना?",
  "रक्त पातळ करण्याचे औषध / इन्सुलिन / साखरेच्या गोळीसोबत रक्तस्राव, काळी शौच, किंवा साखर कमी होणे?",
  term="High-risk medication harm", rf="High-risk drug harm (anticoagulant bleed / hypoglycaemia) — urgent doctor review",
  ddx=["Anticoagulant excess", "Hypoglycaemia (sulfonylurea / insulin)", "Upper GI bleed (NSAID / antiplatelet)"], applies=OLD, src=MD)
geri_background("gx", "ger_meds", 10)

# ---------------------------------------------------------------- BEDSORE / BED-BOUND  (p94-95)
PU = f"{OP}, p94-95 (pressure ulcers)"
Q("gp_where", "ger_bedsore", "hopi", 1, "multi", "Where is the sore / redness?", "घाव / लाली कहाँ है?", "जखम / लाली कुठे आहे?", term="Site", applies={"min_age": 18}, opts=[
    O("sacrum", "Lower back / tailbone", "कमर के नीचे / पूँछ की हड्डी", "कंबरेखाली / माकडहाड", ["Pressure ulcer"]),
    O("heel", "Heels", "एड़ी", "टाच", ["Pressure ulcer"]),
    O("hip", "Side of hip", "कूल्हे की तरफ", "कंबरेच्या बाजूला", ["Pressure ulcer"]),
    O("other", "Elbow / shoulder / back of head", "कोहनी / कंधा / सिर का पीछे", "कोपर / खांदा / डोक्याच्या मागे", ["Pressure ulcer"])],
  src=PU)
Q("gp_stage", "ger_bedsore", "hopi", 2, "choice", "How deep?", "कितना गहरा?", "किती खोल?", term="Depth", applies={"min_age": 18}, opts=[
    O("red", "Red skin only, not fading on pressing", "सिर्फ़ लाल त्वचा, दबाने पर नहीं मिटती", "फक्त लाल त्वचा, दाबल्यावर जात नाही", ["Pressure ulcer (superficial)"]),
    O("blister", "Blister / shallow open wound", "छाला / उथला घाव", "फोड / उथळ जखम", ["Pressure ulcer (superficial)"]),
    O("deep", "Deep hole / black dead skin / bone seen", "गहरा गड्ढा / काली मरी त्वचा / हड्डी दिखे", "खोल खड्डा / काळी मृत त्वचा / हाड दिसते", ["Pressure ulcer (deep)", "Osteomyelitis"])],
  src=PU)
Q("gp_flag", "ger_bedsore", "redflag", 3, "yesno", "Sore with foul smell / pus / spreading redness, or patient has fever / drowsy?",
  "घाव से बदबू / मवाद / फैलती लाली, या मरीज़ को बुखार / सुस्ती?", "जखमेतून दुर्गंधी / पू / पसरणारी लाली, किंवा रुग्णाला ताप / सुस्ती?",
  term="Infected pressure ulcer", rf="Infected pressure ulcer / possible sepsis — urgent doctor (debridement, antibiotics)", ddx=["Infected pressure ulcer", "Sepsis", "Osteomyelitis"],
  applies={"min_age": 18}, src=PU)
Q("gp_risk", "ger_bedsore", "risk", 4, "multi", "Why at risk?", "जोखिम क्यों?", "धोका का?", term="Pressure ulcer risk factors", applies={"min_age": 18}, opts=[
    O("not_turned", "Not turned every 2 hours", "हर 2 घंटे करवट नहीं", "दर 2 तासांनी कूस बदलत नाहीत", ["Pressure ulcer"]),
    O("wet", "Wet with urine / stool for long", "पेशाब / मल में देर तक गीले", "लघवी / शौचात बराच वेळ ओले", ["Pressure ulcer", "Incontinence"]),
    O("poor_food_water", "Eats / drinks little", "खाना / पानी कम", "खाणे / पिणे कमी", ["Undernutrition", "Dehydration"]),
    O("diabetes_numb", "Diabetes / no feeling (paralysis)", "शुगर / सुन्नपन (लकवा)", "मधुमेह / संवेदना नाही (पक्षाघात)", ["Pressure ulcer"]),
    O("no_mattress", "No air mattress / hard bed", "एयर मैट्रेस नहीं / सख़्त बिस्तर", "एअर मॅट्रेस नाही / कडक बिछाना", ["Pressure ulcer"])],
  src=PU)
geri_background("gp", "ger_bedsore", 10)
