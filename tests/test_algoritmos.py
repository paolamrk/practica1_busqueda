import sys
import os
import pytest
import osmnx as ox

# 1. Inyección de ruta ANTES de las importaciones locales
ruta_src = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(ruta_src)

# 2. Ahora sí, importaciones de tus módulos
from fase1_algoritmos import busqueda_bfs, busqueda_ucs
from fase3 import operador_2opt, calcular_costo_ruta, cruza_ox

@pytest.fixture(scope="module")
def grafo_prueba():
    return ox.load_graphml("../data/grafo_cdmx.graphml")

def test_busquedas_fase1(grafo_prueba):
    nodos = list(grafo_prueba.nodes())
    camino_bfs, _, _ = busqueda_bfs(grafo_prueba, nodos[0], nodos[50])
    camino_ucs, _, _, costo = busqueda_ucs(grafo_prueba, nodos[0], nodos[50])
    
    assert camino_bfs is not None and len(camino_bfs) > 0
    assert camino_ucs is not None and costo >= 0

def test_operadores_fase3():
    ruta = [0, 1, 2, 3, 4]
    vecino = operador_2opt(ruta)
    assert len(ruta) == len(vecino)
    assert set(ruta) == set(vecino)
    
    p1, p2 = [1, 2, 3, 4, 5], [5, 4, 3, 2, 1]
    hijo = cruza_ox(p1, p2)
    assert len(hijo) == 5
    assert set(hijo) == set(p1)

def test_funcion_costo():
    matriz_mock = [[0, 10, 20], [10, 0, 30], [20, 30, 0]]
    assert calcular_costo_ruta([0, 1, 2], matriz_mock) == 60