# opc-pro-scheduler
---
## opc-pro-scheduler is a simple scheduler for OPC UA servers.

### Docker build opc-pro-scheduler image
```bash
docker build -t opc-pro-scheduler .
```

### Docker compose up
```bash
docker compose up
```

### Do migration for database
```bash
docker exec opc-pro-scheduler-api-1 alembic upgrade head
```
