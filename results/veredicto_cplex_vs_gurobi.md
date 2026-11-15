# Veredicto comparativo: CPLEX vs. Gurobi (conVRP)

Análisis de la corrida experimental de **CPLEX 22.2.0.0** (`run_id`: `20261115_140551`, `seed = 0`) frente a las corridas registradas de **Gurobi** (`results/results.csv` y `results/results_2.csv`) sobre las dos instancias calibradas de 15 clientes (`1515` variables y `1755` restricciones).

> **Archivos fuente**
> - CPLEX resultados: `results/cplex/20261115_140551/cplex_results_20261115_140551.csv`
> - CPLEX sensibilidad: `results/cplex/20261115_140551/cplex_sensitivity_20261115_140551.csv`
> - CPLEX metadatos: `results/cplex/20261115_140551/cplex_run_20261115_140551.json`
> - Gurobi resultados: `results/results.csv` (idéntico a `results/results_1.csv`) y `results/results_2.csv`

---

## 1. Veredicto general

Los resultados son **plenamente válidos y consistentes** entre ambos solvers:

1. **Equivalencia matemática verificada**: CPLEX y Gurobi alcanzan exactamente los mismos óptimos enteros (`511.19` en C101 y `893.66` en RC101), las mismas cotas de relajación lineal (`129.87` y `156.66`), las mismas brechas de integralidad (`74.59 %` y `82.47 %`) y los mismos valores de holgura, precio sombra y rangos RHS en sensibilidad de capacidad.
2. **Desempeño por instancia**:
   - En **`instance_1_c101_15c`**, Gurobi fue considerablemente más rápido en `base` (`7.67 s` / `10.49 s` vs. `76.64 s` en CPLEX). Sin embargo, el **tuning de CPLEX** y **`mipfocus_1`** recortaron el tiempo de CPLEX a **`19.79 s`** y **`22.56 s`**, respectivamente (~3.4x–3.9x más rápido que el `base` de CPLEX).
   - En **`instance_2_rc101_15c`**, ambos solvers resolvieron en menos de un segundo en `base`, con CPLEX ligeramente más rápido (`0.42 s` vs. `0.57 s` / `0.59 s` en Gurobi) y un tuning casi instantáneo (`2.45 s`).

*(Nota: la corrida de CPLEX corresponde a 1 réplica con `seed=0`, mientras que `results.csv` y `results_2.csv` provienen de ejecuciones previas de Gurobi registradas en el repositorio, por lo que las diferencias finas de tiempo también reflejan condiciones de ejecución independientes).*

---

## 2. Validación del modelo y relajación continua

| Instancia | Métrica | CPLEX | Gurobi |
|---|---|---:|---:|
| `instance_1_c101_15c` | Óptimo MILP (`base`) | `511.19` | `511.19` |
| `instance_1_c101_15c` | Relajación LP (`relajado`) | `129.87` | `129.87` |
| `instance_1_c101_15c` | Brecha de integralidad (`%`) | `74.59 %` | `74.59 %` |
| `instance_2_rc101_15c` | Óptimo MILP (`base`) | `893.66` | `893.66` |
| `instance_2_rc101_15c` | Relajación LP (`relajado`) | `156.66` | `156.66` |
| `instance_2_rc101_15c` | Brecha de integralidad (`%`) | `82.47 %` | `82.47 %` |

La **brecha de integralidad alta** (`74.59 %` y `82.47 %`) es característica de formulaciones de ruteo con ventanas de tiempo basadas en restricciones **Big-M**, donde la relajación continua debilita fuertemente el acoplamiento temporal.

---

## 3. Comparación por configuración (`Threads=1`, `TimeLimit=600 s`)

### 3.1 `instance_1_c101_15c`

| Experimento | CPLEX Tiempo (s) | CPLEX Gap (%) | CPLEX Nodos | CPLEX Estado | Gurobi Tiempo `results.csv` / `results_2.csv` (s) |
|---|---:|---:|---:|---|---:|
| `base` | `76.64` | `0.0078` | `32,292` | `integer optimal, tolerance` | `7.67` / `10.49` |
| `cuts_0` | `71.10` | `0.0079` | `76,370` | `integer optimal, tolerance` | `38.55` / `53.23` |
| `presolve_0` | `88.37` | `0.0094` | `65,672` | `integer optimal, tolerance` | `38.97` / `56.58` |
| `mipfocus_1` | `22.56` | `0.0074` | `20,518` | `integer optimal, tolerance` | `10.20` / `13.90` |
| `mipfocus_3` | `169.75` | `0.0099` | `44,372` | `integer optimal, tolerance` | `21.18` / `30.16` |
| `heuristics_0` | `36.74` | `0.0000` | `20,968` | `integer optimal solution` | `6.67` / `6.68` |
| `relajado` | `0.0041` | `0.0000` | `0` | `optimal` | `0.0077` / `0.0081` |
| `tuned` | `19.79` | `0.0061` | `15,809` | `integer optimal, tolerance` | `7.64` / `8.81` |

- **Tuning C101**: CPLEX tardó `185.33 s` de pared (`tune_time_limit_seconds = 120.0`), pero la configuración afinada (`parameters.mip.limits.cutpasses=1`, `parameters.mip.strategy.probe=-1`, `parameters.mip.strategy.variableselect=4`) redujo el tiempo de resolución en **`-56.84 s`** respecto a `base` (`76.64 s -> 19.79 s`) y superó a la mejor configuración manual (`mipfocus_1`: `22.56 s`) por `2.77 s`. En Gurobi, el tuning demoró `99.86 s` / `98.75 s` y dio un tiempo casi igual al `base` (`7.64 s` vs. `7.67 s` en `results.csv`, y `8.81 s` vs. `10.49 s` en `results_2.csv`).
- **Estrategia MIP**: En CPLEX, **`mipfocus_1`** (énfasis en factibilidad) aceleró más de 3 veces respecto a `base`, mientras que **`mipfocus_3`** (énfasis en cota dual) más que duplicó el tiempo (`169.75 s`). Esto es consistente con la relajación LP débil (`74.59 %` de brecha), donde priorizar soluciones enteras y ramificación rinde más que intentar cerrar la cota dual por cortes/procesamiento pesado.
- **Presolve y cortes**: Desactivar presolve (`presolve_0`) empeoró en ambos solvers (`88.37 s` en CPLEX; `38.97 s` / `56.58 s` en Gurobi). Desactivar cortes (`cuts_0`) penalizó fuertemente a Gurobi (`38.55 s` / `53.23 s`), mientras que en CPLEX mantuvo un tiempo similar (`71.10 s`) a costa de más del doble de nodos (`76,370` vs. `32,292`).

### 3.2 `instance_2_rc101_15c`

| Experimento | CPLEX Tiempo (s) | CPLEX Gap (%) | CPLEX Nodos | CPLEX Estado | Gurobi Tiempo `results.csv` / `results_2.csv` (s) |
|---|---:|---:|---:|---|---:|
| `base` | `0.42` | `0.0000` | `741` | `integer optimal solution` | `0.57` / `0.59` |
| `cuts_0` | `0.49` | `0.0000` | `1,176` | `integer optimal solution` | `0.61` / `0.68` |
| `presolve_0` | `1.25` | `0.0000` | `801` | `integer optimal solution` | `1.81` / `2.11` |
| `mipfocus_1` | `0.30` | `0.0000` | `577` | `integer optimal solution` | `1.58` / `1.82` |
| `mipfocus_3` | `0.47` | `0.0000` | `287` | `integer optimal solution` | `3.65` / `4.20` |
| `heuristics_0` | `0.48` | `0.0000` | `990` | `integer optimal solution` | `0.64` / `0.65` |
| `relajado` | `0.0037` | `0.0000` | `0` | `optimal` | `0.0075` / `0.0093` |
| `tuned` | `0.43` | `0.0000` | `972` | `integer optimal solution` | `0.56` / `0.61` |

- **Tuning RC101**: CPLEX completó el tuning en `2.45 s` (cambiando `parameters.mip.limits.cutpasses=-1`), con un tiempo posterior de `0.43 s` prácticamente igual a `base` (`0.42 s`). Gurobi consumió `120.00 s` / `119.39 s` de tuning y obtuvo `0.56 s` / `0.61 s`.
- **Instancia sencilla**: En ambos solvers RC101 se resuelve de forma muy rápida; `presolve_0` es la variante más lenta en CPLEX (`1.25 s`), y en Gurobi `mipfocus_3` es la más lenta (`3.65 s` / `4.20 s`, con `gap = 0.0044 %`).

---

## 4. Análisis de sensibilidad de capacidad (`sensitivity_capacity`)

Todas las combinaciones `(ruta, día)` (9 por instancia) terminaron en estado `OPTIMAL_LP_FIXED` con `fixed_lp_objective` igual al óptimo entero (`511.19` en C101 y `893.66` en RC101) y **`shadow_price_pi = 0.0`** en ambos solvers:

- **C101 (`Q = 85.0`)**: 8 pares tienen holgura positiva (`5.0` a `35.0`) y 1 par está saturado (`route=2, day=2`, `slack = 0.0`, `SARHSLow = 85.0`, `SARHSUp = 1e+20` / `inf`).
- **RC101 (`Q = 90.0`)**: 7 pares tienen holgura positiva (`5.0` a `30.0`) y 2 pares están saturados (`route=1, day=2` y `route=3, day=1`, ambos con `slack = 0.0`, `SARHSLow = 90.0`, `SARHSUp = 1e+20` / `inf`).

**Interpretación**: Que `Pi = 0.0` incluso en las restricciones activas (`slack = 0.0`) se debe a que el análisis se realiza sobre el **LP con `X` y `Z` fijados** al incumbente óptimo. Una vez fija la asignación de clientes a rutas, la carga diaria es constante y la distancia total no cambia marginalmente al aumentar o disminuir localmente `Q` mientras no se viole la carga ya asignada (`SARHSLow`). Esto no implica que la capacidad no restrinja el problema MILP original si `Q` disminuyera por debajo de `SARHSLow` y obligara a reasignar clientes.

---

## 5. Observaciones metodológicas para el informe

1. **Tolerancia MIP en C101**: En CPLEX, salvo `heuristics_0` (`0.0 %`), las corridas de C101 finalizaron con estado `integer optimal, tolerance` y `gap_pct` entre `0.0061 %` y `0.0099 %` (dentro de la tolerancia relativa por defecto de `0.01 %`), mientras que Gurobi cerró en `0.0 %`. El valor objetivo encontrado (`511.19`) coincide exactamente con el óptimo global en ambos casos.
2. **Representatividad estadística**: Los datos de CPLEX corresponden a una réplica (`seed = 0`). Para reportar medias y desviaciones estándar entre semillas en la T3, se puede ejecutar con múltiples réplicas (por ejemplo `--repeats 5 --seed-base 0 --tag final --allow-large`).
3. **Tiempo de pared del tuning en C101**: Aunque `tune_time_limit_seconds` está configurado en `120.0 s`, el tiempo total de pared registrado en `tuning_wall_seconds` fue `185.33 s`, detalle relevante al contabilizar el costo computacional total del ajuste automático.
