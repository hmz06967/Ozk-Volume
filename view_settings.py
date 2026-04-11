from core import *  

from float_slider import FloatSlider

class ViewConfig:
    def __init__(self):
        self.config = {
            "autoscroll": True,
            "autoview":False,
            "alwaysontop": True,
            "timedomain": False,
            "themalist": ["dark"],
            "langlist": ["en","tr"],
            "thema": "dark",
            "language": "en",
            "bgcolor": "#000",
            "fontcolor": "#fff",           # Girdi aygıtları (örneğin mikrofon)
            "fontsize": 12,                # Çıkış aygıtı (örneğin ses çıkışı)
            "font": "Segoe UI",  # FFT boyutu seçeneği
            "viewopacity": 100,     # Minimum frekans (Hz)
            "fontweight": 100,
        }

class ViewSettings(QWidget):
    changed = pyqtSignal()
    save = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.window_width = 400
        self.window_height = 150

        #self.setStyleSheet("background-color: #444; color: white")

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window |  Qt.WindowType.WindowStaysOnTopHint)

        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(0)

        from top_bar import TitleBar  # buraya taşı
        from config import Config

        self.config = Config()
        self.config_data = self.config.load_config()
        self.view = self.config_data.get("view", {})
        self.title = "View Settings"
        self.top_bar = TitleBar(self)

        f = QFormLayout()
        
        self.font = QComboBox()
        font_names = QFontDatabase.families()
        font = self.view.get("font")
        self.font.addItems(font_names)
        self.font.setCurrentIndex(self.find_index(font_names, font))

        self.viewthema = QComboBox()
        themalist = self.view.get("themalist")
        thema = self.view.get("thema")
        self.viewthema.addItems(themalist)
        self.viewthema.setCurrentIndex(self.find_index(themalist, thema))

        self.lang = QComboBox()
        langlist = self.view.get("langlist")
        self.lang.addItems(langlist)
        lg = self.view.get("language")
        self.lang.setCurrentIndex(self.find_index(langlist, lg))

        # Diğer ayarlar
        fontsize = FloatSlider(8, 48, step=1, value = self.view.get("fontsize")) # min, max, value
        self.fontsize = fontsize.slider

        fontweight = FloatSlider(100, 900, step=1, value = self.view.get("fontweight")) # min, max, value
        self.fontweight = fontweight.slider

        viewopacity = FloatSlider(0.15, 1.0, value = self.view.get("viewopacity") / 100) # min, max, value
        self.viewopacity = viewopacity.slider

        """self.timedomain = QCheckBox("Visible time")
        self.timedomain.setCheckState(
            Qt.CheckState.Checked if self.view.get("timedomain") else Qt.CheckState.Unchecked
        )"""

        f.addRow("Thema", self.viewthema)
        f.addRow("Language", self.lang)
        f.addRow("Font", self.font)
        f.addRow("Font Size", fontsize)
        f.addRow("View Opacity", viewopacity)
        f.addRow("View Bold", fontweight)

        # f.addRow("Time Domain", self.timedomain)

        layout.addWidget(self.top_bar)
        layout.addLayout(f)
        self.setLayout(layout)

        # Sinyaller
        self.viewthema.currentIndexChanged.connect(self._on_changed)
        self.lang.currentIndexChanged.connect(self._on_changed)
        self.font.currentIndexChanged.connect(self._on_changed)
        self.fontsize.valueChanged.connect(self._on_changed)  # dikkat! self._on_changed olmalı
        self.viewopacity.valueChanged.connect(self._on_changed)  # dikkat! self._on_changed olmalı
        self.fontweight.valueChanged.connect(self._on_changed)
        
        #self.timedomain.stateChanged.connect(self._on_changed)

        self.center_on_screen()


    def _on_changed(self, *_):
        logging.info("view settings value changed")
        self.view["thema"] = self.viewthema.currentText()
        self.view["language"] = self.lang.currentText()
        self.view["fontsize"] = int(self.fontsize.value())
        self.view["font"] = self.font.currentText()
        self.view["viewopacity"] = int(self.viewopacity.value())
        self.view["fontweight"] = int(self.fontweight.value())
        
        # self.view["timedomain"] = self.timedomain.isChecked()
        self.config_data["view"] = self.view
        self.changed.emit()

    def closeEvent(self, event):
        self.config.save_config(self.config_data)
        #self.save.emit()
        event.accept()

    def find_index(self, arr, value):
        try:
            index = arr.index(value)
            return index
        except ValueError:
            return -1  # değeri bulamazsa -1 döndür

    def center_on_screen(self):
        """Pencerenin ekranın ortasında görünmesini sağlar."""
        # Ekran boyutlarını al
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()

        # Pencere boyutunu al
        window_width = self.window_width
        window_height = self.window_height

        # Ekranın ortasına göre konum hesapla
        x = (screen_geometry.width() - window_width) // 2
        y = (screen_geometry.height() - window_height) // 2

        # Pencereyi yeni pozisyona yerleştir
        self.setGeometry(x, y, window_width, window_height)

        # Ekranın ortasında kalacak şekilde pencereye ekran konumunu ayarla
        # Bu, "window" özelliği nedeniyle etkili olur.