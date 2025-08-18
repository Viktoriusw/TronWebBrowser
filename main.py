import sys
import socket
import traceback
import time
from threading import Thread, Event
from PySide6.QtWidgets import QApplication
from ui import MainWindow

# Manejo global de excepciones antes de cualquier inicialización
def exception_handler(type, value, tb):
    print("Excepción global no capturada:")
    print("".join(traceback.format_exception(type, value, tb)))

sys.excepthook = exception_handler

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
                if not self._stop_event.is_set():
                    print(f"Error en BookmarkListener: {e}")
                    traceback.print_exc()

    def stop(self):
        """Detiene el thread de manera segura"""
        self._stop_event.set()
        try:
            # Conexión temporal para desbloquear el accept()
            temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            temp_socket.connect(("localhost", 65432))
            temp_socket.close()
        except Exception:
            pass
        if self.is_alive():
            self.join(timeout=2)
        try:
            self.server_socket.close()
        except Exception:
            pass

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    # Iniciar el socket listener para URLs después de verificar que navigation_manager existe
    bookmark_listener = None
    if hasattr(window, 'navigation_manager') and window.navigation_manager:
        bookmark_listener = BookmarkListener(window.navigation_manager)
        bookmark_listener.start()
    else:
        print("Advertencia: Navigation manager no disponible, socket listener deshabilitado")
    window.show()
    try:
        exit_code = app.exec()
    except Exception as e:
        print(f"Error en la aplicación: {e}")
        traceback.print_exc()
        exit_code = 1
    finally:
        if bookmark_listener:
            bookmark_listener.stop()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()