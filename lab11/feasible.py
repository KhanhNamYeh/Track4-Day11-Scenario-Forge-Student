"""Part B: physics check. TODO 3."""
from __future__ import annotations

import math

G = 9.81


def is_feasible(p: dict) -> bool:
    """TODO 3. False for scenarios no real road user could produce. Reject if ANY of:

    - the lane change needs more sideways grip than the road has: the cosine lane change of 3.5 m over
      p["cutDur"] seconds peaks at a_lat = (pi / cutDur)^2 * 3.5 / 2; reject if a_lat > mu * g;
    - the post-merge braking p["cutBrake"] exceeds mu * g;
    - the pedestrian runs: p["pedV"] > 2.5 m/s;
    - the cut-in speed p["cutV"] is not in (0, 22] m/s.
    mu is p["mu"]. A search that keeps infeasible scenarios reports failures that cannot happen.
    """
    mu = p.get("mu", 0.8)
    a_lat = (math.pi / p.get("cutDur", 2.4)) ** 2 * 3.5 / 2
    if a_lat > mu * G:
        return False
    if (p.get("cutBrake") or 0.0) > mu * G:
        return False
    if p.get("pedV", 1.45) > 2.5:
        return False
    cut_v = p.get("cutV", 15.0)
    if not 0 < cut_v <= 22:
        return False
    return True
