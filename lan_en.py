from core import *

vosk_languages = [
    ("None", "Auto"),

    # English
    ("vosk-model-small-en-us-0.15", "English (US - Small)"),
    ("vosk-model-en-us-0.22", "English (US - Large)"),
    ("vosk-model-en-us-0.22-lgraph", "English (US - Dynamic Graph)"),
    ("vosk-model-en-us-0.42-gigaspeech", "English (US - GigaSpeech)"),

    # English Other
    ("vosk-model-en-us-daanzu-20200905", "English (US - Daanzu)"),
    ("vosk-model-en-us-daanzu-20200905-lgraph", "English (US - Daanzu Graph)"),
    ("vosk-model-en-us-librispeech-0.2", "English (US - Librispeech)"),
    ("vosk-model-small-en-us-zamia-0.5", "English (US - Zamia Small)"),
    ("vosk-model-en-us-aspire-0.2", "English (US - Aspire)"),
    ("vosk-model-en-us-0.21", "English (US - Legacy)"),

    # Indian English
    ("vosk-model-en-in-0.5", "English (India - Large)"),
    ("vosk-model-small-en-in-0.4", "English (India - Small)"),

    # Chinese
    ("vosk-model-small-cn-0.22", "Chinese (Small)"),
    ("vosk-model-cn-0.22", "Chinese (Large)"),
    ("vosk-model-cn-kaldi-multicn-0.15", "Chinese (Kaldi Multi)"),

    # Russian
    ("vosk-model-ru-0.42", "Russian (Large)"),
    ("vosk-model-small-ru-0.22", "Russian (Small)"),
    ("vosk-model-ru-0.22", "Russian (Legacy)"),
    ("vosk-model-ru-0.10", "Russian (Old)"),

    # French
    ("vosk-model-small-fr-0.22", "French (Small)"),
    ("vosk-model-fr-0.22", "French (Large)"),
    ("vosk-model-small-fr-pguyot-0.3", "French (Pguyot Small)"),
    ("vosk-model-fr-0.6-linto-2.2.0", "French (Linto)"),

    # German
    ("vosk-model-de-0.21", "German (Large)"),
    ("vosk-model-de-tuda-0.6-900k", "German (TUDA)"),
    ("vosk-model-small-de-zamia-0.3", "German (Zamia Small)"),
    ("vosk-model-small-de-0.15", "German (Small)"),

    # Spanish
    ("vosk-model-small-es-0.42", "Spanish (Small)"),
    ("vosk-model-es-0.42", "Spanish (Large)"),

    # Portuguese
    ("vosk-model-small-pt-0.3", "Portuguese (Small)"),
    ("vosk-model-pt-fb-v0.1.1-20220516_2113", "Portuguese (FalaBrazil)"),

    # Turkish
    ("vosk-model-small-tr-0.3", "Turkish (Small)"),

    # Vietnamese
    ("vosk-model-small-vn-0.4", "Vietnamese (Small)"),
    ("vosk-model-vn-0.4", "Vietnamese (Large)"),

    # Italian
    ("vosk-model-small-it-0.22", "Italian (Small)"),
    ("vosk-model-it-0.22", "Italian (Large)"),

    # Dutch
    ("vosk-model-small-nl-0.22", "Dutch (Small)"),
    ("vosk-model-nl-spraakherkenning-0.6", "Dutch (Medium)"),
    ("vosk-model-nl-spraakherkenning-0.6-lgraph", "Dutch (Graph)"),

    # Arabic
    ("vosk-model-ar-mgb2-0.4", "Arabic (MGB2)"),
    ("vosk-model-ar-0.22-linto-1.1.0", "Arabic (Linto)"),
    ("vosk-model-small-ar-tn-0.1-linto", "Arabic (Tunisian Small)"),
    ("vosk-model-ar-tn-0.1-linto", "Arabic (Tunisian)"),

    # Farsi
    ("vosk-model-fa-0.42", "Farsi (Large)"),
    ("vosk-model-small-fa-0.42", "Farsi (Small)"),
    ("vosk-model-fa-0.5", "Farsi (Legacy)"),
    ("vosk-model-small-fa-0.5", "Farsi (Small Legacy)"),

    # Japanese
    ("vosk-model-small-ja-0.22", "Japanese (Small)"),
    ("vosk-model-ja-0.22", "Japanese (Large)"),

    # Korean
    ("vosk-model-small-ko-0.22", "Korean (Small)"),

    # Hindi
    ("vosk-model-small-hi-0.22", "Hindi (Small)"),
    ("vosk-model-hi-0.22", "Hindi (Large)"),

    # Ukrainian
    ("vosk-model-small-uk-v3-nano", "Ukrainian (Nano)"),
    ("vosk-model-small-uk-v3-small", "Ukrainian (Small)"),
    ("vosk-model-uk-v3", "Ukrainian (Large)"),
    ("vosk-model-uk-v3-lgraph", "Ukrainian (Graph)"),

    # Kazakh
    ("vosk-model-small-kz-0.42", "Kazakh (Small)"),
    ("vosk-model-kz-0.42", "Kazakh (Large)"),

    # Others
    ("vosk-model-small-eo-0.42", "Esperanto"),
    ("vosk-model-small-pl-0.22", "Polish"),
    ("vosk-model-small-uz-0.22", "Uzbek"),
    ("vosk-model-br-0.8", "Breton"),
    ("vosk-model-gu-0.42", "Gujarati (Large)"),
    ("vosk-model-small-gu-0.42", "Gujarati (Small)"),
    ("vosk-model-tg-0.22", "Tajik (Large)"),
    ("vosk-model-small-tg-0.22", "Tajik (Small)"),
    ("vosk-model-small-te-0.42", "Telugu"),
    ("vosk-model-small-ky-0.42", "Kyrgyz (Small)"),
    ("vosk-model-ky-0.42", "Kyrgyz (Large)"),

    # Speaker
    ("vosk-model-spk-0.4", "Speaker Identification"),
]

# Dil kodları ve isimleri
languages = [  
    ("None", "Auto"), ("af", "Afrikaans"), ("am", "Amharic"), ("ar", "Arabic"), ("as", "Assamese"),
    ("az", "Azerbaijani"), ("ba", "Bashkir"), ("be", "Belarusian"), ("bg", "Bulgarian"),
    ("bn", "Bengali"), ("bo", "Tibetan"), ("br", "Breton"), ("bs", "Bosnian"),
    ("ca", "Catalan"), ("cs", "Czech"), ("cy", "Welsh"), ("da", "Danish"),
    ("de", "German"), ("el", "Greek"), ("en", "English"), ("es", "Spanish"),
    ("et", "Estonian"), ("eu", "Basque"), ("fa", "Persian"), ("fi", "Finnish"),
    ("fo", "Faroese"), ("fr", "French"), ("gl", "Galician"), ("gu", "Gujarati"),
    ("ha", "Hausa"), ("haw", "Hawaiian"), ("he", "Hebrew"), ("hi", "Hindi"),
    ("hr", "Croatian"), ("ht", "Haitian Creole"), ("hu", "Hungarian"), ("hy", "Armenian"),
    ("id", "Indonesian"), ("is", "Icelandic"), ("it", "Italian"), ("ja", "Japanese"),
    ("jw", "Javanese"), ("ka", "Georgian"), ("kk", "Kazakh"), ("km", "Khmer"),
    ("kn", "Kannada"), ("ko", "Korean"), ("la", "Latin"), ("lb", "Luxembourgish"),
    ("ln", "Lingala"), ("lo", "Lao"), ("lt", "Lithuanian"), ("lv", "Latvian"),
    ("mg", "Malagasy"), ("mi", "Māori"), ("mk", "Macedonian"), ("ml", "Malayalam"),
    ("mn", "Mongolian"), ("mr", "Marathi"), ("ms", "Malay"), ("mt", "Maltese"),
    ("my", "Burmese"), ("ne", "Nepali"), ("nl", "Dutch"), ("nn", "Norwegian Nynorsk"),
    ("no", "Norwegian"), ("oc", "Occitan"), ("pa", "Punjabi"), ("pl", "Polish"),
    ("ps", "Pashto"), ("pt", "Portuguese"), ("ro", "Romanian"), ("ru", "Russian"),
    ("sa", "Sanskrit"), ("sd", "Sindhi"), ("si", "Sinhala"), ("sk", "Slovak"),
    ("sl", "Slovenian"), ("sn", "Shona"), ("so", "Somali"), ("sq", "Albanian"),
    ("sr", "Serbian"), ("su", "Sundanese"), ("sv", "Swedish"), ("sw", "Swahili"),
    ("ta", "Tamil"), ("te", "Telugu"), ("tg", "Tajik"), ("th", "Thai"),
    ("tk", "Turkmen"), ("tl", "Tagalog"), ("tr", "Turkish"), ("tt", "Tatar"),
    ("uk", "Ukrainian"), ("ur", "Urdu"), ("uz", "Uzbek"), ("vi", "Vietnamese"),
    ("yi", "Yiddish"), ("yo", "Yoruba"), ("zh", "Chinese (Mandarin)"), ("yue", "Cantonese")
]

class LanguageSelector(QWidget):

    lang = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        from config import Config
        self.config = Config()
        self.config_data = self.config.load_config()
        
        self.config_speech = self.config_data.get("speech")
        self.language = self.config_speech.get("lgname")
        self.language_code = self.config_speech.get("lgcode")

        layout = QVBoxLayout()
        
        self.combo = self.create_ui()

        index = self.combo.findData(self.language_code)   # kod üzerinden arama
        self.combo.setCurrentIndex(index)

        layout.addWidget(self.combo)
        self.combo.currentIndexChanged.connect(self.update_label)
        self.setLayout(layout)

    def create_ui(self):

        combo = QComboBox()
        combo.setFixedHeight(40)

        font = QFont()
        font.setPointSize(12)   # 0'dan büyük bir değer vermelisin
        combo.setFont(font)

        self.setStyleSheet("""
            font-size: 12px;
            min-height: 12px;
            background-color: #111;
        """)

        combo.setStyleSheet("""
            QComboBox {
                font-size: 12px;
                max-width: 100px;
                color: #ddd;
            }

            /*QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: right center;
                width: 30px;           
                border-left: 1px solid #1B4F72;
                background-color: #1B4F72;  
                color: #ddd;
            }

            QComboBox::down-arrow {
                image: url(:/qt-project.org/styles/commonstyle/images/arrowdown-16.png);
                width: 16px;
                height: 16px;
            }

            QComboBox QAbstractItemView {
                background-color: #222;  
                color: black;             
                selection-background-color: #5DADE2; 
            }*/

            QScrollBar:vertical {
                background: transparent;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(100, 100, 100, 150);
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: none;
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }

            QScrollBar:horizontal {
                background: transparent;
                height: 12px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background: rgba(100, 100, 100, 150);
                border-radius: 6px;
                min-width: 20px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                background: none;
                width: 0px;
            }
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: none;
            }
        """)

        for code, name in self.update_lang_list():
            combo.addItem(name, code)

        return combo

    def update_lang_list(self, refresh=False):

        api = self.config_speech["api"]
        if api == "vosk":
            langs = languages
        else:
            langs = languages

        if refresh:
            self.combo.clear()  # tüm öğeleri sil
            for code, name in langs:
                self.combo.addItem(name, code)

        return langs

    def update_label(self):
        code = self.combo.currentData()
        name = self.combo.currentText()
        self.config_speech["lgname"] = name
        self.config_speech["lgcode"] = code
        self.config_data["speech"] = self.config_speech
        self.config.save_config(self.config_data)
        self.lang.emit(code, name)

    def file_load(self, filename):
        with open("language/" + filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data

