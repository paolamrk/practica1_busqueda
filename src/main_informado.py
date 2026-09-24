import os
import osmnx as ox
import matplotlib.pyplot as plt
import random
from fase3_informada import generar_matriz_entregas, recocido_simulado, algoritmo_genetico

# Construcción dinámica de la ruta
ruta_base = os.path.dirname(os.path.abspath(__file__))
ruta_mapa = os.path.join(ruta_base, "..", "data", "grafo_cdmx.graphml")

print("Cargando grafo (Versión Informada)...")
grafo = ox.load_graphml(ruta_mapa)
nodos = list(grafo.nodes())

puntos_entrega = random.sample(nodos, 12)
indices_ruta = list(range(len(puntos_entrega)))

print("Calculando matriz de distancias reales con A* (Heurística Haversine)...")
matriz = generar_matriz_entregas(grafo, puntos_entrega)

print("Ejecutando Recocido Simulado...")
estado_inicial = indices_ruta.copy()
random.shuffle(estado_inicial)
mejor_ruta_sa, costo_sa, hist_sa = recocido_simulado(
    estado_inicial, matriz, T=1000, alfa=0.95, T_min=1, iteraciones=50
)

print("Ejecutando Algoritmo Genético...")
pob_inicial = [random.sample(indices_ruta, len(indices_ruta)) for _ in range(50)]
mejor_ruta_ag, costo_ag, hist_ag = algoritmo_genetico(
    pob_inicial, matriz, gen=100, prob_mut=0.1
)

print(f"Costo final SA: {costo_sa:.2f} m | Costo final AG: {costo_ag:.2f} m")

plt.figure(figsize=(10, 6))
plt.plot(hist_sa, label="Simulated Annealing (2-opt)", color="red")
plt.plot(hist_ag, label="Algoritmo Genético (OX)", color="blue")
plt.title("Convergencia de Optimización (Matriz generada con A*)")
plt.xlabel("Iteraciones / Generaciones")
plt.ylabel("Mejor Costo Encontrado (metros)")
plt.legend()
plt.grid(True, linestyle="--", alpha=0.7)
plt.tight_layout()
plt.show()