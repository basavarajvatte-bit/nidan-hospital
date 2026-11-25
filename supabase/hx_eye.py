# ====================================================================== SYSTEM 11: EYE
# Hutchison 24e, Ch 20 (Eyes), p419-438; Table 20.1 (sudden visual disturbance), Table 20.2 (red eye), Box 20.4 (angle closure).
# Executed inside hx_bank.py.

EY = f"{H}, Ch 20"
EYH = f"{EY}, p419 (history)"

C("sudden_vision", "Eye", "Sudden loss / blurring of vision", "अचानक दिखना बंद / धुंधला", "अचानक दिसणे बंद / अंधुक", "⚫", 111, f"{EY}, p420 (Table 20.1)")
C("gradual_vision", "Eye", "Slowly reducing vision", "धीरे-धीरे नज़र कम होना", "हळूहळू दृष्टी कमी होणे", "👓", 112, EYH)
C("red_eye", "Eye", "Red / painful eye", "आँख लाल / दर्द", "डोळा लाल / दुखणे", "👁️", 113, f"{EY}, p421 (Table 20.2)")
C("eye_injury", "Eye", "Eye injury / something in eye / chemical", "आँख में चोट / कुछ गिरा / केमिकल", "डोळ्याला इजा / काही गेले / रसायन", "🎯", 114, EYH)
C("double_vision", "Eye", "Double vision / squint / droopy eyelid", "दोहरा दिखना / भेंगापन / पलक झुकना", "दोन-दोन दिसणे / तिरळेपणा / पापणी लोंबणे", "👀", 115, EYH)
C("floaters", "Eye", "Floaters / flashes / curtain over vision", "आँख के आगे धब्बे / चमक / पर्दा", "डोळ्यासमोर ठिपके / चमक / पडदा", "✨", 116, f"{EY}, p420 (Table 20.1)")

# ---------------------------------------------------------------- SUDDEN VISION LOSS  (Table 20.1)
SV = f"{EY}, p420 (Table 20.1)"
Q("sv_flag", "sudden_vision", "redflag", 1, "yesno", "Vision suddenly lost / badly reduced in the last few days?", "क्या पिछले कुछ दिनों में अचानक दिखना बंद / बहुत कम हुआ?",
  "मागील काही दिवसांत अचानक दिसणे बंद / खूप कमी झाले का?", term="Sudden visual loss", rf="Sudden visual loss — SAME-DAY eye assessment", ddx=["Retinal artery / vein occlusion", "Retinal detachment", "Ischaemic optic neuropathy"], src=SV)
Q("sv_pattern", "sudden_vision", "hopi", 2, "choice", "What happened to the vision?", "नज़र में क्या हुआ?", "दृष्टीत काय झाले?", term="Pattern of loss", opts=[
    O("curtain_minutes", "Curtain came down over one eye for minutes, then recovered", "एक आँख पर कुछ मिनट पर्दा, फिर ठीक", "एका डोळ्यावर काही मिनिटे पडदा, मग बरे", ["Amaurosis fugax (TIA of eye)"]),
    O("one_permanent", "One eye, sudden and still lost", "एक आँख, अचानक और अभी भी बंद", "एक डोळा, अचानक आणि अजून बंद", ["Retinal artery / vein occlusion", "Ischaemic optic neuropathy", "Vitreous haemorrhage"]),
    O("half_field_both", "Half of vision missing in both eyes (same side)", "दोनों आँखों में आधा दिखना ग़ायब (एक तरफ)", "दोन्ही डोळ्यांत अर्धे दिसणे गायब (एका बाजूला)", ["Stroke / TIA"]),
    O("zigzag_headache", "Zig-zag lights then headache, back to normal", "टेढ़ी चमकती लकीरें फिर सिर दर्द, फिर ठीक", "वाकड्या चमकणाऱ्या रेषा मग डोकेदुखी, मग बरे", ["Migraine"]),
    O("seconds_bending", "Brief seconds of blackout on bending / coughing (both eyes)", "झुकने / खाँसने पर कुछ सेकंड अँधेरा (दोनों आँखें)", "वाकताना / खोकताना काही सेकंद अंधार (दोन्ही डोळे)", ["Raised intracranial pressure", "Idiopathic intracranial hypertension"]),
    O("distorted_centre", "Centre of vision distorted / straight lines wavy", "बीच का दिखना टेढ़ा / सीधी लकीरें लहरदार", "मध्यभागी दिसणे वाकडे / सरळ रेषा लहरी", ["Wet age-related macular degeneration"]),
    O("painful_move", "Painful eye movements, colours faded (young)", "आँख घुमाने पर दर्द, रंग फीके (कम उम्र)", "डोळे फिरवताना दुखणे, रंग फिके (कमी वय)", ["Optic neuritis"])],
  src=SV)
Q("sv_gca", "sudden_vision", "redflag", 3, "yesno", "Age over 50 with headache, scalp tenderness, jaw pain on chewing or shoulder stiffness?",
  "क्या 50 से ज़्यादा उम्र, सिर दर्द, सिर छूने पर दर्द, चबाने पर जबड़ा दर्द या कंधे अकड़े?", "50 पेक्षा जास्त वय, डोकेदुखी, डोक्याला स्पर्शाने दुखणे, चावताना जबडा दुखणे किंवा खांदे ताठ?",
  term="Giant cell arteritis features", rf="Possible giant cell arteritis — EMERGENCY (risk to other eye; ESR & steroids)", ddx=["Giant cell arteritis"],
  applies={"min_age": 50}, src=SV)
Q("sv_stroke", "sudden_vision", "redflag", 4, "yesno", "With face / arm / leg weakness, numbness or speech problem?", "क्या साथ में चेहरा / हाथ / पैर कमज़ोर, सुन्न या बोली की तकलीफ़?",
  "सोबत चेहरा / हात / पाय कमजोर, बधिर किंवा बोलण्याचा त्रास?", term="Neurological deficit", rf="Visual loss with neuro deficit — stroke / TIA pathway", ddx=["Stroke / TIA"], src=SV)
Q("sv_risk", "sudden_vision", "risk", 5, "multi", "Vascular risk factors", "जोखिम", "जोखीम", term="Vascular risk factors", key="cv_risk", opts=[
    O("htn", "High BP", "हाई बीपी", "उच्च रक्तदाब", ["Retinal artery / vein occlusion"]),
    O("dm", "Diabetes", "शुगर", "मधुमेह", ["Vitreous haemorrhage", "Retinal artery / vein occlusion"]),
    O("smoke", "Smoking", "धूम्रपान", "धूम्रपान", ["Retinal artery / vein occlusion"]),
    O("af_heart", "Irregular heartbeat / heart disease", "धड़कन अनियमित / दिल की बीमारी", "ठोके अनियमित / हृदयरोग", ["Amaurosis fugax (TIA of eye)", "Retinal artery / vein occlusion"]),
    O("lipids", "High cholesterol", "कोलेस्ट्रॉल ज़्यादा", "कोलेस्टेरॉल जास्त", ["Retinal artery / vein occlusion"])],
  src=SV)

# ---------------------------------------------------------------- GRADUAL VISION LOSS
GV = EYH
Q("gv_type", "gradual_vision", "hopi", 1, "multi", "What is difficult?", "क्या मुश्किल है?", "काय कठीण आहे?", term="Nature of visual difficulty", opts=[
    O("near_after40", "Reading small print after age 40", "40 के बाद बारीक अक्षर पढ़ना", "40 नंतर बारीक अक्षरे वाचणे", ["Presbyopia (needs reading glasses)"]),
    O("distance_child", "Seeing far / blackboard (child / young)", "दूर का / बोर्ड देखना (बच्चा / जवान)", "दूरचे / फळा पाहणे (मूल / तरुण)", ["Refractive error (myopia)"]),
    O("glare_cloudy", "Cloudy / glare from headlights, better in dim light", "धुंधलापन / गाड़ी की लाइट से चकाचौंध", "धूसरपणा / गाडीच्या दिव्यांनी डोळे दिपणे", ["Cataract"]),
    O("bumping_sides", "Bumping into things on the sides", "किनारे की चीज़ों से टकराना", "बाजूच्या वस्तूंना धडकणे", ["Glaucoma (chronic)", "Retinitis pigmentosa"]),
    O("night_blind", "Poor vision at night / in dim light", "रात / कम रोशनी में कम दिखना", "रात्री / कमी उजेडात कमी दिसणे", ["Vitamin A deficiency", "Retinitis pigmentosa", "Cataract"]),
    O("central_blur_old", "Centre blurred / faces hard to see (elderly)", "बीच में धुंधला / चेहरे पहचानना मुश्किल (बुज़ुर्ग)", "मध्यभागी अंधुक / चेहरे ओळखणे कठीण (वृद्ध)", ["Age-related macular degeneration"]),
    O("fluctuating_sugar", "Vision changes with sugar levels", "शुगर के साथ नज़र बदलती", "साखरेसोबत दृष्टी बदलते", ["Diabetic retinopathy", "Diabetes"])],
  src=GV)
Q("gv_risk", "gradual_vision", "risk", 2, "multi", "Risk factors", "जोखिम", "जोखीम", term="Risk factors", opts=[
    O("dm", "Diabetes (last eye check?)", "शुगर (आँख की जाँच कब?)", "मधुमेह (डोळे तपासणी कधी?)", ["Diabetic retinopathy", "Cataract"]),
    O("steroid", "Steroid tablets / eye drops for long", "लंबे समय स्टेरॉयड गोली / आँख की बूँदें", "दीर्घकाळ स्टिरॉइड गोळी / डोळ्यांचे थेंब", ["Cataract", "Steroid-induced glaucoma"]),
    O("family_glaucoma", "Glaucoma in family", "परिवार में काला मोतिया (ग्लूकोमा)", "कुटुंबात काचबिंदू", ["Glaucoma (chronic)"]),
    O("htn", "High BP", "हाई बीपी", "उच्च रक्तदाब", ["Hypertensive retinopathy"]),
    O("child_squint", "Child with squint / lazy eye", "बच्चे में भेंगापन / आलसी आँख", "मुलात तिरळेपणा / आळशी डोळा", ["Amblyopia"]),
    O("poor_diet_child", "Child with poor diet / measles", "बच्चे का खाना कम / खसरा", "मुलाचा आहार कमी / गोवर", ["Vitamin A deficiency"]),
    O("ethambutol", "TB medicine ethambutol", "टीबी की दवा एथमब्यूटोल", "टीबी औषध इथॅम्ब्युटॉल", ["Drug toxic optic neuropathy"])],
  src=GV)
Q("gv_last_check", "gradual_vision", "hopi", 3, "choice", "Last eye test / glasses", "आख़िरी बार आँख की जाँच / चश्मा", "शेवटची डोळे तपासणी / चष्मा", term="Last eye examination", opts=[
    O("lt1y", "Within 1 year", "1 साल के अंदर", "1 वर्षाच्या आत"), O("gt1y", "More than 1 year", "1 साल से पहले", "1 वर्षापूर्वी"),
    O("never", "Never", "कभी नहीं", "कधीच नाही")],
  src=GV)
Q("gv_impact", "gradual_vision", "hopi", 4, "multi", "Daily life", "रोज़ की ज़िंदगी", "रोजचे जीवन", term="Functional impact", opts=[
    O("falls", "Falls / trips", "गिरना / ठोकर", "पडणे / ठेच", ["Falls risk"]),
    O("drives", "Still driving", "अभी भी गाड़ी चलाते", "अजूनही गाडी चालवतात"),
    O("cant_read_meds", "Can't read medicine labels", "दवा का नाम नहीं पढ़ पाते", "औषधाचे नाव वाचता येत नाही"),
    O("work", "Affects work / school", "काम / पढ़ाई पर असर", "काम / शिक्षणावर परिणाम")],
  src=GV)

# ---------------------------------------------------------------- RED EYE  (Table 20.2)
RE = f"{EY}, p421 (Table 20.2)"
Q("re_danger", "red_eye", "redflag", 1, "multi", "Danger signs with red eye", "लाल आँख के साथ ख़तरे के निशान", "लाल डोळ्यासोबत धोक्याची चिन्हे", term="Red eye red flags", opts=[
    O("vision_down", "Vision reduced", "नज़र कम", "दृष्टी कमी", ["Acute angle-closure glaucoma", "Keratitis / corneal ulcer", "Iritis (anterior uveitis)"]),
    O("severe_pain_vomit", "Severe pain, headache, vomiting, rainbow haloes", "तेज़ दर्द, सिर दर्द, उल्टी, रोशनी के चारों ओर इंद्रधनुष", "तीव्र दुखणे, डोकेदुखी, उलटी, दिव्याभोवती इंद्रधनुष्य", ["Acute angle-closure glaucoma"]),
    O("light_hurts", "Can't tolerate light", "रोशनी सहन नहीं", "प्रकाश सहन होत नाही", ["Iritis (anterior uveitis)", "Keratitis / corneal ulcer"]),
    O("contact_lens", "Contact lens wearer with pain", "कॉन्टैक्ट लेंस और दर्द", "कॉन्टॅक्ट लेन्स आणि दुखणे", ["Keratitis / corneal ulcer"]),
    O("white_spot_cornea", "White spot on the black part of eye", "आँख की काली पुतली पर सफ़ेद धब्बा", "डोळ्याच्या काळ्या भागावर पांढरा डाग", ["Keratitis / corneal ulcer"]),
    O("newborn", "Newborn with sticky red eyes", "नवजात की चिपचिपी लाल आँखें", "नवजाताचे चिकट लाल डोळे", ["Ophthalmia neonatorum"])],
  src=RE)
Q("re_flag", "red_eye", "redflag", 2, "yesno", "Red eye with reduced vision, severe pain, light sensitivity, or white spot on cornea?",
  "क्या लाल आँख के साथ नज़र कम, तेज़ दर्द, रोशनी चुभना, या पुतली पर सफ़ेद धब्बा?", "लाल डोळ्यासोबत दृष्टी कमी, तीव्र दुखणे, प्रकाश सहन न होणे, किंवा बुबुळावर पांढरा डाग?",
  term="Sight-threatening red eye", rf="Sight-threatening red eye — SAME-DAY ophthalmology (no steroid drops)", ddx=["Acute angle-closure glaucoma", "Keratitis / corneal ulcer", "Iritis (anterior uveitis)"], src=RE)
Q("re_features", "red_eye", "hopi", 3, "multi", "What is it like?", "कैसी लाली है?", "लाली कशी आहे?", term="Features", opts=[
    O("both_sticky", "Both eyes, sticky yellow discharge", "दोनों आँखें, चिपचिपा पीला कीचड़", "दोन्ही डोळे, चिकट पिवळी घाण", ["Bacterial conjunctivitis"]),
    O("watery_contact", "Watery, gritty, others at home also have it, after cold", "पानी, किरकिरी, घर में औरों को भी, सर्दी के बाद", "पाणी, खुपणे, घरी इतरांनाही, सर्दीनंतर", ["Viral conjunctivitis"]),
    O("itchy_season", "Very itchy, both eyes, allergy / season", "बहुत खुजली, दोनों आँखें, एलर्जी / मौसम", "खूप खाज, दोन्ही डोळे, ॲलर्जी / ऋतू", ["Allergic conjunctivitis"]),
    O("blood_patch", "Bright red patch, no pain (after cough / strain / BP)", "चमकीला लाल धब्बा, दर्द नहीं (खाँसी / ज़ोर / बीपी के बाद)", "चमकदार लाल चट्टा, दुखत नाही (खोकला / जोर / बीपीनंतर)", ["Subconjunctival haemorrhage"]),
    O("one_ache_light", "One eye, aching, light hurts, small pupil", "एक आँख, दर्द, रोशनी चुभती, पुतली छोटी", "एक डोळा, ठणका, प्रकाश सहन होत नाही, बाहुली लहान", ["Iritis (anterior uveitis)"]),
    O("sector_mild", "One patch of redness, mild discomfort", "एक हिस्से में लाली, हल्की तकलीफ़", "एका भागात लाली, सौम्य त्रास", ["Episcleritis"]),
    O("deep_boring_pain", "Deep boring pain, tender eye", "गहरा चुभता दर्द, आँख छूने पर दर्द", "खोल टोचणारे दुखणे, डोळा स्पर्शाला दुखरा", ["Scleritis"])],
  src=RE)
Q("re_systemic", "red_eye", "associated", 4, "multi", "Body clues", "शरीर के संकेत", "शरीराचे संकेत", term="Systemic associations", opts=[
    O("back_joint", "Back pain / joint pain", "कमर दर्द / जोड़ों का दर्द", "कंबरदुखी / सांधेदुखी", ["Iritis (anterior uveitis)", "Spondyloarthritis"]),
    O("ra_lupus", "Rheumatoid arthritis / lupus", "आर्थराइटिस / ल्यूपस", "संधिवात / ल्यूपस", ["Scleritis"]),
    O("cold_sore_rash", "Cold sores / rash on forehead and nose", "होंठ पर छाले / माथे और नाक पर दाने", "ओठांवर फोड / कपाळ व नाकावर पुरळ", ["Herpes keratitis / zoster ophthalmicus"]),
    O("hypermetrope_old", "Older, long-sighted, attacks in dim light", "बुज़ुर्ग, दूर-दृष्टि, कम रोशनी में दौरे", "वृद्ध, दूरदृष्टी, कमी उजेडात झटके", ["Acute angle-closure glaucoma"])],
  src=f"{RE}; {EY}, p425 (Box 20.4)")
Q("re_drops", "red_eye", "risk", 5, "yesno", "Using eye drops from chemist (esp. steroid drops) / home remedies (honey, breast milk, kajal)?",
  "क्या केमिस्ट की आँख की दवा (ख़ासकर स्टेरॉयड वाली) / घरेलू नुस्ख़े (शहद, दूध, काजल) डाले?", "केमिस्टचे डोळ्याचे थेंब (विशेषतः स्टिरॉइड) / घरगुती उपाय (मध, दूध, काजळ) घातले?",
  term="Self-medication of eye", ddx=["Keratitis / corneal ulcer", "Steroid-induced glaucoma"], src="General clinical practice (India)")

# ---------------------------------------------------------------- EYE INJURY / FOREIGN BODY / CHEMICAL
EI = EYH
Q("ei_type", "eye_injury", "hopi", 1, "choice", "What happened?", "क्या हुआ?", "काय झाले?", term="Mechanism", opts=[
    O("chemical", "Chemical / lime (chuna) / acid / cement splash", "केमिकल / चूना / तेज़ाब / सीमेंट छिटका", "रसायन / चुना / ॲसिड / सिमेंट उडाले", ["Chemical eye injury"]),
    O("high_speed", "Hammering / grinding / metal chip flew in", "हथौड़ा / ग्राइंडर / लोहे का टुकड़ा उड़कर लगा", "हातोडा / ग्राइंडर / लोखंडाचा तुकडा उडून लागला", ["Intraocular foreign body"]),
    O("dust_insect", "Dust / insect / grain husk", "धूल / कीड़ा / भूसा", "धूळ / किडा / भुसा", ["Corneal foreign body / abrasion"]),
    O("blunt", "Hit by ball / fist / stick", "गेंद / मुक्का / डंडा लगा", "चेंडू / ठोसा / काठी लागली", ["Blunt eye injury (hyphaema / orbital fracture)"]),
    O("sharp", "Cut / pierced by sharp object", "नुकीली चीज़ से कटा / चुभा", "टोकदार वस्तूने कापले / टोचले", ["Penetrating eye injury"]),
    O("vegetable", "Leaf / plant / crop injury (farmer)", "पत्ता / पौधा / फ़सल से चोट (किसान)", "पान / रोप / पिकाने इजा (शेतकरी)", ["Fungal keratitis (after vegetative trauma)"])],
  src=EI)
Q("ei_chemical_now", "eye_injury", "redflag", 2, "yesno", "Chemical / chuna in eye?", "क्या आँख में केमिकल / चूना गया?", "डोळ्यात रसायन / चुना गेला?",
  term="Chemical injury", rf="CHEMICAL EYE INJURY — wash with clean water for 20–30 min NOW, then urgent eye care", ddx=["Chemical eye injury"], src=EI)
Q("ei_serious", "eye_injury", "redflag", 3, "yesno", "Vision reduced, eye shape changed, blood inside eye, or metal / sharp object injury?",
  "क्या नज़र कम, आँख का आकार बदला, आँख के अंदर ख़ून, या लोहे / नुकीली चीज़ की चोट?", "दृष्टी कमी, डोळ्याचा आकार बदलला, डोळ्यात रक्त, किंवा लोखंड / टोकदार वस्तूची इजा?",
  term="Serious eye trauma", rf="Possible open globe / intraocular FB — do NOT press eye, shield & refer URGENTLY", ddx=["Penetrating eye injury", "Intraocular foreign body"], src=EI)
Q("ei_tetanus_rub", "eye_injury", "risk", 4, "multi", "After the injury", "चोट के बाद", "इजेनंतर", term="Post-injury actions", opts=[
    O("rubbed", "Rubbed the eye", "आँख मसली", "डोळा चोळला"),
    O("home_remedy", "Put home remedy / drops", "घरेलू नुस्ख़ा / बूँदें डालीं", "घरगुती उपाय / थेंब घातले", ["Keratitis / corneal ulcer"]),
    O("contact_lens", "Wearing contact lens", "कॉन्टैक्ट लेंस पहने", "कॉन्टॅक्ट लेन्स घातले", ["Keratitis / corneal ulcer"])],
  src=EI)

# ---------------------------------------------------------------- DOUBLE VISION / SQUINT / PTOSIS
DV = EYH
Q("dv_mono_bino", "double_vision", "hopi", 1, "choice", "Does double vision go away when one eye is closed?", "क्या एक आँख बंद करने पर दोहरा दिखना बंद होता है?",
  "एक डोळा बंद केल्यावर दोन-दोन दिसणे थांबते का?", term="Monocular vs binocular diplopia", opts=[
      O("goes", "Yes, goes away (binocular)", "हाँ, बंद होता है", "हो, थांबते", ["Cranial nerve palsy", "Myasthenia gravis", "Thyroid eye disease"]),
      O("stays", "No, stays in one eye (monocular)", "नहीं, एक आँख में बना रहता", "नाही, एका डोळ्यात राहते", ["Cataract / refractive (monocular diplopia)"]),
      O("no_double", "No double vision (only squint / droop)", "दोहरा नहीं (सिर्फ़ भेंगापन / पलक झुकी)", "दोन-दोन नाही (फक्त तिरळेपणा / पापणी लोंबणे)")],
  src=DV)
Q("dv_flag", "double_vision", "redflag", 2, "yesno", "Sudden double vision / droopy eyelid with headache, a big pupil, or weakness / speech problem?",
  "क्या अचानक दोहरा दिखना / पलक झुकना, साथ में सिर दर्द, बड़ी पुतली, या कमज़ोरी / बोली की तकलीफ़?", "अचानक दोन-दोन दिसणे / पापणी लोंबणे, सोबत डोकेदुखी, मोठी बाहुली, किंवा अशक्तपणा / बोलण्याचा त्रास?",
  term="Acute painful third nerve / brainstem", rf="Painful 3rd nerve palsy / brainstem — EMERGENCY (aneurysm / stroke)", ddx=["Intracranial aneurysm", "Stroke / TIA"], src=f"{EY}, p424 (Box 20.1); {H}, Ch 16")
Q("dv_features", "double_vision", "hopi", 3, "multi", "Other features", "अन्य लक्षण", "इतर लक्षणे", term="Associated features", opts=[
    O("worse_evening", "Worse by evening, droopy lids, tired chewing", "शाम तक बढ़ता, पलकें झुकतीं, चबाने में थकान", "संध्याकाळपर्यंत वाढते, पापण्या लोंबतात, चावताना थकवा", ["Myasthenia gravis"]),
    O("bulging_thyroid", "Bulging eyes, thyroid problem", "आँखें बाहर, थायराइड", "डोळे बाहेर, थायरॉईड", ["Thyroid eye disease"]),
    O("dm_painful", "Diabetic, pain around eye, came over a day", "शुगर, आँख के आसपास दर्द, एक दिन में आया", "मधुमेह, डोळ्याभोवती दुखणे, एका दिवसात आले", ["Diabetic cranial nerve palsy"]),
    O("child_squint", "Child with squint", "बच्चे में भेंगापन", "मुलात तिरळेपणा", ["Childhood strabismus / amblyopia"]),
    O("old_droop", "Elderly, slow droop of lid, no double vision", "बुज़ुर्ग, पलक धीरे-धीरे झुकी, दोहरा नहीं", "वृद्ध, पापणी हळूहळू लोंबली, दोन-दोन नाही", ["Age-related ptosis"]),
    O("small_pupil_droop", "Small pupil + slight droop + no sweating on that side", "छोटी पुतली + हल्की झुकी पलक + उस तरफ पसीना नहीं", "लहान बाहुली + थोडी लोंबलेली पापणी + त्या बाजूला घाम नाही", ["Horner's syndrome (check lung apex / neck)"])],
  src=f"{EY}, p424-425 (Box 20.1-20.3)")
Q("dv_child_flag", "double_vision", "redflag", 4, "yesno", "(Child) White reflex in pupil in photos, or new squint?", "(बच्चा) फ़ोटो में पुतली में सफ़ेद चमक, या नया भेंगापन?",
  "(मूल) फोटोत बाहुलीत पांढरी चमक, किंवा नवीन तिरळेपणा?", term="Leukocoria / new squint in child", rf="Leukocoria / new squint in child — urgent (retinoblastoma / cataract)",
  ddx=["Retinoblastoma", "Congenital cataract"], applies={"max_age": 12}, src="General clinical practice")

# ---------------------------------------------------------------- FLOATERS / FLASHES / CURTAIN  (Table 20.1)
FL = f"{EY}, p419-420 (Table 20.1)"
Q("fl_detach", "floaters", "redflag", 1, "yesno", "New shower of floaters, flashes, or a curtain / shadow spreading across vision?",
  "क्या अचानक बहुत सारे धब्बे, चमक, या दिखने पर फैलता पर्दा / परछाईं?", "अचानक खूप ठिपके, चमक, किंवा दृष्टीवर पसरणारा पडदा / सावली?",
  term="Retinal detachment symptoms", rf="Possible retinal tear / detachment — SAME-DAY eye assessment", ddx=["Retinal detachment"], src=FL)
Q("fl_pattern", "floaters", "hopi", 2, "choice", "What is seen?", "क्या दिखता है?", "काय दिसते?", term="Pattern", opts=[
    O("few_old", "A few old floaters, unchanged for years", "कुछ पुराने धब्बे, सालों से वैसे ही", "काही जुने ठिपके, वर्षानुवर्षे तसेच", ["Benign vitreous floaters"]),
    O("new_few_flash", "New floaters with occasional flashes (age >50)", "नए धब्बे, कभी-कभी चमक (50+ उम्र)", "नवीन ठिपके, कधी कधी चमक (50+ वय)", ["Posterior vitreous detachment"]),
    O("many_red_dm", "Many floaters / red haze, diabetic", "बहुत धब्बे / लाल धुंध, शुगर वाले", "खूप ठिपके / लाल धूसरपणा, मधुमेही", ["Vitreous haemorrhage"]),
    O("curtain", "Curtain / shadow from one side", "एक तरफ से पर्दा / परछाईं", "एका बाजूने पडदा / सावली", ["Retinal detachment"])],
  src=FL)
Q("fl_risk", "floaters", "risk", 3, "multi", "Risk factors", "जोखिम", "जोखीम", term="Retinal detachment risk", opts=[
    O("myopia", "High minus glasses (short-sighted)", "ज़्यादा माइनस नंबर का चश्मा", "जास्त मायनस नंबरचा चष्मा", ["Retinal detachment"]),
    O("cataract_op", "Cataract operation before", "पहले मोतियाबिंद का ऑपरेशन", "आधी मोतीबिंदूचे ऑपरेशन", ["Retinal detachment"]),
    O("eye_injury", "Eye injury", "आँख में चोट", "डोळ्याला इजा", ["Retinal detachment"]),
    O("dm", "Diabetes", "शुगर", "मधुमेह", ["Vitreous haemorrhage"])],
  src=FL)
