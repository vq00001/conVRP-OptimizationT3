# Veredicto comparativo: CPLEX vs. Gurobi (conVRP — mismo computador)

Análisis comparativo ejecutado en igualdad de condiciones (**mismo computador `DESKTOP-07TOJM3`**, CPU `12th Gen Intel(R) Core(TM) i5-12450HX`, Python `3.12.13`, `Threads = 1`, `TimeLimit = 600 s`) entre **Gurobi 14.0.0** y **CPLEX 22.2.0.0** (`run_id = 20261115_151830`, `seed = 0`) sobre las dos instancias calibradas de 15 clientes (`1515` variables y `1755` restricciones antes del presolve).

> **Archivos fuente (mismo computador)**
> - **Gurobi**: `results/results.csv`, `results/sensitivity.csv` y 18 logs nativos en `results/logs/gurobi/`
> - **CPLEX**: `results/cplex_results_all.csv`, `results/cplex_sensitivity_all.csv`, `results/cplex/20261115_151830/cplex_run_20261115_151830.json` y 18 logs nativos en `results/logs/cplex/`
> - **Gráficos**: `results/graficos_instancias/` y `results/graficos_comparacion/`

---

## 1. Veredicto general

Los resultados confirman **equivalencia matemática exacta** entre ambos solvers y muestran diferencias claras de estrategia algorítmica en el árbol de Branch & Cut:

1. **Equivalencia matemática verificada**: Gurobi y CPLEX obtienen exactamente los mismos óptimos enteros (`511.19` en C101 y `893.66` en RC101), los mismos óptimos de relajación continua (`129.87` vía `model.relax()` y CPLEX fijando binarias a continuas; `156.66` en RC101), las mismas brechas de integralidad (`74.59 %` y `82.47 %`) y el mismo comportamiento dual en sensibilidad de capacidad (`Pi = 0.0`).
2. **Desempeño en `instance_1_c101_15c` (ventanas de tiempo más estrechas y acoplamiento fuerte)**:
   - En configuración por defecto (`base`), **Gurobi fue ~12.5x más rápido** (`6.23 s`, `3,371` nodos, gap `0.0000 %`) que **CPLEX** (`77.57 s`, `32,292` nodos, gap `0.0078 %` dentro de tolerancia `1e-4`).
   - Los **logs nativos revelan la causa**: ambos parten con exactamente la misma relajación raíz antes de cortes (`218.92`), pero Gurobi eleva la cota dual del nodo raíz mediante planos de corte hasta **`311.16`** (`gap = 50.0 %`) y encuentra el óptimo `511.19` en el nodo `394`, mientras que CPLEX solo alcanza **`239.47`** al salir de la raíz (`gap = 61.74 %`) y requiere un *restart* más `17,227` nodos para hallar `511.19`.
   - El **tuning automático** de CPLEX (`cutpasses=1`, `probe=-1`, `variableselect=4`) redujo sus nodos a menos de la mitad (`15,809`) y su tiempo a **`19.97 s`** (`3.88x` más rápido que su `base`), mientras `mipfocus_1` bajó a **`22.76 s`**.
3. **Desempeño en `instance_2_rc101_15c`**:
   - Ambos resuelven en menos de un segundo en `base`, con **CPLEX ligeramente más rápido** (`0.43 s`, `741` nodos) frente a **Gurobi** (`0.83 s`, `452` nodos), y `mipfocus_1` en CPLEX en apenas **`0.30 s`**.

---

## 2. Validación del modelo y relajación continua (LP vs. MILP)

| Instancia | Métrica | Gurobi 14.0.0 | CPLEX 22.2.0.0 | Diferencia |
|---|---|---:|---:|---:|
| `instance_1_c101_15c` | Relajación LP (`relajado`) | `129.87` (`0.011 s`, `0` nodos) | `129.87` (`0.005 s`, `0` nodos) | `0.00` |
| `instance_1_c101_15c` | Óptimo MILP (`base`) | `511.19` (`6.23 s`, `3,371` nodos) | `511.19` (`77.57 s`, `32,292` nodos) | `0.00` |
| `instance_1_c101_15c` | Brecha de integralidad (`%`) | `74.59 %` | `74.59 %` | `0.00 %` |
| `instance_2_rc101_15c` | Relajación LP (`relajado`) | `156.66` (`0.009 s`, `0` nodos) | `156.66` (`0.004 s`, `0` nodos) | `0.00` |
| `instance_2_rc101_15c` | Óptimo MILP (`base`) | `893.66` (`0.83 s`, `452` nodos) | `893.66` (`0.43 s`, `741` nodos) | `0.00` |
| `instance_2_rc101_15c` | Brecha de integralidad (`%`) | `82.47 %` | `82.47 %` | `0.00 %` |

La **brecha de integralidad alta** (`74.59 %` en C101 y `82.47 %` en RC101) es estructural a la formulación con restricciones **Big-M** de precedencia temporal: al relajar las variables binarias $X_{ij}^{rd}$ a continuas $[0,1]$, los tiempos de llegada dejan de acoplar efectivamente los arcos y la relajación LP se acerca a una cota de flujo mínimo muy laxa, obligando a los planos de corte y al *branch-and-bound* a cerrar el resto de la brecha.

---

## 3. Comparación por configuración (`Threads = 1`, `TimeLimit = 600 s`)

### 3.1 `instance_1_c101_15c` (Óptimo = `511.19`)

| Experimento | Gurobi Tiempo (s) | Gurobi Nodos | Gurobi Gap (%) | CPLEX Tiempo (s) | CPLEX Nodos | CPLEX Gap (%) |
|---|---:|---:|---:|---:|---:|---:|
| `base` | `6.23` | `3,371` | `0.0000` | `77.57` | `32,292` | `0.0078` |
| `cuts_0` | `34.82` | `74,381` | `0.0078` | `72.33` | `76,370` | `0.0079` |
| `presolve_0` | `50.86` | `22,107` | `0.0059` | `89.09` | `65,672` | `0.0094` |
| `mipfocus_1` | `36.56` | `12,588` | `0.0000` | `22.76` | `20,518` | `0.0074` |
| `mipfocus_3` | `26.38` | `1,237` | `0.0000` | `172.93` | `44,372` | `0.0099` |
| `heuristics_0` | `6.83` | `3,862` | `0.0000` | `37.03` | `20,968` | `0.0000` |
| `relajado` | `0.011` | `0` | `0.0000` | `0.005` | `0` | `0.0000` |
| `tuned` | `6.25` | `3,371` | `0.0000` | `19.97` | `15,809` | `0.0061` |

- **Dependencia de cortes en Gurobi vs. CPLEX**: En Gurobi, desactivar cortes (`cuts_0`) dispara los nodos de `3,371` a `74,381` (~22x) y el tiempo a `34.82 s`, confirmando que los planos de corte en la raíz (`Clique`, `Cover`, `Implied bound`, `Zero half`) son el motor principal de su ventaja en C101. En CPLEX, `cuts_0` duplica los nodos (`76,370`) con un tiempo similar (`72.33 s`).
- **Presolve**: Desactivar `presolve` (`presolve_0`) degrada fuertemente a ambos (`50.86 s` en Gurobi, `89.09 s` en CPLEX).
- **Énfasis MIP (`MIPFocus`)**: En Gurobi, su estrategia por defecto balanceada (`base`) supera ampliamente a `mipfocus_1` (`36.56 s`) y `mipfocus_3` (`26.38 s`, aunque este último logra la menor cantidad de nodos con `1,237`). En CPLEX ocurre lo opuesto: priorizar factibilidad (`mipfocus_1`) recorta el tiempo a `22.76 s`, mientras `mipfocus_3` lo más que duplica (`172.93 s`).
- **Tuning automático (`tune_time_limit = 120 s`)**: Gurobi consumió `106.84 s` de pared y mantuvo el excelente `base` (`6.25 s`, `3,371` nodos). CPLEX empleó `182.52 s` de pared y encontró `{cutpasses: 1, probe: -1, variableselect: 4}`, acelerando de `77.57 s` a `19.97 s` (`3.88x`) con menos de la mitad de nodos (`15,809`).

### 3.2 `instance_2_rc101_15c` (Óptimo = `893.66`)

| Experimento | Gurobi Tiempo (s) | Gurobi Nodos | Gurobi Gap (%) | CPLEX Tiempo (s) | CPLEX Nodos | CPLEX Gap (%) |
|---|---:|---:|---:|---:|---:|---:|
| `base` | `0.83` | `452` | `0.0000` | `0.43` | `741` | `0.0000` |
| `cuts_0` | `0.39` | `473` | `0.0000` | `0.49` | `1,176` | `0.0000` |
| `presolve_0` | `1.53` | `1,224` | `0.0000` | `1.26` | `801` | `0.0000` |
| `mipfocus_1` | `1.26` | `401` | `0.0000` | `0.30` | `577` | `0.0000` |
| `mipfocus_3` | `6.00` | `195` | `0.0000` | `0.48` | `287` | `0.0000` |
| `heuristics_0` | `0.57` | `418` | `0.0000` | `0.49` | `990` | `0.0000` |
| `relajado` | `0.009` | `0` | `0.0000` | `0.004` | `0` | `0.0000` |
| `tuned` | `0.85` | `452` | `0.0000` | `0.43` | `972` | `0.0000` |

En RC101 las ventanas de tiempo más holgadas/heterogéneas reducen el tamaño efectivo del árbol a pocos cientos de nodos: CPLEX termina en `0.30 s–1.26 s` (`2.45 s` de tuning), mientras Gurobi resuelve `base` en `0.83 s` y penaliza `mipfocus_3` (`6.00 s` por sobrecosto de cortes frente a un árbol de apenas `195` nodos; tuning `119.78 s`).

---

## 4. Análisis de sensibilidad de capacidad (`sensitivity_capacity`)

Las 9 restricciones de capacidad `(ruta, día)` por instancia cerraron en `OPTIMAL_LP_FIXED` con `fixed_lp_objective` idéntico al óptimo entero (`511.19` y `893.66`) y **`shadow_price_pi = 0.0`** en ambos solvers:

- **C101 (`Q = 85.0`)**: Ambos encuentran exactamente 1 par saturado (`slack = 0.0`, `SARHSLow = 85.0`, `SARHSUp = inf / 1e+20`) y el mismo multiconjunto de holguras diarias (`5.0` a `35.0`); Gurobi satura `(ruta=3, día=2)` y CPLEX satura `(ruta=2, día=2)` debido a la simetría entre vehículos homogéneos 2 y 3.
- **RC101 (`Q = 90.0`)**: Coincidencia exacta par por par en ambos solvers, con 2 pares saturados (`(ruta=1, día=2)` y `(ruta=3, día=1)`, `slack = 0.0`, `SARHSLow = 90.0`) y 7 pares con holgura positiva (`5.0` a `30.0`).

**Interpretación**: En el LP obtenido al fijar todas las variables binarias $(X, Z)$ al incumbente óptimo, la asignación de clientes a rutas queda constante, por lo que $Q$ no modifica marginalmente la distancia recorrida mientras se mantenga sobre la carga asignada (`SARHSLow`). Esto no significa que $Q$ sea irrelevante en el MILP original: bajar $Q$ por debajo de `SARHSLow` volvería infactible la asignación actual y forzaría nuevas rutas más costosas.
