from dash import html, dcc, callback, Input, Output
import pandas as pd
import plotly.express as px
from static.enumerations import genres
from data.data_manager import DataManager

layout = html.Div(style={'backgroundColor': 'black', 'color': 'white', 'padding': '20px', 'textAlign': 'center'}, children=[
    html.H1('Évolution de la popularité des genres', style={'color': 'white'}),
    html.H3(
        "Cette page illustre l'évolution du nombre de pistes musicales par genre au fil des ans. ",
        style={'textAlign': 'center', 'color': 'white', 'fontWeight': 'normal'}
    ),
    html.H3(
        "En sélectionnant différents genres dans la liste, vous pourrez observer les tendances de popularité et ",
        style={'textAlign': 'center', 'color': 'white', 'fontWeight': 'normal'}),

    html.H3(
        "identifier les variations de la production musicale.",
        style={'textAlign': 'center', 'color': 'white', 'fontWeight': 'normal'}),
    
    html.P(
        "Sélectionnez un ou plusieurs genres :", 
        style={'fontWeight': 'bold', 'color': 'white'}
    ),
    # Conteneur pour centrer la checklist et le graphique
    html.Div(style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'flex-start'}, children=[
        # Bouton pour revenir à l'accueil
        html.Div(style={'position': 'absolute','top': '30px','right': '30px','z-index': '1000','font-size': '40px'},children=[
            dcc.Link('🏠', href='/'),
        ]),
        # Liste des genres
        html.Div(style={'marginRight': '20px'}, children=[
            dcc.Checklist(
                id="linear-checklist",
                options=genres,
                value=["rock"],
                inline=False, 
                style={'color': 'white'}
            )
        ]),

        # Graphique
        html.Div(style={'width': '70%'}, children=[
            dcc.Graph(id="linear-graph", style={'backgroundColor': 'black'})
        ]),
    ]),
])

def register_callback(app):
    @app.callback(
        Output("linear-graph", "figure"), 
        Input("linear-checklist", "value"))
    
    def update_line_chart(selected_genres):
        data_manager = DataManager()
        df = data_manager.create_album_release_dataframe(selected_genres)
        df['release_date'] = pd.to_datetime(df['release_date'])
        df['year'] = df['release_date'].dt.year
        albums_per_year = df.groupby(['year', 'genre']).size().reset_index(name='album_count')
        fig = px.line(albums_per_year, 
                       x="year", y="album_count", color='genre')
        
    
        fig.update_layout(
            plot_bgcolor='black', 
            paper_bgcolor='black', 
            font_color='white'
        )
        
        return fig
