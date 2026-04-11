import json
from typing import List, Dict, Tuple
import datetime
import os 
import re

class SubtitleProcessor:

    def __init__(self):
        self.supported = [".txt", ".ass", ".webvtt", ".srt"]
        self.subtitles: List[Dict[str, str]] = []  # Her alt yazı için start, end, title

    def add_subtitle(self, start: str, end: str, title: str, lang: str = "auto") -> None:
        """Bir alt yazıyı ekle."""
        subtitle = {
            "start": start.strip(),
            "end": end.strip(),
            "title": title.strip(),
            "lang": lang.strip()
        }
        self.subtitles.append(subtitle)

    def convert_seconds_to_hms_format(self, seconds):
        # Saat hesaplaması
        hours = seconds // 3600
        # Kalan saniyeyi dakikaya çevir
        remaining_after_hours = seconds % 3600
        minutes = remaining_after_hours // 60
        seconds_remaining = remaining_after_hours % 60
        
        # İki basamaklı sıfırlama (01, 02, ..., 09, 10 vs.)
        hours_str = f"{hours:02d}"
        minutes_str = f"{minutes:02d}"
        secs_str = f"{seconds_remaining:02d}"
        
        return f"{hours_str}:{minutes_str}:{secs_str}"

    def get_live_time(self, start_s = 0.0):
        current_time = datetime.datetime.now()  # Gerçek saat-saniye-milisaniye
        future_time = current_time + datetime.timedelta(seconds=start_s)
        microseconds_str = future_time.strftime("%f")
        milliseconds_raw = int(int(microseconds_str) / 1000.0)
        milliseconds = f"{milliseconds_raw:03d}"
        live_timestamp = future_time.strftime("%H:%M:%S") + "," + milliseconds
        return live_timestamp

    def get_all_subtitles(self) -> List[Dict[str, str]]:
        """Tüm alt yazıları listeye çevirir."""
        return self.subtitles

    def to_json_string(self) -> str:
        """Her bir alt yazıyı JSON formatında döndür (string olarak)."""
        return json.dumps(self.get_all_subtitles(), ensure_ascii=False, indent=4)

    def to_json_file(self, filename: str) -> None:
        """JSON dosyasına kaydeder."""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.get_all_subinois(), f, ensure_ascii=False, indent=4)
    
    def to_dict_tuple_list(self) -> List[Tuple[str, str, str]]:
        """Her alt yazıyı (start, end, title) üçlü bir tuple olarak döndür."""
        return [(s["start"], s["end"], s["title"]) for s in self.get_all_subtitles()]

    def format_subtitles_to_hash(self):
        formatted_lines = []
        for start_time, end_time, title in self.to_dict_tuple_list():
            line = f"# {start_time} --> {end_time} : {title}"
            formatted_lines.append(line)
        return "\n".join(formatted_lines)

    def to_srt_data(self) -> Dict[str, str]:
        """SRT formatına çevirir. Her bir alt yazı SRT formatında olur."""
        srt_lines = []
        index = 1
        
        for subtitle in self.subtitles:
            start_time = subtitle["start"]
            end_time = subtitle["end"]
            title = subtitle["title"]

            # Format: "00:00:01,12" → 1 saat 1 dakika 1 saniye 12 milisaniye
            # SRT formatı: numara, zaman aralığı, metin
            srt_lines.append(f"{index}")
            srt_lines.append(f"{start_time} --> {end_time}")
            srt_lines.append(f"{title}")
            srt_lines.append("")  # Boş satır (alt satır)
            index += 1

        return srt_lines

    def to_webvtt_data(self) -> Dict[str, str]:
        """WebVTT formatına çevirir. Tarayıcılarda doğrudan çalışır."""
        webvtt_lines = []
        index = 1

        webvtt_lines.append("WEBVTT\n")

        for subtitle in self.subtitles:
            start_time = subtitle["start"]
            end_time = subtitle["end"]
            title = subtitle["title"]

            # WebVTT: 00:00:05.12 --> 00:00:10.45
            webvtt_lines.append(f"{start_time} --> {end_time}")
            webvtt_lines.append(f"{title}")
            webvtt_lines.append("")  # Boş satır

        return webvtt_lines

    def to_ass_data(self) -> Dict[str, str]:
        """ASS formatına çevirir (font, renk, animasyon gibi özellikleri içermez ama yapısal olarak geçerli olur)."""
        # ASS formatı genel yapısı:
        # [Script Info]
        # ; Format: WebVTT
        # Title: Alt Yazılar
        # ScriptType: v4.00+
        # PlayResX: 1920
        # PlayResY: 1080
        # 
        # [V4+ Styles]
        # Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, Outline, Back, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, OutlineColor, Alignment, MarginL, MarginR, MarginV, Encoding
        # Style: Default,Arial,20,&H00FFFFFF,&H000000FF,&H00000000,0,0,0,0,0,100,100,0,0,1,65535,2,10,10,10,1
        #
        # [Events]
        # Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
        # Dialogue: 0,0:00:00.00,0:00:05.12,Default,,0,0,0,,{title}

        ass_content = """[Script Info]
            ; Format: WebVTT
            Title: Alt Yazılar
            ScriptType: v4.00+
            PlayResX: 1920
            PlayResY: 1080

            [V4+ Styles]
            Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, Outline, Back, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, OutlineColor, Alignment, MarginL, MarginR, MarginV, Encoding
            Style: Default,Arial,20,&H00FFFFFF,&H000000FF,&H00000000,0,0,0,0,0,100,100,0,0,1,65535,2,10,10,10,1

            [Events]
            """

        for idx, subtitle in enumerate(self.subtitles):
            start = subtitle["start"]
            end = subtitle["end"]
            title = subtitle["title"]

            # ASS formatı: "Dialogue: 0,0:00:05.12,0:00:08.34,Default,,0,0,0,,{title}"
            event_line = f"Dialogue: 0,{start},{end},Default,,0,0,0,,{title}"
            ass_content += f"{event_line}\n"

        return ass_content

    def to_txt_data(self, addtime):
        data = ""
        formatted_lines = []
        if addtime:
            data = self.format_subtitles_to_hash()
        else:
            for start_time, end_time, title in self.to_dict_tuple_list():
                line = f"# {start_time} --> {end_time} : {title}"
                formatted_lines.append(line)
            data = "\n".join(formatted_lines)
        return data
            
    def to_all_formats(self) -> Dict[str, Dict[str, str]]:
        """Tüm formatları bir dictionary içinde döndür (JSON uyumlu)."""
        return {
            "srt": self.to_srt_data(),
            "webvtt": self.to_webvtt_data(),
            "ass": self.to_ass_data()
        }

    def save_with_format(self, format_name, addtime=True):

        if not format_name:
            return False # Kullanıcı iptal etti

        # Uzantıyı çıkar ve dosya uzantısına göre format belirle
        file_ext = os.path.splitext(format_name)[1].lower()
   
        selected_format = None
        if file_ext in self.supported:
            selected_format = os.path.splitext(format_name)[1].lower()[1:]
        else:
            # Eğer uzantı yoksa, kullanıcıya format seçmesi için klasik bir pencere açılır.
            # Ama burada sadece desteklenenleri gösteriyoruz, kullanıcının seçimini kontrol et
            if not any(format_name.endswith(f) for f in self.supported):
                format_name = format_name + ".srt"  # varsayılan olarak SRT yap
                selected_format = "srt"

        # Format seçildiğinde, doğru veriyi döndür
        if selected_format == "srt":
            data = self.to_srt_data()
            with open(format_name, 'w', encoding='utf-8') as f:
                for line in data:
                    f.write(line + '\n')
            print("SRT kaydedildi.")
        
        elif selected_format == "webvtt":
            data = self.to_webvtt_data()
            with open(format_name, 'w', encoding='utf-8') as f:
                for line in data:
                    f.write(line + '\n')
            print("WebVTT kaydedildi.")
        
        elif selected_format == "ass":
            data = self.to_ass_data()
            with open(format_name, 'w', encoding='utf-8') as f:
                f.write(data + '\n')
            print("ASS kaydedildi.")

        elif selected_format == "txt":
            data = self.to_txt_data(addtime)
            with open(format_name, 'w', encoding='utf-8') as f:
                f.write(data + '\n')
            print("TXT kaydedildi.")
        
        return True

    def load_from_file(self, file_path):
        """
        Belirtilen dosyayı okuyup, desteklenen formatlara göre metinleri yükle.
        Desteklenen formatlar: txt, ass, webvtt, srt
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Dosya bulunamadı: {file_path}")

        file_ext = os.path.splitext(file_path)[1].lower()

        if file_ext not in self.supported:
            logging.error(f"Desteklenmeyen dosya formatı: {file_ext}. Desteklenen formatlar: {self.supported}")
            return -1

        file_ext = file_ext[1:]  # . kaldırılır (örneğin ".txt" -> "txt")

        content = []
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        self.subtitles.clear()

        if file_ext == "txt":

            for line in lines:

                if not line:
                    continue  # Boş satırlar atla

                # Zaman dilimi olup olmadığını kontrol et (örneğin: 01:23:45,678 --> 01:24:00,123)
                time_pattern = r'\#(\s*)(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})\s*[: ](.+)'
                title_match = re.search(time_pattern, line)

                if title_match:
                    start_time = title_match.group(2)
                    end_time = title_match.group(3)
                    title = title_match.group(4).strip()
                    content.append(title)
                    self.add_subtitle(start_time, end_time, title)
                else:
                    # Zaman yoksa: sadece metin
                    # Ama satır bir başlık veya metin olabilir (örneğin "Başlık\nMetin")
                    # Bu durumda, tüm metni tek bir text olarak al
                    parts = line.split('\n')
                    for part in parts:
                        if not part.strip():
                            continue
                        title = part.strip()
                        content.append(title)
                        self.add_subtitle("", "", title)

        elif file_ext == "ass":
            # ASS dosyası, çok karmaşık ama genelde başlık ve metinler içerir.
            # Sadece metin bloklarını al (örneğin: {\\an1}Metin)
            content = []
            in_text_block = False
            for line in lines:
                line = line.strip()
                if line.startswith("Dialogue") and not line.startswith("Dialogue:") and "}" not in line:
                    # Dialogue satırı ile başlar, metin blokları arasında geçiş yapar
                    content.append(line)
                elif line.startswith("{\\an"):
                    # Ana metin bloğuna girmek için bir işaret olabilir
                    continue
                elif line.startswith("}"):
                    in_text_block = False
                elif line and not line.startswith("{") and not line.startswith("}"):
                    if in_text_block:
                        content.append(line)
        
        elif file_ext == "webvtt":
            # WebVTT formatı: zaman dilimi, metin, boş satır
            subtitles = []
            current_subtitle = {}
            
            for line in lines:
                line = line.strip()
                
                if not line:
                    if current_subtitle:
                        # Boş satır varsa, mevcut subtitle'yi ekle
                        subtitles.append(current_subtitle)
                        current_subtitle = {}
                elif re.match(r'\d{2}:\d{2}:\d{2},\d{3}', line):
                    # Zaman dilimi formatı (örneğin: 00:01:23,456)
                    current_subtitle['start_time'] = line
                elif re.match(r'\d{2}:\d{2}:\d{+},\d{3}', line):
                    # Zaman dilimi formatı (örneğin: 00:01:23,456)
                    current_subtitle['end_time'] = line
                elif line and not re.match(r'\d{2}:\d{2}:\d{2},\d{3}', line):
                    # Metin satırı
                    if 'text' not in current_subtitle:
                        current_subtitle['text'] = ""
                    current_subtitle['text'] += " " + line
                    self.add_subtitle(current_subtitle["start_time"], current_subtitle["end_time"], current_subtitle["text"])

            if current_subtitle:  # Son metni ekle
                subtitles.append(current_subtitle)
                
            content = subtitles
        
        elif file_ext == "srt":
            # SRT formatı: numara, zaman dilimi, metin (boş satır)
            subtitles = []
            current_subtitle = {}
            
            for line in lines:
                line = line.strip()
                
                if not line:
                    if current_subtitle:
                        subtitles.append(current_subtitle)
                        current_subtitle = {}
                elif re.match(r'\d+$', line):
                    # Sıra numarası (örneğin: 1)
                    if current_subtitle:
                        subtitles.append(current_subtitle)
                    current_subtitle = {'index': int(line)}
                elif re.match(r'^\d{2}:|^\d{2}:\d{2}|^\d{2}:\d{2}:\d{2}', line):
                    # Zaman dilimi (örneğin: 01:23:45,678)
                    current_subtitle['start_time'] = line
                elif re.match(r'\d{2}:\d{2}:\d{2},\d{3}', line):
                    # Başlangıç ve bitiş zamanları için bir karışık durum
                    if 'end_time' not in current_subtitle:
                        current_subtitle['end_time'] = line
                elif line and not re.match(r'\d+$', line):
                    # Metin satırı
                    if 'text' not in current_subtitle:
                        current_subtitle['text'] = ""
                    current_subtitle['text'] += " " + line

            if current_subtitle:
                self.add_subtitle(current_subtitle["start_time"], current_subtitle["end_time"], current_subtitle["text"])
                subtitles.append(current_subtitle)
                
            content = subtitles
        
        return content
