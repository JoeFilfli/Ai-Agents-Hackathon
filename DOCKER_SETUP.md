# Docker Setup Guide

This guide explains how to run the AI Agents application using Docker.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- OpenAI API key

## Quick Start

### 1. Set Up Environment Variables

Create a `.env.local` file in the project root (or use your existing one):

```bash
cp env.example .env.local
```

Edit `.env.local` and add your OpenAI API key:

```env
OPENAI_API_KEY=sk-your-actual-api-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
NODE_ENV=production
LOG_LEVEL=INFO
```

**Note:** The Docker setup uses `.env.local` to keep your API key secure and separate from the example template.

### 2. Build and Start Services

Build and start both backend and frontend:

```bash
docker-compose up --build
```

For running in detached mode (background):

```bash
docker-compose up -d --build
```

### 3. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/py/docs

## Common Commands

### Start Services

```bash
# Start in foreground (see logs)
docker-compose up

# Start in background
docker-compose up -d
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### View Logs

```bash
# View all logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View specific service logs
docker-compose logs backend
docker-compose logs frontend
```

### Rebuild After Code Changes

```bash
# Rebuild and restart
docker-compose up --build

# Rebuild specific service
docker-compose build backend
docker-compose up -d backend
```

### Execute Commands Inside Containers

```bash
# Access backend container shell
docker-compose exec backend sh

# Access frontend container shell
docker-compose exec frontend sh

# Run Python commands in backend
docker-compose exec backend python -c "print('Hello')"
```

## Development vs Production

### Development Mode

For development with hot reload, you may want to:

1. Mount more volumes in `docker-compose.yml`
2. Use `--reload` flag for uvicorn
3. Use `npm run dev` instead of production build

Create `docker-compose.dev.yml`:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    command: uvicorn api.index:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - ./api:/app/api
      - ./requirements.txt:/app/requirements.txt
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
      target: deps  # Stop at deps stage
    command: npm run dev
    volumes:
      - ./app:/app/app
      - ./public:/app/public
      - ./package.json:/app/package.json
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
```

Run development mode:

```bash
docker-compose -f docker-compose.dev.yml up
```

### Production Mode

Use the standard `docker-compose.yml` for production:

```bash
docker-compose up -d
```

## Troubleshooting

### Port Already in Use

If ports 3000 or 8000 are already in use:

```bash
# Find process using port
# On Windows PowerShell:
Get-NetTCPConnection -LocalPort 3000

# On Linux/Mac:
lsof -i :3000

# Kill the process or change port in docker-compose.yml
```

### Backend Health Check Failing

Check backend logs:

```bash
docker-compose logs backend
```

Common issues:
- Missing OpenAI API key
- Invalid API key format
- Network connectivity issues

### Frontend Can't Connect to Backend

Verify:
1. Backend is healthy: `docker-compose ps`
2. Backend URL is correct in frontend environment
3. Both services are on same network

### Build Fails

Clean and rebuild:

```bash
# Remove all containers and images
docker-compose down --rmi all

# Remove volumes
docker-compose down -v

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up
```

## Performance Tips

### Reduce Image Size

- Use multi-stage builds (already implemented)
- Minimize layers in Dockerfile
- Use `.dockerignore` to exclude unnecessary files

### Speed Up Builds

- Order Dockerfile commands from least to most frequently changing
- Use layer caching effectively
- Consider using Docker BuildKit

### Optimize Runtime

- Use health checks to ensure service availability
- Set appropriate restart policies
- Monitor resource usage: `docker stats`

## Security Best Practices

1. **Never commit `.env.local` file**
   - Always use `env.example` as template
   - `.env.local` is already in `.gitignore`
   
2. **Use secrets for sensitive data**
   ```bash
   echo "my-api-key" | docker secret create openai_key -
   ```

3. **Run containers as non-root**
   - Frontend Dockerfile already uses `nextjs` user
   
4. **Keep images updated**
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

5. **Scan for vulnerabilities**
   ```bash
   docker scan ai-agents-backend
   ```

## Cleaning Up

Remove all Docker resources:

```bash
# Stop and remove containers
docker-compose down

# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove everything (use with caution!)
docker system prune -a --volumes
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Next.js Docker Documentation](https://nextjs.org/docs/deployment#docker-image)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/docker/)

