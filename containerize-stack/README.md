# Containerized Task API (PostgreSQL + Docker)

FlyRank Internship Backend Track · Week 1 · Assignment A3

Running our Task API against a real PostgreSQL database inside a Docker container, managed via Docker Compose and configured with environment secrets.

---

## Stage 0: Running PostgreSQL in Docker

Start the PostgreSQL database server in a container with a persistent data volume:

```powershell
docker run --name taskdb -e POSTGRES_PASSWORD=dev -e POSTGRES_DB=tasks -p 5432:5432 -v taskdata:/var/lib/postgresql/data -d postgres
```

### Verification Commands
```powershell
# Verify container is running
docker ps

# Inspect SQL prompt inside container
docker exec -it taskdb psql -U postgres -d tasks
```

