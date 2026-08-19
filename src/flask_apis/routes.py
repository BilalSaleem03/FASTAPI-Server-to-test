from fastapi import APIRouter, Body, Query
from fastapi.responses import PlainTextResponse

flask_routes = APIRouter(tags=["Recon test endpoints"])


@flask_routes.get("/api/flask-apis")
async def flask_api_users(id: str | None = Query(default=None)):
    return {"users": [{"id": id or "1", "name": "Bilal"}]}


@flask_routes.post("/api/flask-apis")
async def flask_api_create_user(data: dict = Body(default_factory=dict)):
    return {"message": "User created", "name": data.get("name")}


@flask_routes.post("/login")
async def login(data: dict = Body(default_factory=dict)):
    return {"success": True, "username": data.get("username")}


@flask_routes.get("/api/flask-apis/{user_id}")
async def flask_api_user(user_id: int):
    return {"user_id": user_id, "name": f"User {user_id}"}


@flask_routes.delete("/api/flask-apis/{user_id}")
async def flask_api_delete_user(user_id: int):
    return {"message": f"User {user_id} deleted"}


@flask_routes.get("/.env", response_class=PlainTextResponse)
async def exposed_env():
    return (
        "DATABASE_URL=postgresql://postgres:secret123@localhost:5432/production_db\n"
        "JWT_SECRET=super_secret_jwt_key_9999\n"
        "STRIPE_API_KEY=sk_live_51OzTestingFakeKey123456\n"
        "DEBUG=True\n"
    )


@flask_routes.get("/.git/HEAD", response_class=PlainTextResponse)
async def exposed_git_head():
    return "ref: refs/heads/main\n"


@flask_routes.get("/swagger.json")
async def exposed_swagger():
    return {
        "swagger": "2.0",
        "info": {"title": "Internal Admin API", "version": "1.0"},
        "paths": {"/admin/debug": {"get": {"description": "Internal diagnostics"}}},
    }


@flask_routes.get("/actuator/health")
async def exposed_actuator():
    return {
        "status": "UP",
        "components": {
            "db": {"status": "UP", "details": {"database": "PostgreSQL"}},
            "redis": {"status": "UP"},
        },
    }