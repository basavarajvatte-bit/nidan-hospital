# ====================================================================== SYSTEM 6: LOCOMOTOR (bones, joints, muscles, spine)
# Hutchison 24e, Ch 15 (Locomotor system), p273-286; Box 15.1 (GALS), 15.2, 15.3, 15.6, back-pain red flags (p278).
# Executed inside hx_bank.py.

LC = f"{H}, Ch 15"
BRF = f"{LC}, p278 (back pain red flags)"

C("back_pain", "Locomotor", "Back pain", "कमर / पीठ दर्द", "कंबरदुखी / पाठदुखी", "🧍", 61, f"{LC}, p278")
C("neck_pain", "Locomotor", "Neck pain", "गर्दन दर्द", "मानदुखी", "🦒", 62, f"{LC}, p278 (Box 15.2)")
C("injury", "Locomotor", "Injury / fall / possible fracture", "चोट / गिरना / हड्डी टूटना", "इजा / पडणे / हाड मोडणे", "🩹", 63, f"{LC}, p284 (Box 15.9)")
C("muscle_pain", "Locomotor", "Muscle pain / weakness / body ache", "मांसपेशियों में दर्द / कमज़ोरी", "स्नायूदुखी / अशक्तपणा", "💪", 64, f"{LC}, p280 (Box 15.5)")

# ---------------------------------------------------------------- JOINT PAIN refined (GALS + Box 15.3)
JP = f"{LC}, p273-280"
Q("jt_duration", "joint_pain", "hopi", 11, "choice", "How long has it been?", "कब से है?", "कधीपासून आहे?", term="Duration", opts=[
    O("lt6w", "Less than 6 weeks", "6 हफ़्ते से कम", "6 आठवड्यांपेक्षा कमी", ["Viral arthritis (e.g. chikungunya)", "Reactive arthritis", "Gout", "Septic arthritis"]),
    O("gt6w", "More than 6 weeks", "6 हफ़्ते से ज़्यादा", "6 आठवड्यांपेक्षा जास्त", ["Rheumatoid arthritis", "Osteoarthritis", "Spondyloarthritis", "Psoriatic arthritis"])],
  src=JP)
Q("jt_which", "joint_pain", "hopi", 12, "multi", "Which joints?", "कौन-से जोड़?", "कोणते सांधे?", term="Joints involved", opts=[
    O("small_hands", "Small joints of hands / wrists (both sides)", "हाथ / कलाई के छोटे जोड़ (दोनों तरफ)", "हात / मनगटाचे लहान सांधे (दोन्ही बाजू)", ["Rheumatoid arthritis", "SLE", "Viral arthritis (e.g. chikungunya)"]),
    O("finger_tips", "Finger-tip joints", "उँगलियों के सिरे के जोड़", "बोटांच्या टोकाचे सांधे", ["Osteoarthritis", "Psoriatic arthritis"]),
    O("knee", "Knees", "घुटने", "गुडघे", ["Osteoarthritis", "Gout", "Reactive arthritis", "Septic arthritis"]),
    O("hip", "Hips / groin", "कूल्हे / जांघ", "कंबर / जांघ", ["Osteoarthritis", "Avascular necrosis"]),
    O("big_toe_ankle", "Big toe / ankle", "पैर का अंगूठा / टखना", "पायाचा अंगठा / घोटा", ["Gout", "Reactive arthritis"]),
    O("shoulder", "Shoulders", "कंधे", "खांदे", ["Frozen shoulder / rotator cuff", "Polymyalgia rheumatica"]),
    O("heel_lowback", "Heels / low back", "एड़ी / कमर", "टाच / कंबर", ["Spondyloarthritis"])],
  src=f"{LC}, p280 (Box 15.3)")
Q("jt_mechanical", "joint_pain", "hopi", 13, "multi", "Knee / joint mechanics", "जोड़ में", "सांध्यात", term="Mechanical symptoms", opts=[
    O("locking", "Locks / gets stuck", "अटक जाता है / लॉक होता है", "अडकतो / लॉक होतो", ["Meniscal tear / loose body"]),
    O("giving_way", "Gives way", "अचानक साथ छोड़ देता है", "अचानक लटपटतो", ["Ligament injury", "Meniscal tear / loose body"]),
    O("crackling", "Crackling / grinding", "चर-चर आवाज़", "कटकट आवाज", ["Osteoarthritis"]),
    O("deformity", "Shape changed / bent", "आकार बदला / टेढ़ा", "आकार बदलला / वाकडा", ["Osteoarthritis", "Rheumatoid arthritis"])],
  src=f"{LC}, p278")
Q("jt_gals", "joint_pain", "hopi", 14, "multi", "Daily function (GALS screen)", "रोज़ का काम", "रोजचे काम", term="GALS screening questions", opts=[
    O("dressing", "Difficulty dressing", "कपड़े पहनने में दिक्कत", "कपडे घालण्यात अडचण"),
    O("stairs", "Difficulty with stairs / walking", "सीढ़ी / चलने में दिक्कत", "जिना / चालण्यात अडचण"),
    O("squat", "Can't squat / sit on floor / use Indian toilet", "उकड़ूँ / ज़मीन पर / इंडियन टॉयलेट में नहीं बैठ पाते", "उकिडवे / जमिनीवर / भारतीय शौचालयात बसता येत नाही"),
    O("grip", "Weak grip / can't open bottles", "पकड़ कमज़ोर / बोतल नहीं खुलती", "पकड कमजोर / बाटली उघडता येत नाही"),
    O("work", "Can't do work / farm work", "काम / खेती नहीं कर पाते", "काम / शेती करता येत नाही")],
  src=f"{LC}, p274 (Box 15.1 GALS)")
Q("jt_psoriasis", "joint_pain", "associated", 15, "yesno", "Scaly skin patches / nail pits, or psoriasis in family?", "क्या त्वचा पर पपड़ीदार धब्बे / नाखूनों में गड्ढे, या परिवार में सोरायसिस?",
  "त्वचेवर खपल्यांचे चट्टे / नखांत खड्डे, किंवा कुटुंबात सोरायसिस?", term="Psoriasis", ddx=["Psoriatic arthritis"], src=f"{LC}, p286 (Box 15.11)")
Q("jt_gout_hx", "joint_pain", "risk", 16, "multi", "Gout risk", "गठिया (गाउट) के कारण", "गाउटची कारणे", term="Gout risk factors", opts=[
    O("prev_attack", "Similar attack before", "पहले भी ऐसा दौरा", "आधीही असा झटका", ["Gout"]),
    O("uric_acid", "High uric acid", "यूरिक एसिड ज़्यादा", "युरिक ॲसिड जास्त", ["Gout"]),
    O("alcohol_meat", "Alcohol / meat / seafood", "शराब / मांस / सी-फ़ूड", "दारू / मांस / सी-फूड", ["Gout"]),
    O("diuretic", "Water tablets / low-dose aspirin", "पेशाब की गोली / एस्पिरिन", "लघवीची गोळी / ॲस्पिरिन", ["Gout"]),
    O("kidney", "Kidney disease", "किडनी रोग", "मूत्रपिंड आजार", ["Gout"])],
  src=f"{LC}, p280 (Box 15.4)")
Q("jt_steroid_tb", "joint_pain", "risk", 17, "multi", "Other history", "अन्य", "इतर", term="Other relevant history", opts=[
    O("steroid", "Long steroid use / alcohol (hip pain)", "लंबे समय स्टेरॉयड / शराब (कूल्हे का दर्द)", "दीर्घकाळ स्टिरॉइड / दारू (कंबरेचे दुखणे)", ["Avascular necrosis"]),
    O("tb", "TB in past or contact", "पहले टीबी या संपर्क", "आधी टीबी किंवा संपर्क", ["TB arthritis / spine"]),
    O("sore_throat_child", "Sore throat 2–4 weeks before (child/young)", "2–4 हफ़्ते पहले गला ख़राब (बच्चा/जवान)", "2–4 आठवडे आधी घसा खवखव (मूल/तरुण)", ["Rheumatic fever"]),
    O("fh_ra", "Rheumatoid arthritis / psoriasis in family", "परिवार में आर्थराइटिस / सोरायसिस", "कुटुंबात संधिवात / सोरायसिस", ["Rheumatoid arthritis", "Psoriatic arthritis"])],
  src=f"{LC}, p280")

# ---------------------------------------------------------------- BACK PAIN  (p278)
Q("bk_red", "back_pain", "redflag", 1, "multi", "Back-pain red flags", "कमर दर्द के ख़तरे के निशान", "कंबरदुखीची धोक्याची चिन्हे", term="Back pain red flags", opts=[
    O("night_pain", "Pain at night / at rest, not relieved by lying", "रात / आराम में दर्द, लेटने से आराम नहीं", "रात्री / विश्रांतीत दुखणे, झोपल्याने आराम नाही", ["Malignancy (bone)", "Spinal TB"]),
    O("cancer_hx", "History of cancer", "पहले कैंसर", "आधी कर्करोग", ["Malignancy (bone)"]),
    O("unwell", "Fever / weight loss / night sweats", "बुखार / वज़न घटना / रात को पसीना", "ताप / वजन घटणे / रात्री घाम", ["Spinal TB", "Spinal infection", "Malignancy (bone)"]),
    O("thoracic", "Pain in upper/middle back (thoracic)", "पीठ के ऊपर/बीच में दर्द", "पाठीच्या वर/मधे दुखणे", ["Spinal TB", "Malignancy (bone)", "Spondyloarthritis", "Aortic dissection"]),
    O("immuno", "Steroids / HIV / diabetes / IV drugs", "स्टेरॉयड / एचआईवी / शुगर / नस में नशा", "स्टिरॉइड / एचआयव्ही / मधुमेह / नसेतून नशा", ["Spinal infection", "Osteoporotic fracture"]),
    O("trauma", "After fall / injury (or minor fall if old)", "गिरने / चोट के बाद (बुज़ुर्ग में मामूली गिरना भी)", "पडल्यावर / इजेनंतर (वृद्धांत किरकोळ पडणेही)", ["Vertebral fracture", "Osteoporotic fracture"]),
    O("age", "Age <20 or >55 with new back pain", "उम्र 20 से कम या 55 से ज़्यादा, नया दर्द", "वय 20 पेक्षा कमी किंवा 55 पेक्षा जास्त, नवीन दुखणे", ["Malignancy (bone)", "Osteoporotic fracture"])],
  src=BRF)
Q("bk_cauda", "back_pain", "redflag", 2, "yesno", "Numb around anus/genitals, can't pass / control urine or stool, or both legs weak?",
  "क्या गुदा/गुप्तांग के आसपास सुन्नपन, पेशाब/मल रोक या कर नहीं पाते, या दोनों पैर कमज़ोर?",
  "गुदद्वार/गुप्तांगाभोवती बधिरपणा, लघवी/शौच करता किंवा रोखता येत नाही, किंवा दोन्ही पाय कमजोर?",
  term="Cauda equina / cord symptoms", rf="Cauda equina / cord compression — EMERGENCY MRI", ddx=["Cauda equina syndrome", "Spinal cord compression"], key="cord_signs", src=f"{H}, Ch 16, p310")
Q("bk_pattern", "back_pain", "hopi", 3, "choice", "What is the pain like?", "दर्द कैसा है?", "दुखणे कसे आहे?", term="Inflammatory vs mechanical", opts=[
    O("mechanical", "Worse with activity / lifting, better with rest", "काम / वज़न उठाने से बढ़े, आराम से कम", "कामाने / वजन उचलल्याने वाढे, विश्रांतीने कमी", ["Mechanical back pain", "Disc prolapse"]),
    O("inflammatory", "Morning stiffness >30 min, better with exercise, wakes in 2nd half of night", "सुबह 30 मिनट से ज़्यादा अकड़न, कसरत से आराम, रात के दूसरे हिस्से में नींद खुलती", "सकाळी 30 मिनिटांपेक्षा जास्त ताठरपणा, व्यायामाने आराम, उत्तररात्री जाग", ["Spondyloarthritis"]),
    O("constant_night", "Constant, worse at night", "लगातार, रात को ज़्यादा", "सतत, रात्री जास्त", ["Malignancy (bone)", "Spinal TB"])],
  src=f"{LC}, p278")
Q("bk_sciatica", "back_pain", "hopi", 4, "yesno", "Pain shooting down one leg below the knee, with tingling in the foot?",
  "क्या दर्द एक पैर में घुटने के नीचे तक जाता है, पैर में झुनझुनी के साथ?", "दुखणे एका पायात गुडघ्याखाली जाते, पायात मुंग्यांसह?",
  term="Radicular pain (sciatica)", ddx=["Disc prolapse", "Radiculopathy (sciatica)"], src=f"{LC}, p278 (Box 15.2)")
Q("bk_claud", "back_pain", "hopi", 5, "yesno", "Legs heavy / numb on walking, better on sitting or bending forward?", "क्या चलने पर पैर भारी / सुन्न, बैठने या आगे झुकने पर ठीक?",
  "चालताना पाय जड / बधिर, बसल्यावर किंवा पुढे वाकल्यावर बरे?", term="Neurogenic claudication", ddx=["Lumbar canal stenosis"], applies={"min_age": 45}, src=f"{LC}, p278")
Q("bk_foot_drop", "back_pain", "redflag", 6, "yesno", "Weakness of foot / foot slapping or toes catching?", "क्या पैर में कमज़ोरी / पंजा लटकना या उँगलियाँ अटकना?",
  "पायात अशक्तपणा / पाऊल लोंबणे किंवा बोटे अडकणे?", term="Motor deficit (foot drop)", rf="Progressive neurological deficit — urgent spine review", ddx=["Disc prolapse", "Radiculopathy (sciatica)"], src=f"{LC}, p278")
Q("bk_visceral", "back_pain", "associated", 7, "multi", "Could it be from inside the body?", "क्या अंदर के अंग से दर्द हो सकता है?", "आतल्या अवयवामुळे दुखणे असू शकते का?",
  term="Referred / visceral causes", opts=[
      O("urine", "Burning urine / blood in urine / fever", "पेशाब में जलन / खून / बुखार", "लघवीची जळजळ / रक्त / ताप", ["Pyelonephritis", "Renal colic / stone"]),
      O("abdomen", "Belly pain going to back / vomiting", "पीठ की तरफ पेट दर्द / उल्टी", "पाठीकडे पोटदुखी / उलटी", ["Pancreatitis", "Peptic ulcer (posterior)", "Aortic aneurysm"]),
      O("gynae", "(Women) Pain with periods / white discharge", "(महिला) माहवारी के साथ दर्द / सफ़ेद पानी", "(महिला) पाळीसोबत दुखणे / पांढरे पाणी", ["Pelvic inflammatory disease", "Endometriosis"], only={"sex": "female"}),
      O("chest", "Tearing pain to back with sweating", "पसीने के साथ पीठ में फटने जैसा दर्द", "घामासोबत पाठीत फाटल्यासारखे दुखणे", ["Aortic dissection"])],
  src=f"{LC}, p278")
Q("bk_work", "back_pain", "risk", 8, "multi", "Work / life", "काम / रहन-सहन", "काम / जीवनशैली", term="Occupational / psychosocial", opts=[
    O("heavy_lift", "Heavy lifting / farm / construction work", "भारी वज़न / खेती / निर्माण का काम", "जड ओझे / शेती / बांधकाम", ["Mechanical back pain"]),
    O("long_sitting", "Long sitting / driving", "लंबे समय बैठना / गाड़ी चलाना", "बराच वेळ बसणे / गाडी चालवणे", ["Mechanical back pain"]),
    O("low_mood", "Stress / low mood / off work long", "तनाव / उदासी / लंबे समय से काम बंद", "ताण / उदासी / बराच काळ काम बंद", ["Chronic pain (yellow flags)"]),
    O("osteoporosis", "Post-menopause / long steroids (thin bones)", "माहवारी बंद / लंबे स्टेरॉयड (कमज़ोर हड्डी)", "रजोनिवृत्ती / दीर्घ स्टिरॉइड (ठिसूळ हाडे)", ["Osteoporotic fracture"])],
  src=f"{H}, Ch 11, p160 (Box 11.2 yellow flags)")

# ---------------------------------------------------------------- NECK PAIN  (Box 15.2)
NK = f"{LC}, p278 (Box 15.2)"
Q("nk_arm", "neck_pain", "hopi", 1, "yesno", "Pain / tingling going down one arm into fingers?", "क्या दर्द / झुनझुनी एक हाथ से उँगलियों तक जाती है?",
  "दुखणे / मुंग्या एका हातातून बोटांपर्यंत जातात का?", term="Cervical radiculopathy", ddx=["Cervical radiculopathy", "Cervical spondylosis"], src=NK)
Q("nk_myelopathy", "neck_pain", "redflag", 2, "yesno", "Clumsy hands (buttons, writing), unsteady walking, or urine problems?",
  "क्या हाथ अनाड़ी (बटन, लिखना), चलने में लड़खड़ाहट, या पेशाब की दिक्कत?", "हात अनाडी (बटणे, लिहिणे), चालताना डगमग, किंवा लघवीचा त्रास?",
  term="Cervical myelopathy", rf="Possible cervical cord compression — urgent", ddx=["Cervical cord compression"], key="cord_signs", src=f"{H}, Ch 16")
Q("nk_meningism", "neck_pain", "redflag", 3, "yesno", "Neck stiffness with fever, headache or vomiting?", "क्या गर्दन अकड़ने के साथ बुखार, सिर दर्द या उल्टी?",
  "मान ताठ होण्यासोबत ताप, डोकेदुखी किंवा उलटी?", term="Meningism", rf="Possible meningitis", ddx=["Meningitis"], key="meningism", src=f"{H}, Ch 10, p146")
Q("nk_pattern", "neck_pain", "hopi", 4, "choice", "Pattern", "दर्द कैसा है?", "दुखणे कसे आहे?", term="Pattern", opts=[
    O("posture", "After long phone/computer use / bad pillow", "लंबे फ़ोन/कंप्यूटर इस्तेमाल / ख़राब तकिए से", "बराच वेळ फोन/संगणक / चुकीची उशी", ["Mechanical neck pain"]),
    O("sudden_stiff", "Woke up with stiff neck", "सुबह अकड़ी गर्दन के साथ उठे", "सकाळी ताठ मानेसह उठले", ["Acute torticollis"]),
    O("chronic_old", "Long-standing, older age, grinding", "पुराना, ज़्यादा उम्र, चर-चर", "जुने, जास्त वय, कटकट", ["Cervical spondylosis"]),
    O("after_injury", "After accident / fall", "एक्सीडेंट / गिरने के बाद", "अपघात / पडल्यानंतर", ["Cervical spine injury"])],
  src=NK)
Q("nk_injury", "neck_pain", "redflag", 5, "yesno", "Neck pain after accident / fall from height / diving?", "क्या एक्सीडेंट / ऊँचाई से गिरने / पानी में कूदने के बाद गर्दन दर्द?",
  "अपघात / उंचावरून पडणे / पाण्यात सूर मारल्यानंतर मानदुखी?", term="Possible cervical spine injury", rf="Possible neck fracture — immobilise neck, do not move", ddx=["Cervical spine injury"], src=f"{H}, Ch 9")

# ---------------------------------------------------------------- INJURY / FRACTURE  (Box 15.9)
IJ = f"{LC}, p284 (Box 15.9)"
Q("ij_mechanism", "injury", "hopi", 1, "choice", "How did it happen?", "चोट कैसे लगी?", "इजा कशी झाली?", term="Mechanism of injury", opts=[
    O("road", "Road accident", "सड़क दुर्घटना", "रस्ते अपघात", ["Fracture", "Head injury"]),
    O("height", "Fall from height (tree, roof, stairs)", "ऊँचाई से गिरना (पेड़, छत, सीढ़ी)", "उंचावरून पडणे (झाड, छप्पर, जिना)", ["Fracture", "Spinal injury"]),
    O("simple_fall", "Simple fall at home", "घर में साधारण गिरना", "घरात साधे पडणे", ["Osteoporotic fracture", "Sprain"]),
    O("twist", "Twisted ankle / knee while walking / playing", "चलते / खेलते टखना / घुटना मुड़ा", "चालताना / खेळताना घोटा / गुडघा मुरगळला", ["Sprain", "Ligament injury"]),
    O("assault_animal", "Assault / animal attack (cattle, dog)", "मारपीट / जानवर का हमला (बैल, कुत्ता)", "मारहाण / जनावराचा हल्ला (बैल, कुत्रा)", ["Fracture", "Wound"]),
    O("machine", "Machine / work injury", "मशीन / काम पर चोट", "यंत्र / कामावर इजा", ["Fracture", "Crush injury"])],
  src=IJ)
Q("ij_head", "injury", "redflag", 2, "yesno", "Hit head with fainting, vomiting, drowsiness, fits or bleeding from ear/nose?",
  "क्या सिर पर चोट के साथ बेहोशी, उल्टी, सुस्ती, दौरा या कान/नाक से खून?", "डोक्याला इजा होऊन बेशुद्धी, उलटी, गुंगी, झटके किंवा कान/नाकातून रक्त?",
  term="Significant head injury", rf="Head injury with warning signs — CT head, EMERGENCY", ddx=["Head injury"], src=f"{H}, Ch 9")
Q("ij_fracture", "injury", "hopi", 3, "multi", "Signs of broken bone", "हड्डी टूटने के निशान", "हाड मोडल्याची चिन्हे", term="Fracture features", opts=[
    O("cant_bear", "Can't stand / bear weight / use the limb", "खड़े नहीं हो सकते / अंग इस्तेमाल नहीं कर सकते", "उभे राहता येत नाही / अवयव वापरता येत नाही", ["Fracture"]),
    O("deformity", "Limb looks bent / shortened", "अंग टेढ़ा / छोटा दिखता", "अवयव वाकडा / लहान दिसतो", ["Fracture", "Dislocation"]),
    O("crack", "Heard a crack", "कड़क आवाज़ सुनी", "कडकड आवाज ऐकला", ["Fracture"]),
    O("swelling_bruise", "Rapid swelling / bruising", "तुरंत सूजन / नील", "लगेच सूज / काळे-निळे", ["Fracture", "Sprain"]),
    O("point_tender", "Very painful at one bone spot", "हड्डी पर एक जगह बहुत दर्द", "हाडावर एका जागी खूप दुखणे", ["Fracture"])],
  src=IJ)
Q("ij_open_nv", "injury", "redflag", 4, "multi", "Danger signs", "ख़तरे के निशान", "धोक्याची चिन्हे", term="Limb-threatening features", opts=[
    O("open", "Bone visible / wound over the break", "हड्डी दिख रही / टूटी जगह पर घाव", "हाड दिसते / मोडलेल्या जागी जखम", ["Open fracture"]),
    O("cold_numb", "Limb below is cold, pale, numb", "नीचे का अंग ठंडा, पीला, सुन्न", "खालचा अवयव थंड, फिकट, बधिर", ["Vascular injury"]),
    O("pain_tight", "Pain getting worse, very tight swelling (esp. after plaster)", "दर्द बढ़ रहा, बहुत तनी सूजन (ख़ासकर प्लास्टर के बाद)", "दुखणे वाढते, खूप ताणलेली सूज (विशेषतः प्लास्टरनंतर)", ["Compartment syndrome"]),
    O("heavy_bleed", "Heavy bleeding", "बहुत खून बहना", "खूप रक्तस्राव", ["Major haemorrhage"])],
  src=IJ)
Q("ij_bonesetter", "injury", "risk", 5, "yesno", "Already treated by a local bone-setter / tight bandage?", "क्या पहले पहलवान / हड्डी बैठाने वाले से इलाज या कसी पट्टी?",
  "आधी पहिलवान / हाड बसवणाऱ्याकडून उपचार किंवा घट्ट पट्टी?", term="Traditional bone-setter treatment", ddx=["Compartment syndrome", "Malunion"], src="General clinical practice (India)")
Q("ij_tetanus", "injury", "risk", 6, "choice", "Tetanus injection", "टिटनेस का इंजेक्शन", "धनुर्वाताचे इंजेक्शन", term="Tetanus status", opts=[
    O("lt5y", "Within last 5 years", "पिछले 5 साल में", "मागील 5 वर्षांत"), O("gt5y", "More than 5 years ago", "5 साल से पहले", "5 वर्षांपूर्वी"),
    O("never_unknown", "Never / don't know", "कभी नहीं / पता नहीं", "कधीच नाही / माहीत नाही")],
  src="General clinical practice")
Q("ij_osteo", "injury", "risk", 7, "multi", "Bone strength", "हड्डी की मज़बूती", "हाडांची मजबुती", term="Fragility risk", opts=[
    O("old_age", "Age over 60 / previous fracture from small fall", "60 से ज़्यादा उम्र / पहले मामूली गिरने से फ्रैक्चर", "60 पेक्षा जास्त वय / आधी किरकोळ पडण्याने फ्रॅक्चर", ["Osteoporotic fracture"]),
    O("steroid", "Long steroids", "लंबे समय स्टेरॉयड", "दीर्घ स्टिरॉइड", ["Osteoporotic fracture"]),
    O("thinner", "Blood thinners", "खून पतला करने की दवा", "रक्त पातळ करण्याचे औषध", ["Major haemorrhage"]),
    O("fits_falls", "Fall due to fit / fainting / dizziness", "दौरे / बेहोशी / चक्कर से गिरे", "झटके / बेशुद्धी / चक्करमुळे पडले", ["Seizure", "Vasovagal syncope"])],
  src=IJ)

# ---------------------------------------------------------------- MUSCLE PAIN / WEAKNESS  (Box 15.5 PMR)
MP = f"{LC}, p280 (Box 15.5)"
Q("mp_where", "muscle_pain", "hopi", 1, "choice", "Where?", "कहाँ दर्द / कमज़ोरी?", "कुठे दुखणे / अशक्तपणा?", term="Distribution", opts=[
    O("shoulder_hip_old", "Both shoulders & hips, stiff in morning, age over 50", "दोनों कंधे और कूल्हे, सुबह अकड़न, उम्र 50+", "दोन्ही खांदे व कंबर, सकाळी ताठरपणा, वय 50+", ["Polymyalgia rheumatica"]),
    O("all_over_fever", "All over with fever", "पूरे शरीर में बुखार के साथ", "संपूर्ण अंगात तापासोबत", ["Viral fever", "Dengue", "Leptospirosis", "Malaria"]),
    O("proximal_weak", "Weak thighs/upper arms: hard to rise from squat / comb hair", "जांघ/ऊपरी बाँह कमज़ोर: उकड़ूँ से उठना / बाल बनाना मुश्किल", "मांड्या/वरचे हात कमजोर: उकिडव्यातून उठणे / केस विंचरणे कठीण", ["Myopathy", "Hypothyroidism", "Vitamin D deficiency (osteomalacia)"]),
    O("calf_cramps", "Calf cramps at night", "रात को पिंडली में ऐंठन", "रात्री पोटरीत पेटके", ["Electrolyte disturbance", "Peripheral neuropathy (diabetes / B12 / alcohol)"]),
    O("widespread_chronic", "Widespread pain for months, tired, poor sleep", "महीनों से हर जगह दर्द, थकान, नींद ख़राब", "महिन्यांपासून सगळीकडे दुखणे, थकवा, झोप खराब", ["Fibromyalgia", "Depression", "Vitamin D deficiency (osteomalacia)"])],
  src=MP)
Q("mp_dark_urine", "muscle_pain", "redflag", 2, "yesno", "Severe muscle pain with dark cola-coloured urine?", "क्या तेज़ मांसपेशी दर्द के साथ कोला जैसा गहरा पेशाब?",
  "तीव्र स्नायूदुखीसोबत कोलासारखी गडद लघवी?", term="Myoglobinuria", rf="Possible rhabdomyolysis — check CK & kidneys", ddx=["Rhabdomyolysis"], src="General clinical practice")
Q("mp_gca", "muscle_pain", "redflag", 3, "yesno", "With new headache, scalp tenderness, jaw pain on chewing or vision change?", "क्या साथ में नया सिर दर्द, सिर छूने पर दर्द, चबाने पर जबड़ा दर्द या नज़र में बदलाव?",
  "सोबत नवीन डोकेदुखी, डोक्याला स्पर्शाने दुखणे, चावताना जबडा दुखणे किंवा दृष्टीत बदल?", term="Giant cell arteritis features",
  rf="Possible giant cell arteritis — urgent (vision risk)", ddx=["Giant cell arteritis"], show={"q": "mp_where", "in": ["shoulder_hip_old"]}, src=MP)
Q("mp_drugs", "muscle_pain", "risk", 4, "multi", "Medicines / causes", "दवाएँ / कारण", "औषधे / कारणे", term="Drug / metabolic causes", opts=[
    O("statin", "Cholesterol tablets (statins)", "कोलेस्ट्रॉल की गोली (स्टैटिन)", "कोलेस्टेरॉलची गोळी (स्टॅटिन)", ["Statin myopathy"]),
    O("steroid", "Steroids", "स्टेरॉयड", "स्टिरॉइड", ["Steroid myopathy"]),
    O("diuretic", "Water tablets / loose motions (low potassium)", "पेशाब की गोली / दस्त (पोटैशियम कम)", "लघवीची गोळी / जुलाब (पोटॅशियम कमी)", ["Hypokalaemic paralysis", "Electrolyte disturbance"]),
    O("no_sun", "Little sunlight / covered clothing / pregnancy", "धूप कम / ढके कपड़े / गर्भावस्था", "ऊन कमी / झाकलेले कपडे / गर्भावस्था", ["Vitamin D deficiency (osteomalacia)"]),
    O("alcohol", "Heavy alcohol", "ज़्यादा शराब", "जास्त दारू", ["Alcoholic myopathy"])],
  src=MP)
Q("mp_thyroid", "muscle_pain", "associated", 5, "yesno", "Feeling cold, weight gain, constipation, slowness?", "क्या ठंड ज़्यादा लगना, वज़न बढ़ना, कब्ज़, सुस्ती?",
  "थंडी जास्त वाजणे, वजन वाढणे, बद्धकोष्ठता, सुस्ती?", term="Hypothyroid features", ddx=["Hypothyroidism"], src=f"{H}, Ch 18")
Q("mp_skin", "muscle_pain", "associated", 6, "yesno", "Purple rash on eyelids / knuckles with weakness?", "क्या कमज़ोरी के साथ पलकों / उँगलियों के जोड़ों पर बैंगनी दाने?",
  "अशक्तपणासोबत पापण्यांवर / बोटांच्या सांध्यांवर जांभळे पुरळ?", term="Dermatomyositis rash", ddx=["Dermatomyositis"], show={"q": "mp_where", "in": ["proximal_weak"]}, src=f"{LC}, p286")
