# Docker Quick Start Guide

Get your full-stack AI Agents application running with Docker in minutes!

## Prerequisites

1. Install Docker Desktop:
   - **Windows/Mac**: [Docker Desktop](https://www.docker.com/products/docker-desktop/)
   - **Linux**: [Docker Engine](https://docs.docker.com/engine/install/)

2. Get an OpenAI API key from [OpenAI Platform](https://platform.openai.com/api-keys)

## Quick Start (3 Steps)

### Step 1: Set Your API Key

Create a `.env.local` file in the project root (or use your existing one):

```bash
cp env.example .env.local
```

Edit `.env.local` and add your OpenAI API key:

```env
OPENAI_API_KEY=sk-your-actual-key-here
```

**Note:** If you already have `.env.local` with your API key, you're all set! The Docker setup will use it automatically.

### Step 2: Start the Application

**Windows:**
```bash
docker-start.bat
```

**Linux/Mac:**
```bash
chmod +x docker-start.sh
./docker-start.sh
```

**Or manually:**
```bash
docker-compose up --build
```

### Step 3: Access Your App

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/py/docs

That's it! 🎉

## Common Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose up --build

# Restart specific service
docker-compose restart backend

# View running containers
docker-compose ps
```

## Architecture

```
┌─────────────────────────────────────────┐
│  Docker Host                            │
│                                         │
│  ┌──────────────┐    ┌──────────────┐  │
│  │  Frontend    │    │   Backend    │  │
│  │  (Next.js)   │───▶│  (FastAPI)   │  │
│  │  Port 3000   │    │  Port 8000   │  │
│  └──────────────┘    └──────────────┘  │
│         │                    │          │
│         └────────┬───────────┘          │
│                  │                      │
│         ┌────────▼─────────┐            │
│         │  Docker Network  │            │
│         └──────────────────┘            │
└─────────────────────────────────────────┘
```

## Troubleshooting

### Port Conflicts

If ports are in use, stop conflicting services:

```powershell
# Windows PowerShell - Find what's using port 3000
Get-NetTCPConnection -LocalPort 3000

# Linux/Mac
lsof -i :3000
```

### Backend Health Check Fails

Check logs for errors:

```bash
docker-compose logs backend
```

Common causes:
- Missing or invalid OpenAI API key
- Network connectivity issues

### Can't Connect to Backend from Frontend

Ensure both services are running:

```bash
docker-compose ps
```

Both should show status as "Up" and healthy.

### Clean Rebuild

If something goes wrong:

```bash
# Stop and remove everything
docker-compose down -v

# Remove old images
docker-compose build --no-cache

# Start fresh
docker-compose up
```

## Development Mode

For development with hot reload, edit volumes in `docker-compose.yml`:

```yaml
backend:
  command: uvicorn api.index:app --host 0.0.0.0 --port 8000 --reload
  volumes:
    - ./api:/app/api  # This enables hot reload
```

## Production Deployment

For production, consider:

1. Use environment-specific compose files
2. Set up proper secrets management
3. Configure reverse proxy (nginx/traefik)
4. Enable HTTPS
5. Set resource limits
6. Configure proper logging

See [DOCKER_SETUP.md](DOCKER_SETUP.md) for detailed production setup.

## Need Help?

- Full documentation: [DOCKER_SETUP.md](DOCKER_SETUP.md)
- Docker docs: https://docs.docker.com/
- Next.js deployment: https://nextjs.org/docs/deployment
- FastAPI deployment: https://fastapi.tiangolo.com/deployment/

## File Structure

```
your-project/
├── Dockerfile.backend          # Backend container definition
├── Dockerfile.frontend         # Frontend container definition
├── docker-compose.yml          # Orchestration configuration
├── .dockerignore              # Files to exclude from build
├── .env                       # Your environment variables
├── docker-start.sh            # Linux/Mac startup script
├── docker-start.bat           # Windows startup script
├── DOCKER_QUICKSTART.md       # This file
└── DOCKER_SETUP.md           # Detailed documentation
```

## What Gets Containerized?

**Backend Container:**
- Python 3.11
- FastAPI + Uvicorn
- All Python dependencies from requirements.txt
- Your API code from `api/` folder
- Runs on port 8000

**Frontend Container:**
- Node.js 18
- Next.js production build
- React application
- All Node dependencies
- Runs on port 3000

Both containers communicate through a Docker network named `ai-agents-network`.

---

**Ready to start?** Run `docker-start.bat` (Windows) or `./docker-start.sh` (Linux/Mac) and you're good to go! 🚀

