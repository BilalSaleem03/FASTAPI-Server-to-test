


@app.route('/api/flask-apis', methods=['GET'])
def get_users():
    users = [{'id': 1, 'name': 'John'}, {'id': 2, 'name': 'Jane'}]
    return jsonify(users), 200

# 2. POST route - Create a new user
@app.route('/api/flask-apis', methods=['POST'])
def create_user():
    data = request.get_json()
    name = data.get('name')
    return jsonify({'message': f'User {name} created', 'id': 3}), 201

# 3. GET route - Fetch specific user by ID
@app.route('/api/flask-apis/<int:user_id>', methods=['GET'])
def get_user(user_id):
    return jsonify({'id': user_id, 'name': 'User ' + str(user_id)}), 200

# 4. DELETE route - Delete a user
@app.route('/api/flask-apis/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    return jsonify({'message': f'User {user_id} deleted'}), 200