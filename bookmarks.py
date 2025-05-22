from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                              QLabel, QLineEdit, QListWidget, QListWidgetItem,
                              QDialog, QTextEdit, QComboBox, QMenu, QInputDialog,
                              QMessageBox, QFrame, QScrollArea, QCheckBox)
from PySide6.QtCore import Qt, Signal, QObject, QSettings, QUrl, QSize
from PySide6.QtGui import QIcon, QPixmap, QColor
import json
import os
import urllib.request
from urllib.parse import urlparse
import re

class BookmarkManager(QObject):
    bookmark_added = Signal(str, str)
    bookmark_removed = Signal(str)
    bookmark_updated = Signal(str, dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.bookmarks = {}
        self.tags = set()
        self.favicon_cache = {}
        self.init_ui()
        self.load_bookmarks()

    def init_ui(self):
        self.widget = QWidget()
        layout = QVBoxLayout(self.widget)
        
        # Barra de búsqueda
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar marcadores...")
        self.search_input.textChanged.connect(self.filter_bookmarks)
        search_layout.addWidget(self.search_input)
        
        # Filtro de tags
        self.tag_filter = QComboBox()
        self.tag_filter.addItem("Todos los tags", "")
        self.tag_filter.currentIndexChanged.connect(self.filter_bookmarks)
        search_layout.addWidget(self.tag_filter)
        
        layout.addLayout(search_layout)
        
        # Lista de marcadores
        self.bookmarks_list = QListWidget()
        self.bookmarks_list.setStyleSheet("""
            QListWidget {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #e0e0e0;
            }
        """)
        layout.addWidget(self.bookmarks_list)
        
        # Botones de acción
        buttons_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Añadir")
        self.add_button.clicked.connect(self.add_bookmark)
        buttons_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Editar")
        self.edit_button.clicked.connect(self.edit_bookmark)
        buttons_layout.addWidget(self.edit_button)
        
        self.remove_button = QPushButton("Eliminar")
        self.remove_button.clicked.connect(self.remove_bookmark)
        buttons_layout.addWidget(self.remove_button)
        
        layout.addLayout(buttons_layout)
        
        self.widget.setLayout(layout)

    def load_bookmarks(self):
        """Carga los marcadores guardados"""
        try:
            settings = QSettings("TronBrowser", "Bookmarks")
            bookmarks_data = settings.value("bookmarks", "{}")
            self.bookmarks = json.loads(bookmarks_data)
            
            # Cargar tags
            self.tags = set()
            for bookmark in self.bookmarks.values():
                if 'tags' in bookmark:
                    self.tags.update(bookmark['tags'])
            
            # Actualizar filtro de tags
            self.update_tag_filter()
            
            # Actualizar lista
            self.update_bookmarks_list()
            
        except Exception as e:
            print(f"Error al cargar marcadores: {str(e)}")

    def save_bookmarks(self):
        """Guarda los marcadores"""
        try:
            settings = QSettings("TronBrowser", "Bookmarks")
            settings.setValue("bookmarks", json.dumps(self.bookmarks))
            settings.sync()
        except Exception as e:
            print(f"Error al guardar marcadores: {str(e)}")

    def update_tag_filter(self):
        """Actualiza el filtro de tags"""
        current_tag = self.tag_filter.currentData()
        self.tag_filter.clear()
        self.tag_filter.addItem("Todos los tags", "")
        for tag in sorted(self.tags):
            self.tag_filter.addItem(tag, tag)
        if current_tag:
            index = self.tag_filter.findData(current_tag)
            if index >= 0:
                self.tag_filter.setCurrentIndex(index)

    def get_favicon(self, url):
        """Obtiene el favicon de una URL"""
        try:
            if url in self.favicon_cache:
                return self.favicon_cache[url]
            
            parsed_url = urlparse(url)
            favicon_url = f"{parsed_url.scheme}://{parsed_url.netloc}/favicon.ico"
            
            # Descargar favicon
            with urllib.request.urlopen(favicon_url) as response:
                favicon_data = response.read()
                pixmap = QPixmap()
                pixmap.loadFromData(favicon_data)
                
                if not pixmap.isNull():
                    self.favicon_cache[url] = pixmap
                    return pixmap
                
        except Exception as e:
            print(f"Error al obtener favicon: {str(e)}")
        
        # Favicon por defecto
        return QPixmap(":/icons/bookmark.png")

    def create_bookmark_item(self, url, data):
        """Crea un item de marcador con favicon y tags"""
        item = QListWidgetItem()
        
        # Crear widget personalizado
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Primera fila: favicon y título
        title_layout = QHBoxLayout()
        
        # Favicon
        favicon_label = QLabel()
        favicon = self.get_favicon(url)
        favicon_label.setPixmap(favicon.scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        title_layout.addWidget(favicon_label)
        
        # Título
        title_label = QLabel(data.get('title', url))
        title_label.setStyleSheet("font-weight: bold;")
        title_layout.addWidget(title_label)
        
        layout.addLayout(title_layout)
        
        # Segunda fila: URL
        url_label = QLabel(url)
        url_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(url_label)
        
        # Tercera fila: tags
        if 'tags' in data and data['tags']:
            tags_layout = QHBoxLayout()
            for tag in data['tags']:
                tag_label = QLabel(tag)
                tag_label.setStyleSheet("""
                    background-color: #e0e0e0;
                    padding: 2px 6px;
                    border-radius: 10px;
                    font-size: 10px;
                """)
                tags_layout.addWidget(tag_label)
            layout.addLayout(tags_layout)
        
        # Cuarta fila: notas
        if 'notes' in data and data['notes']:
            notes_label = QLabel(data['notes'])
            notes_label.setStyleSheet("color: #666; font-size: 10px;")
            notes_label.setWordWrap(True)
            layout.addWidget(notes_label)
        
        widget.setLayout(layout)
        item.setSizeHint(widget.sizeHint())
        
        return item, widget

    def update_bookmarks_list(self):
        """Actualiza la lista de marcadores"""
        self.bookmarks_list.clear()
        
        # Filtrar marcadores
        search_text = self.search_input.text().lower()
        selected_tag = self.tag_filter.currentData()
        
        for url, data in self.bookmarks.items():
            # Aplicar filtros
            if search_text and search_text not in data.get('title', '').lower() and search_text not in url.lower():
                continue
                
            if selected_tag and selected_tag not in data.get('tags', []):
                continue
            
            # Crear item
            item, widget = self.create_bookmark_item(url, data)
            self.bookmarks_list.addItem(item)
            self.bookmarks_list.setItemWidget(item, widget)

    def filter_bookmarks(self):
        """Filtra los marcadores según el texto de búsqueda y tags"""
        self.update_bookmarks_list()

    def add_bookmark(self):
        """Añade un nuevo marcador"""
        try:
            # Obtener URL y título del navegador actual
            current_url = self.parent.current_url()
            current_title = self.parent.current_title()
            
            if not current_url:
                QMessageBox.warning(self.parent, "Error", "No hay una página activa para marcar")
                return
            
            # Diálogo para añadir marcador
            dialog = QDialog(self.parent)
            dialog.setWindowTitle("Añadir marcador")
            layout = QVBoxLayout(dialog)
            
            # Campos
            title_input = QLineEdit(current_title)
            layout.addWidget(QLabel("Título:"))
            layout.addWidget(title_input)
            
            url_input = QLineEdit(current_url)
            layout.addWidget(QLabel("URL:"))
            layout.addWidget(url_input)
            
            tags_input = QLineEdit()
            layout.addWidget(QLabel("Tags (separados por comas):"))
            layout.addWidget(tags_input)
            
            notes_input = QTextEdit()
            layout.addWidget(QLabel("Notas:"))
            layout.addWidget(notes_input)
            
            # Checkbox para mostrar en barra
            show_in_bar_checkbox = QCheckBox("Mostrar en barra de favoritos")
            layout.addWidget(show_in_bar_checkbox)
            
            # Botones
            buttons_layout = QHBoxLayout()
            save_button = QPushButton("Guardar")
            save_button.clicked.connect(dialog.accept)
            cancel_button = QPushButton("Cancelar")
            cancel_button.clicked.connect(dialog.reject)
            buttons_layout.addWidget(save_button)
            buttons_layout.addWidget(cancel_button)
            layout.addLayout(buttons_layout)
            
            if dialog.exec():
                # Procesar tags
                tags = [tag.strip() for tag in tags_input.text().split(',') if tag.strip()]
                self.tags.update(tags)
                
                # Guardar marcador
                self.bookmarks[current_url] = {
                    'title': title_input.text(),
                    'tags': tags,
                    'notes': notes_input.toPlainText(),
                    'show_in_bar': show_in_bar_checkbox.isChecked(),
                    'favicon': self.get_favicon(current_url)
                }
                
                self.save_bookmarks()
                self.update_tag_filter()
                self.update_bookmarks_list()
                self.bookmark_added.emit(current_url, title_input.text())
                
                # Actualizar barra de favoritos si existe
                if hasattr(self.parent, 'update_favorites_bar'):
                    self.parent.update_favorites_bar()
                
        except Exception as e:
            print(f"Error al añadir marcador: {str(e)}")

    def edit_bookmark(self):
        """Edita un marcador existente"""
        try:
            current_item = self.bookmarks_list.currentItem()
            if not current_item:
                return
            
            # Obtener datos del marcador
            url = None
            for bookmark_url, data in self.bookmarks.items():
                if data.get('title') == current_item.text():
                    url = bookmark_url
                    break
            
            if not url:
                return
            
            data = self.bookmarks[url]
            
            # Diálogo para editar marcador
            dialog = QDialog(self.parent)
            dialog.setWindowTitle("Editar marcador")
            layout = QVBoxLayout(dialog)
            
            # Campos
            title_input = QLineEdit(data.get('title', ''))
            layout.addWidget(QLabel("Título:"))
            layout.addWidget(title_input)
            
            url_input = QLineEdit(url)
            layout.addWidget(QLabel("URL:"))
            layout.addWidget(url_input)
            
            tags_input = QLineEdit(', '.join(data.get('tags', [])))
            layout.addWidget(QLabel("Tags (separados por comas):"))
            layout.addWidget(tags_input)
            
            notes_input = QTextEdit()
            notes_input.setPlainText(data.get('notes', ''))
            layout.addWidget(QLabel("Notas:"))
            layout.addWidget(notes_input)
            
            # Checkbox para mostrar en barra
            show_in_bar_checkbox = QCheckBox("Mostrar en barra de favoritos")
            show_in_bar_checkbox.setChecked(data.get('show_in_bar', False))
            layout.addWidget(show_in_bar_checkbox)
            
            # Botones
            buttons_layout = QHBoxLayout()
            save_button = QPushButton("Guardar")
            save_button.clicked.connect(dialog.accept)
            cancel_button = QPushButton("Cancelar")
            cancel_button.clicked.connect(dialog.reject)
            buttons_layout.addWidget(save_button)
            buttons_layout.addWidget(cancel_button)
            layout.addLayout(buttons_layout)
            
            if dialog.exec():
                # Procesar tags
                tags = [tag.strip() for tag in tags_input.text().split(',') if tag.strip()]
                self.tags.update(tags)
                
                # Actualizar marcador
                new_url = url_input.text()
                if new_url != url:
                    del self.bookmarks[url]
                    url = new_url
                
                self.bookmarks[url] = {
                    'title': title_input.text(),
                    'tags': tags,
                    'notes': notes_input.toPlainText(),
                    'show_in_bar': show_in_bar_checkbox.isChecked(),
                    'favicon': self.get_favicon(url)
                }
                
                self.save_bookmarks()
                self.update_tag_filter()
                self.update_bookmarks_list()
                self.bookmark_updated.emit(url, self.bookmarks[url])
                
                # Actualizar barra de favoritos si existe
                if hasattr(self.parent, 'update_favorites_bar'):
                    self.parent.update_favorites_bar()
                
        except Exception as e:
            print(f"Error al editar marcador: {str(e)}")

    def remove_bookmark(self):
        """Elimina un marcador"""
        try:
            current_item = self.bookmarks_list.currentItem()
            if not current_item:
                return
            
            # Obtener URL del marcador
            url = None
            for bookmark_url, data in self.bookmarks.items():
                if data.get('title') == current_item.text():
                    url = bookmark_url
                    break
            
            if not url:
                return
            
            # Confirmar eliminación
            reply = QMessageBox.question(
                self.parent,
                "Confirmar eliminación",
                f"¿Estás seguro de que quieres eliminar el marcador '{self.bookmarks[url].get('title')}'?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                del self.bookmarks[url]
                self.save_bookmarks()
                self.update_tag_filter()
                self.update_bookmarks_list()
                self.bookmark_removed.emit(url)
                
        except Exception as e:
            print(f"Error al eliminar marcador: {str(e)}")

    def get_widget(self):
        """Retorna el widget principal del gestor de marcadores"""
        return self.widget 

    def get_favorites_for_bar(self):
        """Devuelve una lista de favoritos marcados para mostrar en la barra de favoritos"""
        favs = []
        for url, data in self.bookmarks.items():
            if data.get('show_in_bar'):
                favs.append({
                    'url': url,
                    'title': data.get('title', url),
                    'icon': data.get('favicon', ':/icons/bookmark.png')
                })
        return favs 