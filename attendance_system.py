print("Program started")  # At the very top of the file

import sys
import os
import cv2
import numpy as np
import pandas as pd
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QMessageBox, 
                            QInputDialog, QProgressBar, QListWidget)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
from cryptography.fernet import Fernet
import pickle
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

class AttendanceSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Digital Attendance System")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize variables
        self.known_faces = {}  # Dictionary to store face data
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.attendance_file = os.path.join(BASE_DIR, "attendance.xlsx")
        self.face_data_file = os.path.join(BASE_DIR, "face_data.enc")
        self.key_file = os.path.join(BASE_DIR, "encryption.key")
        self.encryption_key = self.load_or_create_key()
        self.fernet = Fernet(self.encryption_key)
        
        # Face capture variables
        self.capture_mode = False
        self.face_samples = []
        self.sample_count = 0
        self.required_samples = 5  # Number of angles to capture
        self.current_capture_name = None
        
        # Load face detection classifier
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Create left panel for camera feed
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Camera feed label
        self.camera_label = QLabel()
        self.camera_label.setMinimumSize(640, 480)
        left_layout.addWidget(self.camera_label)
        
        # Progress bar for face capture
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(self.required_samples)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        left_layout.addWidget(self.progress_bar)
        
        # Create right panel for controls
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Add student button
        self.add_student_button = QPushButton("Add New Student")
        self.add_student_button.clicked.connect(self.start_face_capture)
        right_layout.addWidget(self.add_student_button)
        
        # Remove student button
        self.remove_student_button = QPushButton("Remove Student")
        self.remove_student_button.clicked.connect(self.show_remove_student_dialog)
        right_layout.addWidget(self.remove_student_button)
        
        # View attendance button
        self.view_attendance_button = QPushButton("View Attendance")
        self.view_attendance_button.clicked.connect(self.view_attendance)
        right_layout.addWidget(self.view_attendance_button)
        
        # About button
        self.about_button = QPushButton("About")
        self.about_button.clicked.connect(self.show_about)
        right_layout.addWidget(self.about_button)
        
        # Add panels to main layout
        layout.addWidget(left_panel, 2)
        layout.addWidget(right_panel, 1)
        
        # Initialize camera
        self.camera = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Start camera immediately
        
        # Load existing face data
        self.load_face_data()
        
        # Create attendance file if it doesn't exist
        if not os.path.exists(self.attendance_file):
            df = pd.DataFrame(columns=['Name', 'Date', 'Time'])
            df.to_excel(self.attendance_file, index=False)

    def load_or_create_key(self):
        if os.path.exists(self.key_file):
            with open(self.key_file, "rb") as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, "wb") as f:
                f.write(key)
            return key

    def load_face_data(self):
        if os.path.exists(self.face_data_file):
            try:
                with open(self.face_data_file, "rb") as f:
                    encrypted_data = f.read()
                    decrypted_data = self.fernet.decrypt(encrypted_data)
                    self.known_faces = pickle.loads(decrypted_data)
            except Exception as e:
                print(f"Error loading face data: {e}")
                self.known_faces = {}

    def save_face_data(self):
        try:
            serialized_data = pickle.dumps(self.known_faces)
            encrypted_data = self.fernet.encrypt(serialized_data)
            with open(self.face_data_file, "wb") as f:
                f.write(encrypted_data)
        except Exception as e:
            print(f"Error saving face data: {e}")

    def start_face_capture(self):
        name, ok = QInputDialog.getText(self, 'Add Student', 'Enter student name:')
        if ok and name:
            self.capture_mode = True
            self.face_samples = []
            self.sample_count = 0
            self.current_capture_name = name
            self.progress_bar.setValue(0)
            self.progress_bar.setVisible(True)
            QMessageBox.information(self, "Face Capture", 
                "Please look at the camera and slowly turn your head to capture different angles.\n"
                "Keep your face within the green rectangle.")

    def update_frame(self):
        ret, frame = self.camera.read()
        if not ret:
            return
        color_frame = frame.copy()  # Keep the color frame for display
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        if self.capture_mode:
            if len(faces) > 0:
                x, y, w, h = faces[0]
                face_roi = gray[y:y+h, x:x+w]
                cv2.rectangle(color_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(color_frame, f"Capturing sample {self.sample_count + 1}/{self.required_samples}",
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                if self.sample_count < self.required_samples:
                    self.face_samples.append(face_roi)
                    self.sample_count += 1
                    self.progress_bar.setValue(self.sample_count)
                    if self.sample_count == self.required_samples:
                        self.known_faces[self.current_capture_name] = self.face_samples.copy()
                        self.save_face_data()
                        self.capture_mode = False
                        self.progress_bar.setVisible(False)
                        QMessageBox.information(self, "Success",
                            f"Student {self.current_capture_name} added successfully with {self.required_samples} face samples!")
        else:
            for (x, y, w, h) in faces:
                face_roi = gray[y:y+h, x:x+w]
                name = "Unknown"
                for known_name, known_faces in self.known_faces.items():
                    for known_face in known_faces:
                        try:
                            result = cv2.matchTemplate(face_roi, known_face, cv2.TM_CCOEFF_NORMED)
                            if cv2.minMaxLoc(result)[1] > 0.8:
                                name = known_name
                                self.mark_attendance(name)
                                break
                        except Exception as e:
                            continue
                    if name != "Unknown":
                        break
                cv2.rectangle(color_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(color_frame, name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
        # Convert BGR to RGB for display
        rgb_frame = cv2.cvtColor(color_frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.camera_label.setPixmap(QPixmap.fromImage(qt_image))

    def mark_attendance(self, name):
        if name != "Unknown":
            df = pd.read_excel(self.attendance_file)
            current_time = datetime.now()
            today = current_time.strftime("%Y-%m-%d")
            if not ((df['Name'] == name) & (df['Date'] == today)).any():
                new_row = {
                    'Name': name,
                    'Date': today,
                    'Time': current_time.strftime("%H:%M:%S")
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                df.to_excel(self.attendance_file, index=False)

    def view_attendance(self):
        if os.path.exists(self.attendance_file):
            df = pd.read_excel(self.attendance_file)
            QMessageBox.information(self, "Attendance Records", df.to_string())
        else:
            QMessageBox.warning(self, "Error", "No attendance records found!")

    def show_about(self):
        about_text = (
            "Digital Attendance System\n"
            "Developed by: Tariqul Islam\n"
            "Department: CSE\n"
            "Batch: 37\n"
            "GB"
        )
        QMessageBox.about(self, "About", about_text)

    def show_remove_student_dialog(self):
        if not self.known_faces:
            QMessageBox.warning(self, "Warning", "No students registered in the system!")
            return

        # Create a dialog window
        dialog = QWidget(self, Qt.Window)
        dialog.setWindowTitle("Remove Student")
        dialog.setGeometry(200, 200, 300, 400)
        
        # Create layout
        layout = QVBoxLayout(dialog)
        
        # Add label
        label = QLabel("Select student to remove:")
        layout.addWidget(label)
        
        # Create list widget
        list_widget = QListWidget()
        list_widget.addItems(self.known_faces.keys())
        layout.addWidget(list_widget)
        
        # Add buttons
        button_layout = QHBoxLayout()
        
        remove_button = QPushButton("Remove")
        remove_button.clicked.connect(lambda: self.remove_student(list_widget.currentItem().text() if list_widget.currentItem() else None, dialog))
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.close)
        
        button_layout.addWidget(remove_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        dialog.show()

    def remove_student(self, name, dialog=None):
        if name is None:
            QMessageBox.warning(self, "Warning", "Please select a student to remove!")
            return
            
        reply = QMessageBox.question(self, 'Confirm Removal',
                                   f'Are you sure you want to remove {name}?',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Remove from known faces
            if name in self.known_faces:
                del self.known_faces[name]
                self.save_face_data()
                
                # Remove from attendance records
                if os.path.exists(self.attendance_file):
                    df = pd.read_excel(self.attendance_file)
                    df = df[df['Name'] != name]
                    df.to_excel(self.attendance_file, index=False)
                
                QMessageBox.information(self, "Success", f"Student {name} has been removed successfully!")
                if dialog:
                    dialog.close()
            else:
                QMessageBox.warning(self, "Error", f"Student {name} not found in the system!")

    def closeEvent(self, event):
        if self.camera is not None:
            self.camera.release()
        event.accept()

if __name__ == '__main__':
    print("Launching GUI...")
    try:
        app = QApplication(sys.argv)
        window = AttendanceSystem()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print("Error occurred:", e)
    print("Program ended")  # This will never print unless the GUI closes 