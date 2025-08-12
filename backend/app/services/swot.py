from ..schemas import SWOTIn, SWOTOut

def build_swot(swot: SWOTIn) -> SWOTOut:
    return SWOTOut(**swot.model_dump())
