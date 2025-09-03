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

        # Eliminar estilos hardcodeados para heredar tema global
        
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
        
        # Eliminar estilos hardcodeados para heredar tema global
        
        # Crear la barra de herramientas