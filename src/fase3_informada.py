import random
import math
from fase2 import a_star, h2_haversine

def generar_matriz_entregas(grafo, puntos_entrega):
    """Calcula el costo real de viaje entre todos los puntos usando A* (Fase 2)."""
    n = len(puntos_entrega)
    matriz = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                # Extraemos el costo_g (índice 1) que retorna la función a_star de fase2.py
                _, costo, _, _ = a_star(puntos_entrega[i], puntos_entrega[j], grafo, h2_haversine)
                matriz[i][j] = costo
    return matriz

def calcular_costo_ruta(ruta, matriz):
    costo = sum(matriz[ruta[i]][ruta[i+1]] for i in range(len(ruta) - 1))
    costo += matriz[ruta[-1]][ruta[0]]
    return costo

def operador_2opt(ruta):
    nueva = ruta.copy()
    i, j = sorted(random.sample(range(len(nueva)), 2))
    nueva[i:j+1] = reversed(nueva[i:j+1])
    return nueva

def recocido_simulado(estado, matriz, T, alfa, T_min, iteraciones):
    mejor_estado, mejor_costo = estado, calcular_costo_ruta(estado, matriz)
    costo_actual = mejor_costo
    historial = []
    
    while T > T_min:
        for _ in range(iteraciones):
            vecino = operador_2opt(estado)
            c_vecino = calcular_costo_ruta(vecino, matriz)
            delta = c_vecino - costo_actual
            
            if delta < 0 or random.random() < math.exp(-delta / T):
                estado, costo_actual = vecino, c_vecino
                if c_vecino < mejor_costo:
                    mejor_estado, mejor_costo = estado, c_vecino
                    
        historial.append(mejor_costo)
        T *= alfa
        
    return mejor_estado, mejor_costo, historial

def cruza_ox(p1, p2):
    size = len(p1)
    hijo = [-1] * size
    start, end = sorted(random.sample(range(size), 2))
    hijo[start:end+1] = p1[start:end+1]
    
    p2_filtrado = [g for g in p2 if g not in hijo]
    idx = 0
    for i in range(size):
        if hijo[i] == -1:
            hijo[i] = p2_filtrado[idx]
            idx += 1
    return hijo

def algoritmo_genetico(poblacion, matriz, gen, prob_mut):
    historial = []
    for _ in range(gen):
        poblacion.sort(key=lambda x: calcular_costo_ruta(x, matriz))
        historial.append(calcular_costo_ruta(poblacion[0], matriz))
        
        nueva = poblacion[:2] 
        while len(nueva) < len(poblacion):
            p1, p2 = random.sample(poblacion[:len(poblacion)//2], 2)
            hijo = cruza_ox(p1, p2)
            
            if random.random() < prob_mut:
                i, j = random.sample(range(len(hijo)), 2)
                hijo[i], hijo[j] = hijo[j], hijo[i]
                
            nueva.append(hijo)
        poblacion = nueva
        
    mejor = min(poblacion, key=lambda x: calcular_costo_ruta(x, matriz))
    return mejor, calcular_costo_ruta(mejor, matriz), historial