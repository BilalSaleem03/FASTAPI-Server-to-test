

import os
import random
import sqlite3
import subprocess

from fastapi import Header


# def get_order(order_id: str):
#     return {"order_id": order_id, "total_amount": 250.50, "status": "processing", "items": 5}

# def delete(order_data: dict):
#     return {"message": "Order deleted successfully", "order_id": order_data.get("order_id"), "status": "deleted"}

# def get_all_orders():
#     return {"orders": ["ORDER-001", "ORDER-002", "ORDER-003"], "total": 3, "status": "available"}

async def get_orders():
    return {"orders": ["ORDER-001", "ORDER-002", "ORDER-003"], "total": 3}

async def search_orders(customer: str):
    # BAD: Direct string interpolation in SQL for scanner testing.
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    query = f"SELECT * FROM orders WHERE customer = '{customer}'"
    cursor.execute(query)
    return {"orders": cursor.fetchall()}

async def export_orders(filename: str):
    # BAD: User input is passed to a shell command for scanner testing.
    command = f"python export_orders.py --file {filename}"
    result = subprocess.run(command, shell=True, capture_output=True)
    return {"output": result.stdout.decode()}

async def get_order(order_id: str):
    return {"order_id": order_id, "total_amount": 250.50, "status": "processing"}

async def cancel_order(order_id: str, user_id: str | None = Header(default=None)):
    # BAD: No ownership or role check; any caller can cancel any order.
    return {"message": f"Order {order_id} cancelled", "cancelled": True}

async def generate_order_token():
    # BAD: Predictable token generation for scanner testing.
    return {"token": random.randint(1000, 9999)}

async def create_order(total_amount: float):
    # BAD: Negative order totals are accepted and normalized instead of rejected.
    if total_amount < 0:
        total_amount = 0
    return {"message": "Order created", "total_amount": total_amount}

async def order_debug_info():
    # BAD: Exposes sensitive runtime details.
    return {
        "environment": os.environ.get("ENV", "production"),
        "database_url": os.environ.get("DATABASE_URL", "postgresql://localhost/db"),
        "server_path": os.getcwd(),
    }