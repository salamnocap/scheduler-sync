# scheduler-sync
## scheduler-sync is a tool designed for automating data collection from OPC UA and PLC servers

### Docker Build for scheduler-sync Image
```bash
docker build -t scheduler-sync .
```

### Docker Compose Up for Application Deployment
```bash
docker compose up
```

### Database Migration with Alembic
```bash
docker exec scheduler-sync-api-1 alembic upgrade head
```
These instructions walk you through creating the Docker image, launching the application using Docker Compose, 
and performing essential database migration via Alembic. 

Follow these steps in order to successfully set up and initialize the scheduler-sync app, 
and access the Swagger UI for the application API at ```localhost:8082/docs.```
