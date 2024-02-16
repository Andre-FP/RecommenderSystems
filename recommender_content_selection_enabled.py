import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
from tkinter import Canvas, Frame, Label, Scrollbar, VERTICAL

# Carregar os dados dos filmes
# The file path needs to be updated with the correct path where the movies.csv is located
movies_df = pd.read_csv('movies.csv')
movies_df['year'] = movies_df['title'].str.extract('(\(\d{4}\))')
movies_df['year'] = movies_df['year'].str.extract('(\d{4})')
movies_df['title'] = movies_df['title'].str.replace('(\(\d{4}\))', '').str.strip()
movies_df['genres'] = movies_df['genres'].str.split('|')

# Criando variáveis dummy para os gêneros
movies_with_dummies = movies_df.copy()
for index, row in movies_df.iterrows():
    for genre in row['genres']:
        movies_with_dummies.at[index, genre] = 1
movies_with_dummies = movies_with_dummies.fillna(0)

# Função de recomendação baseada em gênero
def recommend_similar_movies(movie_title, movies_df, top_n=10):
    if movie_title not in movies_df['title'].values:
        return f"O filme '{movie_title}' não foi encontrado na base de dados."
    movie_index = movies_df.index[movies_df['title'] == movie_title].tolist()[0]
    movie_genres = movies_df.loc[movie_index, 'Adventure':'(no genres listed)'].values.reshape(1, -1)
    movies_genres_table = movies_df.loc[:, 'Adventure':'(no genres listed)']
    similarity = cosine_similarity(movie_genres, movies_genres_table)
    similarity_df = pd.DataFrame(similarity.T, index=movies_df['title'], columns=['similarity'])
    similar_movies = similarity_df.sort_values(by='similarity', ascending=False)
    similar_movies = similar_movies[similar_movies.index != movie_title]
    return similar_movies.head(top_n)

# Interface gráfica do usuário
def gui_recommend_movies():
    
    
    # Atualizar a lista de filmes à medida que o usuário digita
    def update_movie_list(event):
        max_movies_display = 10
        search_term = entry.get().lower()
        filtered_movies = [movie for movie in movies_df['title'] if search_term in movie.lower()]
        # Clear the previous movie labels in the frame
        for widget in frame.winfo_children():
            widget.destroy()
        # Create a label for each filtered movie (up to max_movies_display) and add it to the frame
        for movie in filtered_movies[:max_movies_display]:  # Limit the number of displayed movies
            movie_label = Label(frame, text=movie, anchor='center', bg='white')
            movie_label.bind('<Button-1>', lambda e, movie=movie: on_movie_select(e, movie))
            movie_label.pack(fill='x')

    def on_movie_select(event, movie_title):
        entry.delete(0, tk.END)
        entry.insert(0, movie_title)
        on_select(None)

    # Quando um filme é selecionado na Listbox
    def on_select(event):
        selected_movie = entry.get()
        recommendations = recommend_similar_movies(selected_movie, movies_with_dummies, top_n=10)
        # Clear the previous results
        for widget in frame.winfo_children():
            widget.destroy()
        # If the function returns a string, it means there was an error
        if isinstance(recommendations, str):
            result_label.config(text=recommendations)
        else:
            for movie in recommendations.index:
                movie_label = Label(frame, text=movie, anchor='w', bg='white')
                movie_label.bind('<Button-1>', lambda e, movie=movie: on_movie_select(e, movie))
                movie_label.pack(fill='x')

    # Janela principal
    root = tk.Tk()
    root.title("Sistema de Recomendação Baseado em Conteúdo")

    # Adicionar um cabeçalho à interface do usuário
    title_label = tk.Label(root, text='Sistema de Recomendação Baseado em Conteúdo', font=('Helvetica', 20, 'bold'))
    title_label.pack(pady=10)
    default_font = tkFont.nametofont("TkDefaultFont")
    default_font.configure(size=14)
    root.option_add("*Font", default_font)
    root.title("Sistema de Recomendação de Filmes")

    # Criação da Entry para entrada de texto
    entry_label = tk.Label(root, text="Digite o nome do filme:")
    entry_label.pack(pady=5)

    entry = tk.Entry(root, width=60)
    entry.pack(pady=5)
    entry.bind('<KeyRelease>', update_movie_list)  # Atualizar lista de filmes quando o usuário digita
    entry.bind('<Return>', on_select)  # Get recommendations when Enter is pressed

    # Criação do Canvas e do Frame para lista de filmes correspondentes à entrada do usuário
    canvas = Canvas(root)
    scrollbar = Scrollbar(root, command=canvas.yview)
    frame = Frame(canvas)

    # Adicionando a Scrollbar ao Canvas
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side='right', fill='y')
    canvas.pack(side='left', fill='both', expand=True)
    canvas.create_window((0, 0), window=frame, anchor='nw')

    frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    # Label para exibir os resultados
    result_label = tk.Label(root, text="", justify=tk.LEFT)
    result_label.pack(pady=10)

    # Rodar a janela
    root.mainloop()

# Rodar a interface gráfica
gui_recommend_movies()
