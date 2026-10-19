"""Regenerate public aggregate charts from results/summary.json."""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
data = json.loads((RESULTS / "summary.json").read_text(encoding="utf-8"))

plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": "white"})
matched = data["matched_60_essay_subset"]
names = ["Basic LR", "Expanded LR", "Selected LLM"]
rows = [matched["lr_basic"], matched["lr_expanded"], matched["selected_llm"]]
colors = ["#91b8d4", "#3178ab", "#e98c35"]
fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
for ax, key, title, better in zip(axes, ("pearson_r", "mse"), ("Pearson r", "Mean squared error"), ("Higher is better", "Lower is better")):
    values = [row[key] for row in rows]
    bars = ax.bar(names, values, color=colors, width=0.65)
    ax.set_title(title, weight="bold")
    ax.set_ylabel(better)
    ax.set_ylim(0, max(values) * 1.23)
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value + max(values) * 0.025, f"{value:.3f}", ha="center")
fig.suptitle("Matched comparison on the same 60 essays", weight="bold", y=1.01)
fig.tight_layout()
fig.savefig(RESULTS / "fig03_official1_fair_comparison.png", dpi=170, bbox_inches="tight")
plt.close(fig)

conditions = data["llm_conditions"]
names = {"deepseek/deepseek-v3.2": "DeepSeek V3.2", "mistralai/mistral-small-3.1-24b-instruct": "Mistral Small 3.1", "google/gemma-3-27b-it": "Gemma 3 27B"}
palette = {"DeepSeek V3.2": "#3178ab", "Mistral Small 3.1": "#d35750", "Gemma 3 27B": "#4d9a65"}
marker = {"P1_direct_holistic": "o", "P2_analytic_to_holistic": "s"}
fig, ax = plt.subplots(figsize=(8.4, 5.3))
for row in conditions:
    model = names[row["model_id"]]
    ax.scatter(row["pearson_r"], row["mse"], s=100, color=palette[model], marker=marker[row["prompt_key"]], alpha=0.9)
    ax.annotate(f"{row['temperature']:.1f}", (row["pearson_r"], row["mse"]), xytext=(5, 3), textcoords="offset points", fontsize=7)
ax.set(xlabel="Pearson r  (higher is better)", ylabel="MSE  (lower is better)", title="12 rubric-guided LLM conditions on 60 essays")
ax.grid(alpha=0.2)
ax.set_axisbelow(True)
from matplotlib.lines import Line2D
legend = [Line2D([0], [0], marker="o", color="none", markerfacecolor=palette[name], markeredgecolor="none", markersize=9, label=name) for name in palette]
legend += [Line2D([0], [0], marker=marker[key], color="#444", linestyle="none", markersize=8, label=label) for key, label in (("P1_direct_holistic", "Direct prompt"), ("P2_analytic_to_holistic", "Analytic prompt"))]
ax.legend(handles=legend, loc="upper left", bbox_to_anchor=(1.02, 1), fontsize=8, frameon=False)
fig.tight_layout()
fig.savefig(RESULTS / "fig02_official1_all_conditions.png", dpi=170, bbox_inches="tight")
plt.close(fig)
print("Charts regenerated from aggregate results.")

