from fastapi import FastAPI, HTTPException
import pandas as pd
from datetime import datetime
from fastapi.responses import RedirectResponse

# Inicialización de FastAPI
app = FastAPI(
    title='¿Qué vemos hoy?',
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
       # Convertir el mes ingresado a minúsculas
    mes = mes.lower()
    # Obtener el número del mes y verificar su validez
    mes_num = meses.get(mes)
    
    if mes_num is None:
        raise HTTPException(status_code=400, detail= 'Mes no válido. Usa el nombre completo del mes en español.') 
    
    # Filtrar las películas estrenadas en el mes específico
    cantidad = data[data['release_date'].dt.month == mes_num].shape[0]
    
    return {"mensaje": f"En {mes.capitalize()}, se estrenaron {cantidad} películas."}


# 2.

# Asegúrate de que la columna 'release_date' esté en formato de fecha
data['release_date'] = pd.to_datetime(data['release_date'], errors='coerce')

# Diccionario que incluye formas con y sin acento
dias_semana = {
    'lunes': 0,
    'martes': 1,
    'miércoles': 2, 'miercoles': 2,
    'jueves': 3,
    'viernes': 4,
    'sábado': 5, 'sabado': 5,
    'domingo': 6
}

@app.get("/cantidad_filmaciones_dia/{dia}")
def cantidad_filmaciones_dia(dia: str):
    # Convertir el día ingresado a minúsculas para uniformidad
    dia = dia.lower()
    
    # Verificar si el día ingresado es válido en el diccionario
    if dia not in dias_semana:
        raise HTTPException(status_code=400, detail= 'Día no válido. Elige entre: lunes, martes, miércoles, jueves, viernes, sábado o domingo.')

    # Filtrar las películas que fueron estrenadas en el día de la semana deseado
    dia_num = dias_semana[dia]
    peliculas_dia = data[data['release_date'].dt.weekday == dia_num]

    # Contar la cantidad de películas y retornar el mensaje
    cantidad = len(peliculas_dia)
    return {"mensaje": f"{cantidad} cantidad de películas fueron estrenadas en días {dia.capitalize()}"}
