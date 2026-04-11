from core import *  

from float_slider import FloatSlider

class SpeechConfig:
    def __init__(self):
        self.config = {
            "sizelist": ["tiny","base","small","medium","large","large-v3"],
            "apilist": ["faster_whisper","vosk"],
            "api": "faster_whisper",
            "lgname": "Turkish",
            "lgcode": "tr",
            "size": "medium",
            "chunksize": 2,
            "beamsize": 1,
            "vadfilter": True,
            "autolang": True,
        }

class SpeechSettings(QWidget):
    changed = pyqtSignal()
    save = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.window_width = 400
        self.window_height = 150
        self.bparent = parent

        #self.setStyleSheet("background-color: #444; color: white")

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window |  Qt.WindowType.WindowStaysOnTopHint)

        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(0)

        from top_bar import TitleBar  # buraya taşı
        from config import Config

        self.config = Config()
        self.config_data = self.config.load_config()
        self.speech = self.config_data.get("speech", {})
        self.title = self.bparent.lang.get("speech_filter")
        self.top_bar = TitleBar(self)

        f = QFormLayout()
        
        sizelist = self.speech.get("sizelist")
        size = self.speech.get("size")
        self.msize = self.set_combo(sizelist, size)

        apilist = self.speech.get("apilist")
        apiname = self.speech.get("api")
        self.api = self.set_combo(apilist, apiname)

        # Diğer ayarlar
        beamsize = FloatSlider(1, 10, step=1, value=self.speech.get("beamsize")) # min, max, value
        self.beamsize = beamsize.slider

        chunksize = FloatSlider(1, 100, step=1, value=self.speech.get("chunksize")) # min, max, value
        self.chunksize = chunksize.slider
        
        self.vadfilter = QCheckBox(self.bparent.lang.get("vad_filter"))
        self.vadfilter.setCheckState(
            Qt.CheckState.Checked if self.speech.get("vadfilter") else Qt.CheckState.Unchecked
        )

        self.autolang = QCheckBox(self.bparent.lang.get("auto_lang"))
        self.autolang.setCheckState(
            Qt.CheckState.Checked if self.speech.get("autolang") else Qt.CheckState.Unchecked
        )

        f.addRow("Api", self.api)
        f.addRow("Size", self.msize)
        f.addRow("Chunk Size", chunksize)
        f.addRow("Beam Size", beamsize)
        f.addRow("Vad Filter", self.vadfilter)
        #f.addRow("Auto Language", self.autolang)

        layout.addWidget(self.top_bar)
        layout.addLayout(f)
        self.setLayout(layout)

        # Sinyaller
        self.api.currentIndexChanged.connect(self._on_changed)
        self.msize.currentIndexChanged.connect(self._on_changed)
        
        chunksize.slider.valueChanged.connect(self._on_changed)  # dikkat! self._on_changed olmalı
        chunksize.spin.valueChanged.connect(self._on_changed)
        beamsize.slider.valueChanged.connect(self._on_changed)  # dikkat! self._on_changed olmalı
        beamsize.spin.valueChanged.connect(self._on_changed)
        
        self.vadfilter.stateChanged.connect(self._on_changed)
        self.autolang.stateChanged.connect(self._on_changed)

        self.center_on_screen()

    def set_combo(self, array, value):
        combo = QComboBox()
        combo.addItems(array)
        combo.setCurrentIndex(self.find_index(array, value))
        return combo

    def _on_changed(self, *_):
        self.speech["api"] = self.api.currentText()
        self.speech["size"] = self.msize.currentText()
        self.speech["chunksize"] = int(self.chunksize.value())
        self.speech["beamsize"] = int(self.beamsize.value())
        self.speech["vadfilter"] = self.vadfilter.isChecked()
        self.speech["autolang"] = self.autolang.isChecked()
        self.config_data["speech"] = self.speech
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

        