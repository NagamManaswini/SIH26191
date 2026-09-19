export type Language = "en" | "ml" | "hi" | "ta" | "kn" | "te";

export interface LanguageOption {
  code: Language;
  label: string;
  nativeName: string;
  flag: string;
}

export const LANGUAGES: LanguageOption[] = [
  { code: "en", label: "English", nativeName: "English", flag: "🇬🇧" },
  { code: "ml", label: "Malayalam", nativeName: "മലയാളം", flag: "🇮🇳" },
  { code: "hi", label: "Hindi", nativeName: "हिंदी", flag: "🇮🇳" },
  { code: "ta", label: "Tamil", nativeName: "தமிழ்", flag: "🇮🇳" },
  { code: "kn", label: "Kannada", nativeName: "ಕನ್ನಡ", flag: "🇮🇳" },
  { code: "te", label: "Telugu", nativeName: "తెలుగు", flag: "🇮🇳" },
];

export interface TranslationDictionary {
  hazardBulletin: string;
  wayanadSector: string;
  portalTitle: string;
  portalSubtitle: string;
  sosBtnNormal: string;
  sosBtnSent: string;
  sosAlert: string;
  
  evacuationTitle: string;
  evacuationDesc: string;
  
  shelterTitle: string;
  shelterDesc: string;
  
  mapTitle: string;
  mapDesc: string;
  
  nearestSheltersHeader: string;
  viewAllShelters: string;
  shelterActive: string;
  shelterAvailable: string;
  shelterMaxCap: string;
  navigateRoute: string;
  
  weatherHeader: string;
  extremeRain: string;
  soilIndex: string;
  
  helplineHeader: string;
  ndrfControl: string;
  districtCollectorate: string;
  fireRescue: string;
  
  textSizeLabel: string;
  languageLabel: string;
  currentFontSize: string;
  resetFont: string;
}

export const translations: Record<Language, TranslationDictionary> = {
  en: {
    hazardBulletin: "Live Hazard Bulletin",
    wayanadSector: "Wayanad Sector Red Zone",
    portalTitle: "Citizen Disaster Safety Portal",
    portalSubtitle: "Locate safe shelters, calculate real-time safe evacuation routes, and request emergency NDRF assistance.",
    sosBtnNormal: "SEND INSTANT SOS EMERGENCY SIGNAL",
    sosBtnSent: "SOS SIGNAL DISPATCHED ✓",
    sosAlert: "🚨 EMERGENCY SOS BROADCASTED TO NDRF CONTROL CENTER!\n\nYour Location Coordinates (11.5204° N, 76.1368° E) have been dispatched to nearby emergency response teams.",
    
    evacuationTitle: "Find Safe Evacuation Route",
    evacuationDesc: "Calculates shortest path bypassing red zone landslides & flooded roads directly to nearest shelter.",
    
    shelterTitle: "View Safe Relief Shelters",
    shelterDesc: "Check real-time shelter carrying capacity, available space, water supply & medical facilities.",
    
    mapTitle: "Interactive Hazard Map",
    mapDesc: "Explore live hazard polygons, rain gauges, and satellite GIS layers in real-time.",
    
    nearestSheltersHeader: "Nearest Safe Relief Camps & Shelters",
    viewAllShelters: "View All Shelters →",
    shelterActive: "ACTIVE",
    shelterAvailable: "Available Space",
    shelterMaxCap: "Max Capacity",
    navigateRoute: "Navigate Route",
    
    weatherHeader: "Live Meteorological Weather Status",
    extremeRain: "EXTREME RAIN",
    soilIndex: "Saturated Soil Index: 92%. High landslide probability in Chooralmala and Mundakkai slopes.",
    
    helplineHeader: "Emergency Disaster Helplines",
    ndrfControl: "NDRF Disaster Control Room",
    districtCollectorate: "District Collectorate Helpline",
    fireRescue: "Fire & Rescue Services",
    
    textSizeLabel: "Letter Size",
    languageLabel: "Language",
    currentFontSize: "Font Size",
    resetFont: "Reset",
  },
  ml: {
    hazardBulletin: "തത്സമയ ദുരന്ത അറിയിപ്പ്",
    wayanadSector: "വയനാട് മേഖല റെഡ് സോൺ",
    portalTitle: "പൗരന്മാരുടെ ദുരന്ത സുരക്ഷാ പോർട്ടൽ",
    portalSubtitle: "സുരക്ഷിത ദുരിതാശ്വാസ ക്യാമ്പുകൾ കണ്ടെത്തുക, തത്സമയ ഒഴിപ്പിക്കൽ പാതകൾ കണ്ടെത്തുക, എമർജൻസി NDRF സഹായം അഭ്യർത്ഥിക്കുക.",
    sosBtnNormal: "അടിയന്തര SOS സിഗ്നൽ അയക്കുക",
    sosBtnSent: "SOS സിഗ്നൽ അയച്ചു കഴിഞ്ഞു ✓",
    sosAlert: "🚨 NDRF കൺട്രോൾ സെന്ററിലേക്ക് അടിയന്തര SOS അയച്ചു!\n\nനിങ്ങളുടെ ലൊക്കേഷൻ കോർഡിനേറ്റുകൾ (11.5204° N, 76.1368° E) അടിയന്തര രക്ഷാസേനയ്ക്ക് കൈമാറി.",
    
    evacuationTitle: "സുരക്ഷിത ഒഴിപ്പിക്കൽ പാത കണ്ടെത്തുക",
    evacuationDesc: "ഉരുൾപൊട്ടലും വെള്ളപ്പൊക്കവുമുള്ള റോഡുകൾ ഒഴിവാക്കി അടുത്തുള്ള സുരക്ഷിത ക്യാമ്പിലേക്കുള്ള വഴി നൽകുന്നു.",
    
    shelterTitle: "ദുരിതാശ്വാസ ക്യാമ്പുകൾ കാണുക",
    shelterDesc: "ക്യാമ്പുകളിലെ ലഭ്യമായ സ്ഥലം, കുടിവെള്ളം, വൈദ്യസഹായം എന്നിവ തത്സമയം പരിശോധിക്കുക.",
    
    mapTitle: "തത്സമയ അപകട ഭൂപടം",
    mapDesc: "അപകടമേഖലകൾ, മഴയുടെ അളവ്, സാറ്റലൈറ്റ് ഉപഗ്രഹ വിവരങ്ങൾ തത്സമയം കാണുക.",
    
    nearestSheltersHeader: "അടുത്തുള്ള സുരക്ഷിത ദുരിതാശ്വാസ ക്യാമ്പുകൾ",
    viewAllShelters: "എല്ലാ ക്യാമ്പുകളും കാണുക →",
    shelterActive: "പ്രവർത്തനക്ഷമം",
    shelterAvailable: "ലഭ്യമായ സ്ഥലം",
    shelterMaxCap: "പരമാവധി ശേഷി",
    navigateRoute: "റൂട്ട് കാണിക്കുക",
    
    weatherHeader: "തത്സമയ കാലാവസ്ഥാ വിവരങ്ങൾ",
    extremeRain: "അതിശക്തമായ മഴ",
    soilIndex: "മണ്ണിന്റെ ഈർപ്പ നില: 92%. ചൂരൽമല, മുണ്ടക്കൈ മേഖലകളിൽ ഉരുൾപൊട്ടൽ സാധ്യത വളരെ കൂടുതൽ.",
    
    helplineHeader: "അടിയന്തര സഹായ നമ്പറുകൾ",
    ndrfControl: "NDRF ദുരന്തനിവാരണ കൺട്രോൾ റൂം",
    districtCollectorate: "ജില്ലാ കളക്ടറേറ്റ് ഹെൽപ്പ് ലൈൻ",
    fireRescue: "ഫയർ & റെസ്ക്യൂ സർവീസ്",
    
    textSizeLabel: "അക്ഷര വലിപ്പം",
    languageLabel: "ഭാഷ",
    currentFontSize: "അക്ഷര വലിപ്പം",
    resetFont: "യഥാർത്ഥ വലിപ്പം",
  },
  hi: {
    hazardBulletin: "लाइव आपदा चेतावनी",
    wayanadSector: "वायनाड सेक्टर रेड ज़ोन",
    portalTitle: "नागरिक आपदा सुरक्षा पोर्टल",
    portalSubtitle: "सुरक्षित आश्रय स्थल खोजें, वास्तविक समय की निकासी मार्ग देखें और आपातकालीन NDRF सहायता का अनुरोध करें।",
    sosBtnNormal: "तत्काल SOS आपातकालीन सिग्नल भेजें",
    sosBtnSent: "SOS सिग्नल भेज दिया गया ✓",
    sosAlert: "🚨 NDRF नियंत्रण केंद्र को आपातकालीन SOS भेजा गया!\n\nआपकी स्थान स्थिति (11.5204° N, 76.1368° E) आपातकालीन टीमों को भेज दी गई है।",
    
    evacuationTitle: "सुरक्षित निकासी मार्ग खोजें",
    evacuationDesc: "भूस्खलन और बाढ़ प्रभावित सड़कों को छोड़कर निकटतम आश्रय तक सबसे सुरक्षित मार्ग बताता है।",
    
    shelterTitle: "सुरक्षित राहत शिविर देखें",
    shelterDesc: "राहत शिविरों में उपलब्ध क्षमता, पेयजल, भोजन और चिकित्सा सुविधाओं की वास्तविक स्थिति जांचें।",
    
    mapTitle: "इंटरएक्टिव आपदा मानचित्र",
    mapDesc: "आपदा प्रभावित क्षेत्रों, वर्षा मापक डेटा और उपग्रह जीआईएस परतों को वास्तविक समय में देखें।",
    
    nearestSheltersHeader: "निकटतम सुरक्षित राहत शिविर और आश्रय स्थल",
    viewAllShelters: "सभी आश्रय स्थल देखें →",
    shelterActive: "सक्रिय",
    shelterAvailable: "उपलब्ध स्थान",
    shelterMaxCap: "कुल क्षमता",
    navigateRoute: "मार्ग दिखाएं",
    
    weatherHeader: "लाइव मौसम स्थिति",
    extremeRain: "अत्यधिक भारी बारिश",
    soilIndex: "मृदा संतृप्ति सूचकांक: 92%। चूरलमला और मुंडक्कई ढलानों में भूस्खलन की अत्यधिक संभावना।",
    
    helplineHeader: "आपातकालीन हेल्पलाइन नंबर",
    ndrfControl: "NDRF आपदा नियंत्रण कक्ष",
    districtCollectorate: "जिला कलेक्टर हेल्पलाइन",
    fireRescue: "अग्निशमन एवं बचाव सेवा",
    
    textSizeLabel: "अक्षर आकार",
    languageLabel: "भाषा",
    currentFontSize: "फ़ॉन्ट आकार",
    resetFont: "रीसेट",
  },
  ta: {
    hazardBulletin: "நேரலை ஆபத்து அறிவிப்பு",
    wayanadSector: "வயநாடு மண்டலம் சிவப்பு மண்டலம்",
    portalTitle: "குடிமக்கள் பேரிடர் பாதுகாப்பு போர்டல்",
    portalSubtitle: "பாதுகாப்பான முகாம்களைக் கண்டறிந்து, நேரலை வெளியேற்ற வழிகளைக் கணக்கிட்டு, NDRF அவசர உதவியைப் பெறவும்.",
    sosBtnNormal: "உடனடி SOS அவசர சிக்னல் அனுப்புக",
    sosBtnSent: "SOS சிக்னல் அனுப்பப்பட்டது ✓",
    sosAlert: "🚨 NDRF கட்டுப்பாட்டு மையத்திற்கு அவசர SOS அனுப்பப்பட்டது!\n\nஉங்கள் இருப்பிட அச்சுக்கோடுகள் அவசர மீட்புக் குழுக்களுக்கு அனுப்பப்பட்டுள்ளன.",
    
    evacuationTitle: "பாதுகாப்பான வெளியேற்ற வழியைக் கண்டறியவும்",
    evacuationDesc: "நிலச்சரிவு மற்றும் வெள்ளப் பகுதிகளைத் தவிர்த்து அருகிலுள்ள முகாமிற்குச் செல்லும் குறுகிய வழி.",
    
    shelterTitle: "பாதுகாப்பான நிவாரண முகாம்களைப் பார்க்கவும்",
    shelterDesc: "முகாம்களில் உள்ள இடைவெளி, குடிநீர் மற்றும் மருத்துவ வசதிகளின் நேரலை நிலையைச் சரிபார்க்கவும்.",
    
    mapTitle: "நேரலை ஆபத்து வரைபடம்",
    mapDesc: "ஆபத்து பகுதிகள், மழை அளவு மற்றும் செயற்கைக்கோள் தரவுகளை நேரலையில் பார்க்கவும்.",
    
    nearestSheltersHeader: "அருகிலுள்ள பாதுகாப்பான நிவாரண முகாம்கள்",
    viewAllShelters: "அனைத்து முகாம்களையும் பார்க்கவும் →",
    shelterActive: "செயலில் உள்ளது",
    shelterAvailable: "கிடைக்கும் இடம்",
    shelterMaxCap: "அதிகபட்ச திறன்",
    navigateRoute: "வழி காட்டுக",
    
    weatherHeader: "நேரலை வானிலை நிலை",
    extremeRain: "கடும் மழை எச்சரிக்கை",
    soilIndex: "மண் ஈரப்பத குறியீடு: 92%. சூரல்மலை மற்றும் முண்டக்கை சாய்வுகளில் நிலச்சரிவு அபாயம் அதிகம்.",
    
    helplineHeader: "அவசர உதவி எண்கள்",
    ndrfControl: "NDRF பேரிடர் கட்டுப்பாட்டு அறை",
    districtCollectorate: "மாவட்ட ஆட்சியர் உதவி எண்",
    fireRescue: "தீயணைப்பு மற்றும் மீட்பு சேவை",
    
    textSizeLabel: "எழுத்து அளவு",
    languageLabel: "மொழி",
    currentFontSize: "எழுத்து அளவு",
    resetFont: "மீட்டமை",
  },
  kn: {
    hazardBulletin: "ನೇರ ಲೈವ್ ವಿಪತ್ತು ಸೂಚನೆ",
    wayanadSector: "ವಯನಾಡ್ ವಲಯ ರೆಡ್ ಝೋನ್",
    portalTitle: "ನಾಗರಿಕರ ವಿಪತ್ತು ಸುರಕ್ಷತಾ ಪೋರ್ಟಲ್",
    portalSubtitle: "ಸುರಕ್ಷಿತ ಸಂತ್ರಸ್ತ ಶಿಬಿರಗಳನ್ನು ಹುಡುಕಿ, ನೈಜ ಸಮಯದ ಸ್ಥಳಾಂತರ ಮಾರ್ಗಗಳನ್ನು ತಿಳಿಯಿರಿ ಮತ್ತು ತುರ್ತು NDRF ನೆರವು ಪಡೆಯಿರಿ.",
    sosBtnNormal: "ತಕ್ಷಣದ SOS ತುರ್ತು ಸಿಗ್ನಲ್ ಕಳುಹಿಸಿ",
    sosBtnSent: "SOS ಸಿಗ್ನಲ್ ಕಳುಹಿಸಲಾಗಿದೆ ✓",
    sosAlert: "🚨 NDRF ನಿಯಂತ್ರಣ ಕೊಠಡಿಗೆ ತುರ್ತು SOS ಕಳುಹಿಸಲಾಗಿದೆ!\n\nನಿಮ್ಮ ಸ್ಥಳ ವಿವರಗಳನ್ನು (11.5204° N, 76.1368° E) ತುರ್ತು ರಕ್ಷಣಾ ತಂಡಗಳಿಗೆ ಕಳುಹಿಸಲಾಗಿದೆ.",
    
    evacuationTitle: "ಸುರಕ್ಷಿತ ಸ್ಥಳಾಂತರ ಮಾರ್ಗ ಹುಡುಕಿ",
    evacuationDesc: "ಕುಸಿತ ಮತ್ತು ಪ್ರವಾಹ ಪೀಡಿತ ರಸ್ತೆಗಳನ್ನು ಹೊರತುಪಡಿಸಿ ಹತ್ತಿರದ ಸುರಕ್ಷಿತ ಶಿಬಿರಕ್ಕೆ ಮಾರ್ಗ ಒದಗಿಸುತ್ತದೆ.",
    
    shelterTitle: "ಸುರಕ್ಷಿತ ಪರಿಹಾರ ಶಿಬಿರಗಳನ್ನು ವೀಕ್ಷಿಸಿ",
    shelterDesc: "ಶಿಬಿರಗಳಲ್ಲಿ ಲಭ್ಯವಿರುವ ಜಾಗ, ಕುಡಿಯುವ ನೀರು ಮತ್ತು ವೈದ್ಯಕೀಯ ಸೌಲಭ್ಯಗಳನ್ನು ಪರಿಶೀಲಿಸಿ.",
    
    mapTitle: "ಇಂಟರಾಕ್ಟಿವ್ ವಿಪತ್ತು ನಕ್ಷೆ",
    mapDesc: "ವಿಪತ್ತು ಪ್ರದೇಶಗಳು, ಮಳೆ ಪ್ರಮಾಣ ಮತ್ತು ಸ್ಯಾಟಲೈಟ್ ಮಾಹಿತಿಯನ್ನು ನೈಜ ಸಮಯದಲ್ಲಿ ವೀಕ್ಷಿಸಿ.",
    
    nearestSheltersHeader: "ಹತ್ತಿರದ ಸುರಕ್ಷಿತ ಪರಿಹಾರ ಶಿಬಿರಗಳು",
    viewAllShelters: "ಎಲ್ಲಾ ಶಿಬಿರಗಳನ್ನು ವೀಕ್ಷಿಸಿ →",
    shelterActive: "ಸಕ್ರಿಯವಾಗಿದೆ",
    shelterAvailable: "ಲಭ್ಯವಿರುವ ಜಾಗ",
    shelterMaxCap: "ಗರಿಷ್ಠ ಸಾಮರ್ಥ್ಯ",
    navigateRoute: "ಮಾರ್ಗ ತೋರಿಸಿ",
    
    weatherHeader: "ಲೈವ್ ಹವಾಮಾನ ಸ್ಥಿತಿ",
    extremeRain: "ಅತ್ಯಂತ ಭಾರೀ ಮಳೆ",
    soilIndex: "ಮಣ್ಣಿನ ತೇವಾಂಶ ಸೂಚ್ಯಂಕ: 92%. ಚೂರಲ್ಮಲಾ ಮತ್ತು ಮುಂಡಕ್ಕೈ ಪ್ರದೇಶಗಳಲ್ಲಿ ಭೂಕುಸಿತದ ಸಾಧ್ಯತೆ ಹೆಚ್ಚಾಗಿದೆ.",
    
    helplineHeader: "ತುರ್ತು ಸಹಾಯವಾಣಿ ಸಂಖ್ಯೆಗಳು",
    ndrfControl: "NDRF ವಿಪತ್ತು ನಿಯಂತ್ರಣ ಕೊಠಡಿ",
    districtCollectorate: "ಜಿಲ್ಲಾಧಿಕಾರಿಗಳ ಸಹಾಯವಾಣಿ",
    fireRescue: "ಅಗ್ನಿಶಾಮಕ ಮತ್ತು ರಕ್ಷಣಾ ಸೇವೆ",
    
    textSizeLabel: "ಅಕ್ಷರ ಗಾತ್ರ",
    languageLabel: "ಭಾಷೆ",
    currentFontSize: "ಫಾಂಟ್ ಗಾತ್ರ",
    resetFont: "ಮರುಹೊಂದಿಸಿ",
  },
  te: {
    hazardBulletin: "ప్రత్యక్ష ప్రమాద సమాచారం",
    wayanadSector: "వాయనాడ్ సెక్టార్ రెడ్ జోన్",
    portalTitle: "పౌరుల విపత్తు భద్రతా పోర్టల్",
    portalSubtitle: "సురక్షిత సహాయ శిబిరాలను కనుగొనండి, నిజసమయ సురక్షిత తరలింపు మార్గాలను గుర్తించండి మరియు అత్యవసర NDRF సహాయం పొందండి.",
    sosBtnNormal: "తక్షణ SOS అత్యవసర సిగ్నల్ పంపండి",
    sosBtnSent: "SOS సిగ్నల్ పంపబడింది ✓",
    sosAlert: "🚨 NDRF కంట్రోల్ సెంటర్‌కు అత్యవసర SOS పంపబడింది!\n\nమీ లొకేషన్ వివరాలు (11.5204° N, 76.1368° E) అత్యవసర సహాయ బృందాలకు అందించబడ్డాయి.",
    
    evacuationTitle: "సురక్షిత తరలింపు మార్గాన్ని కనుగొనండి",
    evacuationDesc: "వర్షాలు మరియు కొండచరియలు విరిగిపడిన రోడ్లను నివారించి సమీప సురక్షిత శిబిరానికి వేగవంతమైన మార్గాన్ని అందిస్తుంది.",
    
    shelterTitle: "సురక్షిత సహాయ శిబిరాలను చూడండి",
    shelterDesc: "శిబిరాలలో అందుబాటులో ఉన్న స్థలం, తాగునీరు మరియు వైద్య సదుపాయాల నిజసమయ వివరాలను తనిఖీ చేయండి.",
    
    mapTitle: "ఇంటరాక్టివ్ విపత్తు మ్యాప్",
    mapDesc: "ప్రమాదకర ప్రాంతాలు, వర్షపాతం నమోదు డేటా మరియు శాటిలైట్ జిఐఎస్ లేయర్లను నిజసమయంలో చూడండి.",
    
    nearestSheltersHeader: "సమీప సురక్షిత సహాయ శిబిరాలు",
    viewAllShelters: "అన్ని శిబిరాలను చూడండి →",
    shelterActive: "క్రియాశీలకంగా ఉంది",
    shelterAvailable: "లభ్యమయ్యే స్థలం",
    shelterMaxCap: "గరిష్ట సామర్థ్యం",
    navigateRoute: "మార్గం చూపించు",
    
    weatherHeader: "ప్రత్యక్ష వాతావరణ సమాచారం",
    extremeRain: "భారీ వర్షపాతం",
    soilIndex: "నేల తేమ సూచిక: 92%. చూరల్మల మరియు ముండక్కై ప్రాంతాలలో కొండచరియలు విరిగిపడే ప్రమాదం ఉంది.",
    
    helplineHeader: "అత్యవసర విపత్తు హెల్ప్‌లైన్ నంబర్లు",
    ndrfControl: "NDRF విపత్తు కంట్రోల్ రూమ్",
    districtCollectorate: "జిల్లా కలెక్టరేట్ హెల్ప్‌లైన్",
    fireRescue: "ఫైర్ & రెస్క్యూ సర్వీసెస్",
    
    textSizeLabel: "అక్షర పరిమాణం",
    languageLabel: "భాష",
    currentFontSize: "ఫాంట్ పరిమాణం",
    resetFont: "రీసెట్",
  },
};
