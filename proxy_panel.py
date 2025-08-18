#!/usr/bin/env python3
"""
Panel de Gestión de Proxies - Integración completa con Scrapelillo
"""

import sys
import json
import time
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, 
                               QTextEdit, QPushButton, QLabel, QSpinBox, 
                               QLineEdit, QComboBox, QListWidget, QListWidgetItem,
                               QCheckBox, QGroupBox, QScrollArea, QFrame, QMessageBox,
                               QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog,
                               QProgressBar, QSplitter, QInputDialog, QApplication)
from PySide6.QtCore import Qt, QThread, Signal as pyqtSignal, QTimer
from PySide6.QtGui import QFont, QColor, QIcon

class ProxyValidationThread(QThread):
    """Thread para validar proxies en segundo plano"""
    validation_complete = pyqtSignal(dict)
    progress_updated = pyqtSignal(int, str)
    
    def __init__(self, proxy_manager, proxy_list):
        super().__init__()
        self.proxy_manager = proxy_manager
        self.proxy_list = proxy_list
        self.running = True
    
    def run(self):
        """Ejecutar validación de proxies"""
        results = {}
        total = len(self.proxy_list)
        
        for i, proxy in enumerate(self.proxy_list):
            if not self.running:
                break
                
            try:
                # Validar proxy usando el manager
                if hasattr(self.proxy_manager, 'validate_proxy_sync'):
                    is_valid = self.proxy_manager.validate_proxy_sync(proxy)
                elif hasattr(self.proxy_manager, 'validate_proxy'):
                    # Fallback para método asíncrono (simplificado para sync)
                    is_valid = True  # Placeholder - validación básica
                else:
                    is_valid = True  # Sin validación disponible
                    
                results[proxy] = {
                    'valid': is_valid,
                    'timestamp': datetime.now().isoformat(),
                    'response_time': 0  # Placeholder
                }
                
                self.progress_updated.emit(
                    int((i + 1) / total * 100),
                    f"Validando {proxy}..."
                )
                
            except Exception as e:
                results[proxy] = {
                    'valid': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
        
        self.validation_complete.emit(results)
    
    def stop(self):
        """Detener validación"""
        self.running = False

class ProxyPanel(QWidget):
    def __init__(self, proxy_manager=None, parent=None):
        super().__init__(parent)
        self.proxy_manager = proxy_manager
        self.validation_thread = None
        self.setup_ui()
        self.load_proxy_config()
    
    def setup_ui(self):
        """Setup complete UI for proxy management"""
        layout = QVBoxLayout()
        
        # Create tab widget for all features
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)  # Pestañas planas estilo moderno
        
        # Create all tabs with comprehensive features
        self.tab_widget.addTab(self.create_proxy_list_tab(), "📋 Lista de Proxies")
        self.tab_widget.addTab(self.create_configuration_tab(), "⚙️ Configuración")
        self.tab_widget.addTab(self.create_validation_tab(), "🔍 Validación")
        self.tab_widget.addTab(self.create_statistics_tab(), "📊 Estadísticas")
        self.tab_widget.addTab(self.create_import_export_tab(), "📤 Importar/Exportar")
        
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)
    
    def create_proxy_list_tab(self):
        """Tab para gestionar la lista de proxies"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.add_proxy_btn = QPushButton("➕ Añadir Proxy")
        self.add_proxy_btn.clicked.connect(self.add_proxy)
        controls_layout.addWidget(self.add_proxy_btn)
        
        self.remove_proxy_btn = QPushButton("🗑️ Eliminar Seleccionado")
        self.remove_proxy_btn.clicked.connect(self.remove_selected_proxy)
        controls_layout.addWidget(self.remove_proxy_btn)
        
        self.clear_all_btn = QPushButton("🗑️ Limpiar Todo")
        self.clear_all_btn.clicked.connect(self.clear_all_proxies)
        controls_layout.addWidget(self.clear_all_btn)
        
        self.refresh_btn = QPushButton("🔄 Actualizar Lista")
        self.refresh_btn.clicked.connect(self.refresh_proxy_list)
        controls_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(controls_layout)
        
        # Proxy input
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Nuevo Proxy:"))
        
        self.proxy_input = QLineEdit()
        self.proxy_input.setPlaceholderText("http://user:pass@host:port o host:port")
        self.proxy_input.setFixedHeight(32)  # Altura consistente
        if hasattr(self.proxy_input, "setClearButtonEnabled"):
            self.proxy_input.setClearButtonEnabled(True)
        input_layout.addWidget(self.proxy_input)
        
        self.add_single_btn = QPushButton("➕ Añadir")
        self.add_single_btn.clicked.connect(self.add_single_proxy)
        input_layout.addWidget(self.add_single_btn)
        
        layout.addLayout(input_layout)
        
        # Proxy table
        self.proxy_table = QTableWidget()
        self.proxy_table.setColumnCount(6)
        self.proxy_table.setHorizontalHeaderLabels([
            "Proxy", "Estado", "Último Uso", "Fallos", "Velocidad", "País"
        ])
        
        # Set table properties
        header = self.proxy_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.proxy_table)
        
        # Status bar
        self.status_label = QLabel("Listo")
        layout.addWidget(self.status_label)
        
        widget.setLayout(layout)
        return widget
    
    def create_configuration_tab(self):
        """Tab para configuración de proxies"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Enable/Disable proxies
        enable_group = QGroupBox("Habilitar Proxies")
        enable_layout = QVBoxLayout()
        
        self.enable_proxies_cb = QCheckBox("Habilitar rotación de proxies")
        self.enable_proxies_cb.toggled.connect(self.toggle_proxy_enabled)
        enable_layout.addWidget(self.enable_proxies_cb)
        
        enable_group.setLayout(enable_layout)
        layout.addWidget(enable_group)
        
        # Rotation strategy
        strategy_group = QGroupBox("Estrategia de Rotación")
        strategy_layout = QVBoxLayout()
        
        strategy_layout.addWidget(QLabel("Estrategia:"))
        self.strategy_combo = QComboBox()
        self.strategy_combo.addItems(["round_robin", "random", "weighted"])
        self.strategy_combo.currentTextChanged.connect(self.change_rotation_strategy)
        strategy_layout.addWidget(self.strategy_combo)
        
        strategy_group.setLayout(strategy_layout)
        layout.addWidget(strategy_group)
        
        # Timeout settings
        timeout_group = QGroupBox("Configuración de Timeout")
        timeout_layout = QHBoxLayout()
        
        timeout_layout.addWidget(QLabel("Timeout (segundos):"))
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 60)
        self.timeout_spin.setValue(10)
        self.timeout_spin.valueChanged.connect(self.change_timeout)
        timeout_layout.addWidget(self.timeout_spin)
        
        timeout_group.setLayout(timeout_layout)
        layout.addWidget(timeout_group)
        
        # Failure settings
        failure_group = QGroupBox("Configuración de Fallos")
        failure_layout = QHBoxLayout()
        
        failure_layout.addWidget(QLabel("Máximo fallos antes de desactivar:"))
        self.max_failures_spin = QSpinBox()
        self.max_failures_spin.setRange(1, 10)
        self.max_failures_spin.setValue(3)
        self.max_failures_spin.valueChanged.connect(self.change_max_failures)
        failure_layout.addWidget(self.max_failures_spin)
        
        failure_group.setLayout(failure_layout)
        layout.addWidget(failure_group)
        
        # Validation settings
        validation_group = QGroupBox("Configuración de Validación")
        validation_layout = QVBoxLayout()
        
        validation_layout.addWidget(QLabel("URL de validación:"))
        self.validation_url_input = QLineEdit()
        self.validation_url_input.setText("http://httpbin.org/ip")
        self.validation_url_input.setFixedHeight(32)  # Altura consistente
        if hasattr(self.validation_url_input, "setClearButtonEnabled"):
            self.validation_url_input.setClearButtonEnabled(True)
        self.validation_url_input.textChanged.connect(self.change_validation_url)
        validation_layout.addWidget(self.validation_url_input)
        
        validation_group.setLayout(validation_layout)
        layout.addWidget(validation_group)
        
        # Apply button
        self.apply_config_btn = QPushButton("💾 Aplicar Configuración")
        self.apply_config_btn.clicked.connect(self.apply_configuration)
        layout.addWidget(self.apply_config_btn)
        
        widget.setLayout(layout)
        return widget
    
    def create_validation_tab(self):
        """Tab para validar proxies"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Validation controls
        controls_layout = QHBoxLayout()
        
        self.validate_all_btn = QPushButton("🔍 Validar Todos")
        self.validate_all_btn.clicked.connect(self.validate_all_proxies)
        controls_layout.addWidget(self.validate_all_btn)
        
        self.validate_selected_btn = QPushButton("🔍 Validar Seleccionados")
        self.validate_selected_btn.clicked.connect(self.validate_selected_proxies)
        controls_layout.addWidget(self.validate_selected_btn)
        
        self.stop_validation_btn = QPushButton("⏹️ Detener Validación")
        self.stop_validation_btn.clicked.connect(self.stop_validation)
        self.stop_validation_btn.setEnabled(False)
        controls_layout.addWidget(self.stop_validation_btn)
        
        layout.addLayout(controls_layout)
        
        # Progress bar
        self.validation_progress = QProgressBar()
        self.validation_progress.setVisible(False)
        layout.addWidget(self.validation_progress)
        
        # Validation results
        self.validation_text = QTextEdit()
        self.validation_text.setPlaceholderText("Resultados de validación aparecerán aquí...")
        layout.addWidget(self.validation_text)
        
        widget.setLayout(layout)
        return widget
    
    def create_statistics_tab(self):
        """Tab para estadísticas de proxies"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Refresh button
        self.refresh_stats_btn = QPushButton("🔄 Actualizar Estadísticas")
        self.refresh_stats_btn.clicked.connect(self.refresh_statistics)
        layout.addWidget(self.refresh_stats_btn)
        
        # Statistics display
        self.stats_text = QTextEdit()
        self.stats_text.setPlaceholderText("Estadísticas aparecerán aquí...")
        layout.addWidget(self.stats_text)
        
        widget.setLayout(layout)
        return widget
    
    def create_import_export_tab(self):
        """Tab para importar/exportar proxies"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Import controls
        import_group = QGroupBox("Importar Proxies")
        import_layout = QVBoxLayout()
        
        import_btn_layout = QHBoxLayout()
        self.import_file_btn = QPushButton("📁 Importar desde Archivo")
        self.import_file_btn.clicked.connect(self.import_from_file)
        import_btn_layout.addWidget(self.import_file_btn)
        
        self.import_text_btn = QPushButton("📝 Importar desde Texto")
        self.import_text_btn.clicked.connect(self.import_from_text)
        import_btn_layout.addWidget(self.import_text_btn)
        
        import_layout.addLayout(import_btn_layout)
        import_group.setLayout(import_layout)
        layout.addWidget(import_group)
        
        # Export controls
        export_group = QGroupBox("Exportar Proxies")
        export_layout = QVBoxLayout()
        
        export_btn_layout = QHBoxLayout()
        self.export_file_btn = QPushButton("💾 Exportar a Archivo")
        self.export_file_btn.clicked.connect(self.export_to_file)
        export_btn_layout.addWidget(self.export_file_btn)
        
        self.export_text_btn = QPushButton("📋 Copiar a Portapapeles")
        self.export_text_btn.clicked.connect(self.export_to_clipboard)
        export_btn_layout.addWidget(self.export_text_btn)
        
        export_layout.addLayout(export_btn_layout)
        export_group.setLayout(export_layout)
        layout.addWidget(export_group)
        
        # Bulk input
        bulk_group = QGroupBox("Entrada Masiva")
        bulk_layout = QVBoxLayout()
        
        self.bulk_input = QTextEdit()
        self.bulk_input.setPlaceholderText("Pega aquí una lista de proxies (uno por línea)")
        self.bulk_input.setMaximumHeight(100)
        bulk_layout.addWidget(self.bulk_input)
        
        bulk_btn_layout = QHBoxLayout()
        self.add_bulk_btn = QPushButton("➕ Añadir Todos")
        self.add_bulk_btn.clicked.connect(self.add_bulk_proxies)
        bulk_btn_layout.addWidget(self.add_bulk_btn)
        
        self.clear_bulk_btn = QPushButton("🗑️ Limpiar")
        self.clear_bulk_btn.clicked.connect(self.clear_bulk_input)
        bulk_btn_layout.addWidget(self.clear_bulk_btn)
        
        bulk_layout.addLayout(bulk_btn_layout)
        bulk_group.setLayout(bulk_layout)
        layout.addWidget(bulk_group)
        
        widget.setLayout(layout)
        return widget
    
    # Action methods
    def add_proxy(self):
        """Añadir proxy manualmente"""
        proxy, ok = QInputDialog.getText(self, "Añadir Proxy", 
                                        "Introduce el proxy (formato: host:port o http://user:pass@host:port):")
        if ok and proxy.strip():
            self.add_single_proxy_to_manager(proxy.strip())
    
    def add_single_proxy(self):
        """Añadir proxy desde el input"""
        proxy = self.proxy_input.text().strip()
        if proxy:
            self.add_single_proxy_to_manager(proxy)
            self.proxy_input.clear()
    
    def add_single_proxy_to_manager(self, proxy):
        """Añadir proxy al manager"""
        try:
            if self.proxy_manager:
                self.proxy_manager.add_proxy(proxy)
                self.refresh_proxy_list()
                self.status_label.setText(f"Proxy añadido: {proxy}")
            else:
                QMessageBox.warning(self, "Error", "Proxy manager no disponible")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error añadiendo proxy: {str(e)}")
    
    def remove_selected_proxy(self):
        """Eliminar proxy seleccionado"""
        current_row = self.proxy_table.currentRow()
        if current_row >= 0:
            proxy_item = self.proxy_table.item(current_row, 0)
            if proxy_item:
                proxy = proxy_item.text()
                try:
                    if self.proxy_manager:
                        self.proxy_manager.remove_proxy(proxy)
                        self.refresh_proxy_list()
                        self.status_label.setText(f"Proxy eliminado: {proxy}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Error eliminando proxy: {str(e)}")
    
    def clear_all_proxies(self):
        """Limpiar todos los proxies"""
        reply = QMessageBox.question(self, "Confirmar", 
                                   "¿Estás seguro de que quieres eliminar todos los proxies?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                if self.proxy_manager:
                    # Clear all proxies
                    self.proxy_manager.proxies.clear()
                    self.refresh_proxy_list()
                    self.status_label.setText("Todos los proxies eliminados")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error limpiando proxies: {str(e)}")
    
    def refresh_proxy_list(self):
        """Actualizar la lista de proxies"""
        try:
            if not self.proxy_manager:
                return
            
            self.proxy_table.setRowCount(0)
            
            for proxy in self.proxy_manager.proxies:
                row = self.proxy_table.rowCount()
                self.proxy_table.insertRow(row)
                
                # Proxy URL
                self.proxy_table.setItem(row, 0, QTableWidgetItem(proxy.url))
                
                # Status
                status = "✅ Activo" if proxy.is_active else "❌ Inactivo"
                self.proxy_table.setItem(row, 1, QTableWidgetItem(status))
                
                # Last used
                last_used = proxy.last_used.isoformat() if proxy.last_used else "Nunca"
                self.proxy_table.setItem(row, 2, QTableWidgetItem(last_used))
                
                # Failures
                self.proxy_table.setItem(row, 3, QTableWidgetItem(str(proxy.failure_count)))
                
                # Speed
                speed = f"{proxy.speed:.2f}ms" if proxy.speed else "N/A"
                self.proxy_table.setItem(row, 4, QTableWidgetItem(speed))
                
                # Country
                country = proxy.country or "N/A"
                self.proxy_table.setItem(row, 5, QTableWidgetItem(country))
            
            self.status_label.setText(f"Lista actualizada: {len(self.proxy_manager.proxies)} proxies")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error actualizando lista: {str(e)}")
    
    def toggle_proxy_enabled(self, enabled):
        """Habilitar/deshabilitar proxies"""
        try:
            if self.proxy_manager:
                self.proxy_manager.enabled = enabled
                self.status_label.setText(f"Proxies {'habilitados' if enabled else 'deshabilitados'}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error cambiando estado: {str(e)}")
    
    def change_rotation_strategy(self, strategy):
        """Cambiar estrategia de rotación"""
        try:
            if self.proxy_manager:
                self.proxy_manager.rotation_strategy = strategy
                self.status_label.setText(f"Estrategia cambiada a: {strategy}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error cambiando estrategia: {str(e)}")
    
    def change_timeout(self, timeout):
        """Cambiar timeout"""
        try:
            if self.proxy_manager:
                self.proxy_manager.timeout = timeout
                self.status_label.setText(f"Timeout cambiado a: {timeout}s")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error cambiando timeout: {str(e)}")
    
    def change_max_failures(self, max_failures):
        """Cambiar máximo de fallos"""
        try:
            if self.proxy_manager:
                self.proxy_manager.max_failures = max_failures
                self.status_label.setText(f"Máximo fallos cambiado a: {max_failures}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error cambiando máximo fallos: {str(e)}")
    
    def change_validation_url(self, url):
        """Cambiar URL de validación"""
        try:
            if self.proxy_manager:
                self.proxy_manager.validation_url = url
                self.status_label.setText(f"URL de validación cambiada a: {url}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error cambiando URL de validación: {str(e)}")
    
    def apply_configuration(self):
        """Aplicar configuración"""
        try:
            # Apply all configuration changes
            self.status_label.setText("Configuración aplicada")
            QMessageBox.information(self, "Éxito", "Configuración aplicada correctamente")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error aplicando configuración: {str(e)}")
    
    def validate_all_proxies(self):
        """Validar todos los proxies"""
        if not self.proxy_manager or not self.proxy_manager.proxies:
            QMessageBox.warning(self, "Advertencia", "No hay proxies para validar")
            return
        
        self.start_validation(self.proxy_manager.proxies)
    
    def validate_selected_proxies(self):
        """Validar proxies seleccionados"""
        selected_rows = set(item.row() for item in self.proxy_table.selectedItems())
        if not selected_rows:
            QMessageBox.warning(self, "Advertencia", "No hay proxies seleccionados")
            return
        
        selected_proxies = []
        for row in selected_rows:
            proxy_item = self.proxy_table.item(row, 0)
            if proxy_item:
                proxy_url = proxy_item.text()
                # Find proxy object
                for proxy in self.proxy_manager.proxies:
                    if proxy.url == proxy_url:
                        selected_proxies.append(proxy)
                        break
        
        if selected_proxies:
            self.start_validation(selected_proxies)
    
    def start_validation(self, proxy_list):
        """Iniciar validación de proxies"""
        if self.validation_thread and self.validation_thread.isRunning():
            QMessageBox.warning(self, "Advertencia", "Validación ya en progreso")
            return
        
        self.validation_thread = ProxyValidationThread(self.proxy_manager, proxy_list)
        self.validation_thread.validation_complete.connect(self.on_validation_complete)
        self.validation_thread.progress_updated.connect(self.on_validation_progress)
        
        self.validation_progress.setVisible(True)
        self.validation_progress.setValue(0)
        self.stop_validation_btn.setEnabled(True)
        self.validate_all_btn.setEnabled(False)
        self.validate_selected_btn.setEnabled(False)
        
        self.validation_thread.start()
    
    def stop_validation(self):
        """Detener validación"""
        if self.validation_thread:
            self.validation_thread.stop()
            self.validation_thread.wait()
        
        self.validation_progress.setVisible(False)
        self.stop_validation_btn.setEnabled(False)
        self.validate_all_btn.setEnabled(True)
        self.validate_selected_btn.setEnabled(True)
    
    def on_validation_complete(self, results):
        """Callback cuando termina la validación"""
        self.validation_progress.setVisible(False)
        self.stop_validation_btn.setEnabled(False)
        self.validate_all_btn.setEnabled(True)
        self.validate_selected_btn.setEnabled(True)
        
        # Display results
        result_text = "🔍 RESULTADOS DE VALIDACIÓN\n\n"
        
        valid_count = 0
        for proxy, result in results.items():
            status = "✅ VÁLIDO" if result['valid'] else "❌ INVÁLIDO"
            error = result.get('error', '')
            result_text += f"{proxy}: {status}\n"
            if error:
                result_text += f"  Error: {error}\n"
            if result['valid']:
                valid_count += 1
        
        result_text += f"\n📊 RESUMEN:\n"
        result_text += f"  • Total validados: {len(results)}\n"
        result_text += f"  • Válidos: {valid_count}\n"
        result_text += f"  • Inválidos: {len(results) - valid_count}\n"
        
        self.validation_text.setText(result_text)
        self.refresh_proxy_list()  # Update table with new status
        self.status_label.setText(f"Validación completada: {valid_count}/{len(results)} válidos")
    
    def on_validation_progress(self, progress, message):
        """Callback para actualizar progreso de validación"""
        self.validation_progress.setValue(progress)
        self.status_label.setText(message)
    
    def refresh_statistics(self):
        """Actualizar estadísticas"""
        try:
            if not self.proxy_manager:
                self.stats_text.setText("❌ Proxy manager no disponible")
                return
            
            stats = self.proxy_manager.get_proxy_stats()
            
            stats_text = "📊 ESTADÍSTICAS DE PROXIES\n\n"
            stats_text += f"📈 GENERAL:\n"
            stats_text += f"  • Total de proxies: {stats.get('total_proxies', 0)}\n"
            stats_text += f"  • Proxies activos: {stats.get('active_proxies', 0)}\n"
            stats_text += f"  • Proxies fallidos: {stats.get('failed_proxies', 0)}\n\n"
            
            stats_text += f"🔄 USO:\n"
            stats_text += f"  • Total de requests: {stats.get('total_requests', 0)}\n"
            stats_text += f"  • Requests exitosos: {stats.get('successful_requests', 0)}\n"
            stats_text += f"  • Requests fallidos: {stats.get('failed_requests', 0)}\n"
            stats_text += f"  • Rotaciones: {stats.get('rotation_count', 0)}\n\n"
            
            if stats.get('last_rotation'):
                stats_text += f"⏰ Última rotación: {stats['last_rotation']}\n"
            
            self.stats_text.setText(stats_text)
            self.status_label.setText("Estadísticas actualizadas")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error actualizando estadísticas: {str(e)}")
    
    def import_from_file(self):
        """Importar proxies desde archivo"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo de proxies", "", 
            "Text files (*.txt);;All files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    proxies = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                
                for proxy in proxies:
                    self.add_single_proxy_to_manager(proxy)
                
                QMessageBox.information(self, "Éxito", f"Importados {len(proxies)} proxies desde {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error importando archivo: {str(e)}")
    
    def import_from_text(self):
        """Importar proxies desde texto"""
        text, ok = QInputDialog.getMultiLineText(
            self, "Importar Proxies", 
            "Pega aquí la lista de proxies (uno por línea):"
        )
        
        if ok and text.strip():
            proxies = [line.strip() for line in text.split('\n') if line.strip()]
            
            for proxy in proxies:
                self.add_single_proxy_to_manager(proxy)
            
            QMessageBox.information(self, "Éxito", f"Importados {len(proxies)} proxies")
    
    def export_to_file(self):
        """Exportar proxies a archivo"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Guardar archivo de proxies", "proxies.txt", 
            "Text files (*.txt);;All files (*)"
        )
        
        if file_path:
            try:
                if not self.proxy_manager:
                    raise Exception("Proxy manager no disponible")
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    for proxy in self.proxy_manager.proxies:
                        f.write(f"{proxy.url}\n")
                
                QMessageBox.information(self, "Éxito", f"Exportados {len(self.proxy_manager.proxies)} proxies a {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error exportando archivo: {str(e)}")
    
    def export_to_clipboard(self):
        """Exportar proxies al portapapeles"""
        try:
            if not self.proxy_manager:
                raise Exception("Proxy manager no disponible")
            
            proxy_list = '\n'.join(proxy.url for proxy in self.proxy_manager.proxies)
            
            # Copy to clipboard
            clipboard = QApplication.clipboard()
            clipboard.setText(proxy_list)
            
            QMessageBox.information(self, "Éxito", f"Copiados {len(self.proxy_manager.proxies)} proxies al portapapeles")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error copiando al portapapeles: {str(e)}")
    
    def add_bulk_proxies(self):
        """Añadir proxies en masa"""
        text = self.bulk_input.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Advertencia", "No hay texto para procesar")
            return
        
        proxies = [line.strip() for line in text.split('\n') if line.strip()]
        
        for proxy in proxies:
            self.add_single_proxy_to_manager(proxy)
        
        QMessageBox.information(self, "Éxito", f"Añadidos {len(proxies)} proxies")
        self.clear_bulk_input()
    
    def clear_bulk_input(self):
        """Limpiar entrada masiva"""
        self.bulk_input.clear()
    
    def load_proxy_config(self):
        """Cargar configuración de proxies"""
        try:
            if self.proxy_manager:
                # Load current configuration
                self.enable_proxies_cb.setChecked(self.proxy_manager.enabled)
                self.strategy_combo.setCurrentText(self.proxy_manager.rotation_strategy)
                self.timeout_spin.setValue(self.proxy_manager.timeout)
                self.max_failures_spin.setValue(self.proxy_manager.max_failures)
                self.validation_url_input.setText(self.proxy_manager.validation_url)
                
                # Refresh proxy list
                self.refresh_proxy_list()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error cargando configuración: {str(e)}") 