"""Genera gráficos comparativos CPLEX vs. Gurobi para presentación (Tarea 3).

Uso:
    python src/compare_solvers_charts.py
    python src/compare_solvers_charts.py --output-dir results/graficos_comparacion
"""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_GUROBI_CSV = REPO_ROOT / "results" / "results.csv"
DEFAULT_CPLEX_CSV = REPO_ROOT / "results" / "cplex_results_all.csv"
DEFAULT_CPLEX_SENS_CSV = REPO_ROOT / "results" / "cplex_sensitivity_all.csv"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "results" / "graficos_comparacion"

CONFIG_LABELS = [
    ("base", "Baseline"),
    ("cuts_0", "Cuts=0"),
    ("presolve_0", "Presolve=0"),
    ("mipfocus_1", "MIPFocus=1"),
    ("mipfocus_3", "MIPFocus=3"),
    ("heuristics_0", "Heuristics=0"),
    ("tuned", "Tune"),
]

INSTANCES = [
    ("instance_1_c101_15c", "Instancia C101 (15 clientes)"),
    ("instance_2_rc101_15c", "Instancia RC101 (15 clientes)"),
]

COLORS = {
    "Gurobi": "#1D4ED8",
    "CPLEX": "#0D9488",
    "LP": "#64748B",
    "TuneCost": "#F59E0B",
    "Saturated": "#DC2626",
    "Used": "#0D9488",
    "Slack": "#CBD5E1",
}


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


def _load_latest_by_instance_experiment(csv_path):
    """Carga un CSV de resultados y conserva la última fila por (instance, experiment)."""
    df = pd.read_csv(csv_path)
    df = df[df["experiment"].notna() & df["instance"].notna()].copy()
    dedup = df.drop_duplicates(subset=["instance", "experiment"], keep="last")
    return {
        (row["instance"], row["experiment"]): row
        for _, row in dedup.iterrows()
    }


def _save_fig(fig, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=240, bbox_inches="tight")
    plt.close(fig)
    return path


def _plot_grouped_by_config(
    gurobi, cplex, metric, ylabel, title, footer, fmt, output_path, integer=False
):
    """Dibuja barras agrupadas Gurobi vs. CPLEX por configuración en C101 y RC101."""
    fig, axes = plt.subplots(1, 2, figsize=(14.5, 5.8))
    keys = [k for k, _ in CONFIG_LABELS]
    labels = [lbl for _, lbl in CONFIG_LABELS]
    x = list(range(len(keys)))
    width = 0.38

    for ax, (inst, inst_title) in zip(axes, INSTANCES):
        g_vals = [float(gurobi[inst, k][metric]) for k in keys]
        c_vals = [float(cplex[inst, k][metric]) for k in keys]

        b1 = ax.bar(
            [i - width / 2 for i in x],
            g_vals,
            width,
            label="Gurobi",
            color=COLORS["Gurobi"],
        )
        b2 = ax.bar(
            [i + width / 2 for i in x],
            c_vals,
            width,
            label="CPLEX",
            color=COLORS["CPLEX"],
        )

        if integer:
            ax.bar_label(
                b1,
                labels=[f"{int(round(v)):,}" for v in g_vals],
                padding=3,
                fontsize=8.2,
                rotation=90,
            )
            ax.bar_label(
                b2,
                labels=[f"{int(round(v)):,}" for v in c_vals],
                padding=3,
                fontsize=8.2,
                rotation=90,
            )
        else:
            ax.bar_label(b1, fmt=fmt, padding=3, fontsize=8.5, rotation=90)
            ax.bar_label(b2, fmt=fmt, padding=3, fontsize=8.5, rotation=90)

        max_val = max(g_vals + c_vals)
        ax.set_ylim(0, max_val * 1.28)
        ax.set_xticks(x, labels, rotation=32, ha="right")
        ax.set_ylabel(ylabel)
        ax.set_title(inst_title)
        ax.grid(axis="y", alpha=0.25)
        ax.set_axisbelow(True)
        ax.legend(frameon=True)

    fig.suptitle(title, fontsize=14, fontweight="bold", y=1.02)
    fig.text(0.5, -0.03, footer, ha="center", fontsize=9.5, color="#475569")
    fig.tight_layout()
    return _save_fig(fig, output_path)


def chart_runtime_by_config(gurobi, cplex, output_dir):
    """Barras agrupadas de tiempo de resolución (s) por configuración y solver."""
    return _plot_grouped_by_config(
        gurobi,
        cplex,
        metric="runtime_seconds",
        ylabel="Tiempo de resolución (s)",
        title="Comparación de tiempo de resolución por configuración: Gurobi vs. CPLEX",
        footer="Mismo computador, Threads=1, TimeLimit=600 s. En Tune se grafica solo la resolución posterior al ajuste.",
        fmt="%.2f",
        output_path=output_dir / "comparacion_tiempos_configs.png",
    )


def chart_nodes_by_config(gurobi, cplex, output_dir):
    """Barras agrupadas de nodos explorados por configuración y solver."""
    return _plot_grouped_by_config(
        gurobi,
        cplex,
        metric="nodes",
        ylabel="Nodos explorados (Branch & Bound)",
        title="Comparación de nodos explorados por configuración: Gurobi vs. CPLEX",
        footer="Mismo computador, Threads=1, TimeLimit=600 s. Menor cantidad de nodos refleja podas/cortes más efectivos.",
        fmt="%.0f",
        output_path=output_dir / "comparacion_nodos_explorados.png",
        integer=True,
    )


def chart_relative_change_vs_baseline(gurobi, cplex, output_dir):
    """Cambio porcentual de tiempo respecto al Baseline propio de cada solver."""
    fig, axes = plt.subplots(1, 2, figsize=(14.5, 5.8))
    non_base = [(k, lbl) for k, lbl in CONFIG_LABELS if k != "base"]
    keys = [k for k, _ in non_base]
    labels = [lbl for _, lbl in non_base]
    y = list(range(len(keys)))
    height = 0.36

    for ax, (inst, inst_title) in zip(axes, INSTANCES):
        g_base = float(gurobi[inst, "base"]["runtime_seconds"])
        c_base = float(cplex[inst, "base"]["runtime_seconds"])

        g_pct = [
            (float(gurobi[inst, k]["runtime_seconds"]) - g_base) / g_base * 100
            for k in keys
        ]
        c_pct = [
            (float(cplex[inst, k]["runtime_seconds"]) - c_base) / c_base * 100
            for k in keys
        ]

        b1 = ax.barh(
            [i + height / 2 for i in y],
            g_pct,
            height,
            label=f"Gurobi (base={g_base:.2f} s)",
            color=COLORS["Gurobi"],
        )
        b2 = ax.barh(
            [i - height / 2 for i in y],
            c_pct,
            height,
            label=f"CPLEX (base={c_base:.2f} s)",
            color=COLORS["CPLEX"],
        )

        ax.axvline(0, color="#0F172A", linewidth=1.0)
        for bars in (b1, b2):
            for bar in bars:
                val = bar.get_width()
                offset = 8 if val >= 0 else -8
                ha = "left" if val >= 0 else "right"
                ax.annotate(
                    f"{val:+.1f}%",
                    xy=(val, bar.get_y() + bar.get_height() / 2),
                    xytext=(offset / 2, 0),
                    textcoords="offset points",
                    va="center",
                    ha=ha,
                    fontsize=8.5,
                    fontweight="bold",
                )

        min_v, max_v = min(g_pct + c_pct), max(g_pct + c_pct)
        pad_left = max(145, abs(min_v) * 1.15)
        pad_right = max(95, max_v * 0.25)
        ax.set_xlim(min(0, min_v) - pad_left, max_v + pad_right)
        ax.set_yticks(y, labels)
        ax.invert_yaxis()
        ax.set_xlabel("Cambio de tiempo respecto al Baseline (%)  [negativo = más rápido]")
        ax.set_title(inst_title)
        ax.grid(axis="x", alpha=0.25)
        ax.set_axisbelow(True)
        ax.legend(loc="lower right", frameon=True)

    fig.suptitle(
        "Sensibilidad a configuraciones respecto al Baseline de cada solver",
        fontsize=14,
        fontweight="bold",
        y=1.02,
    )
    fig.tight_layout()
    return _save_fig(fig, output_dir / "comparacion_impacto_vs_baseline.png")


def chart_tuning_cost_vs_solve(gurobi, cplex, output_dir):
    """Compara tiempo Baseline, resolución post-tuning y costo de tuning."""
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.4))
    solvers = [("Gurobi", gurobi), ("CPLEX", cplex)]
    categories = ["Baseline", "Post-Tuning", "Proceso Tuning"]
    x = list(range(len(categories)))
    width = 0.36

    for ax, (inst, inst_title) in zip(axes, INSTANCES):
        vals = {}
        for name, data in solvers:
            vals[name] = [
                float(data[inst, "base"]["runtime_seconds"]),
                float(data[inst, "tuned"]["runtime_seconds"]),
                float(data[inst, "tuned"]["tuning_wall_seconds"]),
            ]

        b1 = ax.bar(
            [i - width / 2 for i in x],
            vals["Gurobi"],
            width,
            label="Gurobi",
            color=COLORS["Gurobi"],
        )
        b2 = ax.bar(
            [i + width / 2 for i in x],
            vals["CPLEX"],
            width,
            label="CPLEX",
            color=COLORS["CPLEX"],
        )

        ax.bar_label(b1, fmt="%.2f s", padding=3, fontsize=9)
        ax.bar_label(b2, fmt="%.2f s", padding=3, fontsize=9)

        max_v = max(vals["Gurobi"] + vals["CPLEX"])
        ax.set_ylim(0, max_v * 1.18)
        ax.set_xticks(x, categories)
        ax.set_ylabel("Tiempo (s)")
        ax.set_title(inst_title)
        ax.grid(axis="y", alpha=0.25)
        ax.set_axisbelow(True)
        ax.legend(frameon=True)

    fig.suptitle(
        "Costo del ajuste automático (tuning) vs. tiempo de resolución",
        fontsize=14,
        fontweight="bold",
        y=1.02,
    )
    c_b = float(cplex["instance_1_c101_15c", "base"]["runtime_seconds"])
    c_t = float(cplex["instance_1_c101_15c", "tuned"]["runtime_seconds"])
    ratio = c_b / c_t if c_t else 0.0
    fig.text(
        0.5,
        -0.03,
        f"tune_time_limit_seconds = 120 s por instancia. En C101 el tuning de CPLEX pasó de {c_b:.2f} s a {c_t:.2f} s ({ratio:.2f}x).",
        ha="center",
        fontsize=9.5,
        color="#475569",
    )
    fig.tight_layout()
    return _save_fig(fig, output_dir / "comparacion_tuning_tiempo.png")


def chart_lp_milp_validation(gurobi, cplex, output_dir):
    """Validación cruzada de LP relajado, óptimo MILP y brecha de integralidad."""
    fig, ax = plt.subplots(figsize=(10.5, 5.6))

    groups = [
        ("C101\nGurobi", "instance_1_c101_15c", gurobi),
        ("C101\nCPLEX", "instance_1_c101_15c", cplex),
        ("RC101\nGurobi", "instance_2_rc101_15c", gurobi),
        ("RC101\nCPLEX", "instance_2_rc101_15c", cplex),
    ]
    x = [0, 1, 2.4, 3.4]
    width = 0.36

    lp_vals = [float(src[inst, "relajado"]["objective"]) for _, inst, src in groups]
    milp_vals = [float(src[inst, "base"]["objective"]) for _, inst, src in groups]
    gaps = [float(src[inst, "base"]["integrality_gap_pct"]) for _, inst, src in groups]

    b1 = ax.bar(
        [i - width / 2 for i in x],
        lp_vals,
        width,
        label="Relajación continua (LP)",
        color=COLORS["LP"],
    )
    b2 = ax.bar(
        [i + width / 2 for i in x],
        milp_vals,
        width,
        label="Óptimo entero (MILP)",
        color=COLORS["TuneCost"],
    )

    ax.bar_label(b1, fmt="%.2f", padding=3, fontsize=9)
    ax.bar_label(b2, fmt="%.2f", padding=3, fontsize=9)

    for pos, v_milp, gap in zip(x, milp_vals, gaps):
        ax.text(
            pos,
            v_milp + 55,
            f"Brecha: {gap:.2f}%",
            ha="center",
            fontsize=9.5,
            fontweight="bold",
            color="#0F172A",
            bbox=dict(boxstyle="round,pad=0.22", facecolor="#F8FAFC", edgecolor="#CBD5E1"),
        )

    ax.axvline(1.7, color="#CBD5E1", linestyle="--", linewidth=1.2)
    ax.set_xticks(x, [lbl for lbl, _, _ in groups])
    ax.set_ylim(0, max(milp_vals) * 1.24)
    ax.set_ylabel("Distancia total (valor objetivo)")
    ax.set_title(
        "Validación cruzada de objetivos y brecha de integralidad: Gurobi vs. CPLEX",
        pad=14,
    )
    ax.grid(axis="y", alpha=0.25)
    ax.set_axisbelow(True)
    ax.legend(loc="upper left", frameon=True)
    fig.tight_layout()
    return _save_fig(fig, output_dir / "comparacion_validacion_lp_milp.png")


def chart_capacity_sensitivity(cplex_sens_csv, output_dir):
    """Uso de capacidad y holgura por par (ruta, día) en el análisis de sensibilidad CPLEX."""
    df = pd.read_csv(cplex_sens_csv)
    df = df[df["experiment"] == "sensitivity_capacity"].copy()

    fig, axes = plt.subplots(1, 2, figsize=(14.5, 5.6))

    for ax, (inst, inst_title) in zip(axes, INSTANCES):
        sub = df[df["instance"] == inst].sort_values(["route", "day"]).copy()
        labels = [f"R{int(r)}-D{int(d)}" for r, d in zip(sub["route"], sub["day"])]
        rhs = sub["capacity_rhs"].astype(float).tolist()
        slack = sub["slack"].astype(float).tolist()
        used = [q - s for q, s in zip(rhs, slack)]
        bar_colors = [
            COLORS["Saturated"] if s <= 1e-9 else COLORS["Used"] for s in slack
        ]

        x = list(range(len(labels)))
        ax.bar(x, used, color=bar_colors)
        ax.bar(
            x,
            slack,
            bottom=used,
            color=COLORS["Slack"],
            edgecolor="#94A3B8",
        )
        ax.axhline(rhs[0], color="#0F172A", linestyle="--", linewidth=1.1)

        for idx, (u, s) in enumerate(zip(used, slack)):
            ax.text(idx, u / 2, f"{u:.0f}", ha="center", va="center", color="white", fontweight="bold", fontsize=8.5)
            if s > 0:
                ax.text(idx, u + s / 2, f"+{s:.0f}", ha="center", va="center", color="#334155", fontsize=8)

        ax.set_xticks(x, labels)
        ax.set_ylim(0, rhs[0] * 1.28)
        ax.set_ylabel("Demanda / Capacidad")
        ax.set_title(f"{inst_title} (Q = {rhs[0]:.0f})")
        ax.grid(axis="y", alpha=0.25)
        ax.set_axisbelow(True)
        handles = [
            Patch(facecolor=COLORS["Used"], label="Capacidad utilizada (Q - holgura)"),
            Patch(facecolor=COLORS["Saturated"], label="Par saturado (slack=0, Pi=0)"),
            Patch(facecolor=COLORS["Slack"], edgecolor="#94A3B8", label="Holgura disponible (slack)"),
            plt.Line2D([0], [0], color="#0F172A", linestyle="--", linewidth=1.1, label=f"Capacidad Q={rhs[0]:.0f}"),
        ]
        ax.legend(handles=handles, loc="upper right", fontsize=8.2, ncol=2, frameon=True)

    fig.suptitle(
        "Sensibilidad de capacidad (LP fijado): carga asignada y holgura por ruta y día",
        fontsize=14,
        fontweight="bold",
        y=1.02,
    )
    fig.text(
        0.5,
        -0.03,
        "En ambos solvers todos los pares tienen Pi=0.0 (LP con X y Z fijos); rutas homogéneas con idéntico multiconjunto diario de holguras.",
        ha="center",
        fontsize=9.5,
        color="#475569",
    )
    fig.tight_layout()
    return _save_fig(fig, output_dir / "comparacion_sensibilidad_capacidad.png")


def main():
    parser = argparse.ArgumentParser(
        description="Generar gráficos comparativos CPLEX vs. Gurobi."
    )
    parser.add_argument("--gurobi-csv", default=str(DEFAULT_GUROBI_CSV))
    parser.add_argument("--cplex-csv", default=str(DEFAULT_CPLEX_CSV))
    parser.add_argument("--cplex-sens-csv", default=str(DEFAULT_CPLEX_SENS_CSV))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    args = parser.parse_args()

    _configure_style()
    gurobi = _load_latest_by_instance_experiment(args.gurobi_csv)
    cplex = _load_latest_by_instance_experiment(args.cplex_csv)
    output_dir = Path(args.output_dir)

    generated = [
        chart_runtime_by_config(gurobi, cplex, output_dir),
        chart_nodes_by_config(gurobi, cplex, output_dir),
        chart_relative_change_vs_baseline(gurobi, cplex, output_dir),
        chart_tuning_cost_vs_solve(gurobi, cplex, output_dir),
        chart_lp_milp_validation(gurobi, cplex, output_dir),
        chart_capacity_sensitivity(args.cplex_sens_csv, output_dir),
    ]
    for path in generated:
        print(f"Generado: {path}")


if __name__ == "__main__":
    main()
