#!/usr/bin/env python3
"""
Panel de Scraping Funcional - Análisis real de HTML y selección de elementos
"""

import sys
import json
import time
from datetime import datetime
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, 
                               QTextEdit, QPushButton, QLabel, QSpinBox, 
                               QLineEdit, QComboBox, QListWidget, QListWidgetItem,
                               QCheckBox, QGroupBox, QScrollArea, QFrame, QMessageBox)
from PySide6.QtCore import Qt, QThread, Signal as pyqtSignal
from PySide6.QtGui import QFont, QColor

class ScrapingPanel(QWidget):
    def __init__(self, scraping_integration, parent=None):
        super().__init__(parent)
        self.scraping_integration = scraping_integration
        self.setup_ui()
    
    def setup_ui(self):
        """Setup complete UI with REAL scraping functionality"""
        layout = QVBoxLayout()
        
        # Create tab widget for all features
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)  # Pestañas planas estilo moderno
        
        # Create all tabs with comprehensive features
        self.tab_widget.addTab(self.create_analysis_tab(), "📊 Análisis Real")
        self.tab_widget.addTab(self.create_selection_tab(), "🎯 Selección de Elementos")
        self.tab_widget.addTab(self.create_extraction_tab(), "📥 Extracción de Datos")
        self.tab_widget.addTab(self.create_export_tab(), "📤 Exportar Datos")
        self.tab_widget.addTab(self.create_discovery_tab(), "🔍 Descubrimiento de URLs")
        self.tab_widget.addTab(self.create_status_tab(), "ℹ️ Estado del Sistema")
        
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)
    
    def create_analysis_tab(self):
        """Análisis real de HTML con funcionalidad completa"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Controls
        controls_layout = QHBoxLayout()
        self.analyze_btn = QPushButton("🔍 Analizar Página Actual")
        self.analyze_btn.clicked.connect(self.run_analysis)
        controls_layout.addWidget(self.analyze_btn)
        
        self.refresh_btn = QPushButton("🔄 Actualizar HTML")
        self.refresh_btn.clicked.connect(self.refresh_html)
        controls_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(controls_layout)
        
        # Analysis results
        self.analysis_text = QTextEdit()
        self.analysis_text.setPlaceholderText("Resultados del análisis aparecerán aquí...")
        layout.addWidget(self.analysis_text)
        
        widget.setLayout(layout)
        return widget
    
    def create_selection_tab(self):
        """Selección interactiva de elementos"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Controls
        controls_layout = QHBoxLayout()
        self.load_elements_btn = QPushButton("📋 Cargar Elementos")
        self.load_elements_btn.clicked.connect(self.load_selectable_elements)
        controls_layout.addWidget(self.load_elements_btn)
        
        self.clear_selection_btn = QPushButton("🗑️ Limpiar Selección")
        self.clear_selection_btn.clicked.connect(self.clear_selection)
        controls_layout.addWidget(self.clear_selection_btn)
        
        self.select_all_btn = QPushButton("✅ Seleccionar Todo")
        self.select_all_btn.clicked.connect(self.select_all_elements)
        controls_layout.addWidget(self.select_all_btn)
        
        # Interactive selection controls
        self.enable_selection_btn = QPushButton("🎯 Activar Selección Interactiva")
        self.enable_selection_btn.clicked.connect(self.toggle_interactive_selection)
        controls_layout.addWidget(self.enable_selection_btn)
        
        # Selector input for manual selection
        self.manual_selector_input = QLineEdit()
        self.manual_selector_input.setPlaceholderText("CSS selector (ej: h1, .class, #id)")
        self.manual_selector_input.setFixedHeight(32)  # Altura consistente
        if hasattr(self.manual_selector_input, "setClearButtonEnabled"):
            self.manual_selector_input.setClearButtonEnabled(True)
        controls_layout.addWidget(QLabel("Selector:"))
        controls_layout.addWidget(self.manual_selector_input)
        
        self.add_by_selector_btn = QPushButton("➕ Añadir por Selector")
        self.add_by_selector_btn.clicked.connect(self.add_elements_by_selector)
        controls_layout.addWidget(self.add_by_selector_btn)
        
        # Sync button for JavaScript selected elements
        self.sync_js_elements_btn = QPushButton("🔄 Sincronizar JS")
        self.sync_js_elements_btn.clicked.connect(self.sync_javascript_elements)
        controls_layout.addWidget(self.sync_js_elements_btn)
        
        layout.addLayout(controls_layout)
        
        # Elements list
        elements_group = QGroupBox("Elementos Disponibles")
        elements_layout = QVBoxLayout()
        
        # Filter controls
        filter_layout = QHBoxLayout()
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Todos", "Encabezados", "Enlaces", "Botones", "Párrafos", "Imágenes", "Texto destacado"])
        self.filter_combo.currentTextChanged.connect(self.filter_elements)
        filter_layout.addWidget(QLabel("Filtrar por tipo:"))
        filter_layout.addWidget(self.filter_combo)
        
        self.refresh_elements_btn = QPushButton("🔄 Actualizar")
        self.refresh_elements_btn.clicked.connect(self.load_selectable_elements)
        filter_layout.addWidget(self.refresh_elements_btn)
        
        elements_layout.addLayout(filter_layout)
        
        self.elements_list = QListWidget()
        self.elements_list.setSelectionMode(QListWidget.MultiSelection)
        self.elements_list.itemDoubleClicked.connect(self.add_single_element)
        elements_layout.addWidget(self.elements_list)
        
        elements_group.setLayout(elements_layout)
        layout.addWidget(elements_group)
        
        # Selected elements
        selected_group = QGroupBox("Elementos Seleccionados")
        selected_layout = QVBoxLayout()
        
        self.selected_list = QListWidget()
        selected_layout.addWidget(self.selected_list)
        
        selected_group.setLayout(selected_layout)
        layout.addWidget(selected_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_extraction_tab(self):
        """Extracción de datos con selectores personalizados"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Controls
        controls_layout = QHBoxLayout()
        self.extract_btn = QPushButton("📥 Extraer Datos")
        self.extract_btn.clicked.connect(self.run_extraction)
        controls_layout.addWidget(self.extract_btn)
        
        # Selectors input
        self.selectors_input = QLineEdit()
        self.selectors_input.setPlaceholderText("h1, p, a, table, img (separados por comas)")
        self.selectors_input.setFixedHeight(32)  # Altura consistente
        if hasattr(self.selectors_input, "setClearButtonEnabled"):
            self.selectors_input.setClearButtonEnabled(True)
        controls_layout.addWidget(QLabel("Selectores:"))
        controls_layout.addWidget(self.selectors_input)
        
        layout.addLayout(controls_layout)
        
        # Results
        self.extraction_text = QTextEdit()
        self.extraction_text.setPlaceholderText("Datos extraídos aparecerán aquí...")
        layout.addWidget(self.extraction_text)
        
        widget.setLayout(layout)
        return widget
    
    def create_export_tab(self):
        """Exportación de datos seleccionados"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Controls
        controls_layout = QHBoxLayout()
        self.export_btn = QPushButton("📤 Exportar Datos")
        self.export_btn.clicked.connect(self.run_export)
        controls_layout.addWidget(self.export_btn)
        
        # Format selection
        self.export_format = QComboBox()
        self.export_format.addItems(["CSV", "Excel", "JSON", "YAML"])
        controls_layout.addWidget(QLabel("Formato:"))
        controls_layout.addWidget(self.export_format)
        
        # Filename input
        self.export_filename = QLineEdit()
        self.export_filename.setPlaceholderText("nombre_archivo")
        self.export_filename.setFixedHeight(32)  # Altura consistente
        if hasattr(self.export_filename, "setClearButtonEnabled"):
            self.export_filename.setClearButtonEnabled(True)
        controls_layout.addWidget(QLabel("Archivo:"))
        controls_layout.addWidget(self.export_filename)
        
        layout.addLayout(controls_layout)
        
        # Export info
        self.export_text = QTextEdit()
        self.export_text.setPlaceholderText("Información de exportación aparecerá aquí...")
        layout.addWidget(self.export_text)
        
        widget.setLayout(layout)
        return widget
    
    def create_discovery_tab(self):
        """Descubrimiento de URLs"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Controls
        controls_layout = QHBoxLayout()
        self.discover_btn = QPushButton("🔍 Descubrir URLs")
        self.discover_btn.clicked.connect(self.run_discovery)
        controls_layout.addWidget(self.discover_btn)
        
        # Parameters
        self.max_urls_spin = QSpinBox()
        self.max_urls_spin.setRange(10, 1000)
        self.max_urls_spin.setValue(100)
        controls_layout.addWidget(QLabel("Max URLs:"))
        controls_layout.addWidget(self.max_urls_spin)
        
        layout.addLayout(controls_layout)
        
        # Export controls
        export_layout = QHBoxLayout()
        export_layout.addWidget(QLabel("📤 Exportar URLs:"))
        
        self.export_csv_btn = QPushButton("📊 CSV")
        self.export_csv_btn.clicked.connect(lambda: self.export_urls('csv'))
        self.export_csv_btn.setEnabled(False)
        export_layout.addWidget(self.export_csv_btn)
        
        self.export_json_btn = QPushButton("📋 JSON")
        self.export_json_btn.clicked.connect(lambda: self.export_urls('json'))
        self.export_json_btn.setEnabled(False)
        export_layout.addWidget(self.export_json_btn)
        
        self.export_txt_btn = QPushButton("📄 TXT")
        self.export_txt_btn.clicked.connect(lambda: self.export_urls('txt'))
        self.export_txt_btn.setEnabled(False)
        export_layout.addWidget(self.export_txt_btn)
        
        self.export_excel_btn = QPushButton("📈 Excel")
        self.export_excel_btn.clicked.connect(lambda: self.export_urls('excel'))
        self.export_excel_btn.setEnabled(False)
        export_layout.addWidget(self.export_excel_btn)
        
        layout.addLayout(export_layout)
        
        # Results
        self.discovery_text = QTextEdit()
        self.discovery_text.setPlaceholderText("URLs descubiertas aparecerán aquí...")
        layout.addWidget(self.discovery_text)
        
        # Store discovered URLs
        self.discovered_urls = []
        self.fuzzing_results = []
        
        widget.setLayout(layout)
        return widget
    
    def create_status_tab(self):
        """Estado del sistema"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Controls
        controls_layout = QHBoxLayout()
        self.status_btn = QPushButton("🔄 Actualizar Estado")
        self.status_btn.clicked.connect(self.refresh_status)
        controls_layout.addWidget(self.status_btn)
        
        layout.addLayout(controls_layout)
        
        # Status display
        self.status_text = QTextEdit()
        self.status_text.setPlaceholderText("Estado del sistema aparecerá aquí...")
        layout.addWidget(self.status_text)
        
        widget.setLayout(layout)
        return widget
    
    # Action methods
    def run_analysis(self):
        """Ejecutar análisis real de la página"""
        try:
            if not self.scraping_integration.current_html:
                self.analysis_text.setText("❌ Error: No hay contenido HTML para analizar")
                return
            
            result = self.scraping_integration.analyze_page()
            
            if "error" not in result:
                display_text = f"✅ ANÁLISIS COMPLETADO\n"
                display_text += f"📅 Timestamp: {result.get('timestamp', 'N/A')}\n"
                display_text += f"🔗 URL: {result.get('url', 'N/A')}\n\n"
                
                # Display detailed analysis
                if 'analysis' in result:
                    analysis = result['analysis']
                    display_text += "📊 ELEMENTOS DETECTADOS:\n"
                    display_text += f"   • Enlaces: {len(analysis.get('links', []))}\n"
                    display_text += f"   • Imágenes: {len(analysis.get('images', []))}\n"
                    display_text += f"   • Formularios: {len(analysis.get('forms', []))}\n"
                    display_text += f"   • Tablas: {len(analysis.get('tables', []))}\n"
                    display_text += f"   • Listas: {len(analysis.get('lists', []))}\n"
                    display_text += f"   • Encabezados: {len(analysis.get('headings', []))}\n"
                    display_text += f"   • Párrafos: {len(analysis.get('paragraphs', []))}\n"
                    display_text += f"   • Botones: {len(analysis.get('buttons', []))}\n"
                    display_text += f"   • Inputs: {len(analysis.get('inputs', []))}\n\n"
                    
                    # Show some examples
                    if analysis.get('links'):
                        display_text += "🔗 EJEMPLOS DE ENLACES:\n"
                        for i, link in enumerate(analysis['links'][:5], 1):
                            display_text += f"   {i}. {link.get('text', 'Sin texto')} -> {link.get('href', 'Sin URL')}\n"
                    
                    if analysis.get('headings'):
                        display_text += "\n📝 EJEMPLOS DE ENCABEZADOS:\n"
                        for i, heading in enumerate(analysis['headings'][:5], 1):
                            display_text += f"   {i}. {heading.get('level', 'h')}: {heading.get('text', 'Sin texto')}\n"
                
                self.analysis_text.setText(display_text)
            else:
                self.analysis_text.setText(f"❌ Error: {result.get('error', 'Desconocido')}")
        except Exception as e:
            self.analysis_text.setText(f"❌ Error: {str(e)}")
    
    def refresh_html(self):
        """Actualizar HTML desde el navegador"""
        try:
            # This would be called from the browser to update HTML
            self.analysis_text.setText("🔄 HTML actualizado desde el navegador")
        except Exception as e:
            self.analysis_text.setText(f"❌ Error actualizando HTML: {str(e)}")
    
    def load_selectable_elements(self):
        """Cargar elementos seleccionables de la página"""
        try:
            if not self.scraping_integration.current_html:
                QMessageBox.warning(self, "Error", "No hay contenido HTML para analizar")
                return
            
            elements = self.scraping_integration.get_selectable_elements()
            self.all_elements = elements  # Store all elements for filtering
            self.display_elements(elements)
            
            QMessageBox.information(self, "Éxito", f"Se cargaron {len(elements)} elementos")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error cargando elementos: {str(e)}")
    
    def display_elements(self, elements):
        """Display elements in the list with better formatting"""
        self.elements_list.clear()
        
        for element in elements:
            item = QListWidgetItem()
            
            # Create better display text
            element_type = element.get('type', 'Otro')
            importance = element.get('importance', 0)
            text_limpio = element.get('texto_limpio', element.get('text', 'Sin texto'))
            
            # Truncate text for display
            display_text = text_limpio[:60] + "..." if len(text_limpio) > 60 else text_limpio
            
            # Add importance indicator
            if importance > 80:
                display_text = f"⭐ [{element_type}] {display_text}"
            elif importance > 60:
                display_text = f"🔸 [{element_type}] {display_text}"
            else:
                display_text = f"📄 [{element_type}] {display_text}"
            
            item.setText(display_text)
            item.setData(Qt.UserRole, element)
            
            # Set comprehensive tooltip
            tooltip = f"Tipo: {element_type}\n"
            tooltip += f"Importancia: {importance}\n"
            tooltip += f"Selector: {element.get('selector', 'N/A')}\n"
            tooltip += f"Texto limpio: {text_limpio}\n"
            
            # Add structured data info
            if "structured_data" in element:
                structured = element["structured_data"]
                if structured.get("url"):
                    tooltip += f"URL: {structured['url']}\n"
                if structured.get("texto_enlace"):
                    tooltip += f"Texto enlace: {structured['texto_enlace']}\n"
                if structured.get("nivel_encabezado"):
                    tooltip += f"Nivel: {structured['nivel_encabezado']}\n"
            
            item.setToolTip(tooltip)
            
            self.elements_list.addItem(item)
    
    def filter_elements(self):
        """Filter elements by type"""
        if not hasattr(self, 'all_elements'):
            return
        
        filter_type = self.filter_combo.currentText()
        
        if filter_type == "Todos":
            filtered_elements = self.all_elements
        else:
            # Map display names to element types
            type_mapping = {
                "Encabezados": "Encabezado",
                "Enlaces": "Enlace", 
                "Botones": "Botón",
                "Párrafos": "Párrafo",
                "Imágenes": "Imagen",
                "Texto destacado": "Texto destacado"
            }
            
            target_type = type_mapping.get(filter_type, filter_type)
            filtered_elements = [e for e in self.all_elements if e.get('type') == target_type]
        
        self.display_elements(filtered_elements)
    
    def add_single_element(self, item):
        """Add a single element when double-clicked"""
        try:
            element_data = item.data(Qt.UserRole)
            self.scraping_integration.add_selected_element(element_data)
            self.update_selected_list()
            
            QMessageBox.information(self, "Elemento Añadido", 
                f"✅ Elemento añadido:\n{element_data.get('type', 'N/A')}: {element_data.get('text', 'N/A')}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error añadiendo elemento: {str(e)}")
    
    def clear_selection(self):
        """Limpiar selección de elementos"""
        try:
            self.scraping_integration.clear_selected_elements()
            self.selected_list.clear()
            QMessageBox.information(self, "Éxito", "Selección limpiada")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error limpiando selección: {str(e)}")
    
    def select_all_elements(self):
        """Seleccionar todos los elementos"""
        try:
            self.elements_list.selectAll()
            self.add_selected_elements()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error seleccionando elementos: {str(e)}")
    
    def add_selected_elements(self):
        """Agregar elementos seleccionados a la lista de seleccionados"""
        try:
            selected_items = self.elements_list.selectedItems()
            
            for item in selected_items:
                element_data = item.data(Qt.UserRole)
                self.scraping_integration.add_selected_element(element_data)
            
            self.update_selected_list()
            QMessageBox.information(self, "Éxito", f"Se agregaron {len(selected_items)} elementos")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error agregando elementos: {str(e)}")
    
    def update_selected_list(self):
        """Actualizar lista de elementos seleccionados"""
        try:
            self.selected_list.clear()
            selected_elements = self.scraping_integration.get_selected_elements()
            
            for element in selected_elements:
                item = QListWidgetItem()
                item.setText(f"{element['tag']}: {element['text']}")
                item.setData(Qt.UserRole, element)
                self.selected_list.addItem(item)
                
        except Exception as e:
            print(f"Error actualizando lista: {e}")
    
    def toggle_interactive_selection(self):
        """Activar/desactivar selección interactiva desde la página"""
        try:
            if not hasattr(self, 'interactive_selection_active'):
                self.interactive_selection_active = False
            
            self.interactive_selection_active = not self.interactive_selection_active
            
            # Activar/desactivar en el navegador
            if hasattr(self, 'browser_tab') and self.browser_tab:
                js_code = f"window.toggleInteractiveSelection({str(self.interactive_selection_active).lower()});"
                self.browser_tab.page().runJavaScript(js_code)
                print(f"🎯 Enviando comando JavaScript: toggleInteractiveSelection({self.interactive_selection_active})")
            else:
                print("❌ No hay pestaña del navegador disponible")
            
            if self.interactive_selection_active:
                self.enable_selection_btn.setText("🎯 Desactivar Selección Interactiva")
                self.enable_selection_btn.setStyleSheet("background-color: #ff6b6b;")
                QMessageBox.information(self, "Selección Interactiva", 
                    "✅ Selección interactiva ACTIVADA\n\n"
                    "Ahora puedes:\n"
                    "• Hacer clic en elementos de la página para añadirlos\n"
                    "• Usar el selector manual para añadir elementos específicos\n"
                    "• Los elementos seleccionados aparecerán en la lista de abajo\n\n"
                    "�� El cursor cambiará a una cruz cuando pases sobre elementos clickeables\n"
                    "🔍 Usa '🔄 Sincronizar JS' para traer elementos seleccionados")
            else:
                self.enable_selection_btn.setText("🎯 Activar Selección Interactiva")
                self.enable_selection_btn.setStyleSheet("")
                QMessageBox.information(self, "Selección Interactiva", 
                    "❌ Selección interactiva DESACTIVADA")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error activando selección interactiva: {str(e)}")
    
    def add_elements_by_selector(self):
        """Añadir elementos usando un selector CSS"""
        try:
            selector = self.manual_selector_input.text().strip()
            if not selector:
                QMessageBox.warning(self, "Error", "Por favor ingresa un selector CSS")
                return
            
            result = self.scraping_integration.add_element_by_selector(selector)
            
            if "error" not in result:
                QMessageBox.information(self, "Éxito", 
                    f"✅ Se añadieron {result.get('elements_added', 0)} elementos\n"
                    f"Selector: {result.get('selector', 'N/A')}")
                self.update_selected_list()
                self.manual_selector_input.clear()
            else:
                QMessageBox.critical(self, "Error", f"Error añadiendo elementos: {result.get('error', 'Desconocido')}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error añadiendo elementos: {str(e)}")
    
    def add_element_from_page_click(self, x: int, y: int):
        """Añadir elemento desde clic en la página (llamado desde el navegador)"""
        try:
            if not hasattr(self, 'interactive_selection_active') or not self.interactive_selection_active:
                return
            
            result = self.scraping_integration.add_element_by_click(x, y)
            
            if "error" not in result:
                self.update_selected_list()
                print(f"✅ Elemento añadido desde clic en ({x}, {y})")
            else:
                print(f"❌ Error añadiendo elemento desde clic: {result.get('error', 'Desconocido')}")
                
        except Exception as e:
            print(f"Error añadiendo elemento desde clic: {e}")
    
    def handle_page_click(self, x: int, y: int):
        """Manejar clic en la página web"""
        try:
            if hasattr(self, 'interactive_selection_active') and self.interactive_selection_active:
                self.add_element_from_page_click(x, y)
        except Exception as e:
            print(f"Error manejando clic en página: {e}")
    
    def sync_javascript_elements(self):
        """Sincronizar elementos seleccionados desde JavaScript"""
        try:
            if hasattr(self, 'browser_tab') and self.browser_tab:
                # Get selected elements from JavaScript
                js_code = "window.getSelectedElements();"
                self.browser_tab.page().runJavaScript(js_code, self.process_javascript_elements)
                
                # Also check if interactive selection is active
                check_active_js = "window.interactiveSelectionActive;"
                self.browser_tab.page().runJavaScript(check_active_js, self.check_selection_status)
            else:
                QMessageBox.warning(self, "Error", "No hay pestaña del navegador disponible")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error sincronizando elementos: {str(e)}")
    
    def check_selection_status(self, is_active):
        """Check if interactive selection is active"""
        if is_active:
            print("✅ Selección interactiva está activa en JavaScript")
        else:
            print("❌ Selección interactiva NO está activa en JavaScript")
    
    def process_javascript_elements(self, js_elements):
        """Procesar elementos seleccionados desde JavaScript"""
        try:
            if js_elements and len(js_elements) > 0:
                added_count = 0
                for js_element in js_elements:
                    # Convert JavaScript element to Python format
                    element_data = {
                        "tag": js_element.get('tag', 'unknown'),
                        "text": js_element.get('text', ''),
                        "full_text": js_element.get('text', ''),
                        "selector": js_element.get('selector', ''),
                        "attributes": {
                            "href": js_element.get('href', ''),
                            "alt": js_element.get('alt', ''),
                            "class": js_element.get('className', ''),
                            "id": js_element.get('id', '')
                        },
                        "html": f"<{js_element.get('tag', 'div')}>{js_element.get('text', '')}</{js_element.get('tag', 'div')}>",
                        "importance": 50,  # Default importance
                        "type": self._get_element_type_from_tag(js_element.get('tag', 'div'))
                    }
                    
                    self.scraping_integration.add_selected_element(element_data)
                    added_count += 1
                
                self.update_selected_list()
                QMessageBox.information(self, "Sincronización Exitosa", 
                    f"✅ Se sincronizaron {added_count} elementos desde JavaScript")
                
                # Clear JavaScript elements after sync
                if hasattr(self, 'browser_tab') and self.browser_tab:
                    self.browser_tab.page().runJavaScript("window.clearSelectedElements();")
            else:
                QMessageBox.information(self, "Sin Elementos", "No hay elementos seleccionados en JavaScript")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error procesando elementos: {str(e)}")
    
    def _get_element_type_from_tag(self, tag: str) -> str:
        """Get element type from tag name"""
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            return "Encabezado"
        elif tag == 'a':
            return "Enlace"
        elif tag in ['button', 'input']:
            return "Botón"
        elif tag == 'img':
            return "Imagen"
        elif tag == 'p':
            return "Párrafo"
        elif tag in ['span', 'div']:
            return "Contenedor"
        elif tag in ['li', 'td', 'th']:
            return "Elemento de lista"
        elif tag in ['strong', 'b', 'em', 'i']:
            return "Texto destacado"
        else:
            return "Otro"
    
    def run_extraction(self):
        """Ejecutar extracción de datos"""
        try:
            selectors_text = self.selectors_input.text()
            selectors = [s.strip() for s in selectors_text.split(',')] if selectors_text else ['h1', 'p', 'a']
            
            result = self.scraping_integration.extract_data(selectors)
            
            if "error" not in result:
                display_text = f"✅ EXTRACCIÓN COMPLETADA\n"
                display_text += f"🎯 Selectores usados: {len(result.get('selectors_used', []))}\n"
                display_text += f"📊 Total elementos: {result.get('total_elements', 0)}\n\n"
                
                # Display extracted data
                if result.get('extracted_data'):
                    display_text += "📥 DATOS EXTRAÍDOS:\n"
                    for selector, data in result['extracted_data'].items():
                        display_text += f"\n🔍 Selector '{selector}':\n"
                        if isinstance(data, list):
                            for i, item in enumerate(data[:3], 1):
                                display_text += f"   {i}. {item.get('text', 'Sin texto')[:50]}...\n"
                            if len(data) > 3:
                                display_text += f"   ... y {len(data) - 3} más\n"
                        else:
                            display_text += f"   {data.get('text', 'Sin texto')[:100]}...\n"
                
                self.extraction_text.setText(display_text)
            else:
                self.extraction_text.setText(f"❌ Error: {result.get('error', 'Desconocido')}")
        except Exception as e:
            self.extraction_text.setText(f"❌ Error: {str(e)}")
    
    def run_export(self):
        """Ejecutar exportación de datos"""
        try:
            if not self.scraping_integration.get_selected_elements():
                QMessageBox.warning(self, "Error", "No hay elementos seleccionados para exportar")
                return
            
            format_type = self.export_format.currentText().lower()
            filename = self.export_filename.text() or "scraped_data"
            
            result = self.scraping_integration.export_selected_data(format_type, filename)
            
            if "error" not in result:
                display_text = f"📤 EXPORTACIÓN COMPLETADA\n"
                display_text += f"📄 Formato: {result.get('format', 'N/A')}\n"
                display_text += f"📁 Archivo: {result.get('filename', 'N/A')}\n"
                display_text += f"📊 Elementos exportados: {result.get('elements_exported', 0)}\n"
                display_text += f"📋 Columnas exportadas: {result.get('columns_exported', 0)}\n\n"
                
                # Show sample of exported data
                display_text += "📋 COLUMNAS EXPORTADAS:\n"
                columns_info = [
                    "• tipo_elemento - Tipo de elemento HTML",
                    "• tipo_categoria - Categoría del elemento",
                    "• texto_limpio - Texto limpio sin caracteres especiales",
                    "• texto_original - Texto original extraído",
                    "• selector_css - Selector CSS del elemento",
                    "• importancia - Puntuación de importancia",
                    "• url_enlace - URL del enlace (si aplica)",
                    "• texto_enlace - Texto del enlace",
                    "• url_imagen - URL de la imagen (si aplica)",
                    "• texto_alternativo - Texto alternativo de imagen",
                    "• nivel_encabezado - Nivel H1-H6 (si aplica)",
                    "• texto_encabezado - Texto del encabezado",
                    "• tipo_boton - Tipo de botón (si aplica)",
                    "• valor_boton - Valor del botón",
                    "• atributo_* - Atributos HTML específicos"
                ]
                
                for column_info in columns_info:
                    display_text += f"  {column_info}\n"
                
                display_text += "\n💡 CONSEJOS:\n"
                display_text += "• CSV/Excel: Datos limpios y estructurados para análisis\n"
                display_text += "• JSON/YAML: Datos completos con metadatos\n"
                display_text += "• Los caracteres especiales han sido limpiados\n"
                display_text += "• Los datos están organizados por columnas específicas"
                
                self.export_text.setText(display_text)
                QMessageBox.information(self, "Éxito", 
                    f"✅ Datos exportados exitosamente\n"
                    f"📁 Archivo: {result.get('filename', 'archivo')}\n"
                    f"📊 {result.get('elements_exported', 0)} elementos exportados\n"
                    f"📋 {result.get('columns_exported', 0)} columnas de datos")
            else:
                self.export_text.setText(f"❌ Error: {result.get('error', 'Desconocido')}")
                QMessageBox.critical(self, "Error", f"Error exportando: {result.get('error', 'Desconocido')}")
        except Exception as e:
            self.export_text.setText(f"❌ Error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error exportando: {str(e)}")
    
    def run_discovery(self):
        """Ejecutar descubrimiento de URLs"""
        try:
            max_urls = self.max_urls_spin.value()
            
            result = self.scraping_integration.discover_urls(max_urls, 3)
            
            if "error" not in result:
                # Store discovered URLs for export
                self.discovered_urls = result.get('discovered_urls', [])
                self.fuzzing_results = result.get('fuzzing_results', [])
                
                display_text = f"✅ DESCUBRIMIENTO COMPLETADO\n"
                display_text += f"🔍 URLs encontradas: {len(self.discovered_urls)}\n"
                display_text += f"🎯 Resultados de fuzzing: {len(self.fuzzing_results)}\n\n"
                
                # Display discovered URLs
                if self.discovered_urls:
                    display_text += "🔗 URLs DESCUBIERTAS:\n"
                    for i, url in enumerate(self.discovered_urls[:10], 1):
                        display_text += f"   {i}. {url}\n"
                    if len(self.discovered_urls) > 10:
                        display_text += f"   ... y {len(self.discovered_urls) - 10} más\n"
                
                # Enable export buttons if URLs were found
                if self.discovered_urls:
                    self.export_csv_btn.setEnabled(True)
                    self.export_json_btn.setEnabled(True)
                    self.export_txt_btn.setEnabled(True)
                    self.export_excel_btn.setEnabled(True)
                    display_text += "\n📤 Botones de exportación habilitados"
                else:
                    self.export_csv_btn.setEnabled(False)
                    self.export_json_btn.setEnabled(False)
                    self.export_txt_btn.setEnabled(False)
                    self.export_excel_btn.setEnabled(False)
                    display_text += "\n⚠️ No se encontraron URLs para exportar"
                
                self.discovery_text.setText(display_text)
            else:
                self.discovery_text.setText(f"❌ Error: {result.get('error', 'Desconocido')}")
                # Disable export buttons on error
                self.export_csv_btn.setEnabled(False)
                self.export_json_btn.setEnabled(False)
                self.export_txt_btn.setEnabled(False)
                self.export_excel_btn.setEnabled(False)
        except Exception as e:
            self.discovery_text.setText(f"❌ Error: {str(e)}")
            # Disable export buttons on error
            self.export_csv_btn.setEnabled(False)
            self.export_json_btn.setEnabled(False)
            self.export_txt_btn.setEnabled(False)
            self.export_excel_btn.setEnabled(False)
    
    def export_urls(self, format_type: str):
        """Exportar URLs descubiertas a un formato específico"""
        try:
            if not self.discovered_urls:
                QMessageBox.warning(self, "Error", "No hay URLs para exportar.")
                return
            
            filename = f"discovered_urls.{format_type}"
            
            if format_type == 'csv':
                self.scraping_integration.export_urls_to_csv(self.discovered_urls, filename)
            elif format_type == 'json':
                self.scraping_integration.export_urls_to_json(self.discovered_urls, filename)
            elif format_type == 'txt':
                self.scraping_integration.export_urls_to_txt(self.discovered_urls, filename)
            elif format_type == 'excel':
                self.scraping_integration.export_urls_to_excel(self.discovered_urls, filename)
            
            QMessageBox.information(self, "Éxito", f"URLs exportadas exitosamente a {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error exportando URLs: {str(e)}")
    
    def refresh_status(self):
        """Actualizar estado del sistema"""
        try:
            result = self.scraping_integration.get_comprehensive_status()
            
            if "error" not in result:
                display_text = f"ℹ️ ESTADO DEL SISTEMA\n"
                display_text += f"🔧 Scrapelillo disponible: {result.get('scrapelillo_available', False)}\n"
                display_text += f"📦 Componentes: {len(result.get('components', {}))}\n\n"
                
                if result.get('current_state'):
                    state = result['current_state']
                    display_text += "📊 ESTADO ACTUAL:\n"
                    display_text += f"   • HTML cargado: {'✅' if state.get('html_loaded') else '❌'}\n"
                    display_text += f"   • URL cargada: {'✅' if state.get('url_loaded') else '❌'}\n"
                    display_text += f"   • Análisis listo: {'✅' if state.get('analysis_ready') else '❌'}\n"
                    display_text += f"   • Elementos seleccionados: {state.get('elements_selected', 0)}\n"
                    display_text += f"   • Datos extraídos: {'✅' if state.get('data_extracted') else '❌'}\n"
                
                self.status_text.setText(display_text)
            else:
                self.status_text.setText(f"❌ Error: {result.get('error', 'Desconocido')}")
        except Exception as e:
            self.status_text.setText(f"❌ Error: {str(e)}") 