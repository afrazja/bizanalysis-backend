from typing import List
from ..schemas import ProductIn, BCGPoint

GROWTH_THRESHOLD = 10.0
RMS_THRESHOLD = 1.0

def classify_bcg(products: List[ProductIn]) -> List[BCGPoint]:
    out: List[BCGPoint] = []
    for p in products:
        rms = p.market_share / max(p.largest_rival_share, 1e-9)
        g = p.market_growth_rate
        if g >= GROWTH_THRESHOLD and rms >= RMS_THRESHOLD:
            q = "Star"
        elif g < GROWTH_THRESHOLD and rms >= RMS_THRESHOLD:
            q = "Cash Cow"
        elif g >= GROWTH_THRESHOLD and rms < RMS_THRESHOLD:
            q = "Question Mark"
        else:
            q = "Dog"
        out.append(BCGPoint(name=p.name, rms=rms, growth=g, quadrant=q))
    return out
