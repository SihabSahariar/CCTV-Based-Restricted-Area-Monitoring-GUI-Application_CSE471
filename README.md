# CCTV Based Restricted Area Monitoring GUI Application

## Overview

This project aims to create a robust and user-friendly CCTV monitoring system with advanced features for restricted area surveillance. The application is developed using Python and PyQt5 for the GUI, SQL for the database, OpenCV for camera handling, and YOLO for object detection.

## System Features

1. **Add Camera:**
   - Users can add cameras using IP, RTSP, or webcam.

2. **Delete Camera:**
   - Users can remove cameras from the system.

3. **Live Streaming:**
   - Real-time monitoring of camera feeds.

4. **User Admin Panel:**
   - Access control with multi-user levels and permissions.

5. **Camera Health Checks:**
   - Automated checks with status alerts.

6. **Auto Camera Reconnect:**
   - Reconnects cameras automatically after disconnection.

7. **Intruder Detection and Tracking:**
   - Identifies and tracks intruders within specified areas of interest.

8. **Customizable Area of Interest:**
   - Users can define and customize areas for monitoring.

9. **Detection Parameter Configuration:**
   - Users can configure parameters for detection algorithms.

10. **Data Recording:**
    - Records data for further analysis.

11. **Vehicle Stationary Detection:**
    - Detects stationary vehicles in no-parking zones.

12. **Facial Detection:**
    - Identifies faces in restricted areas for further analysis.

13. **Real-time Notification System:**
    - Integration with Redis or API for notifications.

14. **Report Generation:**
    - Generates report files for documentation.

15. **Database Operations:**
    - Users can restore/export the database.

16. **Seamless Background Processing:**
    - Background tasks while minimzing the user interface.

17. **Video Streaming without Analytics:**
    - Users can stream video without analytical features.

18. **Object Detection and Tracking:**
    - Specific object detection and tracking in restricted areas.

19. **File Encryption:**
    - Users can encrypt files for future safety.

20. **Multi-user Access Levels:**
    - Different user access levels with specific permissions.

## External Features

- **Cross-Platform Deployment:**
  - Works on Windows, macOS, and Linux.

- **User-Friendly and Lightweight:**
  - Intuitive interface with minimal resource consumption.

- **CPU/GPU Usage:**
  - Utilizes both CPU and GPU for AI inference.

- **Offline Functionality:**
  - Operates without an internet connection.

## Implementation Details

- **Language and Framework:**
  - Python, PyQt5

- **Database:**
  - SQL

- **AI Libraries:**
  - OpenCV, YOLO

## Deployment Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/CCTV-Monitoring-System.git
   cd CCTV-Monitoring-System
