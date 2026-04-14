import jwt
import datetime
from functools import wraps
from flask import request, jsonify
import os

def generate_token(username):
    payload = {
        'username': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    return jwt.encode(payload, os.getenv('JWT_SECRET', 'fallback-secret'), algorithm='HS256')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            token = request.args.get('token')
            
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
            
        try:
            if token.startswith('Bearer '):
                token = token.split(' ')[1]
            data = jwt.decode(token, os.getenv('JWT_SECRET', 'fallback-secret'), algorithms=['HS256'])
            current_user = data['username']
        except Exception as e:
            return jsonify({'message': 'Token is invalid!'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated
