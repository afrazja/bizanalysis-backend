from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict

from .config import settings
from .schemas import ProductIn, BCGPoint, SWOTIn, SWOTOut
from .services.bcg import classify_bcg
from .services.swot import build_swot
from .services.porter import forces_index

app = FastAPI(title=settings.APP_NAME, version="0.1.0")

# Print CORS origins for debugging
print(f"CORS Origins: {settings.CORS_ORIGINS}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # This now calls the property
    allow_credentials=True,
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
