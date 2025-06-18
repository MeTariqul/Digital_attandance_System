# Digital Attendance System

## Overview
This is a digital attendance system with a graphical user interface (GUI) that uses face detection to mark attendance. All data is securely stored and managed in the same directory as the program.

## Features
- Modern PyQt5 GUI
- Real-time camera view in natural color
- Add new students with multi-angle face capture (5 samples)
- Remove students (face data and attendance)
- Face data is encrypted for privacy
- Attendance records are saved in an Excel file
- View attendance records in the app
- About section with developer info

## Setup Instructions
1. **Install Python 3.8–3.10** (recommended)
2. **Create and activate a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/Mac:
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the program:**
   ```bash
   python attendance_system.py
   ```

## Usage Guide
- **Add New Student:**
  - Click "Add New Student"
  - Enter the student's name
  - Look at the camera and slowly turn your head to capture 5 different angles
  - Wait for the success message

- **Remove Student:**
  - Click "Remove Student"
  - Select a student from the list and click "Remove"
  - Confirm removal

- **View Attendance:**
  - Click "View Attendance" to see all attendance records

- **About:**
  - Click "About" to see developer and batch information

## Data Storage
- All files (`attendance.xlsx`, `face_data.enc`, `encryption.key`) are saved in the same directory as `attendance_system.py`.
- Face data is encrypted for privacy and security.
- Attendance is stored in Excel format for easy access and backup.

## Developer Info
- Developed by: Tariqul Islam
- Department: CSE
- Batch: 37
- GB

## Troubleshooting
- If the camera does not show real color, ensure you are using the latest code version.
- If you see errors about missing packages, re-run `pip install -r requirements.txt`.
- For any other issues, check the terminal for error messages and ensure your Python version is compatible.