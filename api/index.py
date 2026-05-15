import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from mangum import Mangum
from backend.main import app

# Strip /api prefix so FastAPI routes match (vercel routes /api/* here)
handler = Mangum(app, lifespan="auto", api_gateway_base_path="/api")
