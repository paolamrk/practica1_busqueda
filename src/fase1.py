import osmnx as ox
import os

# Coordenadas céntricas de CDMX (Zócalo)
punto_central = (19.432608, -99.133209)
# Radio en metros para abarcar zonas centro y norte
radio_metros = 5000 

print("Descargando el grafo urbano, esto puede tomar unos minutos...")

# Descarga el grafo dirigido de calles reales exclusivamente para vehículos
grafo = ox.graph_from_point(punto_central, dist=radio_metros, network_type='drive')

# Genera la ruta para guardar el archivo en la carpeta 'data'
ruta_archivo = os.path.join("data", "grafo_cdmx.graphml")

# Guarda el grafo en formato GraphML para uso futuro
ox.save_graphml(grafo, filepath=ruta_archivo)

print(f"Grafo guardado exitosamente en {ruta_archivo}")
print(f"Total de intersecciones (nodos): {len(grafo.nodes)}")
print(f"Total de calles (arcos): {len(grafo.edges)}")