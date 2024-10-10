import pandas as pd
import plotly.express as px
from data.data_manager import DataManager
from static.enumerations import genre_colors


def build_linear_chart(selected_genres):
    data_manager = DataManager()
    
    album_data = pd.DataFrame()

    for genre in selected_genres:
        genre_album_df = data_manager.create_album_release_dataframe([genre])
        genre_album_df['genre'] = genre 
        album_data = pd.concat([album_data, genre_album_df], ignore_index=True)
    
    if album_data.empty:
        print("Aucun album trouvé pour les genres sélectionnés.")
        return None
    
    album_data['release_year'] = album_data['release_date'].dt.year
    genre_yearly_data = album_data.groupby(['genre', 'release_year']).size().reset_index(name='album_count')
    
    fig = px.line(
        genre_yearly_data, 
        x='release_year', 
        y='album_count', 
        color='genre', 
        title='Évolution du nombre d\'albums par genre au fil des années',
        line_shape='linear',
        markers=True,
        color_discrete_map=genre_colors 
    )
    
    fig.update_layout(
        xaxis_title='Année', 
        yaxis_title='Nombre d\'albums', 
        legend_title='Genres',
        plot_bgcolor='black',  # Fond noir
        paper_bgcolor='black',  # Fond noir
        font=dict(color='white')  # Texte blanc
    )
    
    return fig
