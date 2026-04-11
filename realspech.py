
from core import *  

from top_bar import TitleBar, TopbarEvent
from audio_settings import AudioConfig
from speech_worker import AudioSpeechWorker, SpeechStatus
from resize import ResizableWindow
# from translate import Translator
from history import HistoryFunct

class Realspeech(QMainWindow, ResizableWindow):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.resize(700, 400)

        self.create_qtray()

        self.main = True
        self.drag_pos = None
        self.resizing = False
        self.resize_edge = None
        self.margin = 6
        self.status = SpeechStatus.LOAD
        self.last_save = None
        self.mouse_pressed = False
        
        self.history = HistoryFunct(self)
 
        container = QWidget()
        container.setStyleSheet(
            """background-color: #111;"""
        )

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.top_bar = TitleBar(self)

        self.config = Config()
        self.config_data = self.config.load_config()
        self.view_data = self.config_data.get("view")
        self.trans_data = self.config_data.get("translate")
        self.setWindowOpacity(self.view_data.get("viewopacity") / 100)  # %80 opaklık
        self.viewauto = self.view_data.get("autoview")

        # self.translator = Translator(self)

        self.viewtime = self.view_data["timedomain"]
        self.timer = QTimer()  # Belirli süre sonra çalışacak
        self.timer.setSingleShot(True)  # Sadece bir kez çalışır
        self.timer.setInterval(2500)  # ms'ye çevirme
        self.timer.timeout.connect(self.on_timeout)

        fontcolor = self.view_data.get("fontcolor")
        bgcolor = self.view_data.get("bgcolor")

        self.text_edit = QTextEdit()
        self.text_edit.setCursorWidth(0) 

        # self.text_edit.setReadOnly(True)
        self.text_edit.setMinimumHeight(20)  # Örneğin 60 piksel

        self.set_text_edit_style(bgcolor, fontcolor)
        
        # self.current_font = self.text_edit.font()
        # print(self.current_font.family())
        # casper = text_edit.toplaintext()

        layout.addWidget(self.top_bar)
        layout.addWidget(self.text_edit)
    
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.top_bar.hide()

        self.setMouseTracking(True)
        self.text_edit.setMouseTracking(True)
        self.text_edit.installEventFilter(self)

        self.speech_thread = QThread()
        self.speech_worker = AudioSpeechWorker()
        self.speech_worker.moveToThread(self.speech_thread)
        self.speech_worker.log.connect(self.log)
        self.speech_worker.text.connect(self.speech_callback)
        self.speech_worker.status.connect(self.speech_status_callback)
        self.speech_thread.started.connect(self.speech_worker.run)

        self.top_bar.play.connect(self.speech_play_callback)
        self.top_bar.topevent.connect(self.topbar_event_callback)
 
        self.speech_thread.start() 

    def show_from_tray(self):
        self.setWindowOpacity(self.view_data.get("viewopacity") / 100)  # %80 opaklık
        self.show()
        self.setWindowState(self.windowState() & ~Qt.WindowState.WindowMinimized)
        self.raise_()
        self.activateWindow()

    def on_tray_activated(self, reason):
        # Çift tık ile aç/kapat
        # if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
        if self.isVisible():
            self.hide()
        else:
            self.show_from_tray()

    def create_qtray(self):
        
        # Not: Kendi .ico dosyanı koyman en iyisi
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(QIcon("img/logo.png"))

        menu = QMenu()

        act_show = QAction("Show", self)
        act_quit = QAction("Quit", self)

        act_show.triggered.connect(self.show_from_tray)
        act_quit.triggered.connect(self.close)

        menu.addAction(act_show)
        menu.addSeparator()
        menu.addAction(act_quit)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self.on_tray_activated)
        
        self.tray.show()

        # İstersen ilk çalıştırmada bilgi ver
        """self.tray.showMessage(
            "Running in background",
            "App is minimized to tray. Right click tray icon for menu.",
            QSystemTrayIcon.MessageIcon.Information,
            2500
        )"""

        # “gerçekten çık” için flag
        self._really_quit = False

    def set_text_edit_style(self, bgcolor, fontcolor):

        self.set_text_edit_font()
            
        self.text_edit.setStyleSheet(f"""
            QTextEdit {{
                outline: none;
                background-color: {bgcolor};
                color: {fontcolor};
                border: 4px solid transparent;
            }}

            QScrollBar:vertical {{
                background: transparent;
                width: 12px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: rgba(100, 100, 100, 150);
                border-radius: 6px;
                min-height: 20px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                background: none;
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}

            QScrollBar:horizontal {{
                background: transparent;
                height: 12px;
                margin: 0px;
            }}
            QScrollBar::handle:horizontal {{
                background: rgba(100, 100, 100, 150);
                border-radius: 6px;
                min-width: 20px;
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                background: none;
                width: 0px;
            }}
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                background: none;
            }}
        """)
    
    def set_text_edit_font(self):
        font = QFont()
        font.setFamily(self.view_data.get("font"))   # Burada istediğiniz font ailesini yazın
        font.setPointSize(int(self.view_data.get("fontsize")))
        font.setWeight(int(self.view_data.get("fontweight")))  # Normal ağırlık (standart)
        self.text_edit.setFont(font)

    def log(self, msg):
        logging.info(msg) 
    
    def toplaintext(self):
        cleaned = self.text_edit.toPlainText()
        #cleaned = re.sub(r'^["\']|["\']$', '', data)
        #cleaned = cleaned[1::-1]
        return cleaned.strip()
    
    def input_file(self, file_path):
        
        logging.info("Dosya seçildi: %s", file_path)

        is_file = None

        for file_end in self.speech_worker.supported:
            if file_path.endswith(file_end):
                is_file = "audio"

        for file_end in self.speech_worker.subtitle_api.supported:
            if file_path.endswith(file_end):
                is_file = "subtitle"

        if is_file == "subtitle":
            self.speech_status_callback(SpeechStatus.PAUSED)
            self.speech_worker.subtitle_api.load_from_file(file_path)
            self.speech_insert_text()

        elif is_file == "audio":
            self.speech_worker.status_mode = SpeechStatus.WAIT 
            self.speech_status_callback(SpeechStatus.WAIT )
            self.speech_worker.load_from_file(file_path)
            self.speech_worker.status_mode = SpeechStatus.PAUSED
            self.speech_status_callback(SpeechStatus.PAUSED)
                
    def save_to_file(self, save_as=None):
        
        try:
            dt = datetime.now()
            fname = f"{dt.day}-{dt.month}-{dt.year}-{dt.hour}-{dt.minute}-{dt.second}-subtitle.txt"

            if not hasattr(self, "old_file_path") or save_as:
                self.old_file_path, _ = QFileDialog.getSaveFileName(
                    self,
                    "Save",
                    fname,
                    f"Audio Time-Text Formats (*.txt *.srt *.webvtt *.ass);; All Files (*)"
                )

            if self.speech_worker.subtitle_api.save_with_format(self.old_file_path, self.viewtime):
                self.old_file_path = format_name

            # logging.info("Son dosya kaydedildi..")

        except Exception as e: 
            logging.error(e)

    def topbar_event_callback(self, event):
        if event == TopbarEvent.CLEAR:
            self.text_edit.clear()
        elif event == TopbarEvent.AUTOSCROOL:
            self.text_autoscrool = True
        elif event == TopbarEvent.COPY:
            pyperclip.copy(self.toplaintext())
        elif event == TopbarEvent.SETVIEW:
            self.view_data = self.top_bar.view_setup.view
            self.setWindowOpacity(self.view_data.get("viewopacity") / 100)  # %80 opaklık
            self.set_text_edit_font()
        elif event == TopbarEvent.SETSPEECH:
            self.speech_data = self.top_bar.speech_setup.speech
            # self.top_bar.lang_widget.config_speech = self.speech_data
            # self.top_bar.lang_widget.update_lang_list(True)

            if self.speech_worker.model_size is not None: 
                if self.speech_worker.model_size != self.speech_data.get("size") or self.speech_worker.speech_api != self.speech_data.get("api"):
                    self.config.save_config(self.top_bar.speech_setup.config_data)
                    self.speech_worker.status_mode = SpeechStatus.RELOAD
                else:
                    self.speech_worker.chunk_size = self.speech_data.get("chunksize")
                    self.speech_worker.vad_filter = self.speech_data.get("vadfilter")
                    self.speech_worker.beam_size = self.speech_data.get("beamsize")
                    self.speech_worker.auto_lang = self.speech_data.get("autolang")
                    # self.speech_worker.language = None if self.speech_worker.auto_lang else self.speech_data.get("lgcode")
            
        elif event == TopbarEvent.SETLANG:
            lang = self.top_bar.speech_lang_code
            lang = None if lang == "None" else lang
            self.speech_worker.language = lang
            if self.speech_worker.speech_api == "vosk":
                self.speech_worker.status_mode = SpeechStatus.RELOAD

        elif event == TopbarEvent.ONTOPALWAYS:
            if self.top_bar.always_on_top_action.isChecked():
                self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
            else:
                self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
            self.show()
        elif event==TopbarEvent.SETTRANSLATE:
            self.trans_data = self.top_bar.translate_setup.translate
        elif event==TopbarEvent.TRANSLATE:
            self.trans_data["active"] = self.top_bar.trans["active"]
        elif event == TopbarEvent.VIEWTIME:
            self.viewtime = self.top_bar.timedomain.isChecked()
            self.speech_insert_text()
        elif event == TopbarEvent.VIEWAUTO:
            self.viewauto = self.top_bar.auto_view.isChecked()

        logging.info(event)  

    def speech_insert_text(self):

        logging.info("Viewtab ile text eklendi!")
        self.text_edit.clear()
        subtitle_api = self.speech_worker.subtitle_api
        if self.viewtime:
            self.text_edit.insertPlainText(subtitle_api.format_subtitles_to_hash())
        else:
            for subtitle in subtitle_api.get_all_subtitles():
                self.text_edit.append(subtitle["title"])

    def speech_play_callback(self, play):
        if play == 2 and self.status == SpeechStatus.STARTED:
            self.speech_worker.audio_stop()
        elif play == 1 and self.status == SpeechStatus.PAUSED:
            self.speech_worker.audio_start()
        elif play == 3:
            self.speech_worker.status_mode = SpeechStatus.RELOAD
        elif play == 4:
            self.speech_worker.audio_stop()
            self.speech_worker.audio_start()

    def speech_status_callback(self, status):
        logging.info(status)
        self.status = status
        if status == SpeechStatus.STARTED:
            self.top_bar.play_status = 2
        elif status == SpeechStatus.PAUSED:
            self.top_bar.play_status = 1
        else:
            self.top_bar.play_status = 0

        self.top_bar.play_action()
    
    def speech_callback(self, line, msg):

        # print(source_lang, target_lang)       
        if self.viewauto:
            self.setWindowOpacity(self.view_data.get("viewopacity") / 100)
            self.timer.start()

        active_translate = self.trans_data["active"]
        source_lang = self.speech_worker.language
        target_lang = self.trans_data["lgcode"]

        """if source_lang != target_lang and active_translate:
            msg = self.translator.translate(msg, source_lang, target_lang)"""
        
        new_line = line if self.viewtime else msg
        self.text_edit.append(new_line)

        # self.text_edit.insertPlainText(msg)

        if self.top_bar.view_auto_scroll:
            # Otomatik olarak aşağıya kaydır
            self.text_edit.verticalScrollBar().setValue(
                self.text_edit.verticalScrollBar().maximum()
            )

        """cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.text_edit.setTextCursor(cursor)
        self.text_edit.insertPlainText(msg)"""

    def speech_stop(self):
        self.speech_worker.stop()
        self.speech_thread.quit()
        self.speech_thread.wait()

    def on_timeout(self):

        if self.viewauto and not self.mause_event:
            # self.hide()
            self.setWindowOpacity(0)
            self.timer.stop()
    
    def eventFilter(self, obj, event):
        if event.type() == event.Type.MouseMove:
            print("move")
            
        if obj == self.text_edit and event.type() == event.Type.MouseMove:
            pos = event.pos()
            edge = self.get_edge(pos)
            self.cursorUpdate(edge)
            print("TextEdit edge:", edge)
        return super().eventFilter(obj, event)
        
    def enterEvent(self, event: QEvent):
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        # Otomatik olarak aşağıya kaydır
        self.text_edit.verticalScrollBar().setValue(
            self.text_edit.verticalScrollBar().maximum()
        )
        
        self.mause_event = True

        self.top_bar.show()

    def leaveEvent(self, event):
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        buttons = QApplication.mouseButtons()
        self.mause_event = False

        if buttons != Qt.MouseButton.NoButton:
            return
            
        self.top_bar.hide()

    def closeEvent(self, event):
        # self.config.save_config(self.config_data)

        data = self.text_edit.toPlainText()
        if len(data) > 0:
            dt = datetime.now()
            fname = f"{dt.day}-{dt.month}-{dt.year}-{dt.hour}-{dt.minute}-{dt.second}-subtitle"
            self.history.create_files(fname, data)

        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Realspeech()
    window.show()
    sys.exit(app.exec())
