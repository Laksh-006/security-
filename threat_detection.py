import os
from datetime import datetime

MAX_FILE_SIZE = 50 * 1024 * 1024 # 50 MB limits
ALLOWED_EXTENSIONS = {'.txt', '.pdf', '.png', '.jpg', '.jpeg', '.docx', '.csv'}
DANGEROUS_EXTENSIONS = {'.exe', '.bat', '.sh', '.js', '.vbs', '.msi', '.cmd', '.php', '.dll'}

def log_activity(db, username, action, threat_detected=False):
    db.logs.insert_one({
        'user': username,
        'action': action,
        'threat_detected': threat_detected,
        'timestamp': datetime.utcnow()
    })

def validate_file_upload(file_name, file_size, db, username):
    # 1. Path Traversal
    if '..' in file_name or '/' in file_name or '\\' in file_name:
        log_activity(db, username, f'Path traversal attempt with filename: {file_name}', threat_detected=True)
        return False, "Path traversal attack detected."

    # 2. Malicious File Type
    _, ext = os.path.splitext(file_name)
    ext = ext.lower()
    
    if ext in DANGEROUS_EXTENSIONS:
        log_activity(db, username, f'Malicious file upload attempt: {file_name}', threat_detected=True)
        return False, "Malicious file type detected."

    if ext and ext not in ALLOWED_EXTENSIONS:
        log_activity(db, username, f'Disallowed file upload attempt: {file_name}', threat_detected=True)
        return False, f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"

    # 3. Buffer Overflow
    if file_size > MAX_FILE_SIZE:
        log_activity(db, username, f'Buffer overflow simulation - oversized file: {file_size} bytes', threat_detected=True)
        return False, "Simulated buffer overflow: File size exceeds the allowed limit."

    return True, "File is safe."
