from core import *  

class IconButton(QWidget):
    play = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        

    def colorize_icon(path, color):
        pixmap = QPixmap(path)
        painter = QPainter(pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(pixmap.rect(), QColor(color))
        painter.end()
        return QIcon(pixmap)

    def set_play_button(self):
        self.play_button = QPushButton()
        self.pause_icon_path = "img/pause.png"
        self.play_icon_path = "img/play.png"

        # İkonu renklendir
        play_icon = colorize_icon(self.play_icon_path, "#00AAFF")  # mavi ton
        self.play_button.setIcon(play_icon)

        # Boyut ayarı
        self.play_button.setIconSize(QSize(48, 48))   # ikon boyutu
        self.play_button.setFixedSize(72, 72)         # buton boyutu

        self.play_button.setToolTip("Oynat")
        self.play_button.clicked.connect(self.play_action)
