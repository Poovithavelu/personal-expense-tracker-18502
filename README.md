# Project Repository

This repository contains a fullstack personal expense tracker.

Backend (Flask):
- REST API: /expenses, /categories, /export
- Swagger UI/OpenAPI at /docs
- Uses MySQL via environment variables:
  - MYSQL_URL, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, MYSQL_PORT
- See expense_tracker_backend/.env.example for variables

Run backend locally:
1) Configure environment variables.
2) pip install -r expense_tracker_backend/requirements.txt
3) cd expense_tracker_backend && python run.py

The backend will attempt to initialize schema automatically (tables: categories, expenses).