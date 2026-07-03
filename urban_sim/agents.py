import numpy as np
import pandas as pd

from .city import nearest, manhattan_step, clamp_pos


def create_agents(city, cfg):
    rng = np.random.default_rng(cfg.get("seed", 42))
    n = int(cfg.get("n_agents", 150))

    homes = city["facilities"]["home"]
    works = city["facilities"]["work"]
    schools = city["facilities"]["school"]

    agents = []
    for i in range(n):
        home = homes[rng.integers(0, len(homes))]
        role = rng.choice(["worker", "student", "senior"], p=[0.62, 0.25, 0.13])

        if role == "worker":
            daily_place = works[rng.integers(0, len(works))]
            income = float(rng.normal(1.0, 0.20))
        elif role == "student":
            daily_place = schools[rng.integers(0, len(schools))]
            income = float(rng.normal(0.35, 0.08))
        else:
            daily_place = home
            income = float(rng.normal(0.55, 0.10))

        agents.append({
            "agent_id": i,
            "role": role,
            "home": tuple(home),
            "daily_place": tuple(daily_place),
            "pos": tuple(home),
            "target": tuple(home),
            "income": max(0.1, income),
            "fatigue": float(rng.uniform(0.05, 0.18)),
            "satisfaction": float(rng.uniform(0.55, 0.75)),
            "health_need": float(rng.uniform(0.0, 0.3)),
            "spending": 0.0,
            "energy": 0.0,
            "waste": 0.0,
            "distance_today": 0.0,
        })
    return agents


def hour_from_frame(frame, cfg):
    minutes = frame * int(cfg.get("minutes_per_frame", 15))
    return (minutes // 60) % 24


def choose_target(agent, hour, city, cfg):
    f = city["facilities"]

    # Remote work policy reduces worker commuting.
    remote_work = cfg.get("policy_remote_work", False) and agent["role"] == "worker" and hour in range(8, 18)
    if remote_work:
        return agent["home"], "remote_work"

    if 6 <= hour < 8:
        # commute toward station first if far from daily destination
        return nearest(agent["pos"], f["station"]), "morning_commute"
    if 8 <= hour < 12:
        if agent["role"] in ["worker", "student"]:
            return agent["daily_place"], "work_or_school"
        return nearest(agent["home"], f["park"]), "park"
    if 12 <= hour < 14:
        if agent["role"] == "senior":
            return nearest(agent["pos"], f["park"]), "park"
        return nearest(agent["pos"], f["commerce"]), "lunch_commerce"
    if 14 <= hour < 17:
        if agent["role"] in ["worker", "student"]:
            return agent["daily_place"], "work_or_school"
        # Some seniors visit hospital/admin/park.
        if agent["health_need"] > 0.22:
            return nearest(agent["pos"], f["hospital"]), "hospital"
        return nearest(agent["pos"], f["park"]), "park"
    if 17 <= hour < 20:
        if agent["role"] in ["worker", "student"]:
            return nearest(agent["pos"], f["station"]), "evening_commute"
        return nearest(agent["pos"], f["commerce"]), "commerce"
    if 20 <= hour < 22:
        # commerce or park before home
        if agent["fatigue"] < 0.5 and agent["income"] > 0.5:
            return nearest(agent["pos"], f["commerce"]), "evening_commerce"
        return agent["home"], "home"
    return agent["home"], "home"


def cell_counts(agents, city):
    grid = np.zeros((city["height"], city["width"]), dtype=float)
    for a in agents:
        x, y = a["pos"]
        if 0 <= x < city["width"] and 0 <= y < city["height"]:
            grid[y, x] += 1
    return grid


def local_congestion(pos, counts, city, radius=1):
    x, y = pos
    r = int(radius)
    y0, y1 = max(0, y-r), min(city["height"], y+r+1)
    x0, x1 = max(0, x-r), min(city["width"], x+r+1)
    return float(counts[y0:y1, x0:x1].sum())


def update_agents(agents, city, cfg, frame):
    hour = hour_from_frame(frame, cfg)
    speed = int(cfg.get("movement_speed", 1))

    # First choose targets and move.
    prev_positions = [a["pos"] for a in agents]
    activities = []
    for a in agents:
        target, activity = choose_target(a, hour, city, cfg)
        a["target"] = clamp_pos(target, city)
        old = a["pos"]
        if old != a["target"]:
            a["pos"] = clamp_pos(manhattan_step(old, a["target"], speed), city)
        moved = abs(a["pos"][0] - old[0]) + abs(a["pos"][1] - old[1])
        a["distance_today"] += moved
        activities.append(activity)

    counts = cell_counts(agents, city)

    # Then update individual life states.
    total_spending = 0.0
    total_energy = 0.0
    total_waste = 0.0
    public_load = 0.0

    for a, activity in zip(agents, activities):
        congestion = local_congestion(a["pos"], counts, city, cfg.get("congestion_radius", 1))
        moving = 1.0 if a["pos"] != a["target"] else 0.0

        fatigue_gain = float(cfg.get("base_fatigue_gain", 0.020))
        if "commute" in activity:
            fatigue_gain += float(cfg.get("commute_fatigue_gain", 0.045))
        fatigue_gain += float(cfg.get("congestion_fatigue_gain", 0.018)) * min(congestion / 10.0, 2.0)

        # Recovery / increase.
        if activity == "home":
            a["fatigue"] -= float(cfg.get("home_recovery", 0.050))
        elif activity == "park":
            a["fatigue"] -= float(cfg.get("park_recovery", 0.045))
            a["satisfaction"] += 0.025
        else:
            a["fatigue"] += fatigue_gain * (0.55 + moving)

        a["fatigue"] = float(np.clip(a["fatigue"], 0, 1))

        # Spending and waste.
        spend = 0.0
        waste = 0.0
        if "commerce" in activity or "lunch" in activity:
            spend = float(cfg.get("income_spending_rate", 0.030)) * a["income"] * (1.0 + 0.25*np.random.default_rng(a["agent_id"]+frame).random())
            waste = float(cfg.get("waste_per_commerce_visit", 0.20))
            a["satisfaction"] += 0.010

        # Energy.
        if activity == "home":
            energy = float(cfg.get("energy_home_base", 0.55))
        elif activity in ["work_or_school", "remote_work"]:
            energy = float(cfg.get("energy_work_base", 0.80))
        else:
            energy = 0.30

        # Hospital/admin load.
        if activity in ["hospital", "remote_work"]:
            public_load += 1.0 if activity == "hospital" else 0.15

        # Satisfaction: access helps, congestion/fatigue hurts.
        a["satisfaction"] += 0.010
        a["satisfaction"] -= 0.055 * a["fatigue"]
        a["satisfaction"] -= 0.010 * min(congestion / 8.0, 3.0)
        if activity == "hospital" and a["health_need"] > 0.2:
            a["satisfaction"] += 0.040
            a["health_need"] *= 0.98
        a["satisfaction"] = float(np.clip(a["satisfaction"], 0, 1))

        a["spending"] += spend
        a["energy"] += energy
        a["waste"] += waste
        total_spending += spend
        total_energy += energy
        total_waste += waste

    return counts, {
        "hour": hour,
        "avg_fatigue": float(np.mean([a["fatigue"] for a in agents])),
        "avg_satisfaction": float(np.mean([a["satisfaction"] for a in agents])),
        "total_spending": float(total_spending),
        "energy_demand": float(total_energy),
        "waste_generated": float(total_waste),
        "public_service_load": float(public_load),
        "avg_congestion": float(np.mean(counts[counts > 0])) if np.any(counts > 0) else 0.0,
        "max_congestion": float(np.max(counts)),
    }


def agents_dataframe(agents, frame, hour):
    return pd.DataFrame([{
        "frame": frame,
        "hour": hour,
        "agent_id": a["agent_id"],
        "role": a["role"],
        "x": a["pos"][0],
        "y": a["pos"][1],
        "target_x": a["target"][0],
        "target_y": a["target"][1],
        "fatigue": a["fatigue"],
        "satisfaction": a["satisfaction"],
        "spending_total": a["spending"],
        "energy_total": a["energy"],
        "waste_total": a["waste"],
        "distance_today": a["distance_today"],
    } for a in agents])
