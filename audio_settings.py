from core import *  

from float_slider import FloatSlider

class AudioConfig:
    def __init__(self):
        self.config = {
            "fft_list": ["256", "512", "1024", "2048", "4096", "8096", "12288", "16384", "32798", "48000"],
            "mode_list": ["Input", "Output (loopback)", "Both"],
            "mode": 1,
            "input": 2,           # Girdi aygıtları (örneğin mikrofon)
            "output": 2,                # Çıkış aygıtı (örneğin ses çıkışı)
            "fftsize": 1024,  # FFT boyutu seçeneği
            "minfreq": 20,     # Minimum frekans (Hz)
            "maxfreq": 16000, # Maksimum frekans (Hz)
            "gate": -45,      # Gürültü kapısı (threshold)
            "onfilter": True,
        }

class AudioSettings(QWidget):
    changed = pyqtSignal()
    save = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.bparent = parent
 
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window |  Qt.WindowType.WindowStaysOnTopHint)
        self.restart_worker = False

        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(0)

        from top_bar import TitleBar  # buraya taşı
        from config import Config

        self.config = Config()
        self.config_data = self.config.load_config()
        self.audio = self.config_data.get("audio", {})
        self.title = self.bparent.lang.get("audio_sett")
        self.top_bar = TitleBar(self)

        self.fft_list = self.audio.get("fft_list")
        self.mode_list = self.audio.get("mode_list")

        f = QFormLayout()
        
        # I/O seçimi
        self.io_mode = QComboBox()
        self.io_mode.addItems(self.mode_list)

        # Gerçek cihaz listeleri
        self.input_dev = QComboBox()
        self.output_dev = QComboBox()

        self.fft_size = QComboBox()
        self.fft_size.addItems(self.fft_list)
        
        self.min_freq = QSpinBox(); self.min_freq.setRange(0, 20000); 
        self.max_freq = QSpinBox(); self.max_freq.setRange(0, 20000); 
 
        # Diğer ayarlar
        ng = FloatSlider(-120, -1, value=self.audio.get("gate")) # min, max, value
        self.noise_gate = ng.slider
        ng.changed.connect(lambda: (self.changed.emit()))
        
        f.addRow(self.bparent.lang.get("io_mode"), self.io_mode)
        f.addRow(self.bparent.lang.get("inp_dev"), self.input_dev)
        f.addRow(self.bparent.lang.get("out_dev"), self.output_dev)
        f.addRow(self.bparent.lang.get("fft_size"), self.fft_size)
        f.addRow(self.bparent.lang.get("min_freq"), self.min_freq)
        f.addRow(self.bparent.lang.get("max_freq"), self.max_freq)

        self.filter_en = QCheckBox()
        self.filter_en.setCheckState(
            Qt.CheckState.Checked if self.audio.get("onfilter", False) else Qt.CheckState.Unchecked
        )
        
        f.addRow(self.bparent.lang.get("filter_en"), self.filter_en)
 
        #f.addRow("Noise gate (dB)", ng)

        row = QHBoxLayout()
        self.btn_refresh = QPushButton(self.bparent.lang.get("refresh"))
        row.addWidget(self.btn_refresh)

        f.addRow("", row)

        layout.addWidget(self.top_bar)
        layout.addLayout(f)
        self.setLayout(layout)

        # Sinyaller
        self.btn_refresh.clicked.connect(lambda: self.refresh_audio_devices(keep_current=True))
        self.set_default()
        self.setup_auto_connections()
        self.refresh_audio_devices(keep_current=False)

        self.filter_en.stateChanged.connect(self._on_changed)

        self.center_on_screen()

    def set_default(self):
        fft_size = str(self.audio.get("fftsize"))
        fft_index = self.find_index(self.fft_list, fft_size)
        self.io_mode.setCurrentIndex(self.audio.get("mode"))
        self.min_freq.setValue(self.audio.get("minfreq")) 
        self.max_freq.setValue(self.audio.get("maxfreq"))
        self.fft_size.setCurrentIndex(fft_index)
        self.input_dev.setCurrentIndex(self.audio.get("input"))
        self.output_dev.setCurrentIndex(self.audio.get("output"))
        # self.noise_gate.setValue(self.audio.get("gate"))


    def setup_auto_connections(self):
        control_map = {
            "io_mode": self._on_changed,
            "input_dev": self._on_changed,
            "output_dev": self._on_changed,
            "min_freq": self._on_changed,
            "max_freq": self._on_changed,
            "noise_gate": self._on_changed,  # slider için
            "fft_size": self._on_changed,      # combo box için
            "filter_en": self._on_changed
        }

        for control_name in control_map:
            widget = getattr(self, control_name)
            if isinstance(widget, (QComboBox, QSlider, QSpinBox)):
                if isinstance(widget, QComboBox):
                    widget.currentIndexChanged.connect(control_map[control_name])
                elif isinstance(widget, (QSlider, QSpinBox)):  
                    widget.valueChanged.connect(control_map[control_name])
                elif isinstance(widget, (QCheckBox)):
                    print("test ok")
                    widget.stateChanged.connect(control_map[control_name])
                else:
                    print(widget)
                    continue  # Diğer türler desteklenmiyor (örneğin QLineEdit)

                # Otomatik bağlama

    def refresh_audio_devices(self, keep_current: bool = True):
        cur_in = self.input_dev.currentData() if keep_current else None
        cur_out = self.output_dev.currentData() if keep_current else None

        ki = 0
        ko = 0

        sin = self.audio.get("input")
        sot = self.audio.get("output")

        self.input_dev.blockSignals(True)
        self.output_dev.blockSignals(True)
        self.input_dev.clear()
        self.output_dev.clear()

        try:
            devices = sd.query_devices()
            default_in, default_out = sd.default.device  # index veya None
        except Exception as e:
            # cihaz sorgusu başarısızsa boş bırak
            self.input_dev.addItem(f"(audio query failed) {e}", None)
            self.output_dev.addItem(f"(audio query failed) {e}", None)
            self.input_dev.blockSignals(False)
            self.output_dev.blockSignals(False)
            return

        for idx, d in enumerate(devices):
            name = d.get("name", f"Device {idx}")
            hostapi = d.get("hostapi", None)

            # hostapi adı (isteğe bağlı, daha okunur)
            api_name = ""
            try:
                if hostapi is not None:
                    api = sd.query_hostapis(hostapi)
                    api_name = api.get("name", "")
            except Exception:
                api_name = ""

            tag = f"{name} [{api_name}]" if api_name else name

            if d.get("max_input_channels", 0) > 0:
                prefix = "(d) " if idx == default_in else ""
                self.input_dev.addItem(prefix + tag, idx)
                if idx == sin and cur_in is None:
                    self.input_dev.setCurrentIndex(ki)
                ki += 1

            if d.get("max_output_channels", 0) > 0:
                prefix = "(d) " if idx == default_out else ""
                self.output_dev.addItem(prefix + tag, idx)
                if idx == sot and cur_out is None:
                    self.output_dev.setCurrentIndex(ko)
                ko += 1

        # seçim geri yükle
        if cur_in is not None:
            i = self.input_dev.findData(cur_in)
            if i >= 0: self.input_dev.setCurrentIndex(i)
        if cur_out is not None:
            i = self.output_dev.findData(cur_out)
            if i >= 0: self.output_dev.setCurrentIndex(i)

        self.input_dev.blockSignals(False)
        self.output_dev.blockSignals(False)
        self.changed.emit()

        # restart audio worker
        self.restart_worker = True

        self.save.emit()

    def find_index(self, arr, value):
        try:
            index = arr.index(value)
            return index
        except ValueError:
            return -1  # değeri bulamazsa -1 döndür
            
    def _on_changed(self, *_):

        logging.info("value changed")

        device = self.selected_devices()

        mode = device["io_mode"]

        self.input_dev.setEnabled(mode in [self.bparent.lang.get("inp"), self.bparent.lang.get("both")])
        self.output_dev.setEnabled(mode in [self.bparent.lang.get("output"), self.bparent.lang.get("both")])

        self.audio["mode"] = self.find_index(self.mode_list, mode)
        self.audio["input"] = device["input_index"]
        self.audio["output"] = device["output_index"]
        self.audio["fftsize"] = int(self.fft_size.currentText())
        self.audio["minfreq"] = int(self.min_freq.value())
        self.audio["maxfreq"] = int(self.max_freq.value()) 
        # self.audio["gate"] = int(self.noise_gate.value())
        self.audio["onfilter"] = self.filter_en.isChecked()
        
        self.config_data["audio"] = self.audio

        self.config.save_config(self.config_data)

        self.changed.emit()

    def selected_devices(self) -> dict:
        return {
            "io_mode": self.io_mode.currentText(),
            "input_index": self.input_dev.currentData(),
            "output_index": self.output_dev.currentData(),
        }

    def closeEvent(self, event):
        # self.save.emit()
        event.accept()

    def center_on_screen(self):
        """Pencerenin ekranın ortasında görünmesini sağlar."""
        # Ekran boyutlarını al
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()

        # Pencere boyutunu al
        window_width = 500
        window_height = 200

        # Ekranın ortasına göre konum hesapla
        x = (screen_geometry.width() - window_width) // 2
        y = (screen_geometry.height() - window_height) // 2

        # Pencereyi yeni pozisyona yerleştir
        self.setGeometry(x, y, window_width, window_height)

        # Ekranın ortasında kalacak şekilde pencereye ekran konumunu ayarla
        # Bu, "window" özelliği nedeniyle etkili olur.