# Digital Attendance System with Smart Learning

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)

**A modern facial recognition attendance system with adaptive learning capabilities**

</div>

## 📋 Overview

The Digital Attendance System is a sophisticated application that uses computer vision and machine learning to automate attendance tracking. The system features smart learning capabilities that improve recognition accuracy over time by adapting to gradual changes in appearance.

<div align="center">

*Streamline your attendance process with cutting-edge facial recognition technology*

</div>

## ✨ Key Features

- **Advanced Facial Recognition** - Accurate identification of registered individuals
- **Smart Learning Algorithm** - Continuously improves recognition accuracy over time
- **Automatic Adaptation** - Adjusts to gradual changes in appearance
- **Excel Integration** - Attendance logs stored in Excel format for easy analysis
- **Secure Data Storage** - Face data encrypted for privacy protection
- **Modern UI** - Intuitive and responsive graphical interface
- **Real-time Processing** - Instant recognition and attendance marking

## 🔧 System Requirements

- Python 3.8 or higher
- Webcam or camera device
- 4GB RAM minimum (8GB recommended)
- 500MB free disk space

## 📥 Installation Guide

### Windows

1. **Install Python**:
   - Download Python 3.8+ from [python.org](https://www.python.org/downloads/windows/)
   - During installation, check "Add Python to PATH"
   - Verify installation by opening Command Prompt and typing: `python --version`

2. **Clone the Repository**:
   ```
   git clone https://github.com/MeTariqul/Digital_attandance_System.git
   cd Digital_attandance_System
   ```

3. **Install Dependencies**:
   ```
   pip install -r requirements.txt
   ```

### macOS

1. **Install Python**:
   - Install Homebrew if not already installed:
     ```
     /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
     ```
   - Install Python:
     ```
     brew install python
     ```
   - Verify installation: `python3 --version`

2. **Clone the Repository**:
   ```
   git clone https://github.com/MeTariqul/Digital_attandance_System.git
   cd Digital_attandance_System
   ```

3. **Install Dependencies**:
   ```
   pip3 install -r requirements.txt
   ```

### Linux (Ubuntu/Debian)

1. **Install Python and Required Packages**:
   ```
   sudo apt update
   sudo apt install python3 python3-pip python3-opencv
   sudo apt install libqt5gui5 libqt5core5a libqt5widgets5
   ```
   - Verify installation: `python3 --version`

2. **Clone the Repository**:
   ```
   git clone https://github.com/MeTariqul/Digital_attandance_System.git
   cd Digital_attandance_System
   ```

3. **Install Dependencies**:
   ```
   pip3 install -r requirements.txt
   ```

## 🚀 Getting Started

1. **Launch the Application**:
   - Windows: `python attendance_system.py`
   - macOS/Linux: `python3 attendance_system.py`

2. **First-time Setup**:
   - The system will create necessary files on first run
   - An encryption key will be generated for secure data storage

## 📖 User Manual

### Main Interface

The application is divided into two main panels:
- **Left Panel**: Camera feed and status display
- **Right Panel**: Control buttons and settings

### Adding a New Student

1. Click the "Add New Student" button in the Student Management section
2. Enter the student's name when prompted
3. Position the student's face in the camera frame
4. Follow the on-screen instructions to capture multiple angles
5. The progress bar will show capture completion status
6. Once complete, the student is registered in the system

### Marking Attendance

1. Ensure the camera is active (starts automatically on launch)
2. When a registered face is detected, the system will:
   - Display the recognized name
   - Mark attendance automatically
   - Log the entry in the attendance file

### Viewing Attendance Records

1. Click the "View Attendance" button
2. The attendance records will be displayed in a table format
3. Records include name, date, and time of attendance

### Removing a Student

1. Click the "Remove Student" button
2. Select the student to remove from the displayed list
3. Confirm the deletion when prompted

### Smart Learning Settings

- Toggle the "Enable Smart Learning" checkbox to turn the feature on/off
- When enabled, the system will:
  - Update face data when recognition is successful but with lower confidence
  - Gradually adapt to changes in appearance over time
  - Improve recognition accuracy with continued use

## 🔍 Troubleshooting

### Camera Not Detected
- Ensure your webcam is properly connected
- Check if other applications are using the camera
- Restart the application

### Recognition Issues
- Ensure adequate lighting in the environment
- Try registering the face again with different angles
- Check if Smart Learning is enabled

### Application Crashes
- Verify all dependencies are correctly installed
- Check system requirements are met
- Ensure the attendance.xlsx file is not open in another program

## 📁 File Structure

- `attendance_system.py`: Main application script
- `attendance.xlsx`: Excel file storing attendance records
- `face_data.enc`: Encrypted file containing face recognition data
- `encryption.key`: Key file for secure data storage
- `requirements.txt`: List of Python dependencies

## 📊 Technical Details

- **Face Detection**: Haar Cascade Classifier
- **Face Recognition**: Custom implementation with adaptive learning
- **UI Framework**: PyQt5
- **Data Storage**: Pandas with Excel integration
- **Security**: Fernet symmetric encryption

---

<div align="center">

## 📞 Support & Contact

For issues, suggestions, or contributions, please open an issue on GitHub or contact:

**MD Tariqul Islam**  
[GitHub Profile](https://github.com/MeTariqul)

© 2024 MD Tariqul Islam. All rights reserved.

</div>