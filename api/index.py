import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from mangum import Mangum
from backend.main import app

# lifespan="auto" lets FastAPI's startup event (init_db) run on cold start
handler = Mangum(app, lifespan="auto")
