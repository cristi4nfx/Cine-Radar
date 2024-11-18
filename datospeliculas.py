import pandas as pd
import os

# Lista de nombres predefinidos
nombres = [
    "Alex", "Blake", "Casey", "Drew", "Evan", "Finn", "Gray", "Harper", "Jamie", "Jordan", "Kai", "Logan",
    "Morgan", "Parker", "Quinn", "Reese", "Riley", "Rowan", "Shay", "Sky", "Tatum", "Taylor", "Zion", "Avery",
    "Bailey", "Cameron", "Charlie", "Dakota", "Dallas", "Elliott", "Emerson", "Hayden", "Hunter", "Jayden",
    "Jesse", "Justice", "Kendall", "Kennedy", "Lennon", "Marlow", "Marley", "Micah", "Noel", "Oakley", "Peyton",
    "Phoenix", "Quincy", "Raine", "Remy", "Robin", "Sage", "Sam", "Sawyer", "Scout", "Shawn", "Sloan", "Stevie",
    "Storm", "Toby", "Wren", "Aiden", "Angel", "Ash", "Aspen", "August", "Billie", "Blaine", "Briar", "Brook",
    "Campbell", "Chase", "Chris", "Corey", "Dylan", "Easton", "Ellis", "Emery", "Eren", "Frankie", "Gabriel",
    "Gael", "Indigo", "Jace", "Jamie", "Jean", "Jess", "Jules", "Jules", "Justice", "Kade", "Keegan", "Kieran",
    "Lake", "Lennox", "Levi", "Lex", "Lincoln", "Luca", "Lyric", "Maddox", "Maverick", "Mckenzie", "Milan",
    "Monroe", "Morgan", "Nico", "Oaklee", "Onyx", "Orion", "Paris", "Pax", "Payton", "Rain", "Reagan", "Rex",
    "River", "Rome", "Rory", "Ryan", "Ryker", "Sasha", "Shiloh", "Skye", "Sterling", "Stormy", "Sunny", "Sutton",
    "Sydney", "Taj", "Teagan", "Terry", "Theo", "Tory", "Tristan", "True", "Ty", "Val", "Winter", "Zane", "Zen",
    "Ari", "Alexis", "Blair", "Carter", "Cleo", "Devon", "Emery", "Emmett", "Finnley", "Georgie", "Grier", 
    "Hunter", "Jaiden", "Joey", "Keaton", "Lane", "Laurie", "Linden", "Lyra", "Marley", "Nevada", "Ocean", 
    "Presley", "Quinn", "Rafe", "Rae", "Remington", "Ryder", "Sloane", "Tanner", "Tori", "Vaughn", "West", 
    "Wyatt", "Zeke", "Zoey", "Wade", "Rowe", "Lark", "Oak", "Reed"
]

# Ruta a los archivos
base_path = os.path.join(os.path.dirname(__file__), 'ml-25m')
ratings_path = os.path.join(base_path, "ratings.csv")
movies_path = os.path.join(base_path, "movies.csv")

# Cargar los datos
ratings = pd.read_csv(ratings_path)
movies = pd.read_csv(movies_path)

# Filtrar películas lanzadas después del año 2000
movies['year'] = movies['title'].str.extract(r'\((\d{4})\)').astype(float)
movies_recent = movies[movies['year'] > 2000]

# Unir con ratings para obtener solo películas recientes
ratings_recent = ratings.merge(movies_recent[['movieId', 'title']], on='movieId')

# Seleccionar 50 películas con al menos 4 calificaciones de distintos usuarios
top_movies = (
    ratings_recent.groupby('movieId')
    .filter(lambda x: x['userId'].nunique() >= 4)
    .movieId.value_counts()
    .head(50)
    .index
)

ratings_filtered_movies = ratings_recent[ratings_recent['movieId'].isin(top_movies)]

# Filtrar 150 usuarios que hayan calificado entre 3 y 8 de estas películas
user_movie_counts = ratings_filtered_movies.groupby('userId').movieId.nunique()
selected_users = user_movie_counts[(user_movie_counts >= 3)].index[:150]
final_ratings = ratings_filtered_movies[ratings_filtered_movies['userId'].isin(selected_users)]

def sample_user_ratings(df):
    if len(df) > 8:
        return df.sample(8)
    return df

final_ratings = final_ratings.groupby('userId', group_keys=False).apply(sample_user_ratings).reset_index(drop=True)

# Assign names to the selected users
final_ratings['name'] = final_ratings['userId'].map(dict(zip(selected_users[:150], nombres[:150])))

# Renombrar y guardar el archivo
output_file = 'Peliculas.csv'
final_ratings = final_ratings[['userId', 'name', 'movieId', 'title', 'rating']]
final_ratings.to_csv(output_file, index=False)

print("Datos filtrados y guardados en 'Peliculas.csv'")