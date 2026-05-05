import sys
import os
import subprocess
import threading
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                             QComboBox, QProgressBar, QFrame, QCheckBox, QTextEdit, QTextBrowser, QSplitter)
from PyQt6.QtCore import Qt, pyqtSignal, QUrl, QTimer
from PyQt6.QtGui import QPixmap, QDesktopServices, QColor

class NeonOCRApp(QMainWindow):
    processing_finished = pyqtSignal(bool)
    log_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Antigravity AI - Agentic Digitizer")
        self.setFixedSize(1250, 800)
        self.setStyleSheet("""
            QMainWindow { background-color: #0F172A; }
            QFrame#MainCard { background-color: #1E293B; border-radius: 20px; border: 1px solid #334155; }
            QFrame#SettingsBox { background-color: #0F172A; border-radius: 12px; padding: 15px; border: 1px solid #334155; }
            QLabel { color: #F8FAFC; }
            QLabel#Title { color: #00F2FF; font-size: 32px; font-weight: 900; letter-spacing: -1px; }
            QLabel#SubTitle { color: #94A3B8; font-size: 14px; }
            QLabel#SectionTitle { color: #00F2FF; font-size: 16px; font-weight: bold; margin-bottom: 5px; }
            QLabel#PreviewPlaceholder { border: 2px dashed #334155; border-radius: 12px; background-color: #0F172A; color: #475569; font-weight: bold; }
            QPushButton#PrimaryBtn { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #00F2FF, stop:1 #FF00E5); color: #FFFFFF; border: none; border-radius: 14px; padding: 15px; font-weight: 800; font-size: 16px; }
            QPushButton#PrimaryBtn:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #00E4F0, stop:1 #E000CA); }
            QPushButton#FolderBtn { background-color: #334155; color: #00F2FF; border: 1px solid #00F2FF; border-radius: 10px; padding: 8px; font-weight: bold; }
            QPushButton#SecondaryBtn { background-color: #334155; color: #F8FAFC; border: 1px solid #475569; border-radius: 10px; padding: 10px; font-weight: bold; }
            QComboBox { border: 1px solid #334155; border-radius: 8px; padding: 8px; background-color: #1E293B; color: #00F2FF; font-weight: bold; }
            QComboBox QAbstractItemView { background-color: #1E293B; color: #00F2FF; selection-background-color: #334155; }
            QProgressBar { border: none; background-color: #0F172A; height: 10px; border-radius: 5px; }
            QProgressBar::chunk { background-color: #FF00E5; border-radius: 5px; }
            QCheckBox { color: #00F2FF; font-weight: bold; font-size: 14px; }
            QCheckBox::indicator { width: 20px; height: 20px; border-radius: 4px; border: 2px solid #334155; background-color: #1E293B; }
            QCheckBox::indicator:checked { background-color: #FF00E5; border: 2px solid #FF00E5; }
            QTextEdit, QTextBrowser { background-color: #0B1120; color: #E2E8F0; border-radius: 10px; border: 1px solid #334155; padding: 15px; font-size: 14px; }
            QTextEdit#LogConsole { color: #00FF41; font-family: Consolas, monospace; font-size: 12px; }
        """)

        self.processing_finished.connect(self.on_processing_finished)
        self.log_signal.connect(self.append_log)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        self.card = QFrame()
        self.card.setObjectName("MainCard")
        self.card_layout = QVBoxLayout(self.card)
        self.card_layout.setContentsMargins(30, 30, 30, 30)
        self.card_layout.setSpacing(15)

        # --- Header ---
        top_row = QHBoxLayout()
        header_vbox = QVBoxLayout()
        self.title = QLabel("NEON AGENTIC DIGITIZER")
        self.title.setObjectName("Title")
        self.subtitle = QLabel("Phase 2: Autonomous Multi-Agent VLM Extraction System")
        self.subtitle.setObjectName("SubTitle")
        header_vbox.addWidget(self.title)
        header_vbox.addWidget(self.subtitle)
        top_row.addLayout(header_vbox)
        
        self.open_folder_btn = QPushButton("📂 Output Folder")
        self.open_folder_btn.setObjectName("FolderBtn")
        self.open_folder_btn.setFixedWidth(130)
        self.open_folder_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.open_folder_btn.clicked.connect(self.open_output_folder)
        top_row.addWidget(self.open_folder_btn, alignment=Qt.AlignmentFlag.AlignTop)
        
        self.card_layout.addLayout(top_row)

        # --- Body ---
        body_layout = QHBoxLayout()
        body_layout.setSpacing(25)

        # LEFT COLUMN (Input & Agents)
        left_col = QVBoxLayout()
        left_col.setSpacing(15)
        
        self.preview_label = QLabel("⚡ DROP IMAGE HERE")
        self.preview_label.setObjectName("PreviewPlaceholder")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setFixedSize(500, 300)
        left_col.addWidget(self.preview_label)
        
        # Settings Bar
        settings_bar = QFrame()
        settings_bar.setObjectName("SettingsBox")
        settings_bar.setFixedHeight(80)
        settings_hbox = QHBoxLayout(settings_bar)
        
        self.browse_btn = QPushButton("BROWSE IMAGE")
        self.browse_btn.setObjectName("SecondaryBtn")
        self.browse_btn.clicked.connect(self.open_file_dialog)
        settings_hbox.addWidget(self.browse_btn)
        
        self.engine_combo = QComboBox()
        self.engine_combo.addItems(["Handwritten (Paddle)", "Printed (Tess)"])
        settings_hbox.addWidget(self.engine_combo)
        
        self.ai_checkbox = QCheckBox("Phase 2: MAS Workflow")
        self.ai_checkbox.setChecked(True)
        settings_hbox.addWidget(self.ai_checkbox)
        
        left_col.addWidget(settings_bar)
        
        # Agent Logs
        log_label = QLabel("🤖 Live Agent Workspace & Logs")
        log_label.setObjectName("SectionTitle")
        left_col.addWidget(log_label)
        
        self.log_console = QTextEdit()
        self.log_console.setObjectName("LogConsole")
        self.log_console.setReadOnly(True)
        self.log_console.setPlaceholderText("Agent thoughts and remarks will appear here in real-time...")
        left_col.addWidget(self.log_console)
        
        body_layout.addLayout(left_col, stretch=1)

        # RIGHT COLUMN (Output Text)
        right_col = QVBoxLayout()
        right_col.setSpacing(15)
        
        result_label = QLabel("📄 Extracted Document Output")
        result_label.setObjectName("SectionTitle")
        right_col.addWidget(result_label)
        
        self.result_browser = QTextBrowser()
        self.result_browser.setPlaceholderText("The perfectly formatted text will be previewed here instantly after the Formatter Agent completes its job.")
        self.result_browser.setStyleSheet("background-color: #0F172A; border: 1px solid #334155; font-size: 15px;")
        right_col.addWidget(self.result_browser)
        
        body_layout.addLayout(right_col, stretch=1)

        self.card_layout.addLayout(body_layout)

        # --- Footer ---
        footer_vbox = QVBoxLayout()
        self.progress = QProgressBar()
        self.progress.hide()
        footer_vbox.addWidget(self.progress)

        self.convert_btn = QPushButton("⚡ INITIALIZE AUTONOMOUS AGENTS ⚡")
        self.convert_btn.setObjectName("PrimaryBtn")
        self.convert_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.convert_btn.clicked.connect(self.start_processing)
        footer_vbox.addWidget(self.convert_btn)

        self.status_label = QLabel("SYSTEM IDLE")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #475569; font-weight: bold;")
        footer_vbox.addWidget(self.status_label)
        
        self.card_layout.addLayout(footer_vbox)
        self.main_layout.addWidget(self.card)

        # State var for parsing final output
        self.capturing_output = False
        self.final_text_buffer = []

    def open_output_folder(self):
        path = os.path.abspath(".")
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def open_file_dialog(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg)")
        if file:
            self.file_path = file
            self.status_label.setText(f"READY: {os.path.basename(file)}")
            pixmap = QPixmap(file)
            self.preview_label.setPixmap(pixmap.scaled(self.preview_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            self.preview_label.setStyleSheet("border: 2px solid #00F2FF; border-radius: 12px;")

    def start_processing(self):
        if not hasattr(self, 'file_path') or not os.path.exists(self.file_path):
            self.status_label.setText("⚠️ ERROR: NO FILE LOADED")
            return
        self.convert_btn.setEnabled(False)
        self.progress.show()
        self.progress.setRange(0, 0)
        self.log_console.clear()
        self.result_browser.clear()
        self.capturing_output = False
        self.final_text_buffer = []
        self.status_label.setText("AGENTS ARE THINKING...")
        threading.Thread(target=self.run_ocr_and_finish, daemon=True).start()

    def append_log(self, text):
        if "=== FINAL_OUTPUT_START ===" in text:
            self.capturing_output = True
            self.final_text_buffer = []
            return
        elif "=== FINAL_OUTPUT_END ===" in text:
            self.capturing_output = False
            final_text = "\n".join(self.final_text_buffer)
            if not final_text.strip():
                final_text = "[ERROR] AI generated no text or buffer was empty."
            self.result_browser.setPlainText(final_text)
            return
            
        if self.capturing_output:
            self.final_text_buffer.append(text)
        else:
            self.log_console.append(text)
            scrollbar = self.log_console.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

    def run_ocr_and_finish(self):
        engine = "handwritten" if "Handwritten" in self.engine_combo.currentText() else "printed"
        try:
            if self.ai_checkbox.isChecked():
                cmd = ["python", "-u", "agentic_pipeline.py", self.file_path]
            else:
                cmd = ["python", "-u", "ocr_pipeline.py", self.file_path, "--type", engine, "--lang", "en"]
                
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0, encoding='utf-8', errors='replace')
            
            for line in iter(process.stdout.readline, ''):
                if line:
                    self.log_signal.emit(line.strip())
            
            process.stdout.close()
            process.wait()
            self.processing_finished.emit(process.returncode == 0)
        except Exception as e:
            self.log_signal.emit(f"ERROR: {str(e)}")
            self.processing_finished.emit(False)

    def on_processing_finished(self, success):
        self.progress.hide()
        self.convert_btn.setEnabled(True)
        if success:
            self.status_label.setText("✅ SUCCESS: AGENT WORKFLOW COMPLETE & SAVED TO DOCX")
            self.status_label.setStyleSheet("color: #00F2FF; font-weight: bold;")
        else:
            self.status_label.setText("❌ SYSTEM FAILURE OR AGENT ERROR")
            self.status_label.setStyleSheet("color: #FF00E5; font-weight: bold;")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NeonOCRApp()
    window.show()
    sys.exit(app.exec())
