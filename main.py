from fastapi import FastAPI
import pandas as pd
from datetime import datetime
from fastapi.responses import RedirectResponse

# Inicialización de FastAPI
app = FastAPI(
    title='& consulta sin miedo',
    description= 'Sistema de recomendación para cinéfilos',
    docs_url='/docs')

# Carga de datos
data = pd.read_parquet('movies_processed.parquet')

@app.get("/")
def read_root():
    return RedirectResponse(url="/docs")

#Página de presentación
@app.get('/')
async def index():
    return 'Bienvenid@s! ¿Qué vemos hoy?'

# Asegurar que la columna 'release_date' esté en formato datetime


# Diccionario para mapear los meses en español
meses = {
    'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
    'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
    'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
}
# 1- Cantidad de filmaciones por mes
@app.get("/cantidad_filmaciones_mes/{mes}")
def cantidad_filmaciones_mes(mes: str):
    # Convertir el mes ingresado a número
    mes_num = meses.get(mes.lower())
    
    if mes_num is None:
        return {"error": "Mes no válido. Usa el nombre del mes en español."}
    
    # Filtrar las películas estrenadas en el mes específico
    data['release_date'] = pd.to_datetime(data['release_date'], errors='coerce')
    cantidad = data[data['release_date'].dt.month == mes_num].shape[0]
    
    return {"mensaje": f"{cantidad} cantidad de películas fueron estrenadas en el mes de {mes.capitalize()}"}