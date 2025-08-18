from PySide6.QtWidgets import (QMainWindow, QToolBar, QPushButton, QLineEdit, 
                              QDockWidget, QMenu, QMessageBox, QWidget, QVBoxLayout,
                              QSplitter, QFrame, QCheckBox, QTabWidget, QTextEdit,
                              QHBoxLayout, QLabel, QSpinBox, QComboBox)
from PySide6.QtCore import Qt, QUrl, QSettings, QSize
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile
from PySide6.QtGui import QIcon, QPalette, QColor, QAction, QCursor
from PySide6.QtWebEngineWidgets import QWebEngineView
from tabs import TabManager
from navigation import NavigationManager
from history import HistoryManager
from devtools import DevToolsDock
from privacy import PrivacyManager
from favorites_bar import FavoritesBar
import socket
import sqlite3
import os
import subprocess
from contextlib import closing
from maintag import BookmarkManager
from password_manager import PasswordManager
import urllib.parse
import json
import time

# Importar el módulo de integración de scraping
try:
    from scraping_integration import scraping_integration
    from scraping_panel import ScrapingPanel
    SCRAPING_AVAILABLE = True
    print("✅ Módulos de scraping cargados correctamente")
except ImportError as e:
    SCRAPING_AVAILABLE = False
    print(f"Advertencia: Módulo de scraping no disponible - {e}")

# Importar el módulo de gestión de proxies
try:
    from proxy_panel import ProxyPanel
    PROXY_AVAILABLE = True
    print("✅ Módulo de gestión de proxies cargado correctamente")
except ImportError as e:
    PROXY_AVAILABLE = False
    print(f"Advertencia: Módulo de gestión de proxies no disponible - {e}")

# Importar el módulo de chat con IA
try:
    from chat_panel_safe import ChatPanelSafe as ChatPanel
    CHAT_AVAILABLE = True
    print("✅ Módulo de chat con IA cargado correctamente")
except ImportError as e:
    CHAT_AVAILABLE = False
    print(f"Advertencia: Módulo de chat con IA no disponible - {e}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tron Browser")
        self.setGeometry(100, 100, 1200, 800)
        
        # Configurar ventana sin bordes internos
        self.setStyleSheet("""
            QMainWindow {
                border: none;
                margin: 0px;
                padding: 0px;
            }
        """)
        
        # Crear el widget principal
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Crear el layout principal horizontal para barra lateral SIN márgenes
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)  # Sin márgenes
        main_layout.setSpacing(0)  # Sin espaciado
        
        # Crear el contenedor principal (navegador)
        browser_container = QWidget()
        browser_layout = QVBoxLayout(browser_container)
        browser_layout.setContentsMargins(0, 0, 0, 0)
        browser_layout.setSpacing(0)
        
        # Inicializar componentes en el orden correcto
        self.history_manager = HistoryManager()
        self.bookmark_manager = BookmarkManager(self)
        self.password_manager = PasswordManager()
        self.navigation_manager = NavigationManager(self)
        self.tab_manager = TabManager(self.history_manager, self)
        self.navigation_manager.initialize_tab_manager(self.tab_manager)
        
        # Crear la barra de navegación después de tener navigation_manager
        self.nav_bar = QToolBar("Navigation")
        self.setup_nav_bar()
        browser_layout.addWidget(self.nav_bar)
        
        # Configurar el widget del navegador (pestañas)
        browser_layout.addWidget(self.tab_manager.tabs)
        
        # Añadir el contenedor principal al layout
        main_layout.addWidget(browser_container)
        
        # Crear barra lateral derecha
        self.setup_right_sidebar()
        main_layout.addWidget(self.sidebar)
        
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
        
        # Configurar Barra de Favoritos
        self.favorites_bar = FavoritesBar(self)
        self.favorites_bar.setAllowedAreas(Qt.TopToolBarArea | Qt.BottomToolBarArea)
        self.addToolBar(Qt.TopToolBarArea, self.favorites_bar)
        self.favorites_bar.hide()  # Inicialmente oculta
        # Conectar señal de clic en favorito
        self.favorites_bar.favorite_clicked.connect(self.load_url)
        
        # Configurar Privacy Manager
        self.privacy_manager = PrivacyManager(self)
        self.privacy_dock = QDockWidget("Privacy Settings", self)
        self.privacy_dock.setWidget(self.privacy_manager)
        self.privacy_dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, self.privacy_dock)
        self.privacy_dock.hide()
        
        # Conectar señal para aplicar cambios al vuelo
        self.privacy_manager.settings_changed.connect(self.reapply_privacy_to_all_tabs)
        
        # Configurar Password Manager
        self.password_dock = QDockWidget("Gestor de Contraseñas", self)
        self.password_dock.setWidget(self.password_manager)
        self.password_dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, self.password_dock)
        self.password_dock.hide()
        
        # Configurar Scraping Panel (si está disponible)
        if SCRAPING_AVAILABLE:
            self.scraping_integration = scraping_integration
            self.scraping_panel = ScrapingPanel(self.scraping_integration)
            self.scraping_dock = QDockWidget("🔍 Scrapelillo Completo", self)
            self.scraping_dock.setWidget(self.scraping_panel)
            self.scraping_dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
            self.addDockWidget(Qt.RightDockWidgetArea, self.scraping_dock)
            self.scraping_dock.hide()
            print("✅ Panel de scraping configurado correctamente")
        else:
            self.scraping_integration = None
            self.scraping_panel = None
            self.scraping_dock = None
            print("❌ Panel de scraping no disponible")
        
        # Configurar Proxy Panel (si está disponible)
        if PROXY_AVAILABLE:
            # Obtener el proxy manager del scraping integration si está disponible
            proxy_manager = None
            if SCRAPING_AVAILABLE and hasattr(scraping_integration, 'proxy_manager'):
                proxy_manager = scraping_integration.proxy_manager
            
            self.proxy_panel = ProxyPanel(proxy_manager)
            self.proxy_dock = QDockWidget("🌐 Gestión de Proxies", self)
            self.proxy_dock.setWidget(self.proxy_panel)
            self.proxy_dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
            self.addDockWidget(Qt.RightDockWidgetArea, self.proxy_dock)
            self.proxy_dock.hide()
            print("✅ Panel de gestión de proxies configurado correctamente")
        else:
            self.proxy_panel = None
            self.proxy_dock = None
            print("❌ Panel de gestión de proxies no disponible")
        
        # Configurar Chat Panel (si está disponible)
        if CHAT_AVAILABLE:
            self.chat_panel = ChatPanel()
            self.chat_dock = QDockWidget("🤖 Chat con IA", self)
            self.chat_dock.setWidget(self.chat_panel)
            self.chat_dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
            self.addDockWidget(Qt.RightDockWidgetArea, self.chat_dock)
            self.chat_dock.hide()
            print("✅ Panel de chat con IA configurado correctamente")
        else:
            self.chat_panel = None
            self.chat_dock = None
            print("❌ Panel de chat con IA no disponible")

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
        # Configurar toolbar moderno
        self.nav_bar.setIconSize(QSize(20, 20))
        self.nav_bar.setToolButtonStyle(Qt.ToolButtonIconOnly)
        
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

        # URL Bar con estilo pill
        self.url_bar = UrlBar(load_url_callback=self.load_url)
        self.url_bar.returnPressed.connect(lambda: self.load_url(self.url_bar.text()))
        self.url_bar.setFixedHeight(32)
        if hasattr(self.url_bar, "setClearButtonEnabled"):
            self.url_bar.setClearButtonEnabled(True)
        self.nav_bar.addWidget(self.url_bar)

        # Solo guardar referencia de las acciones para aplicar iconos después
        self.function_actions = {}

        # Campo de búsqueda de pestañas
        self.tab_search = QLineEdit()
        self.tab_search.setPlaceholderText("Buscar pestañas abiertas...")
        self.tab_search.textChanged.connect(self.tab_manager.buscar_pestanas)
        self.nav_bar.addWidget(self.tab_search)
        
        # Aplicar iconos vectoriales solo a navegación básica
        try:
            import qtawesome as qta
            back_action.setIcon(qta.icon('fa.angle-left'))
            forward_action.setIcon(qta.icon('fa.angle-right'))
            refresh_action.setIcon(qta.icon('fa.rotate-right'))
            new_tab_action.setIcon(qta.icon('fa.plus'))
            history_action.setIcon(qta.icon('fa.clock-o'))
            print("✅ Iconos vectoriales aplicados a navegación básica")
        except Exception as e:
            print(f"⚠️ Usando iconos PNG como fallback: {e}")
            pass  # Fallback: usar los QIcon("icons/*.png") ya definidos

    def setup_right_sidebar(self):
        """Configura la barra lateral derecha con botones de funciones"""
        # Crear el widget de la barra lateral
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(60)  # Ancho fijo de barra lateral
        self.sidebar.setStyleSheet("""
            QWidget {
                border: none;
                border-left: 1px solid rgba(128,128,128,0.2);
                border-radius: 0px;
                margin: 0px;
                padding: 0px;
            }
        """)
        
        # Layout vertical para los botones
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(6, 8, 6, 8)  # Márgenes mínimos pero funcionales
        sidebar_layout.setSpacing(4)
        
        # Función helper para crear botones de barra lateral
        def create_sidebar_button(icon_name, tooltip, callback, icon_fallback=None):
            btn = QPushButton()
            btn.setFixedSize(48, 48)
            btn.setToolTip(tooltip)
            btn.clicked.connect(callback)
            btn.setStyleSheet("""
                QPushButton {
                    border: 1px solid rgba(128,128,128,0.4);
                    border-radius: 6px;
                    padding: 8px;
                }
                QPushButton:hover {
                    background: rgba(0,120,215,0.1);
                    border: 1px solid rgba(0,120,215,0.5);
                }
                QPushButton:pressed {
                    background: rgba(0,120,215,0.2);
                }
            """)
            
            # Aplicar icono
            try:
                import qtawesome as qta
                btn.setIcon(qta.icon(icon_name))
                btn.setIconSize(QSize(24, 24))
            except:
                if icon_fallback:
                    btn.setIcon(QIcon(icon_fallback))
                    btn.setIconSize(QSize(24, 24))
                else:
                    btn.setText(tooltip[:2])  # Usar primeras 2 letras como fallback
            
            return btn
        
        # Crear botones de funciones
        self.fav_btn = create_sidebar_button('fa.heart', 'Guardar Favorito', 
                                           self.show_save_favorite_menu, 'icons/heart.png')
        sidebar_layout.addWidget(self.fav_btn)
        
        self.privacy_btn = create_sidebar_button('fa.lock', 'Privacidad', 
                                               self.toggle_privacy_panel, 'icons/lock.png')
        sidebar_layout.addWidget(self.privacy_btn)
        
        self.password_btn = create_sidebar_button('fa.key', 'Gestor de Contraseñas', 
                                                self.toggle_password_manager, 'icons/key.png')
        sidebar_layout.addWidget(self.password_btn)
        
        self.devtools_btn = create_sidebar_button('fa.wrench', 'DevTools', 
                                                self.toggle_devtools, 'icons/wrench.png')
        sidebar_layout.addWidget(self.devtools_btn)
        
        # Botones condicionales
        if SCRAPING_AVAILABLE:
            self.scraping_btn = create_sidebar_button('fa.search', 'Scraping', 
                                                    self.toggle_scraping_panel, 'icons/scrap.png')
            sidebar_layout.addWidget(self.scraping_btn)
        
        if PROXY_AVAILABLE:
            self.proxy_btn = create_sidebar_button('fa.globe', 'Proxies', 
                                                 self.toggle_proxy_panel, 'icons/proxy.png')
            sidebar_layout.addWidget(self.proxy_btn)
        
        if CHAT_AVAILABLE:
            self.chat_btn = create_sidebar_button('fa.commenting', 'Chat IA', 
                                                self.toggle_chat_panel, 'icons/chat.png')
            sidebar_layout.addWidget(self.chat_btn)
        
        self.bookmark_btn = create_sidebar_button('fa.bookmark', 'Marcadores', 
                                                self.toggle_bookmark_manager, 'icons/bookmark.png')
        sidebar_layout.addWidget(self.bookmark_btn)
        
        self.favorites_btn = create_sidebar_button('fa.star', 'Barra de Favoritos', 
                                                 self.toggle_favorites_bar, 'icons/heart.png')
        sidebar_layout.addWidget(self.favorites_btn)
        
        self.theme_btn = create_sidebar_button('fa.adjust', 'Cambiar Tema', 
                                             self.toggle_theme, 'icons/settings.png')
        sidebar_layout.addWidget(self.theme_btn)
        
        # Espaciador flexible para empujar botones hacia arriba
        sidebar_layout.addStretch()

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
        from PySide6.QtWidgets import QApplication
        
        # Usar paleta Qt nativa para tema oscuro
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
        
        # Aplicar a toda la aplicación
        app = QApplication.instance()
        app.setPalette(palette)
        
        # Aplicar estilos personalizados con tema oscuro
        self._apply_dark_styles()
        print("✅ Tema oscuro aplicado")

    def set_light_theme(self):
        """Aplica el tema claro"""
        from PySide6.QtWidgets import QApplication
        
        # Usar paleta Qt nativa para tema claro
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
        
        # Aplicar a toda la aplicación
        app = QApplication.instance()
        app.setPalette(palette)
        
        # Aplicar estilos personalizados con tema claro
        self._apply_light_styles()
        print("✅ Tema claro aplicado")

    def _load_custom_styles(self):
        """Carga estilos QSS personalizados desde themes/modern.qss"""
        try:
            import os
            qss_path = "themes/modern.qss"
            if os.path.exists(qss_path):
                with open(qss_path, "r", encoding="utf-8") as f:
                    return f.read()
            return ""
        except Exception as e:
            print(f"Error cargando estilos personalizados: {e}")
            return ""

    def _apply_light_styles(self):
        """Aplica estilos QSS para tema claro"""
        try:
            from PySide6.QtWidgets import QApplication
            custom_qss = self._load_custom_styles()
            
            # Estilos específicos para tema claro
            light_qss = """
            /* Tema claro - Fuentes oscuras */
            * { color: #000000; margin: 0px; padding: 0px; border: none; }
            QMainWindow { margin: 0px; padding: 0px; border: none; }
            QWidget { color: #000000; background-color: #f5f5f5; margin: 0px; }
            QLabel { color: #000000; }
            QLineEdit { color: #000000; background-color: #ffffff; }
            QPushButton { color: #000000; background-color: #e0e0e0; }
            QGroupBox { color: #000000; }
            QCheckBox { color: #000000; }
            QComboBox { color: #000000; background-color: #ffffff; }
            QListWidget { color: #000000; background-color: #ffffff; }
            QTextEdit { color: #000000; background-color: #ffffff; }
            QTreeWidget { color: #000000; background-color: #ffffff; }
            QTableWidget { color: #000000; background-color: #ffffff; }
            
            /* Overrides específicos */
            QToolBar { background: #f5f6f7; color: #000000; margin: 0px; border: none; }
            QTabWidget::pane { background: #f8f8f8; margin: 0px; }
            QTabBar::tab { background: #ececec; color: #000000; }
            QTabBar::tab:selected { background: #ffffff; color: #000000; }
            QDockWidget::title { background: #f0f0f0; color: #000000; }
            """
            
            app = QApplication.instance()
            app.setStyleSheet(custom_qss + "\n" + light_qss)
        except Exception as e:
            print(f"Error aplicando estilos del tema claro: {e}")

    def _apply_dark_styles(self):
        """Aplica estilos QSS para tema oscuro"""
        try:
            from PySide6.QtWidgets import QApplication
            custom_qss = self._load_custom_styles()
            
            # Estilos específicos para tema oscuro
            dark_qss = """
            /* Tema oscuro - Fuentes claras */
            * { color: #ffffff; margin: 0px; padding: 0px; border: none; }
            QMainWindow { margin: 0px; padding: 0px; border: none; }
            QWidget { color: #ffffff; background-color: #2b2b2b; margin: 0px; }
            QLabel { color: #ffffff; }
            QLineEdit { color: #ffffff; background-color: #404040; }
            QPushButton { color: #ffffff; background-color: #404040; }
            QGroupBox { color: #ffffff; }
            QCheckBox { color: #ffffff; }
            QComboBox { color: #ffffff; background-color: #404040; }
            QListWidget { color: #ffffff; background-color: #353535; }
            QTextEdit { color: #ffffff; background-color: #353535; }
            QTreeWidget { color: #ffffff; background-color: #353535; }
            QTableWidget { color: #ffffff; background-color: #353535; }
            
            /* Overrides específicos */
            QToolBar { background: #3c3c3c; color: #ffffff; margin: 0px; border: none; }
            QTabWidget::pane { background: #2b2b2b; margin: 0px; }
            QTabBar::tab { background: #404040; color: #ffffff; }
            QTabBar::tab:selected { background: #535353; color: #ffffff; }
            QDockWidget::title { background: #404040; color: #ffffff; }
            """
            
            app = QApplication.instance()
            app.setStyleSheet(custom_qss + "\n" + dark_qss)
        except Exception as e:
            print(f"Error aplicando estilos del tema oscuro: {e}")

    def _apply_custom_styles(self):
        """Método legacy - mantener por compatibilidad"""
        self._apply_light_styles()

    def toggle_theme(self):
        """Alterna entre tema claro y oscuro"""
        current_theme = self.settings.value("theme", "light")
        new_theme = "dark" if current_theme == "light" else "light"
        print(f"🔄 Cambiando tema de {current_theme} a {new_theme}")
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
        """Carga una URL o realiza una búsqueda en DuckDuckGo"""
        try:
            url = url.strip()
            # Si es una URL válida, navega directo
            if url.startswith(('http://', 'https://')) or ('.' in url and ' ' not in url):
                final_url = url if url.startswith(('http://', 'https://')) else 'https://' + url
            else:
                # Si no es URL, realiza búsqueda en DuckDuckGo
                query = urllib.parse.quote(url)
                final_url = f'https://duckduckgo.com/?q={query}'
            
            # Crear una nueva pestaña
            new_tab = self.tab_manager.add_new_tab()
            if new_tab:
                if hasattr(self, 'privacy_manager'):
                    self.privacy_manager.apply_privacy_settings(new_tab)
                
                # Conectar la señal de carga terminada para sincronizar con scraping
                new_tab.loadFinished.connect(lambda success: self.on_page_loaded(new_tab, final_url))
                
                new_tab.setUrl(QUrl(final_url))
                self.url_bar.setText(final_url)
                self.tab_manager.tabs.setCurrentWidget(new_tab)
            else:
                QMessageBox.warning(self, "Error", "No se pudo crear una nueva pestaña")
        except Exception as e:
            error_msg = f"Error al cargar la URL: {str(e)}"
            print(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
    
    def on_page_loaded(self, browser_tab, url):
        """Callback cuando se termina de cargar una página"""
        try:
            # Obtener el HTML de la página cargada
            browser_tab.page().toHtml(lambda html_content: self.on_html_loaded(html_content, url))
            
            # También actualizar el scraping integration con el widget del navegador
            if SCRAPING_AVAILABLE and self.scraping_integration:
                self.scraping_integration.browser_widget = browser_tab
                
        except Exception as e:
            print(f"Error en on_page_loaded: {e}")
    
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

    def toggle_scraping_panel(self):
        """Alterna la visibilidad del panel de scraping"""
        if SCRAPING_AVAILABLE and self.scraping_dock:
            if self.scraping_dock.isVisible():
                self.scraping_dock.hide()
                self.statusBar().showMessage("Panel de Scraping oculto", 3000)
            else:
                self.scraping_dock.show()
                # Ajustar el tamaño del dock widget
                self.scraping_dock.setMinimumWidth(400)
                self.scraping_dock.setMinimumHeight(500)
                # Actualizar el contenido de la página actual en el scraping integration
                self.update_scraping_content()
                self.statusBar().showMessage("🔍 Panel de Scraping abierto - Analiza y extrae datos de la página", 5000)
        else:
            QMessageBox.information(self, "🔍 Scraping", "Las herramientas de scraping no están disponibles. Verifica que scraping_integration.py esté presente.")
    
    def toggle_proxy_panel(self):
        """Alterna la visibilidad del panel de gestión de proxies"""
        if PROXY_AVAILABLE and self.proxy_dock:
            if self.proxy_dock.isVisible():
                self.proxy_dock.hide()
                self.statusBar().showMessage("Panel de Proxies oculto", 3000)
            else:
                self.proxy_dock.show()
                # Ajustar el tamaño del dock widget
                self.proxy_dock.setMinimumWidth(400)
                self.proxy_dock.setMinimumHeight(500)
                # Actualizar la lista de proxies si es necesario
                if hasattr(self, 'proxy_panel') and self.proxy_panel:
                    self.proxy_panel.refresh_proxy_list()
                self.statusBar().showMessage("🌐 Panel de Proxies abierto - Gestiona y configura proxies", 5000)
        else:
            QMessageBox.information(self, "🌐 Proxies", "Las herramientas de gestión de proxies no están disponibles. Verifica que proxy_panel.py esté presente.")
    
    def toggle_chat_panel(self):
        """Alterna la visibilidad del panel de chat con IA"""
        if CHAT_AVAILABLE and self.chat_dock:
            if self.chat_dock.isVisible():
                self.chat_dock.hide()
                self.statusBar().showMessage("Panel de Chat oculto", 3000)
            else:
                self.chat_dock.show()
                # Ajustar el tamaño del dock widget
                self.chat_dock.setMinimumWidth(400)
                self.chat_dock.setMinimumHeight(600)
                self.statusBar().showMessage("🤖 Panel de Chat abierto - Conversa con IA usando LM Studio", 5000)
        else:
            QMessageBox.information(self, "🤖 Chat IA", "Las herramientas de chat con IA no están disponibles. Verifica que chat_panel.py esté presente.")

    def update_scraping_content(self):
        """Actualiza el contenido de la página actual en el scraping integration"""
        if SCRAPING_AVAILABLE and self.scraping_integration:
            current_browser = self.tab_manager.tabs.currentWidget()
            if current_browser:
                # Obtener la URL actual
                current_url = current_browser.url().toString()
                
                # Actualizar el widget del navegador en el scraping integration
                self.scraping_integration.browser_widget = current_browser
                
                # Conectar eventos de clic para selección interactiva
                self.setup_interactive_selection(current_browser)
                
                # Obtener el HTML de la página actual
                current_browser.page().toHtml(lambda html_content: self.on_html_loaded(html_content, current_url))
    
    def setup_interactive_selection(self, browser_tab):
        """Configurar selección interactiva para una pestaña del navegador"""
        try:
            if SCRAPING_AVAILABLE and hasattr(self, 'scraping_panel'):
                # Inyectar JavaScript para detectar clics
                js_code = """
                // Global variables
                window.interactiveSelectionActive = false;
                window.selectedElements = [];
                
                // Simple click detection
                document.addEventListener('click', function(event) {
                    if (window.interactiveSelectionActive) {
                        event.preventDefault();
                        event.stopPropagation();
                        
                        var element = event.target;
                        var text = element.textContent.trim();
                        
                        // Only process elements with meaningful content
                        if (text && text.length > 2) {
                            var selector = generateSelector(element);
                            var elementInfo = {
                                tag: element.tagName.toLowerCase(),
                                text: text.substring(0, 100),
                                selector: selector,
                                href: element.href || '',
                                alt: element.alt || '',
                                className: element.className || '',
                                id: element.id || ''
                            };
                            
                            // Add to selected elements
                            window.selectedElements.push(elementInfo);
                            
                            // Visual feedback
                            highlightElement(element);
                            
                            // Show notification
                            showNotification('Elemento añadido: ' + text.substring(0, 50));
                            
                            // Log for debugging
                            console.log('Element added:', elementInfo);
                        }
                    }
                });
                
                function generateSelector(element) {
                    if (element.id) {
                        return '#' + element.id;
                    } else if (element.className) {
                        return '.' + element.className.split(' ').join('.');
                    } else {
                        return element.tagName.toLowerCase();
                    }
                }
                
                function highlightElement(element) {
                    element.style.outline = '3px solid #ff6b6b';
                    element.style.outlineOffset = '2px';
                    element.style.backgroundColor = 'rgba(255, 107, 107, 0.1)';
                    
                    setTimeout(function() {
                        element.style.outline = '';
                        element.style.outlineOffset = '';
                        element.style.backgroundColor = '';
                    }, 2000);
                }
                
                function showNotification(message) {
                    // Create notification element
                    var notification = document.createElement('div');
                    notification.style.cssText = `
                        position: fixed;
                        top: 20px;
                        right: 20px;
                        background: #4CAF50;
                        color: white;
                        padding: 10px 15px;
                        border-radius: 5px;
                        z-index: 10000;
                        font-family: Arial, sans-serif;
                        font-size: 14px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
                    `;
                    notification.textContent = message;
                    document.body.appendChild(notification);
                    
                    setTimeout(function() {
                        if (document.body.contains(notification)) {
                            document.body.removeChild(notification);
                        }
                    }, 3000);
                }
                
                // Toggle function
                window.toggleInteractiveSelection = function(active) {
                    window.interactiveSelectionActive = active;
                    console.log('Interactive selection:', active ? 'ACTIVATED' : 'DEACTIVATED');
                    
                    if (active) {
                        document.body.style.cursor = 'crosshair';
                        document.body.style.userSelect = 'none';
                        showNotification('Selección interactiva ACTIVADA - Haz clic en elementos para añadirlos');
                    } else {
                        document.body.style.cursor = '';
                        document.body.style.userSelect = '';
                        showNotification('Selección interactiva DESACTIVADA');
                    }
                };
                
                // Function to get selected elements
                window.getSelectedElements = function() {
                    console.log('Getting selected elements:', window.selectedElements.length);
                    return window.selectedElements;
                };
                
                // Function to clear selected elements
                window.clearSelectedElements = function() {
                    window.selectedElements = [];
                    console.log('Cleared selected elements');
                };
                
                // Initialize
                console.log('Interactive selection script loaded');
                """
                
                # Inyectar el código JavaScript
                browser_tab.page().runJavaScript(js_code)
                
                # Conectar el panel de scraping con el navegador
                if hasattr(self.scraping_panel, 'handle_page_click'):
                    # Crear un bridge para comunicación
                    self.scraping_panel.browser_tab = browser_tab
                    
        except Exception as e:
            print(f"Error configurando selección interactiva: {e}")
    
    def handle_element_click(self, click_data):
        """Manejar clic en elemento de la página"""
        try:
            if SCRAPING_AVAILABLE and hasattr(self, 'scraping_panel'):
                x = click_data.get('x', 0)
                y = click_data.get('y', 0)
                self.scraping_panel.handle_page_click(x, y)
        except Exception as e:
            print(f"Error manejando clic en elemento: {e}")

    def on_html_loaded(self, html_content, url):
        """Callback cuando se carga el HTML de la página"""
        if SCRAPING_AVAILABLE and self.scraping_integration:
            self.scraping_integration.update_content(html_content, url)

    def toggle_favorites_bar(self):
        """Alterna la visibilidad de la barra de favoritos"""
        if hasattr(self, 'favorites_bar'):
            if self.favorites_bar.isVisible():
                self.favorites_bar.hide()
                self.statusBar().showMessage("Barra de favoritos oculta", 3000)
            else:
                self.favorites_bar.show()
                self.favorites_bar.refresh_favorites()  # Actualizar favoritos
                self.statusBar().showMessage("Barra de favoritos visible", 3000)
        else:
            QMessageBox.information(self, "Barra de Favoritos", "La barra de favoritos no está disponible.")

    def update_favorites_bar(self):
        """Actualiza la barra de favoritos con los favoritos marcados para mostrar en barra desde el gestor principal (maintag.py)"""
        if hasattr(self, 'favorites_bar'):
            self.favorites_bar.refresh_favorites()

    def reapply_privacy_to_all_tabs(self):
        """Aplica la configuración de privacidad a todas las pestañas abiertas"""
        try:
            if not (hasattr(self, 'tab_manager') and self.tab_manager and hasattr(self, 'privacy_manager')):
                print("Tab manager o privacy manager no disponibles")
                return

            # Obtener todas las pestañas
            tabs_count = self.tab_manager.tabs.count()
            if tabs_count == 0:
                print("No hay pestañas abiertas")
                return
            
            # Variables para controlar recarga
            needs_reload = False
            
            # Verificar si cambios críticos requieren recarga
            current_block_ads = self.privacy_manager.settings.get_setting("block_ads")
            current_block_third_party = self.privacy_manager.settings.get_setting("block_third_party")
            current_block_javascript = self.privacy_manager.settings.get_setting("block_javascript")
            
            # Inicializar estados previos si no existen
            if not hasattr(self, '_last_privacy_settings'):
                self._last_privacy_settings = {
                    'block_ads': current_block_ads,
                    'block_third_party': current_block_third_party,
                    'block_javascript': current_block_javascript
                }
            else:
                # Verificar si hubo cambios que requieren recarga
                if (self._last_privacy_settings['block_ads'] != current_block_ads or 
                    self._last_privacy_settings['block_third_party'] != current_block_third_party):
                    needs_reload = True
                    print("Detectados cambios en filtros de red - programando recarga")
                
                # Actualizar estados guardados
                self._last_privacy_settings.update({
                    'block_ads': current_block_ads,
                    'block_third_party': current_block_third_party,
                    'block_javascript': current_block_javascript
                })
            
            # Aplicar configuración a cada pestaña
            successful_applications = 0
            failed_applications = 0
            
            for i in range(tabs_count):
                try:
                    tab = self.tab_manager.tabs.widget(i)
                    if tab and hasattr(tab, 'page'):
                        # Aplicar configuración de privacidad
                        self.privacy_manager.apply_privacy_settings(tab)
                        successful_applications += 1
                        
                        # Recarga suave si es necesario para cambios de filtros de red
                        if needs_reload:
                            try:
                                # Solo recargar si la pestaña tiene contenido
                                current_url = tab.url()
                                if not current_url.isEmpty() and current_url.toString() != "about:blank":
                                    tab.reload()
                                    print(f"Pestaña {i+1} recargada: {current_url.toString()[:50]}...")
                            except Exception as reload_error:
                                print(f"Error al recargar pestaña {i+1}: {reload_error}")
                                
                except Exception as tab_error:
                    print(f"Error al aplicar privacidad a pestaña {i+1}: {tab_error}")
                    failed_applications += 1
            
            # Reporte de resultados
            print(f"Configuración de privacidad aplicada: {successful_applications}/{tabs_count} pestañas exitosas")
            if failed_applications > 0:
                print(f"Errores en {failed_applications} pestañas")
            if needs_reload:
                print("Pestañas con contenido recargadas para aplicar filtros de red")
                    
        except Exception as e:
            print(f"Error crítico al reaplicar configuración de privacidad: {e}")
            import traceback
            traceback.print_exc()


class UrlBar(QLineEdit):
    def __init__(self, parent=None, load_url_callback=None):
        super().__init__(parent)
        self.load_url_callback = load_url_callback

    def insertFromMimeData(self, source):
        # Llama al método original para pegar el texto
        super().insertFromMimeData(source)
        text = self.text().strip()
        if self.load_url_callback and text:
            # Si el texto pegado es un enlace, navega automáticamente
            if text.startswith(('http://', 'https://')) or ('.' in text and ' ' not in text):
                self.load_url_callback(text)





