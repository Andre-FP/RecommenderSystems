import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont

# Carregar os dados dos filmes e avaliações
movies_df = pd.read_csv('movies.csv')
ratings_df = pd.read_csv('ratings.csv')

# Criando um mapa de IDs de filmes para índices e vice-versa
movie_to_idx = {movie: idx for idx, movie in enumerate(movies_df['movieId'])}
idx_to_movie = {idx: movie for movie, idx in movie_to_idx.items()}

# Preparando a matriz de usuário-item
ratings_pivot = ratings_df.pivot(index='movieId', columns='userId', values='rating').fillna(0)
ratings_matrix = csr_matrix(ratings_pivot.values)

# Definindo o modelo KNN
knn_model = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=20, n_jobs=-1)
knn_model.fit(ratings_matrix)

# Função de recomendação com KNN
def movie_recommender(movie_id, data, model, n_recommendations):
    model_index = movie_to_idx[movie_id]
    distances, indices = model.kneighbors(data.iloc[model_index, :].values.reshape(1, -1), n_neighbors=n_recommendations+1)
    recommendations = []
    for i, (idx, dist) in enumerate(sorted(list(zip(indices.squeeze().tolist(), distances.squeeze().tolist())), key=lambda x: x[1])[:0:-1]):
        if idx in idx_to_movie:
            movie_id = idx_to_movie[idx]
            movie_title = movies_df.loc[movies_df['movieId'] == movie_id, 'title'].values[0]
            recommendations.append(f"{movie_title} (Similarity: {1 - dist:.2f})")
    return recommendations

# Função para atualizar a combobox com base no texto digitado
def update_combobox(*args):
    typed_text = combo_var.get()
    matching_movies = [movie for movie in movies_df['title'] if typed_text.lower() in movie.lower()]
    combo['values'] = matching_movies

# GUI
def recommend():
    recommendations_label['text'] = ""  # Limpar as recomendações anteriores
    movie_name = combo.get()
    movie_id = movies_df.loc[movies_df['title'] == movie_name, 'movieId'].values[0]
    recommendations = movie_recommender(movie_id, ratings_pivot, knn_model, 10)
    recommendations_text = "\n".join(recommendations)  # Junta as recomendações em um único texto
    recommendations_label['text'] = recommendations_text

root = tk.Tk()
root.title("Sistema de Recomendação com Filtragem Colaborativa")

# Adicionar um cabeçalho à interface do usuário
title_label = tk.Label(root, text='Sistema de Recomendação com Filtragem Colaborativa', font=('Helvetica', 20, 'bold'))
title_label.pack(pady=10)
default_font = tkFont.nametofont("TkDefaultFont")
default_font.configure(size=14)
root.option_add("*Font", default_font)

label = tk.Label(root, text="Digite o título do filme:")
label.pack()

# Variável de controle para a combobox
combo_var = tk.StringVar()
combo_var.trace('w', update_combobox)  # Chama a função update_combobox quando o texto na combobox é alterado
combo = ttk.Combobox(root, textvariable=combo_var, width=50)
combo.pack()

button = tk.Button(root, text="Recomendar Filmes", command=recommend)
button.pack()

recommendations_label = tk.Label(root, text="", justify=tk.LEFT)
recommendations_label.pack()

root.mainloop()