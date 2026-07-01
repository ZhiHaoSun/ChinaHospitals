"""Vercel FastAPI entrypoint.

Vercel's Python runtime looks for serverless functions under the top-level
`api/` directory. The application code stays in `medtour_ai.api.main`.
"""

from medtour_ai.api.main import app

