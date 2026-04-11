import sys
import importlib
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QEvent
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PyQt6.QtGui import QAction

from pathlib import Path
import time

# İzleyeceğimiz dosya
MODULE_NAME = "realspech"
MODULE_PATH = f".py"

# Modülü ilk kez yükle
module = importlib.import_module(MODULE_NAME)

class FileWatcher(QThread):
    file_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.observer = Observer()
 
    def run(self):
        event_handler = FileChangeHandler(self)
        self.observer.schedule(event_handler, path='.', recursive=True)
        self.observer.start()
        self.exec()  # QThread event loop

    def stop(self):
        self.observer.stop()
        self.observer.join() 
        self.quit()

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, watcher):
        self.watcher = watcher
        self.last_event_time = 0          
        self.debounce_delay = 0.5         

    def on_modified(self, event):
        current_time = time.time()        
        if current_time - self.last_event_time < self.debounce_delay:  
            return                                              
        
        self.last_event_time = current_time                            

        if event.src_path.endswith('.png.0.pdnSave'):
            p = Path(event.src_path)
            print(f"\n{p.name} değişti! Yeniden yükleniyor...")
            self.watcher.file_changed.emit()

        if event.src_path.endswith('.py'):
            p = Path(event.src_path)
            print(f"\n{p.name} değişti! Yeniden yükleniyor...")
            self.watcher.file_changed.emit()

class DynamicMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.resize(700, 400)
 
        # Merkezi widget ve layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(10, 10, 10, 10)

        # İlk GUI çizimi
        self.reload_gui()

        # Dosya izleyiciyi başlat
        self.watcher = FileWatcher()
        self.watcher.file_changed.connect(self.reload_module)
        self.watcher.start()

    def enterEvent(self, event: QEvent):
        if hasattr(self, "new_ui"):
            self.new_ui.enterEvent(event)

    def leaveEvent(self, event):
        if hasattr(self, "new_ui"):
            self.new_ui.leaveEvent(event)

    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def reload_module(self):
        try:
            global module
            importlib.reload(importlib.import_module("speech_worker"))
            importlib.reload(importlib.import_module("audio_worker"))

            importlib.reload(module)
            print("Modül yeniden yüklendi.")
            self.reload_gui()
        except Exception as e:
            self.show_error(f"Modül yüklenirken hata: {e}")

    def reload_gui(self):

        try:
            if hasattr(module, "Realspeech"):

                # reload sonrası
                if hasattr(self, "new_ui"):


                    """if hasattr(self.new_ui, "uart_worker") and self.new_ui.uart_worker is not None:
                        self.new_ui.uart_worker.stop()
                    if hasattr(self.new_ui, "uart_thread") and self.new_ui.uart_thread is not None:
                        self.new_ui.uart_thread.quit()"""
                     
                # Yeni arayüzü oluştur ve mevcut pencereye ata
                self.new_ui = module.Realspeech()
                self.new_ui.btn_min.clicked.connect(self.showMinimized)
                self.new_ui.btn_max.clicked.connect(self.toggle_maximize)
                self.new_ui.btn_close.clicked.connect(self.close)
                
                self.setCentralWidget(self.new_ui.centralWidget())
                if hasattr(self.new_ui, "status"):
                    self.setStatusBar(self.new_ui.status)
                self.setWindowTitle("♻️ Yenilendi")
                print("✅ GUI içerik yenilendi (soft reload).")

        except Exception as e:
            print("❌ Rebuild hatası:", e)

    def show_error(self, message):
        label = QLabel(message)
        label.setStyleSheet("color: red; font-weight: bold;")
        self.layout.addWidget(label)

    def closeEvent(self, event):
        self.watcher.stop()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DynamicMainWindow()
    window.show()
    sys.exit(app.exec())