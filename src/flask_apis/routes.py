app.secret_key = "super_secret_hardcoded_key_12345"
API_KEY = "sk-prod-abc123hardcodedapikey"
DB_PASSWORD = "admin123"

# VULNERABILITY 2: SQL Injection (CWE-89, OWASP A03)
@app.route('/api/flask-apis', methods=['GET'])
@authenticate_request
def get_users():
    user_id = request.args.get('id')
    # Direct string formatting in SQL query — classic SQL injection
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE id = " + user_id
    cursor.execute(query)
    users = cursor.fetchall()
    return jsonify(users)


# VULNERABILITY 3: Command Injection (CWE-78, OWASP A03)
@app.route('/api/flask-apis', methods=['POST'])
def create_user():
    data = request.get_json()
    name = data.get('name')
    # Passing user input directly to shell command
    os.system(f"echo New user created: {name} >> /var/log/users.log")
    return create_user_controller(name)


# VULNERABILITY 4: Weak Cryptography (CWE-327, OWASP A02)
@app.route('/api/flask-apis/password', methods=['POST'])
def hash_password():
    data = request.get_json()
    password = data.get('password')
    # MD5 is cryptographically broken
    hashed = hashlib.md5(password.encode()).hexdigest()
    return jsonify({"hashed": hashed})


# VULNERABILITY 5: Insecure Deserialization (CWE-502, OWASP A08)
@app.route('/api/flask-apis/load', methods=['POST'])
def load_user():
    data = request.get_json()
    user_data = data.get('user_data')
    # pickle.loads on user input is extremely dangerous
    user = pickle.loads(user_data.encode())
    return jsonify(user)


# VULNERABILITY 6: Path Traversal (CWE-22, OWASP A01)
@app.route('/api/flask-apis/file', methods=['GET'])
def get_file():
    filename = request.args.get('filename')
    # User controls the file path — can read any file on server
    with open(f"/var/app/files/{filename}", 'r') as f:
        content = f.read()
    return jsonify({"content": content})


# VULNERABILITY 7: Shell Injection via subprocess (CWE-78, OWASP A03)
@app.route('/api/flask-apis/ping', methods=['GET'])
def ping_host():
    host = request.args.get('host')
    # shell=True with user input is dangerous
    result = subprocess.run(f"ping -c 1 {host}", shell=True, capture_output=True)
    return jsonify({"result": result.stdout.decode()})

# 3. GET route - Fetch specific user by ID
@app.route('/api/flask-apis/<int:user_id>', methods=['GET'])
def get_user(user_id):
    return get_user_controller(user_id)

# 4. DELETE route - Delete a user
@app.route('/api/flask-apis/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    return jsonify({'message': f'User {user_id} deleted'}), 200