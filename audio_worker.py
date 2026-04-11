
from core import *

class AudioWorker(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str)
    log = pyqtSignal(int, str)

    CHANNELS = 1
    BLOCK = 1024
    RATE = 48000

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self._running = False
        self.audio_q = queue.Queue() # maxsize=self.AUDIO_Q_MAX
        self._stream = None
        self._p = None
        self.input = False
        self._rate = 48000

        #self.rate = parent.io.get("fft_size")

    # --- VU Audio Stream ---
    def start_stream(self):

        self.config = Config().load_config()
        self.audio = self.config.get("audio")

        self._running = True
        # self.dev_search()

        mode = self.audio.get("mode", 0)
        input_dev = self.audio.get("input")
        output_dev = self.audio.get("output")

        # logging.info(f"selected: {mode}")
        # print(self.io.get("io_mode", ""), self.default_in, self.default_out)

        if mode == 0:
            # print("input cihazı başlıyor..", self.default_in)
            self._stream = self.input_audio(input_dev)
            self.input = True
        elif mode == 1:
            # print("output cihazı başlıyor..", self.default_out)
            self._stream, self._p = self.loop_back_stream(output_dev)
            self.input = False
        return self._stream

    def dev_search(self):

        try:
            devices = sd.query_devices()
            self.default_in, self.default_out = sd.default.device  # index veya None
        except Exception as e:
            return

        for idx, d in enumerate(devices):
            name = d.get("name", f"Device {idx}")
            if idx == self.audio.get("input"):
                self.default_in = idx
            elif idx == self.audio.get("output"):
                self.default_out = idx

    def input_audio(self, device):
        self._rate = 48000
        stream = sd.InputStream(
            device=device, 
            channels=self.CHANNELS, 
            samplerate=self._rate, 
            blocksize=self.audio.get("fftsize"), 
            dtype="float32", 
            callback=self.callback
        )
        return stream

    def loop_back_stream(self, device):
        # --- WASAPI loopback stream aç ---

        _p = pyaudio.PyAudio()
        # Varsayılan hoparlör (render) cihazını bulup loopback ile açıyoruz
        #wasapi_info["defaultOutputDevice"]
        #self.default_dev = wasapi_info["defaultOutputDevice"]
        #wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
        speakers = _p.get_device_info_by_index(device) #p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])
        loopback_device = _p.get_loopback_device_info_generator()
        loop_dev = None

        for d in loopback_device:
            if speakers["name"] in d["name"]:
                loop_dev = d
                break

        if loop_dev is None:
            logging.error("Loopback device bulunamadı. Ses cihazı adını kontrol et.")

        logging.info(f"Default Speakers : {speakers["name"]}")
        logging.info(f"Loopback Device : {loop_dev["name"]}")

        sample_rate = int(loop_dev["defaultSampleRate"])
        dev_index = loop_dev["index"]
        
        self._p = _p
        self._rate = sample_rate
        self.dev = loop_dev
        
        stream = _p.open(
            format=pyaudio.paFloat32,
            channels=self.CHANNELS,
            rate=sample_rate,
            input=True,
            input_device_index=dev_index,
            frames_per_buffer= self.audio.get("fftsize"),
            stream_callback=self.callback
        )

        return stream, _p

    @pyqtSlot()
    def run(self):

        try:
            self.start_stream()
        except Exception as e:
            logging.error(e)
            return

        if self._stream:
            logging.info("[Audio Worker] başladı..")
            with self._stream:
                while self._running:
                    time.sleep(0.1)
                        
        self.finished.emit()
        logging.info("[Audio Worker] durduruldu..")

    @pyqtSlot()
    def stop(self):
        self._running = False

    def put(self, q: queue.Queue, item):
        try:
            q.put(item)
        except Exception as e:
            pass

        """Queue doluysa en eskiyi at, yeniyi koy."""
        """try:
            q.put_nowait(item)
        except queue.Full:
            try:
                q.get_nowait()
            except queue.Empty:
                pass
            try:
                q.put_nowait(item)
            except queue.Full:
                pass"""

    def callback(self, in_data, frame_count, time_info, flag): 
        x = np.frombuffer(in_data, dtype=np.float32)
        self.put(self.audio_q, x)
        return (in_data, flag)
    