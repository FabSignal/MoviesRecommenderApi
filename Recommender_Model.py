

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity



df = pd.read_parquet(r"C:\Users\Sofita\Documents\Henry\Movies\merged_data_actors.parquet")




# # Filtrar por popularity




# Aplicar múltiples filtros acumulativos
popularity_threshold = data['popularity'].quantile(0.75)
data_filtered = data[(data['popularity'] >= popularity_threshold) & 
                     (data['vote_count'] > 100) & 
                     (data['vote_average'] >= 6)].copy()

# Confirmar el tamaño del DataFrame filtrado
print(f"Filas después del filtro de popularidad y votos: {data_filtered.shape[0]}")
data_filtered.reset_index(drop=True, inplace=True)




# Filtrar las columnas deseadas y guardarlas en un nuevo DataFrame
data_filtered = data_filtered[['overview', 'title', 'genres_name', 'main_cast']].copy()



#data_filtered.to_csv('data_de_prueba.csv')




# Paso 1: Concatenar la información relevante en un campo
# Concatenamos géneros, elenco y sinopsis en una sola columna de "texto"



data_filtered['combined_features'] = data_filtered['genres_name'].apply(lambda x: ' '.join(x) + ' ') * 3 + \
                            data_filtered['overview'].fillna('') + \
                            data_filtered['main_cast'].apply(lambda x: ' '.join(x) + ' ') 


#data_filtered['combined_features'] = data_filtered['genres_name'].apply(lambda x: ' '.join(x) + ' ') * 3 + \
#                            data_filtered['overview'].fillna('') 
                            




# Paso 2: Convertir el texto en un vector de características
tfidf_vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf_vectorizer.fit_transform(data_filtered['combined_features'])




# Codificación binaria para `genres_name`
mlb_genres = MultiLabelBinarizer()
genres_encoded = mlb_genres.fit_transform(data_filtered['genres_name'])
genres_df = pd.DataFrame(genres_encoded, columns=[f'genre_{genre}' for genre in mlb_genres.classes_])

# Codificación binaria para `main_cast`
mlb_cast = MultiLabelBinarizer()
cast_encoded = mlb_cast.fit_transform(data_filtered['main_cast'])
cast_df = pd.DataFrame(cast_encoded, columns=[f'actor_{actor}' for actor in mlb_cast.classes_])

# Concatenar los DataFrames
data_filtered = pd.concat([data_filtered.reset_index(drop=True), genres_df, cast_df], axis=1)




# Definir el número de componentes
n_components = 100  # Puedes ajustar este valor según tu conjunto de datos
svd = TruncatedSVD(n_components=n_components)

# Aplicar SVD a la matriz TF-IDF
tfidf_reduced = svd.fit_transform(tfidf_matrix)





# Paso 1: Reducir la dimensión con SVD
tfidf_reduced = svd.fit_transform(tfidf_matrix)

# Paso 2: Convertir tfidf_reduced en un DataFrame temporal con nombres de columnas adecuados
tfidf_reduced_df = pd.DataFrame(tfidf_reduced, columns=[f'tfidf_component_{i}' for i in range(tfidf_reduced.shape[1])])

# Paso 3: Concatenar el DataFrame de componentes con data_filtered de una sola vez
data_filtered = pd.concat([data_filtered.reset_index(drop=True), tfidf_reduced_df], axis=1)





# Paso 3: Calcular la similitud del coseno entre todas las películas
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# Guardar la matriz de similitud en un archivo
with open('data/cosine_sim.pkl', 'wb') as f:
    pickle.dump(cosine_sim, f)







