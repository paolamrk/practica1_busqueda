import sys
import os
import pytest
import osmnx as ox

# Inyección de ruta dinámica
ruta_src = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(ruta_src)

from fase2 import a_star, greedy_best_first, h2_haversine
from fase3_informada import operador_2opt, calcular_costo_ruta, cruza_ox

@pytest.fixture(scope="module")
def grafo_prueba():
    # Construcción dinámica de la ruta para encontrar la carpeta 'data'
    ruta_base = os.path.dirname(os.path.abspath(__file__))
    ruta_mapa = os.path.join(ruta_base, "..", "data", "grafo_cdmx.graphml")
    return ox.load_graphml(ruta_mapa)

def test_busquedas_fase2(grafo_prueba):
    nodos = list(grafo_prueba.nodes())
    origen, destino = nodos[0], nodos[50]
    
    camino_a, costo_a, _, _ = a_star(origen, destino, grafo_prueba, h2_haversine)
    assert camino_a is not None and len(camino_a) > 0
    assert costo_a >= 0
    
    camino_g, costo_g, _, _ = greedy_best_first(origen, destino, grafo_prueba, h2_haversine)
    assert camino_g is not None and len(camino_g) > 0
    assert costo_g >= 0

def test_operadores_fase3_informada():
    ruta = [0, 1, 2, 3, 4]
    vecino = operador_2opt(ruta)
    assert len(ruta) == len(vecino)
    
    p1, p2 = [1, 2, 3, 4, 5], [5, 4, 3, 2, 1]
    hijo = cruza_ox(p1, p2)
    assert len(hijo) == 5
    assert set(hijo) == set(p1)