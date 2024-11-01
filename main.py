from fastapi import FastAPI, HTTPException
import pandas as pd
from datetime import datetime
from fastapi.responses import RedirectResponse

# Inicialización de FastAPI
app = FastAPI(
    title='¿Qué vemos hoy?\nAPI para cinéfilos.',
    description=(
        'Descubre películas, accede a información detallada y obtén recomendaciones personalizadas basadas en datos. '
        'Nuestro sistema de recomendación te sugiere películas similares a las que te interesan, haciendo que encontrar tu próxima favorita sea más fácil que nunca.'
    ),
    docs_url='/docs'
)


# Carga de datos
data = pd.read_parquet('processed_data.parquet')

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
# 1. Cantidad de filmaciones por mes
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


# 3. Función para actores
@app.get("/actor/{nombre_actor}")
def get_actor(nombre_actor:str):
    # Verificar que el nombre completo (nombre y apellido) haya sido ingresado
    if len(nombre_actor.split()) < 2:
        raise HTTPException(
            status_code=400,
            detail="Por favor ingrese el nombre completo del actor, incluyendo nombre y apellido."
        )
    
    # Convertir el nombre ingresado a minúsculas para una comparación insensible a mayúsculas
    nombre_actor = nombre_actor.lower()

    # Filtrar las películas donde el nombre completo del actor (en minúsculas) está presente en la columna 'cast_name'
    actor_films = data[data['cast_name'].apply(lambda x: nombre_actor in x.lower() if pd.notnull(x) else False)]

    # Calcular cantidad de películas, retorno total y promedio
    cantidad_peliculas = len(actor_films)
    retorno_total = round(actor_films['return'].sum(), 2)
    retorno_promedio = round(retorno_total / cantidad_peliculas, 2) if cantidad_peliculas > 0 else 0

    # Formatear el nombre para que aparezca con iniciales en mayúsculas en el mensaje
    nombre_formateado = ' '.join([word.capitalize() for word in nombre_actor.split()])
    
    # Retornar el mensaje con los datos calculados
    return {
        "mensaje": f"El actor {nombre_formateado} ha participado en {cantidad_peliculas} películas, "
                   f"con un retorno total acumulado de {retorno_total} veces la inversión "
                   f"y un retorno promedio de {retorno_promedio} veces la inversión por película."
    }
   
    
# 4. Función para directores
@app.get("/director/{nombre_director}")
def get_director(nombre_director: str):

    # Verificar que el nombre completo (nombre y apellido) haya sido ingresado
    if len(nombre_director.split()) < 2:
        raise HTTPException(
            status_code=400,
            detail="Por favor ingrese el nombre completo del director, incluyendo nombre y apellido."
        )

    # Convertir el nombre ingresado a minúsculas para comparación insensible a mayúsculas
    nombre_director = nombre_director.lower()
    
    # Filtrar las películas donde crew_name coincide con el director especificado y el crew_job es 'Director'
    director_films = data[
        data['crew_name'].apply(lambda x: nombre_director in x.lower() if pd.notnull(x) else False) &
        (data['crew_job'] == 'Director')
    ] 
    
    # Crear una lista con la información de cada película dirigida por el director, incluyendo verificación de título nulo
film_info = [
    {
        "pelicula": row['title'] if pd.notnull(row['title']) else "Título no disponible",
        "fecha_lanzamiento": row['release_date'].strftime("%d-%m-%Y") if pd.notnull(row['release_date']) else "Fecha no disponible",
        "retorno": round(row['return'], 2) if pd.notnull(row['return']) else "Dato no disponible",
        "costo": f"${round(row['budget'], 2):,.2f}" if pd.notnull(row['budget']) else "Costo no disponible",
        "ganancia": f"${round(row['revenue'] - row['budget'], 2):,.2f}" if pd.notnull(row['revenue']) and pd.notnull(row['budget']) else "Ganancia no disponible"
    }
    for _, row in director_films.iterrows()
    
    # Formatear el nombre para que aparezca con iniciales en mayúsculas en el mensaje
    nombre_formateado = ' '.join([word.capitalize() for word in nombre_director.split()])

    return {
        "mensaje": f"El director {nombre_formateado} ha dirigido {len(film_info)} películas.",
        "detalles": film_info
    }