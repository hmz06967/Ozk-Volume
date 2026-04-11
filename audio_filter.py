import numpy as np
import sounddevice as sd
from scipy.signal import butter, filtfilt
import threading
import time
import queue

class AudioFilter:
    """
    Gerçek zamanlı ses işleme sınıfı.
    
    Özellikler:
    - Ses genliği yükseltme (gain)
    - Bant Geçiren Filtre (BPF) – belirli frekans aralığını korur
    - Düşük Sınır Filtresi (LPF) – yüksek frekansları kaldırır
    
    Kullanım:
    filter = AudioFilter(gain=1.0, bpf_low=1000, bpf_high=3000, lpf_cutoff=5000)
    filter.start()  # Gerçek zamanlı işlemi başlat
    """
    
    def __init__(
        self,
        gain_db: float = 1.0,       # Genlik artışı (dB), örneğin +10 dB → 10
        bpf_low: float = 200,         # BPF alt sınırı Hz
        bpf_high: float = 7000,        # BPF üst sınırı Hz
        lpf_cutoff: float = 5000,      # LPF kesim frekansı Hz
        sample_rate: int = 16000,   # Örnek hızı (Hz)
        buffer_size: int = 256      # Her seferde kaç örnek alacak?
    ):
        self.gain_db = gain_db
        self.bpf_low = bpf_low
        self.bpf_high = bpf_high
        self.lpf_cutoff = lpf_cutoff
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        
        # Genlik artırma (dB'den lineara çevir)
        self.gain_linear = 10 ** (gain_db / 20) if gain_db != 0 else 1.0

        # Filtre parametreleri
        self._init_filters()

        print("✅ Gerçek zamanlı ses işleme başlatıldı...")
        print(f"• Genlik: {self.gain_db} dB (x{self.gain_linear:.3f})")
        print(f"• BPF: {self.bpf_low}-{self.bpf_high} Hz")
        print(f"• LPF: {self.lpf_cutoff} Hz")

    def _init_filters(self):
        """Filtre parametrelerini hesapla ve depola"""
        nyquist = 0.5 * self.sample_rate
        
        # BPF (Butterworth 4. derece)
        if self.bpf_low > 0 and self.bpf_high > 0:
            low_norm = self.bpf_low / nyquist
            high_norm = self.bpf_high / nyquist
            self.bpf_b, self.bpf_a = butter(4, [low_norm, high_norm], btype='band', analog=False)
        else:
            # BPF yoksa, filtre atla (kayıt olarak geçer)
            self.bpf_b, self.bpf_a = None, None

        # LPF (Butterworth 4. derece)
        if self.lpf_cutoff > 0:
            cutoff_norm = self.lpf_cutoff / nyquist
            self.lpf_b, self.lpf_a = butter(8, cutoff_norm, btype='high', analog=False)
        else:
            # LPF yoksa atla
            self.lpf_b, self.lpf_a = None, None

    def _apply_gain(self, data):
        """Ses genliği yükseltme"""
        if not isinstance(data, np.ndarray) or len(data.shape) != 1:
            raise ValueError("Girdi sinyal vektörel olmalıdır (1D).")
        
        # Genlik artırma
        return data * self.gain_linear

    def _apply_bpf(self, data):
        if self.bpf_b is None or self.bpf_a is None:
            return data  # BPF yoksa sinyali döndür
        try:
            filtered = filtfilt(self.bpf_b, self.bpf_a, data)
            return np.clip(filtered, -1.0, 1.0)  # Genlik sınırları (16-bit için uygun)
        except Exception as e:
            print(f"BPF hatası: {e}")
            return data

    def _apply_lpf(self, data):
        """Düşük Sınırlı Filtre (Low-Pass Filter)"""
        if self.lpf_b is None or self.lpf_a is None:
            return data  # LPF yoksa sinyali döndür
        try:
            filtered = filtfilt(self.lpf_b, self.lpf_a, data)
            return np.clip(filtered, -1.0, 1.0)  # Genlik sınırları
        except Exception as e:
            print(f"LPF hatası: {e}")
            return data

    def _process_chunk(self, chunk):
        """Bir saniyedeki ses bloğunu işlemek"""
        # Gain → BPF → LPF sırasıyla uygula
        processed = self._apply_gain(chunk)
        processed = self._apply_bpf(processed)
        # processed = self._apply_lpf(processed)

        return processed

    def proccess(self, raw_data, callback=None):
        
        self.buffer_size = len(raw_data)

        try:
            processed_data = self._process_chunk(raw_data)
            return np.array(processed_data, dtype=np.float32)
        except Exception as e:
            print(f"Filter error: {e}")
            pass
        return raw_data