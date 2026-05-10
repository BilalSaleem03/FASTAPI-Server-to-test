from fastapi import FastAPI, HTTPException, Request, Response, Cookie, Header, Depends
from fastapi.responses import JSONResponse
from typing import Optional, List
import hashlib
import subprocess
import pickle
import base64
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, urljoin
import requests
import jwt
import os
import random

app = FastAPI()

# Fake database
products_db = {}
users_db = {}
API_KEY = "sk_live_4eC39HqLyjWDarjtT1zdp7dc"  # Hardcoded secret

# ============================================================
# CRITICAL VULNERABILITIES (ERROR level in Semgrep)
# ============================================================

# 1. SQL Injection (CWE-89) - CRITICAL
@app.get("/products/sql-injection")
async def get_products_sqli(category: str):
    # BAD: Direct string concatenation in SQL
    import sqlite3
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    query = f"SELECT * FROM products WHERE category = '{category}'"
    cursor.execute(query)  # SQL Injection vulnerability
    return {"products": cursor.fetchall()}

# 2. Command Injection (CWE-78) - CRITICAL
@app.post("/products/export")
async def export_products(filename: str):
    # BAD: User input directly in system command
    command = f"python export.py --file {filename}"
    result = subprocess.run(command, shell=True, capture_output=True)  # Command injection
    return {"output": result.stdout.decode()}

# 3. Hardcoded JWT Secret (CWE-798) - CRITICAL
SECRET_KEY = "supersecretkey123456789"  # Hardcoded secret

@app.post("/login")
async def login(username: str, password: str):
    # BAD: Hardcoded secret key
    token = jwt.encode({"user": username, "role": "admin"}, SECRET_KEY, algorithm="HS256")
    return {"token": token}

# 4. Insecure Deserialization (CWE-502) - CRITICAL
@app.post("/products/load-config")
async def load_config(config_data: str):
    # BAD: Pickle deserialization from user input
    config_bytes = base64.b64decode(config_data)
    config = pickle.loads(config_bytes)  # Remote code execution vulnerability
    return {"config": config}

# 5. XML External Entity (CWE-611) - CRITICAL
@app.post("/products/parse-xml")
async def parse_product_xml(xml_data: str):
    # BAD: XXE vulnerability
    root = ET.fromstring(xml_data)  # XXE vulnerability
    return {"parsed": root.tag}

# ============================================================
# HIGH VULNERABILITIES (WARNING level in Semgrep)
# ============================================================

# 6. Path Traversal (CWE-22) - HIGH
@app.get("/products/download/{filename}")
async def download_product_file(filename: str):
    # BAD: No path sanitization
    filepath = f"./static/products/{filename}"
    with open(filepath, 'rb') as f:  # Path traversal vulnerability
        content = f.read()
    return Response(content=content)

# 7. Hard-coded Password in Code (CWE-259) - HIGH
DEFAULT_PASSWORD = "admin123"  # Hardcoded password

@app.post("/admin/reset-password")
async def reset_admin_password(user_id: int):
    # BAD: Using hardcoded default password
    users_db[user_id] = {"password": DEFAULT_PASSWORD}
    return {"message": "Password reset to default"}

# 8. Weak Cryptographic Hash (CWE-327) - HIGH
@app.post("/register")
async def register_user(username: str, password: str):
    # BAD: MD5 is weak
    hashed = hashlib.md5(password.encode()).hexdigest()
    users_db[username] = {"password": hashed}
    return {"message": "User registered", "hash": hashed}

# 9. Server-Side Request Forgery (CWE-918) - HIGH
@app.post("/products/fetch-image")
async def fetch_product_image(url: str):
    # BAD: No URL validation, SSRF vulnerability
    response = requests.get(url)  # SSRF vulnerability
    return {"content": response.text[:100]}

# 10. Open Redirect (CWE-601) - HIGH
@app.get("/products/redirect")
async def redirect_to_product(return_url: str):
    # BAD: No validation of redirect URL
    return RedirectResponse(url=return_url)  # Open redirect

# ============================================================
# MEDIUM VULNERABILITIES (INFO level in Semgrep)
# ============================================================

# 11. Sensitive Data Exposure in Logs (CWE-200) - MEDIUM
@app.post("/products/update-price")
async def update_product_price(product_id: int, price: float, api_key: str):
    # BAD: Logging sensitive information
    print(f"API Key received: {api_key}")  # Sensitive data in logs
    
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    products_db[product_id] = {"price": price}
    return {"message": "Price updated"}

# 12. Improper Authorization (CWE-285) - MEDIUM
@app.delete("/products/{product_id}")
async def delete_product(product_id: int, user_role: str = Header(None)):
    # BAD: No proper authorization check
    # Should check if user is admin
    if product_id in products_db:
        del products_db[product_id]
        return {"message": "Product deleted"}
    raise HTTPException(status_code=404)

# 13. Use of Insufficiently Random Values (CWE-330) - MEDIUM
@app.get("/products/generate-token")
async def generate_product_token():
    # BAD: Weak random number generator
    token = random.randint(1000, 9999)  # Predictable token
    return {"token": token}

# 14. Information Disclosure (CWE-200) - MEDIUM
@app.get("/debug/info")
async def debug_info():
    # BAD: Exposing sensitive system information
    return {
        "python_version": os.sys.version,
        "environment": os.environ.get("ENV", "production"),
        "database_url": os.environ.get("DATABASE_URL", "postgresql://localhost/db"),
        "server_path": os.getcwd()
    }

# 15. Insecure HTTP Headers (Missing security headers) - MEDIUM
@app.get("/products")
async def list_products():
    # BAD: No security headers
    response = JSONResponse({"products": list(products_db.keys())})
    # Missing: X-Frame-Options, X-Content-Type-Options, CSP
    return response

# ============================================================
# LOW VULNERABILITIES (default/INFO level)
# ============================================================

# 16. Use of `eval()` on User Input (Low)
@app.post("/products/calculate")
async def calculate_price(expression: str):
    # BAD: eval on user input
    result = eval(expression)  # Code injection but limited impact
    return {"result": result}

# 17. Weak Password Policy (Low)
@app.post("/users/change-password")
async def change_password(username: str, new_password: str):
    # BAD: No password strength validation
    users_db[username]["password"] = new_password
    return {"message": "Password changed"}

# 18. Missing Rate Limiting (Low)
@app.post("/products/review")
async def add_review(product_id: int, review: str):
    # BAD: No rate limiting, allows spam
    return {"message": "Review added"}

# 19. Missing Input Validation (Low)
@app.post("/products/create")
async def create_product(name: str, price: float):
    # BAD: No input validation for price
    if price < 0:
        price = 0  # Just sets to 0 instead of rejecting
    products_db[name] = {"price": price}
    return {"message": "Product created"}

# 20. Debug Mode Enabled in Production (Low)
if __name__ == "__main__":
    import uvicorn
    # BAD: Debug mode enabled
    uvicorn.run(app, host="0.0.0.0", port=8000, debug=True)