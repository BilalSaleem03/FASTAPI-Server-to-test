


@app.route('/api/flask-apis', methods=['GET'])
@authenticate_request
def get_users():
    users = [{'id': 1, 'name': 'John'}, {'id': 2, 'name': 'Jane'}]
    return get_user()

# 2. POST route - Create a new user
@app.route('/api/flask-apis', methods=['POST'])
def create_user():
    data = request.get_json()
    name = data.get('name')
    return create_user_controller(name)

# 3. GET route - Fetch specific user by ID
@app.route('/api/flask-apis/<int:user_id>', methods=['GET'])
def get_user(user_id):
    return get_user_controller(user_id)

# 4. DELETE route - Delete a user
@app.route('/api/flask-apis/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    return jsonify({'message': f'User {user_id} deleted'}), 200