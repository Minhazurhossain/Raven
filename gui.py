# gui.py (Enhanced)
import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QFileDialog, QMessageBox,
    QRadioButton, QButtonGroup, QDateTimeEdit, QCheckBox, QComboBox,
    QProgressBar, QTabWidget, QListWidget, QGroupBox, QFormLayout
)
from PyQt6.QtCore import Qt, QDateTime, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from utils import load_templates


class SendWorker(QThread):
    """Background thread for sending messages"""
    progress = pyqtSignal(int, int)
    log = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, contact_file, message, media_path, scheduled_time):
        super().__init__()
        self.contact_file = contact_file
        self.message = message
        self.media_path = media_path
        self.scheduled_time = scheduled_time

    def run(self):
        from main import run_sender_yielding
        try:
            for success, total, failed in run_sender_yielding(
                self.contact_file, self.message, self.media_path, self.scheduled_time
            ):
                self.progress.emit(success, total)
                if failed:
                    last = failed[-1]
                    self.log.emit(f"❌ Failed: {last['name']} - {last['phone']}")
            self.log.emit("✅ All messages processed.")
        except Exception as e:
            self.log.emit(f"🚨 Error: {str(e)}")
        finally:
            self.finished.emit()


class WhatsAppGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("💼 Office WhatsApp Sender Pro")
        self.resize(700, 800)
        self.setStyleSheet(self.get_stylesheet())

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        self.setup_send_tab()
        self.setup_logs_tab()
        self.setup_templates_tab()

    def get_stylesheet(self):
        return """
            background-color: #f0f2f5;
            color: #1c1e21;
            font-family: 'Segoe UI';
        """

    def setup_send_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        title = QLabel("🚀 Send Bulk Messages")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Contact File
        layout.addWidget(QLabel("📁 Contact File (CSV/TXT):"))
        file_layout = QHBoxLayout()
        self.file_input = QLineEdit()
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(self.file_input)
        file_layout.addWidget(self.browse_btn)
        layout.addLayout(file_layout)

        # Template
        layout.addWidget(QLabel("📄 Select Template:"))
        self.template_combo = QComboBox()
        self.load_template_list()
        self.template_combo.currentTextChanged.connect(self.load_template_text)
        layout.addWidget(self.template_combo)

        # Message Editor
        layout.addWidget(QLabel("💬 Edit Message:"))
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Hi {name}, here's our offer...")
        layout.addWidget(self.message_input)

        # Media
        layout.addWidget(QLabel("📎 Attach File (Image/PDF):"))
        media_layout = QHBoxLayout()
        self.media_input = QLineEdit()
        self.media_btn = QPushButton("Select")
        self.media_btn.clicked.connect(self.select_media)
        media_layout.addWidget(self.media_input)
        media_layout.addWidget(self.media_btn)
        layout.addLayout(media_layout)

        # Schedule
        self.scheduled_checkbox = QCheckBox("Schedule for later?")
        self.scheduled_checkbox.stateChanged.connect(self.toggle_schedule)
        layout.addWidget(self.scheduled_checkbox)

        self.datetime_input = QDateTimeEdit()
        self.datetime_input.setDateTime(QDateTime.currentDateTime())
        self.datetime_input.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.datetime_input.setEnabled(False)
        layout.addWidget(self.datetime_input)

        # Progress Bar
        layout.addWidget(QLabel("📊 Progress:"))
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Send Button
        self.send_btn = QPushButton("📤 START SENDING")
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #128C7E; color: white; padding: 12px;
                border-radius: 8px; font-size: 14px; font-weight: bold;
            }
            QPushButton:hover { background-color: #0B6B5E; }
        """)
        self.send_btn.clicked.connect(self.start_sending)
        layout.addWidget(self.send_btn)

        tab.setLayout(layout)
        self.tabs.addTab(tab, "📤 Send")

    def setup_logs_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.log_list = QListWidget()
        layout.addWidget(QLabel("📒 Recent Logs"))
        layout.addWidget(self.log_list)

        tab.setLayout(layout)
        self.tabs.addTab(tab, "📋 Logs")

    def setup_templates_tab(self):
        tab = QWidget()
        layout = QFormLayout()

        self.template_name = QLineEdit()
        self.template_content = QTextEdit()
        save_btn = QPushButton("💾 Save Template")
        save_btn.clicked.connect(self.save_template)

        layout.addRow("Template Name:", self.template_name)
        layout.addRow("Content ({name} for personalization):", self.template_content)
        layout.addWidget(save_btn)

        tab.setLayout(layout)
        self.tabs.addTab(tab, "➕ Templates")

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

    def toggle_schedule(self, state):
        self.datetime_input.setEnabled(state == 2)

    def load_template_list(self):
        templates = load_templates()
        self.template_combo.clear()
        self.template_combo.addItem("Custom Message")
        for name in templates:
            self.template_combo.addItem(name)

    def load_template_text(self, name):
        if name == "Custom Message":
            return
        templates = load_templates()
        if name in templates:
            self.message_input.setPlainText(templates[name])

    def save_template(self):
        name = self.template_name.text().strip()
        content = self.template_content.toPlainText().strip()
        if not name or not content:
            QMessageBox.warning(self, "Error", "Name and content required.")
            return
        from config import TEMPLATES_DIR
        path = os.path.join(TEMPLATES_DIR, f"{name}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        self.load_template_list()
        QMessageBox.information(self, "Saved", f"Template '{name}' saved!")
        self.template_name.clear()
        self.template_content.clear()

    def start_sending(self):
        contact_file = self.file_input.text().strip()
        message = self.message_input.toPlainText().strip()
        media_path = self.media_input.text().strip() or None
        scheduled = self.scheduled_checkbox.isChecked()
        scheduled_time = self.datetime_input.dateTime().toString("yyyy-MM-dd HH:mm") if scheduled else None

        if not contact_file or not message:
            QMessageBox.critical(self, "Error", "Please select contact file and message.")
            return

        # Start worker thread
        self.worker = SendWorker(contact_file, message, media_path, scheduled_time)
        self.worker.progress.connect(self.update_progress)
        self.worker.log.connect(self.add_log_entry)
        self.worker.finished.connect(self.sending_finished)
        self.worker.start()

        self.send_btn.setEnabled(False)
        self.log_list.addItem("🔄 Sending started in background...")

    def update_progress(self, success, total):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(success)
        self.statusBar().showMessage(f"Sent: {success}/{total}")

    def add_log_entry(self, text):
        self.log_list.addItem(text)

    def sending_finished(self):
        self.send_btn.setEnabled(True)
        self.statusBar().showMessage("✅ Sending completed.", 5000)
        QMessageBox.information(self, "Done", "Bulk sending completed!")