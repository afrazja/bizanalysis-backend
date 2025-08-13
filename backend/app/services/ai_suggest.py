from typing import List, Dict
from ..schemas import SuggestSWOTIn, SWOTOut, BCGPoint

GROWTH_HI = 10.0
RMS_LEADER = 1.0


def _uniq(xs: List[str]) -> List[str]:
    seen = set(); out = []
    for x in xs:
        k = x.strip().lower()
        if k and k not in seen:
            seen.add(k); out.append(x.strip())
    return out


def suggest_swot(body: SuggestSWOTIn) -> SWOTOut:
    strengths: List[str] = []
    weaknesses: List[str] = []
    opportunities: List[str] = []
    threats: List[str] = []

    # Prefer points if present (already computed RMS & growth)
    pts: List[BCGPoint] = body.points or []

    # If no points, synthesize from products/markets heuristics
    if not pts and body.products:
        # basic RMS calc per product (no quadrant)
        for p in body.products:
            if p.largest_rival_share > 0:
                rms = p.market_share / p.largest_rival_share
                pts.append(BCGPoint(name=p.name, rms=rms, growth=0.0, quadrant="Question Mark"))

    # Market context
    hi_growth = any(m.growth_rate >= GROWTH_HI for m in (body.markets or []))
    if hi_growth:
        opportunities.append("High growth market tailwinds")

    # Points-based heuristics
    for p in pts:
        if p.rms >= RMS_LEADER and p.growth >= GROWTH_HI:
            strengths.append(f"Leadership in high-growth segment ({p.name})")
        if p.rms >= RMS_LEADER and p.growth < GROWTH_HI:
            strengths.append(f"Strong relative share: {p.name}")
        if p.rms < RMS_LEADER and p.growth >= GROWTH_HI:
            opportunities.append(f"Gain share in fast-growing {p.name}")
        if p.rms < RMS_LEADER and p.growth < GROWTH_HI:
            weaknesses.append(f"Low relative share: {p.name}")

    # Generic industry prompts (lightweight)
    if body.industry:
        opportunities.append(f"Evolving {body.industry} customer needs")
        threats.append(f"Intense competition in {body.industry}")

    # Company name can seed a neutral statement
    if body.company:
        strengths.append(f"Brand equity for {body.company}")

    return SWOTOut(
        strengths=_uniq(strengths)[:8],
        weaknesses=_uniq(weaknesses)[:8],
        opportunities=_uniq(opportunities)[:8],
        threats=_uniq(threats)[:8],
    )
