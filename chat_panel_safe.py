#!/usr/bin/env python3
"""
Panel de Chat con IA - Versión Segura
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
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor, QTextCursor

class ChatPanelSafe(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.chat_history = []
        self.server_url = ""
        self.setup_ui()
        
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
        self.test_connection_btn.clicked.connect(self.test_connection_safe)
        status_layout.addWidget(self.test_connection_btn)
        
        layout.addLayout(status_layout)
        
        # Context information display
        context_group = QGroupBox("📄 Información de Contexto de Página")
        context_layout = QVBoxLayout()
        
        self.context_info_label = QLabel("No hay información de contexto disponible")
        self.context_info_label.setStyleSheet("color: gray; font-style: italic;")
        self.context_info_label.setWordWrap(True)
        context_layout.addWidget(self.context_info_label)
        
        self.refresh_context_btn = QPushButton("🔄 Actualizar Contexto")
        self.refresh_context_btn.clicked.connect(self.update_context_info)
        context_layout.addWidget(self.refresh_context_btn)
        
        context_group.setLayout(context_layout)
        layout.addWidget(context_group)
        
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
        self.send_btn.clicked.connect(self.send_message_safe)
        self.send_btn.setEnabled(False)
        send_layout.addWidget(self.send_btn)
        
        self.clear_btn = QPushButton("🗑️ Limpiar Chat")
        self.clear_btn.clicked.connect(self.clear_chat)
        send_layout.addWidget(self.clear_btn)
        
        self.context_checkbox = QCheckBox("Incluir contexto de página actual")
        self.context_checkbox.setChecked(True)
        self.context_checkbox.toggled.connect(self.on_context_toggled)
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
        self.test_btn.clicked.connect(self.test_connection_safe)
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
            
    def test_connection_safe(self):
        """Probar la conexión de forma segura sin threads"""
        if not self.server_url:
            QMessageBox.warning(self, "Error", "Por favor configura la URL del servidor primero")
            return
            
        try:
            self.status_label.setText("Estado: Probando conexión...")
            self.status_label.setStyleSheet("color: blue; font-weight: bold;")
            
            # Probar conectividad básica
            response = requests.get(f"{self.server_url}/v1/models", timeout=10)
            
            if response.status_code != 200:
                self.status_label.setText("Estado: Error del servidor")
                self.status_label.setStyleSheet("color: red; font-weight: bold;")
                QMessageBox.warning(self, "Error", f"Error del servidor: {response.status_code}")
                return
                
            # Probar chat completions
            test_payload = {
                "messages": [{"role": "user", "content": "Hola"}],
                "temperature": 0.7,
                "max_tokens": 20,
                "stream": False
            }
            
            response = requests.post(
                f"{self.server_url}/v1/chat/completions",
                json=test_payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    self.status_label.setText("Estado: Conectado")
                    self.status_label.setStyleSheet("color: green; font-weight: bold;")
                    self.connection_status_label.setText("Estado: Conectado ✓")
                    QMessageBox.information(self, "Conexión Exitosa", "El servidor LM Studio responde correctamente")
                else:
                    self.status_label.setText("Estado: Respuesta inválida")
                    self.status_label.setStyleSheet("color: red; font-weight: bold;")
                    QMessageBox.warning(self, "Error", "Respuesta inválida del servidor")
            else:
                error_data = response.json()
                error_msg = error_data.get("error", {}).get("message", "")
                
                if "No models loaded" in error_msg:
                    self.status_label.setText("Estado: No hay modelos cargados")
                    self.status_label.setStyleSheet("color: orange; font-weight: bold;")
                    self.connection_status_label.setText("Estado: Sin modelo ✗")
                    
                    error_msg = """No hay modelos cargados en LM Studio.

Para solucionarlo:

1. Abre LM Studio
2. Ve a la pestaña 'Models'
3. Selecciona un modelo (recomendado: google/gemma-3-4b)
4. Haz clic en 'Load'
5. Espera a que se cargue (puede tardar 2-5 minutos)
6. Vuelve a probar la conexión

Una vez cargado el modelo, el chat funcionará correctamente."""
                    
                    QMessageBox.information(self, "Información", error_msg)
                else:
                    self.status_label.setText("Estado: Error de conexión")
                    self.status_label.setStyleSheet("color: red; font-weight: bold;")
                    self.connection_status_label.setText("Estado: Error ✗")
                    QMessageBox.warning(self, "Error", f"Error: {error_msg}")
                    
        except requests.exceptions.ConnectionError:
            self.status_label.setText("Estado: Sin conexión")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            QMessageBox.warning(self, "Error", "No se pudo conectar al servidor LM Studio")
        except requests.exceptions.Timeout:
            self.status_label.setText("Estado: Timeout")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            QMessageBox.warning(self, "Error", "Timeout: El servidor tardó demasiado en responder")
        except Exception as e:
            self.status_label.setText("Estado: Error")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            QMessageBox.warning(self, "Error", f"Error: {str(e)}")
            
    def send_message_safe(self):
        """Enviar mensaje de forma segura sin threads"""
        message = self.message_input.toPlainText().strip()
        if not message:
            QMessageBox.warning(self, "Error", "Por favor escribe un mensaje")
            return
            
        if not self.server_url:
            QMessageBox.warning(self, "Error", "Por favor configura la URL del servidor primero")
            return
            
        # Obtener contexto de la página actual usando la nueva función
        context = self.get_current_context()
        
        # Agregar mensaje del usuario al chat
        self.add_message_to_chat("Usuario", message, "user")
        
        # Limpiar input
        self.message_input.clear()
        
        # Deshabilitar botón mientras procesa
        self.send_btn.setEnabled(False)
        self.send_btn.setText("⏳ Procesando...")
        
        try:
            # Preparar payload
            payload = {
                "messages": [
                    {
                        "role": "system",
                        "content": f"Eres un asistente útil. Contexto adicional: {context}"
                    },
                    {
                        "role": "user", 
                        "content": message
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 1000,
                "stream": False
            }
            
            # Realizar request
            response = requests.post(
                f"{self.server_url}/v1/chat/completions",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    content = data["choices"][0]["message"]["content"]
                    self.add_message_to_chat("IA", content, "assistant")
                    self.save_to_history(message, content)
                else:
                    self.add_message_to_chat("Sistema", "Respuesta inválida del servidor", "error")
            else:
                error_data = response.json()
                error_msg = error_data.get("error", {}).get("message", "Error desconocido")
                self.add_message_to_chat("Sistema", f"Error: {error_msg}", "error")
                
        except requests.exceptions.ConnectionError:
            self.add_message_to_chat("Sistema", "No se pudo conectar al servidor LM Studio", "error")
        except requests.exceptions.Timeout:
            self.add_message_to_chat("Sistema", "Timeout: El servidor tardó demasiado en responder", "error")
        except Exception as e:
            self.add_message_to_chat("Sistema", f"Error: {str(e)}", "error")
        finally:
            # Rehabilitar botón
            self.send_btn.setEnabled(True)
            self.send_btn.setText("📤 Enviar")
        
    def format_ai_response(self, text):
        """Formatea la respuesta de la IA con estructura HTML adecuada"""
        if not text:
            return text
            
        # Convertir el texto a HTML con formato adecuado
        formatted_text = text
        
        # Formatear títulos principales (líneas que terminan con :)
        formatted_text = formatted_text.replace('\n\n', '\n')  # Normalizar saltos de línea
        
        # Detectar y formatear títulos principales (líneas que terminan con :)
        lines = formatted_text.split('\n')
        formatted_lines = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Detectar títulos principales (líneas que terminan con :)
            if line.endswith(':') and len(line) < 100:
                formatted_lines.append(f'<h3 style="color: #2E7D32; margin: 15px 0 10px 0; font-size: 16px; font-weight: bold;">{line}</h3>')
                continue
                
            # Detectar títulos secundarios (líneas que empiezan con **)
            if line.startswith('**') and line.endswith('**'):
                title = line[2:-2]  # Remover **
                formatted_lines.append(f'<h4 style="color: #388E3C; margin: 12px 0 8px 0; font-size: 14px; font-weight: bold;">{title}</h4>')
                continue
                
            # Detectar listas numeradas (líneas que empiezan con número.)
            if line and line[0].isdigit() and '. ' in line[:5]:
                parts = line.split('. ', 1)
                if len(parts) == 2:
                    number = parts[0]
                    content = parts[1]
                    formatted_lines.append(f'<div style="margin: 5px 0; padding-left: 20px;"><strong>{number}.</strong> {content}</div>')
                    continue
                    
            # Detectar elementos de lista con *
            if line.startswith('* ') or line.startswith('- '):
                content = line[2:] if line.startswith('* ') else line[2:]
                formatted_lines.append(f'<div style="margin: 3px 0; padding-left: 20px;">• {content}</div>')
                continue
                
            # Detectar elementos de lista con +
            if line.startswith('+ '):
                content = line[2:]
                formatted_lines.append(f'<div style="margin: 3px 0; padding-left: 20px;">• {content}</div>')
                continue
                
            # Detectar texto en negrita (**texto**)
            if '**' in line:
                # Reemplazar **texto** con <strong>texto</strong>
                import re
                line = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line)
                
            # Detectar texto en cursiva (*texto*)
            if '*' in line and '**' not in line:
                # Reemplazar *texto* con <em>texto</em> (solo si no es **)
                import re
                line = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', line)
                
            # Línea normal
            if line:
                formatted_lines.append(f'<div style="margin: 5px 0; line-height: 1.4;">{line}</div>')
        
        # Unir todas las líneas formateadas
        formatted_text = '\n'.join(formatted_lines)
        
        # Agregar estilos CSS para mejorar la presentación
        formatted_text = f'''
        <div style="
            font-family: 'Segoe UI', Arial, sans-serif;
            line-height: 1.5;
            color: #333;
            background-color: #f9f9f9;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #4CAF50;
            margin: 10px 0;
        ">
            {formatted_text}
        </div>
        '''
        
        return formatted_text

    def add_message_to_chat(self, sender, message, message_type):
        """Agregar mensaje al área de chat"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Formatear según el tipo de mensaje
        if message_type == "user":
            formatted_message = f'''
            <div style="
                margin: 10px 0;
                padding: 10px;
                background-color: #E3F2FD;
                border-radius: 8px;
                border-left: 4px solid #2196F3;
            ">
                <strong style="color: #1976D2; font-size: 14px;">{sender} ({timestamp}):</strong><br>
                <div style="margin-top: 5px; line-height: 1.4;">{message}</div>
            </div>
            '''
        elif message_type == "assistant":
            # Formatear la respuesta de la IA con estructura HTML
            formatted_content = self.format_ai_response(message)
            formatted_message = f'''
            <div style="margin: 10px 0;">
                <strong style="color: #2E7D32; font-size: 14px;">{sender} ({timestamp}):</strong><br>
                {formatted_content}
            </div>
            '''
        else:  # error
            formatted_message = f'''
            <div style="
                margin: 10px 0;
                padding: 10px;
                background-color: #FFEBEE;
                border-radius: 8px;
                border-left: 4px solid #F44336;
            ">
                <strong style="color: #D32F2F; font-size: 14px;">{sender} ({timestamp}):</strong><br>
                <div style="margin-top: 5px; line-height: 1.4;">{message}</div>
            </div>
            '''
            
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

    def update_context_info(self):
        """Actualiza la información de contexto de la página actual"""
        try:
            main_window = self.window()
            if hasattr(main_window, 'tab_manager'):
                current_tab = main_window.tab_manager.tabs.currentWidget()
                if current_tab:
                    current_url = current_tab.url().toString()
                    current_title = current_tab.page().title()
                    
                    # Formatear información de contexto
                    context_text = f"""
<b>📄 Página Actual:</b>
• <b>Título:</b> {current_title}
• <b>URL:</b> {current_url}
• <b>Estado:</b> {'✅ Contexto activo' if self.context_checkbox.isChecked() else '❌ Contexto desactivado'}
                    """
                    
                    self.context_info_label.setText(context_text)
                    self.context_info_label.setStyleSheet("color: black; font-weight: normal;")
                else:
                    self.context_info_label.setText("No hay pestaña activa")
                    self.context_info_label.setStyleSheet("color: orange; font-weight: bold;")
            else:
                self.context_info_label.setText("No se puede acceder al gestor de pestañas")
                self.context_info_label.setStyleSheet("color: red; font-weight: bold;")
        except Exception as e:
            self.context_info_label.setText(f"Error obteniendo contexto: {str(e)}")
            self.context_info_label.setStyleSheet("color: red; font-weight: bold;")
    
    def on_context_toggled(self, checked):
        """Callback cuando se activa/desactiva el contexto"""
        if checked:
            self.context_info_label.setStyleSheet("color: green; font-weight: bold;")
            # Actualizar el texto para mostrar que está activo
            current_text = self.context_info_label.text()
            if "Estado:" in current_text:
                current_text = current_text.replace("❌ Contexto desactivado", "✅ Contexto activo")
                self.context_info_label.setText(current_text)
        else:
            self.context_info_label.setStyleSheet("color: orange; font-weight: bold;")
            # Actualizar el texto para mostrar que está desactivado
            current_text = self.context_info_label.text()
            if "Estado:" in current_text:
                current_text = current_text.replace("✅ Contexto activo", "❌ Contexto desactivado")
                self.context_info_label.setText(current_text)
    
    def get_current_context(self):
        """Obtiene el contexto actual de la página"""
        if not self.context_checkbox.isChecked():
            return ""
            
        try:
            main_window = self.window()
            if hasattr(main_window, 'tab_manager'):
                current_tab = main_window.tab_manager.tabs.currentWidget()
                if current_tab:
                    current_url = current_tab.url().toString()
                    current_title = current_tab.page().title()
                    return f"Contexto: Usuario navegando en '{current_title}' ({current_url})"
                else:
                    return "Contexto: Usuario navegando en el navegador web"
            else:
                return "Contexto: Usuario navegando en el navegador web"
        except Exception as e:
            print(f"Error obteniendo contexto de página: {e}")
            return "Contexto: Usuario navegando en el navegador web" 