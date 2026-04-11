from core import *  
 
from audio_settings import AudioSettings
from view_settings import ViewSettings
from speech_settings import SpeechSettings
from lan_en import LanguageSelector
from history import CacheManager

import webbrowser

me_url = "https://www.hamzaozkan.com.tr/2026/03/ozk-volume.html"

logging.basicConfig(filename= "top_bar", level=logging.INFO)

class TopbarEvent(Enum):
    CLEAR = 0
    AUTOSCROOL = 1
    COPY = 2
    TRANSLATE = 8,
    ONTOPALWAYS = 6
    VIEWTIME = 9
    VIEWAUTO = 10,

    SETVIEW = 3
    SETSPEECH = 4
    SETLANG = 5
    SETTRANSLATE = 7

class TitleBar(QWidget):
    play = pyqtSignal(int)
    topevent = pyqtSignal(TopbarEvent)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.parent_window = parent
        self.margin = 6
        self.play_status = 0

        self.setFixedHeight(30)
        self.setStyleSheet("background-color: #111; color: white;")

        self.set_config_data()
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.btn_logo = QPushButton()
        
        self.btn_clear = QPushButton()
        self.btn_copy = QPushButton()
        self.btn_play = QPushButton()
        self.btn_translate = QPushButton()

        self.btn_min = QPushButton("—")
        self.btn_max = QPushButton("□")
        self.btn_close = QPushButton("✕")

        self.lang_widget = LanguageSelector()
        self.lang_widget.lang.connect(self.set_play_language)
        self.lang = self.lang_widget.file_load(self.view["language"])
        
        for btn in (self.btn_min, self.btn_max, self.btn_close):
            btn.setFixedSize(30, 20)
            btn.setStyleSheet(
                "color: #fff; border: none;"
            )

        if hasattr(parent, "main"):
            self.set_play_button()
 
            # create clear button
            self.set_button_icon(self.btn_clear, "img/clear.png")
            self.btn_clear.setIconSize(QSize(20, 1208))
            self.btn_clear.setToolTip(self.lang.get("clear_text"))
            self.btn_clear.clicked.connect(lambda: self.topevent.emit(TopbarEvent.CLEAR))
 
            # translate button
            tcolor = "#595959" if not self.trans.get("active") else "#ddd"
            self.set_button_icon(self.btn_translate, "img/translate.png", tcolor)
            self.btn_translate.setIconSize(QSize(18, 18))
            self.btn_translate.setToolTip(self.lang.get("translate_text"))
            self.btn_translate.clicked.connect(self.translate_action)
 
            # create copy button
            self.set_button_icon(self.btn_copy, "img/copy.png")
            self.btn_copy.setIconSize(QSize(14, 14))
            self.btn_copy.setToolTip(self.lang.get("copy_text"))
            self.btn_copy.clicked.connect(lambda: self.topevent.emit(TopbarEvent.COPY))

            self.set_button_icon(self.btn_logo, "img/logo.png")
            self.btn_logo.setIconSize(QSize(14, 14))
            self.btn_logo.setToolTip("Ozk")
            self.btn_logo.clicked.connect(lambda: webbrowser.open(me_url))

            file_menu = self.set_qmenu(self.lang.get("file"))
            
            self.file_menu = file_menu 
            file_menu.addAction(self.lang.get("open"), self.file_open)
            self.history_action = file_menu.addAction(self.lang.get("history"), self.history_settings)
            
            # HistoryPage(self)
            file_menu.addAction(self.lang.get("save"), self.parent_window.save_to_file)
            file_menu.addAction(self.lang.get("save_as"), lambda: self.parent_window.save_to_file(True))
            file_menu.addAction(self.lang.get("exit"), self.close)

            self.auto_scroll_on_top_action = QAction(self.lang.get("auto_sc"), self, checkable=True)
            self.auto_scroll_on_top_action.setChecked(self.view_auto_scroll)
            self.auto_scroll_on_top_action.triggered.connect(self.toggle_on_autoscrool)

            self.always_on_top_action = QAction(self.lang.get("always_on"), self, checkable=True)
            self.always_on_top_action.setChecked(self.view_alwaysontop)
            self.always_on_top_action.triggered.connect(self.toggle_on_always)

            self.auto_view = QAction(self.lang.get("auto_view"), self, checkable=True)
            self.auto_view.setChecked(self.view_auto)
            self.auto_view.triggered.connect(self.toggle_auto_view)

            self.timedomain = QAction(self.lang.get("visible_time"), self, checkable=True)
            self.timedomain.setChecked(self.view_timedomain)
            self.timedomain.triggered.connect(self.toggle_on_timedomain)

            view_menu = QMenu(self.lang.get("view"), self)
            view_menu.addAction(self.auto_scroll_on_top_action)
            view_menu.addAction(self.always_on_top_action)
            view_menu.addAction(self.auto_view)
            view_menu.addAction(self.timedomain)
            view_menu.addAction(self.lang.get("bg_color"), self.change_bg_color)
            view_menu.addAction(self.lang.get("font_color"), self.change_text_color)
            view_menu.addAction(self.lang.get("settings"), self.view_settings)

            settings_menu = QMenu(self.lang.get("settings"), self)
            settings_menu.addAction(self.lang.get("audio"), self.audio_settings)
            settings_menu.addAction(self.lang.get("speech"), self.speech_settings)
            # settings_menu.addAction(self.lang.get("translate"), self.translate_settings)
            # settings_menu.addAction(self.lang.get("profiles"), self.audio_settings)

            lang_menu = QMenu(self.lang.get("language"), self)
            lang_menu.addAction("English")
            lang_menu.addAction("Türkçe")

            btn_file = self._create_qmenu(self.lang.get("file"), file_menu)
            btn_view = self._create_qmenu(self.lang.get("view"), view_menu)
            btn_settings = self._create_qmenu(self.lang.get("settings"), settings_menu)
            # btn_language = self._create_qmenu("Language", lang_menu)
            
            layout.addWidget(self.btn_logo)
            layout.addWidget(btn_file)
            layout.addWidget(btn_view)
            layout.addWidget(btn_settings)
            layout.addWidget(self.lang_widget)
        else: 
            title = QLabel(parent.title)
            title.setStyleSheet("color: white; border: none")

            layout.addWidget(title)

        layout.addStretch()

        if hasattr(parent, "main"):
            layout.addWidget(self.btn_clear)
            layout.addWidget(self.btn_copy)
            # layout.addWidget(self.btn_translate)
            layout.addWidget(self.btn_play)

        layout.addWidget(self.btn_min)
        layout.addWidget(self.btn_max)
        layout.addWidget(self.btn_close)

        # bağlantılar
        self.btn_min.clicked.connect(self.parent_window.showMinimized)
        self.btn_max.clicked.connect(self.toggle_maximize)
        self.btn_close.clicked.connect(self.parent_window.close)

        # "File" menüsüne bir QAction ekleyelim
        # self.history_action.setToolTip("Click or hover to view history files")
        # self.history_action.triggered.connect(self.open_history)

        # Hover popup işlevini başlat
        self.setup_hover_popup()

    def setup_hover_popup(self):
        """Popup’u oluştur ve hover ile göster"""
        self.popup = QWidget()
        self.popup.setStyleSheet("""
            background: white;
            border: 1px solid #ccc;
            border-radius: 8px;
            padding: 12px;
            font-size: 14px;
        """)
        
        layout = QVBoxLayout(self.popup)
        label = QLabel("Hover History (Right Panel)")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        self.popup.hide()

        # Menü üzerinde hover olayını dinle
        # self.history_action.installEventFilter(self)  # EventFilter’ı ekliyoruz

    def eventFilter(self, obj, event):
        """Fare hareketi kontrolü"""
        if obj == self.history_action:
            if event.type() == Qt.EventType.MouseMove:
                rect = self.history_action.rect()
                if rect.contains(event.globalPos()):
                    self.show_popup()
                else:
                    self.popup.hide()
            elif event.type() == Qt.EventType.MouseLeave:
                self.popup.hide()
        return super().eventFilter(obj, event)

    def show_popup(self):
        print("open on history")
        """Popup'ı göster"""
        # Konum ayarla: menünün sağında
        menu_rect = self.history_action.rect()

        popup_x = menu_rect.right() + 10
        popup_y = menu_rect.y()
        
        self.popup.setGeometry(popup_x, popup_y, 250, 300)
        self.popup.show()

    def open_history(self):
        """Tıklandığında gerçek geçmişi açar (örneğin başka pencere veya listeye gider)"""
        self.popup.hide()
        print("History opened!")

    def translate_action(self):
        self.trans["active"] = not self.trans["active"]
        self.config_data["translate"] = self.trans
        self.config.save_config(self.config_data)
        color = "#595959" if not self.trans.get("active") else "#ddd"
        self.btn_translate.setIcon(self.colorize_icon("img/translate.png", color))
        self.topevent.emit(TopbarEvent.TRANSLATE) 

    def set_config_data(self):
        self.config = Config()
        self.config_data = self.config.load_config()
        self.view = self.config_data.get("view")
        self.view_auto_scroll = self.view.get("alwaysontop")
        self.view_alwaysontop = self.view.get("autoscroll")
        self.view_auto = self.view.get("autoview")
        self.view_timedomain = self.view.get("timedomain")
        self.trans = self.config_data.get("translate")

    def set_qmenu(self, qmenu):
        q = QMenu(qmenu, self)
        q.setStyleSheet("""
            QMenu {
                background-color: #2b2b2b;
                border: 1px solid #444;
                padding: 4px;
            }

            QMenu::item {
                padding: 6px 25px;
                background-color: transparent;
                color: #f0f0f0;
            }

            QMenu::item:selected {
                background-color: #3d6cb9;   /* Hover/Seçili öğe */
                color: white;
            }

            QMenu::item:disabled {
                color: #777;
            }

            QMenu::separator {
                height: 1px;
                background: #555;
                margin: 4px 10px;
            }

            QMenu::indicator {
                width: 16px;
                height: 16px;
            }""")
        return q

    def colorize_icon(self, path, color):
        pixmap = QPixmap(path)
        tinted = QPixmap(pixmap.size())
        #tinted.fill(QColor(color))
        tinted.fill(QColor(0, 0, 0, 0))  # tamamen transparan

        painter = QPainter(tinted)
        painter.fillRect(pixmap.rect(), QColor(color))

        # PyQt6’da sabitler enum altında:
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationIn)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

        return QIcon(tinted)

    def set_play_language(self, code, name):
        logging.info(f"Changed language: {name}")
        self.speech_lang_code = code
        self.topevent.emit(TopbarEvent.SETLANG)

    def set_play_button(self):
        
        self.pause_icon_path = "img/pause.png"
        self.play_icon_path = "img/play.png"
        self.wait_icon_path = "img/wait.png"

        self.set_button_icon(self.btn_play, self.wait_icon_path)
        self.btn_play.setIconSize(QSize(18, 18))
        self.btn_play.setToolTip("Oynat")
        self.btn_play.clicked.connect(self.play_action)

    def check_image_exists(self, path):
        """Resmi yükleyip geçerli olup olmadığını kontrol eder"""
        try:
            QPixmap(path).scaled(32, 32)  # küçük bir boyutta test yapar
            return True
        except Exception as e:
            logging.info(f"❌ Resim hatası: {e}")
            return False

    def set_button_icon(self, button, icon_path, color = "#ddd"):
        """Butona ikon atar (daha sonra değiştirilebilir)"""
        if self.check_image_exists(icon_path):
            button.setIcon(self.colorize_icon(icon_path, color))
        else:
            logging.info(f"❌ İkon ({icon_path}) yüklenemedi!")

    def _create_qmenu(self, name, qmenu):
        btn = QPushButton(name)
        btn.setMenu(qmenu)
        btn.setProperty("hasMenu", True)
        btn.setStyleSheet("""
            QPushButton::menu-indicator {
                image: none;
            }
            QPushButton {
                color: gray;                /* yazı rengi beyaz */
                margin-left: 5px;
                margin-right: 5px;

            }
            QPushButton:hover {
                color: white;
                 /*background-color: #2980b9;   hover rengi */
            }
            QPushButton:pressed {
                background-color: #1c5980;   /* basılıyken */
            }
        """)

        qmenu.setStyleSheet("""
            QMenu {
                background-color: #222; /* Arka planı boş yapar */
                border: none;
                font-size: 12px;
                font-family: Arial;
                color: #ddd;
                width: 150px;
            }
            QMenu::item {
                padding: 4px 8px;
                margin: 0px;
                width: 150%;
                border-bottom: 1px solid #111;
            }
            QMenu::item:selected {
                background-color: #f0f0f0; /* Seçili olanı hafif yapar */
                color: black;
            }
        """)
        
        return btn

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self.drag_pos
            self.parent_window.move(self.parent_window.pos() + delta)
            self.drag_pos = event.globalPosition().toPoint()
    
    def toggle_auto_view(self):
        checked =  self.auto_view.isChecked()
        self.set_view_data("autoview", checked)
        self.config.save_config(self.config_data)
        self.topevent.emit(TopbarEvent.VIEWAUTO)

    def toggle_maximize(self):
        if self.parent_window.isMaximized():
            self.parent_window.showNormal()
        else:
            self.parent_window.showMaximized()

    def toggle_on_timedomain(self):
        checked =  self.timedomain.isChecked()
        self.set_view_data("timedomain", checked)
        self.config.save_config(self.config_data)
        self.topevent.emit(TopbarEvent.VIEWTIME)

    # Actions 
    def play_action(self):
        if self.play_status == 1:
            text = self.lang.get("run_speech")
            icon = self.play_icon_path
            self.play_status = 2
        elif self.play_status == 2:
            text = self.lang.get("pause_speech")
            icon = self.pause_icon_path
            self.play_status = 1
        else:
            text = self.lang.get("loading")
            icon = self.wait_icon_path
        
        self.set_button_icon(self.btn_play, icon)
        self.btn_play.setToolTip(text)
        self.play.emit(self.play_status)

    def open_history(self):

        self.cache_manager = CacheManager(self)
        # self.cache_manager.connect.text()
        # self.translate_setup.changed.connect(lambda: self.topevent.emit(TopbarEvent.SETTRANSLATE))

    def file_open(self):
        # Dosya seçici aç
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Audio File",
            "",  # Başlangıç dizini (kullanıcı belirleyebilir)
            "Audio Files (*.wav *.mp3 *.flac *.ogg *.aac);;Subtitle Files (*.txt *.srt *.webvtt *.ass);"
        )

        self.parent_window.input_file(file_path)

    def set_view_data(self, name, value):
        self.view[name] = value
        self.config_data["view"] = self.view
        self.config.save_config(self.config_data)

    def toggle_on_always(self):
        self.set_view_data("alwaysontop", self.always_on_top_action.isChecked())
        self.topevent.emit(TopbarEvent.ONTOPALWAYS)

    def toggle_on_autoscrool(self):
        self.view_auto_scroll = self.auto_scroll_on_top_action.isChecked()
        self.set_view_data("autoscroll", self.view_auto_scroll)
        self.topevent.emit(TopbarEvent.AUTOSCROOL)
        """if self.auto_scroll_on_top_action.isChecked():
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
        self.show()"""

    def change_bg_color(self):
        dialog = QColorDialog(self.parent_window)
        if dialog.exec():
            fontcolor = self.view.get("fontcolor")
            color = dialog.currentColor()
            bgcolor = color.name()
            self.view["bgcolor"] = bgcolor
            self.config_data["view"] = self.view
            self.config.save_config(self.config_data)
            self.parent_window.set_text_edit_style(bgcolor, fontcolor)

    def change_text_color(self):
        dialog = QColorDialog(self.parent_window)
        if dialog.exec():
            bgcolor = bg = self.view.get("bgcolor")
            color = dialog.currentColor()
            fontcolor = color.name()
            self.view["fontcolor"] = fontcolor
            self.config_data["view"] = self.view
            self.config.save_config(self.config_data)
            self.parent_window.set_text_edit_style(bgcolor, fontcolor)

    def text_edit_set(self, text):
        self.parent_window.text_edit.clear()
        self.parent_window.text_edit.insertPlainText(text)

    def active_screen(self, setup):
        setup.show()
        setup.raise_()   # öne getir
        setup.activateWindow()

    def history_settings(self):
        self.history_setup = CacheManager(self)
        self.active_screen(self.history_setup)
        self.history_setup.changed.connect(lambda: self.topevent.emit(TopbarEvent.SETHISTORY))
        self.history_setup.text.connect(self.text_edit_set)

    def translate_settings(self):
        self.translate_setup = TranslateSettings(self)
        self.active_screen(self.translate_setup)
        self.translate_setup.changed.connect(lambda: self.topevent.emit(TopbarEvent.SETTRANSLATE))

    def speech_settings(self):
        self.speech_setup = SpeechSettings(self)
        self.active_screen(self.speech_setup)
        self.speech_setup.changed.connect(lambda: self.topevent.emit(TopbarEvent.SETSPEECH))

    def view_settings(self):
        self.view_setup = ViewSettings(self)
        self.active_screen(self.view_setup)
        self.view_setup.changed.connect(lambda: self.topevent.emit(TopbarEvent.SETVIEW))

    def audio_settings(self):
        self.audio_setup = AudioSettings(self)
        self.active_screen(self.audio_setup)
        self.audio_setup.save.connect(lambda: self.play.emit(4))
