const LOCAL_API_URL = "http://127.0.0.1:8000/chat";
const DEPLOYED_API_URL = "https://sahayak-backend-y4fu.onrender.com/chat";
const API_URL =
  window.location.protocol === "file:" ||
  window.location.hostname === "127.0.0.1" ||
  window.location.hostname === "localhost"
    ? LOCAL_API_URL
    : DEPLOYED_API_URL;

const chatForm = document.getElementById("chatForm");
const problemInput = document.getElementById("problemInput");
const chatMessages = document.getElementById("chatMessages");
const sendButton = document.getElementById("sendButton");
const errorBox = document.getElementById("errorBox");
const languageSelect = document.getElementById("languageSelect");
const appTitle = document.getElementById("appTitle");
const statusPill = document.getElementById("statusPill");
const noticeText = document.getElementById("noticeText");
const welcomeText = document.getElementById("welcomeText");
const problemLabel = document.getElementById("problemLabel");
const languageLabel = document.getElementById("languageLabel");

let currentLanguage = "en";
let loadingState = false;
const responseCards = [];

const ui = {
  en: {
    appTitle: "SAHAYAK",
    language: "Language",
    status: "Ready",
    processing: "Processing...",
    notice: "Describe a household or local societal problem in Hindi, Hinglish, or English.",
    welcome: "Hello! I am SAHAYAK. Tell me your problem and I will suggest safe, practical next steps.",
    placeholder: "Example: Mere bathroom ka tap leak ho raha hai...",
    problemLabel: "Describe your problem",
    send: "Send",
    sending: "Sending...",
    emptyError: "Please describe your problem first.",
    backendError: "Unable to connect to the chatbot service right now. Please try again.",
    fallbackError: "Unable to connect to the chatbot service right now. Please try again.",
    safeDiy: "Safe DIY guidance available",
    professional: "Professional or authority support recommended",
    emergency: "Emergency or authority escalation needed",
    identified: "Problem Identified",
    severity: "Severity",
    likelyCause: "Likely Cause",
    immediateAction: "Immediate Action",
    solution: "Step-by-step Solution",
    tools: "Required Tools / Materials",
    estimatedTime: "Estimated Time",
    estimatedCost: "Estimated Cost",
    safety: "Safety Precautions",
    alternative: "Alternative Solution",
    whenNotDiy: "When NOT To DIY",
    authority: "When To Contact A Professional Or Authority",
    prevention: "Prevention Tips",
    followUp: "Follow-up Question",
    helplines: "Helplines",
    category: "Category",
    service: "Service",
    phone: "Phone",
    purpose: "Purpose",
    call: "Call",
    notAvailable: "N/A",
  },
  hi: {
    appTitle: "SAHAYAK",
    language: "भाषा",
    status: "तैयार",
    processing: "प्रक्रिया जारी है...",
    notice: "घरेलू या स्थानीय सामाजिक समस्या हिंदी, हिंग्लिश या अंग्रेज़ी में लिखें।",
    welcome: "नमस्ते! मैं SAHAYAK हूं। अपनी समस्या बताइए, मैं सुरक्षित और व्यावहारिक अगले कदम बताऊंगा।",
    placeholder: "उदाहरण: मेरे बाथरूम का नल लीक हो रहा है...",
    problemLabel: "अपनी समस्या लिखें",
    send: "भेजें",
    sending: "भेजा जा रहा है...",
    emptyError: "कृपया पहले अपनी समस्या लिखें।",
    backendError: "अभी चैटबॉट सेवा से कनेक्ट नहीं हो सका। कृपया फिर कोशिश करें।",
    fallbackError: "अभी चैटबॉट सेवा से कनेक्ट नहीं हो सका। कृपया फिर कोशिश करें।",
    safeDiy: "सुरक्षित घरेलू समाधान उपलब्ध है",
    professional: "विशेषज्ञ या संबंधित अधिकारी की मदद लेना बेहतर है",
    emergency: "आपातकालीन या अधिकारी की मदद ज़रूरी है",
    identified: "समस्या की पहचान",
    severity: "गंभीरता",
    likelyCause: "संभावित कारण",
    immediateAction: "तुरंत क्या करें",
    solution: "चरणबद्ध समाधान",
    tools: "ज़रूरी औज़ार / सामग्री",
    estimatedTime: "अनुमानित समय",
    estimatedCost: "अनुमानित खर्च",
    safety: "सुरक्षा सावधानियां",
    alternative: "वैकल्पिक समाधान",
    whenNotDiy: "खुद कब नहीं करना है",
    authority: "विशेषज्ञ या अधिकारी से कब संपर्क करें",
    prevention: "रोकथाम के सुझाव",
    followUp: "छोटा सवाल",
    helplines: "हेल्पलाइन",
    category: "श्रेणी",
    service: "सेवा",
    phone: "फोन",
    purpose: "उद्देश्य",
    call: "कॉल करें",
    notAvailable: "उपलब्ध नहीं",
  },
};

const severityLabel = {
  en: { LOW: "LOW", MEDIUM: "MEDIUM", CRITICAL: "CRITICAL" },
  hi: { LOW: "निम्न", MEDIUM: "मध्यम", CRITICAL: "गंभीर" },
};

const issueRules = [
  {
    id: "gas",
    severity: "CRITICAL",
    keywords: ["gas", "cylinder", "lpg", "गैस", "सिलेंडर", "बदबू", "smell"],
    identified: { en: "Possible gas/LPG leak or gas smell.", hi: "गैस/एलपीजी लीक या गैस की गंध की आशंका।" },
    likelyCause: { en: ["Loose regulator, damaged pipe, open burner knob, or leaking cylinder valve."], hi: ["ढीला रेगुलेटर, खराब पाइप, खुला बर्नर नॉब या सिलेंडर वाल्व से रिसाव।"] },
    immediateAction: { en: ["Do not use switches, flames, lighters, or appliances.", "Open doors/windows only if safe and leave the area.", "Call the gas agency or fire service immediately."], hi: ["स्विच, आग, लाइटर या उपकरणों का उपयोग न करें।", "अगर सुरक्षित हो तो दरवाज़े/खिड़कियां खोलें और जगह से दूर जाएं।", "गैस एजेंसी या फायर सर्विस को तुरंत कॉल करें।"] },
    solution: { en: ["Do not attempt DIY repair. Wait for trained gas/emergency personnel."], hi: ["खुद मरम्मत न करें। प्रशिक्षित गैस/आपातकालीन कर्मियों का इंतज़ार करें।"] },
    safety: { en: ["Keep children and elderly people away.", "Do not search for the leak with a flame."], hi: ["बच्चों और बुज़ुर्गों को दूर रखें।", "आग लगाकर लीक खोजने की कोशिश न करें।"] },
    authority: { en: "Call the gas agency, fire department, or local emergency number immediately.", hi: "गैस एजेंसी, फायर विभाग या स्थानीय आपातकालीन नंबर पर तुरंत कॉल करें।" },
    whenNotDiy: { en: "Always. Gas leaks are not DIY-safe.", hi: "हमेशा। गैस लीक में घरेलू मरम्मत सुरक्षित नहीं है।" },
    prevention: { en: ["Replace old gas pipes on schedule.", "Close the cylinder knob after use."], hi: ["पुरानी गैस पाइप समय पर बदलें।", "उपयोग के बाद सिलेंडर नॉब बंद करें।"] },
    time: { en: "Immediate action required", hi: "तुरंत कार्रवाई ज़रूरी है" },
    cost: { en: "Depends on emergency/gas service", hi: "आपातकालीन/गैस सेवा पर निर्भर" },
  },
  {
    id: "fire",
    severity: "CRITICAL",
    keywords: ["fire", "smoke", "burning", "आग", "धुआं", "जल"],
    identified: { en: "Fire, smoke, or burning smell risk.", hi: "आग, धुआं या जलने की गंध का जोखिम।" },
    likelyCause: { en: ["Electrical fault, open flame, overheated appliance, gas issue, or burning material."], hi: ["बिजली की खराबी, खुली आग, गर्म उपकरण, गैस समस्या या जलती सामग्री।"] },
    immediateAction: { en: ["Evacuate people first.", "Call fire services immediately.", "Cut power/gas only if it is clearly safe from a distance."], hi: ["सबसे पहले लोगों को बाहर निकालें।", "फायर सर्विस को तुरंत कॉल करें।", "बिजली/गैस केवल तभी बंद करें जब दूरी से सुरक्षित हो।"] },
    solution: { en: ["Do not fight a spreading fire yourself. Use an appropriate extinguisher only for a very small fire and only if your exit is clear."], hi: ["फैलती आग को खुद बुझाने की कोशिश न करें। बहुत छोटी आग में ही सही अग्निशामक का उपयोग करें और निकास रास्ता साफ हो।"] },
    safety: { en: ["Do not use water on electrical or oil fires.", "Stay low if there is smoke and move outside."], hi: ["बिजली या तेल की आग पर पानी न डालें।", "धुआं हो तो नीचे झुककर बाहर जाएं।"] },
    authority: { en: "Call fire services/emergency authority immediately.", hi: "फायर सर्विस/आपातकालीन अधिकारी को तुरंत कॉल करें।" },
    whenNotDiy: { en: "Do not DIY if fire is spreading, smoke is heavy, or gas/electricity is involved.", hi: "आग फैल रही हो, धुआं ज़्यादा हो या गैस/बिजली शामिल हो तो खुद न करें।" },
    time: { en: "Immediate action required", hi: "तुरंत कार्रवाई ज़रूरी है" },
  },
  {
    id: "electrical",
    severity: "MEDIUM",
    keywords: ["switch", "socket", "wire", "wiring", "electric", "shock", "spark", "बिजली", "तार", "स्विच", "सॉकेट", "करंट", "चिंगारी"],
    identified: { en: "Electrical switch, socket, or wiring problem.", hi: "बिजली के स्विच, सॉकेट या वायरिंग की समस्या।" },
    likelyCause: { en: ["Loose wiring, damaged switch, overload, moisture, or worn insulation."], hi: ["ढीली वायरिंग, खराब स्विच, ओवरलोड, नमी या खराब इंसुलेशन।"] },
    immediateAction: { en: ["Switch off the related power supply if safe.", "Keep the area dry and keep people away."], hi: ["अगर सुरक्षित हो तो संबंधित बिजली सप्लाई बंद करें।", "जगह सूखी रखें और लोगों को दूर रखें।"] },
    solution: { en: ["Do a visual check only.", "Do not open the switchboard or touch exposed wiring.", "Unplug nearby appliances only with dry hands and dry floor."], hi: ["केवल देखकर जांच करें।", "स्विचबोर्ड न खोलें और खुले तार न छुएं।", "हाथ और फर्श सूखे हों तभी पास के उपकरणों का प्लग निकालें।"] },
    tools: { en: ["Torch", "Dry footwear", "Phone camera for documentation"], hi: ["टॉर्च", "सूखे जूते/चप्पल", "दस्तावेज़ के लिए फोन कैमरा"] },
    safety: { en: ["Do not touch switches with wet hands.", "Do not stand in water near electrical points."], hi: ["गीले हाथों से स्विच न छुएं।", "बिजली के पास पानी में खड़े न हों।"] },
    authority: { en: "Call an electrician. Call emergency/electricity board if there is shock, smoke, or sparking.", hi: "इलेक्ट्रिशियन बुलाएं। झटका, धुआं या चिंगारी हो तो आपातकालीन सेवा/बिजली बोर्ड को कॉल करें।" },
    whenNotDiy: { en: "Do not DIY if there is shock, spark, burning smell, exposed wire, or water nearby.", hi: "झटका, चिंगारी, जलने की गंध, खुले तार या पास में पानी हो तो खुद न करें।" },
    prevention: { en: ["Do not overload sockets.", "Keep water leaks away from electrical points.", "Get old wiring inspected."], hi: ["सॉकेट ओवरलोड न करें।", "बिजली के पास पानी की लीकेज न रहने दें।", "पुरानी वायरिंग की जांच करवाएं।"] },
    time: { en: "10-20 minutes for safe basic checks", hi: "सुरक्षित बुनियादी जांच के लिए १०-२० मिनट" },
  },
  {
    id: "flood",
    severity: "CRITICAL",
    keywords: ["flood", "flooding", "water entering", "पानी भर", "बाढ़", "जलभराव"],
    identified: { en: "Flooding or water entering the home/local area.", hi: "घर या स्थानीय क्षेत्र में पानी भरना/बाढ़ जैसी स्थिति।" },
    likelyCause: { en: ["Heavy rain, blocked drainage, overflowing drain, burst pipe, or low-lying area flooding."], hi: ["तेज़ बारिश, बंद ड्रेनेज, ओवरफ्लो नाली, पाइप फटना या निचले क्षेत्र में जलभराव।"] },
    immediateAction: { en: ["Move people, documents, medicines, and essentials to a higher safe place.", "Turn off electricity if safe; do not enter water near electrical points.", "Avoid walking/driving through moving water."], hi: ["लोगों, दस्तावेज़, दवाइयों और ज़रूरी सामान को ऊंची सुरक्षित जगह ले जाएं।", "सुरक्षित हो तो बिजली बंद करें; बिजली के पास पानी में न जाएं।", "बहते पानी में चलने/गाड़ी चलाने से बचें।"] },
    solution: { en: ["Do not try risky repairs during active flooding.", "Use sandbags/temporary barriers only if water level is low and movement is safe.", "Report blocked public drains or severe waterlogging to municipal/emergency authorities."], hi: ["सक्रिय जलभराव में जोखिम भरी मरम्मत न करें।", "पानी कम हो और चलना सुरक्षित हो तभी अस्थायी बैरियर/रेत की बोरी लगाएं।", "सार्वजनिक नाली बंद या गंभीर जलभराव हो तो नगर निकाय/आपातकालीन अधिकारी को रिपोर्ट करें।"] },
    safety: { en: ["Do not touch electrical equipment in standing water.", "Keep children away from floodwater."], hi: ["जमे पानी में बिजली के उपकरण न छुएं।", "बच्चों को बाढ़/गंदे पानी से दूर रखें।"] },
    authority: { en: "Contact municipal disaster helpline, emergency services, or local authority if water is rising or blocking exits.", hi: "पानी बढ़ रहा हो या बाहर निकलने का रास्ता बंद हो तो नगर आपदा हेल्पलाइन, आपातकालीन सेवा या स्थानीय अधिकारी से संपर्क करें।" },
    whenNotDiy: { en: "Do not DIY during rising water, sewage overflow, electrical risk, or structural damage.", hi: "पानी बढ़ रहा हो, सीवेज ओवरफ्लो हो, बिजली का जोखिम हो या ढांचे को नुकसान हो तो खुद न करें।" },
    prevention: { en: ["Keep drains clear before monsoon.", "Store emergency contacts and essentials in a waterproof bag."], hi: ["मानसून से पहले नालियां साफ रखें।", "आपातकालीन संपर्क और ज़रूरी सामान वाटरप्रूफ बैग में रखें।"] },
    time: { en: "Immediate safety action first", hi: "पहले तुरंत सुरक्षा कार्रवाई" },
  },
  {
    id: "plumbing",
    severity: "LOW",
    keywords: ["tap", "faucet", "pipe", "leak", "drip", "नल", "पाइप", "लीक", "टपक"],
    identified: { en: "Water leak from a tap, faucet, or pipe.", hi: "नल, फॉसेट या पाइप से पानी लीक होना।" },
    likelyCause: { en: ["Loose connection, worn washer, damaged cartridge, cracked pipe, or high water pressure."], hi: ["ढीला कनेक्शन, खराब वॉशर, खराब कार्ट्रिज, टूटा पाइप या ज्यादा पानी का दबाव।"] },
    immediateAction: { en: ["Place a bucket/cloth under the leak.", "Close the local water valve if dripping is continuous."], hi: ["लीक के नीचे बाल्टी/कपड़ा रखें।", "पानी लगातार टपक रहा हो तो स्थानीय पानी वाल्व बंद करें।"] },
    solution: { en: ["Find whether water is coming from the spout, handle, joint, or pipe.", "Gently tighten only visible loose joints.", "Clean deposits around the tap.", "If dripping continues, washer/cartridge replacement is likely needed."], hi: ["देखें पानी टोंटी, हैंडल, जोड़ या पाइप से आ रहा है।", "केवल दिख रहे ढीले जोड़ को हल्के से कसें।", "नल के आसपास जमी परत साफ करें।", "टपकना जारी रहे तो वॉशर/कार्ट्रिज बदलना पड़ सकता है।"] },
    tools: { en: ["Cloth", "Bucket", "Adjustable wrench", "Gloves"], hi: ["कपड़ा", "बाल्टी", "एडजस्टेबल रिंच", "दस्ताने"] },
    safety: { en: ["Do not overtighten metal parts.", "Keep the floor dry."], hi: ["धातु के हिस्सों को ज़्यादा न कसें।", "फर्श सूखा रखें।"] },
    alternative: { en: "Temporarily collect dripping water and close the supply valve until a plumber visits.", hi: "प्लंबर आने तक पानी इकट्ठा करें और सप्लाई वाल्व बंद रखें।" },
    authority: { en: "Call a plumber if the leak is inside a wall, pipe is cracked, or water is near electricity.", hi: "लीक दीवार के अंदर हो, पाइप टूटा हो या पानी बिजली के पास हो तो प्लंबर बुलाएं।" },
    whenNotDiy: { en: "Do not DIY if leakage increases, pipe breaks, or electricity is nearby.", hi: "लीक बढ़े, पाइप टूटे या पास में बिजली हो तो खुद न करें।" },
    prevention: { en: ["Do not force tap handles.", "Repair small drips early."], hi: ["नल के हैंडल को ज़ोर से न घुमाएं।", "छोटी टपकन जल्दी ठीक करें।"] },
    time: { en: "15-30 minutes for basic checks", hi: "बुनियादी जांच के लिए १५-३० मिनट" },
    cost: { en: "Rs. 0-300 for basic materials", hi: "बुनियादी सामग्री के लिए ₹०-३००" },
  },
  {
    id: "drain",
    severity: "LOW",
    keywords: ["drain", "sink", "blocked", "blockage", "clog", "jam", "नाली", "सिंक", "जाम"],
    identified: { en: "Blocked or slow drain/sink.", hi: "नाली या सिंक जाम/धीमा होना।" },
    likelyCause: { en: ["Hair, food waste, soap scum, grease, or debris near the drain opening."], hi: ["बाल, खाने का कचरा, साबुन की परत, तेल/ग्रीस या नाली के पास कचरा।"] },
    immediateAction: { en: ["Stop pouring more water if it is backing up.", "Remove visible waste from the drain cover."], hi: ["पानी वापस आ रहा हो तो और पानी डालना रोकें।", "ड्रेन कवर पर दिख रहा कचरा हटाएं।"] },
    solution: { en: ["Wear gloves.", "Remove visible hair/food waste.", "Pour warm water slowly to check flow.", "Use a plunger gently if flow is still slow."], hi: ["दस्ताने पहनें।", "दिख रहे बाल/खाने का कचरा हटाएं।", "धीरे-धीरे गुनगुना पानी डालकर बहाव जांचें।", "बहाव धीमा रहे तो प्लंजर से हल्का दबाव दें।"] },
    tools: { en: ["Gloves", "Bucket", "Old brush", "Plunger", "Warm water"], hi: ["दस्ताने", "बाल्टी", "पुराना ब्रश", "प्लंजर", "गुनगुना पानी"] },
    safety: { en: ["Do not mix chemical cleaners.", "Do not put bare hands into dirty standing water."], hi: ["केमिकल क्लीनर आपस में न मिलाएं।", "गंदे जमा पानी में नंगे हाथ न डालें।"] },
    alternative: { en: "If plunging does not help, stop and let a plumber clear the trap/line.", hi: "प्लंजर से मदद न मिले तो रुकें और प्लंबर से ट्रैप/लाइन साफ करवाएं।" },
    authority: { en: "Contact a plumber or municipal body if multiple drains are blocked or sewage is backing up.", hi: "कई नालियां जाम हों या सीवेज वापस आए तो प्लंबर या नगर निकाय से संपर्क करें।" },
    whenNotDiy: { en: "Do not DIY if sewage, foul smell across the house, or public drain overflow is involved.", hi: "सीवेज, पूरे घर में बदबू या सार्वजनिक नाली ओवरफ्लो हो तो खुद न करें।" },
    prevention: { en: ["Use drain strainers.", "Do not pour oil/grease into sinks.", "Clean drain covers weekly."], hi: ["ड्रेन स्ट्रेनर लगाएं।", "सिंक में तेल/ग्रीस न डालें।", "ड्रेन कवर हर सप्ताह साफ करें।"] },
    time: { en: "20-40 minutes", hi: "२०-४० मिनट" },
    cost: { en: "Rs. 0-500", hi: "₹०-५००" },
  },
  {
    id: "sanitation",
    severity: "MEDIUM",
    keywords: ["garbage", "waste", "sewage", "dirty", "कचरा", "गंदगी", "सीवेज", "सफाई"],
    identified: { en: "Local sanitation, garbage, or sewage concern.", hi: "स्थानीय सफाई, कचरा या सीवेज से जुड़ी समस्या।" },
    likelyCause: { en: ["Missed waste collection, open dumping, blocked public drain, or sewage overflow."], hi: ["कचरा उठान छूटना, खुले में कचरा, सार्वजनिक नाली बंद या सीवेज ओवरफ्लो।"] },
    immediateAction: { en: ["Avoid direct contact.", "Take photos and note the exact location/time.", "Keep children away."], hi: ["सीधे संपर्क से बचें।", "फोटो लें और सही जगह/समय नोट करें।", "बच्चों को दूर रखें।"] },
    solution: { en: ["If it is your household waste, segregate and bag it safely.", "Report public/shared-area issues to municipal sanitation support.", "Share photos/location with the housing society or ward office."], hi: ["अगर यह घरेलू कचरा है तो उसे अलग कर सुरक्षित बैग में रखें।", "सार्वजनिक/साझा जगह की समस्या नगर सफाई विभाग को रिपोर्ट करें।", "फोटो/लोकेशन हाउसिंग सोसाइटी या वार्ड ऑफिस को भेजें।"] },
    tools: { en: ["Gloves", "Mask", "Phone camera", "Location details"], hi: ["दस्ताने", "मास्क", "फोन कैमरा", "लोकेशन जानकारी"] },
    safety: { en: ["Do not handle medical, chemical, or sharp waste yourself."], hi: ["मेडिकल, केमिकल या नुकीला कचरा खुद न संभालें।"] },
    authority: { en: "Contact municipal sanitation department for public/shared waste or sewage overflow.", hi: "सार्वजनिक/साझा कचरा या सीवेज ओवरफ्लो के लिए नगर सफाई विभाग से संपर्क करें।" },
    whenNotDiy: { en: "Do not DIY if hazardous waste, sewage liquid, or public health risk is present.", hi: "खतरनाक कचरा, सीवेज तरल या सार्वजनिक स्वास्थ्य जोखिम हो तो खुद न करें।" },
    prevention: { en: ["Segregate wet/dry waste.", "Use covered bins.", "Report missed collection early."], hi: ["गीला/सूखा कचरा अलग करें।", "ढक्कन वाले डिब्बे इस्तेमाल करें।", "कचरा उठान छूटे तो जल्दी रिपोर्ट करें।"] },
    time: { en: "10-20 minutes to document/report", hi: "दस्तावेज़/रिपोर्ट करने में १०-२० मिनट" },
    cost: { en: "Usually Rs. 0", hi: "आम तौर पर ₹०" },
  },
  {
    id: "structural",
    severity: "MEDIUM",
    keywords: ["crack", "wall", "roof", "collapse", "ceiling", "दरार", "दीवार", "छत", "गिर"],
    identified: { en: "Wall, roof, ceiling, or structural damage concern.", hi: "दीवार, छत या ढांचे के नुकसान की समस्या।" },
    likelyCause: { en: ["Seepage, settlement, old construction, impact damage, or structural weakness."], hi: ["सीलन, जमीन बैठना, पुराना निर्माण, चोट/धक्का या ढांचे की कमजोरी।"] },
    immediateAction: { en: ["Keep people away from the damaged area.", "Remove only light movable items if safe.", "Take photos for assessment."], hi: ["लोगों को क्षतिग्रस्त जगह से दूर रखें।", "सुरक्षित हो तो केवल हल्का सामान हटाएं।", "जांच के लिए फोटो लें।"] },
    solution: { en: ["Do not chip, drill, or patch deep cracks before inspection.", "Mark the crack edges/date to see if it is growing.", "Contact a civil engineer/contractor for deep, wide, or spreading cracks."], hi: ["जांच से पहले गहरी दरार को तोड़ें, ड्रिल करें या पैच न करें।", "दरार बढ़ रही है या नहीं देखने के लिए किनारे/तारीख मार्क करें।", "गहरी, चौड़ी या बढ़ती दरार में सिविल इंजीनियर/कॉन्ट्रैक्टर से संपर्क करें।"] },
    tools: { en: ["Phone camera", "Tape/marker", "Torch"], hi: ["फोन कैमरा", "टेप/मार्कर", "टॉर्च"] },
    safety: { en: ["Do not stand under a sagging ceiling or loose plaster."], hi: ["झुकी छत या ढीले प्लास्टर के नीचे न खड़े हों।"] },
    authority: { en: "Contact building maintenance, landlord, engineer, or local authority if collapse risk exists.", hi: "गिरने का जोखिम हो तो बिल्डिंग मेंटेनेंस, मकान मालिक, इंजीनियर या स्थानीय अधिकारी से संपर्क करें।" },
    whenNotDiy: { en: "Do not DIY if cracks are wide/spreading, ceiling is sagging, or debris is falling.", hi: "दरार चौड़ी/बढ़ती हो, छत झुक रही हो या मलबा गिर रहा हो तो खुद न करें।" },
    prevention: { en: ["Fix seepage early.", "Inspect roofs/walls after heavy rain.", "Avoid overloading weak shelves/walls."], hi: ["सीलन जल्दी ठीक करें।", "तेज़ बारिश के बाद छत/दीवार जांचें।", "कमज़ोर दीवार/शेल्फ पर ज़्यादा भार न डालें।"] },
  },
];

languageSelect.addEventListener("change", () => {
  currentLanguage = languageSelect.value;
  updateLanguage();
});

problemInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    chatForm.requestSubmit();
  }
});

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  if (loadingState) return;

  const problem = problemInput.value.trim();
  if (!problem) {
    showError(t("emptyError"));
    return;
  }

  clearError();
  addUserMessage(problem);
  problemInput.value = "";
  setLoading(true);
  const loadingMessage = addLoadingMessage();

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ problem, language: currentLanguage }),
    });

    if (!response.ok) {
      throw new Error(t("backendError"));
    }

    const data = await response.json();
    loadingMessage.remove();
    addAiResponse(buildDynamicResponse(data));
  } catch (error) {
    loadingMessage.remove();
    showError(t("fallbackError"));
  } finally {
    setLoading(false);
    problemInput.focus();
  }
});

function buildDynamicResponse(apiData) {
  if (hasBackendGuidance(apiData)) {
    return buildBackendResponse(apiData);
  }

  const problem = apiData.problem || "";
  const matches = findMatchingRules(problem);
  if (matches.length === 0) {
    return buildUnknownResponse(problem, apiData.helplines);
  }

  const severity = resolveSeverity(apiData.severity, matches);
  const response = emptyResponse(problem, severity);
  response.helplines = Array.isArray(apiData.helplines) ? apiData.helplines : [];

  matches.forEach((rule) => applyRule(response, rule));
  refineCombinedRisks(response, matches);

  if (needsFollowUp(problem, matches, response.severity)) {
    response.content.en.followUp = buildFollowUp(matches, "en");
    response.content.hi.followUp = buildFollowUp(matches, "hi");
  }

  return response;
}

function hasBackendGuidance(apiData) {
  return Boolean(
    apiData?.understanding ||
      apiData?.solution_info ||
      apiData?.safety_guidance ||
      apiData?.clarification_question ||
      apiData?.helplines?.length
  );
}

function buildBackendResponse(apiData) {
  const problem = apiData.problem || "";

  if (currentLanguage === "hi") {
    const bilingualMatches = findMatchingRules(problem);
    if (bilingualMatches.length > 0) {
      const localizedResponse = emptyResponse(
        problem,
        resolveSeverity(apiData.severity, bilingualMatches),
      );
      localizedResponse.helplines = Array.isArray(apiData.helplines)
        ? apiData.helplines
        : [];
      bilingualMatches.forEach((rule) => applyRule(localizedResponse, rule));
      refineCombinedRisks(localizedResponse, bilingualMatches);
      return localizedResponse;
    }
  }

  const solutionInfo = apiData.solution_info || {};
  const safetyGuidance = apiData.safety_guidance || {};
  const escalation = apiData.escalation || {};
  const content = {
    identified: apiData.understanding?.summary || summarizeProblem(problem, "en"),
    solution: solutionInfo.steps || apiData.solution,
    tools: solutionInfo.tools_materials || apiData.required_tools,
    estimatedTime: solutionInfo.estimated_time || apiData.estimated_time,
    estimatedCost: solutionInfo.estimated_cost || apiData.estimated_cost,
    safety: safetyGuidance.precautions || apiData.safety_precautions,
    whenNotDiy: safetyGuidance.when_to_stop || apiData.when_to_stop,
    authority: escalation.contact || apiData.when_to_contact_authority,
    prevention: apiData.prevention,
    followUp: apiData.clarification_question,
  };

  return {
    problem,
    severity: apiData.severity || "LOW",
    can_solve_myself: Boolean(apiData.can_solve_myself),
    helplines: Array.isArray(apiData.helplines) ? apiData.helplines : [],
    content: {
      en: content,
      hi: content,
    },
  };
}

function findMatchingRules(problem) {
  const normalized = normalize(problem);
  return issueRules.filter((rule) =>
    rule.keywords.some((keyword) => normalized.includes(normalize(keyword)))
  );
}

function resolveSeverity(apiSeverity, matches) {
  const levels = [apiSeverity || "LOW", ...matches.map((rule) => rule.severity)];
  if (levels.includes("CRITICAL")) return "CRITICAL";
  if (levels.includes("MEDIUM")) return "MEDIUM";
  return "LOW";
}

function emptyResponse(problem, severity) {
  return {
    problem,
    severity,
    can_solve_myself: severity === "LOW",
    content: {
      en: { identified: summarizeProblem(problem, "en") },
      hi: { identified: summarizeProblem(problem, "hi") },
    },
  };
}

function buildUnknownResponse(problem, helplines) {
  const response = emptyResponse(problem, "UNKNOWN");
  response.can_solve_myself = false;
  response.helplines = Array.isArray(helplines) ? helplines : [];
  applyUnknownProblemGuidance(response, problem);
  return response;
}

function applyRule(response, rule) {
  ["en", "hi"].forEach((lang) => {
    const content = response.content[lang];
    content.identified = mergeText(content.identified, rule.identified[lang]);
    addItems(content, "likelyCause", rule.likelyCause?.[lang]);
    addItems(content, "immediateAction", rule.immediateAction?.[lang]);
    addItems(content, "solution", rule.solution?.[lang]);
    addItems(content, "tools", rule.tools?.[lang]);
    addItems(content, "safety", rule.safety?.[lang]);
    addItems(content, "prevention", rule.prevention?.[lang]);
    content.estimatedTime = content.estimatedTime || rule.time?.[lang];
    content.estimatedCost = content.estimatedCost || rule.cost?.[lang];
    content.alternative = content.alternative || rule.alternative?.[lang];
    content.whenNotDiy = mergeText(content.whenNotDiy, rule.whenNotDiy?.[lang]);
    content.authority = mergeText(content.authority, rule.authority?.[lang]);
  });
}

function refineCombinedRisks(response, matches) {
  const ids = matches.map((rule) => rule.id);
  if (ids.includes("plumbing") && ids.includes("electrical")) {
    addItems(response.content.en, "immediateAction", ["Treat water near electricity as unsafe until power is off."]);
    addItems(response.content.hi, "immediateAction", ["बिजली के पास पानी को तब तक असुरक्षित मानें जब तक बिजली बंद न हो।"]);
    response.severity = "MEDIUM";
    response.can_solve_myself = false;
  }

  if (response.severity === "CRITICAL") {
    response.can_solve_myself = false;
  }
}

function applyUnknownProblemGuidance(response, problem) {
  response.can_solve_myself = false;
  response.content.en = {
    identified: summarizeProblem(problem, "en"),
    likelyCause: ["More detail is needed to identify the exact cause safely."],
    immediateAction: ["Check the area visually from a safe distance and avoid touching anything risky."],
    solution: ["Share the exact location, visible signs, and whether electricity, gas, water, injury, or public safety is involved."],
    safety: ["Stop immediately if you notice gas smell, sparks, smoke, structural cracks, injury, sewage backup, or fast-spreading damage."],
    whenNotDiy: "Do not DIY when the issue involves electricity, gas, structural damage, sewage, injury, or public safety risk.",
    authority: "Contact a professional or local authority if the issue affects shared infrastructure or safety.",
    prevention: ["Document recurring problems with photos and dates."],
    followUp: "Where exactly is the problem, and what signs can you see right now?",
  };
  response.content.hi = {
    identified: summarizeProblem(problem, "hi"),
    likelyCause: ["सटीक कारण सुरक्षित रूप से पहचानने के लिए थोड़ी और जानकारी चाहिए।"],
    immediateAction: ["सुरक्षित दूरी से देखकर जांचें और जोखिम वाली चीज़ को न छुएं।"],
    solution: ["सही जगह, दिख रहे संकेत और बिजली, गैस, पानी, चोट या सार्वजनिक सुरक्षा शामिल है या नहीं, यह बताएं।"],
    safety: ["गैस की गंध, चिंगारी, धुआं, दरार, चोट, सीवेज बैकअप या तेज़ी से फैलता नुकसान दिखे तो तुरंत रुकें।"],
    whenNotDiy: "बिजली, गैस, ढांचे के नुकसान, सीवेज, चोट या सार्वजनिक सुरक्षा जोखिम में खुद न करें।",
    authority: "समस्या साझा ढांचे या सुरक्षा को प्रभावित करे तो विशेषज्ञ या स्थानीय अधिकारी से संपर्क करें।",
    prevention: ["बार-बार आने वाली समस्या की फोटो और तारीख संभालकर रखें।"],
    followUp: "समस्या ठीक कहां है, और अभी कौन से संकेत दिख रहे हैं?",
  };
}

function needsFollowUp(problem, matches, severity) {
  const wordCount = problem.trim().split(/\s+/).filter(Boolean).length;
  if (wordCount <= 3) return true;
  if (matches.length === 0) return true;
  if (severity !== "LOW" && !hasAny(problem, ["smell", "spark", "water", "leak", "smoke", "बदबू", "चिंगारी", "पानी", "लीक", "धुआं"])) return true;
  return false;
}

function buildFollowUp(matches, lang) {
  const ids = matches.map((rule) => rule.id);
  if (ids.includes("electrical")) {
    return lang === "hi"
      ? "क्या वहां चिंगारी, जलने की गंध, पानी या करंट का झटका भी है?"
      : "Is there any spark, burning smell, water nearby, or electric shock?";
  }
  if (ids.includes("plumbing") || ids.includes("drain")) {
    return lang === "hi"
      ? "लीक/जाम किस जगह है और पानी कितना तेज़ आ रहा या रुक रहा है?"
      : "Where exactly is the leak/blockage, and how fast is the water leaking or backing up?";
  }
  return lang === "hi"
    ? "समस्या ठीक कहां है और अभी कौन से संकेत दिख रहे हैं?"
    : "Where exactly is the problem, and what signs can you see right now?";
}

function hasAny(value, words) {
  const normalized = normalize(value);
  return words.some((word) => normalized.includes(normalize(word)));
}

function summarizeProblem(problem, lang) {
  return lang === "hi" ? `आपके संदेश के आधार पर: ${problem}` : `Based on your message: ${problem}`;
}

function mergeText(current, next) {
  if (!next) return current;
  if (!current) return next;
  if (current.includes(next)) return current;
  return `${current} ${next}`;
}

function addItems(content, key, items) {
  if (!items || items.length === 0) return;
  content[key] = content[key] || [];
  items.forEach((item) => {
    if (!content[key].includes(item)) {
      content[key].push(item);
    }
  });
}

function normalize(value) {
  return String(value || "").toLowerCase().replace(/\s+/g, " ").trim();
}

function addUserMessage(messageText) {
  const message = createMessage("You", "user-message");
  const bubble = message.querySelector(".bubble");
  bubble.dir = "auto";
  bubble.textContent = messageText;
  chatMessages.appendChild(message);
  scrollToBottom();
}

function addAiResponse(data) {
  const message = createMessage("AI", "ai-message");
  const bubble = message.querySelector(".bubble");
  renderAiBubble(bubble, data);
  responseCards.push({ bubble, data });
  chatMessages.appendChild(message);
  scrollToBottom();
}

function addLoadingMessage() {
  const message = createMessage("AI", "ai-message");
  message.setAttribute("aria-label", t("processing"));
  const bubble = message.querySelector(".bubble");
  bubble.innerHTML = `
    <div class="typing" role="status" aria-label="${t("processing")}">
      <span></span><span></span><span></span>
    </div>
  `;
  chatMessages.appendChild(message);
  scrollToBottom();
  return message;
}

function createMessage(label, className) {
  const message = document.createElement("article");
  message.className = `message ${className}`;
  message.innerHTML = `
    <div class="avatar">${label}</div>
    <div class="bubble"></div>
  `;
  return message;
}

function renderAiBubble(bubble, data) {
  bubble.innerHTML = "";
  bubble.appendChild(renderResponseCard(data));
}

function renderResponseCard(data) {
  const content = data.content[currentLanguage];
  const card = document.createElement("div");
  card.className = "response-card";

  card.appendChild(renderTopSection(data));
  appendHelplineSection(card, data.helplines);
  appendTextSection(card, t("identified"), content.identified);
  appendTextSection(card, t("severity"), severityLabel[currentLanguage][data.severity]);
  appendListSection(card, t("likelyCause"), content.likelyCause);
  appendListSection(card, t("immediateAction"), content.immediateAction);
  appendListSection(card, t("solution"), content.solution);
  appendListSection(card, t("tools"), content.tools);
  appendTextSection(card, t("estimatedTime"), content.estimatedTime);
  appendTextSection(card, t("estimatedCost"), content.estimatedCost);
  appendListSection(card, t("safety"), content.safety);
  appendTextSection(card, t("alternative"), content.alternative);
  appendTextSection(card, t("whenNotDiy"), content.whenNotDiy);
  appendTextSection(card, t("authority"), content.authority);
  appendListSection(card, t("prevention"), content.prevention);
  appendTextSection(card, t("followUp"), content.followUp);

  return card;
}

function appendHelplineSection(card, helplines) {
  if (!Array.isArray(helplines) || helplines.length === 0) return;

  const section = document.createElement("section");
  const heading = document.createElement("h2");
  const list = document.createElement("div");

  heading.className = "section-title";
  heading.textContent = t("helplines");

  helplines.forEach((helpline) => {
    const item = document.createElement("article");
    const category = document.createElement("p");
    const name = document.createElement("p");
    const number = document.createElement("p");
    const purpose = document.createElement("p");
    const callLink = document.createElement("a");

    const notAvailable = t("notAvailable");
    category.textContent = `${t("category")}: ${helpline.category || notAvailable}`;
    name.textContent = `${t("service")}: ${helpline.name || notAvailable}`;
    number.textContent = `${t("phone")}: ${helpline.number || notAvailable}`;
    purpose.textContent = `${t("purpose")}: ${helpline.purpose || notAvailable}`;
    callLink.textContent = t("call");
    callLink.href = `tel:${String(helpline.number || "").replace(/[^\d+]/g, "")}`;

    item.append(category, name, number, purpose, callLink);
    list.appendChild(item);
  });

  section.append(heading, list);
  card.appendChild(section);
}

function renderTopSection(data) {
  const wrapper = document.createElement("div");
  wrapper.className = "response-top";

  const badge = document.createElement("span");
  badge.className = `severity-badge severity-${data.severity.toLowerCase()}`;
  badge.textContent = severityLabel[currentLanguage][data.severity] || data.severity;

  const status = document.createElement("strong");
  if (data.severity === "CRITICAL") {
    status.textContent = t("emergency");
  } else {
    status.textContent = data.can_solve_myself ? t("safeDiy") : t("professional");
  }

  wrapper.append(badge, status);
  return wrapper;
}

function appendTextSection(card, title, value) {
  if (!value) return;

  const section = document.createElement("section");
  const heading = document.createElement("h2");
  const paragraph = document.createElement("p");

  heading.className = "section-title";
  heading.textContent = title;
  paragraph.dir = "auto";
  paragraph.textContent = value;

  section.append(heading, paragraph);
  card.appendChild(section);
}

function appendListSection(card, title, items) {
  if (!Array.isArray(items) || items.length === 0) return;

  const section = document.createElement("section");
  const heading = document.createElement("h2");
  const list = document.createElement("ul");

  heading.className = "section-title";
  heading.textContent = title;

  items.forEach((item) => {
    const listItem = document.createElement("li");
    listItem.dir = "auto";
    listItem.textContent = item;
    list.appendChild(listItem);
  });

  section.append(heading, list);
  card.appendChild(section);
}

function setLoading(isLoading) {
  loadingState = isLoading;
  sendButton.disabled = isLoading;
  sendButton.textContent = isLoading ? t("sending") : t("send");
  sendButton.setAttribute("aria-busy", String(isLoading));
  statusPill.textContent = isLoading ? t("processing") : t("status");
  chatForm.setAttribute("aria-busy", String(isLoading));
}

function showError(message) {
  errorBox.textContent = message;
  errorBox.classList.add("visible");
}

function clearError() {
  errorBox.textContent = "";
  errorBox.classList.remove("visible");
}

function scrollToBottom() {
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function updateLanguage() {
  document.documentElement.lang = currentLanguage === "hi" ? "hi" : "en";
  appTitle.textContent = t("appTitle");
  languageLabel.textContent = t("language");
  statusPill.textContent = t("status");
  noticeText.textContent = t("notice");
  welcomeText.textContent = t("welcome");
  problemLabel.textContent = t("problemLabel");
  problemInput.placeholder = t("placeholder");
  sendButton.textContent = loadingState ? t("sending") : t("send");

  responseCards.forEach(({ bubble, data }) => {
    renderAiBubble(bubble, data);
  });
}

function t(key) {
  return ui[currentLanguage][key] || ui.en[key] || key;
}

updateLanguage();
