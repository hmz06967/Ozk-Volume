import hashlib
from core import * 
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

class FileListItem:
    def __init__(self, name, created_at):
        self.name = name
        self.created_at = created_at
        self.checkbox = QCheckBox()
        self.checkbox.setText(name)

    def widget(self):
        # Listeye eklemek için QListWidgetItem ile birlikte checkbox göster
        item = QListWidgetItem(self.name)
        
        # Checkbox’u bir "sütun" olarak (örneğin, sağ tıkla seç) kullanmak istiyorsanız,
        # bunu bir QHBoxLayout ile birleştirip widget’e ekleyebilirsiniz.
        # Ama: Liste içinde checkbox’ı göstermek için genellikle aşağıdaki gibi yapılır:
        
        layout = QVBoxLayout()
        layout.addWidget(self.checkbox)
        layout.addWidget(QLabel(f"Oluşturma Zamanı: {self.created_at}"))

        widget = QWidget()
        widget.setLayout(layout)

        return item, widget

class HistoryFunct:

    def __init__(self, parent=None):

        self.anahtar = "se1996_chelsie_2"  # 16, 24 veya 32 bayt olmalı (AES için)

        cache_dir =".cache"
        history_folder="ozk-volume"
        self.cache_dir = cache_dir
        self.history_folder = os.path.join(cache_dir, history_folder)
        self.history_file_list_path = os.path.join(cache_dir, "history_file_list.json")
        self.ensure_directories()
        # self.open_files("3-4-2026-1-46-6-subtitle")

    def ensure_directories(self):
        if os.path.exists(self.cache_dir) and os.path.exists(self.history_folder):
            return 
        directories = [self.cache_dir, self.history_folder]
        for directory in directories:
            try:
                os.makedirs(directory, exist_ok=True)
            except PermissionError as e:
                logging.error(f"❌ Hata: Dizin oluşturulamadı - Yetki yok: {directory}. Hata: {str(e)}")
            except Exception as e:
                logging.error(f"❌ BİR HATA OLUŞTU (beklenmeyen): {str(e)}")

    def encrypt_ecb(self, file_path, data, key):
        data_bytes = data.encode('utf-8')  # metni UTF-8 ile bytes'a çevir
        key = key.encode('utf-8')
        cipher = AES.new(key, AES.MODE_CBC)
        padded_data = pad(data_bytes, AES.block_size)
        ciphertext = cipher.encrypt(padded_data)

        with open(file_path, "wb") as f:
            f.write(cipher.iv)  # IV (İlk 16 bayt)
            f.write(ciphertext)

    def decrypt_ecb(self, file_path, key):
        
        with open(file_path, "rb") as f:
            iv = f.read(16)
            binary_data = f.read()

        key = key.encode('utf-8')
        if len(key) not in [16, 24, 32]:
            logging.error("Geçersiz padding!")

        cipher = AES.new(key, AES.MODE_CBC, iv=iv)
        plaintext = cipher.decrypt(binary_data)
        padding_len = plaintext[-1]
        if padding_len > 16 or padding_len == 0:
            logging.error("Geçersiz padding!")
        
        plaintext = plaintext[:-padding_len]
        text = plaintext.decode('utf-8')
        return text
        
    def open_files(self, filename):
        file_path = os.path.join(self.history_folder, filename)
        plaintext = self.decrypt_ecb(file_path, self.anahtar)
        return plaintext

    def create_files(self, filename, data):
        # çevirileri binary ve bir takım güvenlik algoritması ile history de saklayacağız.
        self.save_file_list(filename)
        file_path = os.path.join(self.history_folder, filename)
        self.encrypt_ecb(file_path, data, self.anahtar)

    def save_file_list(self, file_name):
        json_file_path = os.path.join(self.history_folder, file_name)
        
        try:
            with open(self.history_file_list_path, 'r', encoding='utf-8') as f:
                file_list_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            file_list_data = []
            return

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        entry = {
            "file_name": file_name,
            "created_at": timestamp
        }
        file_list_data.append(entry)
            
        file_names = [os.path.basename(f) for f in os.listdir(self.history_folder)]
        with open(self.history_file_list_path, 'w', encoding='utf-8') as f:
            json.dump(file_names, f, ensure_ascii=False, indent=4)
        
    
    def load_file_list(self):
        """
        Load and display the historical file list from JSON.
        
        Returns:
            list: List of file names (e.g., ['report_2025.txt', ...])
        """
        if not os.path.exists(self.history_file_list_path):
            print("❌ History file list not found. Run create_sample_files() first.")
            return []
        
        with open(self.history_file_list_path, 'r', encoding='utf-8') as f:
            file_names = json.load(f)
        
        print("✅ Historical file list loaded:")
        for i, file_name in enumerate(file_names, 1):
            print(f"  {i}. {file_name}")
        
        return file_names

class CacheManager(QWidget):
    changed = pyqtSignal()
    text = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        from top_bar import TitleBar  # buraya taşı
        from config import Config

        self.window_width = 400
        self.window_height = 150
        self.bparent = parent

        # self.setStyleSheet("background-color: #444; color: white")

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window |  Qt.WindowType.WindowStaysOnTopHint)

        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(0)

        self.htmanager = HistoryFunct()
        self.cache_dir = self.htmanager.cache_dir
        self.history_folder = self.htmanager.history_folder
        self.history_file_list_path = self.htmanager.history_file_list_path

        """self.config = Config()
        self.config_data = self.config.load_config()
        self.speech = self.config_data.get("speech", {})"""

        self.title = self.bparent.lang.get("history_cache")
        self.top_bar = TitleBar(self)
        layout.addWidget(self.top_bar)

        # Listeleme alanı (QListWidget ile dosyaları göster)
        self.file_list_widget = QListWidget()
        self.file_list_widget.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)  # Toplu seçim
        self.file_list_widget.setSortingEnabled(True)
        self.file_list_widget.doubleClicked.connect(self.open_list_item)

        # Dosyaları yükleme (oluşturulma zamanını da saklayalım)
        self.file_items = []  # (ad, oluşturma_zamanı, dosya_yolu)

        self.load_files()  # Dosyaları yükleyelim

        # Butonlar (hepsini sil, sil butonu)
        button_layout = QHBoxLayout()

        """
        delete_all: Delete All,
        select_all: Select All,
        delete_sel: Delete Selected
        """

        self.select_all_button = QPushButton(self.bparent.lang.get("select_all"))
        self.select_all_button.clicked.connect(self.select_all)

        self.delete_selected_button = QPushButton(self.bparent.lang.get("delete_sel"))
        self.delete_selected_button.clicked.connect(self.delete_selected_files)

        self.delete_all_button = QPushButton(self.bparent.lang.get("delete_all"))
        self.delete_all_button.clicked.connect(self.delete_all_files)

        button_layout.addWidget(self.select_all_button)
        button_layout.addWidget(self.delete_selected_button)
        button_layout.addWidget(self.delete_all_button)

        # Listeye ekleme ve butonları layout'a ekleyelim
        # layout.addWidget(QLabel("Dosya Geçmişi (Adı & Oluşturma Zamanı)"))
        layout.addWidget(self.file_list_widget)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def open_list_item(self, index):
        model = self.file_list_widget.model()
        item_text = model.data(index, Qt.ItemDataRole.DisplayRole)
        file_text = self.htmanager.open_files(item_text)
        self.text.emit(file_text)

    def load_files(self):
        """
        Belirtilen klasördeki tüm dosyaları yükler.
        Dosya adı + oluşturma zamanı (ISO formatında)
        """
        self.file_items = []
        try:
            for file_path in os.listdir(self.history_folder):
                full_path = os.path.join(self.history_folder, file_path)

                if os.path.isfile(full_path):
                    try:
                        stat_info = os.stat(full_path)
                        created_time = datetime.fromtimestamp(stat_info.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
                        self.file_items.append({
                            "name": file_path,
                            "created_time": created_time,
                            "path": full_path
                        })
                    except Exception as e:
                        print(f"Oluşturma zamanı alınamadı: {file_path}, Hata: {e}")
        except PermissionError:
            QMessageBox.critical(self, "Hata", f"Bu dizine erişim izni yok: {self.cache_dir}")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Dizin okunamadı: {str(e)}")

        # Liste'yi güncelle
        self.update_list()

    def update_list(self):
        """Listeyi güncelleyip dosyaları göster"""
        self.file_list_widget.clear()
        for item in self.file_items:
            # file = FileListItem(item['name'], item['created_time'])
            name = item["name"]
            created_at = item["created_time"]
            file = QListWidgetItem(f"{name}")
            self.file_list_widget.addItem(file)

        # Listeyi yeniden sırala (adına göre)
        self.file_list_widget.sortItems()

    def select_all(self):
        """Tüm dosyaları seç"""
        self.file_list_widget.selectAll()

    def delete_selected_files(self):
        """
        Seçilen dosyaları siler
        Kullanıcı onayı iste (QMessageBox ile)
        """
        selected_items = self.file_list_widget.selectedItems()
        """for i in range(self.file_list_widget.count()):
            item = self.file_list_widget.item(i)
            if isinstance(item, QCheckBox) and item.isChecked():
                # Dosya adı ve yolu al
                file_info = self.file_items[i]
                selected_items.append(file_info["path"])"""

        if not selected_items:
            QMessageBox.warning(self, "Uyarı", "Lütfen en az bir dosya seçin.")
            return

        # Silme onayı iste
        result = QMessageBox.question(
            self,
            "Onay Gerekiyor",
            f"Seçilen {len(selected_items)} dosyayı silmek istediğinizden emin misiniz?\n\n"
            + "\n".join([name.text() for name in selected_items]),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if result == QMessageBox.StandardButton.Yes:
            try:
                deleted_count = 0
                for name in selected_items:
                    file_path = os.path.join(self.history_folder, name.text())
                    os.remove(file_path)
                    deleted_count += 1

                self.load_files()  # Dosyaları yeniden yükle
                # QMessageBox.information(self, "Başarılı", f"{deleted_count} dosya silindi.")
            except PermissionError as e:
                QMessageBox.critical(self, "Hata", f"İzin yok: {str(e)}")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Dosyalar silinirken hata oluştu: {str(e)}")

    def delete_all_files(self):
        """
        Tüm dosyaları siler (onay iste)
        """
        if not self.file_items:
            QMessageBox.information(self, "Bilgi", "Hiçbir dosya yok.")
            return

        # Kullanıcı onayı
        result = QMessageBox.question(
            self,
            "Onay Gerekiyor",
            f"Tüm {len(self.file_items)} dosyayı silmek istediğinizden emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if result == QMessageBox.StandardButton.Yes:
            try:
                deleted_count = 0
                for item in self.file_items:
                    path = item["path"]
                    os.remove(path)
                    deleted_count += 1

                self.load_files()  # Yeniden yükle
                QMessageBox.information(self, "Başarılı", f"{deleted_count} dosya silindi.")
            except PermissionError as e:
                QMessageBox.critical(self, "Hata", f"İzin yok: {str(e)}")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Dosyalar silinirken hata oluştu: {str(e)}")

    def center_on_screen(self):
        """Pencerenin ekranın ortasında görünmesini sağlar."""
        # Ekran boyutlarını al
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()

        # Pencere boyutunu al
        window_width = self.window_width
        window_height = self.window_height

        # Ekranın ortasına göre konum hesapla
        x = (screen_geometry.width() - window_width) // 2
        y = (screen_geometry.height() - window_height) // 2

        # Pencereyi yeni pozisyona yerleştir
        self.setGeometry(x, y, window_width, window_height)

