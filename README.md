# conVRP-OptimizationT3

Modelo de ruteo consistente (**conVRP**) desarrollado para la asignatura **Optimización** de la Universidad de Concepción (continuación de la Tarea 2 hacia la **Tarea 3** con experimentación y comparación entre **Gurobi** y **CPLEX**).

## Requisitos

- Python 3.9+ (probado en CPLEX con Python 3.12)
- Dependencias en `requirements.txt` (`gurobipy`, `cplex`, `docplex`, `pandas`)

```bash
pip install -r requirements.txt
```

## Estructura del repositorio

```text
conVRP-OptimizationT3/
├── data/
│   ├── instance_1_c101_15c.json
│   └── instance_2_rc101_15c.json
├── results/
│   ├── cplex/                         # Corridas individuales de CPLEX por run_id
│   ├── graficos_finales/              # Gráficos generados con graph_generator.py
│   ├── cplex_results_all.csv          # Acumulado de métricas CPLEX
│   ├── cplex_sensitivity_all.csv      # Acumulado de sensibilidad CPLEX
│   ├── results.csv                    # Métricas de referencia Gurobi
│   ├── sensitivity.csv                # Sensibilidad de capacidad Gurobi
│   ├── guia_lectura_resultados.md     # Guía para interpretar columnas y métricas
│   └── veredicto_cplex_vs_gurobi.md   # Comparación y veredicto CPLEX vs. Gurobi
└── src/
    ├── cplex_model.py                 # Construcción del modelo en CPLEX (docplex)
    ├── gurobi_model.py                # Construcción del modelo en Gurobi
    ├── experiments_cplex.py           # Suite reproducible de experimentos CPLEX
    ├── experiments.py                 # Suite de experimentos Gurobi
    ├── ejecucion_cplex.md             # Documentación detallada de experiments_cplex.py
    ├── instance_loader.py             # Carga y validación de instancias JSON
    ├── utils.py                       # Conjuntos y parámetros compartidos
    └── graph_generator.py             # Generación de gráficos desde CSV de resultados
```

## Instrucciones de ejecución

### 1. Experimentos con CPLEX (T3)

Las instancias de 15 clientes (`instance_1_c101_15c.json` e `instance_2_rc101_15c.json`) generan `1515` variables y `1755` restricciones, por lo que superan el límite de licencia comunitaria (`1000`) y requieren `--allow-large` con licencia académica/completa:

```bash
# Corrida simple (1 réplica, seed 0, incluye tuning)
python src/experiments_cplex.py --allow-large -v

# Prueba rápida sin tuning
python src/experiments_cplex.py --repeats 1 --skip-tuning --allow-large -v --tag prueba

# Múltiples réplicas (ej. 5 semillas)
python src/experiments_cplex.py --repeats 5 --seed-base 0 --tag final --allow-large -v
```

Cada ejecución guarda los resultados en `results/cplex/<run_id>/` (`cplex_results_<run_id>.csv`, `cplex_sensitivity_<run_id>.csv` y `cplex_run_<run_id>.json`) y los acumula en `results/cplex_results_all.csv` y `results/cplex_sensitivity_all.csv`. Consulta [src/ejecucion_cplex.md](src/ejecucion_cplex.md) para ver todas las opciones disponibles.

### 2. Experimentos con Gurobi (T2)

```bash
python3 ./src/experiments.py
```

Los resultados se guardan en `results/results.csv` y `results/sensitivity.csv`.

### 3. Gráficos de resultados

```bash
python3 ./src/graph_generator.py ./results/results.csv --output-dir ./results/graficos_finales
```

## Análisis y resultados

- Comparación y veredicto **CPLEX vs. Gurobi**: [results/veredicto_cplex_vs_gurobi.md](results/veredicto_cplex_vs_gurobi.md)
- Guía de interpretación de columnas y métricas: [results/guia_lectura_resultados.md](results/guia_lectura_resultados.md)
