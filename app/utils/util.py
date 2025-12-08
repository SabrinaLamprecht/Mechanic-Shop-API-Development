# app/utils/util.py
from flask import current_app
from datetime import datetime, timedelta, timezone
from jose import jwt
from functools import wraps
from flask import request, jsonify
import os

SECRET_KEY = os.environ.get('SECRET_KEY') or "super secret secrets"

# encode_token function that takes in a mechanic_id or customer_id to create a token specific to that user
def encode_token(user_id, user_type):
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(days=0, hours=1),
        'iat': datetime.now(timezone.utc), 
        'sub': str(user_id),
        'type': user_type
    }
    
    # fetch secret from the Flask app config
    secret_key = current_app.config.get('SECRET_KEY', 'fallback-secret')
    
    
    # this encrypes the token and then returns it
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token

def token_required(required_type=None):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None
        
            if 'Authorization' in request.headers:
            
                token = request.headers['Authorization'].split()[1]
            
                if not token:
                    return jsonify({'message': 'Missing token'}), 400
            
                try:
                    from flask import current_app
                    from jose.exceptions import JWTError, ExpiredSignatureError
                    
                    secret_key = current_app.config.get('SECRET_KEY', 'fallback-secret')
                    data = jwt.decode(token, secret_key, algorithms=['HS256'])

                    user_id = data['sub']
                    user_type = data.get('type')
                    
                    if required_type and user_type != required_type:
                        return jsonify({"message": f'User must be a {required_type}'}), 403
            
                except jwt.ExpiredSignatureError as e:
                    return jsonify({'message': 'Token expired'}), 400
                except jwt.InvalidTokenError:
                    return jsonify({'message': 'Invalid token'}), 400
            
                return f(user_id, user_type, *args, **kwargs)
        
            else:
                return jsonify({'message': 'You must be logged in to access this.'}), 400
        
        return decorated
    
    return decorator  
            
                
            
            
            
            