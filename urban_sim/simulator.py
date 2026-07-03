import json
from pathlib import Path

import pandas as pd

from .city import make_city
from .agents import create_agents, update_agents, agents_dataframe


def simulate(cfg):
    city = make_city(cfg)
    agents = create_agents(city, cfg)

    frames = []
    summary_rows = []
    agent_rows = []

    for frame in range(int(cfg.get("frames", 96))):
        counts, metrics = update_agents(agents, city, cfg, frame)
        hour = metrics["hour"]

        frame_agents = agents_dataframe(agents, frame, hour)
        agent_rows.append(frame_agents)

        frames.append({
            "frame": frame,
            "hour": hour,
            "city": city,
            "agents": frame_agents,
            "congestion_grid": counts.copy(),
            **metrics,
        })

        summary_rows.append({
            "frame": frame,
            "hour": hour,
            **{k: v for k, v in metrics.items() if k != "hour"},
        })

    return city, frames, pd.DataFrame(summary_rows), pd.concat(agent_rows, ignore_index=True)


def run_counterfactuals(base_cfg):
    scenarios = {
        "factual": {},
        "do_add_station": {"policy_add_station": True},
        "do_add_park": {"policy_add_park": True},
        "do_remote_work": {"policy_remote_work": True},
        "do_mixed_use_city": {"policy_mixed_use": True},
        "do_low_movement_speed": {"movement_speed": 1},
        "do_high_movement_speed": {"movement_speed": 2},
        "do_high_congestion_sensitivity": {"congestion_fatigue_gain": 0.040},
    }

    rows = []
    for name, changes in scenarios.items():
        cfg = dict(base_cfg)
        cfg.update(changes)
        _, _, summary, agents = simulate(cfg)

        rows.append({
            "scenario": name,
            "avg_satisfaction_final": float(summary["avg_satisfaction"].iloc[-1]),
            "avg_fatigue_final": float(summary["avg_fatigue"].iloc[-1]),
            "max_congestion_peak": float(summary["max_congestion"].max()),
            "energy_total": float(summary["energy_demand"].sum()),
            "spending_total": float(summary["total_spending"].sum()),
            "waste_total": float(summary["waste_generated"].sum()),
            "public_service_load_total": float(summary["public_service_load"].sum()),
            "avg_distance_today_final": float(agents.groupby("agent_id")["distance_today"].max().mean()),
        })
    return pd.DataFrame(rows)
