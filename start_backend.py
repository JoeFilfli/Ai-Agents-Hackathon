"""
Start the FastAPI backend with optimized settings for long-running requests.

This script starts uvicorn with timeouts configured for processing
long texts with unlimited concept extraction (can take 1-3 minutes).
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "api.index:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        timeout_keep_alive=300,  # 5 minutes keep-alive
        timeout_graceful_shutdown=30,
        log_level="info"
    )

