from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                              QLabel, QComboBox, QCheckBox, QDialog, QSlider,
                              QGroupBox, QScrollArea, QFrame, QListWidget, QMessageBox,
                              QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
                              QSizePolicy, QDialogButtonBox, QLineEdit, QTreeWidget,
                              QTreeWidgetItem, QMenu, QInputDialog)
from PySide6.QtCore import Qt, Signal, QSettings, QUrl, QObject, QDateTime, QTimer
from PySide6.QtWebEngineCore import (QWebEngineProfile, QWebEngineSettings, 
                                    QWebEngineUrlRequestInterceptor, QWebEngineUrlRequestInfo,
                                    QWebEngineScript)
from PySide6.QtWebEngineWidgets import QWebEngineView
import json
import os
import urllib.request
import threading
import time
from datetime import datetime, timedelta
import sqlite3
import shutil
import requests

class PrivacyInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.blocked_domains = set()
        self.load_blocked_domains()

    def interceptRequest(self, info):
        try:
            url = info.requestUrl().toString()
            domain = QUrl(url).host()
            
            # Verificar si el dominio está bloqueado
            if domain in self.blocked_domains:
                info.block(True)
                return

            # Bloquear recursos según el tipo
            resource_type = info.resourceType()
            if resource_type in [
                QWebEngineUrlRequestInfo.ResourceType.Script,
                QWebEngineUrlRequestInfo.ResourceType.Image,
                QWebEngineUrlRequestInfo.ResourceType.StyleSheet
            ]:
                # Aquí puedes añadir lógica adicional para bloquear ciertos tipos de recursos
                pass

        except Exception as e:
            print(f"Error en interceptRequest: {str(e)}")

    def load_blocked_domains(self):
        try:
            if os.path.exists("blocked_domains.json"):
                with open("blocked_domains.json", "r") as f:
                    self.blocked_domains = set(json.load(f))
        except Exception as e:
            print(f"Error cargando dominios bloqueados: {str(e)}")

    def save_blocked_domains(self):
        try:
            with open("blocked_domains.json", "w") as f:
                json.dump(list(self.blocked_domains), f)
        except Exception as e:
            print(f"Error guardando dominios bloqueados: {str(e)}")

    def add_blocked_domain(self, domain):
        self.blocked_domains.add(domain)
        self.save_blocked_domains()

    def remove_blocked_domain(self, domain):
        if domain in self.blocked_domains:
            self.blocked_domains.remove(domain)
            self.save_blocked_domains()

class AdBlockerInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.blocked_domains = set()
        self.blocked_patterns = set()
        self.last_update = 0
        self.update_interval = 24 * 60 * 60  # 24 horas en segundos
        
        # Iniciar la carga de listas de filtros en un hilo separado
        threading.Thread(target=self.load_filter_lists, daemon=True).start()

    def load_filter_lists(self):
        """Carga las listas de filtros desde archivos locales"""
        try:
            # Cargar EasyList
            if os.path.exists("easylist.txt"):
                with open("easylist.txt", "r", encoding="utf-8") as f:
                    self.easylist = f.read().splitlines()
            else:
                print("No se encontró el archivo easylist.txt")
                self.easylist = []

            # Cargar EasyPrivacy
            if os.path.exists("easyprivacy.txt"):
                with open("easyprivacy.txt", "r", encoding="utf-8") as f:
                    self.easyprivacy = f.read().splitlines()
            else:
                print("No se encontró el archivo easyprivacy.txt")
                self.easyprivacy = []

            print("Listas de filtros cargadas correctamente")
        except Exception as e:
            print(f"Error al cargar las listas de filtros: {str(e)}")
            self.easylist = []
            self.easyprivacy = []

    def update_filter_lists(self):
        """Actualiza las listas de filtros desde las fuentes en línea"""
        try:
            # URLs de las listas de filtros
            easylist_url = "https://easylist.to/easylist/easylist.txt"
            easyprivacy_url = "https://easylist.to/easylist/easyprivacy.txt"

            # Descargar EasyList
            try:
                response = requests.get(easylist_url)
                response.raise_for_status()
                with open("easylist.txt", "w", encoding="utf-8") as f:
                    f.write(response.text)
                self.easylist = response.text.splitlines()
            except Exception as e:
                print(f"Error al actualizar EasyList: {str(e)}")

            # Descargar EasyPrivacy
            try:
                response = requests.get(easyprivacy_url)
                response.raise_for_status()
                with open("easyprivacy.txt", "w", encoding="utf-8") as f:
                    f.write(response.text)
                self.easyprivacy = response.text.splitlines()
            except Exception as e:
                print(f"Error al actualizar EasyPrivacy: {str(e)}")

            print("Listas de filtros actualizadas correctamente")
        except Exception as e:
            print(f"Error al actualizar las listas de filtros: {str(e)}")

    def interceptRequest(self, info):
        """Intercepta y bloquea solicitudes de anuncios"""
        try:
            url = info.requestUrl().toString()
            
            # Verificar dominios bloqueados
            for domain in self.blocked_domains:
                if domain in url:
                    info.block(True)
                    return

            # Verificar patrones bloqueados
            for pattern in self.blocked_patterns:
                if pattern in url:
                    info.block(True)
                    return

            # Bloquear tipos específicos de recursos
            resource_type = info.resourceType()
            if resource_type in [QWebEngineUrlRequestInfo.ResourceType.Script,
                               QWebEngineUrlRequestInfo.ResourceType.Image,
                               QWebEngineUrlRequestInfo.ResourceType.StyleSheet]:
                for domain in self.blocked_domains:
                    if domain in url:
                        info.block(True)
                        return

        except Exception as e:
            print(f"Error en interceptRequest: {str(e)}")

class PrivacySettings:
    def __init__(self):
        self.settings = QSettings("TronBrowser", "Privacy")
        self.load_settings()

    def load_settings(self):
        # Valores por defecto
        defaults = {
            "privacy_level": "balanced",  # strict, balanced, custom
            "block_trackers": True,
            "block_ads": True,
            "block_cookies": False,
            "block_javascript": False,
            "block_images": False,
            "block_webrtc": True,
            "block_fingerprinting": True,
            "block_third_party": True,
            "clear_on_exit": True,
            "do_not_track": True
        }

        # Cargar configuración guardada o usar valores por defecto
        for key, default_value in defaults.items():
            if not self.settings.contains(key):
                self.settings.setValue(key, default_value)

    def save_settings(self):
        self.settings.sync()

    def get_setting(self, key):
        value = self.settings.value(key)
        if isinstance(value, str):
            # Convertir strings "true"/"false" a booleanos
            if value.lower() == "true":
                return True
            elif value.lower() == "false":
                return False
        return value

    def set_setting(self, key, value):
        self.settings.setValue(key, value)
        self.settings.sync()

class AutoClearSettings:
    def __init__(self):
        self.settings = QSettings("TronBrowser", "AutoClear")
        self.load_settings()
        self.timer = QTimer()
        self.timer.timeout.connect(self.auto_clear_data)
        self.start_timer()

    def load_settings(self):
        defaults = {
            "enabled": False,
            "frequency": "24 hours",
            "clear_history": True,
            "clear_cookies": True,
            "clear_cache": True,
            "clear_passwords": False,
            "clear_form_data": False,
            "clear_downloads": False
        }
        
        for key, default_value in defaults.items():
            if not self.settings.contains(key):
                self.settings.setValue(key, default_value)
        self.settings.sync()

    def save_settings(self):
        self.settings.sync()
        self.start_timer()

    def get_setting(self, key):
        value = self.settings.value(key)
        if isinstance(value, str):
            if value.lower() == "true":
                return True
            elif value.lower() == "false":
                return False
        return value

    def set_setting(self, key, value):
        self.settings.setValue(key, value)
        self.settings.sync()

    def start_timer(self):
        if not self.get_setting("enabled"):
            self.timer.stop()
            return

        frequency = self.get_setting("frequency")
        hours = int(frequency.split()[0])
        self.timer.start(hours * 60 * 60 * 1000)  # Convertir horas a milisegundos

    def auto_clear_data(self):
        profile = QWebEngineProfile.defaultProfile()
        
        if self.get_setting("clear_history"):
            self.clear_history_data()
        
        if self.get_setting("clear_cookies"):
            profile.cookieStore().deleteAllCookies()
        
        if self.get_setting("clear_cache"):
            profile.clearHttpCache()
        
        if self.get_setting("clear_passwords"):
            self.clear_saved_passwords()
        
        if self.get_setting("clear_form_data"):
            self.clear_form_data()
        
        if self.get_setting("clear_downloads"):
            self.clear_downloads()

    def clear_history_data(self):
        try:
            profile_path = QWebEngineProfile.defaultProfile().persistentStoragePath()
            history_db = os.path.join(profile_path, "History")
            
            if os.path.exists(history_db):
                conn = sqlite3.connect(history_db)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM urls")
                cursor.execute("DELETE FROM visits")
                conn.commit()
                conn.close()
        except Exception as e:
            print(f"Error clearing history: {str(e)}")

    def clear_saved_passwords(self):
        try:
            profile_path = QWebEngineProfile.defaultProfile().persistentStoragePath()
            login_db = os.path.join(profile_path, "Login Data")
            
            if os.path.exists(login_db):
                conn = sqlite3.connect(login_db)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM logins")
                conn.commit()
                conn.close()
        except Exception as e:
            print(f"Error clearing passwords: {str(e)}")

    def clear_form_data(self):
        try:
            profile_path = QWebEngineProfile.defaultProfile().persistentStoragePath()
            form_data_db = os.path.join(profile_path, "Web Data")
            
            if os.path.exists(form_data_db):
                conn = sqlite3.connect(form_data_db)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM autofill")
                conn.commit()
                conn.close()
        except Exception as e:
            print(f"Error clearing form data: {str(e)}")

    def clear_downloads(self):
        try:
            profile_path = QWebEngineProfile.defaultProfile().persistentStoragePath()
            downloads_db = os.path.join(profile_path, "History")
            
            if os.path.exists(downloads_db):
                conn = sqlite3.connect(downloads_db)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM downloads")
                cursor.execute("DELETE FROM downloads_url_chains")
                conn.commit()
                conn.close()
        except Exception as e:
            print(f"Error clearing downloads: {str(e)}")

class SavedDataDialog(QDialog):
    def __init__(self, title, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # Crear tabla para mostrar datos
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Site", "Data"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Llenar tabla con datos
        self.table.setRowCount(len(data))
        for i, (site, info) in enumerate(data.items()):
            self.table.setItem(i, 0, QTableWidgetItem(site))
            self.table.setItem(i, 1, QTableWidgetItem(str(info)))
        
        layout.addWidget(self.table)
        
        # Botones
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)

class HistoryManager:
    def __init__(self):
        self.profile = QWebEngineProfile.defaultProfile()
        self.history_db = os.path.join(self.profile.persistentStoragePath(), "History")
        self.last_visit_time = None
        self.init_history_db()

    def init_history_db(self):
        """Inicializa la base de datos del historial si no existe"""
        try:
            if not os.path.exists(self.history_db):
                conn = sqlite3.connect(self.history_db)
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS urls (
                        id INTEGER PRIMARY KEY,
                        url TEXT NOT NULL,
                        title TEXT,
                        visit_count INTEGER DEFAULT 1,
                        last_visit_time INTEGER,
                        created_time INTEGER
                    )
                ''')
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS visits (
                        id INTEGER PRIMARY KEY,
                        url_id INTEGER,
                        visit_time INTEGER,
                        FOREIGN KEY (url_id) REFERENCES urls(id)
                    )
                ''')
                conn.commit()
                conn.close()
        except Exception as e:
            print(f"Error initializing history database: {str(e)}")

    def add_url(self, url, title=""):
        """Añade una URL al historial"""
        try:
            conn = sqlite3.connect(self.history_db)
            cursor = conn.cursor()
            current_time = int(time.time() * 1000000)  # Microsegundos

            # Verificar si la URL ya existe
            cursor.execute("SELECT id, visit_count FROM urls WHERE url = ?", (url,))
            result = cursor.fetchone()

            if result:
                url_id, visit_count = result
                cursor.execute("""
                    UPDATE urls 
                    SET visit_count = ?, last_visit_time = ?, title = ?
                    WHERE id = ?
                """, (visit_count + 1, current_time, title, url_id))
            else:
                cursor.execute("""
                    INSERT INTO urls (url, title, visit_count, last_visit_time, created_time)
                    VALUES (?, ?, 1, ?, ?)
                """, (url, title, current_time, current_time))
                url_id = cursor.lastrowid

            # Añadir visita
            cursor.execute("""
                INSERT INTO visits (url_id, visit_time)
                VALUES (?, ?)
            """, (url_id, current_time))

            conn.commit()
            conn.close()
            self.last_visit_time = current_time
        except Exception as e:
            print(f"Error adding URL to history: {str(e)}")

    def get_history(self, time_range=None):
        """Obtiene el historial organizado por tiempo"""
        try:
            conn = sqlite3.connect(self.history_db)
            cursor = conn.cursor()
            
            if time_range:
                current_time = int(time.time() * 1000000)
                if time_range == "today":
                    start_time = current_time - (24 * 60 * 60 * 1000000)
                elif time_range == "yesterday":
                    start_time = current_time - (48 * 60 * 60 * 1000000)
                    end_time = current_time - (24 * 60 * 60 * 1000000)
                elif time_range == "last_week":
                    start_time = current_time - (7 * 24 * 60 * 60 * 1000000)
                elif time_range == "last_month":
                    start_time = current_time - (30 * 24 * 60 * 60 * 1000000)
                
                if time_range == "yesterday":
                    cursor.execute("""
                        SELECT u.url, u.title, v.visit_time
                        FROM urls u
                        JOIN visits v ON u.id = v.url_id
                        WHERE v.visit_time BETWEEN ? AND ?
                        ORDER BY v.visit_time DESC
                    """, (start_time, end_time))
                else:
                    cursor.execute("""
                        SELECT u.url, u.title, v.visit_time
                        FROM urls u
                        JOIN visits v ON u.id = v.url_id
                        WHERE v.visit_time > ?
                        ORDER BY v.visit_time DESC
                    """, (start_time,))
            else:
                cursor.execute("""
                    SELECT u.url, u.title, v.visit_time
                    FROM urls u
                    JOIN visits v ON u.id = v.url_id
                    ORDER BY v.visit_time DESC
                """)

            history = cursor.fetchall()
            conn.close()
            return history
        except Exception as e:
            print(f"Error getting history: {str(e)}")
            return []

    def clear_history(self, time_range=None):
        """Limpia el historial según el rango de tiempo especificado"""
        try:
            conn = sqlite3.connect(self.history_db)
            cursor = conn.cursor()
            
            if time_range:
                current_time = int(time.time() * 1000000)
                if time_range == "today":
                    start_time = current_time - (24 * 60 * 60 * 1000000)
                elif time_range == "yesterday":
                    start_time = current_time - (48 * 60 * 60 * 1000000)
                    end_time = current_time - (24 * 60 * 60 * 1000000)
                elif time_range == "last_week":
                    start_time = current_time - (7 * 24 * 60 * 60 * 1000000)
                elif time_range == "last_month":
                    start_time = current_time - (30 * 24 * 60 * 60 * 1000000)
                
                if time_range == "yesterday":
                    cursor.execute("""
                        DELETE FROM visits 
                        WHERE visit_time BETWEEN ? AND ?
                    """, (start_time, end_time))
                else:
                    cursor.execute("""
                        DELETE FROM visits 
                        WHERE visit_time > ?
                    """, (start_time,))
            else:
                cursor.execute("DELETE FROM visits")
                cursor.execute("DELETE FROM urls")
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error clearing history: {str(e)}")

class HistoryDialog(QDialog):
    def __init__(self, history_manager, parent=None):
        super().__init__(parent)
        self.history_manager = history_manager
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("History")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout()
        
        # Barra de herramientas
        toolbar = QHBoxLayout()
        
        # Selector de rango de tiempo
        self.time_range_combo = QComboBox()
        self.time_range_combo.addItems([
            "All History",
            "Today",
            "Yesterday",
            "Last Week",
            "Last Month"
        ])
        self.time_range_combo.currentTextChanged.connect(self.update_history)
        toolbar.addWidget(QLabel("Show:"))
        toolbar.addWidget(self.time_range_combo)
        
        # Botón de búsqueda
        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.search_history)
        toolbar.addWidget(self.search_btn)
        
        # Botón de limpiar
        self.clear_btn = QPushButton("Clear History")
        self.clear_btn.clicked.connect(self.clear_history)
        toolbar.addWidget(self.clear_btn)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # Árbol de historial
        self.history_tree = QTreeWidget()
        self.history_tree.setHeaderLabels(["Title", "URL", "Visit Time"])
        self.history_tree.setColumnWidth(0, 300)
        self.history_tree.setColumnWidth(1, 300)
        self.history_tree.itemDoubleClicked.connect(self.open_url)
        self.history_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.history_tree.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.history_tree)
        
        self.setLayout(layout)
        self.update_history()

    def update_history(self):
        """Actualiza el árbol de historial"""
        self.history_tree.clear()
        
        time_range = self.time_range_combo.currentText().lower().replace(" ", "_")
        history = self.history_manager.get_history(time_range)
        
        # Organizar por fecha
        current_date = None
        current_date_item = None
        
        for url, title, visit_time in history:
            visit_datetime = datetime.fromtimestamp(visit_time / 1000000)
            date_str = visit_datetime.strftime("%Y-%m-%d")
            
            if date_str != current_date:
                current_date = date_str
                current_date_item = QTreeWidgetItem(self.history_tree, [date_str])
                current_date_item.setExpanded(True)
            
            time_str = visit_datetime.strftime("%H:%M:%S")
            item = QTreeWidgetItem(current_date_item, [title or url, url, time_str])
            item.setData(0, Qt.UserRole, url)

    def open_url(self, item, column):
        """Abre la URL seleccionada"""
        if item.parent():  # Si no es un elemento de fecha
            url = item.data(0, Qt.UserRole)
            if url:
                self.parent().load_url(QUrl(url))
                self.accept()

    def search_history(self):
        """Busca en el historial"""
        text, ok = QInputDialog.getText(self, "Search History", "Enter search term:")
        if ok and text:
            self.history_tree.clear()
            history = self.history_manager.get_history()
            
            current_date = None
            current_date_item = None
            
            for url, title, visit_time in history:
                if text.lower() in url.lower() or (title and text.lower() in title.lower()):
                    visit_datetime = datetime.fromtimestamp(visit_time / 1000000)
                    date_str = visit_datetime.strftime("%Y-%m-%d")
                    
                    if date_str != current_date:
                        current_date = date_str
                        current_date_item = QTreeWidgetItem(self.history_tree, [date_str])
                        current_date_item.setExpanded(True)
                    
                    time_str = visit_datetime.strftime("%H:%M:%S")
                    item = QTreeWidgetItem(current_date_item, [title or url, url, time_str])
                    item.setData(0, Qt.UserRole, url)

    def clear_history(self):
        """Limpia el historial"""
        reply = QMessageBox.question(
            self,
            "Clear History",
            "Are you sure you want to clear the history?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            time_range = self.time_range_combo.currentText().lower().replace(" ", "_")
            self.history_manager.clear_history(time_range)
            self.update_history()

    def show_context_menu(self, position):
        """Muestra el menú contextual"""
        item = self.history_tree.itemAt(position)
        if item and item.parent():  # Si no es un elemento de fecha
            menu = QMenu()
            open_action = menu.addAction("Open")
            copy_action = menu.addAction("Copy URL")
            delete_action = menu.addAction("Delete")
            
            action = menu.exec_(self.history_tree.mapToGlobal(position))
            
            if action == open_action:
                self.open_url(item, 0)
            elif action == copy_action:
                url = item.data(0, Qt.UserRole)
                QApplication.clipboard().setText(url)
            elif action == delete_action:
                # Implementar eliminación de URL específica
                pass

class PrivacyManager(QWidget):
    privacy_level_changed = Signal(str)
    tracker_blocked = Signal(str)
    data_shared = Signal(dict)
    data_cleared = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.settings = PrivacySettings()
        self.history_manager = HistoryManager()
        self.auto_clear = AutoClearSettings()
        self.ad_blocker = AdBlockerInterceptor()
        self.init_ui()
        self.load_privacy_presets()
        self.load_auto_clear_settings()
        
        # Configurar actualización periódica de listas de filtros
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_filter_lists)
        self.update_timer.start(24 * 60 * 60 * 1000)  # 24 horas en milisegundos

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(layout)

        # Crear pestañas para organizar las funciones
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)

        # Pestaña de Configuración General
        general_tab = QWidget()
        general_layout = QVBoxLayout()
        general_layout.setSpacing(5)
        general_tab.setLayout(general_layout)

        # Privacy Level Selector
        privacy_group = QGroupBox()
        privacy_group.setTitle("Privacy Level")
        privacy_layout = QHBoxLayout()
        privacy_layout.setContentsMargins(5, 5, 5, 5)
        
        self.privacy_combo = QComboBox()
        self.privacy_combo.addItems(["Strict", "Balanced", "Custom"])
        self.privacy_combo.setMaximumWidth(120)
        self.privacy_combo.currentTextChanged.connect(self.on_privacy_level_changed)
        privacy_layout.addWidget(self.privacy_combo)
        privacy_layout.addStretch()
        
        privacy_group.setLayout(privacy_layout)
        privacy_group.setMaximumHeight(50)  # Limitar la altura del grupo
        general_layout.addWidget(privacy_group)

        # Privacy Features
        features_group = QGroupBox("Privacy Features")
        features_layout = QVBoxLayout()
        features_layout.setSpacing(2)
        
        self.feature_checks = {
            "block_trackers": QCheckBox("Block Trackers"),
            "block_ads": QCheckBox("Block Ads"),
            "block_cookies": QCheckBox("Block Third-Party Cookies"),
            "block_javascript": QCheckBox("Block JavaScript"),
            "block_images": QCheckBox("Block Images"),
            "block_webrtc": QCheckBox("Block WebRTC"),
            "block_fingerprinting": QCheckBox("Block Fingerprinting"),
            "block_third_party": QCheckBox("Block Third-Party Requests"),
            "clear_on_exit": QCheckBox("Clear Data on Exit"),
            "do_not_track": QCheckBox("Send Do Not Track Signal"),
            "block_phishing": QCheckBox("Block Phishing Sites"),
            "block_malware": QCheckBox("Block Malware Sites"),
            "block_location": QCheckBox("Block Location Access"),
            "block_notifications": QCheckBox("Block Notifications"),
            "block_camera": QCheckBox("Block Camera Access"),
            "block_microphone": QCheckBox("Block Microphone Access")
        }

        for check in self.feature_checks.values():
            features_layout.addWidget(check)
            check.stateChanged.connect(self.on_feature_changed)

        features_group.setLayout(features_layout)
        general_layout.addWidget(features_group)

        # Pestaña de Datos de Navegación
        data_tab = QWidget()
        data_layout = QVBoxLayout()
        data_layout.setSpacing(5)
        data_tab.setLayout(data_layout)

        # Botones para borrar datos
        clear_data_group = QGroupBox()
        clear_data_group.setTitle("Clear Browsing Data")
        clear_data_layout = QHBoxLayout()
        clear_data_layout.setContentsMargins(5, 5, 5, 5)
        clear_data_layout.setSpacing(3)
        clear_data_layout.setAlignment(Qt.AlignLeft)

        self.clear_history_btn = QPushButton("Clear History")
        self.clear_history_btn.setFixedWidth(100)
        self.clear_history_btn.clicked.connect(self.clear_history)
        clear_data_layout.addWidget(self.clear_history_btn)

        self.clear_cookies_btn = QPushButton("Clear Cookies")
        self.clear_cookies_btn.setFixedWidth(100)
        self.clear_cookies_btn.clicked.connect(self.clear_cookies)
        clear_data_layout.addWidget(self.clear_cookies_btn)

        self.clear_cache_btn = QPushButton("Clear Cache")
        self.clear_cache_btn.setFixedWidth(100)
        self.clear_cache_btn.clicked.connect(self.clear_cache)
        clear_data_layout.addWidget(self.clear_cache_btn)

        self.clear_all_btn = QPushButton("Clear All Data")
        self.clear_all_btn.setFixedWidth(100)
        self.clear_all_btn.clicked.connect(self.clear_all_data)
        clear_data_layout.addWidget(self.clear_all_btn)

        clear_data_group.setLayout(clear_data_layout)
        clear_data_group.setMaximumHeight(50)
        data_layout.addWidget(clear_data_group)

        # Grupo de opciones de borrado automático
        auto_clear_group = QGroupBox("Auto-Clear Settings")
        auto_clear_layout = QVBoxLayout()
        auto_clear_layout.setSpacing(5)

        # Opciones de borrado automático
        self.auto_clear_check = QCheckBox("Enable automatic data clearing")
        self.auto_clear_check.clicked.connect(self.toggle_auto_clear)
        auto_clear_layout.addWidget(self.auto_clear_check)

        # Selector de frecuencia
        frequency_layout = QHBoxLayout()
        frequency_layout.addWidget(QLabel("Clear data every:"))
        self.frequency_combo = QComboBox()
        self.frequency_combo.addItems(["1 hour", "4 hours", "8 hours", "12 hours", "24 hours", "7 days"])
        self.frequency_combo.setEnabled(False)
        self.frequency_combo.activated.connect(self.on_frequency_changed)
        frequency_layout.addWidget(self.frequency_combo)
        auto_clear_layout.addLayout(frequency_layout)

        # Opciones de qué borrar automáticamente
        self.auto_clear_options = {
            "history": QCheckBox("History"),
            "cookies": QCheckBox("Cookies"),
            "cache": QCheckBox("Cache"),
            "passwords": QCheckBox("Saved Passwords"),
            "form_data": QCheckBox("Form Data"),
            "downloads": QCheckBox("Download History")
        }

        for key, check in self.auto_clear_options.items():
            check.setEnabled(False)
            check.clicked.connect(lambda checked, k=key: self.on_option_changed(k, checked))
            auto_clear_layout.addWidget(check)

        auto_clear_group.setLayout(auto_clear_layout)
        data_layout.addWidget(auto_clear_group)

        # Grupo de gestión de datos guardados
        saved_data_group = QGroupBox("Saved Data Management")
        saved_data_layout = QVBoxLayout()
        saved_data_layout.setSpacing(5)

        # Botones para gestionar datos guardados
        saved_data_buttons = QHBoxLayout()
        
        self.view_passwords_btn = QPushButton("View Saved Passwords")
        self.view_passwords_btn.clicked.connect(self.show_saved_passwords)
        saved_data_buttons.addWidget(self.view_passwords_btn)

        self.view_form_data_btn = QPushButton("View Form Data")
        self.view_form_data_btn.clicked.connect(self.show_form_data)
        saved_data_buttons.addWidget(self.view_form_data_btn)

        self.view_downloads_btn = QPushButton("View Downloads")
        self.view_downloads_btn.clicked.connect(self.show_downloads)
        saved_data_buttons.addWidget(self.view_downloads_btn)

        saved_data_layout.addLayout(saved_data_buttons)
        saved_data_group.setLayout(saved_data_layout)
        data_layout.addWidget(saved_data_group)

        # Añadir un widget vacío que se expanda para empujar el grupo hacia arriba
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        data_layout.addWidget(spacer)

        # Pestaña de Permisos de Sitios
        permissions_tab = QWidget()
        permissions_layout = QVBoxLayout()
        permissions_layout.setSpacing(5)
        permissions_tab.setLayout(permissions_layout)

        self.permissions_table = QTableWidget()
        self.permissions_table.setColumnCount(3)
        self.permissions_table.setHorizontalHeaderLabels(["Site", "Permission", "Status"])
        self.permissions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        permissions_layout.addWidget(self.permissions_table)

        # Añadir las pestañas al widget principal
        tab_widget.addTab(general_tab, "General")
        tab_widget.addTab(data_tab, "Browsing Data")
        tab_widget.addTab(permissions_tab, "Site Permissions")

        # Ajustar el tamaño mínimo del widget
        self.setMinimumWidth(300)
        self.setMinimumHeight(400)

    def load_privacy_presets(self):
        # Cargar configuración actual
        current_level = self.settings.get_setting("privacy_level")
        self.privacy_combo.setCurrentText(current_level.capitalize())
        
        # Actualizar checkboxes
        for key, check in self.feature_checks.items():
            check.setChecked(self.settings.get_setting(key))

    def on_privacy_level_changed(self, level):
        level = level.lower()
        self.settings.set_setting("privacy_level", level)
        
        # Aplicar configuración según el nivel
        if level == "strict":
            self.apply_strict_privacy()
        elif level == "balanced":
            self.apply_balanced_privacy()
        
        self.privacy_level_changed.emit(level)

    def apply_strict_privacy(self):
        for key, check in self.feature_checks.items():
            check.setChecked(True)
            self.settings.set_setting(key, True)

    def apply_balanced_privacy(self):
        balanced_settings = {
            "block_trackers": True,
            "block_ads": True,
            "block_cookies": True,
            "block_javascript": False,
            "block_images": False,
            "block_webrtc": True,
            "block_fingerprinting": True,
            "block_third_party": True,
            "clear_on_exit": True,
            "do_not_track": True
        }
        
        for key, value in balanced_settings.items():
            self.feature_checks[key].setChecked(value)
            self.settings.set_setting(key, value)

    def on_feature_changed(self):
        # Actualizar configuración cuando cambia cualquier feature
        for key, check in self.feature_checks.items():
            self.settings.set_setting(key, check.isChecked())

    def on_font_size_changed(self, size):
        # Implementar cambio de tamaño de fuente en modo lectura
        pass

    def on_theme_changed(self, theme):
        # Implementar cambio de tema en modo lectura
        pass

    def update_data_sharing(self, data):
        """Actualiza el monitor de datos compartidos"""
        self.data_label.setText(f"Data being shared: {json.dumps(data, indent=2)}")
        self.data_shared.emit(data)

    def update_filter_lists(self):
        """Actualiza las listas de filtros desde las fuentes en línea"""
        try:
            # URLs de las listas de filtros
            easylist_url = "https://easylist.to/easylist/easylist.txt"
            easyprivacy_url = "https://easylist.to/easylist/easyprivacy.txt"

            # Descargar EasyList
            try:
                response = requests.get(easylist_url)
                response.raise_for_status()
                with open("easylist.txt", "w", encoding="utf-8") as f:
                    f.write(response.text)
                self.ad_blocker.easylist = response.text.splitlines()
            except Exception as e:
                print(f"Error al actualizar EasyList: {str(e)}")

            # Descargar EasyPrivacy
            try:
                response = requests.get(easyprivacy_url)
                response.raise_for_status()
                with open("easyprivacy.txt", "w", encoding="utf-8") as f:
                    f.write(response.text)
                self.ad_blocker.easyprivacy = response.text.splitlines()
            except Exception as e:
                print(f"Error al actualizar EasyPrivacy: {str(e)}")

            print("Listas de filtros actualizadas correctamente")
        except Exception as e:
            print(f"Error al actualizar las listas de filtros: {str(e)}")

    def clear_history(self):
        """Borra el historial de navegación"""
        try:
            self.history_manager.clear_history()
            self.data_cleared.emit("history")
            QMessageBox.information(self, "Success", "Browsing history cleared successfully")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error clearing history: {str(e)}")

    def clear_cookies(self):
        """Borra las cookies"""
        try:
            profile = QWebEngineProfile.defaultProfile()
            profile.cookieStore().deleteAllCookies()
            self.data_cleared.emit("cookies")
            QMessageBox.information(self, "Success", "Cookies cleared successfully")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error clearing cookies: {str(e)}")

    def clear_cache(self):
        """Borra la caché del navegador"""
        try:
            profile = QWebEngineProfile.defaultProfile()
            profile.clearHttpCache()
            self.data_cleared.emit("cache")
            QMessageBox.information(self, "Success", "Cache cleared successfully")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error clearing cache: {str(e)}")

    def clear_all_data(self):
        """Borra todos los datos de navegación"""
        reply = QMessageBox.question(self, "Confirm Clear All",
                                   "Are you sure you want to clear all browsing data? This cannot be undone.",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.clear_history()
            self.clear_cookies()
            self.clear_cache()
            self.data_cleared.emit("all")
            QMessageBox.information(self, "Success", "All browsing data cleared successfully")

    def update_site_permissions(self):
        """Actualiza la tabla de permisos de sitios"""
        try:
            profile = QWebEngineProfile.defaultProfile()
            # Obtener permisos de sitios
            # Implementar lógica para obtener y mostrar permisos
            pass
        except Exception as e:
            print(f"Error updating site permissions: {str(e)}")

    def apply_privacy_settings(self, browser):
        """Aplica la configuración de privacidad al navegador"""
        try:
            if browser and hasattr(browser, 'page'):
                profile = browser.page().profile()
                
                # Aplicar interceptor de anuncios
                profile.setUrlRequestInterceptor(self.ad_blocker)
                
                # Configurar permisos
                settings = profile.settings()
                settings.setAttribute(QWebEngineSettings.JavascriptEnabled, 
                                   not self.settings.get_setting("block_javascript"))
                settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, 
                                   not self.settings.get_setting("block_cookies"))
                settings.setAttribute(QWebEngineSettings.WebGLEnabled, 
                                   not self.settings.get_setting("block_fingerprinting"))
                settings.setAttribute(QWebEngineSettings.PluginsEnabled, 
                                   not self.settings.get_setting("block_third_party"))
                
                # Configurar WebRTC
                if self.settings.get_setting("block_webrtc"):
                    # Implementar bloqueo de WebRTC
                    pass
                
                print("Configuración de privacidad aplicada correctamente")
        except Exception as e:
            print(f"Error al aplicar configuración de privacidad: {str(e)}")

    def load_auto_clear_settings(self):
        """Carga la configuración de borrado automático"""
        try:
            # Cargar estado del checkbox principal
            enabled = self.settings.get_setting("auto_clear_enabled")
            self.auto_clear_check.setChecked(enabled)
            
            # Cargar frecuencia
            frequency = self.settings.get_setting("auto_clear_frequency")
            if frequency:
                self.frequency_combo.setCurrentText(frequency)
            
            # Cargar opciones individuales
            for key, check in self.auto_clear_options.items():
                value = self.settings.get_setting(f"auto_clear_{key}")
                check.setChecked(value)
                check.setEnabled(enabled)
            
            # Iniciar temporizador si está habilitado
            if enabled:
                self.start_auto_clear_timer()
                
            print("Auto-clear settings loaded")
        except Exception as e:
            print(f"Error loading auto-clear settings: {str(e)}")

    def toggle_auto_clear(self, checked):
        """Habilita/deshabilita las opciones de borrado automático"""
        try:
            self.frequency_combo.setEnabled(checked)
            for check in self.auto_clear_options.values():
                check.setEnabled(checked)
            
            # Guardar configuración
            self.settings.set_setting("auto_clear_enabled", checked)
            self.settings.save_settings()
            
            # Iniciar/detener temporizador
            if checked:
                self.start_auto_clear_timer()
            else:
                self.stop_auto_clear_timer()
                
            print(f"Auto-clear {'enabled' if checked else 'disabled'}")
        except Exception as e:
            print(f"Error toggling auto-clear: {str(e)}")

    def on_frequency_changed(self, index):
        """Maneja el cambio en la frecuencia de borrado"""
        try:
            frequency = self.frequency_combo.currentText()
            self.settings.set_setting("auto_clear_frequency", frequency)
            self.settings.save_settings()
            
            if self.auto_clear_check.isChecked():
                self.start_auto_clear_timer()
                
            print(f"Frequency changed to: {frequency}")
        except Exception as e:
            print(f"Error changing frequency: {str(e)}")

    def on_option_changed(self, key, checked):
        """Maneja el cambio en una opción específica"""
        try:
            self.settings.set_setting(f"auto_clear_{key}", checked)
            self.settings.save_settings()
            print(f"Option {key} {'enabled' if checked else 'disabled'}")
        except Exception as e:
            print(f"Error updating option {key}: {str(e)}")

    def start_auto_clear_timer(self):
        """Inicia el temporizador de borrado automático"""
        try:
            if hasattr(self, 'auto_clear_timer'):
                self.auto_clear_timer.stop()
            
            self.auto_clear_timer = QTimer()
            self.auto_clear_timer.timeout.connect(self.auto_clear_data)
            
            frequency = self.settings.get_setting("auto_clear_frequency")
            hours = int(frequency.split()[0])
            self.auto_clear_timer.start(hours * 60 * 60 * 1000)
            print(f"Auto-clear timer started: {hours} hours")
        except Exception as e:
            print(f"Error starting auto-clear timer: {str(e)}")

    def stop_auto_clear_timer(self):
        """Detiene el temporizador de borrado automático"""
        try:
            if hasattr(self, 'auto_clear_timer'):
                self.auto_clear_timer.stop()
                print("Auto-clear timer stopped")
        except Exception as e:
            print(f"Error stopping auto-clear timer: {str(e)}")

    def auto_clear_data(self):
        """Ejecuta el borrado automático de datos"""
        try:
            profile = QWebEngineProfile.defaultProfile()
            
            if self.settings.get_setting("auto_clear_history"):
                self.clear_history()
            
            if self.settings.get_setting("auto_clear_cookies"):
                profile.cookieStore().deleteAllCookies()
            
            if self.settings.get_setting("auto_clear_cache"):
                profile.clearHttpCache()
            
            if self.settings.get_setting("auto_clear_passwords"):
                self.clear_saved_passwords()
            
            if self.settings.get_setting("auto_clear_form_data"):
                self.clear_form_data()
            
            if self.settings.get_setting("auto_clear_downloads"):
                self.clear_downloads()
                
            print("Auto-clear data completed")
        except Exception as e:
            print(f"Error in auto-clear data: {str(e)}")

    def show_saved_passwords(self):
        """Muestra las contraseñas guardadas"""
        try:
            profile_path = QWebEngineProfile.defaultProfile().persistentStoragePath()
            login_db = os.path.join(profile_path, "Login Data")
            
            if os.path.exists(login_db):
                conn = sqlite3.connect(login_db)
                cursor = conn.cursor()
                cursor.execute("SELECT origin_url, username_value FROM logins")
                passwords = {row[0]: row[1] for row in cursor.fetchall()}
                conn.close()
                
                dialog = SavedDataDialog("Saved Passwords", passwords, self)
                dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading passwords: {str(e)}")

    def show_form_data(self):
        """Muestra los datos de formularios guardados"""
        try:
            profile_path = QWebEngineProfile.defaultProfile().persistentStoragePath()
            form_data_db = os.path.join(profile_path, "Web Data")
            
            if os.path.exists(form_data_db):
                conn = sqlite3.connect(form_data_db)
                cursor = conn.cursor()
                cursor.execute("SELECT name, value FROM autofill")
                form_data = {row[0]: row[1] for row in cursor.fetchall()}
                conn.close()
                
                dialog = SavedDataDialog("Saved Form Data", form_data, self)
                dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading form data: {str(e)}")

    def show_downloads(self):
        """Muestra el historial de descargas"""
        try:
            profile_path = QWebEngineProfile.defaultProfile().persistentStoragePath()
            downloads_db = os.path.join(profile_path, "History")
            
            if os.path.exists(downloads_db):
                conn = sqlite3.connect(downloads_db)
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT url, target_path, start_time 
                    FROM downloads 
                    JOIN downloads_url_chains ON downloads.id = downloads_url_chains.id
                """)
                downloads = {row[0]: f"Path: {row[1]}, Time: {row[2]}" for row in cursor.fetchall()}
                conn.close()
                
                dialog = SavedDataDialog("Download History", downloads, self)
                dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading downloads: {str(e)}")

    def show_history(self):
        """Muestra el diálogo de historial"""
        dialog = HistoryDialog(self.history_manager, self.parent)
        dialog.exec() 