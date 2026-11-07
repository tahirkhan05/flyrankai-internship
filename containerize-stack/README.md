# Containerized Task API (PostgreSQL + Docker Compose)

FlyRank Internship Backend Track · Week 1 · Assignment A3

A complete containerized RESTful Task CRUD API running against a real **PostgreSQL** database inside Docker, managed via **Docker Compose** and configured with environment secrets.

---

## 1. What This Is

This is the containerized sequel to Assignment 1 and Assignment 2:
- **Assignment 1**: In-memory list (data lost on restart).
- **Assignment 2**: Embedded SQLite file `tasks.db` on disk.
- **Assignment 3 (This project)**: Professional PostgreSQL database server running in an isolated Docker container with named persistent volume storage (`taskdata`).

The entire multi-container architecture (API service + PostgreSQL database) boots with a single command.

---

## 2. One Command to Run Everything

```bash
docker compose up
```

*(Add `-d` to run in the background: `docker compose up -d`)*

The API is instantly reachable at:  
👉 **`http://localhost:8000`**  
Interactive Swagger documentation:  
👉 **`http://localhost:8000/docs`**

---

## 3. Environment Variables & Secrets

All database credentials are decoupled from application code and read from the environment.

* **Production / Local Secret**: `.env` *(Git-ignored for security)*
* **Committed Template**: `.env.example`

### Variables (`.env.example`)
```env
DATABASE_URL=postgresql://postgres:dev@localhost:5432/tasks
```
*(Inside the Docker Compose internal network, the API automatically connects to the service hostname `db:5432`).*

---

## 4. API Endpoints

All database interactions use **parameterized SQL queries** (`%s` placeholders in `psycopg`) to prevent SQL injection vulnerabilities.

| Method | Endpoint | Description | Parameterized SQL Query | Status Codes |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/` | API discovery & metadata | None | `200 OK` |
| `GET` | `/health` | Server health check | None | `200 OK` |
| `GET` | `/tasks` | List all tasks | `SELECT id, title, done FROM tasks` | `200 OK` |
| `GET` | `/tasks/{id}` | Retrieve single task | `SELECT id, title, done FROM tasks WHERE id = %s` | `200 OK`, `404 Not Found` |
| `POST` | `/tasks` | Create task | `INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id, title, done` | `201 Created`, `400 Bad Request` |
| `PUT` | `/tasks/{id}` | Update task | `UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING id, title, done` | `200 OK`, `400 Bad Request`, `404 Not Found` |
| `DELETE` | `/tasks/{id}` | Delete task | `DELETE FROM tasks WHERE id = %s` | `204 No Content`, `404 Not Found` |

---

## 5. Sample `curl -i` Verification

### Task Creation (`POST /tasks`)
```http
HTTP/1.1 201 Created
date: Sat, 07 Nov 2026 19:52:53 GMT
server: uvicorn
content-length: 63
content-type: application/json

{"id":4,"title":"Docker Compose Persistence Test","done":false}
```

### Fetch All Tasks (`GET /tasks`)
```http
HTTP/1.1 200 OK
date: Sat, 07 Nov 2026 19:53:20 GMT
server: uvicorn
content-length: 219
content-type: application/json

[
  {"id":1,"title":"Set up project","done":true},
  {"id":2,"title":"Build Stage 2 endpoints","done":false},
  {"id":3,"title":"Write documentation","done":false},
  {"id":4,"title":"Docker Compose Persistence Test","done":false}
]
```

---

## 6. Database Verification in Container (`psql`)

Inspecting the relations and data directly inside the PostgreSQL container:

```bash
docker exec containerize-stack-db-1 psql -U postgres -d tasks -c "\dt"
```
```text
         List of relations
 Schema | Name  | Type  |  Owner   
--------+-------+-------+----------
 public | tasks | table | postgres
(1 row)
```

```bash
docker exec containerize-stack-db-1 psql -U postgres -d tasks -c "SELECT * FROM tasks;"
```
```text
 id |              title              | done 
----+---------------------------------+------
  1 | Set up project                  | t
  2 | Build Stage 2 endpoints         | f
  3 | Write documentation             | f
  4 | Docker Compose Persistence Test | f
(4 rows)
```

![Database Verification Screenshot](db_screenshot.png)

---

## 7. Persistence Across Full-Stack Restart

Data is persisted on disk via the Docker named volume `taskdata`:
1. Start stack and insert data: `docker compose up -d`
2. Destroy containers and network: `docker compose down`
3. Restart stack: `docker compose up -d`
4. Fetch tasks: `curl http://localhost:8000/tasks` -> **All records persist intact.**

---

## 8. Clean Clone Instructions

A collaborator cloning this repository can run the whole stack in under 2 minutes:

```bash
cd containerize-stack
cp .env.example .env
docker compose up --build
```
The database table is created automatically, starter tasks are seeded on first run, and the API is immediately live.
