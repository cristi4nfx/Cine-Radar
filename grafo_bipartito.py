import tkinter as tk
from tkinter import messagebox
import os
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

# Cargar los datos
data_path = "Peliculas.csv"
try:
    data = pd.read_csv(data_path)
except FileNotFoundError:
    messagebox.showerror("Error", f"No se encontró el archivo '{data_path}'.")
    exit()

# Crear el grafo bipartito
B = nx.Graph()
nombres_usuarios = data["name"].unique()
titulos_peliculas = data["title"].unique()

B.add_nodes_from(nombres_usuarios, bipartite=0, label="usuario")
B.add_nodes_from(titulos_peliculas, bipartite=1, label="pelicula")

edges = [(row["name"], row["title"], row["rating"]) for _, row in data.iterrows()]
B.add_weighted_edges_from(edges)


# Función para mostrar las películas
def mostrar_peliculas():
    peliculas = sorted(data["title"].unique())
    peliculas_texto = "\n".join(f"{i+1}. {pelicula}" for i, pelicula in enumerate(peliculas))
    messagebox.showinfo("Películas", peliculas_texto)


# Función para mostrar el grafo
def mostrar_grafo():
    pos = {}
    for i, user in enumerate(nombres_usuarios):
        pos[user] = (-1, i)
    for j, movie in enumerate(titulos_peliculas):
        pos[movie] = (1, j)

    plt.figure(figsize=(12, 14))
    nx.draw_networkx_nodes(B, pos, nodelist=nombres_usuarios, node_color="skyblue", label="Usuarios")
    nx.draw_networkx_nodes(B, pos, nodelist=titulos_peliculas, node_color="salmon", label="Películas")
    nx.draw_networkx_edges(B, pos, edgelist=edges, width=1, alpha=0.7)
    nx.draw_networkx_labels(B, pos, font_size=8)

    plt.title("Grafo Bipartito de Usuarios y Películas")
    plt.axis("off")
    plt.show()


# Función para mostrar películas mejor valoradas
def mejor_valoradas():
    peliculas_agrupadas = data.groupby("title")["rating"].agg(["sum", "count", "mean"])
    peliculas_ordenadas = peliculas_agrupadas.sort_values(by="mean", ascending=False).round(1)

    texto = f"{'Título':<60} {'Veces Calificada':<20} {'Calificación':<10}\n"
    texto += "-" * 100 + "\n"
    for titulo, row in peliculas_ordenadas.iterrows():
        texto += f"{titulo:<66} {int(row['count']):<19} {row['mean']:<10}\n"

    mostrar_ventana_larga("Películas Mejor Valoradas", texto)


# Función para recomendar películas
def recomendar_peliculas():
    usuario = usuario_entry.get()
    if usuario not in nombres_usuarios:
        messagebox.showerror("Error", "Usuario no encontrado.")
        return

    peliculas_usuario = data[data["name"] == usuario][["title", "rating"]]
    usuarios_similares = []

    for user in nombres_usuarios:
        if user != usuario:
            peliculas_user = data[data["name"] == user][["title", "rating"]]
            peliculas_comunes = pd.merge(
                peliculas_usuario, peliculas_user, on="title", suffixes=("_usuario", "_otro")
            )
            peliculas_similares = peliculas_comunes[
                abs(peliculas_comunes["rating_usuario"] - peliculas_comunes["rating_otro"]) <= 0.5
            ]
            if len(peliculas_similares) >= 3:
                usuarios_similares.append(user)

    if not usuarios_similares:
        messagebox.showinfo("Recomendaciones", "No se encontraron usuarios similares. \n Por favor califique mas peliculas")
        return

    recomendaciones = []
    for similar_user in usuarios_similares:
        peliculas_similar_user = data[(data["name"] == similar_user) & (data["rating"] > 3.5)]
        peliculas_no_vistas = peliculas_similar_user[
            ~peliculas_similar_user["title"].isin(peliculas_usuario["title"])
        ]
        recomendaciones.extend(
            [(row["title"], row["rating"]) for _, row in peliculas_no_vistas.iterrows()]
        )

    recomendaciones = list(set(recomendaciones))
    recomendaciones.sort(key=lambda x: x[1], reverse=True)
    top_recomendaciones = recomendaciones[:5]

    if top_recomendaciones:
        texto = "\n".join(
            f"{i+1}. {titulo} - Calificación: {rating}" for i, (titulo, rating) in enumerate(top_recomendaciones)
        )
    else:
        texto = "No hay recomendaciones disponibles."

    messagebox.showinfo("Recomendaciones", texto)


# Función para mostrar una ventana larga con scroll
def mostrar_ventana_larga(titulo, texto):
    ventana = tk.Toplevel(root)
    ventana.title(titulo)
    text_widget = tk.Text(ventana, wrap=tk.WORD, width=100, height=30)
    text_widget.insert(tk.END, texto)
    text_widget.configure(state="disabled")
    text_widget.pack(padx=10, pady=10)


# Interfaz gráfica
root = tk.Tk()
root.title("Cine Radar")
root.geometry("400x500")

tk.Label(root, text="🎬 Cine Radar", font=("Arial", 20, "bold")).pack(pady=10)

tk.Button(root, text="🎥 Mostrar todas las películas", command=mostrar_peliculas, width=30).pack(pady=5)
tk.Button(root, text="🔗 Ver grafo de relaciones", command=mostrar_grafo, width=30).pack(pady=5)
tk.Button(root, text="⭐ Películas mejor calificadas", command=mejor_valoradas, width=30).pack(pady=5)

tk.Label(root, text="📽️ Recomendaciones").pack(pady=10)
tk.Label(root, text="Ingrese el nombre del usuario:").pack()
usuario_entry = tk.Entry(root, width=30)
usuario_entry.pack(pady=5)
tk.Button(root, text="Recomendar Películas", command=recomendar_peliculas, width=30).pack(pady=5)

tk.Button(root, text="❌ Salir", command=root.quit, width=30).pack(pady=20)

root.mainloop()
