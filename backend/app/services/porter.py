from typing import Dict

def forces_index(inputs: Dict[str, float]) -> Dict[str, float]:
    weights = {"supplier":1, "buyer":1, "rivalry":1, "substitutes":1, "new_entrants":1}
    total = sum(weights.values())
    score = sum(inputs.get(k, 0.0) * w for k, w in weights.items()) / total
    return {"per_force": inputs, "overall": score}
