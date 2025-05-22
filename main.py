import sys
from PySide6.QtWidgets import QApplication
from ui import MainWindow
import socket
from threading import Thread, Event
import traceback
import time
from maintag import BookmarkManager


class BookmarkListener(Thread):
    def __init__(self, navigation_manager):
        super().__init__()
        self.navigation_manager = navigation_manager
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(("localhost", 65432))
        self.server_socket.settimeout(1)  # Timeout para permitir verificar el flag de salida
        self.server_socket.listen(1)
        self._stop_event = Event()  # Evento para controlar la parada del thread
        self.daemon = True  # Thread demonio para terminar con el programa principal

    def run(self):
        while not self._stop_event.is_set():
            try:
                client_socket, _ = self.server_socket.accept()
                with client_socket:
                    url = client_socket.recv(1024).decode("utf-8").strip()
                    if url:
                        print(f"URL recibida: {url}")
                        try:
                            self.navigation_manager.navigate_to_url(url)
                        except Exception as e:
                            print(f"Error al manejar la URL: {e}")
            except socket.timeout:
                continue  # Timeout normal para verificar stop_event
            except Exception as e:
                if not self._stop_event.is_set():  # Solo mostrar errores si no estamos deteniendo
                    print(f"Error en BookmarkListener: {e}")
                    traceback.print_exc()

    def stop(self):
        """Detiene el thread de manera segura"""
        self._stop_event.set()
        
        # Forzar cierre del socket para desbloquear accept()
        try:
            # Conexión temporal para desbloquear el accept()
            temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            temp_socket.connect(("localhost", 65432))
            
            temp_socket.close()
        except:
            pass
            
        # Esperar a que el thread termine
        if self.is_alive():
            self.join(timeout=2)
            
        # Cerrar el socket principal
        try:
            self.server_socket.close()
        except:
            pass


class BrowserApplication:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.browser = MainWindow()
        
        # Iniciar el socket listener para URLs
        self.bookmark_listener = BookmarkListener(self.browser.navigation_manager)
        self.bookmark_listener.start()

    def run(self):
        self.browser.show()
        try:
            return self.app.exec()
        except Exception as e:
            print(f"Error en la aplicación: {e}")
            traceback.print_exc()
        finally:
            self.bookmark_listener.stop()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()


def exception_handler(type, value, tb):
    print("Excepción global no capturada:")
    print("".join(traceback.format_exception(type, value, tb)))

sys.excepthook = exception_handler