# FlyRank AI Internship · AI Backend Engineer

Welcome to the backend engineering projects for FlyRank Internship.

## Project Structure

This repository contains the sequential progression from an in-memory CRUD API to a persistent containerized architecture:

- 📁 **[`01-crud-api/`](./01-crud-api)**: **Assignment A1 — Build your first CRUD API**  
  FastAPI application using in-memory state, input validation, and REST conventions.
- 📁 **[`02-connect-crud-to-db/`](./02-connect-crud-to-db)**: **Assignment A2 — Connecting your CRUD to the database**  
  FastAPI application backed by a persistent SQLite database (`tasks.db`) with parameterized SQL queries, automated table creation, idempotent seeding, and restart survival.
- 📁 **[`03-containerize-stack/`](./03-containerize-stack)**: **Assignment A3 — Containerize your stack**  
  FastAPI application connected to a containerized PostgreSQL database with Docker Compose, environment secrets (`.env`), and persistent volume storage.
- 📁 **[`04-auth-login-protect/`](./04-auth-login-protect)**: **Assignment A4 — Auth: Login & Protect**  
  Secure FastAPI authentication service using Supabase Auth (Sign Up, Log In, Log Out, JWT verification, protected route dependencies, and Swagger bearer auth).
- 📁 **[`05-polite-scraper/`](./05-polite-scraper)**: **Assignment A5 (A9) — The Polite Scraper**  
  Polite, robust web scraping pipeline targeting Books to Scrape using Requests, BeautifulSoup, and Pydantic with caching, rate limiting, and failure reporting.

---
