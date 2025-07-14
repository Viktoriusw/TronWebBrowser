from PySide6.QtWidgets import QDockWidget, QVBoxLayout, QWidget, QPlainTextEdit, QLineEdit, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt
import requests

class ChatDock(QDockWidget):
    """Dock widget that provides an AI chat using LM Studio local server."""
    def __init__(self, parent=None, api_url="http://localhost:1234/v1/chat/completions", model="local-model"):
        super().__init__("AI Chat", parent)
        self.api_url = api_url
        self.model = model
        self.messages = []
        self._init_ui()

    def _init_ui(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)
        self.chat_view = QPlainTextEdit()
        self.chat_view.setReadOnly(True)
        layout.addWidget(self.chat_view)

        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.returnPressed.connect(self.send_message)
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)
        layout.addLayout(input_layout)

        self.setWidget(container)
        self.setMinimumWidth(300)
        self.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)

    def send_message(self):
        user_text = self.input_field.text().strip()
        if not user_text:
            return
        self.chat_view.appendPlainText(f"You: {user_text}")
        self.messages.append({"role": "user", "content": user_text})
        self.input_field.clear()

        payload = {"model": self.model, "messages": self.messages}
        try:
            response = requests.post(self.api_url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            assistant_text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        except Exception as exc:
            assistant_text = f"Error: {exc}"
        self.messages.append({"role": "assistant", "content": assistant_text})
        self.chat_view.appendPlainText(f"Assistant: {assistant_text}")

