import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import json
import numpy as np
from urban_sim.simulator import simulate, run_counterfactuals


def test_simulation_outputs():
    with open("configs/urban_life.json", "r", encoding="utf-8") as f:
        cfg = json.load(f)
    cfg["frames"] = 12
    cfg["n_agents"] = 30
    city, frames, summary, agents = simulate(cfg)
    assert len(frames) == len(summary)
    for col in ["avg_fatigue", "avg_satisfaction", "energy_demand", "max_congestion"]:
        assert col in summary.columns
        assert np.isfinite(summary[col]).all()
    assert len(agents) > 0


def test_counterfactuals_outputs():
    with open("configs/urban_life.json", "r", encoding="utf-8") as f:
        cfg = json.load(f)
    cfg["frames"] = 12
    cfg["n_agents"] = 30
    cf = run_counterfactuals(cfg)
    assert len(cf) >= 4
    assert "do_add_station" in set(cf["scenario"])
