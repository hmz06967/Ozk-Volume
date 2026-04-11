from core import *

from audio_worker import AudioWorker
from subtitle import SubtitleProcessor
from audio_filter import AudioFilter

logging.getLogger("faster_whisper").setLevel(logging.ERROR)

class SpeechStatus(Enum):
    LOAD = 0
    RELOAD = 5
    STARTED = 1
    PAUSED = 2
    STOP = 6
    WARNING = 3
    ERROR = 4
    WAIT = 7

class AudioSpeechWorker(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str)
    log = pyqtSignal(int, str)
    text = pyqtSignal(str, str)
    status = pyqtSignal(SpeechStatus)

    def __init__(self):
        super().__init__()

        from config import Config

        self._running = False
        self._stream = None
        self.audio_q = queue.Queue()
        self.status_mode = SpeechStatus.LOAD
        self.is_save = False
        self.is_filter = True
        self.supported = ["wav", "mp3", "flac", "ogg", "aac"]
        self.frames = []

        self.subtitle_api = SubtitleProcessor()

        self.audio_thread = QThread()
        self.audio_worker = AudioWorker()
        self.audio_worker.moveToThread(self.audio_thread)
        self.audio_thread.started.connect(self.audio_worker.run)
        self.audio_worker.log.connect(lambda: self._log)

        self.config_load()

        self.cache_dir = os.path.expanduser("~/.cache/whisper")
        os.makedirs(self.cache_dir, exist_ok=True)

    def _log(self, int, text:str):
        self.log.emit(int, text)

    def bclear(self):
        self.buffer = np.array([], dtype=np.float32)

    def resample_audio(self, data, target_rate=16000):
        """
        Verilen ses verisini hedef örneklemeye (16kHz) dönüştür.
        """

        x = np.array(data, dtype=np.float32)
        y = librosa.resample(x, orig_sr=self.audio_worker._rate, target_sr=target_rate)  # Örneğin 48kHz'den 16kHz'e

        return np.frombuffer(y, dtype=np.float32)

    def config_load(self):
        self.config = Config().load_config()
        self.config_speech = self.config.get("speech")
        self.language = self.config_speech.get("lgcode")
        self.speech_api = self.config_speech.get("api")
        self.model_size = self.config_speech.get("size")
        self.chunk_size = self.config_speech.get("chunksize")
        self.beam_size = self.config_speech.get("beamsize")
        self.vad_filter = self.config_speech.get("vadfilter")
        self.auto_lang = self.config_speech.get("autolang")
        
    def set_status(self, status):
        self.status_mode = status 
        self.status.emit(self.status_mode)

    def api_ready(self, apiname):
        if self.speech_api == apiname:
            if self.model is None:
                return False
            return True
        else:
            return False
    
    def save_audio(self):
        wf = wave.open("output.wav", "wb")
        wf.setnchannels(1)
        wf.setsampwidth(self.audio_worker._p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(16000) #self.audio_worker._rate)
        wf.writeframes(b"".join(self.frames))
        wf.close()

    @pyqtSlot()
    def vosk_speech(self):
        rec = KaldiRecognizer(self.model, 16000)
        text = ""

        data = (self.buffer * 32767).astype(np.int16).tobytes()
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            text = result["text"]
        else:
            partial = json.loads(rec.PartialResult())
            text = partial["partial"]
        
        if text != "":
            start_time = ""
            end_time = ""
            self.subtitle_api.add_subtitle(start_time, end_time, text, self.language)
            line = f"# {start_time} --> {end_time} : {text}"
            self.text.emit(line, text)
            
    @pyqtSlot()
    def whisper_speech(self):
    
            segments, info = self.model.transcribe(
                self.buffer,
                language=self.language,
                beam_size=self.beam_size,
                vad_filter=self.vad_filter,
                vad_parameters=dict(min_silence_duration_ms=100),
            )

            #print(self.language)
            #logging.info(f"Tespit edilen dil: {info.language}")
            #logging.info(f"Dil olasılığı: {info.language_probability}")

            self.set_title_segment(segments, info)

                # print("[%s -> %s] %s" % (start_time, end_time, segment.text))
                # print(self.subtitle_api.get_all_subtitles())
                # print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
            
        #recorder.feed_audio(audio_float)
        #print("Transcription: ", recorder.text())

    @pyqtSlot()
    def run(self):
        from faster_whisper import WhisperModel
        logger.info("[Speech Worker] başladı..")
        
        self.set_status(SpeechStatus.LOAD)
        self._running = True

        try:
            while self._running:

                while self.status_mode == SpeechStatus.WAIT:
                    self.text.emit("loading..")
                    time.sleep(0.1)

                if self.status_mode == SpeechStatus.LOAD or self.status_mode == SpeechStatus.RELOAD:
                    self.config_load()
                    if self.speech_api == "faster_whisper":
                        self.model = WhisperModel(
                            self.model_size, 
                            device="cuda", 
                            compute_type="float32",
                        )
                    elif self.speech_api == "vosk":
                        from vosk import Model, KaldiRecognizer
                        self.model = Model(lang=self.language)
                    
                    logging.info("Selected speech-api-> %s", self.speech_api)

                    self.audio_start()

                    # self.audio_filter.buffer_size = self.chunk_size

                data = self.audio_worker.audio_q.get()
                if data is not None:

                    if self.is_filter:
                        self.audio_filter.sample_rate = self.audio_worker._rate
                        # self.audio_filter.max_freq = self.audio_maxf
                        # self.audio_filter.min_freq = self.audio_maxf

                        data = self.audio_filter.proccess(data)
        
                    y = self.resample_audio(data)

                    if self.is_save:
                        self.frames.append((y * 32767).astype(np.int16).tobytes())

                    self.buffer = np.concatenate((self.buffer, y))
                    
                    if len(self.buffer) >= 16000 * self.chunk_size:
                        if self.api_ready("faster_whisper"):
                            self.whisper_speech()
                        elif self.api_ready("vosk"):
                            self.vosk_speech()
                        self.bclear()

                else:
                    time.sleep(0.001)

        except Exception as e:
            logging.error(f"Speech error: {e}")
            self.set_status(SpeechStatus.ERROR)
            pass

        self.stop()
  
    def audio_start(self):

        if not self.audio_thread.isRunning():
            logging.info("Starting audio thread.")
            self.audio_thread.start()
            time.sleep(0.1)

        self.is_filter = self.audio_worker.audio.get("onfilter")
        self.audio_minf = self.audio_worker.audio.get("maxfreq")
        self.audio_maxf = self.audio_worker.audio.get("minfreq")
        self.audio_filter = AudioFilter()
        self.bclear()

        self.set_status(SpeechStatus.STARTED)
        

    def audio_stop(self):
        self.set_status(SpeechStatus.PAUSED)
        logging.info("Stoping audio thread")
        self.audio_worker.stop()
        self.audio_thread.quit()
        self.audio_thread.wait()

        if self.is_save:
            self.save_audio()

    @pyqtSlot()
    def stop(self):
        self._running = False
        self.audio_stop()
        self.set_status(SpeechStatus.STOP)
        self.finished.emit()
        logger.info("[Speech Worker] durduruldu..")
        
    def load_from_file(self, file_path):
        from faster_whisper import WhisperModel

        self.config_load()
        
        if not self._running or not hasattr(self, "model"):
            model = WhisperModel(self.model_size, device="cuda", compute_type="float32")
            segments, info = model.transcribe(file_path, beam_size=self.beam_size)
            self.set_title_segment(segments, info, True)
        
        elif self.model:
            segments, info = self.model.transcribe(file_path, beam_size=self.beam_size)
            self.set_title_segment(segments, info, True)

    def set_title_segment(self, segments, info, file = False):
        time = 0
        for segment in segments:
            if file:
                st_time = time + segment.start
                e_time = time + segment.end
                # time = st_time + e_time
                start_time = self.subtitle_api.convert_seconds_to_hms_format(int(st_time))
                end_time = self.subtitle_api.convert_seconds_to_hms_format(int(e_time))
            else:
                end_time = self.subtitle_api.get_live_time(-segment.start) 
                start_time = self.subtitle_api.get_live_time(-(segment.start + segment.end))
            self.subtitle_api.add_subtitle(start_time, end_time, segment.text, info.language)
            line = f"# {start_time} --> {end_time} : {segment.text}"
            self.text.emit(line, segment.text)