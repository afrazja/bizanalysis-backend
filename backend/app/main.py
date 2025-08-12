from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict

from .config import settings
from .schemas import ProductIn, BCGPoint, SWOTIn, SWOTOut
from .services.bcg import classify_bcg
from .services.swot import build_swot
from .services.porter import forces_index

app = FastAPI(title=settings.APP_NAME, version="0.1.0")

# Get CORS origins as a list
cors_origins = settings.get_cors_origins()
print(f"CORS Origins: {cors_origins}")

# Add a wildcard for development/debugging
cors_origins.append("*")
print(f"Final CORS Origins (with wildcard): {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporarily allow all origins for debugging
    allow_credentials=False,  # Must be False when allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/bcg", response_model=List[BCGPoint])
async def bcg(products: List[ProductIn]):
    return classify_bcg(products)

@app.post("/swot", response_model=SWOTOut)
async def swot(swot: SWOTIn):
    return build_swot(swot)

@app.post("/porter")
async def porter(inputs: Dict[str, float]):
    return forces_index(inputs)
