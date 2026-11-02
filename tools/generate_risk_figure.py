# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib>=3.9,<4"]
# ///
"""Render the declared synthetic CVaR example. Run: uv run tools/generate_risk_figure.py."""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "figures/risk_example.json").read_text())
plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Liberation Sans", "DejaVu Sans"],
        "font.size": 14,
        "axes.labelsize": 15,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
        "axes.edgecolor": "#66737d",
        "text.color": "#253e54",
        "axes.labelcolor": "#253e54",
        "xtick.color": "#66737d",
        "ytick.color": "#66737d",
        "svg.hashsalt": "risk-example-v1",
    }
)


def cvar(route, alpha):
    failed_mass = min(alpha, route["failure"])
    return (
        data["failure_return"] * failed_mass
        + route["success_return"] * (alpha - failed_mass)
    ) / alpha


fig, ax = plt.subplots(figsize=(7, 3.8))
fig.subplots_adjust(left=0.16, right=0.98, top=0.96, bottom=0.25)
values = [
    data["alpha_min"] + (data["alpha_max"] - data["alpha_min"]) * i / 360
    for i in range(361)
]
for route in data["routes"]:
    ax.plot(
        values,
        [cvar(route, a) for a in values],
        color=route["color"],
        linestyle=route["linestyle"],
        linewidth=2.5,
        label=route["name"],
        gid="curve-" + route["id"],
    )
ax.set(
    xlim=(0.1, 1),
    ylim=(-105, 95),
    xlabel="Worst-return fraction α",
    ylabel="CVaR (reward units)",
)
ax.set_xticks([0.1, 0.3, 0.5, 0.7, 1.0])
ax.set_yticks([-100, 0, 50])
ax.axhline(0, color="#d4dce1", linewidth=0.7, zorder=0)
ax.axvline(
    0.2, color="#8a959b", linewidth=1.2, linestyle=(0, (3, 3)), gid="alpha-cursor"
)
ax.legend(loc="lower right", frameon=False, fontsize=11)
fig.savefig(ROOT / "figures/risk_cvar.svg", metadata={"Date": None})
svg_path = ROOT / "figures/risk_cvar.svg"
svg_path.write_text(
    "\n".join(line.rstrip() for line in svg_path.read_text().splitlines()) + "\n"
)
fig.savefig(
    ROOT / "figures/risk_cvar.pdf", metadata={"CreationDate": None, "ModDate": None}
)
geometry = {
    "left": 0.16 * 504,
    "right": 0.98 * 504,
    "top": (1 - 0.96) * 273.6,
    "bottom": (1 - 0.25) * 273.6,
    "alpha_min": 0.1,
    "alpha_max": 1,
    "y_min": -105,
    "y_max": 95,
}
(ROOT / "figures/risk_plot_geometry.json").write_text(
    json.dumps(geometry, indent=2) + "\n"
)
for alpha in [0.1, 0.6, 1.0]:
    best = max(data["routes"], key=lambda route: cvar(route, alpha))
    print(f"α={alpha:g}: {best['name']}")
