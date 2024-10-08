import plotly.express as px
from data.data_manager import DataManager
from static.enumerations import genre_colors  

def build_bubble_chart(genre):
    data_manager = DataManager()
    df_subgenres = data_manager.get_top_subgenres_per_genre(genre)
    
    if df_subgenres.empty:
        print("Aucune donnée disponible pour les sous-genres.")
        return None
    
    genre_color = genre_colors.get(genre.lower(), '#ffffff')  # Blanc par défaut

    fig = px.scatter(df_subgenres, 
                     x='subgenre', 
                     y='count', 
                     size='count', 
                     color_discrete_sequence=[genre_color],  
                     hover_name='subgenre',
                     title=f'Diagramme en Bulles pour le genre {genre}',
                     labels={'subgenre': 'Sous-genres', 'count': 'Nombre d\'artistes'},
                     size_max=60) 


    fig.update_layout(
        plot_bgcolor='black',  
        paper_bgcolor='black',  # Fond noir 
        font_color='white',  # Texte en blanc 
        title_font_color='white',  # Titre blanc
        xaxis=dict(
            title_font=dict(color='white'), 
            tickfont=dict(color='white'),    
            showgrid=False, 
            zeroline=False
        ),
        yaxis=dict(
            title_font=dict(color='white'), 
            tickfont=dict(color='white'), 
            showgrid=False, 
            zeroline=False
        ),
        title=dict(
            font=dict(color='white') 
        )
    )

    return fig.to_html(full_html=False)
