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

    # Filtrar y contar las películas que fueron estrenadas en el día de la semana deseado
    dia_num = dias_semana[dia]
    cantidad = data[data['release_date'].dt.weekday == dia_num].shape[0]

    # Retornar el mensaje
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
    actor_films = data[data['cast'].apply(lambda x: any(nombre_actor == actor.lower() for actor in x) if pd.notnull(x) else False)]


    # Verificar si el actor no se encuentra en la base de datos
    if actor_films.empty:
        return {
            "mensaje": f"No se encontraron registros para el actor {nombre_actor.capitalize()} en la base de datos."
        }
    
    # Contar películas con retorno igual a 0 (considerados como datos faltantes)
    peliculas_sin_retorno = len(actor_films[actor_films['return'] == 0])

    # Filtrar para el cálculo solo las filas donde `return` tiene un valor válido distinto de cero
    valid_returns = actor_films[actor_films['return'] != 0]

    # Calcular cantidad de películas, retorno total y promedio
    cantidad_peliculas = len(actor_films)
    retorno_total = round(valid_returns['return'].sum(), 2)
    retorno_promedio = round(retorno_total / len(valid_returns), 2) if len(valid_returns) > 0 else 'Datos no disponibles'

    # Formatear el nombre para que aparezca con iniciales en mayúsculas en el mensaje
    nombre_formateado = ' '.join([word.capitalize() for word in nombre_actor.split()])


    # Retornar el mensaje con los datos calculados, aclarando cómo se calcula el promedio
    return {
        "mensaje": f"El actor {nombre_formateado} ha participado en {cantidad_peliculas} películas.",
        "detalles": {
            "retorno_total": f"{retorno_total} veces la inversión",
            "retorno_promedio": retorno_promedio if retorno_promedio != "Datos no disponibles" else "Datos no disponibles",
            "aclaración": f"El retorno promedio se calcula sin incluir {peliculas_sin_retorno} películas cuyo retorno fue 0 por falta de datos."
        }
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
    
    # Filtrar las películas donde ..............
    director_films = data[data['directors'].apply(lambda x: nombre_director == x.lower() if pd.notnull(x) else False)]

    # Verificar si el director no se encuentra en la base de datos
    if director_films.empty:
        return {
            "mensaje": f"No se encontraron registros para el director {nombre_director.capitalize()} en la base de datos."
        }

    """
    # Contar películas con retorno igual a 0 (considerados como datos faltantes)
    peliculas_sin_retorno = len(director_films[director_films['return'] == 0])

    # Filtrar para el cálculo solo las filas donde `return` tiene un valor válido distinto de cero
    valid_returns = director_films[director_films['return'] != 0]

    # Calcular cantidad de películas, retorno total y promedio
    cantidad_peliculas = len(director_films)
    retorno_total = round(valid_returns['return'].sum(), 2)
    retorno_promedio = round(retorno_total / len(valid_returns), 2) if len(valid_returns) > 0 else 'Datos no disponibles'

    # Formatear el nombre para que aparezca con iniciales en mayúsculas en el mensaje
    nombre_formateado = nombre_director.title()

    # Retornar el mensaje con los datos calculados, aclarando cómo se calcula el promedio
    return {
        "mensaje": f"El director {nombre_formateado} ha participado en {cantidad_peliculas} películas.",
        "detalles": {
            "retorno_total": f"{retorno_total} veces la inversión",
            "retorno_promedio": retorno_promedio if retorno_promedio != "Datos no disponibles" else "Datos no disponibles",
            "aclaración": f"El retorno promedio se calcula sin incluir {peliculas_sin_retorno} películas cuyo retorno fue 0 por falta de datos."
        }
    }

    """
    # Crear una lista con la información de cada película dirigida por el director
    film_info = [
        {
            "pelicula": row['title'] if pd.notnull(row['title']) else "Título no disponible",
            "fecha_lanzamiento": row['release_date'].strftime("%d-%m-%Y") if pd.notnull(row['release_date']) else "Fecha no disponible",
            "retorno": (
                round(row['return'], 2) if pd.notnull(row['return']) and row['return'] != 0 else "Dato no disponible"
            ),
            "costo": f"${round(row['budget'], 2):,.2f}" if pd.notnull(row['budget']) else "Costo no disponible",
            "ganancia": (
                f"${round(row['revenue'] - row['budget'], 2):,.2f}"
                if pd.notnull(row['revenue']) and pd.notnull(row['budget']) and row['revenue'] > 0 else "Ganancia no disponible"
            )
        }
        for _, row in director_films.iterrows()
    ]

    # Formatear el nombre para que aparezca con iniciales en mayúsculas en el mensaje
    nombre_formateado = ' '.join([word.capitalize() for word in nombre_director.split()])

    # Verificar si se encontraron películas dirigidas por el director
    if not film_info:
        return {
            "mensaje": f"No se encontraron películas dirigidas por {nombre_formateado}."
        }
    
    return {
        "mensaje": f"El director {nombre_formateado} ha dirigido {len(film_info)} películas.",
        "detalles": film_info
    }

    

# 5. Función para obtener el score de un título
@app.get("/score_titulo/{titulo_de_la_filmacion}")
def score_titulo(titulo_de_la_filmacion: str):
    # Convertir el título a minúsculas para una comparación insensible a mayúsculas
    titulo_de_la_filmacion = titulo_de_la_filmacion.lower()
    
    # Filtrar la fila donde el título coincide
    film = data[data['title'].str.lower() == titulo_de_la_filmacion]
    
    # Verificar si el título no se encuentra en la base de datos
    if film.empty:
        return {
            "mensaje": f"No se encontró la filmación '{titulo_de_la_filmacion}' en la base de datos."
        }
    
    # Obtener título, año de estreno y score
    titulo = film['title'].values[0]
    año_estreno = film['release_date'].dt.year.values[0] if pd.notnull(film['release_date'].values[0]) else "Año no disponible"
    score = film['popularity'].values[0] if pd.notnull(film['popularity'].values[0]) else "Score no disponible"
    
    # Retornar el mensaje con los datos obtenidos
    return {
        "mensaje": f"La película '{titulo}' fue estrenada en el año {año_estreno} con un score/popularidad de {score}."
    }


# 6. Función para obtener votos y valor promedio de votos de un título
@app.get("/votos_titulo/{titulo_de_la_filmacion}")
def votos_titulo(titulo_de_la_filmacion: str):
    # Convertir el título a minúsculas para una comparación insensible a mayúsculas
    titulo_de_la_filmacion = titulo_de_la_filmacion.lower()
    
    # Filtrar la fila donde el título coincide
    film = data[data['title'].str.lower() == titulo_de_la_filmacion]
    
    # Verificar si el título no se encuentra en la base de datos
    if film.empty:
        return {
            "mensaje": f"No se encontró la filmación '{titulo_de_la_filmacion}' en la base de datos."
        }
    
    # Obtener el número de votos y el promedio de votaciones
    cantidad_votos = film['vote_count'].values[0] if pd.notnull(film['vote_count'].values[0]) else 0
    valor_promedio_votos = round(film['vote_average'].values[0], 2) if pd.notnull(film['vote_average'].values[0]) else "Promedio de votos no disponible"
    
    # Verificar si el título cumple con la condición mínima de 2000 votos
    if cantidad_votos < 2000:
        return {
            "mensaje": f"La película '{film['title'].values[0]}' no cumple con el mínimo de 2000 valoraciones, por lo tanto, no se devuelve ningún valor."
        }
    
    # Retornar el mensaje con los datos obtenidos
    return {
        "mensaje": f"La película '{film['title'].values[0]}' tiene {cantidad_votos} valoraciones, con un valor promedio de {valor_promedio_votos}."
    }
