# opc-pro-scheduler
---
## opc-pro-scheduler is a tool designed for automating data collection from OPC UA and PLC servers

### Docker Build for opc-pro-scheduler Image
```bash
docker build -t opc-pro-scheduler .
```

### Docker Compose Up for Application Deployment
```bash
docker compose up
```

### Database Migration with Alembic
```bash
docker exec opc-pro-scheduler-api-1 alembic upgrade head
```
These instructions walk you through creating the Docker image, launching the application using Docker Compose, 
and performing essential database migration via Alembic. 

Follow these steps in order to successfully set up and initialize the OPC-PRO-Scheduler app, 
and access the Swagger UI for the application API at ```localhost:8082/docs.```