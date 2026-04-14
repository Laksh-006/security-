# Secure File Management System

A production-level secure file management SaaS application with robust security features, built using Flask (Python) and MongoDB Atlas. 

## Features
- **Secure Authentication**: Hashed passwords with bcrypt, JSON Web Tokens (JWT) for API access, and Two-Factor Authentication (OTP-based).
- **End-to-End Encryption**: Every uploaded file is fully encrypted using AES (Fernet) symmetrically before it touches the physical storage.
- **Access Control & Sharing**: Secure capability to grant specific users read and download access while ensuring data privacy.
- **Threat Detection**:
  - Validates and restricts anomalous path traversals (`../`).
  - Scans for malicious extensions (`.exe`, `.bat`, `.js`, etc.).
  - Simulates buffer overflow monitoring by detecting file bounds (Max size restricted to 50MB).
- **Activity Logging**: Comprehensive database logs for all authenticated transactions and potential threat attempts.
- **Stunning UI**: Google Drive-like fluid user interface using standard HTML/vanilla JS and Tailwind CSS for the enterprise-grade experience.

## Setup Instructions

1. **Prerequisites**: Make sure you have python installed (Python 3.8+). You also need a MongoDB database running or Atlas URI.
2. **Setup virtual environment (recommended)**:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Environment Set-Up**:
   - Verify variables in `.env`. By default, it connects to standard localhost MongoDB. To use MongoDB Atlas, replace the `MONGODB_URI` connection string inside `.env`.

5. **Run the Application**:
   ```bash
   python app.py
   ```
   Navigate to `http://localhost:5000` via your web browser.

**NOTE:** The 2FA OTP codes during login will be logged in your running terminal (server console) for demonstration purposes. Use the code from the terminal to access the dashboard.
