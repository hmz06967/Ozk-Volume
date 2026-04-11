import pyaudiowpatch as pyaudio
import numpy as np
import librosa
import librosa.display
import time
import threading
from scipy.signal import spectrogram
import os

import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
import queue

from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer

BUFFER_COUNT = 30            # Son 30 buffer'da frekans analizi için (kaydırmak için)

# === Ayarlar ===
SAMPLE_RATE = 48000          # Ses örnekleme oranı
CHUNK_SIZE = 2048            # Her buffer boyutu (örnek: 50ms)
BUFFER_DURATION = 0.5        # Her döngüdeki süresi (saniye)
THRESHOLD_ENERGY = 100       # Vokal enerji eşik değeri
VOCAL_CONFIDENCE_THRESHOLD = 0.7  # Şarkı olma olasılığı

# === Sınıflandırıcı: Basit "Şarkı mı?" tespiti (MFCC ile) ===
def is_song(buffer, sample_rate):
    """
    Bir buffer'da şarkı var mı? MFCC ve enerji ile kontrol eder.
    """
    # Enerji (sadece ses yoğunluğu)
    energy = np.sum(np.abs(buffer)**2) / len(buffer)
    
    print(energy)

    if energy < THRESHOLD_ENERGY:
        return False  # Sessizlik → şarkı değil

    # MFCC (mel frekansı ile)
    y, sr = librosa.load(buffer, sr=sample_rate, duration=0.5)
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)

    # Ortalama MFCC değerleri
    mfcc_mean = np.mean(mfccs, axis=1).mean()

    # Enerji ve MFCC'ye göre bir olasılık
    confidence = (energy / 200.0) + (mfcc_mean * 0.3)
    return confidence > VOCAL_CONFIDENCE_THRESHOLD

# === Basit Vokal İzolementi: Yüksek frekanslı kısmı alır ===
def isolate_vocal(buffer, sample_rate):
    """
    Sadece yüksek frekanslı (vokal) kısmını çıkarır.
    Gerçek vokal izolasyonu için bu basit bir yöntemdir.
    (Geliştirilmiş: DNN ile yapılabilir ama hızlı ve basit)
    """
    y, sr = librosa.load(buffer, sr=sample_rate)

    # Spektrumda orta-uyarı frekansları seç
    # 500 Hz - 4000 Hz arası yüksek enerjili bölgeleri al
    D = np.abs(librosa.stft(y))
    
    # Sadece 500-4000 Hz aralığında olan frekansları seç
    freqs = librosa.fft_frequencies(sr=sr)
    mask = (freqs >= 500) & (freqs <= 4000)

    D_masked = D.copy()
    for i in range(D.shape[1]):
        if np.any(mask):
            # Bu frekansları seç
            freq_idx = np.where(freqs >= 500)[0]
            D_masked[:, i] = D[:, i] * (np.sum(np.abs(freqs[freq_idx])) / len(freqs))
    
    # Geri dönüştür
    vocal_audio = librosa.istft(D_masked, sr=sample_rate)
    
    return vocal_audio

def get_stream(device):
    p = pyaudio.PyAudio()

    speakers = p.get_device_info_by_index(device) #p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])
    loopback_device = p.get_loopback_device_info_generator()
    loop_dev = None
    for d in loopback_device:
        # default output adına benzer olan loopback'i seç
        if speakers["name"] in d["name"]:
            loop_dev = d
            break

    if loop_dev is None:
        raise RuntimeError("Loopback device bulunamadı. Ses cihazı adını kontrol et.")

    print(f"Default Speakers : {speakers["name"]}")
    print(f"Loopback Device : {loop_dev["name"]}")

    sample_rate = int(loop_dev["defaultSampleRate"])
    dev_index = loop_dev["index"]
    
    return p.open(
        input_device_index=dev_index, 
        format=pyaudio.paFloat32,
        channels=1,
        rate=sample_rate,
        input=True,
        frames_per_buffer=CHUNK_SIZE,
        stream_callback=None  # Gerçek zamanlı, callback ile çalışır
    ), p, sample_rate


# === Gerçek zamanlı ses akışı ===
def audio_stream(device):
    stream, p, sample_rate = get_stream(device)

    print("Ses akışı başlatıldı. Her 0.5 saniyede bir analiz ediliyor...")
    
    try:
        while True:
            # Buffer oluştur (örneğin 2048 örnek)
            raw_data = np.frombuffer(stream.read(CHUNK_SIZE), dtype=np.float32)
            
            # Şarkı mı?
            if is_song(raw_data, sample_rate):
                print("✅ Şarkı tespit edildi! Vokal izole ediliyor...")
                
                # Sadece vokal çıkar (basit yöntemle)
                vocal_output = isolate_vocal(raw_data.tobytes(), SAMPLE_RATE)

                # Vokal çıktısını kaydet (veya ses alıcıya gönder)
                # Örneğin: wav dosyasına kaydet
                output_path = f"vocal_{int(time.time())}.wav"
                librosa.output.write_wav(output_path, vocal_output, SAMPLE_RATE)
                
                print(f"🎤 Vokal kaydedildi: {output_path}")
            else:
                pass
           
    except KeyboardInterrupt:
        print("\nUygulama kapatılıyor...")
    
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

# Frekans ağırlıklarını hesaplayacak fonksiyon
def compute_frequency_weights(buffer, sample_rate):
    n_fft = CHUNK_SIZE
    fft_spectrum = np.abs(fft(buffer[:n_fft]))
    
    # Sadece pozitif frekanslar (0–half rate)
    freqs = fftfreq(n_fft, 1/sample_rate)[:n_fft//2]
    
    # Toplam enerji
    total_energy = np.sum(fft_spectrum)
    
    if total_energy == 0:
        return np.zeros(len(freqs)), 0.0
    
    # Her frekans için ağırlık (amplitude / toplam enerji) → 0–1 arası
    weights = fft_spectrum / total_energy
    
    # Sadece 25 Hz’den 1800 Hz’ye kadar olanları değerlendir
    min_freq, max_freq = 25, 1800
    valid_idx = (freqs >= min_freq) & (freqs <= max_freq)
    
    weights_valid = weights[:n_fft//2]  # 1024 → önce 512'ye dönmüş oluyor (doğru)
    total_weight = np.sum(weights_valid[valid_idx])  # sadece valid frekanslara ait ağırlık toplamı

    return freqs, weights_valid, total_weight

# Gerçek zamanlı ses akışı ve grafikleme fonksiyonu
def live_frequency_analysis(device):
    
    stream, p, sample_rate = get_stream(device)


    # Grafik penceresi oluştur
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.set_title("Gerçek Zamanlı Frekans Grafiği (Müzik Tespiti)")
    ax.set_xlabel("Frekans (Hz)")
    ax.set_ylabel("Ağırlık")
    ax.grid(True)

    # Grafik güncellenmesi için çizim thread'i başlat
    plt.ion()  # Interaktif mod
    
    # Buffer tutucu – son 30 frekans değeri saklanacak
    buffer_weights = []
    
    print("🎤 Ses akışı başladı... Sıkıştırma (q'ya basarak durdur)")
    
    timeron = True

    try:
        while True:
            # Ses al
            raw_data = np.frombuffer(stream.read(CHUNK_SIZE), dtype=np.float32)
            
            # Frekans ağırlıklarını hesapla
            freqs, weights, total_weight = compute_frequency_weights(raw_data, sample_rate)

            # Sadece geçerli frekansları göster (valid)
            valid_freqs = freqs[weights > 0] if len(weights) > 0 else []
            valid_weights = weights[weights > 0]
            
            # Son 30 buffer’da toplam ağırlık için bir istatistik
            buffer_weights.append(total_weight)
            
            # Buffer’ı sınırla (son 30 veriyi göster)
            if len(buffer_weights) > BUFFER_COUNT:
                buffer_weights.pop(0)

            def update_chart():
                ax.clear()
                ax.set_title(f"Frekans Grafiği | Toplam Ağırlık: {total_weight:.4f} (Müzik?)")
                
                if len(valid_freqs) > 0:
                    ax.bar(valid_freqs, valid_weights, width=15, color='blue', alpha=0.7)
                
                ax.set_xlabel("Frekans (Hz)")
                ax.set_ylabel("Ağırlık")
                ax.grid(True, linestyle="--", alpha=0.6)

                plt.draw()
                plt.pause(0.1)  # Grafik güncelleme hızı (daha hızlı olursa gecikir)
                
            update_chart()

            if not timeron:
                timeron = False
                timer = QTimer()
                timer.timeout.connect(update_chart)
                timer.start(100)  # Her 100 ms'de bir

            # Müzik mi? → ağırlık ≥ 0.5 ise "Müzik"
            if total_weight >= 0.5:
                print(f"🎵 MÜZİK TESPİTİ: Ağırlık = {total_weight:.4f} (≥0.5)")
            else:
                print(f"🎤 VOKAL/ODAKLANMA: Ağırlık = {total_weight:.4f} (<0.5)")

    except KeyboardInterrupt:
        print("\n🛑 Ses akışı durduruldu.")
        
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

# === Başlat ===
if __name__ == "__main__":
    
    live_frequency_analysis(3)
    # audio_stream(3)
