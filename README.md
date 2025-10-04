<p align="center">
  <h1 align="center">AI Agents - Knowledge Graph Generator</h1>
</p>

<p align="center">An intelligent knowledge graph application that transforms text into interactive visual mindmaps using AI-powered concept extraction.</p>

<br/>

## Introduction

This is a full-stack AI application built with Next.js 14 and Python FastAPI. It analyzes text input (typed or uploaded files) and automatically extracts concepts, relationships, and generates an interactive knowledge graph visualization.

## Features

- **AI-Powered Concept Extraction**: Uses OpenAI to identify key concepts and their relationships
- **Interactive Knowledge Graphs**: Visual mindmap with drag-and-drop nodes and relationship edges
- **File Upload Support**: Process text from PDF, image (OCR), and text files
- **Real-time Processing**: Live progress updates during text analysis
- **Chat Interface**: Query your knowledge graph with natural language
- **Responsive UI**: Modern interface built with Next.js 14 and TailwindCSS

## How It Works

The Python/FastAPI backend provides AI-powered text processing endpoints at `/api/py/`.

This is implemented using [`next.config.js` rewrites](https://github.com/digitros/nextjs-fastapi/blob/main/next.config.js) to map any request to `/api/py/:path*` to the FastAPI server running on port 8000.

**Architecture:**
1. User inputs text or uploads a file
2. Backend extracts text (with OCR for images)
3. OpenAI analyzes text to extract concepts and relationships
4. Frontend renders interactive knowledge graph using force-directed layout
5. Users can query the graph via chat interface

## Quick Start with Docker

The fastest way to get started:

**Windows:**
```bash
docker-start.bat
```

**Linux/Mac:**
```bash
chmod +x docker-start.sh
./docker-start.sh
```

See [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md) for detailed Docker setup.

## Getting Started

### Quick Start (Recommended)

**1. Install Dependencies**
```bash
# Install Node dependencies
npm install

# Install Python dependencies
pip install -r requirements.txt
```

**2. Set up OpenAI API Key**
```bash
# Create .env.local file
cp env.example .env.local

# Edit .env.local and add your key:
OPENAI_API_KEY=sk-...
```

**3. Start Backend with Extended Timeouts**
```bash
# Use the optimized startup script (handles long processing times)
python start_backend.py
```

**4. Start Frontend (in a new terminal)**
```bash
npm run dev
```

**5. Open Your Browser**
- Frontend: [http://localhost:3000](http://localhost:3000)
- API Docs: [http://127.0.0.1:8000/api/py/docs](http://127.0.0.1:8000/api/py/docs)

### Alternative Setup (Standard)

First, create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Then, install the dependencies:

```bash
npm install
pip install -r requirements.txt
```

Then, run the development server:

```bash
npm run dev
```

⚠️ **Note**: For unlimited concept extraction, use `python start_backend.py` instead to avoid timeouts.

The FastApi server will be running on [http://127.0.0.1:8000](http://127.0.0.1:8000) – feel free to change the port in `package.json` (you'll also need to update it in `next.config.js`).

### Processing Time Expectations

The app uses AI-powered concept extraction which takes time:
- **Short texts (100-1500 chars)**: 10-30 seconds
- **Medium texts (1500-3000 chars)**: 30-60 seconds  
- **Long texts (3000+ chars)**: 60-180 seconds

Watch the backend console for real-time progress updates!

## Project Structure

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed information about the codebase organization.

```
Ai_Agents/
├── api/                    # FastAPI Backend
│   ├── models/            # Pydantic data models
│   ├── services/          # Business logic (text processing, graph, LLM)
│   ├── tests/             # Backend test suite
│   └── index.py           # Main API endpoints
├── app/                   # Next.js Frontend
│   ├── components/        # React components (Mindmap, Chat, SidePanel)
│   ├── store/             # State management
│   └── types/             # TypeScript interfaces
├── requirements.txt       # Python dependencies
├── package.json          # Node.js dependencies
└── docker-compose.yml    # Docker orchestration
```

## Testing

The application includes comprehensive test suites:

**Backend Tests:**
```bash
# Run all backend tests
python api/tests/test_setup.py
python api/tests/test_models.py
python api/tests/test_text_processing.py
python api/tests/test_graph_service.py
```

**Frontend Type Checking:**
```bash
npx tsc --noEmit
```

## Documentation

- **[DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md)** - Quick Docker setup guide
- **[DOCKER_SETUP.md](DOCKER_SETUP.md)** - Detailed Docker configuration
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Codebase organization

## Learn More

### Technologies Used

- **[Next.js Documentation](https://nextjs.org/docs)** - React framework for the frontend
- **[FastAPI Documentation](https://fastapi.tiangolo.com/)** - Python web framework for the backend
- **[OpenAI API](https://platform.openai.com/docs)** - AI-powered concept extraction
- **[NetworkX](https://networkx.org/)** - Graph data structure library
- **[TailwindCSS](https://tailwindcss.com/)** - Utility-first CSS framework

## License

See [LICENSE](LICENSE) file for details.
