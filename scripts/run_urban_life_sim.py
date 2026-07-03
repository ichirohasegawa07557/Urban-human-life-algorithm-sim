import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import json
from urban_sim.simulator import simulate
from urban_sim.visualization import animate_city, save_timeline


def main():
    with open("configs/urban_life.json", "r", encoding="utf-8") as f:
        cfg = json.load(f)

    city, frames, summary, agents = simulate(cfg)
    Path("results").mkdir(exist_ok=True)
    summary.to_csv("results/urban_life_summary.csv", index=False)
    agents.to_csv("results/urban_life_agents.csv", index=False)
    save_timeline(summary, "results/urban_life_timeline.png")

    if cfg.get("animate", True):
        animate_city(city, frames, summary, "results/urban_human_life_algorithm.gif", fps=5)

    print("Generated results/urban_human_life_algorithm.gif")
    print("Generated results/urban_life_summary.csv")
    print("Generated results/urban_life_agents.csv")
    print("Generated results/urban_life_timeline.png")
    print("final avg satisfaction =", summary["avg_satisfaction"].iloc[-1])
    print("final avg fatigue =", summary["avg_fatigue"].iloc[-1])


if __name__ == "__main__":
    main()
