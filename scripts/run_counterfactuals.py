import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import json
from urban_sim.simulator import run_counterfactuals
from urban_sim.visualization import plot_counterfactuals


def main():
    with open("configs/urban_life.json", "r", encoding="utf-8") as f:
        cfg = json.load(f)

    cf = run_counterfactuals(cfg)
    Path("results").mkdir(exist_ok=True)
    cf.to_csv("results/urban_policy_counterfactuals.csv", index=False)
    plot_counterfactuals(cf, "results/urban_policy_counterfactuals.png")
    print("Generated results/urban_policy_counterfactuals.csv")
    print("Generated results/urban_policy_counterfactuals.png")
    print(cf)


if __name__ == "__main__":
    main()
