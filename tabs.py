import json
import os
from PySide6.QtWidgets import QTabWidget, QMenu, QInputDialog
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl, Qt
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage

class TabManager:
    SESSION_FILE = "tab_session.json"

    def __init__(self, history_manager, parent):
        self.history_manager = history_manager
        self.parent = parent
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)  # Pestañas planas estilo 2016
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.on_tab_changed)
        self.add_new_tab()

    def add_new_tab(self, url="https://duckduckgo.com"):
        """Crea una nueva pestaña y la devuelve"""
        try:
            if not isinstance(url, str) or not url.strip():
                url = "https://duckduckgo.com"

            # Crear el navegador
            browser = QWebEngineView()
            browser.setUrl(QUrl(url))
            
            # Configurar el perfil
            profile = browser.page().profile()
            profile.setPersistentCookiesPolicy(QWebEngineProfile.AllowPersistentCookies)
            profile.setHttpCacheType(QWebEngineProfile.MemoryHttpCache)
            
            # Conectar señales
            browser.urlChanged.connect(self.on_url_changed)
            browser.urlChanged.connect(self.history_manager.record_history)
            browser.titleChanged.connect(lambda title: self.update_tab_title(title, browser))
            browser.iconChanged.connect(lambda icon: self.update_tab_icon(icon, browser))
            
            # Configurar menú contextual
            browser.setContextMenuPolicy(Qt.CustomContextMenu)
            browser.customContextMenuRequested.connect(lambda pos: self.show_context_menu(pos, browser))

            # Configurar descargas
            if hasattr(self.parent, 'navigation_manager'):
                self.parent.navigation_manager.setup_downloads(browser)

            # Configurar gestor de contraseñas
            if hasattr(self.parent, 'password_manager'):
                self.parent.password_manager.setup_browser(browser)

            # Añadir la pestaña
            index = self.tabs.addTab(browser, "New Tab")
            self.tabs.setCurrentIndex(index)
            
            # Actualizar la barra de URL si está disponible
            if hasattr(self.parent, 'url_bar'):
                self.parent.url_bar.setText(url)
                
            print(f"Pestaña creada exitosamente con URL: {url}")
            return browser
        except Exception as e:
            print(f"Error al crear una nueva pestaña: {str(e)}")
            return None

    def update_tab_icon(self, icon, browser):
        try:
            index = self.tabs.indexOf(browser)
            if index != -1:
                if icon.isNull():
                    icon = QIcon(":/icons/bookmark.png")
                self.tabs.setTabIcon(index, icon)
        except Exception as e:
            print(f"Error al actualizar el icono de la pestaña: {str(e)}")

    def update_tab_title(self, title, browser):
        try:
            index = self.tabs.indexOf(browser)
            if index != -1:
                if not title:
                    url = browser.url().toString()
                    title = url.split('/')[-1] if url else "New Tab"
                if len(title) > 30:
                    title = title[:27] + "..."
                self.tabs.setTabText(index, title)
                if self.tabs.currentWidget() == browser:
                    self.parent.setWindowTitle(f"{title} - Tron Browser")
        except Exception as e:
            print(f"Error al actualizar el título de la pestaña: {str(e)}")

    def close_tab(self, index):
        try:
            if self.tabs.count() > 1:
                self.tabs.removeTab(index)
                current_browser = self.tabs.currentWidget()
                if current_browser:
                    self.update_tab_title(current_browser.page().title(), current_browser)
        except Exception as e:
            print(f"Error al cerrar la pestaña: {str(e)}")

    def show_context_menu(self, pos, browser):
        try:
            menu = QMenu(self.parent)
            back_action = menu.addAction("Back")
            forward_action = menu.addAction("Forward")
            reload_action = menu.addAction("Reload")
            menu.addSeparator()
            open_in_new_tab = menu.addAction("Open in New Tab")
            menu.addSeparator()
            save_bookmark = menu.addAction("Save as Bookmark")
            action = menu.exec(browser.mapToGlobal(pos))
            if action == back_action:
                browser.back()
            elif action == forward_action:
                browser.forward()
            elif action == reload_action:
                browser.reload()
            elif action == open_in_new_tab:
                browser.page().runJavaScript(
                    f"var elem = document.elementFromPoint({pos.x()}, {pos.y()}); elem ? elem.href : null;",
                    self.open_link_in_new_tab
                )
            elif action == save_bookmark:
                current_url = browser.url().toString()
                if current_url:
                    self.parent.show_save_favorite_menu()
        except Exception as e:
            print(f"Error al mostrar el menú contextual: {str(e)}")

    def open_link_in_new_tab(self, link):
        try:
            if link:
                self.add_new_tab(link)
        except Exception as e:
            print(f"Error al abrir enlace en nueva pestaña: {str(e)}")

    def on_url_changed(self, url):
        """Maneja el cambio de URL en una pestaña"""
        try:
            # Actualizar la barra de URL si está disponible
            if hasattr(self.parent, 'url_bar'):
                self.parent.url_bar.setText(url.toString())
        except Exception as e:
            print(f"Error al actualizar la URL: {str(e)}")

    def on_tab_changed(self, index):
        try:
            current_browser = self.tabs.widget(index)
            if current_browser:
                if hasattr(self.parent, 'devtools_dock'):
                    self.parent.devtools_dock.set_browser(current_browser)
                if hasattr(self.parent, 'url_bar'):
                    self.parent.url_bar.setText(current_browser.url().toString())
                self.update_tab_title(current_browser.page().title(), current_browser)
                
                # Sincronizar con el módulo de scraping si está disponible
                if hasattr(self.parent, 'scraping_integration') and self.parent.scraping_integration:
                    current_url = current_browser.url().toString()
                    # Actualizar el widget del navegador en el scraping integration
                    self.parent.scraping_integration.browser_widget = current_browser
                    # Obtener el HTML de la página actual
                    current_browser.page().toHtml(
                        lambda html_content: self.parent.scraping_integration.update_content(html_content, current_url)
                    )
        except Exception as e:
            print(f"Error al cambiar de pestaña: {str(e)}")

    def guardar_sesion(self):
        """Guarda la sesión actual de pestañas (URL) en un archivo JSON"""
        session = []
        for i in range(self.tabs.count()):
            browser = self.tabs.widget(i)
            url = browser.url().toString()
            session.append({"url": url})
        try:
            with open(self.SESSION_FILE, "w", encoding="utf-8") as f:
                json.dump(session, f, ensure_ascii=False, indent=2)
            print(f"Sesión guardada con {len(session)} pestañas.")
        except Exception as e:
            print(f"Error al guardar la sesión: {e}")

    def restaurar_sesion(self):
        """Restaura la sesión de pestañas desde el archivo JSON"""
        if not os.path.exists(self.SESSION_FILE):
            print("No hay sesión guardada para restaurar.")
            return
        try:
            with open(self.SESSION_FILE, "r", encoding="utf-8") as f:
                session = json.load(f)
            while self.tabs.count() > 0:
                self.close_tab(0)
            for tab in session:
                self.add_new_tab(tab.get("url", "https://duckduckgo.com"))
            print(f"Sesión restaurada con {len(session)} pestañas.")
        except Exception as e:
            print(f"Error al restaurar la sesión: {e}")

    def buscar_pestanas(self, query):
        """Filtra las pestañas abiertas por título o URL"""
        query = query.lower().strip()
        for i in range(self.tabs.count()):
            browser = self.tabs.widget(i)
            title = self.tabs.tabText(i).lower()
            url = browser.url().toString().lower()
            visible = query in title or query in url or not query
            self.tabs.setTabVisible(i, visible)
