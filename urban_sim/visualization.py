from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


COLORS = {
    "home": "lightgray",
    "work": "tab:blue",
    "school": "tab:purple",
    "station": "black",
    "commerce": "tab:orange",
    "hospital": "tab:red",
    "park": "tab:green",
    "admin": "tab:brown",
}

ROLE_COLORS = {
    "worker": "tab:blue",
    "student": "tab:purple",
    "senior": "tab:green",
}


def save_timeline(summary, output="results/urban_life_timeline.png"):
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(4, 1, figsize=(10, 10), sharex=True)
    t = summary["frame"]

    axes[0].plot(t, summary["avg_congestion"], label="avg congestion")
    axes[0].plot(t, summary["max_congestion"], label="max congestion")
    axes[0].legend()
    axes[0].set_ylabel("congestion")

    axes[1].plot(t, summary["avg_fatigue"], label="avg fatigue")
    axes[1].plot(t, summary["avg_satisfaction"], label="avg satisfaction")
    axes[1].legend()
    axes[1].set_ylabel("wellbeing")

    axes[2].plot(t, summary["energy_demand"], label="energy demand")
    axes[2].plot(t, summary["total_spending"], label="spending")
    axes[2].plot(t, summary["waste_generated"], label="waste")
    axes[2].legend()
    axes[2].set_ylabel("activity")

    axes[3].plot(t, summary["public_service_load"], label="public service load")
    axes[3].legend()
    axes[3].set_ylabel("service")
    axes[3].set_xlabel("frame")
    fig.suptitle("Urban human life algorithm timeline")
    fig.tight_layout()
    fig.savefig(output)
    plt.close(fig)


def animate_city(city, frames, summary, output="results/urban_human_life_algorithm.gif", fps=5):
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    w, h = city["width"], city["height"]

    fig = plt.figure(figsize=(12, 7))
    gs = fig.add_gridspec(2, 2, height_ratios=[2.0, 1.0])
    ax_map = fig.add_subplot(gs[0, 0])
    ax_state = fig.add_subplot(gs[0, 1])
    ax_time = fig.add_subplot(gs[1, :])

    first_grid = frames[0]["congestion_grid"]
    heat = ax_map.imshow(first_grid, origin="lower", cmap="Reds", vmin=0, vmax=max(5, summary["max_congestion"].max()), alpha=0.45)

    # Facilities
    for ftype, locs in city["facilities"].items():
        if not locs:
            continue
        xs, ys = zip(*locs)
        ax_map.scatter(xs, ys, s=110, marker="s", c=COLORS.get(ftype, "gray"), label=ftype, edgecolors="black", linewidths=0.5)

    agents0 = frames[0]["agents"]
    agent_scatter = ax_map.scatter(agents0["x"], agents0["y"], s=20, c=[ROLE_COLORS.get(r, "gray") for r in agents0["role"]], alpha=0.75)

    ax_map.set_xlim(-0.5, w - 0.5)
    ax_map.set_ylim(-0.5, h - 0.5)
    ax_map.set_aspect("equal")
    ax_map.set_title("Synthetic city and residents")
    ax_map.legend(loc="upper right", fontsize=7, ncol=2)

    names = ["congestion", "fatigue", "satisfaction", "energy", "spending", "waste", "service"]
    bars = ax_state.barh(names, np.zeros(len(names)))
    ax_state.set_xlim(0, 1.05)
    ax_state.set_title("City-scale state")

    t = summary["frame"].to_numpy()
    max_energy = max(summary["energy_demand"].max(), 1e-9)
    max_spend = max(summary["total_spending"].max(), 1e-9)
    max_waste = max(summary["waste_generated"].max(), 1e-9)
    max_service = max(summary["public_service_load"].max(), 1e-9)
    max_cong = max(summary["max_congestion"].max(), 1e-9)

    ax_time.plot(t, summary["max_congestion"]/max_cong, label="congestion")
    ax_time.plot(t, summary["avg_fatigue"], label="fatigue")
    ax_time.plot(t, summary["avg_satisfaction"], label="satisfaction")
    ax_time.plot(t, summary["energy_demand"]/max_energy, label="energy")
    ax_time.plot(t, summary["public_service_load"]/max_service if max_service > 0 else summary["public_service_load"], label="service load")
    marker, = ax_time.plot([], [], marker="o", color="black", markersize=8)
    ax_time.set_ylim(0, 1.08)
    ax_time.set_title("Daily routine -> mobility -> congestion -> wellbeing")
    ax_time.legend(loc="upper left", ncol=5)
    ax_time.set_xlabel("frame")

    def update(i):
        f = frames[i]
        agents = f["agents"]
        heat.set_data(f["congestion_grid"])
        agent_scatter.set_offsets(agents[["x", "y"]].to_numpy())
        agent_scatter.set_color([ROLE_COLORS.get(r, "gray") for r in agents["role"]])

        ax_map.set_title(
            f"Synthetic city and residents | hour={int(f['hour']):02d}:00\n"
            f"congestion={f['max_congestion']:.0f} | fatigue={f['avg_fatigue']:.2f} | satisfaction={f['avg_satisfaction']:.2f}"
        )

        idx = i
        values = [
            summary["max_congestion"].iloc[idx] / max_cong,
            summary["avg_fatigue"].iloc[idx],
            summary["avg_satisfaction"].iloc[idx],
            summary["energy_demand"].iloc[idx] / max_energy,
            summary["total_spending"].iloc[idx] / max_spend if max_spend > 0 else 0.0,
            summary["waste_generated"].iloc[idx] / max_waste if max_waste > 0 else 0.0,
            summary["public_service_load"].iloc[idx] / max_service if max_service > 0 else 0.0,
        ]
        for b, v in zip(bars, values):
            b.set_width(float(np.clip(v, 0, 1)))
        ax_state.set_title(
            "City-scale state\n"
            f"energy={f['energy_demand']:.1f} | spending={f['total_spending']:.2f} | waste={f['waste_generated']:.1f}"
        )
        marker.set_data([i], [summary["avg_satisfaction"].iloc[idx]])
        return heat, agent_scatter, marker, *bars

    anim = FuncAnimation(fig, update, frames=len(frames), interval=180, blit=False)
    anim.save(output, writer="pillow", fps=fps, dpi=65)
    plt.close(fig)


def plot_counterfactuals(cf, output="results/urban_policy_counterfactuals.png"):
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))

    axes[0, 0].bar(cf["scenario"], cf["avg_satisfaction_final"])
    axes[0, 0].set_ylabel("final satisfaction")

    axes[0, 1].bar(cf["scenario"], cf["avg_fatigue_final"])
    axes[0, 1].set_ylabel("final fatigue")

    axes[1, 0].bar(cf["scenario"], cf["max_congestion_peak"])
    axes[1, 0].set_ylabel("peak congestion")

    axes[1, 1].bar(cf["scenario"], cf["energy_total"])
    axes[1, 1].set_ylabel("total energy demand")

    for ax in axes.ravel():
        ax.tick_params(axis="x", rotation=35)

    fig.suptitle("Urban policy counterfactuals")
    fig.tight_layout()
    fig.savefig(output)
    plt.close(fig)
