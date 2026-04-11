from PyQt6.QtWidgets import QWidget, QSlider, QDoubleSpinBox, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal


class FloatSlider(QWidget):
    changed = pyqtSignal(float)

    def __init__(self, minv, maxv, step=0.01, value=0.0, parent=None):
        super().__init__(parent)

        self._scale = int(round(1.0 / step))
        self._min = minv
        self._max = maxv

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(
            int(minv * self._scale),
            int(maxv * self._scale),
        )
        self.slider.setValue(int(value * self._scale))

        self.spin = QDoubleSpinBox()
        self.spin.setRange(minv, maxv)
        self.spin.setSingleStep(step)
        self.spin.setValue(value)
        self.spin.setKeyboardTracking(True)

        self.slider.valueChanged.connect(self._from_slider)
        self.spin.valueChanged.connect(self._from_spin)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.slider)
        lay.addWidget(self.spin)

    def _from_slider(self, v):
        val = v / self._scale
        self.spin.blockSignals(True)
        self.spin.setValue(val)
        self.spin.blockSignals(False)
        self.changed.emit(val)

    def _from_spin(self, v):
        val = v * self._scale 
        self.slider.blockSignals(True)
        self.slider.setValue(int(val))
        self.slider.blockSignals(False)
        self.changed.emit(v)

    def value(self) -> float:
        return self.spin.value() 
    
    def setFloatValue(self, v: float):
        #iv = int((v - self._min) / (self._max - self._min) * self._scale)
        self.slider.blockSignals(True)
        self.slider.setValue(int(v * self._scale))
        self.slider.blockSignals(False)
        self.spin.blockSignals(True)
        self.spin.setValue(v)
        self.spin.blockSignals(False)

    def floatValue(self) -> float:
        return self._min + (self.value() / self._scale) * (self._max - self._min)
    