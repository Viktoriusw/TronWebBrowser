from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                              QLabel, QLineEdit, QListWidget, QListWidgetItem,
                              QDialog, QMessageBox, QInputDialog, QCheckBox,
                              QSpinBox, QComboBox, QGroupBox, QApplication,
                              QTableWidget, QTableWidgetItem, QHeaderView,
                              QDialogButtonBox)
from PySide6.QtCore import Qt, QSettings, Signal, QUrl, QObject, Slot
from PySide6.QtGui import QIcon, QIntValidator
from PySide6.QtWebEngineCore import QWebEngineScript
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel
import json
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import sqlite3
from datetime import datetime
from password_generator import PasswordGenerator

class PasswordBridge(QObject):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    @Slot(str, str, str)
    def saveCredentials(self, url, username, password):
        self.parent.show_password_dialog(url, username, password)

class PasswordManager(QWidget):
    password_saved = Signal(str, str)  # url, username
    password_updated = Signal(str, str)  # url, username
    password_deleted = Signal(str)  # url

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.password_generator = PasswordGenerator()
        self.settings = QSettings("TronBrowser", "Passwords")
        self.db_path = "passwords.db"
        self.init_ui()
        self.init_database()
        self.load_passwords()
        self.setup_encryption()
        self._webchannels = {}

    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        layout = QVBoxLayout(self)
        
        # Estilo oscuro global y específico para QListWidget
        self.setStyleSheet("""
            QWidget {
                background-color: #232323;
                color: #ffffff;
            }
            QLineEdit {
                background-color: #232323;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 4px;
            }
            QPushButton {
                background-color: #0d47a1;
                color: #ffffff;
                border: none;
                padding: 5px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QPushButton:pressed {
                background-color: #0a3d91;
            }
            QGroupBox {
                background-color: #232323;
                border: 1px solid #555555;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
                color: #ffffff;
            }
            QGroupBox::title {
                color: #ffffff;
                background-color: #232323;
            }
            QCheckBox {
                color: #ffffff;
                background-color: #232323;
            }
            QLabel {
                color: #ffffff;
                background-color: #232323;
            }
            QDialog {
                background-color: #232323;
                color: #ffffff;
            }
        """)
        
        # Barra de búsqueda
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar contraseñas...")
        self.search_input.textChanged.connect(self.filter_passwords)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Lista de contraseñas
        self.passwords_list = QListWidget()
        self.passwords_list.setStyleSheet("""
            QListWidget {
                background-color: #232323;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
            }
            QListWidget::item {
                background-color: #232323;
                color: #ffffff;
                padding: 8px;
            }
            QListWidget::item:selected {
                background-color: #0d47a1;
                color: #ffffff;
            }
        """)
        layout.addWidget(self.passwords_list)
        
        # Botones de acción
        buttons_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Añadir")
        self.add_button.clicked.connect(self.add_password)
        buttons_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Editar")
        self.edit_button.clicked.connect(self.edit_password)
        buttons_layout.addWidget(self.edit_button)
        
        self.remove_button = QPushButton("Eliminar")
        self.remove_button.clicked.connect(self.remove_password)
        buttons_layout.addWidget(self.remove_button)
        
        self.generate_button = QPushButton("Generar")
        self.generate_button.clicked.connect(self.show_generator)
        buttons_layout.addWidget(self.generate_button)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)

    def init_database(self):
        """Inicializa la base de datos de contraseñas"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS passwords (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.conn.commit()
        except Exception as e:
            print(f"Error inicializando base de datos: {str(e)}")

    def load_passwords(self):
        """Carga las contraseñas guardadas"""
        try:
            self.passwords_list.clear()
            cursor = self.conn.cursor()
            cursor.execute("SELECT url, username, notes FROM passwords ORDER BY url")
            for row in cursor.fetchall():
                item = QListWidgetItem(f"{row[0]} - {row[1]}")
                if row[2]:
                    item.setToolTip(row[2])
                self.passwords_list.addItem(item)
        except Exception as e:
            print(f"Error cargando contraseñas: {str(e)}")

    def filter_passwords(self):
        """Filtra las contraseñas según el texto de búsqueda"""
        search_text = self.search_input.text().lower()
        for i in range(self.passwords_list.count()):
            item = self.passwords_list.item(i)
            item.setHidden(search_text not in item.text().lower())

    def add_password(self):
        """Añade una nueva contraseña"""
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("Añadir Contraseña")
            layout = QVBoxLayout(dialog)
            
            # Campos
            url_input = QLineEdit()
            layout.addWidget(QLabel("URL:"))
            layout.addWidget(url_input)
            
            username_input = QLineEdit()
            layout.addWidget(QLabel("Usuario:"))
            layout.addWidget(username_input)
            
            password_input = QLineEdit()
            password_input.setEchoMode(QLineEdit.Password)
            layout.addWidget(QLabel("Contraseña:"))
            layout.addWidget(password_input)
            
            notes_input = QLineEdit()
            layout.addWidget(QLabel("Notas:"))
            layout.addWidget(notes_input)
            
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
                cursor = self.conn.cursor()
                cursor.execute(
                    "INSERT INTO passwords (url, username, password, notes) VALUES (?, ?, ?, ?)",
                    (url_input.text(), username_input.text(), password_input.text(), notes_input.text())
                )
                self.conn.commit()
                self.load_passwords()
                self.password_saved.emit(url_input.text(), username_input.text())
                
        except Exception as e:
            print(f"Error añadiendo contraseña: {str(e)}")

    def edit_password(self):
        """Edita una contraseña existente"""
        try:
            current_item = self.passwords_list.currentItem()
            if not current_item:
                return
                
            url, username = current_item.text().split(" - ")
            
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT password, notes FROM passwords WHERE url = ? AND username = ?",
                (url, username)
            )
            row = cursor.fetchone()
            
            if not row:
                return
                
            dialog = QDialog(self)
            dialog.setWindowTitle("Editar Contraseña")
            layout = QVBoxLayout(dialog)
            
            # Campos
            url_input = QLineEdit(url)
            layout.addWidget(QLabel("URL:"))
            layout.addWidget(url_input)
            
            username_input = QLineEdit(username)
            layout.addWidget(QLabel("Usuario:"))
            layout.addWidget(username_input)
            
            password_input = QLineEdit(row[0])
            password_input.setEchoMode(QLineEdit.Password)
            layout.addWidget(QLabel("Contraseña:"))
            layout.addWidget(password_input)
            
            notes_input = QLineEdit(row[1] if row[1] else "")
            layout.addWidget(QLabel("Notas:"))
            layout.addWidget(notes_input)
            
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
                cursor.execute(
                    "UPDATE passwords SET url = ?, username = ?, password = ?, notes = ?, updated_at = CURRENT_TIMESTAMP WHERE url = ? AND username = ?",
                    (url_input.text(), username_input.text(), password_input.text(), notes_input.text(), url, username)
                )
                self.conn.commit()
                self.load_passwords()
                self.password_updated.emit(url_input.text(), username_input.text())
                
        except Exception as e:
            print(f"Error editando contraseña: {str(e)}")

    def remove_password(self):
        """Elimina una contraseña"""
        try:
            current_item = self.passwords_list.currentItem()
            if not current_item:
                return
                
            url, username = current_item.text().split(" - ")
            
            reply = QMessageBox.question(
                self,
                "Confirmar eliminación",
                f"¿Estás seguro de que quieres eliminar la contraseña para {url}?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                cursor = self.conn.cursor()
                cursor.execute(
                    "DELETE FROM passwords WHERE url = ? AND username = ?",
                    (url, username)
                )
                self.conn.commit()
                self.load_passwords()
                self.password_deleted.emit(url)
                
        except Exception as e:
            print(f"Error eliminando contraseña: {str(e)}")

    def show_generator(self):
        """Muestra el generador de contraseñas"""
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("Generador de Contraseñas")
            dialog.setStyleSheet("""
                QDialog {
                    background-color: #232323;
                    color: #ffffff;
                }
                QLabel {
                    color: #ffffff;
                    background-color: #232323;
                }
                QLineEdit {
                    background-color: #232323;
                    color: #ffffff;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    padding: 4px;
                }
                QPushButton {
                    background-color: #0d47a1;
                    color: #ffffff;
                    border: none;
                    padding: 5px 15px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #1565c0;
                    color: #ffffff;
                }
                QPushButton:pressed {
                    background-color: #0a3d91;
                    color: #ffffff;
                }
                QGroupBox {
                    background-color: #232323;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    margin-top: 10px;
                    padding-top: 10px;
                    color: #ffffff;
                }
                QGroupBox::title {
                    color: #ffffff;
                    background-color: #232323;
                }
                QCheckBox {
                    color: #ffffff;
                    background-color: #232323;
                }
            """)
            layout = QVBoxLayout(dialog)
            
            # Opciones de generación
            options_group = QGroupBox("Opciones")
            options_layout = QVBoxLayout()
            
            length_layout = QHBoxLayout()
            length_layout.addWidget(QLabel("Longitud:"))
            length_input = QLineEdit()
            length_input.setPlaceholderText("Ingrese longitud (8-10,000,000)")
            length_input.setValidator(QIntValidator(8, 10_000_000))
            length_input.setText("16")  # Valor por defecto
            length_layout.addWidget(length_input)
            options_layout.addLayout(length_layout)
            
            numbers_check = QCheckBox("Incluir números")
            numbers_check.setChecked(True)
            options_layout.addWidget(numbers_check)
            
            uppercase_check = QCheckBox("Incluir mayúsculas")
            uppercase_check.setChecked(True)
            options_layout.addWidget(uppercase_check)
            
            lowercase_check = QCheckBox("Incluir minúsculas")
            lowercase_check.setChecked(True)
            options_layout.addWidget(lowercase_check)
            
            special_check = QCheckBox("Incluir caracteres especiales")
            special_check.setChecked(True)
            options_layout.addWidget(special_check)
            
            options_group.setLayout(options_layout)
            layout.addWidget(options_group)
            
            # Contraseña generada
            result_group = QGroupBox("Resultado")
            result_layout = QVBoxLayout()
            
            password_input = QLineEdit()
            password_input.setReadOnly(True)
            result_layout.addWidget(password_input)
            
            stats_label = QLabel()
            result_layout.addWidget(stats_label)
            
            result_group.setLayout(result_layout)
            layout.addWidget(result_group)
            
            # Botones
            buttons_layout = QHBoxLayout()
            
            generate_button = QPushButton("Generar")
            def generate():
                try:
                    length = int(length_input.text())
                    if length < 8 or length > 10_000_000:
                        raise ValueError("La longitud debe estar entre 8 y 10,000,000 caracteres")
                        
                    result = self.password_generator.generate_password(
                        length=length,
                        include_numbers=numbers_check.isChecked(),
                        include_uppercase=uppercase_check.isChecked(),
                        include_lowercase=lowercase_check.isChecked(),
                        include_special=special_check.isChecked()
                    )
                    password_input.setText(result["password"])
                    stats_label.setText(
                        f"Tiempo: {result['time']}\n"
                        f"CPU: {result['cpu_usage']}\n"
                        f"RAM: {result['ram_usage']}"
                    )
                except Exception as e:
                    QMessageBox.critical(dialog, "Error", str(e))
            
            generate_button.clicked.connect(generate)
            buttons_layout.addWidget(generate_button)
            
            copy_button = QPushButton("Copiar")
            copy_button.clicked.connect(lambda: QApplication.clipboard().setText(password_input.text()))
            buttons_layout.addWidget(copy_button)
            
            close_button = QPushButton("Cerrar")
            close_button.clicked.connect(dialog.accept)
            buttons_layout.addWidget(close_button)
            
            layout.addLayout(buttons_layout)
            
            # Generar primera contraseña
            generate()
            
            dialog.exec()
            
        except Exception as e:
            print(f"Error mostrando generador: {str(e)}")

    def setup_encryption(self):
        try:
            # Generar o cargar clave de encriptación
            if not self.settings.contains("encryption_key"):
                key = Fernet.generate_key()
                self.settings.setValue("encryption_key", key.decode())
            self.fernet = Fernet(self.settings.value("encryption_key").encode())
        except Exception as e:
            print(f"Error setting up encryption: {str(e)}")

    def save_password(self, url, username, password):
        try:
            # Encriptar la contraseña
            encrypted_password = self.fernet.encrypt(password.encode())
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO passwords (url, username, password)
                VALUES (?, ?, ?)
            ''', (url, username, encrypted_password.decode()))
            conn.commit()
            conn.close()
            
            print(f"Password saved for {url}")
            return True
        except Exception as e:
            print(f"Error saving password: {str(e)}")
            return False

    def get_password(self, url, username):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT password FROM passwords
                WHERE url = ? AND username = ?
            ''', (url, username))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                # Desencriptar la contraseña
                decrypted_password = self.fernet.decrypt(result[0].encode())
                return decrypted_password.decode()
            return None
        except Exception as e:
            print(f"Error getting password: {str(e)}")
            return None

    def get_all_passwords(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT url, username, password FROM passwords')
            results = cursor.fetchall()
            conn.close()
            
            passwords = []
            for url, username, encrypted_password in results:
                try:
                    decrypted_password = self.fernet.decrypt(encrypted_password.encode())
                    passwords.append({
                        'url': url,
                        'username': username,
                        'password': decrypted_password.decode()
                    })
                except:
                    continue
            return passwords
        except Exception as e:
            print(f"Error getting all passwords: {str(e)}")
            return []

    def delete_password(self, url, username):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM passwords
                WHERE url = ? AND username = ?
            ''', (url, username))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting password: {str(e)}")
            return False

    def show_password_dialog(self, url, username, password):
        try:
            dialog = QDialog(self.parent)
            dialog.setWindowTitle("Guardar Contraseña")
            layout = QVBoxLayout()
            
            # Mostrar información
            layout.addWidget(QLabel(f"¿Guardar contraseña para {url}?"))
            layout.addWidget(QLabel(f"Usuario: {username}"))
            
            # Botones
            buttons = QDialogButtonBox(
                QDialogButtonBox.Save | QDialogButtonBox.Cancel
            )
            buttons.accepted.connect(lambda: self.save_password(url, username, password))
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)
            
            dialog.setLayout(layout)
            dialog.exec()
        except Exception as e:
            print(f"Error showing password dialog: {str(e)}")

    def show_passwords_dialog(self):
        try:
            dialog = QDialog(self.parent)
            dialog.setWindowTitle("Saved Passwords")
            dialog.setMinimumSize(600, 400)
            
            layout = QVBoxLayout()
            
            # Tabla de contraseñas
            table = QTableWidget()
            table.setColumnCount(3)
            table.setHorizontalHeaderLabels(["URL", "Username", "Password"])
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            
            # Llenar tabla
            passwords = self.get_all_passwords()
            table.setRowCount(len(passwords))
            for i, pwd in enumerate(passwords):
                table.setItem(i, 0, QTableWidgetItem(pwd['url']))
                table.setItem(i, 1, QTableWidgetItem(pwd['username']))
                table.setItem(i, 2, QTableWidgetItem(pwd['password']))
            
            layout.addWidget(table)
            
            # Botones
            buttons = QDialogButtonBox(QDialogButtonBox.Close)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)
            
            dialog.setLayout(layout)
            dialog.exec()
        except Exception as e:
            print(f"Error showing passwords dialog: {str(e)}")

    def closeEvent(self, event):
        """Maneja el cierre del widget"""
        try:
            if hasattr(self, 'conn'):
                self.conn.close()
        except Exception as e:
            print(f"Error cerrando conexión: {str(e)}")
        finally:
            super().closeEvent(event)

    def setup_browser(self, browser):
        try:
            if browser and hasattr(browser, 'page'):
                # QWebChannel y bridge
                page = browser.page()
                channel = QWebChannel(page)
                bridge = PasswordBridge(self)
                channel.registerObject('passwordBridge', bridge)
                page.setWebChannel(channel)
                self._webchannels[id(page)] = (channel, bridge)

                # Script de QWebChannel
                qwebchannel_script = '''
                (function() {
                    function QWebChannel(transport, initCallback) {
                        if (typeof transport !== "object" || typeof transport.send !== "function") {
                            console.error("The QWebChannel expects a transport object with a send function and onmessage callback property.");
                            return;
                        }

                        var channel = this;
                        channel.transport = transport;
                        transport.onmessage = function(message) {
                            var data = JSON.parse(message.data);
                            channel.handleMessage(data);
                        }
                        channel.execCallbacks = {};
                        channel.execId = 0;
                        channel.exec = function(data, callback) {
                            if (!callback) {
                                callback = function() {};
                            }
                            channel.execId++;
                            channel.execCallbacks[channel.execId] = callback;
                            data.id = channel.execId;
                            channel.transport.send(JSON.stringify(data));
                        };
                        channel.execWithPromise = function(data) {
                            return new Promise(function(resolve, reject) {
                                channel.exec(data, function(response) {
                                    if (response.error) {
                                        reject(response.error);
                                    } else {
                                        resolve(response.data);
                                    }
                                });
                            });
                        };
                        channel.handleMessage = function(message) {
                            var callback = channel.execCallbacks[message.id];
                            if (callback) {
                                callback(message.data);
                                delete channel.execCallbacks[message.id];
                            }
                        };
                        channel.registerObjects = function(objects) {
                            channel.objects = objects;
                        };
                        channel.registerObject = function(name, object) {
                            if (!channel.objects) {
                                channel.objects = {};
                            }
                            channel.objects[name] = object;
                        };
                        channel.destroy = function() {
                            if (channel.transport) {
                                channel.transport.onmessage = undefined;
                            }
                            for (var i in channel.execCallbacks) {
                                channel.execCallbacks[i]({error: "Channel destroyed"});
                            }
                        };
                        channel.exec({type: "init"}, function(data) {
                            for (var i in data) {
                                var object = new QObject(this, i, data[i], function(name, data) {
                                    channel.exec({type: "invokeMethod", object: name, method: data.method, args: data.args});
                                });
                                channel.objects[i] = object;
                            }
                            if (initCallback) {
                                initCallback(channel);
                            }
                        });
                    }

                    function QObject(webChannel, name, data, callback) {
                        function QObject() {}
                        QObject.prototype = {
                            _id: name,
                            _webChannel: webChannel,
                            _data: data,
                            _callback: callback,
                            _signals: {},
                            _propertyUpdateVersion: {},
                            _methodReturnValues: {},
                            _invokableProperties: data.invokableProperties,
                            _invokableMethods: data.invokableMethods,
                            _propertyUpdateVersionTimeout: 0,
                            _notifyAboutNewProperties: false,
                            _signalEmitted: signalEmitted,
                            _invokeMethod: invokeMethod,
                            _connectNotify: connectNotify,
                            _disconnectNotify: disconnectNotify
                        };
                        return new QObject();
                    }

                    function signalEmitted(signalName, signalData) {
                        var signal = this._signals[signalName];
                        if (signal) {
                            signal.emit(signalData);
                        }
                    }

                    function invokeMethod(methodName, args) {
                        return this._callback(this._id, {method: methodName, args: args});
                    }

                    function connectNotify(signalName, callback) {
                        if (!this._signals[signalName]) {
                            this._signals[signalName] = new Signal();
                        }
                        this._signals[signalName].connect(callback);
                    }

                    function disconnectNotify(signalName, callback) {
                        if (this._signals[signalName]) {
                            this._signals[signalName].disconnect(callback);
                        }
                    }

                    function Signal() {
                        this.connect = function(callback) {
                            if (typeof callback !== "function") {
                                console.error("Signal.connect: Cannot connect to non-function");
                                return;
                            }
                            this.callbacks.push(callback);
                        };
                        this.disconnect = function(callback) {
                            var index = this.callbacks.indexOf(callback);
                            if (index !== -1) {
                                this.callbacks.splice(index, 1);
                            }
                        };
                        this.emit = function(data) {
                            for (var i = 0; i < this.callbacks.length; ++i) {
                                this.callbacks[i](data);
                            }
                        };
                        this.callbacks = [];
                    }

                    window.QWebChannel = QWebChannel;
                })();
                '''

                # Script de detección de formularios
                form_script = '''
                (function() {
                    // Función para configurar el bridge
                    function setupBridge() {
                        try {
                            if (typeof qt === 'undefined' || !qt.webChannelTransport) {
                                console.error('QWebChannel not available');
                                return;
                            }
                            
                            new QWebChannel(qt.webChannelTransport, function(channel) {
                                window.passwordBridge = channel.objects.passwordBridge;
                                setupFormHandlers();
                            });
                        } catch (e) {
                            console.error('Error setting up bridge:', e);
                        }
                    }

                    // Función para encontrar campos de formulario
                    function findFormFields(form) {
                        var fields = { username: null, password: null };
                        
                        // Buscar campo de usuario
                        var usernameInputs = form.querySelectorAll('input[type="text"], input[type="email"], input[name*="user"], input[name*="email"], input[id*="user"], input[id*="email"]');
                        for (var i = 0; i < usernameInputs.length; i++) {
                            var input = usernameInputs[i];
                            var name = (input.name || '').toLowerCase();
                            var id = (input.id || '').toLowerCase();
                            var placeholder = (input.placeholder || '').toLowerCase();
                            if (name.includes('user') || name.includes('email') || id.includes('user') || id.includes('email') || placeholder.includes('user') || placeholder.includes('email')) {
                                fields.username = input;
                                break;
                            }
                        }
                        
                        // Buscar campo de contraseña
                        var passwordInputs = form.querySelectorAll('input[type="password"], input[name*="pass"], input[id*="pass"]');
                        if (passwordInputs.length > 0) {
                            fields.password = passwordInputs[0];
                        }
                        
                        return fields;
                    }

                    // Función para configurar un formulario
                    function setupForm(form) {
                        var isLoginForm = false;
                        var formHtml = form.outerHTML.toLowerCase();
                        var formAction = (form.action || '').toLowerCase();
                        var formId = (form.id || '').toLowerCase();
                        var formClass = (form.className || '').toLowerCase();
                        
                        if (formHtml.includes('login') || formHtml.includes('signin') || 
                            formHtml.includes('register') || formHtml.includes('signup') || 
                            formAction.includes('login') || formAction.includes('signin') || 
                            formAction.includes('register') || formAction.includes('signup') || 
                            formId.includes('login') || formId.includes('signin') || 
                            formId.includes('register') || formId.includes('signup') || 
                            formClass.includes('login') || formClass.includes('signin') || 
                            formClass.includes('register') || formClass.includes('signup')) {
                            isLoginForm = true;
                        }
                        
                        var fields = findFormFields(form);
                        if (isLoginForm || (fields.username && fields.password)) {
                            form.removeEventListener('submit', form._submitHandler);
                            form._submitHandler = function(e) {
                                setTimeout(function() {
                                    var fields = findFormFields(form);
                                    if (fields.username && fields.username.value && 
                                        fields.password && fields.password.value) {
                                        if (window.passwordBridge && window.passwordBridge.saveCredentials) {
                                            window.passwordBridge.saveCredentials(
                                                window.location.href,
                                                fields.username.value,
                                                fields.password.value
                                            );
                                        }
                                    }
                                }, 100);
                            };
                            form.addEventListener('submit', form._submitHandler);
                        }
                    }

                    // Función para configurar todos los manejadores
                    function setupFormHandlers() {
                        // Configurar formularios existentes
                        document.querySelectorAll('form').forEach(setupForm);

                        // Observar cambios en el DOM para nuevos formularios
                        var observer = new MutationObserver(function(mutations) {
                            mutations.forEach(function(mutation) {
                                if (mutation.addedNodes) {
                                    mutation.addedNodes.forEach(function(node) {
                                        if (node.nodeName === 'FORM') {
                                            setupForm(node);
                                        }
                                    });
                                }
                            });
                        });
                        observer.observe(document.body, { childList: true, subtree: true });

                        // Observar cambios en campos de entrada
                        document.addEventListener('input', function(e) {
                            if (e.target.tagName === 'INPUT') {
                                var form = e.target.form;
                                if (form) {
                                    setupForm(form);
                                }
                            }
                        });
                    }

                    // Esperar a que el documento esté listo
                    if (document.readyState === 'loading') {
                        document.addEventListener('DOMContentLoaded', setupBridge);
                    } else {
                        setupBridge();
                    }
                })();
                '''
                
                # Crear y configurar los scripts
                qwebchannel_script_obj = QWebEngineScript()
                qwebchannel_script_obj.setSourceCode(qwebchannel_script)
                qwebchannel_script_obj.setInjectionPoint(QWebEngineScript.DocumentCreation)
                qwebchannel_script_obj.setWorldId(QWebEngineScript.MainWorld)
                qwebchannel_script_obj.setRunsOnSubFrames(True)

                form_script_obj = QWebEngineScript()
                form_script_obj.setSourceCode(form_script)
                form_script_obj.setInjectionPoint(QWebEngineScript.DocumentCreation)
                form_script_obj.setWorldId(QWebEngineScript.MainWorld)
                form_script_obj.setRunsOnSubFrames(True)
                
                # Asegurarse de que los scripts se ejecuten después de que la página esté cargada
                def insert_scripts(ok):
                    if ok:
                        page.scripts().insert(qwebchannel_script_obj)
                        page.scripts().insert(form_script_obj)
                
                page.loadFinished.connect(insert_scripts)
                
                print("Gestor de contraseñas configurado correctamente")
        except Exception as e:
            print(f"Error setting up browser: {str(e)}") 