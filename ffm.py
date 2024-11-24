# version 0.1
import os
import sys
import unicodedata
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView, QLabel, QMessageBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class FileConversionThread(QThread):
    update_signal = pyqtSignal(int, str)
    
    def __init__(self, files):
        super().__init__()
        self.files = files
    
    def run(self):
        for i, file in enumerate(self.files):
            old_path, new_name = file
            try:
                new_path = os.path.join(os.path.dirname(old_path), new_name)
                base, ext = os.path.splitext(new_path)
                counter = 1
                while os.path.exists(new_path):
                    new_path = f"{base}_{counter}{ext}"
                    counter += 1
                os.rename(old_path, new_path)
                self.update_signal.emit(i, "Conversion Complete")
            except Exception as e:
                self.update_signal.emit(i, f"Error: {str(e)}")

class FFMApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FFM v0.1")
        self.setGeometry(100, 100, 800, 600)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        self.folder_layout = QHBoxLayout()
        self.folder_label = QLabel("Selected Folder:")
        self.folder_path = QLabel()
        self.select_folder_btn = QPushButton("Select Folder")
        self.select_folder_btn.clicked.connect(self.select_folder)
        self.folder_layout.addWidget(self.folder_label)
        self.folder_layout.addWidget(self.folder_path)
        self.folder_layout.addWidget(self.select_folder_btn)
        
        self.search_btn = QPushButton("Search Separated Files")
        self.search_btn.clicked.connect(self.search_files)
        
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Full Path", "Converted Filename", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        self.convert_btn = QPushButton("Start File Conversion")
        self.convert_btn.clicked.connect(self.start_conversion)
        
        self.layout.addLayout(self.folder_layout)
        self.layout.addWidget(self.search_btn)
        self.layout.addWidget(self.table)
        self.layout.addWidget(self.convert_btn)
        
        self.menuBar().addAction("About", self.show_about)
        
        self.files_to_convert = []
    
    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.folder_path.setText(folder)
    
    def is_separated(self, filename):
        return filename != unicodedata.normalize('NFC', filename)
    
    def search_files(self):
        folder = self.folder_path.text()
        if not folder:
            QMessageBox.warning(self, "Warning", "Please select a folder first.")
            return
        
        self.files_to_convert = []
        self.table.setRowCount(0)
        
        for root, _, files in os.walk(folder):
            for file in files:
                if self.is_separated(file):
                    full_path = os.path.join(root, file)
                    converted_name = unicodedata.normalize('NFC', file)
                    self.files_to_convert.append((full_path, converted_name))
                    row = self.table.rowCount()
                    self.table.insertRow(row)
                    self.table.setItem(row, 0, QTableWidgetItem(full_path))
                    self.table.setItem(row, 1, QTableWidgetItem(converted_name))
                    self.table.setItem(row, 2, QTableWidgetItem("Pending"))
    
    def start_conversion(self):
        if not self.files_to_convert:
            QMessageBox.warning(self, "Warning", "No files to convert.")
            return
        
        self.convert_thread = FileConversionThread(self.files_to_convert)
        self.convert_thread.update_signal.connect(self.update_status)
        self.convert_thread.start()
    
    def update_status(self, row, status):
        self.table.setItem(row, 2, QTableWidgetItem(status))
    
    def show_about(self):
        about_text = "FFM은 한글 자음과 모음이 분리된 파일 이름을 변환해주는 프로그램입니다.\n지정된 폴더의 모든 파일을 검사하여 정규화된 이름으로 변경합니다. \n\n - Created by: OVRock(locustk@gmail.com)\n - Blog: http://make1solved.tistory.com"
        QMessageBox.about(self, "About FFM", about_text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FFMApp()
    window.show()
    sys.exit(app.exec_())