

# def get_user(user_id: int):
#     return {"user_id": user_id, "name": "John Doe"}

# def create_user(user_data: dict):
#     return {"message": "User created successfully", "user_id": 123, "status": "created"}

# def get_all_users():
#     return {"users": ["Alice", "Bob", "Charlie"], "count": 3}

async def get_users():
    return {"users": ["Alice", "Bob", "Charlie"], "count": 3}

async def get_user(user_id: int):
    return {"user_id": user_id, "name": f"User {user_id}", "email": f"user{user_id}@example.com"}

async def create_user():
    return {"message": "User created successfully", "user_id": 123, "status": "created"}