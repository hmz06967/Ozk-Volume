from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtWidgets import QWidget

class ResizableWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.margin = 5
        self.resizing = False
        self.resize_edge = None
        self.start_pos = None
        self.start_geom = None
        self.drag_pos = None
        self.mouse_pressed = False
        self.setMouseTracking(True)
        
    def cursorUpdate(self, edge=None):
        return
        
        if edge is None:
            return

        # Cursor update
        if edge in ("left", "right"):
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif edge in ("top", "bottom"):
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        elif edge in ("topleft", "bottomright"):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif edge in ("topright", "bottomleft"):
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def mousePressEvent(self, event):
        
        edge = self.get_edge(event.pos())

        if edge:
            self.resizing = True
            self.resize_edge = edge
            self.start_pos = event.globalPosition().toPoint()
            self.start_geom = self.geometry()
        else:
            self.drag_pos = event.globalPosition().toPoint()
        self.mouse_pressed = True

    def mouseMoveEvent(self, event):
        pos = event.pos()
        edge = self.get_edge(pos)
  
        self.cursorUpdate(edge)
        if self.resizing:
            self.perform_resize(event.globalPosition().toPoint())
            return

        if self.drag_pos:
            delta = event.globalPosition().toPoint() - self.drag_pos
            self.move(self.pos() + delta)
            self.drag_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.resizing = False
        self.drag_pos = None
        self.mouse_pressed = False

    def get_edge(self, pos):
        x, y, w, h = pos.x(), pos.y(), self.width(), self.height()
        
        print(x,y,w,h)

        # Tam kenar çizgisi kontrolü
        if x < 10:
            return "left"
        elif w - x < 20:
            return "right"
        elif y < 10:
            return "top" 
        elif h - y < 20:
            return "bottom"
        else:
            return None

    def perform_resize(self, global_pos):
        diff = global_pos - self.start_pos
        geom = self.start_geom

        x, y, w, h = geom.x(), geom.y(), geom.width(), geom.height()

        if self.resize_edge:
            if "right" in self.resize_edge:
                w += diff.x()
            if "bottom" in self.resize_edge:
                h += diff.y()
            if "left" in self.resize_edge:
                x += diff.x()
                w -= diff.x()
            if "top" in self.resize_edge:
                y += diff.y()
                h -= diff.y()

        # Minimum boyut sınırı
        self.setGeometry(x, y, max(200, w), max(20, h))