
# Fonction pour créer le Chord Diagram
def plot_chord_diagram(genre_matrix):
    genres = genre_matrix.index.tolist()
    matrix_values = genre_matrix.values
    
    # Créer le diagramme de chord
    fig = go.Figure(data=[go.Chord(
        labels=genres,           
        matrix=matrix_values,
        colorscale='Blues'
    )])

    fig.update_layout(title_text="Chord Diagram des collaborations entre genres musicaux",
                      font=dict(size=14))
    fig.show()

# Appel des fonctions
data_manager = DataManager()

# Créer la matrice de collaboration entre genres
genre_matrix = create_genre_collaboration_matrix(data_manager.tracks_collection, data_manager.artists_collection)

# Générer et afficher le diagramme de chord
plot_chord_diagram(genre_matrix)