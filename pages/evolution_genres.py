from dash import html, dcc, Output, Input, ALL, callback_context, callback
from dash.dependencies import State
import pandas as pd
import plotly.express as px
from static.enumerations import genre_colors, genres, genre_links
from data.data_manager import DataManager
import dash

dash.register_page(__name__, path="/evolutions", name="Evolution des genres")

#div static
articles = [
    html.Div(
        children=[
            html.Img(src=f"/static/images/{genre}.jpg", style={'width': '100%', 'border-radius': '5px'}),
            html.A(f"L'histoire {article} {genre.capitalize()}", href=link, target="_blank", style={'display': 'block', 'text-align': 'center', 'color': 'lightgrey'})
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
                        # Back to home button
            html.Div(style={'position': 'absolute', 'top': '30px', 'right': '30px', 'z-index': '1000', 'font-size': '40px'}, children=[
            dcc.Link('🏠', href='/'),
        ]),
            
        html.Div(id='collab-genre-colored-button', style={'flex': '1', 'padding': '10px', 'display': 'flex', 'flexWrap': 'wrap', 'gap': '10px'}, 
                 children=[
            html.Button(
                genre.title(),
                id=f'collab-genre-button-{genre}',  # Unique ID for each genre button
                n_clicks=0,
                style={
                    'backgroundColor': genre_colors.get(genre, '#CCCCCC'),
                    'color': 'white',
                    'border': 'none',
                    'padding': '10px 20px',
                    'cursor': 'pointer',
                    'borderRadius': '5px'
                }
            ) for genre in genre_colors.keys()
        ]),
            
        # Graph display area
        html.Div(
            style={'width': '70%'},
            children=[dcc.Graph(id="linear-graph", style={'backgroundColor': 'black'})]
        ),
                
             
        dcc.Store(id='selected-genres-collab', data={genre: genre in ['rock', 'r&b'] for genre in genres}),
        ]
        ),
        
        # Section des articles
        articles_section,
    ]
)


@callback(
    Output('linear-graph', 'figure'),
    Input('selected-genres-collab', 'data')
)
def update_content_evolution(selected_genres):

    active_genres = [genre for genre, selected in selected_genres.items() if selected]
    data_manager = DataManager()
    df = data_manager.create_album_release_dataframe(active_genres)
    
    if 'release_date' in df.columns:
        df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
        df['year'] = df['release_date'].dt.year
        albums_per_year = df.groupby(['year', 'genre']).size().reset_index(name='album_count')
    else:
        albums_per_year = pd.DataFrame(columns=['year', 'genre', 'album_count'])

    fig = px.line(albums_per_year, x="year", y="album_count", color='genre', color_discrete_map=genre_colors)
    fig.update_layout(
        plot_bgcolor='black', 
        paper_bgcolor='black', 
        font_color='white',
        xaxis_title="Année",
        yaxis_title="Nombre d'albums"
    )
    return fig
