#!/usr/bin/env python3
"""
Barra de Favoritos - Implementación completa similar a Firefox/Chrome
"""

from PySide6.QtWidgets import (QToolBar, QMenu, QDialog, QVBoxLayout, 
                               QHBoxLayout, QLabel, QLineEdit, QComboBox, 
                               QPushButton, QMessageBox, QCheckBox, QWidget)
from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtGui import QIcon, QPixmap, QAction
import sqlite3
import os
from urllib.parse import urlparse
import urllib.request

class FavoriteDialog(QDialog):
    """Diálogo para añadir/editar favoritos en la barra"""
    
    def __init__(self, parent=None, title="", url="", category="", show_in_bar=True):
        super().__init__(parent)
        self.setWindowTitle("Añadir a Favoritos")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Título
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("Título:"))
        self.title_edit = QLineEdit(title)
        title_layout.addWidget(self.title_edit)
        layout.addLayout(title_layout)
        
        # URL
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("URL:"))
        self.url_edit = QLineEdit(url)
        url_layout.addWidget(self.url_edit)
        layout.addLayout(url_layout)
        
        # Categoría
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("Categoría:"))
        self.category_combo = QComboBox()
        self.load_categories()
        if category:
            index = self.category_combo.findText(category)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
        category_layout.addWidget(self.category_combo)
        layout.addLayout(category_layout)
        
        # Mostrar en barra de favoritos
        self.show_in_bar_check = QCheckBox("Mostrar en barra de favoritos")
        self.show_in_bar_check.setChecked(show_in_bar)
        layout.addWidget(self.show_in_bar_check)
        
        # Botones
        button_layout = QHBoxLayout()
        save_button = QPushButton("Guardar")
        save_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancelar")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
    
    def load_categories(self):
        """Carga las categorías disponibles"""
        try:
            conn = sqlite3.connect('bookmarks.db')
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM categories ORDER BY name")
            categories = cursor.fetchall()
            
            self.category_combo.addItem("Sin categoría")
            for category in categories:
                self.category_combo.addItem(category[0])
            
            conn.close()
        except Exception as e:
            print(f"Error cargando categorías: {e}")
    
    def get_values(self):
        """Obtiene los valores del diálogo"""
        return {
            'title': self.title_edit.text(),
            'url': self.url_edit.text(),
            'category': self.category_combo.currentText(),
            'show_in_bar': self.show_in_bar_check.isChecked()
        }

class FavoritesBar(QToolBar):
    """Barra de favoritos con funcionalidad completa"""
    
    favorite_clicked = Signal(str)  # Señal cuando se hace clic en un favorito
    
    def __init__(self, parent=None):
        super().__init__("Favoritos", parent)
        self.setWindowTitle("Barra de Favoritos")
        self.setVisible(False)  # Inicialmente oculta
        
        # Configurar la barra
        self.setMovable(True)
        self.setFloatable(True)
        self.setIconSize(QPixmap(16, 16).size())
        
        # Cache de favicons
        self.favicon_cache = {}
        
        # Cargar favoritos
        self.load_favorites()
    
    def load_favorites(self):
        """Carga los favoritos desde la base de datos"""
        try:
            conn = sqlite3.connect('bookmarks.db')
            cursor = conn.cursor()
            
            # Obtener favoritos marcados para la barra
            cursor.execute("""
                SELECT title, url, category, notes, tags 
                FROM bookmarks 
                WHERE notes LIKE '%[barra]%' 
                   OR tags LIKE '%[barra]%' 
                   OR category LIKE '%Barra%' 
                   OR tags LIKE '%barra%' 
                   OR notes LIKE '%barra%'
                   OR category = 'Barra de Favoritos'
                ORDER BY title
            """)
            
            favorites = cursor.fetchall()
            conn.close()
            
            # Limpiar barra actual
            self.clear()
            
            # Añadir favoritos a la barra
            for favorite in favorites:
                title, url, category, notes, tags = favorite
                self.add_favorite_to_bar(title, url)
            
            # Añadir botón para añadir favorito actual
            self.add_add_favorite_action()
            
        except Exception as e:
            print(f"Error cargando favoritos: {e}")
    
    def add_favorite_to_bar(self, title, url):
        """Añade un favorito a la barra"""
        try:
            # Obtener favicon
            icon = self.get_favicon(url)
            
            # Crear acción
            action = QAction(icon, title, self)
            action.setToolTip(f"{title}\n{url}")
            action.setData(url)
            action.triggered.connect(lambda: self.favorite_clicked.emit(url))
            
            # Añadir menú contextual
            action.setMenu(self.create_favorite_menu(title, url))
            
            # Añadir a la barra
            self.addAction(action)
            
        except Exception as e:
            print(f"Error añadiendo favorito a la barra: {e}")
    
    def create_favorite_menu(self, title, url):
        """Crea el menú contextual para un favorito"""
        menu = QMenu()
        
        # Abrir
        open_action = menu.addAction("Abrir")
        open_action.triggered.connect(lambda: self.favorite_clicked.emit(url))
        
        # Abrir en nueva pestaña
        open_new_tab_action = menu.addAction("Abrir en nueva pestaña")
        open_new_tab_action.triggered.connect(lambda: self.open_in_new_tab(url))
        
        menu.addSeparator()
        
        # Editar
        edit_action = menu.addAction("Editar")
        edit_action.triggered.connect(lambda: self.edit_favorite(title, url))
        
        # Quitar de barra
        remove_action = menu.addAction("Quitar de barra de favoritos")
        remove_action.triggered.connect(lambda: self.remove_from_bar(title, url))
        
        menu.addSeparator()
        
        # Eliminar
        delete_action = menu.addAction("Eliminar")
        delete_action.triggered.connect(lambda: self.delete_favorite(title, url))
        
        return menu
    
    def add_add_favorite_action(self):
        """Añade el botón para añadir favorito actual"""
        add_action = QAction("⭐", self)
        add_action.setToolTip("Añadir página actual a favoritos")
        add_action.triggered.connect(self.add_current_page)
        self.addAction(add_action)
    
    def add_current_page(self):
        """Añade la página actual a favoritos"""
        try:
            # Obtener la página actual del navegador
            main_window = self.window()
            if hasattr(main_window, 'tab_manager'):
                current_tab = main_window.tab_manager.tabs.currentWidget()
                if current_tab:
                    url = current_tab.url().toString()
                    title = current_tab.page().title()
                    
                    # Mostrar diálogo
                    dialog = FavoriteDialog(self, title, url)
                    if dialog.exec():
                        values = dialog.get_values()
                        self.save_favorite(values)
                        
        except Exception as e:
            print(f"Error añadiendo página actual: {e}")
    
    def save_favorite(self, values):
        """Guarda un favorito en la base de datos"""
        try:
            conn = sqlite3.connect('bookmarks.db')
            cursor = conn.cursor()
            
            # Preparar notas y tags según si se muestra en barra
            notes = "[barra]" if values['show_in_bar'] else ""
            tags = "barra" if values['show_in_bar'] else ""
            
            # Insertar en la base de datos
            cursor.execute("""
                INSERT INTO bookmarks (title, url, category, notes, tags) 
                VALUES (?, ?, ?, ?, ?)
            """, (values['title'], values['url'], values['category'], notes, tags))
            
            conn.commit()
            conn.close()
            
            # Recargar la barra
            self.load_favorites()
            
            QMessageBox.information(self, "Éxito", "Favorito guardado correctamente")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error guardando favorito: {e}")
    
    def edit_favorite(self, title, url):
        """Edita un favorito existente"""
        try:
            conn = sqlite3.connect('bookmarks.db')
            cursor = conn.cursor()
            
            # Obtener datos actuales
            cursor.execute("""
                SELECT title, url, category, notes, tags 
                FROM bookmarks 
                WHERE url = ?
            """, (url,))
            
            result = cursor.fetchone()
            if result:
                current_title, current_url, current_category, current_notes, current_tags = result
                show_in_bar = "[barra]" in current_notes or "barra" in current_tags
                
                # Mostrar diálogo de edición
                dialog = FavoriteDialog(self, current_title, current_url, current_category, show_in_bar)
                if dialog.exec():
                    values = dialog.get_values()
                    self.update_favorite(url, values)
            
            conn.close()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error editando favorito: {e}")
    
    def update_favorite(self, old_url, values):
        """Actualiza un favorito existente"""
        try:
            conn = sqlite3.connect('bookmarks.db')
            cursor = conn.cursor()
            
            # Preparar notas y tags
            notes = "[barra]" if values['show_in_bar'] else ""
            tags = "barra" if values['show_in_bar'] else ""
            
            # Actualizar en la base de datos
            cursor.execute("""
                UPDATE bookmarks 
                SET title = ?, url = ?, category = ?, notes = ?, tags = ?
                WHERE url = ?
            """, (values['title'], values['url'], values['category'], notes, tags, old_url))
            
            conn.commit()
            conn.close()
            
            # Recargar la barra
            self.load_favorites()
            
            QMessageBox.information(self, "Éxito", "Favorito actualizado correctamente")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error actualizando favorito: {e}")
    
    def remove_from_bar(self, title, url):
        """Quita un favorito de la barra (pero no lo elimina)"""
        try:
            conn = sqlite3.connect('bookmarks.db')
            cursor = conn.cursor()
            
            # Actualizar para quitar de la barra
            cursor.execute("""
                UPDATE bookmarks 
                SET notes = REPLACE(notes, '[barra]', ''), 
                    tags = REPLACE(tags, 'barra', '')
                WHERE url = ?
            """, (url,))
            
            conn.commit()
            conn.close()
            
            # Recargar la barra
            self.load_favorites()
            
            QMessageBox.information(self, "Éxito", "Favorito quitado de la barra")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error quitando favorito de la barra: {e}")
    
    def delete_favorite(self, title, url):
        """Elimina completamente un favorito"""
        reply = QMessageBox.question(
            self, "Confirmar eliminación", 
            f"¿Estás seguro de que quieres eliminar '{title}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                conn = sqlite3.connect('bookmarks.db')
                cursor = conn.cursor()
                
                cursor.execute("DELETE FROM bookmarks WHERE url = ?", (url,))
                
                conn.commit()
                conn.close()
                
                # Recargar la barra
                self.load_favorites()
                
                QMessageBox.information(self, "Éxito", "Favorito eliminado correctamente")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error eliminando favorito: {e}")
    
    def open_in_new_tab(self, url):
        """Abre un favorito en una nueva pestaña"""
        try:
            main_window = self.window()
            if hasattr(main_window, 'tab_manager'):
                main_window.tab_manager.add_new_tab(url)
        except Exception as e:
            print(f"Error abriendo en nueva pestaña: {e}")
    
    def get_favicon(self, url):
        """Obtiene el favicon de una URL"""
        try:
            if url in self.favicon_cache:
                return self.favicon_cache[url]
            
            parsed_url = urlparse(url)
            favicon_url = f"{parsed_url.scheme}://{parsed_url.netloc}/favicon.ico"
            
            # No descargar favicons durante la inicialización para evitar bloqueos
            # TODO: Implementar descarga asíncrona de favicons en el futuro
            
            # Favicon por defecto
            try:
                default_icon = QIcon("icons/bookmark.png")
                if default_icon.isNull():
                    # Crear un ícono simple si no hay archivo
                    pixmap = QPixmap(16, 16)
                    pixmap.fill()
                    default_icon = QIcon(pixmap)
            except:
                # Último recurso: ícono vacío
                pixmap = QPixmap(16, 16)
                pixmap.fill()
                default_icon = QIcon(pixmap)
                
            self.favicon_cache[url] = default_icon
            return default_icon
            
        except Exception as e:
            print(f"Error obteniendo favicon: {e}")
            return QIcon("icons/bookmark.png")
    
    def refresh_favorites(self):
        """Actualiza la barra de favoritos"""
        self.load_favorites() 