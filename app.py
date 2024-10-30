from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px
from data.data_manager import DataManager
from static.enumerations import genre_colors
import numpy as np
from view.popularite import layout as map_layout, register_callback as register_map_callback
from view.evolution_genres import layout as linear_layout, register_callback as register_linear_callback
from view.collaborations import layout as sankey_layout, register_callback as register_sankey_callback
from view.caract_musicales import layout as radar_layout, register_callback as register_radar_callback

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
    
    html.H3("Pour rendre l'expérience plus agréable, nous avons classé les genres en 13 grandes catégories. Chaque catégorie regroupe des sous-genres que vous pouvez explorer en cliquant sur le diagramme circulaire.", style={'textAlign': 'center', 'color': 'white', 'fontWeight': 'normal'}),

    # Conteneur pour le pie chart et l'histogramme
    html.Div(style={'display': 'flex', 'justifyContent': 'flex-start', 'alignItems': 'center', 'width': '100%', 'padding': '20px'}, children=[
        
        # Pie chart à gauche
        html.Div(style={'flex': '0 0 40%', 'padding': '10px'}, children=[
            dcc.Graph(id="pie-chart", style={'height': '600px', 'width': '100%'})
        ]),

        # Histogramme horizontal à droite
        html.Div(style={'flex': '1', 'padding': '10px', 'textAlign': 'left'}, children=[
            dcc.Graph(id="histogram-chart", style={'height': '600px', 'width': '100%'})
        ]),
    ]),
    # Pied de page
    html.Footer(
        html.Small(
            [
                "Les données sont fournies par l' ",
                html.A("API Spotify", href="https://developer.spotify.com/documentation/web-api", target="_blank", style={'color': 'white'}),
            ]
        ),
        style={
            "textAlign": "center",
            "padding": "10px",
            "backgroundColor": "black",
            "width": "100%",
            "fontSize": "12px",
            "color": "#999",
            "position": "fixed",
            "bottom": "0",
        },
    ),
])

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/popularite':
        return map_layout
    elif pathname == '/evolution_genres':
        return linear_layout
    elif pathname == '/collaborations':
        return sankey_layout
    elif pathname == '/caract_musicales':
        return radar_layout
    else:
        return home_layout


register_map_callback(app)
register_linear_callback(app)
register_sankey_callback(app)
register_radar_callback(app)


# Callback pour le pie chart et l'histogramme
@app.callback(
    Output("pie-chart", "figure"),
    Output("histogram-chart", "figure"),
    [Input("pie-chart", "clickData")]
)

def update_charts(click_data):
    data_manager = DataManager()

    genre_counts_df = data_manager.create_genre_count_dataframe()

    # Création du pie chart
    genre_counts_df['transformed_count'] = np.sqrt(genre_counts_df['total_count'])  # Transformation racine carrée

    fig_pie = px.pie(
        genre_counts_df,
        names='genre',
        values='transformed_count',  # On utilise la colonne transformée pour réduire l'impact de pop
        color='genre',
        color_discrete_map=genre_colors,
    )
    fig_pie.update_traces(textinfo='percent+label', textposition='inside')
    fig_pie.update_layout(
        plot_bgcolor='black',
        paper_bgcolor='black',
        font_color='white',
        showlegend=False
    )

    selected_genre = "indie"  #par défaut
    if click_data:
        selected_genre = click_data['points'][0]['label']

    df_subgenres = data_manager.get_top_subgenres_per_genre(selected_genre)
    
    df_subgenres = df_subgenres[df_subgenres['subgenre'] != selected_genre]

    fig_histogram = go.Figure()
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
        yaxis=dict(title=None)  
    )

    return fig_pie, fig_histogram

if __name__ == '__main__':
    app.run_server(debug=True)
