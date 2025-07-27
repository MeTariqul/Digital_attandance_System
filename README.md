# Digital Attendance System with Smart Learning

A Python-based digital attendance system using facial recognition with smart learning capabilities and Excel integration.

## Features
- Face data encoding and recognition
- Smart learning for improved recognition accuracy over time
- Automatic adaptation to gradual changes in appearance
- Attendance tracking and logging to Excel (`attendance.xlsx`)
- Secure face data storage (`face_data.enc`)
- User-friendly graphical interface

## Requirements
Install dependencies with:
```
pip install -r requirements.txt
```

## Usage
1. Run the main script:
   ```
   python attendance_system.py
   ```
2. Follow on-screen instructions to register faces and mark attendance.

## Files
- `attendance_system.py`: Main application script
- `attendance.xlsx`: Attendance log
- `face_data.enc`: Encoded face data
- `requirements.txt`: Python dependencies

## Notes
- Ensure your webcam is connected for face registration and attendance.
- For best results, use in a well-lit environment.
- The smart learning feature continuously improves recognition accuracy by updating face data when recognition is successful but with lower confidence.
- Smart learning can be toggled on/off through the interface.

---

© 2024 MD Tariqul Islam. All rights reserved.