

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity



df = pd.read_parquet("data_de_prueba.parquet")


data_filtered = df.copy()

"""
    Aquí se realiza el preprocesamiento de un conjunto de datos de películas
    para un sistema de recomendación basado en contenido. Los pasos incluyen:

    1. Concatenación de características textuales y categóricas relevantes como 
       géneros, elenco y sinopsis en una columna 'combined_features'.
    2. Conversión de la columna 'combined_features' en una matriz TF-IDF (Term Frequency - Inverse Document Frequency).
    3. Codificación binaria de las características 'genres_name' y 'main_cast' usando `MultiLabelBinarizer`.
    4. Aplicación de la descomposición SVD (Singular Value Decomposition) para reducir la dimensionalidad de la matriz TF-IDF.
    5. Cálculo de la similitud del coseno entre las películas.
    6. Guardado de la matriz de similitud en un archivo local para uso posterior.

    El resultado es un DataFrame que contiene las características procesadas de las películas y la matriz de similitud.

    """


data_filtered['combined_features'] = data_filtered['genres_name'].apply(lambda x: ' '.join(x) + ' ') * 2 + \
                            data_filtered['overview'].fillna('') + \
                            data_filtered['main_cast'].apply(lambda x: ' '.join(x) + ' ') 


tfidf_vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf_vectorizer.fit_transform(data_filtered['combined_features'])


mlb_genres = MultiLabelBinarizer()
genres_encoded = mlb_genres.fit_transform(data_filtered['genres_name'])
genres_df = pd.DataFrame(genres_encoded, columns=[f'genre_{genre}' for genre in mlb_genres.classes_])


mlb_cast = MultiLabelBinarizer()
cast_encoded = mlb_cast.fit_transform(data_filtered['main_cast'])
cast_df = pd.DataFrame(cast_encoded, columns=[f'actor_{actor}' for actor in mlb_cast.classes_])


data_filtered = pd.concat([data_filtered.reset_index(drop=True), genres_df, cast_df], axis=1)




n_components = 100  # Puedes ajustar este valor según tu conjunto de datos
svd = TruncatedSVD(n_components=n_components)

tfidf_reduced = svd.fit_transform(tfidf_matrix)



tfidf_reduced = svd.fit_transform(tfidf_matrix)


tfidf_reduced_df = pd.DataFrame(tfidf_reduced, columns=[f'tfidf_component_{i}' for i in range(tfidf_reduced.shape[1])])


data_filtered = pd.concat([data_filtered.reset_index(drop=True), tfidf_reduced_df], axis=1)




cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)


with open('data/cosine_sim.pkl', 'wb') as f:
    pickle.dump(cosine_sim, f)







