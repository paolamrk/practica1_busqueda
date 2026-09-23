import networkx as nx
import osmnx as ox
from collections import deque
import heapq
import time

# Función auxiliar: Reconstruye el camino final yendo hacia atrás desde el destino
def reconstruir_camino(padres, destino):
    camino = [destino]
    actual = destino
    while padres[actual] is not None:
        actual = padres[actual]
        camino.append(actual)
    camino.reverse()
    return camino

# 1. Búsqueda en Anchura (BFS) - Usa una Cola (deque)
def busqueda_bfs(grafo, inicio, destino):
    inicio_tiempo = time.time()
    frontera = deque([inicio])
    visitados = {inicio}
    padres = {inicio: None}
    nodos_expandidos = 0
    
    while frontera:
        nodo_actual = frontera.popleft()
        nodos_expandidos += 1
        
        if nodo_actual == destino:
            tiempo_ms = (time.time() - inicio_tiempo) * 1000
            return reconstruir_camino(padres, destino), nodos_expandidos, tiempo_ms
        
        for vecino in grafo.successors(nodo_actual):
            if vecino not in visitados:
                visitados.add(vecino)
                padres[vecino] = nodo_actual
                frontera.append(vecino)
    return None, nodos_expandidos, 0

# 2. Búsqueda en Profundidad (DFS Iterativo) - Usa una Pila (Lista)
def busqueda_dfs(grafo, inicio, destino):
    inicio_tiempo = time.time()
    frontera = [inicio]
    visitados = set()
    padres = {inicio: None}
    nodos_expandidos = 0
    
    while frontera:
        nodo_actual = frontera.pop()
        
        if nodo_actual in visitados:
            continue
            
        visitados.add(nodo_actual)
        nodos_expandidos += 1
        
        if nodo_actual == destino:
            tiempo_ms = (time.time() - inicio_tiempo) * 1000
            return reconstruir_camino(padres, destino), nodos_expandidos, tiempo_ms
        
        for vecino in grafo.successors(nodo_actual):
            if vecino not in visitados:
                padres[vecino] = nodo_actual
                frontera.append(vecino)
    return None, nodos_expandidos, 0

# 3. Búsqueda de Costo Uniforme (UCS) - Usa una Cola de Prioridad (heapq)
def busqueda_ucs(grafo, inicio, destino):
    inicio_tiempo = time.time()
    frontera = [(0, inicio)] # Guarda tuplas: (distancia_acumulada, nodo)
    visitados = set()
    padres = {inicio: None}
    costo_acumulado = {inicio: 0}
    nodos_expandidos = 0
    
    while frontera:
        costo_actual, nodo_actual = heapq.heappop(frontera)
        
        if nodo_actual in visitados:
            continue
            
        visitados.add(nodo_actual)
        nodos_expandidos += 1
        
        if nodo_actual == destino:
            tiempo_ms = (time.time() - inicio_tiempo) * 1000
            return reconstruir_camino(padres, destino), nodos_expandidos, tiempo_ms, costo_actual
        
        for vecino in grafo.successors(nodo_actual):
            # Obtiene la distancia en metros del segmento de calle
            datos_arista = grafo.get_edge_data(nodo_actual, vecino)[0]
            peso_calle = datos_arista.get('length', 1) 
            
            nuevo_costo = costo_acumulado[nodo_actual] + peso_calle
            
            if vecino not in costo_acumulado or nuevo_costo < costo_acumulado[vecino]:
                costo_acumulado[vecino] = nuevo_costo
                padres[vecino] = nodo_actual
                heapq.heappush(frontera, (nuevo_costo, vecino))
                
    return None, nodos_expandidos, 0, 0

# --- Bloque de Prueba ---
if __name__ == "__main__":
    print("Cargando mapa... esto tomará unos segundos.")
    # Usamos "data/" porque la terminal en tu imagen está en la carpeta principal
    grafo_cdmx = ox.load_graphml("data/grafo_cdmx.graphml") 
    
    # Tomamos dos nodos cualesquiera que existan en tu grafo para probar
    nodos_lista = list(grafo_cdmx.nodes())
    nodo_A = nodos_lista[0]
    nodo_B = nodos_lista[100] # Nodo a 100 posiciones de distancia en la lista
    
    print(f"\nBuscando ruta desde {nodo_A} hasta {nodo_B}...")
    
    camino_bfs, exp_bfs, t_bfs = busqueda_bfs(grafo_cdmx, nodo_A, nodo_B)
    print(f"BFS -> Tiempo: {t_bfs:.2f} ms | Nodos expandidos: {exp_bfs} | Pasos en ruta: {len(camino_bfs)}")
    
    camino_dfs, exp_dfs, t_dfs = busqueda_dfs(grafo_cdmx, nodo_A, nodo_B)
    print(f"DFS -> Tiempo: {t_dfs:.2f} ms | Nodos expandidos: {exp_dfs} | Pasos en ruta: {len(camino_dfs)}")
    
    camino_ucs, exp_ucs, t_ucs, costo_ucs = busqueda_ucs(grafo_cdmx, nodo_A, nodo_B)
    print(f"UCS -> Tiempo: {t_ucs:.2f} ms | Nodos expandidos: {exp_ucs} | Metros recorridos: {costo_ucs:.2f} m")

    print("\nGenerando mapas visuales (esto tomará unos segundos)...")

    # Guardar mapa de BFS (Azul)
    fig_bfs, ax_bfs = ox.plot_graph_route(grafo_cdmx, camino_bfs, route_color='blue', route_linewidth=3, node_size=0, show=False, close=False)
    fig_bfs.savefig("data/ruta_bfs.png", dpi=300, bbox_inches='tight')

    # Guardar mapa de DFS (Rojo)
    fig_dfs, ax_dfs = ox.plot_graph_route(grafo_cdmx, camino_dfs, route_color='red', route_linewidth=3, node_size=0, show=False, close=False)
    fig_dfs.savefig("data/ruta_dfs.png", dpi=300, bbox_inches='tight')

    # Guardar mapa de UCS (Verde)
    fig_ucs, ax_ucs = ox.plot_graph_route(grafo_cdmx, camino_ucs, route_color='green', route_linewidth=3, node_size=0, show=False, close=False)
    fig_ucs.savefig("data/ruta_ucs.png", dpi=300, bbox_inches='tight')

    print("Mapas guardados exitosamente en la carpeta 'data'.")  