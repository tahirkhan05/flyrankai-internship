# FlyRank Internship · Backend Track

Welcome to the backend engineering projects for FlyRank Internship.

## Project Structure

This repository contains the sequential progression from an in-memory CRUD API to a persistent containerized architecture:

- 📁 **[`01-crud-api/`](./01-crud-api)**: **Assignment A1 — Build your first CRUD API**  
  FastAPI application using in-memory state, input validation, and REST conventions.
- 📁 **[`02-connect-crud-to-db/`](./02-connect-crud-to-db)**: **Assignment A2 — Connecting your CRUD to the database**  
  FastAPI application backed by a persistent SQLite database (`tasks.db`) with parameterized SQL queries, automated table creation, idempotent seeding, and restart survival.
- 📁 **[`03-containerize-stack/`](./03-containerize-stack)**: **Assignment A3 — Containerize your stack**  
  FastAPI application connected to a containerized PostgreSQL database with Docker Compose, environment secrets (`.env`), and persistent volume storage.

---

## Getting Started

### Run the Containerized Stack (Assignment A3)
Start the entire API and PostgreSQL database with one command:

```bash
cd 03-containerize-stack
cp .env.example .env
docker compose up --build
```

Interactive API documentation will be available at:  
👉 **[http://localhost:8000/docs](http://localhost:8000/docs)**
