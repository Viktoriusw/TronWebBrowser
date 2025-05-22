from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                              QLabel, QProgressBar, QFileDialog, QMessageBox)
from PySide6.QtCore import Qt, Signal, QObject, QStandardPaths, QTimer
from PySide6.QtWebEngineCore import QWebEngineDownloadRequest
from PySide6.QtGui import QIcon, QPixmap
import os
import re
from pathlib import Path
import mimetypes

class DownloadManager(QObject):
    download_started = Signal(str)
    download_progress = Signal(int)
    download_completed = Signal(str)
    download_failed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.safe_chars = re.compile(r'[^\\/\w\d\-_\.\s]', re.ASCII)  # Caracteres permitidos en nombres de archivo
        self.downloads = {}
        self.init_ui()
        self.init_mime_types()

    def init_mime_types(self):
        """Inicializa los tipos MIME y sus descripciones"""
        self.mime_descriptions = {
            # Documentos
            'application/pdf': 'Documento PDF',
            'application/msword': 'Documento Word',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'Documento Word',
            'application/vnd.ms-excel': 'Hoja de cálculo Excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'Hoja de cálculo Excel',
            'application/vnd.ms-powerpoint': 'Presentación PowerPoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'Presentación PowerPoint',
            'text/plain': 'Archivo de texto',
            'text/html': 'Página web',
            'text/css': 'Hoja de estilos',
            'text/javascript': 'Script JavaScript',
            
            # Imágenes
            'image/jpeg': 'Imagen JPEG',
            'image/png': 'Imagen PNG',
            'image/gif': 'Imagen GIF',
            'image/svg+xml': 'Imagen vectorial SVG',
            'image/webp': 'Imagen WebP',
            
            # Audio
            'audio/mpeg': 'Archivo de audio MP3',
            'audio/wav': 'Archivo de audio WAV',
            'audio/ogg': 'Archivo de audio OGG',
            'audio/webm': 'Archivo de audio WebM',
            
            # Video
            'video/mp4': 'Video MP4',
            'video/webm': 'Video WebM',
            'video/ogg': 'Video OGG',
            
            # Comprimidos
            'application/zip': 'Archivo ZIP',
            'application/x-rar-compressed': 'Archivo RAR',
            'application/x-7z-compressed': 'Archivo 7Z',
            'application/x-tar': 'Archivo TAR',
            'application/gzip': 'Archivo GZIP',
            
            # Ejecutables
            'application/x-msdownload': 'Aplicación Windows',
            'application/x-executable': 'Aplicación ejecutable',
            'application/x-shockwave-flash': 'Aplicación Flash',
            
            # Otros
            'application/json': 'Archivo JSON',
            'application/xml': 'Archivo XML',
            'application/octet-stream': 'Archivo binario'
        }

    def init_ui(self):
        self.widget = QWidget()
        layout = QVBoxLayout(self.widget)
        
        # Título
        title = QLabel("Downloads")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # Lista de descargas
        self.downloads_layout = QVBoxLayout()
        layout.addLayout(self.downloads_layout)
        
        self.widget.setLayout(layout)

    def _sanitize_filename(self, filename):
        """Limpia el nombre de archivo de caracteres potencialmente peligrosos"""
        if not filename:
            return "download"
        
        # Elimina caracteres no seguros
        clean_name = self.safe_chars.sub('', filename)
        
        # Limita la longitud del nombre
        clean_name = clean_name[:150]  # Longitud máxima razonable
        
        return clean_name or "download"  # Fallback si queda vacío

    def _get_safe_download_dir(self):
        """Obtiene un directorio seguro para descargas"""
        # Usa el directorio de descargas del sistema por defecto
        download_dir = QStandardPaths.writableLocation(QStandardPaths.DownloadLocation)
        
        # Verifica que el directorio existe y es escribible
        if not os.access(download_dir, os.W_OK):
            download_dir = os.path.expanduser("~")  # Fallback al home del usuario
        
        return download_dir

    def handle_download(self, download):
        """Maneja una nueva descarga"""
        try:
            # Obtener el nombre del archivo de la URL
            suggested_name = download.suggestedFileName()
            if not suggested_name:
                suggested_name = "download"

            # Mostrar diálogo para seleccionar ubicación
            file_path, _ = QFileDialog.getSaveFileName(
                self.parent,
                "Save File",
                os.path.expanduser(f"~/Downloads/{suggested_name}"),
                "All Files (*.*)"
            )

            if file_path:
                # Configurar la descarga
                download.setDownloadDirectory(os.path.dirname(file_path))
                download.setDownloadFileName(os.path.basename(file_path))
                
                # Conectar señales
                download.stateChanged.connect(
                    lambda state: self.download_state_changed(download, state)
                )
                
                # Iniciar la descarga
                download.accept()
                
                # Crear widget de descarga
                self.create_download_widget(download, file_path)
                
                self.download_started.emit(file_path)
            else:
                download.cancel()
                
        except Exception as e:
            print(f"Error al manejar descarga: {str(e)}")
            self.download_failed.emit(str(e))

    def download_state_changed(self, download, state):
        """Maneja los cambios de estado de la descarga"""
        try:
            if download in self.downloads:
                if state == QWebEngineDownloadRequest.DownloadCompleted:
                    self.downloads[download]['progress_bar'].setValue(100)
                    self.download_completed.emit(self.downloads[download]['path'])
                    self.show_download_confirmation(self.downloads[download]['path'])
                    # Limpiar después de un tiempo
                    QTimer.singleShot(5000, lambda: self.cleanup_download(download))
                elif state == QWebEngineDownloadRequest.DownloadCancelled:
                    self.download_failed.emit("Download cancelled")
                    self.cleanup_download(download)
                elif state == QWebEngineDownloadRequest.DownloadInProgress:
                    # Actualizar progreso
                    received = download.receivedBytes()
                    total = download.totalBytes()
                    if total > 0:
                        progress = int((received / total) * 100)
                        self.downloads[download]['progress_bar'].setValue(progress)
                        self.download_progress.emit(progress)
        except Exception as e:
            print(f"Error al manejar cambio de estado: {str(e)}")

    def get_file_type_info(self, file_path):
        """Obtiene información sobre el tipo de archivo"""
        try:
            # Obtener el tipo MIME
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                # Intentar determinar el tipo por la extensión
                ext = os.path.splitext(file_path)[1].lower()
                if ext == '.pdf':
                    mime_type = 'application/pdf'
                elif ext in ['.doc', '.docx']:
                    mime_type = 'application/msword'
                elif ext in ['.xls', '.xlsx']:
                    mime_type = 'application/vnd.ms-excel'
                elif ext in ['.ppt', '.pptx']:
                    mime_type = 'application/vnd.ms-powerpoint'
                elif ext in ['.jpg', '.jpeg']:
                    mime_type = 'image/jpeg'
                elif ext == '.png':
                    mime_type = 'image/png'
                elif ext == '.gif':
                    mime_type = 'image/gif'
                elif ext in ['.mp3', '.wav', '.ogg']:
                    mime_type = 'audio/mpeg'
                elif ext in ['.mp4', '.webm']:
                    mime_type = 'video/mp4'
                elif ext in ['.zip', '.rar', '.7z']:
                    mime_type = 'application/zip'
                else:
                    mime_type = 'application/octet-stream'

            # Obtener la descripción
            description = self.mime_descriptions.get(mime_type, 'Archivo desconocido')
            
            # Obtener el icono según el tipo
            icon_name = self._get_icon_name(mime_type)
            
            return {
                'mime_type': mime_type,
                'description': description,
                'icon': icon_name
            }
        except Exception as e:
            print(f"Error al obtener tipo de archivo: {str(e)}")
            return {
                'mime_type': 'application/octet-stream',
                'description': 'Archivo desconocido',
                'icon': 'unknown'
            }

    def _get_icon_name(self, mime_type):
        """Obtiene el nombre del icono según el tipo MIME"""
        if mime_type.startswith('image/'):
            return 'image'
        elif mime_type.startswith('video/'):
            return 'video'
        elif mime_type.startswith('audio/'):
            return 'audio'
        elif mime_type.startswith('text/'):
            return 'text'
        elif mime_type == 'application/pdf':
            return 'pdf'
        elif mime_type in ['application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
            return 'word'
        elif mime_type in ['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']:
            return 'excel'
        elif mime_type in ['application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.presentationml.presentation']:
            return 'powerpoint'
        elif mime_type in ['application/zip', 'application/x-rar-compressed', 'application/x-7z-compressed']:
            return 'archive'
        elif mime_type in ['application/x-msdownload', 'application/x-executable']:
            return 'executable'
        else:
            return 'unknown'

    def create_download_widget(self, download, file_path):
        """Crea un widget para mostrar el progreso de la descarga"""
        try:
            container = QWidget()
            layout = QHBoxLayout(container)
            
            # Obtener información del tipo de archivo
            file_info = self.get_file_type_info(file_path)
            
            # Contenedor para el icono y nombre
            info_container = QWidget()
            info_layout = QVBoxLayout(info_container)
            
            # Icono del tipo de archivo
            icon_label = QLabel()
            icon_label.setPixmap(QIcon(f":/icons/{file_info['icon']}.png").pixmap(32, 32))
            info_layout.addWidget(icon_label)
            
            # Nombre del archivo
            name_label = QLabel(os.path.basename(file_path))
            name_label.setStyleSheet("font-weight: bold;")
            info_layout.addWidget(name_label)
            
            # Tipo de archivo
            type_label = QLabel(file_info['description'])
            type_label.setStyleSheet("color: gray; font-size: 10px;")
            info_layout.addWidget(type_label)
            
            layout.addWidget(info_container)
            
            # Barra de progreso
            progress_bar = QProgressBar()
            progress_bar.setMinimum(0)
            progress_bar.setMaximum(100)
            layout.addWidget(progress_bar)
            
            # Botón de cancelar
            cancel_button = QPushButton("Cancel")
            cancel_button.clicked.connect(lambda: self.cancel_download(download))
            layout.addWidget(cancel_button)
            
            # Guardar referencia
            self.downloads[download] = {
                'widget': container,
                'progress_bar': progress_bar,
                'path': file_path,
                'file_info': file_info
            }
            
            self.downloads_layout.addWidget(container)
            
        except Exception as e:
            print(f"Error al crear widget de descarga: {str(e)}")

    def cancel_download(self, download):
        """Cancela una descarga en curso"""
        try:
            if download in self.downloads:
                download.cancel()
                self.cleanup_download(download)
                self.download_failed.emit("Download cancelled by user")
        except Exception as e:
            print(f"Error al cancelar descarga: {str(e)}")

    def cleanup_download(self, download):
        """Limpia los recursos de una descarga"""
        try:
            if download in self.downloads:
                widget = self.downloads[download]['widget']
                self.downloads_layout.removeWidget(widget)
                widget.deleteLater()
                del self.downloads[download]
        except Exception as e:
            print(f"Error al limpiar descarga: {str(e)}")

    def get_widget(self):
        """Retorna el widget principal del gestor de descargas"""
        return self.widget

    def _validate_extension(self, save_path, original_name):
        """Valida que la extensión del archivo sea segura"""
        original_ext = Path(original_name).suffix.lower()
        new_ext = save_path.suffix.lower()
        
        # Permite cambiar extensiones conocidas
        common_extensions = {'.pdf', '.jpg', '.png', '.txt', '.zip', '.exe', '.msi'}
        
        if not original_ext and not new_ext:
            return True
            
        if original_ext in common_extensions and new_ext in common_extensions:
            return True
            
        return new_ext == original_ext

    def show_download_confirmation(self, save_path):
        """Muestra confirmación de descarga con información detallada"""
        try:
            path = Path(save_path)
            file_info = self.get_file_type_info(save_path)
            
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Descarga iniciada")
            msg.setText(f"Descargando {file_info['description']}")
            msg.setInformativeText(f"Nombre: {path.name}\nUbicación: {save_path}")
            
            # Añadir advertencia según el tipo de archivo
            if file_info['mime_type'] in ['application/x-msdownload', 'application/x-executable']:
                msg.setDetailedText("ADVERTENCIA: Este es un archivo ejecutable. Asegúrese de que proviene de una fuente confiable.")
            elif file_info['mime_type'].startswith('application/') and not file_info['mime_type'] in ['application/pdf', 'application/zip']:
                msg.setDetailedText("ADVERTENCIA: Este archivo puede contener código ejecutable. Verifique su origen antes de abrirlo.")
            
            msg.exec()
        except Exception as e:
            print(f"Error al mostrar confirmación: {str(e)}")
            QMessageBox.information(self.parent, "Descarga iniciada",
                                  f"El archivo se está descargando a: {save_path}")