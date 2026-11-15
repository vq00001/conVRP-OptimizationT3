# conVRP-OptimizationT3

Modelo de ruteo consistente (**conVRP**, basado en Campelo et al., 2019) corregido y reimplementado en **Gurobi** y **CPLEX (docplex/cplex)** para la **Tarea Computacional 3** de Optimización (Universidad de Concepción).

## Requisitos

- Python 3.9+ (probado en Python 3.12 con `gurobipy 14.0.0` y `cplex 22.2.0.0`)
- Dependencias en `requirements.txt` (`gurobipy`, `cplex`, `docplex`, `pandas`) más `matplotlib` para gráficos.

```bash
pip install -r requirements.txt
```

## Estructura del repositorio

```text
conVRP-OptimizationT3/
├── data/
│   ├── instance_1_c101_15c.json           # Instancia corregida C101 (15 clientes, 3 días, 3 rutas)
│   └── instance_2_rc101_15c.json          # Instancia corregida RC101 (15 clientes, 3 días, 3 rutas)
├── results/
│   ├── cplex/                             # Corridas individuales de CPLEX por run_id
│   ├── logs/
│   │   ├── cplex/                         # Logs nativos de CPLEX (18 archivos .log)
│   │   └── gurobi/                        # Logs nativos de Gurobi (18 archivos .log)
│   ├── graficos_instancias/               # Mapas espaciales y estructura multi-día
│   ├── graficos_comparacion/              # Gráficos comparativos Gurobi vs. CPLEX
│   ├── cplex_results_all.csv              # Métricas CPLEX en el mismo computador
│   ├── cplex_sensitivity_all.csv          # Sensibilidad CPLEX
│   ├── results.csv                        # Métricas Gurobi en el mismo computador
│   ├── sensitivity.csv                    # Sensibilidad Gurobi
│   ├── guia_lectura_resultados.md         # Guía para interpretar columnas y métricas
│   └── veredicto_cplex_vs_gurobi.md       # Análisis y veredicto Gurobi vs. CPLEX
└── src/
    ├── cplex_model.py                     # Construcción del modelo conVRP en CPLEX (docplex)
    ├── gurobi_model.py                    # Construcción del modelo conVRP en Gurobi
    ├── utils.py                           # Conjuntos activos por día y parámetros compartidos
    ├── instance_loader.py                 # Carga y validación de instancias JSON
    ├── generate_instances.py              # Generador de instancias multi-día desde Solomon
    ├── main.py                            # Ejecución simple en Gurobi (MILP + LP)
    ├── solver.py                          # Wrapper de resolución y extracción de métricas Gurobi
    ├── experiments_cplex.py               # Suite reproducible de experimentos y logs CPLEX
    ├── experiments.py                     # Suite de experimentos y logs Gurobi
    ├── ejecucion_cplex.md                 # Documentación detallada de experiments_cplex.py
    ├── graph_generator.py                 # Gráficos desde CSV individual
    ├── plot_instances.py                  # Gráficos espaciales y de demanda multi-día
    └── compare_solvers_charts.py          # Gráficos comparativos Gurobi vs. CPLEX
```

## Instrucciones de ejecución

### 1. Experimentos con CPLEX

Las instancias de 15 clientes (`instance_1_c101_15c.json` e `instance_2_rc101_15c.json`) generan `1515` variables y `1755` restricciones, por lo que requieren `--allow-large` con licencia académica/completa de CPLEX:

```bash
python src/experiments_cplex.py --allow-large --overwrite-master -v
```

Cada corrida guarda CSV, JSON de metadatos y logs en `results/cplex/<run_id>/`, además de consolidar en `results/cplex_results_all.csv`, `results/cplex_sensitivity_all.csv` y `results/logs/cplex/`. Ver [src/ejecucion_cplex.md](src/ejecucion_cplex.md) para más flags (`--repeats`, `--skip-tuning`, `--tag`).

### 2. Experimentos con Gurobi

```bash
python src/experiments.py --allow-large --overwrite -v
```

Los resultados, análisis de sensibilidad y logs nativos se guardan en `results/results.csv`, `results/sensitivity.csv` y `results/logs/gurobi/`. Para una corrida rápida de una instancia (`MILP` + `LP`), ejecutar `python src/main.py`.

### 3. Visualizaciones

```bash
python src/plot_instances.py
python src/compare_solvers_charts.py
```

## Análisis y resultados

- Comparación y veredicto **CPLEX vs. Gurobi**: [results/veredicto_cplex_vs_gurobi.md](results/veredicto_cplex_vs_gurobi.md)
- Guía de interpretación de columnas y métricas: [results/guia_lectura_resultados.md](results/guia_lectura_resultados.md)
