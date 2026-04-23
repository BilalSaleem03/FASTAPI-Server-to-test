# from fastapi import APIRouter
# from user.controllers import get_user, create_user, get_all_users

# router = APIRouter()

# user_routes = APIRouter(prefix="/user")

# @user_routes.get("/")
# async def get_all_users():
#     return get_all_users()

# @user_routes.get("/{user_id}")
# async def get_user(user_id: int):
#     return get_user(user_id)

# @user_routes.post("/")
# async def create_user():
#     return create_user()
from fastapi import APIRouter
from src.user.controllers import get_users, get_user, create_user


user_routes = APIRouter(prefix="/api/users", tags=["Users"])

user_routes.get("/")(get_users)
user_routes.get("/{user_id}")(get_user)
user_routes.post("/")(create_user)