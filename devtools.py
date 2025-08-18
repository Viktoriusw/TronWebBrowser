from PySide6.QtWidgets import QDockWidget, QVBoxLayout, QToolBar, QPushButton, QTabWidget, QTabBar, QWidget
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import Qt

class DevToolsDock(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Developer Tools", parent)
        self.parent = parent
        self.browser = None
        
        # Crear widget central
        self.central_widget = QWidget()
        self.setWidget(self.central_widget)
        
        # Crear layout
        self.layout = QVBoxLayout(self.central_widget)
        
        # Crear vista de DevTools
        self.dev_tools_view = QWebEngineView()
        self.layout.addWidget(self.dev_tools_view)
        
        # Configurar tamaño mínimo
        self.setMinimumWidth(400)
        self.setMinimumHeight(300)

        # Aplicar tema oscuro
        self.setStyleSheet("""
            QDockWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QDockWidget::title {
                background-color: #1e1e1e;
                color: #ffffff;
                padding: 4px;
            }
            QWebEngineView {
                background-color: #2b2b2b;
                color: #ffffff;
            }
        """)
        
        # Forzar tema oscuro en la vista web (con manejo de errores)
        try:
            self.dev_tools_view.page().setBackgroundColor(Qt.black)
        except Exception as e:
            print(f"Error configurando color de fondo en DevTools: {e}")
        # Los estilos de fondo ahora se heredan del tema global

    def set_browser(self, browser):
        """Establece el navegador actual para las DevTools"""
        if isinstance(browser, QWebEngineView):
            self.browser = browser
            # Conectar las DevTools al navegador
            self.browser.page().setDevToolsPage(self.dev_tools_view.page())
            # Mostrar las DevTools
            self.dev_tools_view.page().setInspectedPage(self.browser.page())
        else:
            # Si no es un navegador válido, limpiar las DevTools
            self.browser = None
            self.dev_tools_view.setUrl(None)

    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        layout = QVBoxLayout(self)
        
        # Estilo oscuro
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QToolBar {
                background-color: #1e1e1e;
                border: none;
                spacing: 3px;
            }
            QPushButton {
                background-color: #0d47a1;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QPushButton:pressed {
                background-color: #0a3d91;
            }
            QTabWidget::pane {
                border: 1px solid #555555;
                background-color: #2b2b2b;
            }
            QTabBar::tab {
                background-color: #1e1e1e;
                color: #ffffff;
                padding: 8px 12px;
                border: 1px solid #555555;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #0d47a1;
            }
            QTabBar::tab:hover {
                background-color: #1565c0;
            }
        """)
        
        # Crear la barra de herramientas