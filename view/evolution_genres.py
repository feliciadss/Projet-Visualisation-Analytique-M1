from dash import html, dcc, Output, Input, ALL, callback_context
from dash.dependencies import State
import pandas as pd
import plotly.express as px
from static.enumerations import genre_colors, genres
from data.data_manager import DataManager

# Création des articles sous forme de Div statiques
articles = [
    html.Div(
        children=[
            html.Img(src=f"/static/images/{genre}.jpg", style={'width': '100%', 'border-radius': '5px'}),
            html.H3(f"L'histoire {article} {genre.capitalize()}", style={'text-align': 'center', 'color': 'white'}),
            html.A("Lire plus", href=link, target="_blank", style={'display': 'block', 'text-align': 'center', 'color': 'cyan'})
        ],
        style={
            'border': '1px solid #444',
            'border-radius': '5px',
            'padding': '10px',
            'background-color': '#333',
            'width': '100%',
            'box-shadow': '2px 2px 5px rgba(0,0,0,0.5)'
        }
    ) for genre, (article, link) in genre_links.items()
]

# Organisation des articles en 3 rangées de 5 colonnes
articles_section = html.Div(
    id="articles-section",
    style={
        'marginTop': '20px',
        'padding': '10px',
        'backgroundColor': '#333',
        'borderRadius': '10px',
        'width': '80%',
        'margin': 'auto',
        'textAlign': 'left',
        'color': 'white'
    },
    children=[
        html.Div(
            children=articles[i:i+5],
            style={'display': 'flex', 'justify-content': 'space-around', 'gap': '10px', 'margin-top': '10px'}
        ) for i in range(0, len(articles), 5)
    ]
)

# Layout for Evolution of Genres page
layout = html.Div(
    style={'backgroundColor': 'black', 'color': 'white', 'padding': '20px', 'textAlign': 'center'},
    children=[
        html.H1('Évolution de la popularité des genres', style={'color': 'white'}),
        html.H3(
            "Découvrez l'évolution de leur popularité depuis 50 ans en sélectionnant un ou plusieurs genres.",
            style={'textAlign': 'center', 'color': 'white', 'fontWeight': 'normal', 'paddingLeft': '50px', 'paddingRight': '50px'}
        ),

        html.Div(
            style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'flex-start'},
            children=[
                # Genre selection buttons with unique IDs
                html.Div(
                    id='evolution-genre-colored-button',
                    style={'flex': '1', 'padding': '10px', 'display': 'flex', 'flexWrap': 'wrap', 'gap': '10px'},
                    children=[
                        html.Button(
                            genre.title(),
                            id={'type': 'evolution-genre-button', 'index': genre},  # Unique type for this page
                            n_clicks=0,
                            style={
                                'backgroundColor': genre_colors.get(genre, '#CCCCCC'),  # Ensure this gets the right color
                                'color': 'white',
                                'border': 'none',
                                'padding': '10px 20px',
                                'cursor': 'pointer',
                                'borderRadius': '5px'
                            }
                        ) for genre in genres
                    ]
                ),

                # Graph display area
                html.Div(
                    style={'width': '70%'},
                    children=[dcc.Graph(id="linear-graph", style={'backgroundColor': 'black'})]
                ),
                
                # Store the selected genres with 'rock' selected by default
                dcc.Store(id='selected-genres-evolution', data={genre: (genre == 'rock') for genre in genres}),
            ]
        ),
        
        # Section des articles statiques en 3 rangées de 5 colonnes
        articles_section,
    ]
)

# Register callback function for Evolution of Genres page
def register_callback(app):
    @app.callback(
        [Output("linear-graph", "figure"),
         Output('selected-genres-evolution', 'data'),
         Output({'type': 'evolution-genre-button', 'index': ALL}, 'style')],
        Input({'type': 'evolution-genre-button', 'index': ALL}, 'n_clicks'),
        State('selected-genres-evolution', 'data')
    )
    def update_content_evolution(n_clicks_list, selected_genres):
        # Determine which button was clicked
        triggered = callback_context.triggered
        if triggered:
            triggered_id = eval(triggered[0]['prop_id'].split('.')[0])
            genre = triggered_id['index']
            selected_genres[genre] = not selected_genres[genre]  # Toggle the selected genre

        # Filter data based on selected genres
        selected_genres_list = [genre for genre, selected in selected_genres.items() if selected]
        data_manager = DataManager()
        df = data_manager.create_album_release_dataframe(selected_genres_list)
        
        # Check for 'release_date' and handle it if missing
        if 'release_date' in df.columns:
            df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
            df['year'] = df['release_date'].dt.year
            albums_per_year = df.groupby(['year', 'genre']).size().reset_index(name='album_count')
        else:
            albums_per_year = pd.DataFrame(columns=['year', 'genre', 'album_count'])

        # Create line graph
        fig = px.line(albums_per_year, x="year", y="album_count", color='genre')
        fig.update_layout(
            plot_bgcolor='black', 
            paper_bgcolor='black', 
            font_color='white',
            xaxis_title="Année",
            yaxis_title="Nombre d'albums"
        )

        # Update button styles based on selection
        button_styles = [
            {
                'backgroundColor': genre_colors.get(genre, '#CCCCCC') if selected_genres[genre] else '#555555',
                'color': 'white',
                'border': 'none',
                'padding': '15px 25px',
                'cursor': 'pointer',
                'fontSize': '16px',
                'borderRadius': '5px'
            }
            for genre in genres
        ]

        return fig, selected_genres, button_styles
