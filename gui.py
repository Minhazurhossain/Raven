# gui.py (Simplified - No Scheduling)
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QFileDialog, QMessageBox,
    QComboBox, QProgressBar, QListWidget, QTabWidget, QGroupBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from utils import load_templates


class SendWorker(QThread):
    """Background thread for sending"""
    log = pyqtSignal(str)
    progress = pyqtSignal(int, int)
    finished = pyqtSignal()

    def __init__(self, contact_file, message, media_path):
        super().__init__()
        self.contact_file = contact_file
        self.message = message
        self.media_path = media_path

    def run(self):
        from main import run_sender_yielding
        try:
            for sent, total, failed in run_sender_yielding(self.contact_file, self.message, self.media_path):
                self.progress.emit(sent, total)
                if failed:
                    last = failed[-1]
                    self.log.emit(f"❌ Failed: {last['name']} - {last['phone']}")
            self.log.emit("✅ All messages sent!")
        except Exception as e:
            self.log.emit(f"🚨 Error: {str(e)}")
        finally:
            self.finished.emit()


class WhatsAppGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("💼 WhatsApp Bulk Sender (Simple)")
        self.resize(600, 700)
        self.setStyleSheet("background:#f0f2f5; font-family:Segoe UI;")

        self.central = QWidget()
        self.setCentralWidget(self.central)
        layout = QVBoxLayout(self.central)
        layout.setSpacing(15)

        # Title
        title = QLabel("📲 Send Bulk WhatsApp Messages")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color:#128C7E; margin:10px;")
        layout.addWidget(title)

        # Contact File
        layout.addWidget(QLabel("📁 Contacts (CSV or TXT):"))
        file_layout = QHBoxLayout()
        self.file_input = QLineEdit()
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(self.file_input)
        file_layout.addWidget(self.browse_btn)
        layout.addLayout(file_layout)

        # Template
        layout.addWidget(QLabel("📄 Select Message:"))
        self.template_combo = QComboBox()
        self.template_combo.addItem("Custom Message")
        self.load_templates()
        self.template_combo.currentTextChanged.connect(self.load_template)
        layout.addWidget(self.template_combo)

        # Message Editor
        layout.addWidget(QLabel("💬 Edit Message ({name} = person's name):"))
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Hi {name}, this is a test.")
        layout.addWidget(self.message_input)

        # Media
        layout.addWidget(QLabel("📎 Attach Image/PDF (Optional):"))
        media_layout = QHBoxLayout()
        self.media_input = QLineEdit()
        self.media_btn = QPushButton("Select File")
        self.media_btn.clicked.connect(self.select_media)
        media_layout.addWidget(self.media_input)
        media_layout.addWidget(self.media_btn)
        layout.addLayout(media_layout)

        # Progress
        layout.addWidget(QLabel("📊 Progress:"))
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Logs
        layout.addWidget(QLabel("📋 Status Log:"))
        self.log_list = QListWidget()
        layout.addWidget(self.log_list)

        # Send Button
        self.send_btn = QPushButton("🚀 START SENDING")
        self.send_btn.clicked.connect(self.start_sending) 
        self.send_btn.setStyleSheet("""
            QPushButton {
                background:#128C7E; color:white; padding:12px; border-radius:8px;
                font:bold;
            }
            QPushButton:hover { background:#0B6B5E; }
        """)
        self.send_btn.clicked.connect(self.start_sending)
        layout.addWidget(self.send_btn)

    def browse_file(self):
        file, _ = QFileDialog.getOpenFileName(
            self, "Select Contacts", "", "CSV Files (*.csv);;Text Files (*.txt)"
        )
        if file:
            self.file_input.setText(file)

    def select_media(self):
        file, _ = QFileDialog.getOpenFileName(self, "Attach File", "", "All Files (*)")
        if file:
            self.media_input.setText(file)

    def load_templates(self):
        templates = load_templates()
        for name in templates:
            self.template_combo.addItem(name)

    def load_template(self, name):
        if name == "Custom Message":
            return
        templates = load_templates()
        if name in templates:
            self.message_input.setPlainText(templates[name])

    def start_sending(self):
        print("🔥 [DEBUG] Button clicked! start_sending() called")  # 🔴 MUST SEE THIS

        contact_file = self.file_input.text().strip()
        print(f"📁 [DEBUG] Contact file: {contact_file}")

        message = self.message_input.toPlainText().strip()
        print(f"💬 [DEBUG] Message: {message}")

        media_path = self.media_input.text().strip() or None
        print(f"📎 [DEBUG] Media: {media_path}")

        if not contact_file or not message:
            print("❌ [DEBUG] Validation failed")  # 🔴
            QMessageBox.critical(self, "Error", "Please select contact file and message.")
            return

        self.send_btn.setEnabled(False)
        self.add_log("🔄 Sending messages...")

        try:
            print("🚀 [DEBUG] Importing run_sender_yielding...")  # 🔴
            from main import run_sender_yielding
            print("✅ [DEBUG] Successfully imported!")  # 🔴

            gen = run_sender_yielding(contact_file, message, media_path)
            print("✅ [DEBUG] Generator created, starting loop...")

            for sent, total, failed in gen:
                print(f"📊 [DEBUG] Progress: {sent}/{total}")
                self.progress_bar.setMaximum(total)
                self.progress_bar.setValue(sent)
                self.statusBar().showMessage(f"Sent: {sent}/{total}")
                if failed:
                    last = failed[-1]
                    self.add_log(f"❌ Failed: {last['name']}")
            self.add_log("✅ All messages sent!")
        except Exception as e:
            self.add_log(f"🚨 Error: {str(e)}")
            import traceback
            traceback.print_exc()  # This will show hidden errors
        finally:
            self.send_btn.setEnabled(True) 
    
    def add_log(self, text):
        self.log_list.addItem(text)
        