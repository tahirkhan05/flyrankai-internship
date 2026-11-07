# FlyRank Internship · Backend Track

Welcome to the backend engineering projects for FlyRank Internship.

## Project Structure

This repository contains the sequential progression from an in-memory CRUD API to a persistent database-backed architecture:

- 📁 **[`crud-api/`](./crud-api)**: **Assignment A1 — Build your first CRUD API**  
  FastAPI application using in-memory state, input validation, and REST conventions.
- 📁 **[`connect-crud-to-db/`](./connect-crud-to-db)**: **Assignment A2 — Connecting your CRUD to the database**  
  FastAPI application backed by a persistent SQLite database (`tasks.db`) with parameterized SQL queries, automated table creation, idempotent seeding, and restart survival.
- 📁 **[`containerize-stack/`](./containerize-stack)**: **Assignment A3 — Containerize your stack**  
  FastAPI application connected to a containerized PostgreSQL database with Docker Compose, environment secrets (`.env`), and persistent volume storage.

---

## Getting Started

### Run the Containerized Stack (Assignment A3)
Start the entire API and PostgreSQL database with one command:

```bash
cd containerize-stack
cp .env.example .env
docker compose up --build
```

Interactive API documentation will be available at:  
👉 **[http://localhost:8000/docs](http://localhost:8000/docs)**

