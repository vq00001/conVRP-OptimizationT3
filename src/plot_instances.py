"""Genera gráficos de las instancias corregidas conVRP para la presentación.

Uso:
    python src/plot_instances.py
    python src/plot_instances.py --output-dir results/graficos_instancias
"""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np

from instance_loader import load_instance

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "results" / "graficos_instancias"

INSTANCES = [
    ("instance_1_c101_15c.json", "Instancia C101 (agrupada, Q = 85)"),
    ("instance_2_rc101_15c.json", "Instancia RC101 (mixta, Q = 90)"),
]


def _configure_style():
    plt.rcParams.update(
        {
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.titleweight": "bold",
            "axes.labelsize": 10.5,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )


def _save_fig(fig, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=240, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_spatial_instances(instances, output_dir):
    """Mapa espacial (x, y) del depósito y los 15 clientes según frecuencia de pedido."""
    fig, axes = plt.subplots(1, 2, figsize=(14.0, 6.2))

    for ax, (inst, title) in zip(axes, instances):
        depot = inst["depot"]
        nodes = inst["nodes"]
        days = inst["days"]

        dx, dy = nodes[depot]["x"], nodes[depot]["y"]
        ax.scatter(
            [dx],
            [dy],
            marker="*",
            s=360,
            color="#DC2626",
            edgecolor="#7F1D1D",
            linewidth=1.0,
            zorder=5,
        )
        ax.annotate(
            f"Depósito (0)\n[{inst['depot_window'][0]:.0f}, {inst['depot_window'][1]:.0f}]",
            xy=(dx, dy),
            xytext=(0, -22),
            textcoords="offset points",
            ha="center",
            va="top",
            fontsize=9,
            fontweight="bold",
            color="#991B1B",
        )

        for cid in inst["customers"]:
            node = nodes[cid]
            active_days = sum(1 for t in days if node["demand_by_day"][t] > 0)
            face = "#0D9488" if active_days == len(days) else "#2563EB"
            edge = "#115E59" if active_days == len(days) else "#1E3A8A"
            ax.scatter(
                [node["x"]],
                [node["y"]],
                s=185,
                color=face,
                edgecolor=edge,
                linewidth=1.0,
                zorder=4,
            )
            ax.text(
                node["x"],
                node["y"],
                str(cid),
                ha="center",
                va="center",
                color="white",
                fontsize=7.8,
                fontweight="bold",
                zorder=6,
            )

        xs = [nodes[nid]["x"] for nid in nodes]
        ys = [nodes[nid]["y"] for nid in nodes]
        ax.set_xlim(min(xs) - 5, max(xs) + 5)
        ax.set_ylim(min(ys) - 9, max(ys) + 5)
        ax.set_xlabel("Coordenada X")
        ax.set_ylabel("Coordenada Y")
        ax.set_title(title)
        ax.grid(True, alpha=0.25)
        ax.set_axisbelow(True)

    legend_items = [
        Line2D(
            [0],
            [0],
            marker="*",
            color="w",
            label="Depósito (nodo 0)",
            markerfacecolor="#DC2626",
            markeredgecolor="#7F1D1D",
            markersize=14,
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            label="Cliente activo 3 días",
            markerfacecolor="#0D9488",
            markeredgecolor="#115E59",
            markersize=10,
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            label="Cliente activo 2 días",
            markerfacecolor="#2563EB",
            markeredgecolor="#1E3A8A",
            markersize=10,
        ),
    ]
    fig.legend(
        handles=legend_items,
        loc="lower center",
        ncol=3,
        bbox_to_anchor=(0.5, -0.02),
        frameon=True,
        fontsize=9.5,
    )
    fig.suptitle(
        "Distribución espacial de las instancias corregidas (15 clientes, 3 días, 3 rutas)",
        fontsize=14,
        fontweight="bold",
        y=1.01,
    )
    fig.tight_layout(rect=(0, 0.05, 1, 0.98))
    return _save_fig(fig, output_dir / "instancias_mapa_espacial.png")


def plot_multiday_demand(instances, output_dir):
    """Matriz de demanda por cliente y día evidenciando la estructura multi-día real."""
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 6.4))

    for ax, (inst, title) in zip(axes, instances):
        customers = inst["customers"]
        days = inst["days"]
        matrix = np.array(
            [
                [inst["nodes"][c]["demand_by_day"][t] for t in days]
                for c in customers
            ],
            dtype=float,
        )

        # Fondo coloreado según demanda; 0 destacado en gris claro
        cmap = plt.cm.YlGnBu.copy()
        masked = np.ma.masked_where(matrix == 0, matrix)
        cmap.set_bad(color="#E2E8F0")
        ax.imshow(masked, cmap=cmap, aspect="auto", vmin=5, vmax=45)

        for r_idx, c in enumerate(customers):
            for c_idx, t in enumerate(days):
                val = matrix[r_idx, c_idx]
                if val == 0:
                    ax.text(
                        c_idx,
                        r_idx,
                        "—",
                        ha="center",
                        va="center",
                        color="#64748B",
                        fontsize=10,
                        fontweight="bold",
                    )
                else:
                    txt_color = "white" if val >= 25 else "#0F172A"
                    ax.text(
                        c_idx,
                        r_idx,
                        f"{val:.0f}",
                        ha="center",
                        va="center",
                        color=txt_color,
                        fontsize=9,
                        fontweight="bold",
                    )

        fleet_cap = len(inst["vehicles"]) * inst["capacity"]
        day_labels = []
        for idx, t in enumerate(days):
            tot = matrix[:, idx].sum()
            act = int((matrix[:, idx] > 0).sum())
            pct = tot / fleet_cap * 100
            day_labels.append(f"Día {t}\n{act}/15 act. ({pct:.1f}% cap.)")

        ax.set_xticks(range(len(days)), day_labels)
        ax.set_yticks(range(len(customers)), [f"Cliente {c}" for c in customers])
        ax.set_title(title)

        # Líneas sutiles entre celdas
        ax.set_xticks(np.arange(-0.5, len(days), 1), minor=True)
        ax.set_yticks(np.arange(-0.5, len(customers), 1), minor=True)
        ax.grid(which="minor", color="white", linestyle="-", linewidth=1.2)
        ax.tick_params(which="minor", bottom=False, left=False)

    legend_handles = [
        Patch(facecolor="#E2E8F0", edgecolor="#94A3B8", label="Sin demanda (0): no se visita ese día"),
        Patch(facecolor="#41B6C4", edgecolor="#0F172A", label="Demanda activa (> 0): visita obligatoria"),
    ]
    fig.legend(
        handles=legend_handles,
        loc="lower center",
        ncol=2,
        bbox_to_anchor=(0.5, -0.02),
        frameon=True,
        fontsize=9.5,
    )
    fig.suptitle(
        "Estructura multi-día real: demanda por cliente y día (36 órdenes activas por instancia)",
        fontsize=14,
        fontweight="bold",
        y=1.01,
    )
    fig.tight_layout(rect=(0, 0.04, 1, 0.98))
    return _save_fig(fig, output_dir / "instancias_estructura_multidia.png")


def main():
    parser = argparse.ArgumentParser(
        description="Graficar instancias conVRP para presentación."
    )
    parser.add_argument("--data-dir", default=str(DATA_DIR))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    args = parser.parse_args()

    _configure_style()
    data_dir = Path(args.data_dir)
    output_dir = Path(args.output_dir)
    loaded = [(load_instance(data_dir / fn), title) for fn, title in INSTANCES]

    for path in (
        plot_spatial_instances(loaded, output_dir),
        plot_multiday_demand(loaded, output_dir),
    ):
        print(f"Generado: {path}")


if __name__ == "__main__":
    main()
