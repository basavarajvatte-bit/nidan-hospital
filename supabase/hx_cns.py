# ====================================================================== SYSTEM 4: NERVOUS SYSTEM (CNS + peripheral)
# Hutchison 24e, Ch 16 (Nervous system), p309-312; Box 16.1, Table 16.1 (syncope vs seizure), Table 16.2 (headache).
# Executed inside hx_bank.py. The old combined "neuro" complaint is retired (split into the specific ones below).

NS = f"{H}, Ch 16"
TIME = f"{NS}, p309 (time course of symptoms)"

C("weakness", "Nervous system", "Weakness / paralysis", "कमज़ोरी / लकवा", "अशक्तपणा / पक्षाघात", "🦾", 41, f"{NS}, p309-310")
C("seizure", "Nervous system", "Fits / seizures", "दौरा / मिर्गी / झटके", "झटके / आकडी / फिट", "⚡", 42, f"{NS}, p310 (Table 16.1)")
C("dizziness", "Nervous system", "Dizziness / vertigo", "चक्कर / सिर घूमना", "चक्कर / डोके गरगरणे", "🌀", 43, f"{NS}, p310 (Box 16.1)")
C("numbness", "Nervous system", "Numbness / tingling", "सुन्नपन / झुनझुनी", "बधिरपणा / मुंग्या", "🖐️", 44, f"{NS}, p310 (Box 16.1)")
C("confusion", "Nervous system", "Confusion / memory loss", "भूलना / उलझन", "विसरणे / गोंधळ", "🧩", 45, f"{NS}, p310")
C("tremor", "Nervous system", "Tremor / slowness / abnormal movements", "हाथ काँपना / धीमापन", "हात थरथरणे / मंदपणा", "🫨", 46, f"{NS}, p310, p338 (Box 16.4)")

# ---------------------------------------------------------------- HEADACHE refinements (Table 16.2, p311)
HT = f"{NS}, p311 (Table 16.2)"
Q("hd_site", "headache", "hopi", 10, "choice", "Where is the headache?", "सिर दर्द कहाँ है?", "डोकेदुखी कुठे आहे?", term="Site", opts=[
    O("one_side", "One side", "एक तरफ", "एका बाजूला", ["Migraine", "Cluster headache"]),
    O("behind_eye", "Behind one eye", "एक आँख के पीछे", "एका डोळ्यामागे", ["Cluster headache", "Acute glaucoma"]),
    O("forehead_face", "Forehead / cheeks", "माथा / गाल", "कपाळ / गाल", ["Sinusitis"]),
    O("back_head", "Back of head / neck", "सिर के पीछे / गर्दन", "डोक्याच्या मागे / मान", ["Tension-type", "Cervical spondylosis", "Raised intracranial pressure"]),
    O("all_over", "All over / band-like", "पूरे सिर में / पट्टी जैसा", "संपूर्ण डोक्यात / पट्ट्यासारखे", ["Tension-type", "Migraine"])],
  src=HT)
Q("hd_timing", "headache", "hopi", 11, "choice", "How long does each attack last / how often?", "हर बार कितनी देर और कितनी बार?", "प्रत्येक वेळी किती वेळ आणि किती वेळा?",
  term="Temporal pattern", opts=[
      O("seconds_face", "Seconds, electric shocks in face", "कुछ सेकंड, चेहरे में करंट जैसा", "काही सेकंद, चेहऱ्यात करंटसारखे", ["Trigeminal neuralgia"]),
      O("up_to_1h", "Up to 1 hour, same time daily for weeks", "1 घंटे तक, हफ़्तों तक रोज़ एक ही समय", "1 तासापर्यंत, आठवडे रोज एकाच वेळी", ["Cluster headache"]),
      O("hours_days", "Hours to 3 days, with gaps", "घंटों से 3 दिन, बीच में ठीक", "तासांपासून 3 दिवस, मधे बरे", ["Migraine"]),
      O("daily", "Most days of the month", "महीने के ज़्यादातर दिन", "महिन्याचे बहुतेक दिवस", ["Tension-type", "Medication-overuse headache"]),
      O("new_constant", "New, constant, getting worse", "नया, लगातार, बढ़ता हुआ", "नवीन, सतत, वाढणारे", ["Intracranial lesion", "Raised intracranial pressure"])],
  src=HT)
Q("hd_provoke", "headache", "hopi", 12, "multi", "What brings it on / makes it worse?", "किससे शुरू होता / बढ़ता है?", "कशाने सुरू होते / वाढते?",
  term="Provoking factors", opts=[
      O("cough_strain", "Coughing / straining / bending", "खाँसना / ज़ोर लगाना / झुकना", "खोकणे / जोर लावणे / वाकणे", ["Raised intracranial pressure"]),
      O("touch_face", "Touching face / chewing / brushing teeth", "चेहरा छूना / चबाना / ब्रश करना", "चेहऱ्याला स्पर्श / चावणे / ब्रश करणे", ["Trigeminal neuralgia"]),
      O("alcohol", "Alcohol", "शराब", "दारू", ["Cluster headache", "Migraine"]),
      O("sleep_food", "Missed meals / poor sleep / periods", "खाना छूटना / नींद कम / माहवारी", "जेवण चुकणे / झोप कमी / पाळी", ["Migraine"]),
      O("exertion_sex", "Exertion / during sex", "मेहनत / संभोग के समय", "श्रम / संभोगाच्या वेळी", ["Subarachnoid haemorrhage", "Benign exertional headache"]),
      O("screen_stress", "Stress / long screen work", "तनाव / देर तक स्क्रीन", "ताण / बराच वेळ स्क्रीन", ["Tension-type"]),
      O("wakes_sleep", "Wakes from sleep with it", "दर्द से नींद खुल जाती है", "दुखण्याने झोपेतून जाग येते", ["Cluster headache", "Raised intracranial pressure"])],
  src=HT)
Q("hd_vision", "headache", "redflag", 13, "yesno", "Brief blackouts of vision on standing/bending, or double vision?",
  "क्या खड़े/झुकने पर कुछ सेकंड के लिए आँखों के आगे अँधेरा, या दोहरा दिखना?", "उभे/वाकल्यावर काही सेकंद डोळ्यांसमोर अंधारी, किंवा दोन-दोन दिसणे?",
  term="Visual obscurations / diplopia", rf="Possible raised intracranial pressure (check fundus)", ddx=["Raised intracranial pressure", "Idiopathic intracranial hypertension"], src=f"{NS}, p311")
Q("hd_special", "headache", "redflag", 14, "multi", "Special situations", "इनमें से कुछ?", "यापैकी काही?", term="High-risk context", opts=[
    O("pregnant_post", "Pregnant / recently delivered", "गर्भवती / हाल में डिलीवरी", "गर्भवती / अलीकडे प्रसूती", ["Pre-eclampsia", "Cerebral venous thrombosis"]),
    O("immuno", "HIV / cancer / steroids", "एचआईवी / कैंसर / स्टेरॉयड", "एचआयव्ही / कर्करोग / स्टिरॉइड", ["Intracranial lesion", "Meningitis"]),
    O("head_injury", "After head injury", "सिर की चोट के बाद", "डोक्याला इजा झाल्यानंतर", ["Subdural haematoma"]),
    O("blood_thinner", "On blood thinners", "खून पतला करने की दवा", "रक्त पातळ करण्याचे औषध", ["Intracranial haemorrhage"])],
  src=f"{NS}, p310-311")

# ---------------------------------------------------------------- WEAKNESS / PARALYSIS
WK = f"{NS}, p309-310"
Q("wk_onset", "weakness", "hopi", 1, "choice", "How did the weakness come?", "कमज़ोरी कैसे आई?", "अशक्तपणा कसा आला?", term="Time course", opts=[
    O("seconds_minutes", "Suddenly, within seconds/minutes", "अचानक, कुछ सेकंड/मिनट में", "अचानक, काही सेकंद/मिनिटांत", ["Stroke / TIA"]),
    O("hours_days", "Over hours to days", "कुछ घंटों से दिनों में", "काही तासांपासून दिवसांत", ["Guillain-Barré syndrome", "Demyelination (MS)", "Spinal cord compression", "Hypokalaemic paralysis"]),
    O("weeks_months", "Slowly over weeks/months", "हफ़्तों/महीनों में धीरे-धीरे", "आठवडे/महिन्यांत हळूहळू", ["Intracranial lesion", "Spinal cord compression", "Motor neurone disease", "Myopathy"]),
    O("comes_goes", "Comes and goes / worse by evening", "आती-जाती है / शाम तक बढ़ती", "येते-जाते / संध्याकाळपर्यंत वाढते", ["Myasthenia gravis", "TIA"])],
  src=TIME)
Q("wk_time_last_well", "weakness", "redflag", 2, "text", "Exact time last seen normal (for stroke treatment)", "मरीज़ आख़िरी बार कब बिल्कुल ठीक था (सही समय)?",
  "रुग्ण शेवटचा केव्हा पूर्ण बरा होता (नेमकी वेळ)?", term="Last known well", show={"q": "wk_onset", "in": ["seconds_minutes"]}, src=f"{NS}, p309")
Q("wk_stroke_now", "weakness", "redflag", 3, "yesno", "Started within the last 24 hours?", "क्या पिछले 24 घंटे के अंदर शुरू हुई?", "मागील 24 तासांत सुरू झाला का?",
  term="Acute onset <24 h", rf="Acute stroke — EMERGENCY, note time, CT brain now", ddx=["Stroke / TIA"], show={"q": "wk_onset", "in": ["seconds_minutes"]}, src=f"{NS}, p309")
Q("wk_where", "weakness", "hopi", 4, "choice", "Which part is weak?", "कहाँ कमज़ोरी है?", "कुठे अशक्तपणा आहे?", term="Distribution", opts=[
    O("one_side", "One side of body (arm + leg ± face)", "शरीर का एक हिस्सा (हाथ + पैर ± चेहरा)", "शरीराची एक बाजू (हात + पाय ± चेहरा)", ["Stroke / TIA", "Intracranial lesion"]),
    O("both_legs", "Both legs", "दोनों पैर", "दोन्ही पाय", ["Spinal cord compression", "Guillain-Barré syndrome", "Spinal TB"]),
    O("all_four", "All four limbs", "चारों हाथ-पैर", "चारही हात-पाय", ["Guillain-Barré syndrome", "Hypokalaemic paralysis", "Cervical cord compression", "Myopathy"]),
    O("face_only", "Face only (one side)", "सिर्फ़ चेहरा (एक तरफ)", "फक्त चेहरा (एका बाजूला)", ["Bell's palsy", "Stroke / TIA"]),
    O("one_limb", "One arm or one leg / foot drop", "एक हाथ या एक पैर / पैर लटकना", "एक हात किंवा एक पाय / पाऊल लोंबणे", ["Peripheral nerve lesion", "Radiculopathy", "Stroke / TIA"]),
    O("shoulders_hips", "Difficulty rising from chair / lifting arms", "कुर्सी से उठना / हाथ ऊपर करना मुश्किल", "खुर्चीतून उठणे / हात वर करणे कठीण", ["Myopathy", "Hypothyroidism"])],
  src=f"{NS}, p310, p330 (Box 16.3)")
Q("wk_face_forehead", "weakness", "hopi", 5, "yesno", "Can't close the eye or wrinkle the forehead on that side?", "क्या उस तरफ आँख बंद नहीं होती या माथे पर सिलवट नहीं पड़ती?",
  "त्या बाजूचा डोळा मिटत नाही किंवा कपाळावर आठी पडत नाही का?", term="Forehead involvement (LMN facial)", pos="Favours Bell's palsy (LMN)",
  neg="Forehead spared suggests UMN (stroke)", ddx=["Bell's palsy"], show={"q": "wk_where", "in": ["face_only"]}, src=f"{NS}, p320")
Q("wk_ascending", "weakness", "redflag", 6, "yesno", "Weakness started in the feet and is climbing up, or breathing/swallowing getting weak?",
  "क्या कमज़ोरी पैरों से शुरू होकर ऊपर बढ़ रही है, या साँस/निगलना कमज़ोर हो रहा है?", "अशक्तपणा पायांपासून सुरू होऊन वर चढतो आहे का, किंवा श्वास/गिळणे कमजोर होत आहे का?",
  term="Ascending weakness / bulbar-respiratory involvement", rf="Possible GBS with respiratory risk — urgent", ddx=["Guillain-Barré syndrome"], src=f"{NS}, p310")
Q("wk_bladder", "weakness", "redflag", 7, "yesno", "Can't pass urine / leaking urine or stool, or numb below a level (band on body)?",
  "क्या पेशाब नहीं हो रहा / अपने आप निकल रहा, या शरीर पर एक लकीर के नीचे सुन्नपन?", "लघवी होत नाही / आपोआप होते, किंवा शरीरावर एका रेषेखाली बधिरपणा?",
  term="Sphincter disturbance / sensory level", rf="Possible spinal cord compression — EMERGENCY MRI", ddx=["Spinal cord compression", "Transverse myelitis"],
  key="cord_signs", src=f"{NS}, p310")
Q("wk_assoc", "weakness", "associated", 8, "multi", "Along with weakness", "कमज़ोरी के साथ", "अशक्तपणासोबत", term="Associated deficits", opts=[
    O("speech", "Speech slurred / can't find words", "बोली लड़खड़ाई / शब्द नहीं मिलते", "बोलणे अडखळते / शब्द सापडत नाहीत", ["Stroke / TIA"]),
    O("swallow", "Choking on food / water", "खाना / पानी में ठसका", "अन्न / पाण्यात ठसका", ["Stroke / TIA", "Guillain-Barré syndrome", "Myasthenia gravis"]),
    O("vision", "Loss of vision / double vision", "दिखना बंद / दोहरा दिखना", "दिसणे बंद / दोन-दोन दिसणे", ["Stroke / TIA", "Myasthenia gravis", "Demyelination (MS)"]),
    O("droopy_lids", "Drooping eyelids, worse by evening", "पलकें झुकना, शाम तक ज़्यादा", "पापण्या लोंबणे, संध्याकाळी जास्त", ["Myasthenia gravis"]),
    O("headache", "Severe headache / vomiting", "तेज़ सिर दर्द / उल्टी", "तीव्र डोकेदुखी / उलटी", ["Intracranial haemorrhage", "Intracranial lesion"]),
    O("back_pain", "Back pain", "कमर दर्द", "कंबरदुखी", ["Spinal cord compression", "Spinal TB"]),
    O("muscle_pain", "Muscle pain / cramps", "मांसपेशियों में दर्द / ऐंठन", "स्नायूदुखी / पेटके", ["Myopathy", "Hypokalaemic paralysis"]),
    O("numb", "Numbness / tingling", "सुन्नपन / झुनझुनी", "बधिरपणा / मुंग्या", ["Guillain-Barré syndrome", "Peripheral nerve lesion"])],
  src=f"{NS}, p310 (Box 16.1)")
Q("wk_recent_illness", "weakness", "risk", 9, "yesno", "Loose motions / fever / vaccine in the last 4 weeks?", "क्या पिछले 4 हफ़्तों में दस्त / बुखार / टीका?",
  "मागील 4 आठवड्यांत जुलाब / ताप / लस?", term="Antecedent infection", ddx=["Guillain-Barré syndrome"], src="General clinical practice")
Q("wk_snake", "weakness", "redflag", 10, "yesno", "Possible snake bite / insecticide exposure / drooping eyelids after sleeping on the floor?",
  "क्या साँप काटने / कीटनाशक / ज़मीन पर सोने के बाद पलकें झुकना?", "साप चावणे / कीटकनाशक / जमिनीवर झोपल्यानंतर पापण्या लोंबणे?",
  term="Toxin exposure (neuroparalytic)", rf="Possible neurotoxic snake bite / organophosphate — EMERGENCY", ddx=["Snake bite (neurotoxic)", "Organophosphate poisoning"], src="General clinical practice (India)")
Q("wk_risk", "weakness", "risk", 11, "multi", "Stroke risk factors", "इनमें से कुछ है?", "यापैकी काही आहे का?", term="Vascular risk factors", key="cv_risk", opts=[
    O("htn", "High BP", "हाई बीपी", "उच्च रक्तदाब", ["Stroke / TIA"]), O("dm", "Diabetes", "शुगर", "मधुमेह", ["Stroke / TIA"]),
    O("smoke", "Smoking / tobacco", "धूम्रपान / तंबाकू", "धूम्रपान / तंबाखू", ["Stroke / TIA"]),
    O("af", "Irregular heartbeat", "धड़कन अनियमित", "ठोके अनियमित", ["Stroke / TIA"]),
    O("prev_stroke", "Previous stroke / TIA", "पहले लकवा", "आधी पक्षाघात", ["Stroke / TIA"]),
    O("lipids", "High cholesterol", "कोलेस्ट्रॉल ज़्यादा", "कोलेस्टेरॉल जास्त", ["Stroke / TIA"])],
  src=f"{H}, Ch 13, p190")

# ---------------------------------------------------------------- SEIZURES  (Table 16.1)
SZ = f"{NS}, p310 (Table 16.1)"
Q("sz_now_long", "seizure", "redflag", 1, "yesno", "Fit lasting more than 5 minutes, or repeated fits without waking up in between?",
  "क्या दौरा 5 मिनट से ज़्यादा चला, या बीच में होश आए बिना बार-बार दौरे?", "झटके 5 मिनिटांपेक्षा जास्त चालले, किंवा मधे शुद्धी न येता वारंवार झटके?",
  term="Status epilepticus", rf="Status epilepticus — EMERGENCY", ddx=["Status epilepticus"], src=SZ)
Q("sz_first", "seizure", "hopi", 2, "choice", "Has this happened before?", "क्या पहले भी ऐसा हुआ है?", "आधीही असे झाले आहे का?", term="First vs recurrent", opts=[
    O("first", "First time ever", "पहली बार", "पहिल्यांदाच", ["Provoked seizure (metabolic / infection / structural)"]),
    O("known_epilepsy", "Known epilepsy, on medicines", "पुरानी मिर्गी, दवा चल रही", "जुनी आकडी, औषध सुरू", ["Epilepsy"]),
    O("known_stopped", "Known epilepsy, medicines stopped/missed", "मिर्गी है, दवा बंद/छूटी", "आकडी आहे, औषध बंद/चुकले", ["Epilepsy (non-adherence)"])],
  src=SZ)
Q("sz_witness", "seizure", "hopi", 3, "multi", "What did the witness see? (ask the person who saw it)", "देखने वाले ने क्या देखा? (जिसने देखा उससे पूछें)",
  "पाहणाऱ्याने काय पाहिले? (ज्यांनी पाहिले त्यांना विचारा)", term="Witness account", opts=[
      O("stiff_jerk", "Stiffened then jerking of all limbs", "शरीर अकड़ा फिर सभी अंगों में झटके", "शरीर ताठ मग सर्व अवयवांना झटके", ["Epilepsy"]),
      O("one_side_jerk", "Jerking of one side / one limb", "एक तरफ / एक अंग में झटके", "एका बाजूला / एका अवयवाला झटके", ["Focal seizure (structural cause)"]),
      O("eyes_open", "Eyes open, rolled up", "आँखें खुली, ऊपर चढ़ी", "डोळे उघडे, वर फिरलेले", ["Epilepsy"]),
      O("eyes_shut_resist", "Eyes tightly shut, resisted opening, side-to-side movements", "आँखें कसकर बंद, खोलने नहीं दी, इधर-उधर हिलना", "डोळे घट्ट मिटलेले, उघडू दिले नाहीत, इकडे-तिकडे हालचाल", ["Psychogenic non-epileptic attack"]),
      O("tongue", "Bitten side of tongue", "जीभ का किनारा कटा", "जिभेची कडा चावली", ["Epilepsy"]),
      O("urine", "Passed urine", "पेशाब निकल गया", "लघवी झाली", ["Epilepsy"]),
      O("blue", "Turned blue", "नीला पड़ गया", "निळा पडला", ["Epilepsy"]),
      O("staring", "Only staring / lip smacking / fiddling", "सिर्फ़ घूरना / होंठ चबाना / हाथ से कुछ करना", "फक्त टक लावणे / ओठ चघळणे / हाताने चाळा", ["Focal seizure (structural cause)"])],
  src=SZ)
Q("sz_after", "seizure", "hopi", 4, "choice", "After the fit", "दौरे के बाद", "झटक्यांनंतर", term="Post-ictal state", opts=[
    O("confused_sleepy", "Confused / sleepy / headache for a long time", "देर तक उलझन / नींद / सिर दर्द", "बराच वेळ गोंधळ / झोप / डोकेदुखी", ["Epilepsy"]),
    O("quick_clear", "Back to normal within a minute", "एक मिनट में ठीक", "एका मिनिटात सामान्य", ["Vasovagal syncope", "Psychogenic non-epileptic attack"]),
    O("weak_side", "Weak on one side after", "बाद में एक तरफ कमज़ोरी", "नंतर एका बाजूला अशक्तपणा", ["Focal seizure (structural cause)", "Stroke / TIA"])],
  src=SZ)
Q("sz_aura", "seizure", "hopi", 5, "yesno", "Warning before: strange smell/taste, rising stomach feeling, déjà vu?", "क्या पहले चेतावनी: अजीब गंध/स्वाद, पेट से ऊपर उठती अनुभूति, पहले देखा-सा लगना?",
  "आधी पूर्वसूचना: विचित्र वास/चव, पोटातून वर येणारी भावना, आधी पाहिल्यासारखे वाटणे?", term="Aura", ddx=["Focal seizure (structural cause)", "Epilepsy"], src=f"{NS}, p310 (Box 16.1)")
Q("sz_provoked", "seizure", "risk", 6, "multi", "Possible triggers", "इनमें से कुछ?", "यापैकी काही?", term="Provoking factors", opts=[
    O("fever", "Fever / neck stiffness", "बुखार / गर्दन अकड़ना", "ताप / मान ताठ", ["Meningitis / encephalitis", "Febrile seizure (child)"]),
    O("head_injury", "Recent head injury", "हाल में सिर की चोट", "अलीकडे डोक्याला इजा", ["Post-traumatic seizure"]),
    O("alcohol", "Alcohol binge or sudden stop", "ज़्यादा शराब या अचानक छोड़ी", "जास्त दारू किंवा अचानक सोडली", ["Alcohol withdrawal seizure"]),
    O("sleep_loss", "No sleep / stress", "नींद नहीं / तनाव", "झोप नाही / ताण", ["Epilepsy"]),
    O("sugar", "Diabetic on insulin / missed meal", "शुगर में इंसुलिन / खाना छूटा", "मधुमेहात इन्सुलिन / जेवण चुकले", ["Hypoglycaemia"]),
    O("vomit_diarrhoea", "Severe vomiting / loose motions", "तेज़ उल्टी / दस्त", "तीव्र उलटी / जुलाब", ["Electrolyte disturbance"]),
    O("pork_worms", "Pork / undercooked food / worms (neurocysticercosis risk)", "सुअर का मांस / कच्चा खाना / कीड़े", "डुकराचे मांस / कच्चे अन्न / जंत", ["Neurocysticercosis"])],
  src=f"{NS}, p310; General clinical practice (India)")
Q("sz_pregnant", "seizure", "redflag", 7, "yesno", "Pregnant or delivered in last 6 weeks?", "क्या गर्भवती हैं या पिछले 6 हफ़्ते में डिलीवरी हुई?",
  "गर्भवती आहात का किंवा मागील 6 आठवड्यांत प्रसूती झाली?", term="Seizure in pregnancy / postpartum", rf="Fit in pregnancy/postpartum — eclampsia until proven otherwise",
  ddx=["Eclampsia"], key="pregnancy", applies={"sex": "female", "min_age": 14, "max_age": 50}, src=f"{H}, Ch 5 (Women)")
Q("sz_injury", "seizure", "redflag", 8, "yesno", "Head injury or burn during the fit?", "क्या दौरे में सिर पर चोट या जलना?", "झटक्यांत डोक्याला इजा किंवा भाजणे?",
  term="Injury during seizure", rf="Injury during seizure — check head injury", src=f"{H}, Ch 9")
Q("sz_safety", "seizure", "risk", 9, "multi", "Safety (for advice)", "सुरक्षा", "सुरक्षितता", term="Safety-relevant activities", opts=[
    O("drives", "Drives a vehicle", "गाड़ी चलाते हैं", "गाडी चालवतात"),
    O("heights_water", "Works at heights / near water / fire / machines", "ऊँचाई / पानी / आग / मशीन के पास काम", "उंचावर / पाण्याजवळ / आगीजवळ / यंत्रांजवळ काम"),
    O("woman_child_age", "Woman who may become pregnant", "महिला जो गर्भवती हो सकती है", "गर्भवती होऊ शकणारी महिला")],
  src="General clinical practice")

# ---------------------------------------------------------------- DIZZINESS / VERTIGO
DZ = f"{NS}, p310 (Box 16.1); {H}, Ch 21"
Q("dz_type", "dizziness", "hopi", 1, "choice", "What kind of dizziness?", "चक्कर कैसा है?", "चक्कर कसा आहे?", term="Type of dizziness", opts=[
    O("spinning", "Room / self spinning", "कमरा या ख़ुद घूमता लगता है", "खोली किंवा स्वतः फिरत असल्यासारखे", ["BPPV / vestibular", "Vestibular neuritis", "Meniere's disease", "Posterior circulation stroke"]),
    O("faint", "Light-headed, about to faint", "हल्कापन, बेहोशी जैसा", "हलकेपणा, बेशुद्ध होणार असे", ["Postural hypotension", "Cardiac syncope (arrhythmia / aortic stenosis)", "Hypoglycaemia", "Anaemia"]),
    O("unsteady", "Unsteady on feet, legs not balanced", "पैर लड़खड़ाते, संतुलन नहीं", "पाय डगमगतात, तोल जातो", ["Cerebellar disorder", "Peripheral neuropathy", "Posterior circulation stroke"]),
    O("vague", "Vague, head heavy", "अस्पष्ट, सिर भारी", "अस्पष्ट, डोके जड", ["Anxiety / panic", "Drug side effect"])],
  src=DZ)
Q("dz_duration", "dizziness", "hopi", 2, "choice", "How long does the spinning last?", "चक्कर कितनी देर रहता है?", "चक्कर किती वेळ राहतो?", term="Duration of vertigo",
  show={"q": "dz_type", "in": ["spinning"]}, opts=[
      O("seconds_head", "Seconds, on turning head / lying down / getting up", "सेकंड भर, सिर घुमाने / लेटने / उठने पर", "काही सेकंद, डोके वळवताना / झोपताना / उठताना", ["BPPV / vestibular"]),
      O("hours_hearing", "Minutes to hours, with ear fullness / ringing / hearing loss", "मिनटों-घंटों तक, कान भारी / सीटी / कम सुनाई", "मिनिटे-तास, कान जड / आवाज / कमी ऐकू येणे", ["Meniere's disease"]),
      O("days_constant", "Constant for days, started suddenly after cold", "सर्दी के बाद अचानक, दिनों तक लगातार", "सर्दीनंतर अचानक, दिवसभर सतत", ["Vestibular neuritis", "Posterior circulation stroke"])],
  src=DZ)
Q("dz_central", "dizziness", "redflag", 3, "yesno", "With double vision, slurred speech, face/limb numbness or weakness, or can't stand/walk at all?",
  "क्या साथ में दोहरा दिखना, बोली लड़खड़ाना, चेहरे/हाथ-पैर में सुन्नपन या कमज़ोरी, या बिल्कुल खड़े/चल नहीं पा रहे?",
  "सोबत दोन-दोन दिसणे, बोलणे अडखळणे, चेहऱ्यात/हात-पायात बधिरपणा किंवा अशक्तपणा, किंवा अजिबात उभे/चालता येत नाही?",
  term="Central (brainstem/cerebellar) features", rf="Vertigo with neuro signs — posterior circulation stroke?", ddx=["Posterior circulation stroke"], src=DZ)
Q("dz_hearing", "dizziness", "associated", 4, "yesno", "Hearing loss / ringing in one ear?", "क्या एक कान में कम सुनाई / सीटी जैसी आवाज़?", "एका कानात कमी ऐकू येते / आवाज येतो?",
  term="Unilateral hearing loss / tinnitus", ddx=["Meniere's disease", "Acoustic neuroma", "Labyrinthitis"], src=f"{H}, Ch 21")
Q("dz_standing", "dizziness", "hopi", 5, "yesno", "Mainly when standing up quickly?", "क्या ज़्यादातर जल्दी खड़े होने पर?", "मुख्यतः पटकन उभे राहिल्यावर?", term="Orthostatic",
  ddx=["Postural hypotension"], show={"q": "dz_type", "in": ["faint"]}, src=f"{H}, Ch 13, p194")
Q("dz_drugs", "dizziness", "risk", 6, "multi", "Medicines", "इनमें से कोई दवा?", "यापैकी कोणते औषध?", term="Drug causes", opts=[
    O("bp", "BP / water tablets", "बीपी / पेशाब की गोली", "बीपी / लघवीची गोळी", ["Postural hypotension"]),
    O("sleep", "Sleeping / anxiety tablets", "नींद / घबराहट की गोली", "झोपेची / चिंतेची गोळी", ["Drug side effect"]),
    O("fits", "Fits medicines", "मिर्गी की दवा", "आकडीची औषधे", ["Drug side effect"]),
    O("sugar", "Sugar medicines / insulin", "शुगर की दवा / इंसुलिन", "साखरेचे औषध / इन्सुलिन", ["Hypoglycaemia"])],
  src=DZ)
Q("dz_falls", "dizziness", "risk", 7, "yesno", "Has fallen because of it?", "क्या इसकी वजह से गिरे हैं?", "यामुळे पडले आहेत का?", term="Falls", key="falls", src=f"{NS}, p310 (Box 16.1)")

# ---------------------------------------------------------------- NUMBNESS / TINGLING
NB = f"{NS}, p310 (Box 16.1)"
Q("nb_pattern", "numbness", "hopi", 1, "choice", "Where is the numbness?", "सुन्नपन कहाँ है?", "बधिरपणा कुठे आहे?", term="Distribution", opts=[
    O("glove_stocking", "Both feet (± hands), like socks/gloves", "दोनों पैर (± हाथ), मोज़े/दस्ताने जैसा", "दोन्ही पाय (± हात), मोजे/हातमोजे सारखे", ["Peripheral neuropathy (diabetes / B12 / alcohol)"]),
    O("hand_night", "Thumb + first fingers, worse at night", "अंगूठा + पहली उँगलियाँ, रात को ज़्यादा", "अंगठा + पहिली बोटे, रात्री जास्त", ["Carpal tunnel syndrome"]),
    O("one_side_body", "One whole side of body / face", "शरीर / चेहरे का एक पूरा हिस्सा", "शरीर / चेहऱ्याची एक पूर्ण बाजू", ["Stroke / TIA"]),
    O("leg_strip", "Strip down one leg with back pain", "कमर दर्द के साथ एक पैर में पट्टी जैसा", "कंबरदुखीसोबत एका पायात पट्ट्यासारखे", ["Radiculopathy (sciatica)"]),
    O("saddle", "Around anus / genitals / inner thighs", "गुदा / गुप्तांग / जांघ के अंदर", "गुदद्वार / गुप्तांग / आतील मांडी", ["Cauda equina syndrome"]),
    O("patches_skin", "Pale numb skin patches", "त्वचा पर फीके सुन्न धब्बे", "त्वचेवर फिकट बधिर चट्टे", ["Leprosy"]),
    O("around_mouth_hands", "Around mouth + both hands with fast breathing", "मुँह के आसपास + दोनों हाथ, तेज़ साँस के साथ", "तोंडाभोवती + दोन्ही हात, जलद श्वासासोबत", ["Anxiety / panic", "Hypocalcaemia"])],
  src=NB)
Q("nb_cauda", "numbness", "redflag", 2, "yesno", "Saddle numbness with difficulty passing urine/stool or leg weakness?", "क्या गुदा के आसपास सुन्नपन के साथ पेशाब/मल में दिक्कत या पैरों में कमज़ोरी?",
  "गुदद्वाराभोवती बधिरपणासोबत लघवी/शौचाचा त्रास किंवा पायांत अशक्तपणा?", term="Cauda equina", rf="Possible cauda equina — EMERGENCY MRI", ddx=["Cauda equina syndrome"],
  key="cord_signs", src=f"{H}, Ch 15")
Q("nb_feet_ulcer", "numbness", "associated", 3, "yesno", "Painless wounds / burns on feet or hands, or slippers falling off without knowing?",
  "क्या पैरों/हाथों पर बिना दर्द के घाव / जलना, या पता न चलना कि चप्पल गिर गई?", "पायांवर/हातांवर न दुखणाऱ्या जखमा / भाजणे, किंवा चप्पल पडली हे न कळणे?",
  term="Loss of protective sensation", ddx=["Peripheral neuropathy (diabetes / B12 / alcohol)", "Leprosy", "Diabetic foot"], src=NB)
Q("nb_causes", "numbness", "risk", 4, "multi", "Possible causes", "इनमें से कुछ?", "यापैकी काही?", term="Risk factors for neuropathy", opts=[
    O("dm", "Diabetes", "शुगर", "मधुमेह", ["Peripheral neuropathy (diabetes / B12 / alcohol)"]),
    O("alcohol", "Heavy alcohol", "ज़्यादा शराब", "जास्त दारू", ["Peripheral neuropathy (diabetes / B12 / alcohol)"]),
    O("veg_b12", "Strict vegetarian / acidity tablets for years (B12)", "शुद्ध शाकाहारी / सालों से एसिडिटी की गोली (B12)", "पूर्ण शाकाहारी / वर्षानुवर्षे ॲसिडिटीची गोळी (B12)", ["Peripheral neuropathy (diabetes / B12 / alcohol)", "Subacute combined degeneration"]),
    O("att_drugs", "TB medicines / chemotherapy", "टीबी की दवा / कीमोथेरेपी", "टीबीचे औषध / केमोथेरपी", ["Drug-induced neuropathy"]),
    O("kidney_thyroid", "Kidney disease / thyroid", "किडनी / थायराइड", "मूत्रपिंड / थायरॉईड", ["Peripheral neuropathy (diabetes / B12 / alcohol)"]),
    O("leprosy_contact", "Leprosy contact", "कुष्ठ रोगी से संपर्क", "कुष्ठरोग्याशी संपर्क", ["Leprosy"])],
  src=NB)
Q("nb_sudden", "numbness", "redflag", 5, "yesno", "Came on suddenly with face / arm / leg weakness or speech problem?", "क्या अचानक आया, साथ में चेहरा/हाथ/पैर कमज़ोर या बोली की दिक्कत?",
  "अचानक आले, सोबत चेहरा/हात/पाय कमजोर किंवा बोलण्याचा त्रास?", term="Acute focal sensory loss", rf="Possible stroke / TIA", ddx=["Stroke / TIA"], src=TIME)

# ---------------------------------------------------------------- CONFUSION / MEMORY
CF = f"{NS}, p310"
Q("cf_speed", "confusion", "hopi", 1, "choice", "How did it start? (ask family)", "कैसे शुरू हुआ? (परिवार से पूछें)", "कसे सुरू झाले? (कुटुंबाला विचारा)", term="Onset", opts=[
    O("hours_days", "Suddenly, over hours / days", "अचानक, घंटों / दिनों में", "अचानक, तास / दिवसांत", ["Delirium (infection / metabolic / drugs)", "Stroke / TIA", "Meningitis / encephalitis"]),
    O("months_years", "Slowly over months / years", "महीनों / सालों में धीरे-धीरे", "महिने / वर्षांत हळूहळू", ["Dementia", "Hypothyroidism", "B12 deficiency", "Depression"]),
    O("fluctuating", "Good and bad days / worse at night", "कभी ठीक कभी ख़राब / रात को ज़्यादा", "कधी बरे कधी वाईट / रात्री जास्त", ["Delirium (infection / metabolic / drugs)", "Lewy body dementia"])],
  src=f"{CF} (informant history)")
Q("cf_acute_flags", "confusion", "redflag", 2, "yesno", "Sudden confusion with fever, drowsiness, fits, or not eating/drinking?", "क्या अचानक उलझन के साथ बुखार, सुस्ती, दौरा, या खाना-पीना बंद?",
  "अचानक गोंधळासोबत ताप, गुंगी, झटके, किंवा खाणे-पिणे बंद?", term="Acute confusional state", rf="Acute confusion (delirium) — find cause now (sugar, infection, sodium, drugs)",
  ddx=["Delirium (infection / metabolic / drugs)", "Meningitis / encephalitis", "Hypoglycaemia"], src=CF)
Q("cf_features", "confusion", "hopi", 3, "multi", "What has the family noticed?", "परिवार ने क्या देखा?", "कुटुंबाने काय पाहिले?", term="Cognitive / behavioural features", opts=[
    O("recent_memory", "Forgets recent things, repeats questions", "हाल की बातें भूलना, बार-बार वही पूछना", "अलीकडच्या गोष्टी विसरणे, तेच तेच विचारणे", ["Dementia"]),
    O("lost", "Gets lost in familiar places", "जानी-पहचानी जगह पर रास्ता भूलना", "ओळखीच्या ठिकाणी रस्ता विसरणे", ["Dementia"]),
    O("money_tasks", "Can't manage money / cooking / medicines", "पैसे / खाना बनाना / दवा नहीं संभाल पाते", "पैसे / स्वयंपाक / औषधे सांभाळता येत नाहीत", ["Dementia"]),
    O("personality", "Personality / behaviour changed", "स्वभाव / व्यवहार बदला", "स्वभाव / वागणूक बदलली", ["Frontotemporal dementia", "Intracranial lesion"]),
    O("seeing_things", "Seeing things that aren't there", "ऐसी चीज़ें दिखना जो नहीं हैं", "नसलेल्या गोष्टी दिसणे", ["Delirium (infection / metabolic / drugs)", "Lewy body dementia"]),
    O("walking_urine", "Walking slowly with small steps + urine leaking", "छोटे क़दम, धीमा चलना + पेशाब निकलना", "लहान पावले, हळू चालणे + लघवी गळणे", ["Normal pressure hydrocephalus"]),
    O("low_mood", "Low mood, withdrawn", "उदास, अलग-थलग", "उदास, एकलकोंडे", ["Depression"])],
  src=f"{CF}")
Q("cf_causes", "confusion", "risk", 4, "multi", "Possible causes", "इनमें से कुछ?", "यापैकी काही?", term="Reversible causes", opts=[
    O("new_drugs", "New medicines / sleeping pills", "नई दवा / नींद की गोली", "नवीन औषध / झोपेची गोळी", ["Delirium (infection / metabolic / drugs)"]),
    O("alcohol", "Heavy alcohol", "ज़्यादा शराब", "जास्त दारू", ["Wernicke's encephalopathy", "Alcohol withdrawal"]),
    O("head_injury_fall", "Fall / head injury in last weeks", "पिछले हफ़्तों में गिरना / सिर की चोट", "मागील आठवड्यांत पडणे / डोक्याला इजा", ["Subdural haematoma"]),
    O("urine_cough", "Burning urine / cough / fever", "पेशाब में जलन / खाँसी / बुखार", "लघवीची जळजळ / खोकला / ताप", ["Delirium (infection / metabolic / drugs)"]),
    O("constipation_retention", "Constipation / not passing urine", "कब्ज़ / पेशाब रुकना", "बद्धकोष्ठता / लघवी अडकणे", ["Delirium (infection / metabolic / drugs)"]),
    O("thyroid_b12", "Thyroid / vegetarian / B12 low", "थायराइड / शाकाहारी / B12 कम", "थायरॉईड / शाकाहारी / B12 कमी", ["Hypothyroidism", "B12 deficiency"])],
  src=CF)
Q("cf_safety", "confusion", "risk", 5, "multi", "Safety at home", "घर पर सुरक्षा", "घरी सुरक्षितता", term="Safety concerns", opts=[
    O("wanders", "Wanders out of home", "घर से बाहर भटक जाते हैं", "घरातून बाहेर भटकतात"),
    O("gas_fire", "Leaves gas / stove on", "गैस / चूल्हा चालू छोड़ देते", "गॅस / चूल चालू ठेवतात"),
    O("alone", "Lives alone", "अकेले रहते हैं", "एकटे राहतात"),
    O("drives", "Still drives", "अभी भी गाड़ी चलाते हैं", "अजूनही गाडी चालवतात")],
  src="General clinical practice")

# ---------------------------------------------------------------- TREMOR / SLOWNESS  (Box 16.4)
TR = f"{NS}, p338 (Box 16.4-16.5)"
Q("tr_when", "tremor", "hopi", 1, "choice", "When is the shaking most?", "हाथ कब ज़्यादा काँपता है?", "हात कधी जास्त थरथरतो?", term="Type of tremor", opts=[
    O("rest", "At rest (hand on lap), less on using it", "आराम में (गोद में हाथ), काम करते समय कम", "विश्रांतीत (मांडीवर हात), काम करताना कमी", ["Parkinson's disease"]),
    O("holding", "Holding cup / writing / arms out", "कप पकड़ते / लिखते / हाथ आगे करने पर", "कप धरताना / लिहिताना / हात पुढे केल्यावर", ["Essential tremor", "Thyrotoxicosis", "Drug-induced tremor", "Anxiety / panic"]),
    O("reaching", "Worse as hand reaches a target", "किसी चीज़ तक हाथ पहुँचते समय बढ़ता", "एखाद्या वस्तूपर्यंत हात पोहोचताना वाढते", ["Cerebellar disorder"])],
  src=TR)
Q("tr_parkinson", "tremor", "hopi", 2, "multi", "Any of these?", "इनमें से कुछ?", "यापैकी काही?", term="Parkinsonian features", opts=[
    O("slow", "Slow in all movements", "हर काम में धीमापन", "प्रत्येक कामात मंदपणा", ["Parkinson's disease"]),
    O("small_writing", "Handwriting getting small", "लिखावट छोटी होना", "अक्षर लहान होणे", ["Parkinson's disease"]),
    O("shuffle", "Small shuffling steps / falls", "छोटे घिसटते क़दम / गिरना", "लहान घसटत पावले / पडणे", ["Parkinson's disease"]),
    O("face", "Less facial expression / soft voice", "चेहरे पर भाव कम / धीमी आवाज़", "चेहऱ्यावर भाव कमी / हळू आवाज", ["Parkinson's disease"]),
    O("stiff", "Stiffness", "अकड़न", "ताठरपणा", ["Parkinson's disease"])],
  src=TR)
Q("tr_drugs", "tremor", "risk", 3, "multi", "Medicines / substances", "दवाएँ / चीज़ें", "औषधे / पदार्थ", term="Drug-induced causes", opts=[
    O("antipsychotic", "Mental illness / vomiting medicines (haloperidol, metoclopramide)", "मानसिक रोग / उल्टी की दवा (हेलोपेरिडोल, मेटोक्लोप्रामाइड)", "मानसिक आजार / उलटीची औषधे", ["Drug-induced parkinsonism"]),
    O("inhaler_thyroxine", "Asthma inhaler / thyroid tablets", "दमे का इनहेलर / थायराइड की गोली", "दम्याचा इनहेलर / थायरॉईड गोळी", ["Drug-induced tremor"]),
    O("valproate_lithium", "Fits / mood medicines (valproate, lithium)", "मिर्गी / मूड की दवा", "आकडी / मूडची औषधे", ["Drug-induced tremor"]),
    O("alcohol_stop", "Alcohol (shaky in morning, better after a drink)", "शराब (सुबह काँपना, पीने के बाद ठीक)", "दारू (सकाळी थरथर, प्यायल्यावर बरे)", ["Alcohol withdrawal"]),
    O("tea_coffee", "Lots of tea / coffee", "बहुत चाय / कॉफ़ी", "खूप चहा / कॉफी", ["Drug-induced tremor"])],
  src=TR)
Q("tr_family", "tremor", "risk", 4, "yesno", "Others in the family have shaking hands? Better after a little alcohol?", "क्या परिवार में दूसरों के भी हाथ काँपते हैं? थोड़ी शराब से कम होता है?",
  "कुटुंबात इतरांचेही हात थरथरतात का? थोड्या दारूने कमी होते का?", term="Family history / alcohol-responsive", ddx=["Essential tremor"], src="General clinical practice")
Q("tr_thyroid", "tremor", "associated", 5, "yesno", "Weight loss, sweating, palpitations, heat intolerance?", "क्या वज़न घटना, पसीना, धड़कन, गर्मी सहन न होना?",
  "वजन घटणे, घाम, धडधड, उष्णता सहन न होणे?", term="Thyrotoxic features", ddx=["Thyrotoxicosis"], src=f"{H}, Ch 18")
