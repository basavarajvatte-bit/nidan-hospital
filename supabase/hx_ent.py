# ====================================================================== SYSTEM 10: ENT (ear, nose, throat, mouth)
# Hutchison 24e, Ch 21 (Ear, nose and throat), p439-464; Box 21.1 (otalgia), Table 21.1 (otorrhoea), Box 21.2 (deafness),
# 21.3 (vertigo), nose symptoms p452-455, 21.6-21.11 (mouth, stridor, dysphonia, salivary, neck lumps). Executed inside hx_bank.py.

ENT = f"{H}, Ch 21"

C("ear_pain", "ENT", "Ear pain", "कान दर्द", "कानदुखी", "👂", 101, f"{ENT}, p441 (Box 21.1)")
C("ear_discharge", "ENT", "Ear discharge", "कान बहना / मवाद", "कान वाहणे / पू", "💧", 102, f"{ENT}, p441-442 (Table 21.1)")
C("hearing_loss", "ENT", "Hearing loss / ringing in ear", "कम सुनाई देना / कान में आवाज़", "कमी ऐकू येणे / कानात आवाज", "🔇", 103, f"{ENT}, p441-442 (Box 21.2)")
C("nose", "ENT", "Blocked / runny nose, sneezing, sinus", "नाक बंद / बहना, छींक, साइनस", "नाक बंद / वाहणे, शिंका, सायनस", "👃", 104, f"{ENT}, p452-455")
C("nosebleed", "ENT", "Nose bleed", "नकसीर (नाक से ख़ून)", "नाकातून रक्त (घोळणा)", "🩸", 105, f"{ENT}, p452-453")
C("sore_throat", "ENT", "Sore throat", "गले में ख़राश / दर्द", "घसा खवखवणे / दुखणे", "🗣️", 106, f"{ENT}, p458-459")
C("hoarseness", "ENT", "Hoarse voice", "आवाज़ बैठना / भारी", "आवाज बसणे / जड", "🎤", 107, f"{ENT}, p460 (Box 21.8)")
C("mouth", "ENT", "Mouth ulcer / white patch / can't open mouth", "मुँह में छाले / सफ़ेद धब्बा / मुँह कम खुलना", "तोंडात फोड / पांढरा डाग / तोंड कमी उघडणे", "👄", 108, f"{ENT}, p458-459 (Box 21.6)")

# ---------------------------------------------------------------- EAR PAIN  (Box 21.1)
EP = f"{ENT}, p441 (Box 21.1)"
Q("ep_ear_or_referred", "ear_pain", "hopi", 1, "multi", "Along with ear pain", "कान दर्द के साथ", "कानदुखीसोबत", term="Ear vs referred pain", opts=[
    O("discharge_deaf", "Discharge / blocked or less hearing", "कान बहना / बंद या कम सुनाई", "कान वाहणे / बंद किंवा कमी ऐकू", ["Acute otitis media", "Otitis externa"]),
    O("cold_child", "After cold, with fever (child)", "सर्दी के बाद, बुखार के साथ (बच्चा)", "सर्दीनंतर, तापासोबत (मूल)", ["Acute otitis media"]),
    O("touch_pinna", "Pain on touching / pulling the ear, itchy canal", "कान छूने / खींचने पर दर्द, अंदर खुजली", "कानाला स्पर्श / ओढल्यावर दुखणे, आत खाज", ["Otitis externa", "Furunculosis"]),
    O("throat_teeth", "Sore throat / tooth pain / jaw clicking (ear looks normal)", "गला दर्द / दाँत दर्द / जबड़े में खट-खट (कान ठीक)", "घसा / दातदुखी / जबड्यात कटकट (कान ठीक)", ["Referred otalgia (throat / teeth / TMJ)"]),
    O("flight_dive", "After flight / diving", "हवाई यात्रा / गोताखोरी के बाद", "विमान प्रवास / पाण्यात सूर मारल्यानंतर", ["Barotrauma"]),
    O("cotton_bud_water", "Cotton bud use / water in ear / swimming", "ईयरबड / कान में पानी / तैरना", "इअरबड / कानात पाणी / पोहणे", ["Otitis externa"])],
  src=EP)
Q("ep_red", "ear_pain", "redflag", 2, "multi", "Danger signs", "ख़तरे के निशान", "धोक्याची चिन्हे", term="Otalgia red flags", opts=[
    O("mastoid", "Swelling / redness behind the ear, ear pushed forward", "कान के पीछे सूजन / लाली, कान आगे की ओर", "कानामागे सूज / लाली, कान पुढे ढकललेला", ["Mastoiditis"]),
    O("face_weak_blisters", "Face weakness / blisters on ear", "चेहरा कमज़ोर / कान पर छाले", "चेहरा कमजोर / कानावर फोड", ["Ramsay Hunt (herpes zoster)"]),
    O("diabetic_elderly_severe", "Diabetic / elderly with severe pain for weeks, granulation", "शुगर वाले / बुज़ुर्ग में हफ़्तों से तेज़ दर्द", "मधुमेही / वृद्धांत आठवड्यांपासून तीव्र दुखणे", ["Necrotising otitis externa"]),
    O("headache_neck_drowsy", "Severe headache, neck stiffness, drowsy, vomiting", "तेज़ सिर दर्द, गर्दन अकड़, सुस्ती, उल्टी", "तीव्र डोकेदुखी, मान ताठ, गुंगी, उलटी", ["Intracranial complication of otitis"])],
  src=EP)
Q("ep_red_flag", "ear_pain", "redflag", 3, "yesno", "Swelling behind ear, face weakness, or headache/drowsiness with ear infection?",
  "क्या कान के पीछे सूजन, चेहरा कमज़ोर, या कान के इन्फेक्शन के साथ सिर दर्द/सुस्ती?", "कानामागे सूज, चेहरा कमजोर, किंवा कानाच्या संसर्गासोबत डोकेदुखी/गुंगी?",
  term="Complicated ear infection", rf="Complicated ear infection (mastoiditis / intracranial / facial palsy) — URGENT ENT",
  ddx=["Mastoiditis", "Intracranial complication of otitis", "Ramsay Hunt (herpes zoster)"], src=EP)
Q("ep_older_unilateral", "ear_pain", "redflag", 4, "yesno", "Adult with one-sided ear pain, normal ear, plus tobacco use / swallowing pain / hoarse voice?",
  "क्या बड़े व्यक्ति में एक तरफ कान दर्द, कान ठीक, साथ में तंबाकू / निगलने में दर्द / आवाज़ बैठी?", "प्रौढ व्यक्तीला एका बाजूला कानदुखी, कान ठीक, सोबत तंबाखू / गिळताना दुखणे / आवाज बसला?",
  term="Referred otalgia with head & neck cancer risk", rf="Possible throat cancer (referred ear pain) — ENT scope", ddx=["Head and neck cancer"], applies={"min_age": 35}, src=EP)

# ---------------------------------------------------------------- EAR DISCHARGE  (Table 21.1)
ED = f"{ENT}, p441-442 (Table 21.1)"
Q("ed_type", "ear_discharge", "hopi", 1, "choice", "What is the discharge like?", "कान से क्या निकलता है?", "कानातून काय निघते?", term="Character of otorrhoea", opts=[
    O("pus_after_pain", "Pus after ear pain (pain eased when it burst)", "कान दर्द के बाद मवाद (फूटने पर दर्द कम)", "कानदुखीनंतर पू (फुटल्यावर दुखणे कमी)", ["Acute otitis media"]),
    O("chronic_mucoid", "Comes and goes for months / years, sticky", "महीनों / सालों से आता-जाता, चिपचिपा", "महिने / वर्षे येते-जाते, चिकट", ["Chronic suppurative otitis media"]),
    O("foul_scanty", "Small amount, very foul smell, constant", "थोड़ा, बहुत बदबूदार, लगातार", "थोडे, खूप दुर्गंधीयुक्त, सतत", ["Cholesteatoma"]),
    O("watery_clear_trauma", "Clear watery fluid after head injury", "सिर की चोट के बाद साफ़ पानी", "डोक्याला इजेनंतर स्वच्छ पाणी", ["CSF leak (skull base fracture)"]),
    O("blood", "Blood", "ख़ून", "रक्त", ["Trauma", "Chronic suppurative otitis media", "Ear canal malignancy"]),
    O("itchy_flaky", "Itchy, flaky / black-white bits (fungal)", "खुजली, पपड़ी / काले-सफ़ेद कण (फ़ंगस)", "खाज, खपल्या / काळे-पांढरे कण (बुरशी)", ["Otitis externa", "Otomycosis"])],
  src=ED)
Q("ed_complication", "ear_discharge", "redflag", 2, "yesno", "Discharging ear with headache, fever, dizziness, face weakness, or clear fluid after injury?",
  "क्या बहते कान के साथ सिर दर्द, बुखार, चक्कर, चेहरा कमज़ोर, या चोट के बाद साफ़ पानी?", "वाहणाऱ्या कानासोबत डोकेदुखी, ताप, चक्कर, चेहरा कमजोर, किंवा इजेनंतर स्वच्छ पाणी?",
  term="Complicated otorrhoea / CSF leak", rf="Complicated ear discharge or CSF leak — URGENT", ddx=["Intracranial complication of otitis", "CSF leak (skull base fracture)", "Cholesteatoma"], src=ED)
Q("ed_habits", "ear_discharge", "risk", 3, "multi", "Habits / history", "आदतें / पहले", "सवयी / आधी", term="Contributing factors", opts=[
    O("oil_drops", "Putting oil / garlic / home drops in ear", "कान में तेल / लहसुन / घरेलू बूँदें डालना", "कानात तेल / लसूण / घरगुती थेंब घालणे", ["Otomycosis", "Otitis externa"]),
    O("pond_bath", "Bathing in pond / river", "तालाब / नदी में नहाना", "तलाव / नदीत आंघोळ", ["Chronic suppurative otitis media"]),
    O("perforation_known", "Known hole in ear drum", "कान के पर्दे में छेद पता है", "कानाच्या पडद्याला छिद्र माहीत आहे", ["Chronic suppurative otitis media"]),
    O("dm", "Diabetes", "शुगर", "मधुमेह", ["Necrotising otitis externa", "Otomycosis"])],
  src=ED)

# ---------------------------------------------------------------- HEARING LOSS / TINNITUS  (Box 21.2)
HL = f"{ENT}, p441-442 (Box 21.2)"
Q("hl_onset", "hearing_loss", "hopi", 1, "choice", "How did it start?", "कम सुनाई कैसे शुरू हुआ?", "कमी ऐकू येणे कसे सुरू झाले?", term="Onset", opts=[
    O("sudden", "Suddenly (over hours / overnight)", "अचानक (घंटों में / रातों-रात)", "अचानक (तासांत / रात्रीतून)", ["Sudden sensorineural hearing loss"]),
    O("after_cold", "After a cold, ear feels full", "सर्दी के बाद, कान भरा लगता", "सर्दीनंतर, कान भरल्यासारखा", ["Middle ear effusion / Eustachian tube dysfunction"]),
    O("gradual_both_old", "Slowly over years, both ears, older age", "सालों में धीरे-धीरे, दोनों कान, बुढ़ापा", "वर्षांत हळूहळू, दोन्ही कान, वृद्धत्व", ["Presbycusis (age-related)"]),
    O("gradual_one", "Slowly, one ear only", "धीरे-धीरे, सिर्फ़ एक कान", "हळूहळू, फक्त एक कान", ["Acoustic neuroma", "Otosclerosis", "Chronic suppurative otitis media"]),
    O("wax_block", "Blocked feeling after bath / cotton bud", "नहाने / ईयरबड के बाद बंद लगना", "आंघोळ / इअरबडनंतर बंद वाटणे", ["Ear wax"])],
  src=HL)
Q("hl_sudden_flag", "hearing_loss", "redflag", 2, "yesno", "Sudden hearing loss in one ear within the last 2 weeks (ear looks normal)?",
  "क्या पिछले 2 हफ़्ते में एक कान से अचानक सुनाई कम हुआ (कान ठीक दिखता)?", "मागील 2 आठवड्यांत एका कानाने अचानक कमी ऐकू येऊ लागले (कान ठीक दिसतो)?",
  term="Sudden SNHL", rf="Sudden sensorineural hearing loss — URGENT (treat within days)", ddx=["Sudden sensorineural hearing loss"], src=HL)
Q("hl_assoc", "hearing_loss", "associated", 3, "multi", "Along with", "साथ में", "सोबत", term="Associated symptoms", opts=[
    O("tinnitus", "Ringing / buzzing in ear", "कान में सीटी / भिनभिनाहट", "कानात शिट्टी / गुणगुण", ["Presbycusis (age-related)", "Noise-induced hearing loss", "Meniere's disease"]),
    O("vertigo", "Spinning episodes", "चक्कर के दौरे", "चक्करचे झटके", ["Meniere's disease", "Acoustic neuroma"]),
    O("pulsatile", "Tinnitus beating with heartbeat", "धड़कन के साथ कान में धक-धक", "ठोक्यांसोबत कानात धकधक", ["Vascular tinnitus"]),
    O("face_numb", "Face numbness / weakness / unsteady", "चेहरा सुन्न / कमज़ोर / लड़खड़ाहट", "चेहरा बधिर / कमजोर / डगमग", ["Acoustic neuroma"]),
    O("discharge", "Ear discharge", "कान बहना", "कान वाहणे", ["Chronic suppurative otitis media"])],
  src=f"{HL}; Box 21.3")
Q("hl_causes", "hearing_loss", "risk", 4, "multi", "Possible causes", "संभावित कारण", "संभाव्य कारणे", term="Risk factors", opts=[
    O("noise", "Loud noise at work / DJ / firecrackers / guns", "काम पर तेज़ आवाज़ / डीजे / पटाखे / बंदूक", "कामावर मोठा आवाज / डीजे / फटाके / बंदूक", ["Noise-induced hearing loss"]),
    O("ototoxic", "Injections like streptomycin / amikacin (TB), chemo, high-dose diuretics", "स्ट्रेप्टोमाइसिन / एमिकासिन (टीबी) इंजेक्शन, कीमो, ज़्यादा डोज़ पेशाब की दवा", "स्ट्रेप्टोमायसिन / अमिकासिन (टीबी) इंजेक्शन, केमो, जास्त लघवीचे औषध", ["Ototoxic hearing loss"]),
    O("family", "Deafness in family / at young age", "परिवार में बहरापन / कम उम्र में", "कुटुंबात बहिरेपणा / कमी वयात", ["Otosclerosis", "Genetic hearing loss"]),
    O("head_injury", "Head injury", "सिर की चोट", "डोक्याला इजा", ["Traumatic hearing loss"]),
    O("child_speech", "(Child) Speech delay / not responding to name", "(बच्चा) बोलने में देरी / नाम पुकारने पर ध्यान नहीं", "(मूल) बोलण्यात उशीर / नावाने हाक मारल्यावर लक्ष नाही", ["Congenital / childhood hearing loss"])],
  src=HL)
Q("hl_impact", "hearing_loss", "hopi", 5, "yesno", "Turns TV up loud / misses conversation / asks to repeat?", "क्या टीवी तेज़ करते हैं / बात समझ नहीं आती / दोबारा पूछते हैं?",
  "टीव्ही मोठा लावतात / संभाषण कळत नाही / पुन्हा विचारतात?", term="Functional impact", src=HL)

# ---------------------------------------------------------------- NOSE / SINUS  (p452-455)
NS2 = f"{ENT}, p452-455"
Q("ns_symptoms", "nose", "hopi", 1, "multi", "Nose symptoms", "नाक की तकलीफ़", "नाकाचा त्रास", term="Nasal symptoms", opts=[
    O("sneeze_itch", "Sneezing, itchy watery nose / eyes", "छींकें, नाक / आँख में खुजली व पानी", "शिंका, नाक / डोळ्यांना खाज व पाणी", ["Allergic rhinitis"]),
    O("block_both_alt", "Blocked, alternating sides", "बंद, कभी एक तरफ कभी दूसरी", "बंद, कधी एका कधी दुसऱ्या बाजूला", ["Allergic rhinitis", "Rhinitis"]),
    O("block_one_constant", "Always blocked on one side", "हमेशा एक तरफ बंद", "नेहमी एका बाजूला बंद", ["Deviated septum", "Nasal polyp", "Sinonasal tumour"]),
    O("yellow_green", "Thick yellow / green discharge", "गाढ़ा पीला / हरा स्राव", "दाट पिवळा / हिरवा स्राव", ["Sinusitis"]),
    O("face_pain", "Face / forehead pain worse on bending", "चेहरे / माथे पर दर्द, झुकने पर बढ़ता", "चेहऱ्यावर / कपाळावर दुखणे, वाकल्यावर वाढते", ["Sinusitis"]),
    O("smell_loss", "Loss of smell", "गंध न आना", "वास न येणे", ["Nasal polyp", "Sinusitis", "Post-viral anosmia"]),
    O("snoring_mouth_child", "(Child) Mouth breathing, snoring", "(बच्चा) मुँह से साँस, खर्राटे", "(मूल) तोंडाने श्वास, घोरणे", ["Adenotonsillar hypertrophy"])],
  src=f"{NS2} (symptoms of nasal disease)")
Q("ns_red", "nose", "redflag", 2, "multi", "Danger signs", "ख़तरे के निशान", "धोक्याची चिन्हे", term="Sinonasal red flags", opts=[
    O("eye_swelling", "Swelling around eye / double vision / eye pushed out", "आँख के आसपास सूजन / दोहरा दिखना / आँख बाहर", "डोळ्याभोवती सूज / दोन-दोन दिसणे / डोळा बाहेर", ["Orbital cellulitis (sinus)"]),
    O("one_side_blood_adult", "Adult: one-side blockage with blood-stained discharge", "बड़े: एक तरफ नाक बंद, ख़ून वाला स्राव", "प्रौढ: एका बाजूला नाक बंद, रक्तमिश्रित स्राव", ["Sinonasal tumour"]),
    O("child_foul_one", "Child: foul discharge from one nostril", "बच्चा: एक नथुने से बदबूदार स्राव", "मूल: एका नाकपुडीतून दुर्गंधीयुक्त स्राव", ["Nasal foreign body"]),
    O("black_crust_dm", "Diabetic: black crust in nose / face pain / swelling", "शुगर वाले: नाक में काली पपड़ी / चेहरा दर्द / सूजन", "मधुमेही: नाकात काळी खपली / चेहऱ्यावर दुखणे / सूज", ["Mucormycosis"]),
    O("clear_after_injury", "Clear watery drip after head injury", "सिर की चोट के बाद साफ़ पानी टपकना", "डोक्याला इजेनंतर स्वच्छ पाणी टपकणे", ["CSF leak (skull base fracture)"])],
  src=f"{NS2} (orbital spread, unilateral discharge)")
Q("ns_red_flag", "nose", "redflag", 3, "yesno", "Eye swelling / double vision, black crust in diabetic, or one-sided bloody discharge?",
  "क्या आँख पर सूजन / दोहरा दिखना, शुगर वाले में काली पपड़ी, या एक तरफ ख़ून वाला स्राव?", "डोळ्यावर सूज / दोन-दोन दिसणे, मधुमेहींत काळी खपली, किंवा एका बाजूला रक्तमिश्रित स्राव?",
  term="Sinonasal emergency / malignancy", rf="Orbital complication / mucormycosis / tumour — URGENT ENT", ddx=["Orbital cellulitis (sinus)", "Mucormycosis", "Sinonasal tumour"], src=NS2)
Q("ns_allergen", "nose", "risk", 4, "multi", "Triggers", "किससे बढ़ता है?", "कशाने वाढते?", term="Allergens / irritants (Box 21.5)", opts=[
    O("dust", "House dust / sweeping", "घर की धूल / झाड़ू", "घरातील धूळ / झाडणे", ["Allergic rhinitis"]),
    O("season", "Certain season / pollen", "किसी मौसम में / पराग", "विशिष्ट ऋतूत / परागकण", ["Allergic rhinitis"]),
    O("pets", "Pets / feathers", "पालतू जानवर / पंख", "पाळीव प्राणी / पिसे", ["Allergic rhinitis"]),
    O("smoke_perfume", "Smoke / perfume / cold air", "धुआँ / परफ़्यूम / ठंडी हवा", "धूर / अत्तर / थंड हवा", ["Rhinitis"]),
    O("nasal_spray_overuse", "Using nose-opening spray (e.g. Otrivin) for weeks", "हफ़्तों से नाक खोलने वाला स्प्रे (ओट्रिविन)", "आठवड्यांपासून नाक मोकळे करणारा स्प्रे (ऑट्रिव्हिन)", ["Rhinitis medicamentosa"])],
  src=f"{ENT}, p455 (Box 21.5)")
Q("ns_asthma", "nose", "associated", 5, "yesno", "Asthma / wheeze too?", "क्या दमा / सीटी भी?", "दमा / शिट्टीही?", term="Associated asthma", ddx=["Allergic rhinitis", "Nasal polyp"], key="atopy", src=f"{H}, Ch 12, p169")

# ---------------------------------------------------------------- NOSEBLEED
NB2 = f"{ENT}, p452-453"
Q("nx_amount", "nosebleed", "redflag", 1, "yesno", "Heavy bleeding not stopping after 20 minutes of pinching, or dizziness / fainting?",
  "क्या 20 मिनट नाक दबाने के बाद भी ज़्यादा ख़ून नहीं रुक रहा, या चक्कर / बेहोशी?", "20 मिनिटे नाक दाबूनही जास्त रक्त थांबत नाही, किंवा चक्कर / बेशुद्धी?",
  term="Severe epistaxis", rf="Severe epistaxis — URGENT (pack, check BP, Hb)", ddx=["Posterior epistaxis"], src=NB2)
Q("nx_pattern", "nosebleed", "hopi", 2, "choice", "Pattern", "कैसे आता है?", "कसे येते?", term="Pattern", opts=[
    O("child_front", "Child, from front of nose, nose picking / dry weather", "बच्चा, नाक के आगे से, नाक में उँगली / सूखा मौसम", "मूल, नाकाच्या पुढच्या भागातून, नाकात बोट / कोरडे हवामान", ["Anterior epistaxis (Little's area)"]),
    O("elderly_back", "Elderly, blood going down the throat", "बुज़ुर्ग, ख़ून गले में जाता", "वृद्ध, रक्त घशात जाते", ["Posterior epistaxis"]),
    O("boy_one_side_block", "Teenage boy: repeated one-side bleeds with blocked nose", "किशोर लड़का: एक तरफ बार-बार ख़ून और नाक बंद", "किशोर मुलगा: एका बाजूला वारंवार रक्त व नाक बंद", ["Juvenile nasopharyngeal angiofibroma"], only={"sex": "male"}),
    O("after_injury", "After injury to nose", "नाक पर चोट के बाद", "नाकाला इजेनंतर", ["Nasal fracture"])],
  src=NB2)
Q("nx_causes", "nosebleed", "risk", 3, "multi", "Possible causes", "संभावित कारण", "संभाव्य कारणे", term="Contributing factors", opts=[
    O("bp", "High BP", "हाई बीपी", "उच्च रक्तदाब", ["Hypertension-related epistaxis"]),
    O("thinner", "Blood thinners / aspirin", "ख़ून पतला करने की दवा / एस्पिरिन", "रक्त पातळ करणारी औषधे / ॲस्पिरिन", ["Anticoagulant-related bleeding"]),
    O("bruising", "Easy bruising / gum bleeding", "आसानी से नील / मसूड़ों से ख़ून", "सहज काळे-निळे / हिरड्यांतून रक्त", ["Bleeding disorder"]),
    O("fever", "Fever / dengue season", "बुखार / डेंगू का मौसम", "ताप / डेंग्यूचा हंगाम", ["Dengue"]),
    O("liver_alcohol", "Liver disease / alcohol", "लिवर रोग / शराब", "यकृत आजार / दारू", ["Chronic liver disease / cirrhosis"])],
  src=NB2)

# ---------------------------------------------------------------- SORE THROAT  (p458-459, Box 21.7)
TH2 = f"{ENT}, p458-459"
Q("st2_danger", "sore_throat", "redflag", 1, "yesno", "Can't swallow own saliva / drooling, noisy breathing, muffled voice, or can't open mouth?",
  "क्या अपना थूक भी नहीं निगल पा रहे / लार टपकना, आवाज़ वाली साँस, दबी आवाज़, या मुँह नहीं खुलता?",
  "स्वतःची लाळही गिळता येत नाही / लाळ गळणे, आवाजासह श्वास, दबलेला आवाज, किंवा तोंड उघडत नाही?",
  term="Airway-threatening sore throat", rf="Possible epiglottitis / quinsy / deep neck abscess — AIRWAY EMERGENCY",
  ddx=["Epiglottitis", "Peritonsillar abscess (quinsy)", "Deep neck abscess"], src=f"{ENT}, p459 (Box 21.7)")
Q("st2_features", "sore_throat", "hopi", 2, "multi", "Features", "लक्षण", "लक्षणे", term="Features (Centor-type)", opts=[
    O("fever", "Fever", "बुखार", "ताप", ["Bacterial tonsillitis (strep)"]),
    O("no_cough", "No cough", "खाँसी नहीं", "खोकला नाही", ["Bacterial tonsillitis (strep)"]),
    O("white_tonsils", "White patches on tonsils", "टॉन्सिल पर सफ़ेद धब्बे", "टॉन्सिलवर पांढरे डाग", ["Bacterial tonsillitis (strep)", "Infectious mononucleosis"]),
    O("neck_glands", "Tender glands in neck", "गर्दन में दर्दनाक गिल्टियाँ", "मानेत दुखऱ्या ग्रंथी", ["Bacterial tonsillitis (strep)"]),
    O("cold_cough", "Runny nose, cough, hoarse (viral)", "नाक बहना, खाँसी, आवाज़ बैठी (वायरल)", "नाक वाहणे, खोकला, आवाज बसला (व्हायरल)", ["Viral pharyngitis"]),
    O("grey_membrane", "Grey membrane in throat, bull-neck, unvaccinated child", "गले में स्लेटी झिल्ली, गर्दन सूजी, बिना टीके का बच्चा", "घशात करडा पडदा, मान सुजलेली, लस न घेतलेले मूल", ["Diphtheria"]),
    O("one_side_severe", "Severe pain one side, voice muffled", "एक तरफ बहुत दर्द, आवाज़ दबी", "एका बाजूला खूप दुखणे, आवाज दबलेला", ["Peritonsillar abscess (quinsy)"])],
  src=TH2)
Q("st2_duration", "sore_throat", "redflag", 3, "yesno", "Sore throat or swallowing pain for more than 3 weeks (esp. tobacco / alcohol user)?",
  "क्या 3 हफ़्ते से ज़्यादा गला दर्द या निगलने में दर्द (ख़ासकर तंबाकू / शराब वाले)?", "3 आठवड्यांपेक्षा जास्त घसा दुखणे किंवा गिळताना दुखणे (विशेषतः तंबाखू / दारू घेणाऱ्यांत)?",
  term="Persistent sore throat", rf="Persistent throat symptoms — exclude head & neck cancer", ddx=["Head and neck cancer"], src=f"{ENT}, p460-461")
Q("st2_recurrent", "sore_throat", "risk", 4, "yesno", "Tonsillitis many times a year / joint pain or heart problem after sore throat?",
  "क्या साल में कई बार टॉन्सिल / गला ख़राब होने के बाद जोड़ों में दर्द या दिल की तकलीफ़?", "वर्षातून अनेकदा टॉन्सिल / घसा खवखवल्यानंतर सांधेदुखी किंवा हृदयाचा त्रास?",
  term="Recurrent tonsillitis / rheumatic sequelae", ddx=["Recurrent tonsillitis", "Rheumatic fever"], src=f"{H}, Ch 13, p239 (Box 13.26)")
Q("st2_immuno", "sore_throat", "risk", 5, "yesno", "On thyroid (carbimazole) / chemo / clozapine tablets? (can lower white cells)", "क्या थायराइड (कार्बिमाज़ोल) / कीमो / क्लोज़ापीन की गोली? (सफ़ेद कोशिकाएँ घट सकती हैं)",
  "थायरॉईड (कार्बिमाझोल) / केमो / क्लोझापिन गोळी? (पांढऱ्या पेशी कमी होऊ शकतात)", term="Drug-induced agranulocytosis risk",
  rf="Sore throat on carbimazole/clozapine/chemo — urgent CBC (agranulocytosis)", ddx=["Neutropenic sepsis"], src="General clinical practice")

# ---------------------------------------------------------------- HOARSENESS  (Box 21.8)
HO = f"{ENT}, p460 (Box 21.8)"
Q("ho_duration", "hoarseness", "redflag", 1, "yesno", "Hoarse for more than 3–4 weeks?", "क्या 3–4 हफ़्ते से ज़्यादा आवाज़ बैठी है?", "3–4 आठवड्यांपेक्षा जास्त आवाज बसला आहे का?",
  term="Persistent dysphonia", rf="Hoarseness >3–4 weeks — laryngoscopy (exclude cancer)", ddx=["Laryngeal cancer", "Lung cancer (recurrent laryngeal nerve)"], src=f"{H}, Ch 12, p169; {HO}")
Q("ho_cause", "hoarseness", "hopi", 2, "multi", "Possible causes", "संभावित कारण", "संभाव्य कारणे", term="Causes of dysphonia", opts=[
    O("cold_shout", "After cold / shouting / singing", "सर्दी / चिल्लाने / गाने के बाद", "सर्दी / ओरडणे / गाण्यानंतर", ["Acute laryngitis", "Vocal nodules"]),
    O("voice_use", "Teacher / vendor / singer (voice use)", "शिक्षक / फेरीवाला / गायक (ज़्यादा बोलना)", "शिक्षक / फेरीवाला / गायक (जास्त बोलणे)", ["Vocal nodules"]),
    O("smoke", "Smoking / tobacco", "धूम्रपान / तंबाकू", "धूम्रपान / तंबाखू", ["Laryngeal cancer", "Reinke's oedema"]),
    O("reflux", "Acidity / throat clearing", "एसिडिटी / बार-बार गला साफ़ करना", "ॲसिडिटी / वारंवार घसा साफ करणे", ["Laryngopharyngeal reflux"]),
    O("thyroid_op", "After thyroid / neck / chest operation", "थायराइड / गर्दन / छाती के ऑपरेशन के बाद", "थायरॉईड / मान / छाती ऑपरेशननंतर", ["Recurrent laryngeal nerve palsy"]),
    O("inhaler", "Steroid inhaler", "स्टेरॉयड इनहेलर", "स्टिरॉइड इनहेलर", ["Inhaled steroid dysphonia / candida"]),
    O("hypothyroid", "Feeling cold, slow, weight gain", "ठंड, सुस्ती, वज़न बढ़ना", "थंडी, सुस्ती, वजन वाढ", ["Hypothyroidism"])],
  src=HO)
Q("ho_stridor", "hoarseness", "redflag", 3, "yesno", "Noisy breathing in / breathlessness / coughing blood?", "क्या साँस लेते समय आवाज़ / साँस फूलना / खाँसी में ख़ून?",
  "श्वास घेताना आवाज / धाप / खोकल्यात रक्त?", term="Stridor / haemoptysis", rf="Hoarseness with stridor/haemoptysis — URGENT airway assessment",
  ddx=["Laryngeal cancer", "Upper airway obstruction / foreign body"], src=f"{ENT}, p459 (Box 21.7)")

# ---------------------------------------------------------------- MOUTH  (Box 21.6; oral pre-cancer — important in India)
MO = f"{ENT}, p458-459 (Box 21.6)"
Q("mo_type", "mouth", "hopi", 1, "multi", "What is the problem?", "मुँह में क्या तकलीफ़?", "तोंडात काय त्रास?", term="Oral lesion", opts=[
    O("small_ulcers_recurrent", "Small painful ulcers that heal in 1–2 weeks, keep coming", "छोटे दर्दनाक छाले, 1–2 हफ़्ते में ठीक, बार-बार", "लहान दुखरे फोड, 1–2 आठवड्यांत बरे, वारंवार", ["Aphthous ulcers", "Vitamin deficiency"]),
    O("non_healing", "Ulcer not healing > 3 weeks", "3 हफ़्ते से ज़्यादा न भरने वाला छाला", "3 आठवड्यांहून जास्त न भरणारा फोड", ["Oral cancer"]),
    O("white_patch", "White patch that can't be scraped off", "सफ़ेद धब्बा जो रगड़ने से नहीं हटता", "पांढरा डाग जो घासल्यावर जात नाही", ["Leukoplakia (pre-cancer)"]),
    O("red_patch", "Red velvety patch", "लाल मख़मली धब्बा", "लाल मखमली डाग", ["Erythroplakia (pre-cancer)"]),
    O("cant_open", "Mouth opening less, burning with spicy food, stiff cheeks", "मुँह कम खुलना, तीखे से जलन, गाल सख़्त", "तोंड कमी उघडणे, तिखटाने जळजळ, गाल कडक", ["Oral submucous fibrosis"]),
    O("white_wipes", "White coating that wipes off (thrush)", "सफ़ेद परत जो पोंछने से हट जाती", "पांढरा थर जो पुसल्यावर जातो", ["Oral candidiasis"]),
    O("burning", "Burning mouth / sore smooth tongue", "मुँह में जलन / चिकनी दर्दनाक जीभ", "तोंडात जळजळ / गुळगुळीत दुखरी जीभ", ["Iron deficiency anaemia", "B12 / folate deficiency"]),
    O("gum_tooth", "Swollen gum / tooth pain / pus", "मसूड़ा सूजा / दाँत दर्द / मवाद", "हिरडी सुजली / दातदुखी / पू", ["Dental abscess"])],
  src=MO)
Q("mo_tobacco", "mouth", "risk", 2, "multi", "Habits (very important for mouth cancer)", "आदतें (मुँह के कैंसर के लिए ज़रूरी)", "सवयी (तोंडाच्या कर्करोगासाठी महत्त्वाचे)", term="Oral cancer risk habits", opts=[
    O("gutka", "Gutka / kharra / mawa / pan masala", "गुटखा / खर्रा / मावा / पान मसाला", "गुटखा / खर्रा / मावा / पान मसाला", ["Oral cancer", "Oral submucous fibrosis"]),
    O("supari", "Supari (areca nut) / paan", "सुपारी / पान", "सुपारी / पान", ["Oral submucous fibrosis", "Oral cancer"]),
    O("khaini_mishri", "Khaini / mishri / tobacco tooth powder", "खैनी / मिश्री / तंबाकू वाला मंजन", "खैनी / मिश्री / तंबाखूचे मंजन", ["Oral cancer"]),
    O("smoke", "Bidi / cigarette", "बीड़ी / सिगरेट", "बिडी / सिगारेट", ["Oral cancer"]),
    O("alcohol", "Alcohol", "शराब", "दारू", ["Oral cancer"]),
    O("sharp_tooth", "Sharp broken tooth / bad denture rubbing", "नुकीला टूटा दाँत / ख़राब दाँत का सेट रगड़ता", "टोकदार तुटलेला दात / खराब कवळी घासते", ["Traumatic ulcer"])],
  src="General clinical practice (India)")
Q("mo_cancer_flag", "mouth", "redflag", 3, "yesno", "Non-healing ulcer / white or red patch / lump in mouth or neck, in a tobacco / supari user?",
  "क्या तंबाकू / सुपारी खाने वाले में न भरने वाला छाला / सफ़ेद या लाल धब्बा / मुँह या गर्दन में गाँठ?", "तंबाखू / सुपारी खाणाऱ्यांत न भरणारा फोड / पांढरा किंवा लाल डाग / तोंडात किंवा मानेत गाठ?",
  term="Suspicious oral lesion", rf="Suspected oral pre-cancer / cancer — biopsy / refer", ddx=["Oral cancer", "Leukoplakia (pre-cancer)"], src=MO)
Q("mo_systemic", "mouth", "associated", 4, "multi", "Other clues", "अन्य", "इतर", term="Systemic associations", opts=[
    O("genital_ulcers_eye", "Genital ulcers / red eyes too", "गुप्तांग में भी छाले / आँखें लाल", "गुप्तांगातही फोड / डोळे लाल", ["Behçet's / aphthous"]),
    O("diarrhoea_wtloss", "Loose motions / weight loss", "दस्त / वज़न घटना", "जुलाब / वजन घटणे", ["IBD", "Coeliac disease"]),
    O("rash_joints", "Rash / joint pain", "दाने / जोड़ों में दर्द", "पुरळ / सांधेदुखी", ["SLE"]),
    O("hiv_steroid", "HIV / steroid inhaler / diabetes (thrush)", "एचआईवी / स्टेरॉयड इनहेलर / शुगर", "एचआयव्ही / स्टिरॉइड इनहेलर / मधुमेह", ["Oral candidiasis", "HIV"])],
  src=MO)
