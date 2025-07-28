print("Program started")  # At the very top of the file

import sys
import os
import cv2
import numpy as np
import pandas as pd
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QMessageBox, 
                            QInputDialog, QProgressBar, QListWidget, QCheckBox,
                            QFrame, QGroupBox, QSplitter, QComboBox, QStyleFactory,
                            QStatusBar, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import QTimer, Qt, QSize
from PyQt5.QtGui import QImage, QPixmap, QFont, QIcon, QColor, QPalette
from cryptography.fernet import Fernet
import pickle
import warnings
import time

warnings.filterwarnings("ignore", category=DeprecationWarning)

class AttendanceSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Digital Attendance System")
        self.setGeometry(100, 100, 1200, 800)
        
        # Set application style
        QApplication.setStyle(QStyleFactory.create('Fusion'))
        
        # Set color palette
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        QApplication.setPalette(palette)
        
        # Initialize variables
        self.known_faces = {}  # Dictionary to store face data
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.attendance_file = os.path.join(BASE_DIR, "attendance.xlsx")
        self.face_data_file = os.path.join(BASE_DIR, "face_data.enc")
        self.key_file = os.path.join(BASE_DIR, "encryption.key")
        self.encryption_key = self.load_or_create_key()
        self.fernet = Fernet(self.encryption_key)
        
        # Smart learning variables
        self.smart_learning_enabled = True
        self.learning_threshold = 0.9  # Higher threshold to trigger more learning
        self.recognition_threshold = 0.65  # Lower threshold for better recognition
        self.max_samples_per_person = float('inf')  # Unlimited face samples per person
        self.last_learning_time = {}  # To prevent too frequent updates for the same person
        
        # Enhanced face recognition variables
        self.min_recognition_matches = 2  # Minimum number of face samples that must match for recognition
        self.match_confidence_threshold = 0.60  # Minimum confidence for a single face match
        
        # Attendance confirmation variables
        self.pending_attendance = None  # Person waiting for attendance confirmation
        self.confirmation_start_time = None  # When confirmation countdown started
        self.confirmation_duration = 0  # No waiting time for attendance confirmation
        
        # Face capture variables
        self.capture_mode = False
        self.face_samples = []
        self.sample_count = 0
        self.required_samples = 8  # Increased number of angles to capture
        self.current_capture_name = None
        
        # Background analysis flag
        self.process_background = False  # Flag to control background analysis
        
        # Load face detection classifier
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # Create a splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        
        # Create left panel for camera feed with a frame
        left_panel = QFrame()
        left_panel.setFrameShape(QFrame.StyledPanel)
        left_panel.setFrameShadow(QFrame.Raised)
        left_layout = QVBoxLayout(left_panel)
        
        # Camera feed title
        camera_title = QLabel("Camera Feed")
        camera_title.setAlignment(Qt.AlignCenter)
        camera_title.setFont(QFont("Arial", 14, QFont.Bold))
        left_layout.addWidget(camera_title)
        
        # Camera feed label with frame
        camera_frame = QFrame()
        camera_frame.setFrameShape(QFrame.StyledPanel)
        camera_frame.setFrameShadow(QFrame.Sunken)
        camera_frame.setStyleSheet("background-color: #1e1e1e; border: 2px solid #3498db; border-radius: 5px;")
        camera_layout = QVBoxLayout(camera_frame)
        
        self.camera_label = QLabel()
        self.camera_label.setMinimumSize(640, 480)
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setStyleSheet("border: none;")
        camera_layout.addWidget(self.camera_label)
        
        left_layout.addWidget(camera_frame)
        
        # Status display
        self.status_label = QLabel("System Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #2ecc71; font-weight: bold; font-size: 14px; padding: 5px;")
        left_layout.addWidget(self.status_label)
        
        # Progress bar for face capture
        progress_frame = QFrame()
        progress_layout = QVBoxLayout(progress_frame)
        
        progress_title = QLabel("Capture Progress:")
        progress_title.setAlignment(Qt.AlignLeft)
        progress_layout.addWidget(progress_title)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(self.required_samples)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #2980b9;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                width: 10px;
                margin: 0.5px;
            }
        """)
        progress_layout.addWidget(self.progress_bar)
        
        left_layout.addWidget(progress_frame)
        
        # Create right panel for controls
        right_panel = QFrame()
        right_panel.setFrameShape(QFrame.StyledPanel)
        right_panel.setFrameShadow(QFrame.Raised)
        right_layout = QVBoxLayout(right_panel)
        
        # Control panel title
        control_title = QLabel("Control Panel")
        control_title.setAlignment(Qt.AlignCenter)
        control_title.setFont(QFont("Arial", 14, QFont.Bold))
        right_layout.addWidget(control_title)
        
        # Student Management Group
        student_group = QGroupBox("Student Management")
        student_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #3498db;
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
                color: #3498db;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        student_layout = QVBoxLayout(student_group)
        
        # Add student button
        self.add_student_button = QPushButton("Add New Student")
        self.add_student_button.setIcon(QIcon.fromTheme("list-add"))
        self.add_student_button.setMinimumHeight(40)
        self.add_student_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        self.add_student_button.clicked.connect(self.start_face_capture)
        student_layout.addWidget(self.add_student_button)
        
        # Remove student button
        self.remove_student_button = QPushButton("Remove Student")
        self.remove_student_button.setIcon(QIcon.fromTheme("list-remove"))
        self.remove_student_button.setMinimumHeight(40)
        self.remove_student_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        self.remove_student_button.clicked.connect(self.show_remove_student_dialog)
        student_layout.addWidget(self.remove_student_button)
        
        right_layout.addWidget(student_group)
        
        # Attendance Group
        attendance_group = QGroupBox("Attendance")
        attendance_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #3498db;
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
                color: #3498db;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        attendance_layout = QVBoxLayout(attendance_group)
        
        # View attendance button
        self.view_attendance_button = QPushButton("View Attendance")
        self.view_attendance_button.setIcon(QIcon.fromTheme("document-open"))
        self.view_attendance_button.setMinimumHeight(40)
        self.view_attendance_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1f618d;
            }
        """)
        self.view_attendance_button.clicked.connect(self.view_attendance)
        attendance_layout.addWidget(self.view_attendance_button)
        
        right_layout.addWidget(attendance_group)
        
        # Settings Group
        settings_group = QGroupBox("Settings")
        settings_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #3498db;
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
                color: #3498db;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        settings_layout = QVBoxLayout(settings_group)
        
        # Smart Learning toggle
        self.smart_learning_checkbox = QCheckBox("Enable Smart Learning")
        self.smart_learning_checkbox.setChecked(self.smart_learning_enabled)
        self.smart_learning_checkbox.setStyleSheet("""
            QCheckBox {
                spacing: 5px;
                font-weight: bold;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #e74c3c;
                background-color: #2c3e50;
                border-radius: 4px;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #2ecc71;
                background-color: #2ecc71;
                border-radius: 4px;
            }
        """)
        self.smart_learning_checkbox.stateChanged.connect(self.toggle_smart_learning)
        settings_layout.addWidget(self.smart_learning_checkbox)
        
        # About button
        self.about_button = QPushButton("About")
        self.about_button.setIcon(QIcon.fromTheme("help-about"))
        self.about_button.setMinimumHeight(40)
        self.about_button.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
            QPushButton:pressed {
                background-color: #6c3483;
            }
        """)
        self.about_button.clicked.connect(self.show_about)
        settings_layout.addWidget(self.about_button)
        
        right_layout.addWidget(settings_group)
        
        # Add stretch to push everything to the top
        right_layout.addStretch()
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([700, 500])
        
        # Add splitter to main layout
        main_layout.addWidget(splitter)
        
        # Create status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("System Ready | Smart Learning: Enabled")
        self.statusBar.setStyleSheet("background-color: #2c3e50; color: white;")
        
        # Set window stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #34495e;
            }
            QWidget {
                background-color: #34495e;
                color: white;
            }
            QLabel {
                color: white;
            }
        """)
        
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
            
            # Update progress bar maximum to match required samples
            self.progress_bar.setMaximum(self.required_samples)
            
            QMessageBox.information(self, "Face Capture", 
                f"Please look at the camera and capture {self.required_samples} different angles of your face:\n\n"
                "1. Look directly at the camera (front view)\n"
                "2. Slightly turn your head to the left\n"
                "3. Slightly turn your head to the right\n"
                "4. Slightly tilt your head up\n"
                "5. Slightly tilt your head down\n"
                "6. Slightly tilt your head up and to the left\n"
                "7. Slightly tilt your head up and to the right\n"
                "8. Normal expression with different lighting if possible\n\n"
                "Keep your face within the green rectangle for each capture.")

    def update_frame(self):
        ret, frame = self.camera.read()
        if not ret:
            return
        color_frame = frame.copy()  # Keep the color frame for display
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Prioritize face detection before any background analysis
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        # Draw a border around the camera feed
        cv2.rectangle(color_frame, (0, 0), (color_frame.shape[1]-1, color_frame.shape[0]-1), (52, 152, 219), 2)
        
        # Add a title bar to the camera feed
        title_bar_height = 30
        title_bar = np.zeros((title_bar_height, color_frame.shape[1], 3), dtype=np.uint8)
        title_bar[:] = (41, 128, 185)  # Blue color
        
        # Only process background if flag is set and we're not in capture mode
        self.process_background = len(faces) > 0 and not self.capture_mode
        
        if self.capture_mode:
            cv2.putText(title_bar, "CAPTURE MODE", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            self.status_label.setText(f"Capturing: {self.sample_count}/{self.required_samples} samples")
            self.status_label.setStyleSheet("color: #f39c12; font-weight: bold; font-size: 14px; padding: 5px;")
            self.statusBar.showMessage(f"Capturing face samples for {self.current_capture_name} | {self.sample_count}/{self.required_samples}")
            
            if len(faces) > 0:
                x, y, w, h = faces[0]
                face_roi = gray[y:y+h, x:x+w]
                
                # Draw a more attractive rectangle with rounded corners effect
                cv2.rectangle(color_frame, (x-2, y-2), (x+w+2, y+h+2), (41, 128, 185), 3)  # Outer blue rectangle
                cv2.rectangle(color_frame, (x, y), (x+w, y+h), (46, 204, 113), 2)  # Inner green rectangle
                
                # Add a label above the face
                label_bg = np.zeros((30, w+10, 3), dtype=np.uint8)
                label_bg[:] = (46, 204, 113)  # Green background
                cv2.putText(label_bg, f"Sample {self.sample_count + 1}/{self.required_samples}", (5, 20), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Overlay the label on the frame
                if y > 40:
                    color_frame[y-30:y, x-5:x+w+5] = label_bg
                
                if self.sample_count < self.required_samples:
                    self.face_samples.append(face_roi)
                    self.sample_count += 1
                    self.progress_bar.setValue(self.sample_count)
                    if self.sample_count == self.required_samples:
                        self.known_faces[self.current_capture_name] = self.face_samples.copy()
                        self.save_face_data()
                        self.capture_mode = False
                        self.progress_bar.setVisible(False)
                        self.status_label.setText("Student added successfully")
                        self.status_label.setStyleSheet("color: #2ecc71; font-weight: bold; font-size: 14px; padding: 5px;")
                        self.statusBar.showMessage("System Ready | Smart Learning: Enabled")
                        QMessageBox.information(self, "Success",
                            f"Student {self.current_capture_name} added successfully with {self.required_samples} face samples!")
        else:
            cv2.putText(title_bar, "RECOGNITION MODE", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Add timestamp to the frame
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(color_frame, current_time, (color_frame.shape[1]-200, color_frame.shape[0]-20), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            # Reset pending attendance if no faces are detected
            if len(faces) == 0 and self.pending_attendance is not None:
                current_time = time.time()
                # Only reset if it's been at least 1 second since confirmation started
                # This prevents flickering when face detection temporarily fails
                if self.confirmation_start_time is not None and (current_time - self.confirmation_start_time) > 1.0:
                    self.pending_attendance = None
                    self.confirmation_start_time = None
                    self.status_label.setText("No face detected - confirmation reset")
                    self.status_label.setStyleSheet("color: #e74c3c; font-weight: bold; font-size: 14px; padding: 5px;")
                    self.statusBar.showMessage("Attendance confirmation reset - person disappeared from frame")
            
            for (x, y, w, h) in faces:
                face_roi = gray[y:y+h, x:x+w]
                name = "Unknown"
                best_score = 0
                best_name = "Unknown"
                
                # Enhanced recognition using multiple face data points
                match_counts = {}  # Count how many samples match for each person
                match_scores = {}  # Track the average score for each person
                
                for known_name, known_faces in self.known_faces.items():
                    match_counts[known_name] = 0
                    match_scores[known_name] = 0
                    match_score_sum = 0
                    match_count = 0
                    
                    for known_face in known_faces:
                        try:
                            result = cv2.matchTemplate(face_roi, known_face, cv2.TM_CCOEFF_NORMED)
                            score = cv2.minMaxLoc(result)[1]
                            
                            # Count matches above the match confidence threshold
                            if score > self.match_confidence_threshold:
                                match_counts[known_name] += 1
                                match_score_sum += score
                                match_count += 1
                                
                            # Still track the best overall score for display
                            if score > best_score:
                                best_score = score
                                best_name = known_name
                        except Exception as e:
                            continue
                    
                    # Calculate average score for this person if there were matches
                    if match_count > 0:
                        match_scores[known_name] = match_score_sum / match_count
                
                # Find the person with the most matches above threshold
                most_matches = 0
                most_matches_name = "Unknown"
                most_matches_score = 0
                
                for person, count in match_counts.items():
                    if count > most_matches:
                        most_matches = count
                        most_matches_name = person
                        most_matches_score = match_scores[person]
                
                # Set a threshold for recognition based on minimum matches
                if most_matches >= self.min_recognition_matches and most_matches_score > self.recognition_threshold:
                    name = most_matches_name
                    # Use the average score for this person
                    best_score = most_matches_score
                    current_time = time.time()
                    
                    # Handle attendance confirmation process
                    if self.pending_attendance is None:
                        # Mark attendance immediately without countdown
                        self.mark_attendance(name)
                        self.pending_attendance = name
                        
                        # Update status
                        self.status_label.setText(f"Confirmed & Marked: {name} (Score: {best_score:.2f})")
                        self.status_label.setStyleSheet("color: #2ecc71; font-weight: bold; font-size: 14px; padding: 5px;")
                        self.statusBar.showMessage(f"Attendance confirmed and marked for {name} | Score: {best_score:.2f}")
                    elif self.pending_attendance == name:
                        # Already marked for this person, just update status
                        self.status_label.setText(f"Already Marked: {name} (Score: {best_score:.2f})")
                        self.statusBar.showMessage(f"Attendance already marked for {name} | Score: {best_score:.2f}")
                    else:
                        # Different person detected, mark their attendance
                        self.mark_attendance(name)
                        self.pending_attendance = name
                        
                        # Update status
                        self.status_label.setText(f"Confirmed & Marked: {name} (Score: {best_score:.2f})")
                        self.status_label.setStyleSheet("color: #2ecc71; font-weight: bold; font-size: 14px; padding: 5px;")
                        self.statusBar.showMessage(f"Attendance confirmed and marked for {name} | Score: {best_score:.2f}")
                    
                    # Smart learning - update face data if recognition is successful but score is not very high
                    if self.smart_learning_enabled and best_score < self.learning_threshold:
                        # Check if we haven't updated this person's data recently (at least 2 seconds ago)
                        if name not in self.last_learning_time or (current_time - self.last_learning_time[name]) > 2:
                            self.update_face_data(name, face_roi)
                            self.last_learning_time[name] = current_time
                else:
                    # Update status for unknown face
                    self.status_label.setText(f"Unknown Face (Best match: {best_name}, Score: {best_score:.2f})")
                    self.status_label.setStyleSheet("color: #e74c3c; font-weight: bold; font-size: 14px; padding: 5px;")
                    
                    # If we were in the middle of confirming attendance, reset it
                    if self.pending_attendance is not None:
                        self.pending_attendance = None
                        self.statusBar.showMessage(f"Attendance confirmation reset - recognition lost (score: {best_score:.2f})")
                        # We don't update status_label here as it's already set to "Unknown Face" above
                
                # Draw a more attractive rectangle with color based on recognition status
                if name != "Unknown":
                    if self.pending_attendance == name:
                        # Confirming attendance - yellow/orange
                        rect_color = (41, 128, 185)  # Blue
                        text_color = (41, 128, 185)  # Blue
                        
                        # Calculate remaining time for confirmation
                        current_time = time.time()
                        # Ensure confirmation_start_time is not None before subtraction
                        if self.confirmation_start_time is not None:
                            elapsed_time = current_time - self.confirmation_start_time
                            remaining_time = max(0, self.confirmation_duration - elapsed_time)
                        else:
                            # If confirmation_start_time is None, set remaining_time to 0
                            remaining_time = 0
                        
                        # If confirmation is complete, change to green
                        if remaining_time <= 0:
                            rect_color = (46, 204, 113)  # Green
                            text_color = (46, 204, 113)  # Green
                    else:
                        # Recognized but not confirming - green
                        rect_color = (46, 204, 113)  # Green
                        text_color = (46, 204, 113)  # Green
                else:
                    # Unknown - red
                    rect_color = (231, 76, 60)  # Red
                    text_color = (231, 76, 60)  # Red
                
                # Draw rectangle with thickness based on confidence
                thickness = max(1, min(3, int(best_score * 5))) if best_score > 0.5 else 1
                cv2.rectangle(color_frame, (x, y), (x+w, y+h), rect_color, thickness)
                
                # Create a background for the name text
                display_name = name
                if self.pending_attendance == name:
                    # Add confirmation indicator to the name
                    display_name = f"{name} ✓"
                
                text_size = cv2.getTextSize(display_name, cv2.FONT_HERSHEY_SIMPLEX, 0.75, 2)[0]
                cv2.rectangle(color_frame, (x, y-30), (x+text_size[0]+10, y), rect_color, -1)
                cv2.putText(color_frame, display_name, (x+5, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
                
                # Add confidence score
                score_text = f"Score: {best_score:.2f}"
                cv2.putText(color_frame, score_text, (x, y+h+20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2)
        
        # Combine title bar and frame
        display_frame = np.vstack((title_bar, color_frame))
        
        # Convert BGR to RGB for display
        rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
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
            
            # Create a dialog to display attendance
            dialog = QWidget(self, Qt.Window)
            dialog.setWindowTitle("Attendance Records")
            dialog.setGeometry(200, 200, 800, 600)
            dialog.setStyleSheet("""
                QWidget {
                    background-color: #34495e;
                    color: white;
                }
                QTableWidget {
                    background-color: #2c3e50;
                    color: white;
                    gridline-color: #3498db;
                    border: 1px solid #3498db;
                    border-radius: 5px;
                }
                QTableWidget::item {
                    padding: 5px;
                }
                QTableWidget::item:selected {
                    background-color: #3498db;
                }
                QHeaderView::section {
                    background-color: #2980b9;
                    color: white;
                    padding: 5px;
                    border: 1px solid #3498db;
                    font-weight: bold;
                }
            """)
            
            # Create layout
            layout = QVBoxLayout(dialog)
            
            # Add title
            title = QLabel("Attendance Records")
            title.setAlignment(Qt.AlignCenter)
            title.setFont(QFont("Arial", 16, QFont.Bold))
            layout.addWidget(title)
            
            # Create table widget
            table = QTableWidget()
            table.setRowCount(len(df))
            table.setColumnCount(len(df.columns))
            table.setHorizontalHeaderLabels(df.columns)
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            table.verticalHeader().setVisible(False)
            
            # Fill table with data
            for i in range(len(df)):
                for j in range(len(df.columns)):
                    item = QTableWidgetItem(str(df.iloc[i, j]))
                    item.setTextAlignment(Qt.AlignCenter)
                    table.setItem(i, j, item)
            
            layout.addWidget(table)
            
            # Add close button
            close_button = QPushButton("Close")
            close_button.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border-radius: 5px;
                    font-weight: bold;
                    padding: 8px;
                    min-height: 30px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
                QPushButton:pressed {
                    background-color: #1f618d;
                }
            """)
            close_button.clicked.connect(dialog.close)
            layout.addWidget(close_button)
            
            dialog.show()
        else:
            QMessageBox.warning(self, "Error", "No attendance records found!")

    def toggle_smart_learning(self, state):
        self.smart_learning_enabled = (state == Qt.Checked)
        status = "enabled" if self.smart_learning_enabled else "disabled"
        self.status_label.setText(f"Smart Learning: {status.capitalize()}")
        self.status_label.setStyleSheet(f"color: {'#2ecc71' if self.smart_learning_enabled else '#e74c3c'}; font-weight: bold; font-size: 14px; padding: 5px;")
        self.statusBar.showMessage(f"System Ready | Smart Learning: {status.capitalize()}")
        QMessageBox.information(self, "Smart Learning", f"Smart learning has been {status}.")
    
    def update_face_data(self, name, new_face_sample):
        if name in self.known_faces:
            # Check if this sample is sufficiently different from existing samples
            is_unique = True
            for existing_sample in self.known_faces[name]:
                try:
                    # Compare the new sample with existing ones
                    result = cv2.matchTemplate(new_face_sample, existing_sample, cv2.TM_CCOEFF_NORMED)
                    similarity = cv2.minMaxLoc(result)[1]
                    
                    # If too similar to an existing sample, don't add it
                    if similarity > 0.85:  # Slightly lower similarity threshold to capture more variations
                        is_unique = False
                        break
                except Exception as e:
                    continue
            
            # Add the new face sample if it's unique
            if is_unique:
                self.known_faces[name].append(new_face_sample)
                self.save_face_data()
                print(f"Smart learning: Added new unique face sample for {name}")
                self.statusBar.showMessage(f"Smart learning: Added new unique face sample for {name} | Total samples: {len(self.known_faces[name])}")
            else:
                print(f"Smart learning: Skipped similar face sample for {name}")
        else:
            # If this is a new person, initialize with this sample
            self.known_faces[name] = [new_face_sample]
            self.save_face_data()
            print(f"Smart learning: Created new face profile for {name}")
            self.statusBar.showMessage(f"Smart learning: Created new face profile for {name}")
    
    def show_about(self):
        # Create a custom about dialog
        dialog = QWidget(self, Qt.Window)
        dialog.setWindowTitle("About Digital Attendance System")
        dialog.setGeometry(200, 200, 500, 400)
        dialog.setStyleSheet("""
            QWidget {
                background-color: #34495e;
                color: white;
            }
            QLabel {
                color: white;
            }
        """)
        
        # Create layout
        layout = QVBoxLayout(dialog)
        
        # Add title
        title = QLabel("Digital Attendance System")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #3498db;")
        layout.addWidget(title)
        
        # Add subtitle
        subtitle = QLabel("with Enhanced Recognition & Smart Learning Technology")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont("Arial", 12, QFont.Italic))
        subtitle.setStyleSheet("color: #2ecc71;")
        layout.addWidget(subtitle)
        
        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #3498db;")
        layout.addWidget(separator)
        
        # Add developer info
        dev_info = QLabel("Developed by: Tariqul Islam\nDepartment: CSE\nBatch: 37\nGB")
        dev_info.setAlignment(Qt.AlignCenter)
        dev_info.setFont(QFont("Arial", 10))
        dev_info.setStyleSheet("margin: 20px;")
        layout.addWidget(dev_info)
        
        # Add feature info
        feature_frame = QFrame()
        feature_frame.setFrameShape(QFrame.StyledPanel)
        feature_frame.setFrameShadow(QFrame.Raised)
        feature_frame.setStyleSheet("border: 1px solid #3498db; border-radius: 5px; padding: 10px;")
        feature_layout = QVBoxLayout(feature_frame)
        
        feature_title = QLabel("Key Features:")
        feature_title.setFont(QFont("Arial", 12, QFont.Bold))
        feature_title.setStyleSheet("color: #f39c12;")
        feature_layout.addWidget(feature_title)
        
        # Enhanced Recognition Features
        enhanced_title = QLabel("Enhanced Face Recognition:")
        enhanced_title.setFont(QFont("Arial", 10, QFont.Bold))
        enhanced_title.setStyleSheet("color: #9b59b6; margin-left: 10px;")
        feature_layout.addWidget(enhanced_title)
        
        enhanced_features = QLabel(
            f"• Uses multiple face data points (minimum {self.min_recognition_matches} matches required)\n"
            "• Prioritizes face capture before background analysis\n"
            "• Captures 8 different face angles for better recognition\n"
            "• Ensures unique face samples for diverse recognition capability"
        )
        enhanced_features.setFont(QFont("Arial", 10))
        enhanced_features.setStyleSheet("margin-left: 20px;")
        feature_layout.addWidget(enhanced_features)
        
        # Smart Learning Features
        smart_learning_title = QLabel("Smart Learning:")
        smart_learning_title.setFont(QFont("Arial", 10, QFont.Bold))
        smart_learning_title.setStyleSheet("color: #2ecc71; margin-left: 10px;")
        feature_layout.addWidget(smart_learning_title)
        
        smart_features = QLabel(
            "• Continuously improves face recognition accuracy\n"
            "• Adapts to gradual changes in appearance\n"
            "• Stores unlimited face samples per person for maximum accuracy\n"
            "• Automatically updates face data during recognition"
        )
        smart_features.setFont(QFont("Arial", 10))
        smart_features.setStyleSheet("margin-left: 20px;")
        feature_layout.addWidget(smart_features)
        
        # Attendance Confirmation Features
        confirmation_title = QLabel("Attendance Confirmation:")
        confirmation_title.setFont(QFont("Arial", 10, QFont.Bold))
        confirmation_title.setStyleSheet("color: #3498db; margin-left: 10px; margin-top: 10px;")
        feature_layout.addWidget(confirmation_title)
        
        confirmation_features = QLabel(
            "• Instant attendance marking upon recognition\n"
            "• Prevents duplicate attendance entries\n"
            "• Visual checkmark confirmation\n"
            "• Color-coded status indicators"
        )
        confirmation_features.setFont(QFont("Arial", 10))
        confirmation_features.setStyleSheet("margin-left: 20px;")
        feature_layout.addWidget(confirmation_features)
        
        layout.addWidget(feature_frame)
        
        # Add close button
        close_button = QPushButton("Close")
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                padding: 8px;
                min-height: 30px;
                margin-top: 20px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1f618d;
            }
        """)
        close_button.clicked.connect(dialog.close)
        layout.addWidget(close_button)
        
        dialog.show()

    def show_remove_student_dialog(self):
        if not self.known_faces:
            QMessageBox.warning(self, "Warning", "No students registered in the system!")
            return

        # Create a dialog window
        dialog = QWidget(self, Qt.Window)
        dialog.setWindowTitle("Remove Student")
        dialog.setGeometry(200, 200, 400, 500)
        dialog.setStyleSheet("""
            QWidget {
                background-color: #34495e;
                color: white;
            }
            QListWidget {
                background-color: #2c3e50;
                color: white;
                border: 1px solid #3498db;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #3498db;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: white;
                margin-bottom: 10px;
            }
        """)
        
        # Create layout
        layout = QVBoxLayout(dialog)
        
        # Add title
        title = QLabel("Remove Student")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #e74c3c; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Add label
        label = QLabel("Select student to remove:")
        label.setStyleSheet("color: #f39c12;")
        layout.addWidget(label)
        
        # Create list widget
        list_widget = QListWidget()
        list_widget.addItems(self.known_faces.keys())
        layout.addWidget(list_widget)
        
        # Add instruction
        instruction = QLabel("Warning: This action cannot be undone. All attendance records for the selected student will also be removed.")
        instruction.setWordWrap(True)
        instruction.setStyleSheet("color: #e74c3c; font-style: italic; margin-top: 10px;")
        layout.addWidget(instruction)
        
        # Add buttons
        button_layout = QHBoxLayout()
        
        remove_button = QPushButton("Remove")
        remove_button.setIcon(QIcon.fromTheme("edit-delete"))
        remove_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                padding: 10px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        remove_button.clicked.connect(lambda: self.remove_student(list_widget.currentItem().text() if list_widget.currentItem() else None, dialog))
        
        cancel_button = QPushButton("Cancel")
        cancel_button.setIcon(QIcon.fromTheme("dialog-cancel"))
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #7f8c8d;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                padding: 10px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #95a5a6;
            }
            QPushButton:pressed {
                background-color: #bdc3c7;
            }
        """)
        cancel_button.clicked.connect(dialog.close)
        
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(remove_button)
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