"""Demo users. DEVELOPMENT CREDENTIALS ONLY - replace before any real deployment.

Passwords are listed in plain text here on purpose (they are public demo
credentials); the user repository stores only their bcrypt hashes.
"""

USERS = [
    {"id": "U001", "username": "admin", "password": "admin123", "full_name": "Alex Morgan",
     "email": "admin@intellierp.example", "role": "ADMIN"},
    {"id": "U002", "username": "inventory", "password": "inventory123", "full_name": "Priya Nair",
     "email": "inventory@intellierp.example", "role": "INVENTORY_MANAGER"},
    {"id": "U003", "username": "procurement", "password": "procurement123", "full_name": "Daniel Reyes",
     "email": "procurement@intellierp.example", "role": "PROCUREMENT_MANAGER"},
    {"id": "U004", "username": "employee", "password": "employee123", "full_name": "Sam Carter",
     "email": "employee@intellierp.example", "role": "EMPLOYEE"},
]
