# from flask import Flask, request, jsonify, send_file, render_template
# import os
# import io
# import time
# import uuid
# import bcrypt
# import random
# from pymongo import MongoClient
# from dotenv import load_dotenv
# from werkzeug.utils import secure_filename
# from datetime import datetime
# from bson.objectid import ObjectId

# from utils.auth import generate_token, token_required
# from utils.encryption import generate_key, encrypt_file_data, decrypt_file_data
# from utils.threat_detection import validate_file_upload, log_activity

# load_dotenv()

# app = Flask(__name__)
# app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')





# if not os.getenv('MONGODB_URI'):
#     print("❌ ERROR: MONGODB_URI not found in .env file")






# client = MongoClient(os.getenv('MONGODB_URI'))
# try:
#     db = client.get_default_database()
# except Exception:
#     db = client['secure_fs_db']

# UPLOAD_FOLDER = 'uploads'
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/dashboard')
# def dashboard():
#     return render_template('dashboard.html')

# @app.route('/api/register', methods=['POST'])
# def register():
#     data = request.json
#     username = data.get('username')
#     password = data.get('password')
#     if not username or not password:
#         return jsonify({'message': 'Username and password required'}), 400
    
#     if db.users.find_one({'username': username}):
#         return jsonify({'message': 'User already exists'}), 400
        
#     hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
#     db.users.insert_one({
#         'username': username,
#         'password_hash': hashed,
#         'otp': None
#     })
#     log_activity(db, username, 'User registered')
#     return jsonify({'message': 'Registered successfully'}), 201

# @app.route('/api/login', methods=['POST'])
# def login():
#     data = request.json
#     username = data.get('username')
#     password = data.get('password')
    
#     user = db.users.find_one({'username': username})
#     if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password_hash']):
#         return jsonify({'message': 'Invalid credentials'}), 401
        
#     otp = str(random.randint(100000, 999999))
#     db.users.update_one({'_id': user['_id']}, {'$set': {'otp': otp}})
    
#     print(f"\n[{datetime.utcnow()}] SECURITY ALERT - OTP for {username}: {otp}\n")
    
#     log_activity(db, username, 'User login initiated (Pending 2FA)')
#     return jsonify({'message': 'OTP sent', 'require_otp': True})

# @app.route('/api/verify-otp', methods=['POST'])
# def verify_otp():
#     data = request.json
#     username = data.get('username')
#     otp = data.get('otp')
    
#     user = db.users.find_one({'username': username})
#     if not user or user.get('otp') != otp:
#         return jsonify({'message': 'Invalid OTP'}), 401
        
#     db.users.update_one({'_id': user['_id']}, {'$set': {'otp': None}})
    
#     token = generate_token(username)
#     log_activity(db, username, 'User login successful (2FA verified)')
#     return jsonify({'token': token})

# @app.route('/api/upload', methods=['POST'])
# @token_required
# def upload_file(current_user):
#     if 'file' not in request.files:
#         return jsonify({'message': 'No file part'}), 400
        
#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({'message': 'No selected file'}), 400
        
#     file_data = file.read()
#     file_size = len(file_data)
    
#     is_safe, msg = validate_file_upload(file.filename, file_size, db, current_user)
#     if not is_safe:
#         return jsonify({'message': msg}), 400
        
#     key = generate_key()
#     encrypted_data = encrypt_file_data(file_data, key)
    
#     unique_filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
#     file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    
#     with open(file_path, 'wb') as f:
#         f.write(encrypted_data)
        
#     db.files.insert_one({
#         'filename': file.filename,
#         'unique_filename': unique_filename,
#         'owner': current_user,
#         'shared_users': [],
#         'encryption_key': key.decode('utf-8'),
#         'metadata': {
#             'size': file_size,
#             'type': file.content_type,
#             'timestamp': datetime.utcnow()
#         }
#     })
    
#     log_activity(db, current_user, f'File uploaded securely: {file.filename}')
#     return jsonify({'message': 'File uploaded securely'})

# @app.route('/api/files', methods=['GET'])
# @token_required
# def get_files(current_user):
#     files = db.files.find({
#         '$or': [
#             {'owner': current_user},
#             {'shared_users': current_user}
#         ]
#     })
    
#     result = []
#     for f in files:
#         f['_id'] = str(f['_id'])
#         f.pop('encryption_key', None)
#         f.pop('unique_filename', None)
#         result.append(f)
        
#     return jsonify(result)

# @app.route('/api/download/<file_id>', methods=['GET'])
# @token_required
# def download_file(current_user, file_id):
#     try:
#         f_record = db.files.find_one({'_id': ObjectId(file_id)})
#     except Exception:
#         return jsonify({'message': 'Invalid file ID'}), 400

#     if not f_record:
#         return jsonify({'message': 'File not found'}), 404
        
#     if f_record['owner'] != current_user and current_user not in f_record['shared_users']:
#         log_activity(db, current_user, f"Unauthorized download attempt: {f_record['filename']}", threat_detected=True)
#         return jsonify({'message': 'Unauthorized'}), 403
        
#     file_path = os.path.join(UPLOAD_FOLDER, f_record['unique_filename'])
#     if not os.path.exists(file_path):
#         return jsonify({'message': 'File missing on server'}), 500
        
#     with open(file_path, 'rb') as f:
#         encrypted_data = f.read()
        
#     key = f_record['encryption_key'].encode('utf-8')
#     try:
#         decrypted_data = decrypt_file_data(encrypted_data, key)
#     except Exception:
#         return jsonify({'message': 'Decryption failed'}), 500
        
#     log_activity(db, current_user, f"File downloaded: {f_record['filename']}")
    
#     return send_file(
#         io.BytesIO(decrypted_data),
#         download_name=f_record['filename'],
#         as_attachment=True
#     )

# @app.route('/api/read/<file_id>', methods=['GET'])
# @token_required
# def read_file(current_user, file_id):
#     try:
#         f_record = db.files.find_one({'_id': ObjectId(file_id)})
#     except Exception:
#         return jsonify({'message': 'Invalid file ID'}), 400

#     if not f_record:
#         return jsonify({'message': 'File not found'}), 404
        
#     if f_record['owner'] != current_user and current_user not in f_record['shared_users']:
#         return jsonify({'message': 'Unauthorized'}), 403
        
#     file_path = os.path.join(UPLOAD_FOLDER, f_record['unique_filename'])


#     if not os.path.exists(file_path):
#     return jsonify({'message': 'File not found on server'}), 500




#     with open(file_path, 'rb') as f:
#         encrypted_data = f.read()
        
#     key = f_record['encryption_key'].encode('utf-8')
#     decrypted_data = decrypt_file_data(encrypted_data, key)
    
#     return send_file(
#         io.BytesIO(decrypted_data),
#         download_name=f_record['filename'],
#         mimetype=f_record['metadata']['type'],
#         as_attachment=False
#     )
    
# @app.route('/api/delete/<file_id>', methods=['DELETE'])
# @token_required
# def delete_file(current_user, file_id):
#     try:
#         f_record = db.files.find_one({'_id': ObjectId(file_id)})
#     except Exception:
#         return jsonify({'message': 'Invalid ID'}), 400
        
#     if not f_record:
#         return jsonify({'message': 'Not found'}), 404
        
#     if f_record['owner'] != current_user:
#         return jsonify({'message': 'Only owner can delete'}), 403
        
#     file_path = os.path.join(UPLOAD_FOLDER, f_record['unique_filename'])
#     if os.path.exists(file_path):
#         os.remove(file_path)
        
#     db.files.delete_one({'_id': ObjectId(file_id)})
#     log_activity(db, current_user, f"File deleted: {f_record['filename']}")
#     return jsonify({'message': 'Deleted successfully'})

# @app.route('/api/share', methods=['POST'])
# @token_required
# def share_file(current_user):
#     data = request.json
#     file_id = data.get('file_id')
#     share_with = data.get('share_with')
    
#     if not file_id or not share_with:
#         return jsonify({'message': 'Missing fields'}), 400
        
#     if not db.users.find_one({'username': share_with}):
#         return jsonify({'message': 'Target user does not exist'}), 404
        
#     try:
#         f_record = db.files.find_one({'_id': ObjectId(file_id)})
#     except Exception:
#         return jsonify({'message': 'Invalid ID'}), 400
        
#     if f_record['owner'] != current_user:
#         return jsonify({'message': 'Only owner can share'}), 403
        
#     if share_with not in f_record['shared_users']:
#         db.files.update_one(
#             {'_id': ObjectId(file_id)},
#             {'$push': {'shared_users': share_with}}
#         )
        
#     log_activity(db, current_user, f"Shared file {f_record['filename']} with {share_with}")
#     return jsonify({'message': 'File shared successfully'})

# # if __name__ == '__main__':
# #     app.run(debug=True, port=5000)
# if __name__ == '__main__':
#     app.run(debug=True, port=5000, use_reloader=False)





from flask import Flask, request, jsonify, send_file, render_template
import os
import io
import uuid
import bcrypt
import random
from pymongo import MongoClient
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from datetime import datetime
from bson.objectid import ObjectId

from utils.auth import generate_token, token_required
from utils.encryption import generate_key, encrypt_file_data, decrypt_file_data
from utils.threat_detection import validate_file_upload, log_activity

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# 🔥 Check MongoDB URI
if not os.getenv('MONGODB_URI'):
    print("❌ ERROR: MONGODB_URI not found in .env file")

# MongoDB Connection
client = MongoClient(os.getenv('MONGODB_URI'))
try:
    db = client.get_default_database()
except Exception:
    db = client['secure_fs_db']

# Upload folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- ROUTES ---------------- #

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# ---------------- AUTH ---------------- #

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password required'}), 400

    if db.users.find_one({'username': username}):
        return jsonify({'message': 'User already exists'}), 400

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    db.users.insert_one({
        'username': username,
        'password_hash': hashed,
        'otp': None
    })

    log_activity(db, username, 'User registered')
    return jsonify({'message': 'Registered successfully'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = db.users.find_one({'username': username})
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password_hash']):
        return jsonify({'message': 'Invalid credentials'}), 401

    otp = str(random.randint(100000, 999999))
    db.users.update_one({'_id': user['_id']}, {'$set': {'otp': otp}})

    print(f"\n[{datetime.utcnow()}] OTP for {username}: {otp}\n")

    log_activity(db, username, 'Login initiated (OTP sent)')
    return jsonify({'message': 'OTP sent', 'require_otp': True})

@app.route('/api/verify-otp', methods=['POST'])
def verify_otp():
    data = request.json
    username = data.get('username')
    otp = data.get('otp')

    user = db.users.find_one({'username': username})
    if not user or user.get('otp') != otp:
        return jsonify({'message': 'Invalid OTP'}), 401

    db.users.update_one({'_id': user['_id']}, {'$set': {'otp': None}})

    token = generate_token(username)
    log_activity(db, username, 'Login successful')

    return jsonify({'token': token})

# ---------------- FILE UPLOAD ---------------- #

@app.route('/api/upload', methods=['POST'])
@token_required
def upload_file(current_user):
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    file_data = file.read()
    file_size = len(file_data)

    is_safe, msg = validate_file_upload(file.filename, file_size, db, current_user)
    if not is_safe:
        return jsonify({'message': msg}), 400

    key = generate_key()
    encrypted_data = encrypt_file_data(file_data, key)

    unique_filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)

    with open(file_path, 'wb') as f:
        f.write(encrypted_data)

    db.files.insert_one({
        'filename': file.filename,
        'unique_filename': unique_filename,
        'owner': current_user,
        'shared_users': [],
        'encryption_key': key.decode(),
        'metadata': {
            'size': file_size,
            'type': file.content_type,
            'timestamp': datetime.utcnow()
        }
    })

    log_activity(db, current_user, f'File uploaded: {file.filename}')
    return jsonify({'message': 'File uploaded securely'})

# ---------------- GET FILES ---------------- #

@app.route('/api/files', methods=['GET'])
@token_required
def get_files(current_user):
    files = db.files.find({
        '$or': [
            {'owner': current_user},
            {'shared_users': current_user}
        ]
    })

    result = []
    for f in files:
        f['_id'] = str(f['_id'])
        f.pop('encryption_key', None)
        f.pop('unique_filename', None)
        result.append(f)

    return jsonify(result)

# ---------------- DOWNLOAD ---------------- #

@app.route('/api/download/<file_id>', methods=['GET'])
@token_required
def download_file(current_user, file_id):
    try:
        f_record = db.files.find_one({'_id': ObjectId(file_id)})
    except Exception:
        return jsonify({'message': 'Invalid ID'}), 400

    if not f_record:
        return jsonify({'message': 'Not found'}), 404

    if f_record['owner'] != current_user and current_user not in f_record['shared_users']:
        return jsonify({'message': 'Unauthorized'}), 403

    file_path = os.path.join(UPLOAD_FOLDER, f_record['unique_filename'])

    if not os.path.exists(file_path):
        return jsonify({'message': 'File missing'}), 500

    with open(file_path, 'rb') as f:
        encrypted_data = f.read()

    decrypted_data = decrypt_file_data(encrypted_data, f_record['encryption_key'].encode())

    return send_file(io.BytesIO(decrypted_data),
                     download_name=f_record['filename'],
                     as_attachment=True)

# ---------------- READ ---------------- #

@app.route('/api/read/<file_id>', methods=['GET'])
@token_required
def read_file(current_user, file_id):
    try:
        f_record = db.files.find_one({'_id': ObjectId(file_id)})
    except Exception:
        return jsonify({'message': 'Invalid ID'}), 400

    if not f_record:
        return jsonify({'message': 'Not found'}), 404

    if f_record['owner'] != current_user and current_user not in f_record['shared_users']:
        return jsonify({'message': 'Unauthorized'}), 403

    file_path = os.path.join(UPLOAD_FOLDER, f_record['unique_filename'])

    if not os.path.exists(file_path):
        return jsonify({'message': 'File not found'}), 500

    with open(file_path, 'rb') as f:
        encrypted_data = f.read()

    decrypted_data = decrypt_file_data(encrypted_data, f_record['encryption_key'].encode())

    return send_file(io.BytesIO(decrypted_data),
                     download_name=f_record['filename'],
                     mimetype=f_record['metadata']['type'])

# ---------------- DELETE ---------------- #

@app.route('/api/delete/<file_id>', methods=['DELETE'])
@token_required
def delete_file(current_user, file_id):
    f_record = db.files.find_one({'_id': ObjectId(file_id)})

    if not f_record:
        return jsonify({'message': 'Not found'}), 404

    if f_record['owner'] != current_user:
        return jsonify({'message': 'Only owner can delete'}), 403

    file_path = os.path.join(UPLOAD_FOLDER, f_record['unique_filename'])

    if os.path.exists(file_path):
        os.remove(file_path)

    db.files.delete_one({'_id': ObjectId(file_id)})

    return jsonify({'message': 'Deleted'})

# ---------------- SHARE ---------------- #

@app.route('/api/share', methods=['POST'])
@token_required
def share_file(current_user):
    data = request.json
    file_id = data.get('file_id')
    share_with = data.get('share_with')

    if not file_id or not share_with:
        return jsonify({'message': 'Missing fields'}), 400

    if not db.users.find_one({'username': share_with}):
        return jsonify({'message': 'User not found'}), 404

    f_record = db.files.find_one({'_id': ObjectId(file_id)})

    if f_record['owner'] != current_user:
        return jsonify({'message': 'Only owner can share'}), 403

    db.files.update_one(
        {'_id': ObjectId(file_id)},
        {'$addToSet': {'shared_users': share_with}}
    )

    return jsonify({'message': 'File shared successfully'})

# ---------------- RUN ---------------- #

if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)