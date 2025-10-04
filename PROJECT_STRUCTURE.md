# Project Structure

```
Ai_Agents/
├── api/                        # FastAPI Backend
│   ├── models/                 # Pydantic data models
│   │   ├── __init__.py
│   │   ├── graph_models.py     # Node, Edge, Graph models
│   │   └── README.md
│   ├── services/               # Business logic services
│   │   ├── __init__.py
│   │   ├── text_processing.py  # Text analysis & concept extraction
│   │   └── README.md
│   ├── tests/                  # Backend test suite
│   │   ├── __init__.py
│   │   ├── test_setup.py       # Setup and dependency tests
│   │   ├── test_models.py      # Data model tests
│   │   ├── test_text_processing.py  # Concept extraction tests
│   │   ├── test_relationships.py    # Relationship extraction tests
│   │   └── README.md
│   └── index.py                # Main FastAPI application
│
├── app/                        # Next.js Frontend
│   ├── types/                  # TypeScript type definitions
│   │   ├── graph.ts            # Graph type interfaces
│   │   ├── graph.test.ts       # Type tests
│   │   └── README.md
│   ├── favicon.ico
│   ├── globals.css             # Global styles (TailwindCSS)
│   ├── layout.tsx              # Root layout
│   └── page.tsx                # Main page
│
├── public/                     # Static assets
│   ├── next.svg
│   └── vercel.svg
│
├── .cursor/                    # Cursor AI project files
│   ├── design.md               # Technical design document
│   ├── requirements.md         # Project requirements
│   └── tasks.md                # Task breakdown
│
├── venv/                       # Python virtual environment
│
├── .env.local                  # Environment variables (create this!)
├── env.example                 # Environment template
├── next.config.js              # Next.js configuration
├── package.json                # Node.js dependencies
├── requirements.txt            # Python dependencies
├── tailwind.config.js          # TailwindCSS configuration
├── tsconfig.json               # TypeScript configuration
└── PROJECT_STRUCTURE.md        # This file
```

## Key Directories

### `/api` - Backend API
All Python/FastAPI code lives here.
- `models/` - Pydantic data models
- `services/` - Business logic services (text processing, graph, LLM)
- `tests/` - Backend test suite
- Future: `utils/`

### `/app` - Frontend
All Next.js/React/TypeScript code lives here.
- `types/` - TypeScript interfaces
- Future: `components/`, `store/`

### `/public` - Static Files
Public assets served directly.
- Future: `audio/` for TTS files

## Running Tests

### Backend Tests
```bash
# Setup tests
python api/tests/test_setup.py

# Model tests
python api/tests/test_models.py

# Text processing tests
python api/tests/test_text_processing.py

# Relationship extraction tests
python api/tests/test_relationships.py
```

### Frontend Tests
```bash
# Type checking
npx tsc --noEmit
```

## Development Workflow

1. **Backend Development**: Work in `api/`
2. **Frontend Development**: Work in `app/`
3. **Test After Changes**: Run relevant tests
4. **Check Types**: Run `npx tsc --noEmit`

## Next Steps

As we build the project, new directories will be added:
- ✅ `api/services/` - Business logic services (text_processing.py complete)
- `api/utils/` - Helper functions
- `app/components/` - React components
- `app/store/` - State management
- `public/audio/` - Generated audio files

