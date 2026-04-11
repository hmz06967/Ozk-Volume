import pyaudiowpatch as pyaudio

# === Ayarlar ===
CHUNK_SIZE = 4096

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
