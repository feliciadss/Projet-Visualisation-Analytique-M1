from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px
from data.data_manager import DataManager
from static.enumerations import genre_colors
import numpy as np

app = Dash(__name__, suppress_callback_exceptions=True)

# Layout de la page d'accueil
home_layout = html.Div(style={'backgroundColor': 'black', 'minHeight': '100vh', 'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'justifyContent': 'center', 'color': 'white'}, children=[
    html.H1("Analyse des Genres Musicaux en Europe"),
    html.H2(
        "Ce site web vous fournit des informations clés sur la popularité des genres musicaux en Europe, "
        "l'évolution des tendances par pays, ainsi que les collaborations entre artistes de différents genres. "
        "En analysant les données des dernières années, vous pourrez suivre la croissance ou le déclin des genres, "
        "évaluer la diversité et l'influence des genres à travers les featurings, et ainsi identifier les meilleures "
        "opportunités d'investissement dans de nouveaux artistes et collaborations.",
        style={'textAlign': 'center', 'color': 'white', 'fontWeight': 'normal'}
    ),
    html.P("Sélectionnez une analyse à explorer :"),
    html.Div([
        dcc.Link(
            html.Button('Popularité des genres', style={'margin': '10px', 'color': 'black', 'backgroundColor': 'white', 'fontSize': '20px', 'padding': '15px 30px'}),
            href='/popularite'
        ),
        dcc.Link(
            html.Button('Évolution des genres', style={'margin': '10px', 'color': 'black', 'backgroundColor': 'white', 'fontSize': '20px', 'padding': '15px 30px'}),
            href='/evolution_genres'
        ),
        dcc.Link(
            html.Button('Collaborations entre genres', style={'margin': '10px', 'color': 'black', 'backgroundColor': 'white', 'fontSize': '20px', 'padding': '15px 30px'}),
            href='/collaborations'
        ),
        dcc.Link(
            html.Button('Caractéristiques musicales', style={'margin': '10px', 'color': 'black', 'backgroundColor': 'white', 'fontSize': '20px', 'padding': '15px 30px'}),
            href='/caract_musicales'
        ),
    ], style={'display': 'flex', 'justifyContent': 'center', 'flexDirection': 'row', 'gap': '20px'}),
    
    html.H3("Nous avons catégorisé les genres en 14 grandes catégories. Sélectionnez un genre pour voir les sous-genres associés :", style={'color': 'white', 'paddingTop': '40px'}),

    # Conteneur principal
    html.Div(style={'display': 'flex', 'justifyContent': 'flex-start', 'alignItems': 'center', 'width': '100%', 'padding': '20px'}, children=[
        
        # Bubble chart à gauche
        html.Div(style={'flex': '0 0 40%', 'padding': '10px'}, children=[
            dcc.Graph(id="bubble-chart", style={'height': '600px', 'width': '100%'})
        ]),

        # Histogramme horizontal à droite
        html.Div(style={'flex': '1', 'padding': '10px', 'textAlign': 'left'}, children=[
            dcc.Graph(id="histogram-chart", style={'height': '600px', 'width': '100%'})
        ]),
    ])
])

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    return home_layout  

# Callback pour le bubble chart et l'histogramme
@app.callback(
    Output("bubble-chart", "figure"),
    Output("histogram-chart", "figure"),
    Input("bubble-chart", "clickData")
)
def update_charts(click_data):
    data_manager = DataManager()
    
    genre_counts_df = data_manager.create_genre_count_dataframe()

    # Génération aléatoire positions bulles (evite le chevauchement)
    np.random.seed(42)
    genre_counts_df['x'] = np.random.uniform(low=-1, high=1, size=len(genre_counts_df))
    genre_counts_df['y'] = np.random.uniform(low=-1, high=1, size=len(genre_counts_df))

    fig_bubble = px.scatter(
        genre_counts_df,
        x='x',
        y='y',
        size='total_count',
        color='genre',
        hover_name='genre',
        size_max=60,
        color_discrete_map=genre_colors
    )
    fig_bubble.update_layout(
        plot_bgcolor='black',
        paper_bgcolor='black',
        font_color='white',
        showlegend=False,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        title="Cliquez sur un genre pour voir les sous-genres"
    )

    fig_histogram = go.Figure()

    if click_data:
        selected_genre = click_data['points'][0]['hovertext']
        df_subgenres = data_manager.get_top_subgenres_per_genre(selected_genre)
        
        df_subgenres = df_subgenres[df_subgenres['subgenre'] != selected_genre]

        fig_histogram.add_trace(
            go.Bar(
                x=df_subgenres['count'],
                y=df_subgenres['subgenre'],
                orientation='h',
                marker=dict(color=genre_colors.get(selected_genre.lower(), 'white'))
            )
        )
        fig_histogram.update_layout(
            plot_bgcolor='black',
            paper_bgcolor='black',
            font_color='white',
            title=f"Répartition des sous-genres pour {selected_genre}",
            xaxis=dict(title="Nombre d'artistes"),
            yaxis=dict(title="Sous-genres")
        )

    return fig_bubble, fig_histogram

if __name__ == '__main__':
    app.run_server(debug=True)
