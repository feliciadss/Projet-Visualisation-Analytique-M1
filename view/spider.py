import plotly.express as px
from data.data_manager import create_spider_chart_dataframe  # Importer la fonction qui génère le DataFrame

# Créer la Spider Chart en fonction des genres sélectionnés
def create_spider_chart(selected_genres):
    df = create_spider_chart_dataframe(selected_genres)  # Génération autonome du DataFrame depuis data_manager
    print(df.head())
    fig = px.line_polar(
        df,
        r='value',  # Valeurs des caractéristiques
        theta='feature',  # Caractéristiques audio (tempo, energy, etc.)
        color='genre',  # Lignes de couleur par genre
        line_close=True
    )

    fig.update_traces(fill='toself')
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1])
        ),
        showlegend=True  # Afficher la légende des genres
    )

    return fig
