from PySide6.QtWidgets import (QMainWindow, QToolBar, QPushButton, QLineEdit, 
                              QDockWidget, QMenu, QMessageBox, QWidget, QVBoxLayout,
                              QSplitter, QFrame, QCheckBox)
from PySide6.QtCore import Qt, QUrl, QSettings
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile
from PySide6.QtGui import QIcon, QPalette, QColor, QAction, QCursor
from PySide6.QtWebEngineWidgets import QWebEngineView
from tabs import TabManager
from navigation import NavigationManager
from history import HistoryManager
from devtools import DevToolsDock
from privacy import PrivacyManager
import socket
import sqlite3
import os
import subprocess
from contextlib import closing
from maintag import BookmarkManager
from password_manager import PasswordManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tron Browser")
        self.setGeometry(100, 100, 1200, 800)
        
        # Crear el widget principal
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Crear el layout principal
        main_layout = QVBoxLayout(main_widget)
        
        # Inicializar componentes en el orden correcto
        self.history_manager = HistoryManager()
        self.bookmark_manager = BookmarkManager(self)
        self.password_manager = PasswordManager()
        self.navigation_manager = NavigationManager(self)
        self.tab_manager = TabManager(self.history_manager, self)
        
        # Crear la barra de navegación después de tener navigation_manager
        self.nav_bar = QToolBar("Navigation")
        self.url_bar = QLineEdit()
        self.setup_nav_bar()
        main_layout.addWidget(self.nav_bar)
        
        # Configurar el widget del navegador
        browser_widget = QWidget()
        browser_layout = QVBoxLayout(browser_widget)
        browser_layout.setContentsMargins(0, 0, 0, 0)
        browser_layout.setSpacing(0)
        browser_layout.addWidget(self.tab_manager.tabs)
        main_layout.addWidget(browser_widget)
        
        # Configurar paneles dock
        self.setup_dock_widgets()
        
        # Configurar tema y atajos
        self.setup_theme()
        self.setup_shortcuts()
        
        # Restaurar sesión
        self.tab_manager.restaurar_sesion()
        
        # Configurar cierre de la aplicación
        self.closeEvent = self.on_close
        
        # Asegurar que haya al menos una pestaña activa al iniciar
        self.tab_manager.add_new_tab()

    def setup_dock_widgets(self):
        # Configurar DevTools
        self.devtools_dock = DevToolsDock(self)
        self.devtools_dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.BottomDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, self.devtools_dock)
        self.devtools_dock.hide()
        
        # Configurar Bookmark Manager
        self.bookmark_dock = QDockWidget("Gestor de Marcadores", self)
        self.bookmark_dock.setWidget(self.bookmark_manager)
        self.bookmark_dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, self.bookmark_dock)
        self.bookmark_dock.hide()
        
        # Configurar Privacy Manager
        self.privacy_manager = PrivacyManager(self)
        self.privacy_dock = QDockWidget("Privacy Settings", self)
        self.privacy_dock.setWidget(self.privacy_manager)
        self.privacy_dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, self.privacy_dock)
        self.privacy_dock.hide()
        
        # Configurar Password Manager
        self.password_dock = QDockWidget("Gestor de Contraseñas", self)
        self.password_dock.setWidget(self.password_manager)
        self.password_dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, self.password_dock)
        self.password_dock.hide()

    def setup_theme(self):
        # Cargar configuración de tema
        self.settings = QSettings("TronBrowser", "Settings")
        self.load_theme()

    def setup_shortcuts(self):
        # ... (existing code)
        pass

    def on_close(self, event):
        # ... (existing code)
        pass

    def setup_nav_bar(self):
        # Back Button
        back_action = QAction(QIcon("icons/back.png"), "Back", self)
        back_action.triggered.connect(self.navigation_manager.navigate_back)
        self.nav_bar.addAction(back_action)

        # Forward Button
        forward_action = QAction(QIcon("icons/forward.png"), "Forward", self)
        forward_action.triggered.connect(self.navigation_manager.navigate_forward)
        self.nav_bar.addAction(forward_action)

        # Refresh Button
        refresh_action = QAction(QIcon("icons/refresh.png"), "Refresh", self)
        refresh_action.triggered.connect(self.navigation_manager.refresh_page)
        self.nav_bar.addAction(refresh_action)

        # New Tab Button
        new_tab_action = QAction(QIcon("icons/new-tab.png"), "New Tab", self)
        new_tab_action.triggered.connect(lambda: self.tab_manager.add_new_tab())
        self.nav_bar.addAction(new_tab_action)

        # History Button
        history_action = QAction(QIcon("icons/history.png"), "History", self)
        history_action.triggered.connect(lambda: self.history_manager.show_history(self.tab_manager))
        self.nav_bar.addAction(history_action)

        # URL Bar
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(lambda: self.load_url(self.url_bar.text()))
        self.nav_bar.addWidget(self.url_bar)

        # Botón para guardar favorito (heart)
        fav_action = QAction(QIcon("icons/heart.png"), "Fav", self)
        fav_action.triggered.connect(self.show_save_favorite_menu)
        self.nav_bar.addAction(fav_action)

        # Privacy Button (lock)
        privacy_action = QAction(QIcon("icons/lock.png"), "Privacy", self)
        privacy_action.triggered.connect(self.toggle_privacy_panel)
        self.nav_bar.addAction(privacy_action)

        # Password Manager Button (key)
        password_action = QAction(QIcon("icons/key.png"), "Password Manager", self)
        password_action.setToolTip("Gestor de Contraseñas")
        password_action.triggered.connect(self.toggle_password_manager)
        self.nav_bar.addAction(password_action)

        # DevTools Button (wrench)
        devtools_action = QAction(QIcon("icons/wrench.png"), "DevTools", self)
        devtools_action.setToolTip("Toggle Developer Tools")
        devtools_action.triggered.connect(self.toggle_devtools)
        self.nav_bar.addAction(devtools_action)

        # Botón para mostrar el gestor de marcadores
        bookmark_manager_action = QAction(QIcon("icons/bookmark.png"), "Bookmark Manager", self)
        bookmark_manager_action.triggered.connect(self.toggle_bookmark_manager)
        self.nav_bar.addAction(bookmark_manager_action)

        # Campo de búsqueda de pestañas
        self.tab_search = QLineEdit()
        self.tab_search.setPlaceholderText("Buscar pestañas abiertas...")
        self.tab_search.textChanged.connect(self.tab_manager.buscar_pestanas)
        self.nav_bar.addWidget(self.tab_search)

        # Theme Toggle Button
        self.theme_action = QAction(QIcon("icons/settings.png"), "Toggle Theme", self)
        self.theme_action.triggered.connect(self.toggle_theme)
        self.nav_bar.addAction(self.theme_action)

    def load_theme(self):
        """Carga el tema guardado o usa el tema por defecto"""
        theme = self.settings.value("theme", "light")
        self.apply_theme(theme)

    def apply_theme(self, theme):
        """Aplica el tema especificado"""
        if theme == "dark":
            self.set_dark_theme()
        else:
            self.set_light_theme()
        self.settings.setValue("theme", theme)

    def set_dark_theme(self):
        """Aplica el tema oscuro"""
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        self.setPalette(palette)

    def set_light_theme(self):
        """Aplica el tema claro"""
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(240, 240, 240))
        palette.setColor(QPalette.WindowText, Qt.black)
        palette.setColor(QPalette.Base, Qt.white)
        palette.setColor(QPalette.AlternateBase, QColor(233, 233, 233))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.black)
        palette.setColor(QPalette.Text, Qt.black)
        palette.setColor(QPalette.Button, QColor(240, 240, 240))
        palette.setColor(QPalette.ButtonText, Qt.black)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(0, 0, 255))
        palette.setColor(QPalette.Highlight, QColor(0, 120, 215))
        palette.setColor(QPalette.HighlightedText, Qt.white)
        self.setPalette(palette)

    def toggle_theme(self):
        """Alterna entre tema claro y oscuro"""
        current_theme = self.settings.value("theme", "light")
        new_theme = "dark" if current_theme == "light" else "light"
        self.apply_theme(new_theme)

    def toggle_bookmark_manager(self):
        """Alterna la visibilidad del gestor de marcadores"""
        if self.bookmark_dock.isVisible():
            self.bookmark_dock.hide()
        else:
            self.bookmark_dock.show()

    def toggle_privacy_panel(self):
        """Alterna la visibilidad del panel de privacidad"""
        if self.privacy_dock.isVisible():
            self.privacy_dock.hide()
        else:
            self.privacy_dock.show()

    def toggle_password_manager(self):
        """Alterna la visibilidad del gestor de contraseñas"""
        if self.password_dock.isVisible():
            self.password_dock.hide()
        else:
            self.password_dock.show()

    def load_url(self, url):
        """Carga una URL en una nueva pestaña"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Crear una nueva pestaña
            new_tab = self.tab_manager.add_new_tab()
            if new_tab:
                # Aplicar configuración de privacidad antes de cargar la URL
                if hasattr(self, 'privacy_manager'):
                    self.privacy_manager.apply_privacy_settings(new_tab)
                
                # Cargar la URL en la nueva pestaña
                new_tab.setUrl(QUrl(url))
                
                # Actualizar la barra de direcciones con la URL actual
                self.url_bar.setText(url)
                
                # Asegurarse de que la pestaña esté visible
                self.tab_manager.tabs.setCurrentWidget(new_tab)
            else:
                QMessageBox.warning(self, "Error", "No se pudo crear una nueva pestaña")
        except Exception as e:
            error_msg = f"Error al cargar la URL: {str(e)}"
            print(error_msg)  # Log detallado
            QMessageBox.critical(self, "Error", error_msg)

    def update_tab_title(self, title):
        """Actualiza el título de la pestaña actual"""
        current_tab = self.tab_manager.tabs.currentWidget()
        if current_tab:
            index = self.tab_manager.tabs.indexOf(current_tab)
            self.tab_manager.tabs.setTabText(index, title)

    def show_save_favorite_menu(self):
        """Muestra el menú para guardar favoritos con manejo seguro de BD"""
        try:
            with closing(self._get_db_connection()) as conn:
                if conn is None:
                    return

                cursor = conn.cursor()
                cursor.execute("SELECT name FROM categories")
                categories = [row[0] for row in cursor.fetchall()]

                menu = QMenu(self)
                for category in categories:
                    menu.addAction(category, lambda c=category: self.save_favorite_to_category(c))

                # Obtener la posición del botón de favoritos
                fav_action = self.sender()
                if isinstance(fav_action, QAction):
                    # Obtener la posición del botón en la barra de herramientas
                    button = self.nav_bar.widgetForAction(fav_action)
                    if button:
                        menu.exec(button.mapToGlobal(button.rect().bottomLeft()))
                    else:
                        # Si no podemos obtener el widget, mostrar el menú en la posición actual del cursor
                        menu.exec(QCursor.pos())
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error al cargar categorías: {e}")

    def save_favorite_to_category(self, category):
        """Guarda un favorito en la categoría especificada con transacción segura"""
        current_url = self.url_bar.text().strip()
        if not current_url:
            self.statusBar().showMessage("Error: No hay URL para guardar", 5000)
            return

        try:
            with closing(self._get_db_connection()) as conn:
                if conn is None:
                    return

                with conn:  # Usa el contexto como transacción
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO bookmarks (title, url, category, notes, tags) VALUES (?, ?, ?, ?, ?)",
                        ("Untitled", current_url, category, "Guardado desde el navegador", "No tags")
                    )
                self.statusBar().showMessage(f"Marcador guardado en '{category}'", 5000)
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Esta URL ya existe en la categoría seleccionada")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error al guardar marcador: {e}")

    def _get_db_connection(self):
        """Obtiene una conexión a la base de datos con manejo seguro"""
        try:
            conn = sqlite3.connect("bookmarks.db")
            conn.execute("PRAGMA foreign_keys = ON")
            return conn
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"No se pudo conectar a la base de datos: {e}")
            return None

    def toggle_devtools(self):
        """Alterna la visibilidad de las DevTools"""
        current_browser = self.tab_manager.tabs.currentWidget()
        if current_browser:
            if self.devtools_dock.isVisible():
                self.devtools_dock.hide()
            else:
                self.devtools_dock.set_browser(current_browser)
                self.devtools_dock.show()
                # Ajustar el tamaño del dock widget
                self.devtools_dock.setMinimumWidth(400)
                self.devtools_dock.setMinimumHeight(300)

    def toggle_favorites_bar(self):
        self.favorites_bar.setVisible(not self.favorites_bar.isVisible())

    def update_favorites_bar(self):
        """Actualiza la barra de favoritos con los favoritos marcados para mostrar en barra desde el gestor principal (maintag.py)"""
        self.favorites_bar.clear()
        # Obtener favoritos marcados para barra desde el gestor principal de marcadores
        if hasattr(self.bookmark_manager, 'get_favorites_for_bar'):
            favorites = self.bookmark_manager.get_favorites_for_bar()
            for fav in favorites:
                action = QAction(QIcon(fav['icon']), fav['title'], self)
                action.setToolTip(fav['url'])
                action.triggered.connect(lambda checked=False, url=fav['url']: self.load_url(url))
                self.favorites_bar.addAction(action)


