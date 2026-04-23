

def authenticate_request(f):
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or auth_header != 'Bearer mysecrettoken':
            return jsonify({'message': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return wrapper