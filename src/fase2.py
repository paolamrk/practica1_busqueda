import osmnx as ox
import networkx as nx
import folium
import heapq
import math
import time
import os

def cargar_grafo():
    """Carga el grafo desde el archivo local guardado en la Fase 1."""
    ruta_archivo = os.path.join("data", "grafo_cdmx.graphml")
    print(f"Cargando grafo desde {ruta_archivo}...")
    
    # Cargar el grafo y convertir los IDs de los nodos a enteros 
    # (osmnx a veces los lee como strings desde GraphML)
    grafo = ox.load_graphml(ruta_archivo)
    grafo = nx.convert_node_labels_to_integers(grafo, label_attribute='osmid')
    
    print(f"Grafo cargado: {len(grafo.nodes)} nodos y {len(grafo.edges)} arcos.")
    return grafo

def h1_euclidiana(nodo, destino, G):
    """
    Distancia Euclidiana (línea recta en coordenadas cartesianas).
    Se multiplica por 111,320 (metros aproximados por grado) para alinear 
    la escala geométrica con los pesos (metros) de las arcos.
    """
    x1, y1 = G.nodes[nodo]['x'], G.nodes[nodo]['y']
    x2, y2 = G.nodes[destino]['x'], G.nodes[destino]['y']
    
    distancia = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return distancia * 111320

def h2_haversine(nodo, destino, G):
    """
    Distancia de Haversine (distancia real sobre la superficie esférica terrestre).
    Garantiza admisibilidad al ser la distancia más corta posible entre dos puntos en una esfera.
    """
    lon1, lat1 = G.nodes[nodo]['x'], G.nodes[nodo]['y']
    lon2, lat2 = G.nodes[destino]['x'], G.nodes[destino]['y']
    
    R = 6371000  # Radio de la Tierra en metros
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def a_star(origen, destino, G, heuristica_func):
    """
    Algoritmo A* implementado con f(n) = g(n) + h(n).
    Retorna la tupla: (camino_reconstruido, costo_total, nodos_expandidos, tiempo_ms)
    """
    inicio_tiempo = time.time()
    
    # Cola de prioridad: almacena tuplas (f_score, nodo_id)
    frontera = []
    heapq.heappush(frontera, (0, origen))
    
    # Rastrear el costo real g(n) desde el origen hasta cada nodo
    costo_g = {origen: 0}
    # Rastrear el nodo padre para reconstruir la ruta final
    padres = {origen: None}
    
    nodos_expandidos = 0
    
    while frontera:
        # Extraer el nodo con el menor valor f(n)
        _, actual = heapq.heappop(frontera)
        
        # Condición de éxito: reconstruir ruta
        if actual == destino:
            camino = []
            while actual is not None:
                camino.append(actual)
                actual = padres[actual]
            camino.reverse()
            tiempo_ms = (time.time() - inicio_tiempo) * 1000
            return camino, costo_g[destino], nodos_expandidos, tiempo_ms
        
        nodos_expandidos += 1
        
        # Explorar intersecciones vecinas (arcos dirigidos)
        for vecino in G.successors(actual):
            # Obtener la distancia real de la calle (peso g)
            # En grafos MultiDiGraph de osmnx, los arcos tienen un índice (usualmente 0)
            datos_arco = G.get_edge_data(actual, vecino)[0]
            distancia_calle = datos_arco.get('length', 1.0)
            
            nuevo_costo_g = costo_g[actual] + distancia_calle
            
            # Si encontramos un camino más corto hacia el vecino, lo actualizamos
            if vecino not in costo_g or nuevo_costo_g < costo_g[vecino]:
                costo_g[vecino] = nuevo_costo_g
                f_score = nuevo_costo_g + heuristica_func(vecino, destino, G)
                
                heapq.heappush(frontera, (f_score, vecino))
                padres[vecino] = actual
                
    # Si la frontera se vacía y no se encontró el destino
    tiempo_ms = (time.time() - inicio_tiempo) * 1000
    return None, float('inf'), nodos_expandidos, tiempo_ms

def h3_personalizada(nodo, destino, G):
    """
    Heurística 3: Combina la distancia de Haversine con una penalización
    por el número de giros estimados (simulando que en entornos urbanos 
    los giros toman tiempo/distancia extra).
    """
    # 1. Calculamos la distancia base con Haversine
    distancia_base = h2_haversine(nodo, destino, G)
    
    # 2. Estimación de giros (enfoque tipo Manhattan)
    # Si las coordenadas x e y son diferentes, estimamos al menos 1 giro.
    x1, y1 = G.nodes[nodo]['x'], G.nodes[nodo]['y']
    x2, y2 = G.nodes[destino]['x'], G.nodes[destino]['y']
    
    giros_estimados = 0
    if abs(x1 - x2) > 0.0001 and abs(y1 - y2) > 0.0001:
        giros_estimados = 1
        
    # Penalización moderada de 5 metros por giro estimado para intentar 
    # mantener la admisibilidad de la heurística.
    penalizacion_giro = 5.0 
    
    return distancia_base + (giros_estimados * penalizacion_giro)


def greedy_best_first(origen, destino, G, heuristica_func):
    """
    Algoritmo Greedy Best-First.
    Evalúa los nodos en la frontera usando SOLO h(n), ignorando g(n).
    No garantiza el camino óptimo, pero suele ser más rápido.
    """
    inicio_tiempo = time.time()
    
    frontera = []
    heapq.heappush(frontera, (0, origen))
    
    padres = {origen: None}
    # Solo necesitamos g(n) para calcular el costo real de la ruta final, 
    # NO para tomar decisiones en la cola de prioridad.
    costo_g = {origen: 0}
    
    nodos_expandidos = 0
    
    while frontera:
        _, actual = heapq.heappop(frontera)
        
        if actual == destino:
            camino = []
            while actual is not None:
                camino.append(actual)
                actual = padres[actual]
            camino.reverse()
            tiempo_ms = (time.time() - inicio_tiempo) * 1000
            return camino, costo_g[destino], nodos_expandidos, tiempo_ms
        
        nodos_expandidos += 1
        
        for vecino in G.successors(actual):
            datos_arco = G.get_edge_data(actual, vecino)[0]
            distancia_calle = datos_arco.get('length', 1.0)
            nuevo_costo_g = costo_g[actual] + distancia_calle
            
            if vecino not in padres:  # Si no ha sido visitado
                costo_g[vecino] = nuevo_costo_g
                padres[vecino] = actual
                
                # LA DIFERENCIA CON A*: El valor de prioridad es SOLAMENTE h(n)
                h_score = heuristica_func(vecino, destino, G)
                heapq.heappush(frontera, (h_score, vecino))
                
    tiempo_ms = (time.time() - inicio_tiempo) * 1000
    return None, float('inf'), nodos_expandidos, tiempo_ms

def visualizar_ruta_folium(G, ruta, nombre_archivo="ruta_mapa.html"):
    """Genera un mapa HTML interactivo con la ruta calculada."""
    # Obtener coordenadas del nodo inicial para centrar el mapa
    nodo_inicio = ruta[0]
    lat_inicio = G.nodes[nodo_inicio]['y']
    lon_inicio = G.nodes[nodo_inicio]['x']

    # Crear el mapa base centrado en el punto de inicio
    mapa = folium.Map(
        location=[lat_inicio, lon_inicio], 
        zoom_start=15,
        tiles='https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png',
        attr='© OpenStreetMap contributors, Tiles by HOT'
    )

    # Extraer las coordenadas (lat, lon) de todos los nodos de la ruta
    coordenadas_ruta = [(G.nodes[n]['y'], G.nodes[n]['x']) for n in ruta]

    # Dibujar la línea de la ruta
    folium.PolyLine(
        coordenadas_ruta,
        weight=5,
        color='blue',
        opacity=0.8,
        tooltip="Ruta calculada"
    ).add_to(mapa)

    # Agregar marcadores para distinguir el inicio y el destino
    folium.Marker(coordenadas_ruta[0], popup="Inicio", icon=folium.Icon(color="green")).add_to(mapa)
    folium.Marker(coordenadas_ruta[-1], popup="Destino", icon=folium.Icon(color="red")).add_to(mapa)

    # Guardar el mapa en la carpeta data
    ruta_guardado = os.path.join("data", nombre_archivo)
    mapa.save(ruta_guardado)
    print(f"Mapa interactivo guardado exitosamente en: {ruta_guardado}")

# Ejecución principal de prueba
if __name__ == "__main__":
    G = cargar_grafo()
    
    # Seleccionamos un nodo origen y un destino más distante para notar el contraste
    nodos_lista = list(G.nodes)
    origen_prueba = nodos_lista[0]
    destino_prueba = nodos_lista[5000] 
    
    print("\n--- COMPARATIVA DE ALGORITMOS FASE 2 ---")
    print(f"Ruta desde el nodo {origen_prueba} hasta {destino_prueba}\n")
    
    # 1. Ejecución de A* (Garantiza el camino óptimo)
    print(">> Ejecutando A* (f = g + h) con heurística Haversine...")
    ruta_astar, costo_astar, exp_astar, tiempo_astar = a_star(origen_prueba, destino_prueba, G, h2_haversine)
    
    if ruta_astar:
        print(f"Costo (distancia): {costo_astar:.2f} m | Nodos expandidos: {exp_astar} | Tiempo: {tiempo_astar:.2f} ms")
        visualizar_ruta_folium(G, ruta_astar, "mapa_A_star.html")
    else:
        print("A* no encontró ruta.")
        
    print("-" * 50)
    
    # 2. Ejecución de Greedy Best-First (Suele ser más rápido pero subóptimo)
    print(">> Ejecutando Greedy Best-First (f = h) con heurística Haversine...")
    ruta_greedy, costo_greedy, exp_greedy, tiempo_greedy = greedy_best_first(origen_prueba, destino_prueba, G, h2_haversine)
    
    if ruta_greedy:
        print(f"Costo (distancia): {costo_greedy:.2f} m | Nodos expandidos: {exp_greedy} | Tiempo: {tiempo_greedy:.2f} ms")
        visualizar_ruta_folium(G, ruta_greedy, "mapa_Greedy.html")
    else:
        print("Greedy no encontró ruta.")