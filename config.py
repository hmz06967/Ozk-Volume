from core import *

from audio_settings import AudioConfig
from view_settings import ViewConfig
from speech_settings import SpeechConfig

class Config:
    def __init__(self):
        pass

    def default(self):
        audio = AudioConfig()
        view = ViewConfig()
        speech = SpeechConfig()

        return {
            "audio": audio.config,
            "view": view.config,
            "speech": speech.config,
            # "translate": translate.config
        }
 
    def load_config(self, filename="config.json"):
        config = self.default()

        if not os.path.exists(filename):
            logging.warning(f"⚠️  {filename} bulunamadı. Yeni bir dosya oluşturulacak.")
            self.save_config(config)
            return config

        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logging.info(f"✅ Yapılandırma başarıyla {filename} dosyasından yüklenmiştir.")
            return data
        except Exception as e:
            return config

    def save_config(self, data, filename="config.json"):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            logging.info(f"✅ Yapılandırma başarıyla {filename} dosyasına kaydedildi.")
        except Exception as e:
            logging.error(f"config: {e}")
            