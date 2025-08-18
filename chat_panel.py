#!/usr/bin/env python3
"""
Panel de Chat con IA - Integración con LM Studio
"""

import sys
import json
import time
import requests
from datetime import datetime
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, 
                               QTextEdit, QPushButton, QLabel, QSpinBox, 
                               QLineEdit, QComboBox, QListWidget, QListWidgetItem,
                               QCheckBox, QGroupBox, QScrollArea, QFrame, QMessageBox,
                               QSplitter, QProgressBar)
from PySide6.QtCore import Qt, QThread, Signal as pyqtSignal, QTimer
from PySide6.QtGui import QFont, QColor, QTextCursor

class ChatWorker(QThread):
    """Worker thread para manejar las comunicaciones con LM Studio"""
    response_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    connection_status = pyqtSignal(bool, str)
    
    def __init__(self, server_url, message, context=""):
        super().__init__()
        self.server_url = server_url
        self.message = message
        self.context = context
        self._is_running = True
        
    def stop(self):
        """Detener el worker de forma segura"""
        self._is_running = False
        self.wait()  # Esperar a que termine
        
    def run(self):
        try:
            if not self._is_running:
                return
                
            # Verificar conexión
            self.connection_status.emit(True, "Conectando...")
            
            # Validar URL del servidor
            if not self.server_url or not self.server_url.startswith(('http://', 'https://')):
                self.error_occurred.emit("URL del servidor inválida")
                self.connection_status.emit(False, "URL inválida")
                return
            
            if not self._is_running:
                return
            
            # Preparar payload para LM Studio
            payload = {
                "messages": [
                    {
                        "role": "system",
                        "content": f"Eres un asistente útil. Contexto adicional: {self.context}"
                    },
                    {
                        "role": "user", 
                        "content": self.message
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 1000,
                "stream": False
            }
            
            if not self._is_running:
                return
            
            # Realizar request con timeout más largo
            response = requests.post(
                f"{self.server_url}/v1/chat/completions",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60  # Aumentar timeout a 60 segundos
            )
            
            if not self._is_running:
                return
            
            if response.status_code == 200:
                data = response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    content = data["choices"][0]["message"]["content"]
                    if self._is_running:
                        self.response_received.emit(content)
                        self.connection_status.emit(True, "Respuesta recibida")
                else:
                    if self._is_running:
                        self.error_occurred.emit("Respuesta inválida del servidor")
            else:
                error_msg = f"Error del servidor: {response.status_code}"
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_msg = error_data["error"].get("message", error_msg)
                except:
                    pass
                if self._is_running:
                    self.error_occurred.emit(error_msg)
                
        except requests.exceptions.ConnectionError:
            if self._is_running:
                self.error_occurred.emit("No se pudo conectar al servidor LM Studio")
                self.connection_status.emit(False, "Sin conexión")
        except requests.exceptions.Timeout:
            if self._is_running:
                self.error_occurred.emit("Timeout: El servidor tardó demasiado en responder")
                self.connection_status.emit(False, "Timeout")
        except requests.exceptions.InvalidURL:
            if self._is_running:
                self.error_occurred.emit("URL del servidor inválida")
                self.connection_status.emit(False, "URL inválida")
        except Exception as e:
            if self._is_running:
                self.error_occurred.emit(f"Error: {str(e)}")
                self.connection_status.emit(False, "Error")

class ChatPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.chat_worker = None
        self.test_worker = None
        self.chat_history = []
        self.server_url = ""
        self.setup_ui()
        
    def closeEvent(self, event):
        """Manejar el cierre del panel de forma segura"""
        self.cleanup_workers()
        super().closeEvent(event)
        
    def cleanup_workers(self):
        """Limpiar workers de forma segura"""
        if self.chat_worker and self.chat_worker.isRunning():
            self.chat_worker.stop()
            self.chat_worker.wait()
        if self.test_worker and self.test_worker.isRunning():
            self.test_worker.stop()
            self.test_worker.wait()
        
    def setup_ui(self):
        """Setup complete UI for AI chat functionality"""
        layout = QVBoxLayout()
        
        # Create tab widget for all features
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)  # Pestañas planas estilo moderno
        
        # Create all tabs with comprehensive features
        self.tab_widget.addTab(self.create_chat_tab(), "💬 Chat con IA")
        self.tab_widget.addTab(self.create_settings_tab(), "⚙️ Configuración")
        self.tab_widget.addTab(self.create_history_tab(), "📚 Historial")
        self.tab_widget.addTab(self.create_help_tab(), "❓ Ayuda")
        
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)
        
    def create_chat_tab(self):
        """Tab principal del chat"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Connection status
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Estado: Desconectado")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        status_layout.addWidget(self.status_label)
        
        self.test_connection_btn = QPushButton("🔗 Probar Conexión")
        self.test_connection_btn.clicked.connect(self.test_connection)
        status_layout.addWidget(self.test_connection_btn)
        
        layout.addLayout(status_layout)
        
        # Chat area
        chat_splitter = QSplitter(Qt.Vertical)
        
        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setPlaceholderText("Inicia una conversación con la IA...")
        self.chat_display.setMinimumHeight(300)
        chat_splitter.addWidget(self.chat_display)
        
        # Input area
        input_widget = QWidget()
        input_layout = QVBoxLayout()
        
        # Message input
        self.message_input = QTextEdit()
        self.message_input.setMaximumHeight(100)
        self.message_input.setPlaceholderText("Escribe tu mensaje aquí...")
        self.message_input.setAcceptRichText(False)
        input_layout.addWidget(self.message_input)
        
        # Send controls
        send_layout = QHBoxLayout()
        
        self.send_btn = QPushButton("📤 Enviar")
        self.send_btn.clicked.connect(self.send_message)
        self.send_btn.setEnabled(False)
        send_layout.addWidget(self.send_btn)
        
        self.clear_btn = QPushButton("🗑️ Limpiar Chat")
        self.clear_btn.clicked.connect(self.clear_chat)
        send_layout.addWidget(self.clear_btn)
        
        self.context_checkbox = QCheckBox("Incluir contexto de página actual")
        self.context_checkbox.setChecked(True)
        send_layout.addWidget(self.context_checkbox)
        
        input_layout.addLayout(send_layout)
        input_widget.setLayout(input_layout)
        chat_splitter.addWidget(input_widget)
        
        layout.addWidget(chat_splitter)
        
        widget.setLayout(layout)
        return widget
        
    def create_settings_tab(self):
        """Tab de configuración del servidor"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Server configuration
        server_group = QGroupBox("Configuración del Servidor LM Studio")
        server_layout = QVBoxLayout()
        
        # Server URL input
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("URL del Servidor:"))
        self.server_url_input = QLineEdit()
        self.server_url_input.setPlaceholderText("http://localhost:1234")
        self.server_url_input.setFixedHeight(32)  # Altura consistente
        if hasattr(self.server_url_input, "setClearButtonEnabled"):
            self.server_url_input.setClearButtonEnabled(True)
        self.server_url_input.textChanged.connect(self.on_server_url_changed)
        url_layout.addWidget(self.server_url_input)
        
        self.save_url_btn = QPushButton("💾 Guardar URL")
        self.save_url_btn.clicked.connect(self.save_server_url)
        url_layout.addWidget(self.save_url_btn)
        
        server_layout.addLayout(url_layout)
        
        # Connection test
        test_layout = QHBoxLayout()
        self.test_btn = QPushButton("🔗 Probar Conexión")
        self.test_btn.clicked.connect(self.test_connection)
        test_layout.addWidget(self.test_btn)
        
        self.connection_status_label = QLabel("Estado: No configurado")
        test_layout.addWidget(self.connection_status_label)
        
        server_layout.addLayout(test_layout)
        
        # Advanced settings
        advanced_group = QGroupBox("Configuración Avanzada")
        advanced_layout = QVBoxLayout()
        
        # Temperature setting
        temp_layout = QHBoxLayout()
        temp_layout.addWidget(QLabel("Temperatura (creatividad):"))
        self.temperature_spin = QSpinBox()
        self.temperature_spin.setRange(0, 20)
        self.temperature_spin.setValue(7)
        self.temperature_spin.setSuffix(" (0.7)")
        temp_layout.addWidget(self.temperature_spin)
        
        advanced_layout.addLayout(temp_layout)
        
        # Max tokens setting
        tokens_layout = QHBoxLayout()
        tokens_layout.addWidget(QLabel("Máximo de tokens:"))
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(100, 4000)
        self.max_tokens_spin.setValue(1000)
        tokens_layout.addWidget(self.max_tokens_spin)
        
        advanced_layout.addLayout(tokens_layout)
        
        advanced_group.setLayout(advanced_layout)
        server_layout.addWidget(advanced_group)
        
        server_group.setLayout(server_layout)
        layout.addWidget(server_group)
        
        # Load saved settings
        self.load_settings()
        
        widget.setLayout(layout)
        return widget
        
    def create_history_tab(self):
        """Tab del historial de conversaciones"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.refresh_history_btn = QPushButton("🔄 Actualizar Historial")
        self.refresh_history_btn.clicked.connect(self.refresh_history)
        controls_layout.addWidget(self.refresh_history_btn)
        
        self.clear_history_btn = QPushButton("🗑️ Limpiar Historial")
        self.clear_history_btn.clicked.connect(self.clear_history)
        controls_layout.addWidget(self.clear_history_btn)
        
        self.export_history_btn = QPushButton("📤 Exportar Historial")
        self.export_history_btn.clicked.connect(self.export_history)
        controls_layout.addWidget(self.export_history_btn)
        
        layout.addLayout(controls_layout)
        
        # History list
        self.history_list = QListWidget()
        self.history_list.itemDoubleClicked.connect(self.load_conversation)
        layout.addWidget(self.history_list)
        
        widget.setLayout(layout)
        return widget
        
    def create_help_tab(self):
        """Tab de ayuda y documentación"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setHtml("""
        <h2>🤖 Panel de Chat con IA - Ayuda</h2>
        
        <h3>Configuración Inicial:</h3>
        <ol>
            <li>Descarga e instala <a href="https://lmstudio.ai/">LM Studio</a></li>
            <li>Abre LM Studio y descarga un modelo de IA</li>
            <li>Inicia el servidor local en LM Studio</li>
            <li>Configura la URL del servidor en la pestaña "Configuración"</li>
            <li>Prueba la conexión</li>
        </ol>
        
        <h3>Uso del Chat:</h3>
        <ul>
            <li><strong>Enviar mensaje:</strong> Escribe en el área de texto y presiona "Enviar"</li>
            <li><strong>Contexto de página:</strong> Marca la casilla para incluir información de la página actual</li>
            <li><strong>Limpiar chat:</strong> Usa el botón "Limpiar Chat" para empezar una nueva conversación</li>
        </ul>
        
        <h3>Configuración Avanzada:</h3>
        <ul>
            <li><strong>Temperatura:</strong> Controla la creatividad de las respuestas (0.0 = muy conservador, 1.0 = muy creativo)</li>
            <li><strong>Máximo de tokens:</strong> Limita la longitud de las respuestas</li>
        </ul>
        
        <h3>URLs típicas de LM Studio:</h3>
        <ul>
            <li><code>http://localhost:1234</code> - Puerto por defecto</li>
            <li><code>http://localhost:8080</code> - Puerto alternativo</li>
            <li><code>http://127.0.0.1:1234</code> - IP local</li>
        </ul>
        
        <h3>Solución de Problemas:</h3>
        <ul>
            <li><strong>Error de conexión:</strong> Verifica que LM Studio esté ejecutándose</li>
            <li><strong>Timeout:</strong> El modelo puede tardar en cargar, espera unos segundos</li>
            <li><strong>Respuesta vacía:</strong> Prueba con un mensaje más simple</li>
        </ul>
        """)
        
        layout.addWidget(help_text)
        widget.setLayout(layout)
        return widget
        
    def on_server_url_changed(self):
        """Callback cuando cambia la URL del servidor"""
        url = self.server_url_input.text().strip()
        if url:
            self.server_url = url
            self.send_btn.setEnabled(True)
        else:
            self.send_btn.setEnabled(False)
            
    def save_server_url(self):
        """Guardar la URL del servidor"""
        url = self.server_url_input.text().strip()
        if url:
            self.server_url = url
            self.save_settings()
            QMessageBox.information(self, "Configuración", "URL del servidor guardada correctamente")
        else:
            QMessageBox.warning(self, "Error", "Por favor ingresa una URL válida")
            
    def test_connection(self):
        """Probar la conexión con el servidor LM Studio"""
        if not self.server_url:
            QMessageBox.warning(self, "Error", "Por favor configura la URL del servidor primero")
            return
            
        try:
            # Crear worker para probar conexión
            self.test_worker = ChatWorker(self.server_url, "Hola", "")
            self.test_worker.response_received.connect(self.on_test_success)
            self.test_worker.error_occurred.connect(self.on_test_error)
            self.test_worker.connection_status.connect(self.on_connection_status)
            self.test_worker.start()
        except Exception as e:
            print(f"Error creando worker de prueba: {e}")
            QMessageBox.warning(self, "Error", f"Error al crear prueba de conexión: {e}")
        
    def on_test_success(self, response):
        """Callback cuando la prueba de conexión es exitosa"""
        self.status_label.setText("Estado: Conectado")
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
        self.connection_status_label.setText("Estado: Conectado ✓")
        QMessageBox.information(self, "Conexión Exitosa", "El servidor LM Studio responde correctamente")
        
    def on_test_error(self, error):
        """Callback cuando hay error en la prueba de conexión"""
        self.status_label.setText("Estado: Error de conexión")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        self.connection_status_label.setText("Estado: Error ✗")
        
        # Mensaje específico para modelo no cargado
        if "No models loaded" in error or "model_not_found" in error:
            error_msg = """Error: No hay modelos cargados en LM Studio.

Para solucionarlo:

1. Abre LM Studio
2. Ve a la pestaña 'Models'
3. Selecciona un modelo (recomendado: meta-llama-3-8b-instruct)
4. Haz clic en 'Load'
5. Espera a que se cargue (puede tardar 2-5 minutos)
6. Vuelve a probar la conexión

Una vez cargado el modelo, el chat funcionará correctamente."""
        else:
            error_msg = f"No se pudo conectar al servidor: {error}"
            
        QMessageBox.information(self, "Información", error_msg)
        
    def on_connection_status(self, connected, status):
        """Callback para actualizar el estado de conexión"""
        if connected:
            self.status_label.setText(f"Estado: {status}")
            self.status_label.setStyleSheet("color: blue; font-weight: bold;")
        else:
            self.status_label.setText(f"Estado: {status}")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            
    def send_message(self):
        """Enviar mensaje al servidor LM Studio"""
        message = self.message_input.toPlainText().strip()
        if not message:
            QMessageBox.warning(self, "Error", "Por favor escribe un mensaje")
            return
            
        if not self.server_url:
            QMessageBox.warning(self, "Error", "Por favor configura la URL del servidor primero")
            return
            
        # Limpiar worker anterior si existe
        if self.chat_worker and self.chat_worker.isRunning():
            self.chat_worker.stop()
            self.chat_worker.wait()
            
        # Obtener contexto de la página actual si está habilitado
        context = ""
        if self.context_checkbox.isChecked():
            # Intentar obtener información de la página actual del navegador
            try:
                # Buscar la ventana principal del navegador
                main_window = self.window()
                if hasattr(main_window, 'tab_manager'):
                    current_tab = main_window.tab_manager.tabs.currentWidget()
                    if current_tab:
                        current_url = current_tab.url().toString()
                        current_title = current_tab.page().title()
                        context = f"Contexto: Usuario navegando en '{current_title}' ({current_url})"
                    else:
                        context = "Contexto: Usuario navegando en el navegador web"
                else:
                    context = "Contexto: Usuario navegando en el navegador web"
            except Exception as e:
                print(f"Error obteniendo contexto de página: {e}")
                context = "Contexto: Usuario navegando en el navegador web"
            
        # Agregar mensaje del usuario al chat
        self.add_message_to_chat("Usuario", message, "user")
        
        # Limpiar input
        self.message_input.clear()
        
        # Deshabilitar botón mientras procesa
        self.send_btn.setEnabled(False)
        self.send_btn.setText("⏳ Procesando...")
        
        try:
            # Crear worker para enviar mensaje
            self.chat_worker = ChatWorker(self.server_url, message, context)
            self.chat_worker.response_received.connect(self.on_response_received)
            self.chat_worker.error_occurred.connect(self.on_response_error)
            self.chat_worker.connection_status.connect(self.on_connection_status)
            self.chat_worker.start()
        except Exception as e:
            print(f"Error creando worker de chat: {e}")
            self.add_message_to_chat("Sistema", f"Error al crear conexión: {e}", "error")
            self.send_btn.setEnabled(True)
            self.send_btn.setText("📤 Enviar")
        
    def on_response_received(self, response):
        """Callback cuando se recibe respuesta del servidor"""
        self.add_message_to_chat("IA", response, "assistant")
        
        # Guardar en historial
        self.save_to_history("Usuario", response)
        
        # Rehabilitar botón
        self.send_btn.setEnabled(True)
        self.send_btn.setText("📤 Enviar")
        
    def on_response_error(self, error):
        """Callback cuando hay error en la respuesta"""
        self.add_message_to_chat("Sistema", f"Error: {error}", "error")
        
        # Rehabilitar botón
        self.send_btn.setEnabled(True)
        self.send_btn.setText("📤 Enviar")
        
    def add_message_to_chat(self, sender, message, message_type):
        """Agregar mensaje al área de chat"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Formatear según el tipo de mensaje
        if message_type == "user":
            formatted_message = f'<div style="margin: 10px 0;"><strong style="color: #2196F3;">{sender} ({timestamp}):</strong><br>{message}</div>'
        elif message_type == "assistant":
            formatted_message = f'<div style="margin: 10px 0;"><strong style="color: #4CAF50;">{sender} ({timestamp}):</strong><br>{message}</div>'
        else:  # error
            formatted_message = f'<div style="margin: 10px 0;"><strong style="color: #F44336;">{sender} ({timestamp}):</strong><br>{message}</div>'
            
        # Agregar al chat
        self.chat_display.append(formatted_message)
        
        # Auto-scroll al final
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.chat_display.setTextCursor(cursor)
        
    def clear_chat(self):
        """Limpiar el área de chat"""
        self.chat_display.clear()
        self.chat_history = []
        
    def save_to_history(self, user_message, ai_response):
        """Guardar conversación en el historial"""
        conversation = {
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "ai_response": ai_response
        }
        self.chat_history.append(conversation)
        self.refresh_history()
        
    def refresh_history(self):
        """Actualizar la lista del historial"""
        self.history_list.clear()
        for i, conv in enumerate(self.chat_history):
            timestamp = datetime.fromisoformat(conv["timestamp"]).strftime("%Y-%m-%d %H:%M")
            item_text = f"{timestamp}: {conv['user_message'][:50]}..."
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, i)
            self.history_list.addItem(item)
            
    def load_conversation(self, item):
        """Cargar conversación desde el historial"""
        index = item.data(Qt.UserRole)
        if 0 <= index < len(self.chat_history):
            conv = self.chat_history[index]
            self.chat_display.clear()
            self.add_message_to_chat("Usuario", conv["user_message"], "user")
            self.add_message_to_chat("IA", conv["ai_response"], "assistant")
            
    def clear_history(self):
        """Limpiar el historial"""
        self.chat_history.clear()
        self.history_list.clear()
        
    def export_history(self):
        """Exportar historial a archivo"""
        if not self.chat_history:
            QMessageBox.information(self, "Historial", "No hay conversaciones para exportar")
            return
            
        try:
            filename = f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.chat_history, f, indent=2, ensure_ascii=False)
            QMessageBox.information(self, "Exportar", f"Historial exportado a {filename}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo exportar el historial: {e}")
            
    def load_settings(self):
        """Cargar configuración guardada"""
        try:
            # Aquí podrías cargar desde un archivo de configuración
            # Por ahora usamos valores por defecto
            pass
        except Exception as e:
            print(f"Error cargando configuración: {e}")
            
    def save_settings(self):
        """Guardar configuración"""
        try:
            # Aquí podrías guardar en un archivo de configuración
            pass
        except Exception as e:
            print(f"Error guardando configuración: {e}") 