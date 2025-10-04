<p align="center">
  <a href="https://nextjs-fastapi-starter.vercel.app/">
    <img src="https://assets.vercel.com/image/upload/v1588805858/repositories/vercel/logo.png" height="96">
    <h3 align="center">Next.js FastAPI Starter</h3>
  </a>
</p>

<p align="center">Simple Next.j 14 boilerplate that uses <a href="https://fastapi.tiangolo.com/">FastAPI</a> as the API backend.</p>

<br/>

## Introduction

This is a hybrid Next.js 14 + Python template. One great use case of this is to write Next.js apps that use Python AI libraries on the backend, while still having the benefits of Next.js Route Handlers and Server Side Rendering.

## How It Works

The Python/FastAPI server is mapped into to Next.js app under `/api/`.

This is implemented using [`next.config.js` rewrites](https://github.com/digitros/nextjs-fastapi/blob/main/next.config.js) to map any request to `/api/py/:path*` to the FastAPI API, which is hosted in the `/api` folder.

Also, the app/api routes are available on the same domain, so you can use NextJs Route Handlers and make requests to `/api/...`.

On localhost, the rewrite will be made to the `127.0.0.1:8000` port, which is where the FastAPI server is running.

In production, the FastAPI server is hosted as [Python serverless functions](https://vercel.com/docs/concepts/functions/serverless-functions/runtimes/python) on Vercel.

## Demo

https://nextjs-fastapi-starter.vercel.app/

## Deploy Your Own

You can clone & deploy it to Vercel with one click:

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fdigitros%2Fnextjs-fastapi%2Ftree%2Fmain)

## Developing Locally

You can clone & create this repo with the following command

```bash
npx create-next-app nextjs-fastapi --example "https://github.com/digitros/nextjs-fastapi"
```

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

The app uses unlimited concept extraction which can take time:
- **Short texts (100-1500 chars)**: 10-30 seconds
- **Medium texts (1500-3000 chars)**: 30-60 seconds  
- **Long texts (3000+ chars)**: 60-180 seconds

Watch the backend console for real-time progress updates!

📚 **See [TIMEOUT_FIX.md](TIMEOUT_FIX.md) for detailed timeout handling and optimization tips.**

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.
- [FastAPI Documentation](https://fastapi.tiangolo.com/) - learn about FastAPI features and API.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js/) - your feedback and contributions are welcome!
