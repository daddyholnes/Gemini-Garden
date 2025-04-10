# Docker Setup Guide for Gemini Garden

This guide explains how to run the Gemini Garden application using Docker and Docker Compose.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Configuration

1. Make sure you have the following files in your project root:
   - `Dockerfile` - Main container configuration
   - `docker-compose.yml` - Multi-container setup
   - `.env` - Environment variables (update with your actual API keys)
   - `.dockerignore` - Files to exclude from the Docker build

2. Update the `.env` file with your actual API keys and configuration values.

## Building and Running

### Method 1: Using Docker Compose (Recommended)

This method starts both the application and database containers:

```bash
# Build and start all services
docker-compose up --build

# Run in detached mode (background)
docker-compose up --build -d

# View logs when running in detached mode
docker-compose logs -f
```

Access your application at: http://localhost:8501

### Method 2: Using Docker Directly

If you only want to run the application container without the database:

```bash
# Build the Docker image
docker build -t gemini-garden .

# Run the container
docker run -d -p 8501:8501 --name gemini-app gemini-garden
```

Access your application at: http://localhost:8501

## Development with Live Updates

The Docker Compose configuration includes volume mapping, which means changes to your local code will be reflected in the container. This is ideal for development purposes.

## Managing Containers

```bash
# Stop all containers
docker-compose down

# Stop and remove volumes (data will be lost)
docker-compose down -v

# View running containers
docker-compose ps

# Restart a specific service
docker-compose restart app
```

## Database Access

The PostgreSQL database is available at:

- Host: `localhost` (from your machine) or `db` (from within the app container)
- Port: `5432`
- Username: Value from `POSTGRES_USER` in .env
- Password: Value from `POSTGRES_PASSWORD` in .env
- Database: Value from `POSTGRES_DB` in .env

You can connect to the database with tools like pgAdmin or using the command line:

```bash
# Connect from your local machine
docker-compose exec db psql -U user -d gemini_db

# Replace "user" and "gemini_db" with your values from .env
```

## Troubleshooting

1. **Port conflicts**: If port 8501 is already in use, change it in the docker-compose.yml file.

2. **Environment variables**: Make sure all required environment variables are set in the .env file.

3. **Permission issues**: If you encounter permission issues with the database volume, use:
   ```bash
   sudo chown -R 1000:1000 ./postgres_data
   ```

4. **Logs**: Check container logs for errors:
   ```bash
   docker-compose logs -f app
   ```

## Backup and Restore

### Backing up the database

```bash
docker-compose exec -T db pg_dump -U user gemini_db > backup.sql
```

### Restoring the database

```bash
cat backup.sql | docker-compose exec -T db psql -U user -d gemini_db
```